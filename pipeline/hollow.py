"""Hollow a solid zone mesh into a printable shell via skeleton subtraction.

Instead of offsetting the surface inward (fragile on detailed meshes),
we subtract the skeleton clearance volume from the solid zone piece.
This creates a shell whose internal cavity exactly matches the skeleton
frame + clearance, guaranteeing fit.

For the torso zone, the shell is split into front/back clamshell halves
since it can't slide over the shoulder brackets as one piece.

Each zone also gets a removal taper (draft angle) along its removal
direction so shells slide on/off easily.

Usage:
    from pipeline.hollow import hollow_zone
    result = hollow_zone(solid_mesh, zone="head")
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import trimesh
import manifold3d as mf

from pipeline.skeleton import (
    SHELL_MIN_WALL,
    BODY_ZONES,
    BASE_W, BASE_D, BASE_H,
    TORSO_D, TORSO_R,
    WAIST_Z, SHOULDER_Z, SHOULDER_X,
    HEAD_PAN_Z, HEAD_TILT_Z,
    SG90, MG90S,
    C_WALL, T_WALL,
    CLEARANCE_EXPANSION,
    REMOVAL_SPECS,
    JOINT_SWEEPS,
    envelope_for_zone,
)


@dataclass
class HollowResult:
    """Result of hollowing a zone mesh."""
    shells: list[trimesh.Trimesh]  # 1 piece for most zones, 2 for torso clamshell
    zone: str
    wall_thickness_used: str       # "subtraction" — not a fixed number anymore
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


def _make_box(center, extents):
    """Create a box at a given center position."""
    b = trimesh.creation.box(extents=extents)
    b.apply_translation(center)
    return b


def _make_cylinder(center, radius, height, axis="Z"):
    """Create a cylinder at a position along a given axis."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=32)

    if axis == "X":
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
        cyl.apply_transform(rot)
    elif axis == "Y":
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
        cyl.apply_transform(rot)

    cyl.apply_translation(center)
    return cyl


# ── Clearance Volume Builders Per Zone ────────────────────────────────────

def _build_head_clearance() -> trimesh.Trimesh:
    """Clearance volume for the head zone.

    Includes: head pan servo, head tilt servo, neck post,
    head magnet ring, pan rotation sweep.
    """
    C = CLEARANCE_EXPANSION
    parts = []

    # Head pan servo body + clearance
    pan_w = SG90.body_l + 2 * C_WALL + 2 * C
    pan_d = SG90.body_w + 2 * C_WALL + 2 * C
    pan_h = SG90.total_h + 2 * C
    parts.append(_make_box(
        [0, 0, HEAD_PAN_Z + pan_h / 2],
        [pan_w, pan_d, pan_h],
    ))

    # Head tilt servo (rotated: shaft → +Y)
    tilt_w = SG90.body_w + 2 * C_WALL + 2 * C   # Along X
    tilt_d = SG90.body_h + 2 * C_WALL + 2 * C    # Along Y (shaft axis)
    tilt_h = SG90.body_l + 2 * C_WALL + 2 * C    # Along Z
    parts.append(_make_box(
        [0, 0, HEAD_TILT_Z],
        [tilt_w, tilt_d, tilt_h],
    ))

    # Connecting column from cut plane up to pan servo
    connect_h = HEAD_PAN_Z - 113  # From just below cut plane
    parts.append(_make_box(
        [0, 0, 113 + connect_h / 2],
        [TORSO_D + 2 * C, TORSO_D + 2 * C, connect_h + 2],
    ))

    # Pan rotation sweep at the neck boundary
    sweep = JOINT_SWEEPS["head_pan_yaw"]
    parts.append(_make_cylinder(
        sweep["center"], sweep["radius"], sweep["height"], sweep["axis"],
    ))

    # Tilt rotation sweep
    sweep = JOINT_SWEEPS["head_tilt_pitch"]
    parts.append(_make_cylinder(
        sweep["center"], sweep["radius"], sweep["height"], sweep["axis"],
    ))

    # Union all parts
    result = _trimesh_to_manifold(parts[0])
    for p in parts[1:]:
        result = result + _trimesh_to_manifold(p)

    return _manifold_to_trimesh(result)


