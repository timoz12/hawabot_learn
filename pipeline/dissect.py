"""Dissect a 3D character mesh into body zones using cut planes.

Takes a watertight character mesh and slices it into 5 zones:
head, torso, left_arm, right_arm, base.

Cut planes are adjustable — the customer can shift them during the
guided dissection step. This module handles the geometry; the UI
is handled by the web layer.

Usage:
    from pipeline.dissect import dissect_character
    zones = dissect_character(mesh, cut_planes=None)
    # zones = {"head": Trimesh, "torso": Trimesh, ...}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import trimesh
import manifold3d as mf

from pipeline.skeleton import (
    DEFAULT_CUT_PLANES,
    CutPlane,
    BODY_ZONES,
    TOTAL_HEIGHT,
    BASE_H,
)


@dataclass
class DissectResult:
    """Result of dissecting a character mesh into body zones."""
    zones: dict[str, trimesh.Trimesh]
    cut_planes_used: list[CutPlane]
    warnings: list[str]


def _trimesh_to_manifold(mesh: trimesh.Trimesh) -> mf.Manifold:
    """Convert trimesh to manifold3d for boolean ops."""
    return mf.Manifold(
        mf.Mesh(
            vert_properties=np.array(mesh.vertices, dtype=np.float32),
            tri_verts=np.array(mesh.faces, dtype=np.uint32),
        )
    )


def _manifold_to_trimesh(manifold: mf.Manifold) -> trimesh.Trimesh:
    """Convert manifold3d back to trimesh."""
    out = manifold.to_mesh()
    return trimesh.Trimesh(
        vertices=out.vert_properties[:, :3],
        faces=out.tri_verts,
    )


def _make_half_space(
    axis: str,
    position: float,
    keep_side: str,
    bounds: np.ndarray,
    padding: float = 2.0,
) -> trimesh.Trimesh:
    """Create a large box representing one side of a cut plane.

    Args:
        axis: "X", "Y", or "Z"
        position: where the cut plane is along that axis
        keep_side: "above" (keep > position) or "below" (keep < position)
        bounds: (2, 3) array of mesh bounding box [min, max]
        padding: extra mm to extend beyond mesh bounds
    """
    mn = bounds[0] - padding
    mx = bounds[1] + padding

    axis_idx = {"X": 0, "Y": 1, "Z": 2}[axis]

    if keep_side == "above":
        mn[axis_idx] = position
    else:
        mx[axis_idx] = position

    center = (mn + mx) / 2
    extents = mx - mn

    half = trimesh.creation.box(extents=extents)
    half.apply_translation(center)
    return half


def _slice_mesh(
    mesh: trimesh.Trimesh,
    axis: str,
    position: float,
    keep_side: str,
) -> trimesh.Trimesh:
    """Slice a mesh at a plane, keeping one side.

    Uses boolean intersection: mesh ∩ half-space box.
    """
    bounds = mesh.bounds
    half = _make_half_space(axis, position, keep_side, bounds)

    m_mesh = _trimesh_to_manifold(mesh)
    m_half = _trimesh_to_manifold(half)
    result = m_mesh ^ m_half  # Intersection
    return _manifold_to_trimesh(result)


MIN_ARM_ZONE_WIDTH = 15.0  # mm — minimum X-width for arm zones


def validate_tpose(
    mesh: trimesh.Trimesh,
    cut_planes: list[CutPlane],
) -> tuple[bool, list[str]]:
    """Check if a character mesh appears to be in T-pose.

    Validates by measuring the mesh width at the shoulder cut height.
    In T-pose, the mesh should extend significantly beyond the arm cut planes.

    Returns:
        (is_tpose, warnings) — is_tpose is False if arms appear to be
        against the body.
    """
    warnings = []

    head_z = next((c.position for c in cut_planes if c.name == "head_torso"), 115)
    base_z = next((c.position for c in cut_planes if c.name == "torso_base"), 10)
    left_x = next((c.position for c in cut_planes if c.name == "left_arm"), -28)
    right_x = next((c.position for c in cut_planes if c.name == "right_arm"), 28)

    # Measure mesh width at shoulder height (midpoint of torso zone)
    shoulder_z = (head_z + base_z) / 2
    bounds = mesh.bounds

    # Slice a thin band at shoulder height and measure its X extent
    try:
        band_top = _slice_mesh(mesh, "Z", shoulder_z - 5, "above")
        band = _slice_mesh(band_top, "Z", shoulder_z + 5, "below")

        if band is not None and len(band.vertices) > 0:
            band_bounds = band.bounds
            mesh_width_at_shoulders = band_bounds[1][0] - band_bounds[0][0]

            # Check if mesh extends beyond arm cut planes
            left_extent = band_bounds[0][0]   # Most negative X
            right_extent = band_bounds[1][0]   # Most positive X

            left_arm_width = abs(left_extent - left_x)
            right_arm_width = abs(right_extent - right_x)

            if left_arm_width < MIN_ARM_ZONE_WIDTH:
                warnings.append(
                    f"Left arm zone is only {left_arm_width:.1f}mm wide "
                    f"(need ≥{MIN_ARM_ZONE_WIDTH}mm). Character may not be "
                    f"in T-pose — arms should be straight out to the sides."
                )

            if right_arm_width < MIN_ARM_ZONE_WIDTH:
                warnings.append(
                    f"Right arm zone is only {right_arm_width:.1f}mm wide "
                    f"(need ≥{MIN_ARM_ZONE_WIDTH}mm). Character may not be "
                    f"in T-pose — arms should be straight out to the sides."
                )

            # Overall width check: T-pose character should be wider than tall
            # (or at least close). If height >> width, arms are probably down.
            mesh_height = bounds[1][2] - bounds[0][2]
            width_to_height = mesh_width_at_shoulders / mesh_height

            if width_to_height < 0.5:
                warnings.append(
                    f"Character is much taller ({mesh_height:.0f}mm) than wide "
                    f"({mesh_width_at_shoulders:.0f}mm) at shoulder height. "
                    f"This suggests the arms are NOT in T-pose. "
                    f"Consider regenerating with arms out."
                )

            is_tpose = len(warnings) == 0
            return is_tpose, warnings

    except Exception:
        pass

    # Fallback: use overall mesh bounds
    total_width = bounds[1][0] - bounds[0][0]
    total_height = bounds[1][2] - bounds[0][2]

    if total_width < total_height * 0.6:
        warnings.append(
            f"Mesh width ({total_width:.0f}mm) is much less than height "
            f"({total_height:.0f}mm). Character is likely NOT in T-pose."
        )
        return False, warnings

    return True, warnings


def validate_cut_planes(
    cut_planes: list[CutPlane],
) -> list[str]:
    """Check that cut planes are within valid ranges and don't conflict."""
    warnings = []

    for cp in cut_planes:
        if cp.position < cp.min_pos or cp.position > cp.max_pos:
            warnings.append(
                f"Cut plane '{cp.name}' at {cp.position} is outside "
                f"range [{cp.min_pos}, {cp.max_pos}]"
            )

    # Check head/torso cut is above torso/base cut
    head_cut = next((c for c in cut_planes if c.name == "head_torso"), None)
    base_cut = next((c for c in cut_planes if c.name == "torso_base"), None)
    if head_cut and base_cut and head_cut.position <= base_cut.position:
        warnings.append(
            f"Head cut (Z={head_cut.position}) must be above "
            f"base cut (Z={base_cut.position})"
        )

    # Check arm cuts don't overlap
    left_cut = next((c for c in cut_planes if c.name == "left_arm"), None)
    right_cut = next((c for c in cut_planes if c.name == "right_arm"), None)
    if left_cut and right_cut and abs(left_cut.position) < abs(right_cut.position) * 0.5:
        warnings.append("Arm cut planes are very close — torso zone may be too narrow")

    return warnings


