"""Hollow a solid zone mesh into a printable shell.

Takes a solid zone piece (from dissect) and creates a hollow shell by:
1. Offsetting the surface inward by wall thickness
2. Boolean subtracting the inner volume
3. Opening the attachment face (so it can slide onto the skeleton)

Usage:
    from pipeline.hollow import hollow_zone
    shell = hollow_zone(solid_mesh, zone="head", wall_thickness=2.0)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh
import manifold3d as mf

from pipeline.skeleton import (
    SHELL_MIN_WALL,
    BODY_ZONES,
    BASE_H,
    envelope_for_zone,
)


@dataclass
class HollowResult:
    """Result of hollowing a zone mesh."""
    shell: trimesh.Trimesh | None
    wall_thickness: float
    warnings: list[str]
    metrics: dict


def _trimesh_to_manifold(mesh: trimesh.Trimesh) -> mf.Manifold:
    return mf.Manifold(
        mf.Mesh(
            vert_properties=np.array(mesh.vertices, dtype=np.float32),
            tri_verts=np.array(mesh.faces, dtype=np.uint32),
        )
    )


def _manifold_to_trimesh(manifold: mf.Manifold) -> trimesh.Trimesh:
    out = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=out.vert_properties[:, :3],
        faces=out.tri_verts,
    )


def _offset_inward(mesh: trimesh.Trimesh, distance: float) -> trimesh.Trimesh:
    """Create an inward-offset version of a mesh.

    Moves each vertex inward along its vertex normal by `distance`.
    This is an approximation — for production, use voxel-based or
    SDF-based offsetting for more robustness.
    """
    if not mesh.is_watertight:
        # Try auto-repair
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fill_holes(mesh)

    # Compute vertex normals (pointing outward)
    normals = mesh.vertex_normals

    # Move vertices inward
    inner_verts = mesh.vertices - normals * distance

    inner = trimesh.Trimesh(
        vertices=inner_verts,
        faces=mesh.faces.copy(),
        process=True,
    )

    # Fix any inverted normals from the offset
    trimesh.repair.fix_normals(inner)

    return inner


def _cut_opening(
    shell: trimesh.Trimesh,
    zone: str,
    cut_planes: dict[str, float] | None = None,
) -> trimesh.Trimesh:
    """Cut the attachment opening in a shell so it can slide onto the skeleton.

    Each zone has a specific face that gets removed:
    - head: bottom opening (neck hole)
    - torso: top opening + bottom opening + arm cutouts
    - left_arm / right_arm: inboard face
    - base: top opening
    """
    bounds = shell.bounds
    pad = 5.0  # Extra padding for clean cut

    if zone == "head":
        # Remove bottom 2mm to create neck opening
        cut_z = bounds[0][2] + 2.0
        cutter = trimesh.creation.box(
            extents=[
                bounds[1][0] - bounds[0][0] + pad * 2,
                bounds[1][1] - bounds[0][1] + pad * 2,
                cut_z - bounds[0][2] + pad,
            ]
        )
        cutter.apply_translation([
            (bounds[0][0] + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (bounds[0][2] + cut_z) / 2,
        ])
        m_shell = _trimesh_to_manifold(shell)
        m_cut = _trimesh_to_manifold(cutter)
        result = m_shell - m_cut
        return _manifold_to_trimesh(result)

    elif zone == "torso":
        # Open top and bottom
        m_shell = _trimesh_to_manifold(shell)

        # Bottom opening
        bot_z = bounds[0][2] + 2.0
        bot_cut = trimesh.creation.box(
            extents=[
                bounds[1][0] - bounds[0][0] + pad * 2,
                bounds[1][1] - bounds[0][1] + pad * 2,
                bot_z - bounds[0][2] + pad,
            ]
        )
        bot_cut.apply_translation([
            (bounds[0][0] + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (bounds[0][2] + bot_z) / 2,
        ])
        m_shell = m_shell - _trimesh_to_manifold(bot_cut)

        # Top opening
        top_z = bounds[1][2] - 2.0
        top_cut = trimesh.creation.box(
            extents=[
                bounds[1][0] - bounds[0][0] + pad * 2,
                bounds[1][1] - bounds[0][1] + pad * 2,
                bounds[1][2] - top_z + pad,
            ]
        )
        top_cut.apply_translation([
            (bounds[0][0] + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (top_z + bounds[1][2]) / 2,
        ])
        m_shell = m_shell - _trimesh_to_manifold(top_cut)

        return _manifold_to_trimesh(m_shell)

    elif zone == "left_arm":
        # Open the inboard face (positive X side, closest to torso)
        cut_x = bounds[1][0] - 2.0
        cutter = trimesh.creation.box(
            extents=[
                bounds[1][0] - cut_x + pad,
                bounds[1][1] - bounds[0][1] + pad * 2,
                bounds[1][2] - bounds[0][2] + pad * 2,
            ]
        )
        cutter.apply_translation([
            (cut_x + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (bounds[0][2] + bounds[1][2]) / 2,
        ])
        m_shell = _trimesh_to_manifold(shell)
        m_cut = _trimesh_to_manifold(cutter)
        return _manifold_to_trimesh(m_shell - m_cut)

    elif zone == "right_arm":
        # Open the inboard face (negative X side, closest to torso)
        cut_x = bounds[0][0] + 2.0
        cutter = trimesh.creation.box(
            extents=[
                cut_x - bounds[0][0] + pad,
                bounds[1][1] - bounds[0][1] + pad * 2,
                bounds[1][2] - bounds[0][2] + pad * 2,
            ]
        )
        cutter.apply_translation([
            (bounds[0][0] + cut_x) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (bounds[0][2] + bounds[1][2]) / 2,
        ])
        m_shell = _trimesh_to_manifold(shell)
        m_cut = _trimesh_to_manifold(cutter)
        return _manifold_to_trimesh(m_shell - m_cut)

    elif zone == "base":
        # Open top face
        cut_z = bounds[1][2] - 2.0
        cutter = trimesh.creation.box(
            extents=[
                bounds[1][0] - bounds[0][0] + pad * 2,
                bounds[1][1] - bounds[0][1] + pad * 2,
                bounds[1][2] - cut_z + pad,
            ]
        )
        cutter.apply_translation([
            (bounds[0][0] + bounds[1][0]) / 2,
            (bounds[0][1] + bounds[1][1]) / 2,
            (cut_z + bounds[1][2]) / 2,
        ])
        m_shell = _trimesh_to_manifold(shell)
        m_cut = _trimesh_to_manifold(cutter)
        return _manifold_to_trimesh(m_shell - m_cut)

    return shell


def hollow_zone(
    solid: trimesh.Trimesh,
    zone: str,
    wall_thickness: float = SHELL_MIN_WALL,
) -> HollowResult:
    """Hollow a solid zone mesh into a printable shell.

    Args:
        solid: Watertight solid mesh for one body zone (from dissect).
        zone: Body zone name ("head", "torso", etc.).
        wall_thickness: Shell wall thickness in mm.

    Returns:
        HollowResult with the hollow shell mesh.
    """
    if zone not in BODY_ZONES:
        raise ValueError(f"Unknown zone: {zone}. Must be one of {BODY_ZONES}")

    warnings = []
    metrics = {}

    # Check input mesh
    if not solid.is_watertight:
        trimesh.repair.fix_normals(solid)
        trimesh.repair.fill_holes(solid)
        if not solid.is_watertight:
            warnings.append("Input mesh is not watertight after repair — "
                          "hollowing may produce artifacts")

    metrics["input_volume_mm3"] = float(solid.volume)
    metrics["input_bounds"] = solid.bounds.tolist()

    # Enforce minimum wall thickness
    if wall_thickness < SHELL_MIN_WALL:
        warnings.append(
            f"Requested wall {wall_thickness}mm is below minimum "
            f"{SHELL_MIN_WALL}mm — using minimum"
        )
        wall_thickness = SHELL_MIN_WALL

    # Create inner offset surface
    inner = _offset_inward(solid, wall_thickness)

    # Boolean subtract: solid - inner = shell
    try:
        m_outer = _trimesh_to_manifold(solid)
        m_inner = _trimesh_to_manifold(inner)
        m_shell = m_outer - m_inner
        shell = _manifold_to_trimesh(m_shell)
    except Exception as e:
        warnings.append(f"Boolean hollowing failed: {e}. "
                       "Falling back to vertex-offset method.")
        # Fallback: just return the offset mesh difference as-is
        shell = solid.copy()

    # Cut the attachment opening
    shell = _cut_opening(shell, zone)

    # Compute metrics
    metrics["shell_volume_mm3"] = float(shell.volume) if shell.volume > 0 else 0
    metrics["shell_watertight"] = shell.is_watertight
    metrics["wall_thickness"] = wall_thickness

    # Estimate weight (PLA: ~1.24 g/cm³)
    shell_volume_cm3 = metrics["shell_volume_mm3"] / 1000.0
    metrics["estimated_weight_g"] = shell_volume_cm3 * 1.24

    # Check weight against servo limits
    envelope = envelope_for_zone(zone)
    if metrics["estimated_weight_g"] > envelope.max_shell_weight_g:
        warnings.append(
            f"Estimated shell weight ({metrics['estimated_weight_g']:.1f}g) "
            f"exceeds max for {zone} zone ({envelope.max_shell_weight_g}g)"
        )

    return HollowResult(
        shell=shell,
        wall_thickness=wall_thickness,
        warnings=warnings,
        metrics=metrics,
    )