def _build_torso_clearance() -> trimesh.Trimesh:
    """Clearance volume for the torso zone.

    Includes: torso column, waist servo top, shoulder bracket inboard halves,
    wire channels, waist rotation sweep, shoulder rotation sweeps.
    """
    C = CLEARANCE_EXPANSION
    parts = []

    # Torso column (full height of torso zone)
    col_size = TORSO_D + 2 * C
    torso_bottom = 10   # Just above base cut
    torso_top = 115     # Just below head cut
    torso_h = torso_top - torso_bottom
    parts.append(_make_box(
        [0, 0, torso_bottom + torso_h / 2],
        [col_size, col_size, torso_h],
    ))

    # Waist servo upper portion (sticks into torso zone)
    waist_top = WAIST_Z + SG90.total_h + C
    if waist_top > torso_bottom:
        parts.append(_make_box(
            [0, 0, (torso_bottom + waist_top) / 2],
            [SG90.tab_l + 2 * C, SG90.body_w + 2 * C_WALL + 2 * C, waist_top - torso_bottom],
        ))

    # Shoulder brackets (inboard portions within torso zone)
    bracket_d = MG90S.body_l + 2 * C_WALL + 2 * C
    bracket_h = MG90S.body_w + 2 * C_WALL + 2 * C
    for sign in [-1, 1]:
        # Bracket from torso edge to arm cut plane
        inner_edge = sign * (TORSO_D / 2)
        arm_cut = sign * 28  # Default arm cut plane
        mid_x = (inner_edge + arm_cut) / 2
        width = abs(arm_cut - inner_edge) + 2 * C
        parts.append(_make_box(
            [mid_x, 0, SHOULDER_Z],
            [width, bracket_d, bracket_h],
        ))

    # Wire channels (vertical)
    wire_r = 3.0 + C  # D_wire/2 + expansion
    parts.append(_make_cylinder(
        [TORSO_D / 2 - 2, 0, torso_bottom + torso_h / 2],
        wire_r, torso_h + 4, "Z",
    ))

    # Wire channels (horizontal to shoulders)
    for sign in [-1, 1]:
        parts.append(_make_cylinder(
            [sign * SHOULDER_X / 2, 0, SHOULDER_Z],
            wire_r, SHOULDER_X, "X",
        ))

    # Waist rotation sweep
    sweep = JOINT_SWEEPS["waist_yaw"]
    parts.append(_make_cylinder(
        sweep["center"], sweep["radius"], sweep["height"], sweep["axis"],
    ))

    # Shoulder rotation sweeps
    for name in ["left_shoulder_pitch", "right_shoulder_pitch"]:
        sweep = JOINT_SWEEPS[name]
        parts.append(_make_cylinder(
            sweep["center"], sweep["radius"], sweep["height"], sweep["axis"],
        ))

    result = _trimesh_to_manifold(parts[0])
    for p in parts[1:]:
        result = result + _trimesh_to_manifold(p)

    return _manifold_to_trimesh(result)


def _build_arm_clearance(side: str) -> trimesh.Trimesh:
    """Clearance volume for an arm zone.

    Includes: shoulder servo housing, shaft tube, rotation sweep.
    """
    C = CLEARANCE_EXPANSION
    sign = -1 if side == "left" else 1
    parts = []

    # Servo housing block
    housing_l = 35 + 2 * C  # Outward extent
    housing_d = MG90S.body_l + 2 * C_WALL + 2 * C
    housing_h = MG90S.body_w + 2 * C_WALL + 2 * C

    # From arm cut plane outward
    arm_cut = sign * 28
    outer_x = sign * (SHOULDER_X + 20)
    mid_x = (arm_cut + outer_x) / 2
    width = abs(outer_x - arm_cut)

    parts.append(_make_box(
        [mid_x, 0, SHOULDER_Z],
        [width, housing_d, housing_h],
    ))

    # Shaft tube extending outward
    parts.append(_make_cylinder(
        [sign * (SHOULDER_X + 10), 0, SHOULDER_Z],
        MG90S.spline_od / 2 + 3 + C, 25, "X",
    ))

    # Rotation sweep at the shoulder joint
    sweep_name = f"{side}_shoulder_pitch"
    sweep = JOINT_SWEEPS[sweep_name]
    parts.append(_make_cylinder(
        sweep["center"], sweep["radius"], sweep["height"], sweep["axis"],
    ))

    result = _trimesh_to_manifold(parts[0])
    for p in parts[1:]:
        result = result + _trimesh_to_manifold(p)

    return _manifold_to_trimesh(result)