def dissect_character(
    mesh: trimesh.Trimesh,
    cut_planes: Optional[list[CutPlane]] = None,
) -> DissectResult:
    """Dissect a character mesh into 5 body zones.

    Args:
        mesh: Watertight character mesh, scaled and centered on skeleton origin.
        cut_planes: Custom cut plane positions. Uses defaults if None.

    Returns:
        DissectResult with zone meshes and any warnings.
    """
    if cut_planes is None:
        cut_planes = list(DEFAULT_CUT_PLANES)

    warnings = validate_cut_planes(cut_planes)

    # T-pose validation
    is_tpose, tpose_warnings = validate_tpose(mesh, cut_planes)
    warnings.extend(tpose_warnings)
    if not is_tpose:
        warnings.append(
            "⚠ CHARACTER IS NOT IN T-POSE — arm zones will be too small. "
            "Regenerate the model with arms straight out to the sides."
        )

    # Extract cut positions
    head_z = next(c.position for c in cut_planes if c.name == "head_torso")
    base_z = next(c.position for c in cut_planes if c.name == "torso_base")
    left_x = next(c.position for c in cut_planes if c.name == "left_arm")
    right_x = next(c.position for c in cut_planes if c.name == "right_arm")

    zones: dict[str, trimesh.Trimesh] = {}

    # 1. Head: everything above head_z
    zones["head"] = _slice_mesh(mesh, "Z", head_z, "above")

    # 2. Base: everything below base_z
    zones["base"] = _slice_mesh(mesh, "Z", base_z, "below")

    # 3. Middle band: between base_z and head_z
    middle = _slice_mesh(mesh, "Z", base_z, "above")
    middle = _slice_mesh(middle, "Z", head_z, "below")

    # 4. Left arm: middle band, everything left of left_x (negative X)
    zones["left_arm"] = _slice_mesh(middle, "X", left_x, "below")

    # 5. Right arm: middle band, everything right of right_x (positive X)
    zones["right_arm"] = _slice_mesh(middle, "X", right_x, "above")

    # 6. Torso: middle band, between left_x and right_x
    torso = _slice_mesh(middle, "X", left_x, "above")
    torso = _slice_mesh(torso, "X", right_x, "below")
    zones["torso"] = torso

    # Validate zone sizes
    for zone_name, zone_mesh in zones.items():
        if zone_mesh is None or len(zone_mesh.vertices) == 0:
            warnings.append(f"Zone '{zone_name}' is empty after cutting")
            continue

        bounds = zone_mesh.bounds
        size = bounds[1] - bounds[0]
        min_dim = min(size)
        if min_dim < 15:
            warnings.append(
                f"Zone '{zone_name}' is very thin ({min_dim:.1f}mm) — "
                f"may not be printable"
            )

    return DissectResult(
        zones=zones,
        cut_planes_used=cut_planes,
        warnings=warnings,
    )


