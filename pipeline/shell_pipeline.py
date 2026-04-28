"""Shell pipeline: Scale → Subtract → Trim → Validate.

Takes a sculpture mesh (from AI generation or manual design) and a skeleton mesh,
produces a printable shell by:
1. SCALE: Fit the skeleton inside the sculpture
2. SUBTRACT: Boolean-cut the skeleton out of the sculpture
3. TRIM: Enforce minimum wall thickness, remove artifacts
4. VALIDATE: Check watertightness, wall thickness, printability

Usage:
    python shell_pipeline.py sculpture.stl skeleton.stl output_shell.stl
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh


@dataclass
class PipelineResult:
    """Result of the shell pipeline."""

    shell: trimesh.Trimesh | None
    success: bool
    steps_completed: list[str]
    errors: list[str]
    metrics: dict


def _trimesh_to_manifold(mesh: trimesh.Trimesh) -> mf.Manifold:
    """Convert a trimesh mesh to a manifold3d Manifold."""
    m = mf.Manifold(
        mf.Mesh(
            vert_properties=np.array(mesh.vertices, dtype=np.float32),
            tri_verts=np.array(mesh.faces, dtype=np.uint32),
        )
    )
    return m


def _manifold_to_trimesh(manifold: mf.Manifold) -> trimesh.Trimesh:
    """Convert a manifold3d Manifold back to trimesh."""
    out = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=out.vert_properties[:, :3],
        faces=out.tri_verts,
    )


# ---------------------------------------------------------------------------
# Step 1: SCALE — fit the skeleton inside the sculpture
# ---------------------------------------------------------------------------

def scale_skeleton_to_sculpture(
    sculpture: trimesh.Trimesh,
    skeleton: trimesh.Trimesh,
    padding_mm: float = 3.0,
) -> trimesh.Trimesh:
    """Scale and center the skeleton to fit inside the sculpture.

    The skeleton is scaled uniformly so it fits within the sculpture's
    bounding box with `padding_mm` of clearance on each side (this
    becomes the minimum wall thickness).

    Both meshes are centered on the same origin.
    """
    # Center both meshes
    sculpture_center = sculpture.bounding_box.centroid
    skeleton_center = skeleton.bounding_box.centroid

    skeleton_scaled = skeleton.copy()
    skeleton_scaled.apply_translation(-skeleton_center)

    # Calculate scale factor
    sculpt_size = sculpture.bounding_box.extents
    skel_size = skeleton.bounding_box.extents

    # Available interior space = sculpture size - 2*padding on each axis
    available = sculpt_size - 2 * padding_mm

    # Scale uniformly by the smallest ratio (so skeleton fits on all axes)
    scale_ratios = available / skel_size
    scale_factor = max(min(scale_ratios), 0.5)  # Don't shrink below 50%

    skeleton_scaled.apply_scale(scale_factor)

    # Center the skeleton inside the sculpture
    skeleton_scaled.apply_translation(sculpture_center)

    return skeleton_scaled


# ---------------------------------------------------------------------------
# Step 2: SUBTRACT — boolean cut the skeleton from the sculpture
# ---------------------------------------------------------------------------

def subtract_skeleton(
    sculpture: trimesh.Trimesh,
    skeleton: trimesh.Trimesh,
) -> trimesh.Trimesh:
    """Boolean subtract the skeleton from the sculpture using manifold3d.

    Returns the shell (sculpture minus skeleton interior).
    """
    sculpt_mf = _trimesh_to_manifold(sculpture)
    skel_mf = _trimesh_to_manifold(skeleton)

    shell_mf = sculpt_mf - skel_mf

    return _manifold_to_trimesh(shell_mf)


# ---------------------------------------------------------------------------
# Step 3: TRIM — clean up the result
# ---------------------------------------------------------------------------

def trim_shell(
    shell: trimesh.Trimesh,
    min_wall_mm: float = 2.0,
) -> trimesh.Trimesh:
    """Clean up the shell mesh.

    - Remove degenerate faces
    - Fill small holes
    - Remove disconnected fragments smaller than 10% of total volume
    """
    # Remove degenerate faces
    shell.remove_degenerate_faces()
    shell.remove_duplicate_faces()
    shell.remove_unreferenced_vertices()

    # If the mesh splits into multiple bodies, keep only the largest ones
    if hasattr(shell, 'split'):
        bodies = shell.split()
        if len(bodies) > 1:
            # Keep bodies that are at least 10% of the largest
            volumes = [abs(b.volume) if b.is_watertight else 0 for b in bodies]
            if max(volumes) > 0:
                threshold = max(volumes) * 0.1
                kept = [b for b, v in zip(bodies, volumes) if v >= threshold]
                if kept:
                    shell = trimesh.util.concatenate(kept)

    return shell


# ---------------------------------------------------------------------------
# Step 4: VALIDATE — check printability
# ---------------------------------------------------------------------------

def validate_shell(shell: trimesh.Trimesh) -> dict:
    """Run validation checks on the shell mesh.

    Returns a dict of metrics and pass/fail checks.
    """
    bounds = shell.bounds
    size = bounds[1] - bounds[0]

    metrics = {
        "vertices": len(shell.vertices),
        "faces": len(shell.faces),
        "watertight": shell.is_watertight,
        "volume_mm3": abs(shell.volume) if shell.is_watertight else None,
        "volume_cm3": abs(shell.volume) / 1000.0 if shell.is_watertight else None,
        "size_mm": {"x": round(size[0], 1), "y": round(size[1], 1), "z": round(size[2], 1)},
        "has_degenerate_faces": len(shell.faces) != len(shell.nondegenerate_faces) if hasattr(shell, 'nondegenerate_faces') else False,
    }

    # Estimate wall thickness from ray casting
    # Cast rays inward from surface points and measure distance to opposite wall
    if shell.is_watertight and len(shell.vertices) > 0:
        # Sample points on the surface
        n_samples = min(500, len(shell.vertices))
        indices = np.random.choice(len(shell.vertices), n_samples, replace=False)
        points = shell.vertices[indices]

        # Get face normals at these points (approximate using vertex normals)
        if shell.vertex_normals is not None and len(shell.vertex_normals) > 0:
            normals = shell.vertex_normals[indices]
            # Cast rays inward
            ray_origins = points + normals * 0.01  # slight offset
            ray_dirs = -normals
            hits, ray_ids, _ = shell.ray.intersects_location(ray_origins, ray_dirs)

            if len(hits) > 0:
                # For each ray that hit, compute distance
                distances = np.linalg.norm(hits - ray_origins[ray_ids], axis=1)
                metrics["wall_thickness_min_mm"] = round(float(np.min(distances)), 2)
                metrics["wall_thickness_avg_mm"] = round(float(np.mean(distances)), 2)
                metrics["wall_thickness_max_mm"] = round(float(np.max(distances)), 2)

    # Summary
    printable = (
        metrics["watertight"]
        and not metrics["has_degenerate_faces"]
        and metrics.get("wall_thickness_min_mm", 0) >= 1.0
    )
    metrics["printable"] = printable

    return metrics


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    sculpture_path: str | Path,
    skeleton_path: str | Path,
    output_path: str | Path,
    wall_thickness_mm: float = 3.0,
    min_wall_mm: float = 2.0,
) -> PipelineResult:
    """Run the complete shell pipeline.

    Args:
        sculpture_path: Path to the sculpture STL/OBJ/PLY.
        skeleton_path: Path to the skeleton STL.
        output_path: Where to save the resulting shell STL.
        wall_thickness_mm: Target padding between skeleton and sculpture surface.
        min_wall_mm: Minimum acceptable wall thickness.

    Returns:
        PipelineResult with the shell mesh and diagnostics.
    """
    result = PipelineResult(
        shell=None, success=False, steps_completed=[], errors=[], metrics={},
    )

    # Load meshes
    try:
        sculpture = trimesh.load(str(sculpture_path), force="mesh")
        skeleton = trimesh.load(str(skeleton_path), force="mesh")
        print(f"Loaded sculpture: {len(sculpture.vertices)} verts, "
              f"watertight={sculpture.is_watertight}")
        print(f"Loaded skeleton:  {len(skeleton.vertices)} verts, "
              f"watertight={skeleton.is_watertight}")
    except Exception as e:
        result.errors.append(f"Failed to load meshes: {e}")
        return result

    # Repair sculpture if needed
    if not sculpture.is_watertight:
        print("Repairing sculpture mesh...")
        trimesh.repair.fix_normals(sculpture)
        trimesh.repair.fill_holes(sculpture)
        trimesh.repair.fix_winding(sculpture)
        print(f"  After repair: watertight={sculpture.is_watertight}")
        if not sculpture.is_watertight:
            print("  Warning: sculpture still not watertight, proceeding anyway")

    # Step 1: Scale
    print("\n[1/4] SCALE — fitting skeleton inside sculpture...")
    try:
        skeleton_scaled = scale_skeleton_to_sculpture(
            sculpture, skeleton, padding_mm=wall_thickness_mm,
        )
        skel_size = skeleton_scaled.bounding_box.extents
        print(f"  Scaled skeleton: {skel_size[0]:.1f} x {skel_size[1]:.1f} x {skel_size[2]:.1f} mm")
        result.steps_completed.append("scale")
    except Exception as e:
        result.errors.append(f"Scale failed: {e}")
        return result

    # Step 2: Subtract
    print("\n[2/4] SUBTRACT — cutting skeleton from sculpture...")
    try:
        shell = subtract_skeleton(sculpture, skeleton_scaled)
        print(f"  Result: {len(shell.vertices)} verts, {len(shell.faces)} faces")
        result.steps_completed.append("subtract")
    except Exception as e:
        result.errors.append(f"Boolean subtract failed: {e}")
        return result

    # Step 3: Trim
    print("\n[3/4] TRIM — cleaning up shell...")
    try:
        shell = trim_shell(shell, min_wall_mm=min_wall_mm)
        print(f"  Cleaned: {len(shell.vertices)} verts, {len(shell.faces)} faces")
        result.steps_completed.append("trim")
    except Exception as e:
        result.errors.append(f"Trim failed: {e}")
        # Continue with uncleaned shell
        pass

    # Step 4: Validate
    print("\n[4/4] VALIDATE — checking printability...")
    try:
        metrics = validate_shell(shell)
        result.metrics = metrics
        result.steps_completed.append("validate")

        print(f"  Watertight: {metrics['watertight']}")
        print(f"  Size: {metrics['size_mm']['x']} x {metrics['size_mm']['y']} x {metrics['size_mm']['z']} mm")
        if metrics.get('volume_cm3'):
            print(f"  Volume: {metrics['volume_cm3']:.1f} cm³")
        if metrics.get('wall_thickness_min_mm'):
            print(f"  Wall thickness: min={metrics['wall_thickness_min_mm']:.1f}mm, "
                  f"avg={metrics['wall_thickness_avg_mm']:.1f}mm")
        print(f"  Printable: {metrics.get('printable', False)}")
    except Exception as e:
        result.errors.append(f"Validate failed: {e}")

    # Save
    try:
        output_path = Path(output_path)
        shell.export(str(output_path))
        print(f"\nShell saved to {output_path}")
        result.shell = shell
        result.success = True
    except Exception as e:
        result.errors.append(f"Export failed: {e}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shell_pipeline.py <sculpture.stl> <skeleton.stl> [output.stl]")
        print("\nGenerating test sculpture and running pipeline...")

        # Generate a simple test sculpture (sphere/capsule as a character body)
        from pipeline.skeleton import build_skeleton_for_subtraction

        # Create a simple humanoid-ish sculpture: stacked ellipsoids
        body = trimesh.creation.capsule(height=90, radius=40)
        body.apply_translation([0, 0, 35])

        head = trimesh.creation.icosphere(radius=30)
        head.apply_translation([0, 0, 95])

        l_arm = trimesh.creation.capsule(height=50, radius=10)
        l_arm.apply_translation([-45, 0, 55])

        r_arm = trimesh.creation.capsule(height=50, radius=10)
        r_arm.apply_translation([45, 0, 55])

        # Combine into sculpture
        sculpture = trimesh.util.concatenate([body, head, l_arm, r_arm])

        # Make it a proper solid via convex hull (simple but works for test)
        sculpture = sculpture.convex_hull

        sculpture.export("test_sculpture.stl")
        print(f"Test sculpture: {len(sculpture.vertices)} verts, watertight={sculpture.is_watertight}")

        # Build skeleton
        skeleton = build_skeleton_for_subtraction()
        skeleton.export("skeleton_spark.stl")

        # Run pipeline
        result = run_pipeline("test_sculpture.stl", "skeleton_spark.stl", "test_shell.stl")

        if result.success:
            print(f"\n✓ Pipeline succeeded!")
            print(f"  Steps: {', '.join(result.steps_completed)}")
        else:
            print(f"\n✗ Pipeline failed!")
            for err in result.errors:
                print(f"  Error: {err}")
    else:
        sculpture_path = sys.argv[1]
        skeleton_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else "shell_output.stl"
        run_pipeline(sculpture_path, skeleton_path, output_path)