def _build_base_clearance() -> trimesh.Trimesh:
    """Clearance volume for the base zone.

    Includes: base plate body, Pico cavity area, waist servo lower portion,
    USB access slot.
    """
    C = CLEARANCE_EXPANSION
    parts = []

    # Base plate interior (the shell wraps around the outside)
    parts.append(_make_box(
        [0, 0, -BASE_H / 2],
        [BASE_W + 2 * C, BASE_D + 2 * C, BASE_H + 2 * C],
    ))

    # Waist servo lower portion (below the torso/base cut)
    waist_h = min(SG90.body_h + 2 * C, 20)  # Capped at base zone height
    parts.append(_make_box(
        [0, 0, WAIST_Z + waist_h / 2],
        [SG90.tab_l + 2 * C, SG90.body_w + 2 * C_WALL + 2 * C, waist_h],
    ))

    # USB access opening on +X side
    parts.append(_make_box(
        [BASE_W / 2, 0, -BASE_H / 2],
        [10 + 2 * C, 16 + 2 * C, BASE_H + 2 * C],
    ))

    result = _trimesh_to_manifold(parts[0])
    for p in parts[1:]:
        result = result + _trimesh_to_manifold(p)

    return _manifold_to_trimesh(result)


def build_clearance_volume(zone: str) -> trimesh.Trimesh:
    """Build the skeleton clearance volume for a given zone.

    This is the volume that gets boolean-subtracted from the solid
    zone piece to create the shell.
    """
    builders = {
        "head": _build_head_clearance,
        "torso": _build_torso_clearance,
        "left_arm": lambda: _build_arm_clearance("left"),
        "right_arm": lambda: _build_arm_clearance("right"),
        "base": _build_base_clearance,
    }

    if zone not in builders:
        raise ValueError(f"Unknown zone: {zone}")

    return builders[zone]()


# ── Draft Taper ───────────────────────────────────────────────────────────

def _apply_draft_taper(clearance_vol: trimesh.Trimesh, zone: str) -> trimesh.Trimesh:
    """Expand the clearance volume with a draft taper along the removal direction.

    This makes the cavity slightly wider toward the opening so the shell
    slides on/off without binding.

    Implemented as a slight scale along the removal axis at the opening end.
    """
    spec = REMOVAL_SPECS[zone]
    angle = spec.draft_angle_deg

    if angle <= 0:
        return clearance_vol

    # Get bounds along removal direction
    dx, dy, dz = spec.direction
    bounds = clearance_vol.bounds
    center = (bounds[0] + bounds[1]) / 2

    # Apply a slight taper by scaling vertices along the removal direction
    # Vertices closer to the opening get expanded more
    verts = clearance_vol.vertices.copy()

    # Determine which axis is the removal direction
    if abs(dz) > abs(dx) and abs(dz) > abs(dy):
        # Z-axis removal
        axis_idx = 2
        if dz > 0:
            # Opening is at max Z
            opening_z = bounds[1][2]
            base_z = bounds[0][2]
        else:
            opening_z = bounds[0][2]
            base_z = bounds[1][2]

        span = abs(opening_z - base_z)
        if span > 0:
            for i in range(len(verts)):
                t = abs(verts[i][2] - base_z) / span  # 0 at base, 1 at opening
                expansion = t * math.tan(math.radians(angle)) * span
                # Expand X and Y
                offset_x = (verts[i][0] - center[0])
                offset_y = (verts[i][1] - center[1])
                if abs(offset_x) > 0.1:
                    verts[i][0] += math.copysign(expansion * 0.5, offset_x)
                if abs(offset_y) > 0.1:
                    verts[i][1] += math.copysign(expansion * 0.5, offset_y)

    elif abs(dx) > abs(dy):
        # X-axis removal (arms)
        axis_idx = 0
        if dx > 0:
            opening_x = bounds[1][0]
            base_x = bounds[0][0]
        else:
            opening_x = bounds[0][0]
            base_x = bounds[1][0]

        span = abs(opening_x - base_x)
        if span > 0:
            for i in range(len(verts)):
                t = abs(verts[i][0] - base_x) / span
                expansion = t * math.tan(math.radians(angle)) * span
                offset_y = (verts[i][1] - center[1])
                offset_z = (verts[i][2] - center[2])
                if abs(offset_y) > 0.1:
                    verts[i][1] += math.copysign(expansion * 0.5, offset_y)
                if abs(offset_z) > 0.1:
                    verts[i][2] += math.copysign(expansion * 0.5, offset_z)

    elif abs(dy) > 0:
        # Y-axis removal (torso clamshell)
        axis_idx = 1
        # Taper is less critical for clamshell since it opens sideways
        pass

    tapered = trimesh.Trimesh(vertices=verts, faces=clearance_vol.faces.copy())
    trimesh.repair.fix_normals(tapered)
    return tapered


# ── Clamshell Split ───────────────────────────────────────────────────────