def preview_cuts(
    mesh: trimesh.Trimesh,
    cut_planes: Optional[list[CutPlane]] = None,
) -> dict[str, dict]:
    """Preview where cuts will happen without actually cutting.

    Returns zone bounding boxes for UI display.
    """
    if cut_planes is None:
        cut_planes = list(DEFAULT_CUT_PLANES)

    bounds = mesh.bounds
    head_z = next(c.position for c in cut_planes if c.name == "head_torso")
    base_z = next(c.position for c in cut_planes if c.name == "torso_base")
    left_x = next(c.position for c in cut_planes if c.name == "left_arm")
    right_x = next(c.position for c in cut_planes if c.name == "right_arm")

    return {
        "head": {
            "min": [bounds[0][0], bounds[0][1], head_z],
            "max": [bounds[1][0], bounds[1][1], bounds[1][2]],
        },
        "base": {
            "min": [bounds[0][0], bounds[0][1], bounds[0][2]],
            "max": [bounds[1][0], bounds[1][1], base_z],
        },
        "left_arm": {
            "min": [bounds[0][0], bounds[0][1], base_z],
            "max": [left_x, bounds[1][1], head_z],
        },
        "right_arm": {
            "min": [right_x, bounds[0][1], base_z],
            "max": [bounds[1][0], bounds[1][1], head_z],
        },
        "torso": {
            "min": [left_x, bounds[0][1], base_z],
            "max": [right_x, bounds[1][1], head_z],
        },
    }
