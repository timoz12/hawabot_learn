"""Shell pipeline orchestrator: Dissect → Hollow → Magnets → Validate → Export.

Takes a character mesh and produces 5 print-ready shell STL files.

Usage:
    python -m pipeline.shell_pipeline path/to/character.stl output_dir/

    # Or programmatically:
    from pipeline.shell_pipeline import run_pipeline
    result = run_pipeline("character.stl", "output/")
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import trimesh

from pipeline.skeleton import BODY_ZONES, DEFAULT_CUT_PLANES, CutPlane, TOTAL_HEIGHT, SHELL_MIN_WALL
from pipeline.dissect import dissect_character, DissectResult
from pipeline.hollow import hollow_zone, HollowResult
from pipeline.magnets import select_magnets, add_magnet_bosses, MagnetSelection
from pipeline.validate import validate_shell, ValidationReport, print_report


@dataclass
class PipelineResult:
    """Complete result of the shell pipeline."""
    success: bool
    shells: dict[str, trimesh.Trimesh]
    dissect_result: DissectResult | None
    hollow_results: dict[str, HollowResult]
    magnet_selections: dict[str, MagnetSelection]
    validation_reports: dict[str, ValidationReport]
    export_paths: dict[str, str]
    errors: list[str]
    warnings: list[str]


def load_and_prepare(
    mesh_path: str,
    target_height: float = TOTAL_HEIGHT,
) -> trimesh.Trimesh:
    """Load a character mesh and prepare it for the pipeline.

    - Loads from file (STL, OBJ, GLB, PLY)
    - Scales to target height
    - Centers on skeleton origin
    - Repairs mesh if needed
    """
    mesh = trimesh.load(mesh_path, force="mesh")

    # Repair
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)

    # Scale to target height
    bounds = mesh.bounds
    current_height = bounds[1][2] - bounds[0][2]
    if current_height > 0:
        scale_factor = target_height / current_height
        mesh.apply_scale(scale_factor)

    # Center: put the bottom of the mesh at Z = -BASE_H (base plate bottom)
    # and center X/Y on origin
    bounds = mesh.bounds
    center_x = (bounds[0][0] + bounds[1][0]) / 2
    center_y = (bounds[0][1] + bounds[1][1]) / 2
    bottom_z = bounds[0][2]

    # We want the character's feet at roughly Z = -20 (base plate bottom)
    # and center of mass aligned with skeleton origin
    from pipeline.skeleton import BASE_H
    mesh.apply_translation([-center_x, -center_y, -bottom_z - BASE_H])

    return mesh


def run_pipeline(
    mesh_path: str,
    output_dir: str,
    cut_planes: list[CutPlane] | None = None,
    wall_thickness: float = SHELL_MIN_WALL,
) -> PipelineResult:
    """Run the complete shell pipeline.

    Args:
        mesh_path: Path to character mesh file.
        output_dir: Directory to write output STL files.
        cut_planes: Custom cut plane positions (uses defaults if None).
        wall_thickness: Shell wall thickness in mm.

    Returns:
        PipelineResult with all outputs and reports.
    """
    errors: list[str] = []
    warnings: list[str] = []
    shells: dict[str, trimesh.Trimesh] = {}
    hollow_results: dict[str, HollowResult] = {}
    magnet_selections: dict[str, MagnetSelection] = {}
    validation_reports: dict[str, ValidationReport] = {}
    export_paths: dict[str, str] = {}
    dissect_result = None

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load and prepare ──────────────────────────────────────
    print(f"Loading {mesh_path}...")
    try:
        mesh = load_and_prepare(mesh_path)
        print(f"  Loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        print(f"  Bounds: {mesh.bounds[0]} → {mesh.bounds[1]}")
        print(f"  Watertight: {mesh.is_watertight}")
    except Exception as e:
        errors.append(f"Failed to load mesh: {e}")
        return PipelineResult(
            success=False, shells={}, dissect_result=None,
            hollow_results={}, magnet_selections={},
            validation_reports={}, export_paths={},
            errors=errors, warnings=warnings,
        )

    # ── Step 2: Dissect into zones ────────────────────────────────────
    print("\nDissecting into body zones...")
    try:
        dissect_result = dissect_character(mesh, cut_planes)
        warnings.extend(dissect_result.warnings)

        for zone_name, zone_mesh in dissect_result.zones.items():
            if zone_mesh is not None and len(zone_mesh.vertices) > 0:
                print(f"  {zone_name}: {len(zone_mesh.vertices)} verts")
            else:
                errors.append(f"Zone '{zone_name}' is empty after dissection")
    except Exception as e:
        errors.append(f"Dissection failed: {e}")
        return PipelineResult(
            success=False, shells={}, dissect_result=dissect_result,
            hollow_results={}, magnet_selections={},
            validation_reports={}, export_paths={},
            errors=errors, warnings=warnings,
        )

    # ── Step 3: Hollow each zone ──────────────────────────────────────
    print(f"\nHollowing shells (wall: {wall_thickness}mm)...")
    for zone_name, zone_mesh in dissect_result.zones.items():
        if zone_mesh is None or len(zone_mesh.vertices) == 0:
            continue

        try:
            result = hollow_zone(zone_mesh, zone_name, wall_thickness)
            hollow_results[zone_name] = result
            warnings.extend(result.warnings)

            if result.shell is not None:
                print(f"  {zone_name}: {result.metrics.get('estimated_weight_g', 0):.1f}g estimated")
            else:
                errors.append(f"Hollowing failed for {zone_name}")
        except Exception as e:
            errors.append(f"Hollowing failed for {zone_name}: {e}")

    # ── Step 4: Select magnets and add bosses ─────────────────────────
    print("\nSelecting magnets and adding bosses...")
    for zone_name, h_result in hollow_results.items():
        if h_result.shell is None:
            continue

        try:
            selection = select_magnets(h_result.shell, zone_name)
            magnet_selections[zone_name] = selection
            warnings.extend(selection.warnings)

            print(f"  {zone_name}: {len(selection.selected)} magnets "
                  f"({selection.total_pull_force_kg:.1f}kg pull)")

            # Add bosses to shell
            shell_with_bosses = add_magnet_bosses(h_result.shell, selection)
            shells[zone_name] = shell_with_bosses
        except Exception as e:
            warnings.append(f"Magnet processing failed for {zone_name}: {e}")
            # Use shell without bosses as fallback
            shells[zone_name] = h_result.shell

    # ── Step 5: Validate ──────────────────────────────────────────────
    print("\nValidating shells...")
    for zone_name, shell in shells.items():
        magnet_count = len(magnet_selections.get(zone_name, MagnetSelection(
            zone=zone_name, selected=[], rejected=[], total_pull_force_kg=0, warnings=[]
        )).selected)

        report = validate_shell(shell, zone_name, magnet_count)
        validation_reports[zone_name] = report
        print(print_report(report))

    # ── Step 6: Export ────────────────────────────────────────────────
    print("\nExporting STL files...")
    for zone_name, shell in shells.items():
        stl_path = out / f"{zone_name}_shell.stl"
        shell.export(str(stl_path))
        export_paths[zone_name] = str(stl_path)
        print(f"  {stl_path} ({len(shell.faces)} faces)")

    # Overall success
    all_passed = all(r.passed for r in validation_reports.values())
    has_critical_errors = len(errors) > 0

    success = not has_critical_errors
    if not all_passed:
        warnings.append("Some validation checks failed — review reports above")

    print(f"\n{'='*50}")
    print(f"  Pipeline {'COMPLETE' if success else 'FAILED'}")
    print(f"  {len(shells)} shells exported to {output_dir}")
    if errors:
        print(f"  {len(errors)} errors")
    if warnings:
        print(f"  {len(warnings)} warnings")
    print(f"{'='*50}")

    return PipelineResult(
        success=success,
        shells=shells,
        dissect_result=dissect_result,
        hollow_results=hollow_results,
        magnet_selections=magnet_selections,
        validation_reports=validation_reports,
        export_paths=export_paths,
        errors=errors,
        warnings=warnings,
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m pipeline.shell_pipeline <character.stl> <output_dir/>")
        print("\nExample:")
        print("  python -m pipeline.shell_pipeline meshes/naruto.stl output/naruto_shells/")
        sys.exit(1)

    result = run_pipeline(sys.argv[1], sys.argv[2])
    sys.exit(0 if result.success else 1)