def _split_clamshell(shell: trimesh.Trimesh) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    """Split a torso shell into front and back halves along the XZ plane (Y=0).

    Returns (front_half, back_half).
    """
    bounds = shell.bounds
    pad = 5.0

    # Front half: Y < 0
    front_box = _make_box(
        [(bounds[0][0] + bounds[1][0]) / 2,
         (bounds[0][1] + 0) / 2,
         (bounds[0][2] + bounds[1][2]) / 2],
        [bounds[1][0] - bounds[0][0] + pad * 2,
         abs(bounds[0][1]) + pad,
         bounds[1][2] - bounds[0][2] + pad * 2],
    )

    # Back half: Y > 0
    back_box = _make_box(
        [(bounds[0][0] + bounds[1][0]) / 2,
         (0 + bounds[1][1]) / 2,
         (bounds[0][2] + bounds[1][2]) / 2],
        [bounds[1][0] - bounds[0][0] + pad * 2,
         bounds[1][1] + pad,
         bounds[1][2] - bounds[0][2] + pad * 2],
    )

    m_shell = _trimesh_to_manifold(shell)
    front = _manifold_to_trimesh(m_shell ^ _trimesh_to_manifold(front_box))
    back = _manifold_to_trimesh(m_shell ^ _trimesh_to_manifold(back_box))

    return front, back


# ── Main Entry Point ──────────────────────────────────────────────────────

def hollow_zone(
    solid: trimesh.Trimesh,
    zone: str,
    wall_thickness: float = SHELL_MIN_WALL,
) -> HollowResult:
    """Hollow a solid zone mesh by subtracting the skeleton clearance volume.

    Args:
        solid: Watertight solid mesh for one body zone (from dissect).
        zone: Body zone name ("head", "torso", etc.).
        wall_thickness: Not used directly — retained for API compatibility.
            Wall thickness is determined by the character geometry minus
            the skeleton clearance volume.

    Returns:
        HollowResult with one or more shell meshes.
    """
    if zone not in BODY_ZONES:
        raise ValueError(f"Unknown zone: {zone}. Must be one of {BODY_ZONES}")

    warnings = []
    metrics = {}

    # Check input
    if not solid.is_watertight:
        trimesh.repair.fix_normals(solid)
        trimesh.repair.fill_holes(solid)
        if not solid.is_watertight:
            warnings.append("Input mesh not watertight after repair — subtraction may produce artifacts")

    metrics["input_volume_mm3"] = float(solid.volume)

    # Step 1: Build clearance volume for this zone
    clearance = build_clearance_volume(zone)

    # Step 2: Apply draft taper for removal ease
    clearance = _apply_draft_taper(clearance, zone)

    # Step 3: Boolean subtract clearance from solid zone
    try:
        m_solid = _trimesh_to_manifold(solid)
        m_clearance = _trimesh_to_manifold(clearance)
        m_shell = m_solid - m_clearance
        shell = _manifold_to_trimesh(m_shell)
    except Exception as e:
        warnings.append(f"Boolean subtraction failed: {e}")
        shell = solid.copy()

    # Step 4: For torso zone, split into clamshell halves
    removal = REMOVAL_SPECS[zone]
    shells = []

    if removal.is_clamshell:
        try:
            front, back = _split_clamshell(shell)
            shells = [front, back]
            metrics["clamshell"] = True
        except Exception as e:
            warnings.append(f"Clamshell split failed: {e}. Using single piece.")
            shells = [shell]
            metrics["clamshell"] = False
    else:
        shells = [shell]
        metrics["clamshell"] = False

    # Compute metrics
    total_volume = sum(s.volume for s in shells if s.volume > 0)
    metrics["shell_volume_mm3"] = float(total_volume)
    metrics["shell_count"] = len(shells)
    metrics["removal_direction"] = removal.direction
    metrics["draft_angle_deg"] = removal.draft_angle_deg

    # Weight estimate (PLA: 1.24 g/cm³)
    volume_cm3 = total_volume / 1000.0
    metrics["estimated_weight_g"] = volume_cm3 * 1.24

    # Check weight against limits
    envelope = envelope_for_zone(zone)
    if metrics["estimated_weight_g"] > envelope.max_shell_weight_g:
        warnings.append(
            f"Estimated weight ({metrics['estimated_weight_g']:.1f}g) exceeds "
            f"max for {zone} ({envelope.max_shell_weight_g}g)"
        )

    return HollowResult(
        shells=shells,
        zone=zone,
        wall_thickness_used="subtraction",
        warnings=warnings,
        metrics=metrics,
    )
