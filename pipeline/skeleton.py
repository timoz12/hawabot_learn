"""Spark tabletop skeleton geometry generator.

Builds a 3D mesh representing the internal volume of the Spark tier robot:
- Base plate (sits on desk)
- Torso column (vertical post)
- Waist servo housing
- Head servo housing
- Left/right shoulder servo housings
- Wire channels between components
- Electronics bay (Pi Pico W)

All dimensions in millimeters. The skeleton is what gets SUBTRACTED from
the sculpture to create the hollow shell.
"""

from __future__ import annotations

import numpy as np
import trimesh
from trimesh.creation import box, cylinder


# ---------------------------------------------------------------------------
# Spark skeleton dimensions (mm)
# Based on SG90/MG90S servo dimensions + Pi Pico W
# ---------------------------------------------------------------------------

# SG90 servo: 22.2 x 11.8 x 22.7 mm (body), shaft on top
SERVO_SG90 = {"width": 22.5, "depth": 12.5, "height": 23.0}

# MG90S servo: 22.5 x 12.2 x 22.5 mm (body), slightly beefier
SERVO_MG90S = {"width": 23.0, "depth": 13.0, "height": 23.0}

# Pi Pico W: 51 x 21 x 3.8 mm (board only)
PICO_W = {"width": 52.0, "depth": 22.0, "height": 10.0}  # height includes clearance

# Overall skeleton proportions for a ~150mm tall tabletop companion
BASE_WIDTH = 80.0
BASE_DEPTH = 60.0
BASE_HEIGHT = 8.0

TORSO_DIAMETER = 20.0
TORSO_HEIGHT = 60.0

# Vertical positions (Z, from base top surface)
WAIST_Z = 5.0  # waist servo sits just above base
SHOULDER_Z = 55.0  # shoulder servos near top of torso
HEAD_Z = 65.0  # head servo at very top
ELECTRONICS_Z = 0.0  # Pi Pico in the base

# Shoulder spread (distance from center to each shoulder)
SHOULDER_SPREAD = 35.0

# Clearance added around each component for wire routing and tolerance
CLEARANCE = 2.0


def _servo_box(servo_spec: dict, clearance: float = CLEARANCE) -> trimesh.Trimesh:
    """Create a box representing a servo + clearance envelope."""
    return box(extents=[
        servo_spec["width"] + clearance * 2,
        servo_spec["depth"] + clearance * 2,
        servo_spec["height"] + clearance * 2,
    ])


def _translate(mesh: trimesh.Trimesh, x: float = 0, y: float = 0, z: float = 0) -> trimesh.Trimesh:
    """Return a translated copy of the mesh."""
    m = mesh.copy()
    m.apply_translation([x, y, z])
    return m


def _rotate_z(mesh: trimesh.Trimesh, degrees: float) -> trimesh.Trimesh:
    """Return a copy rotated around Z axis."""
    m = mesh.copy()
    rad = np.radians(degrees)
    rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
    m.apply_transform(rot)
    return m


def build_skeleton() -> trimesh.Trimesh:
    """Build the complete Spark skeleton as a single combined mesh.

    The skeleton represents ALL internal volume that must be subtracted
    from a sculpture to create the printable shell. It includes servo
    housings, wire channels, electronics, and structural elements.

    Origin is at the center of the base plate's top surface.
    +Z is up, +X is right (from robot's perspective), +Y is forward.
    """
    parts: list[trimesh.Trimesh] = []

    # 1. Base plate — flat platform the robot sits on
    base = box(extents=[BASE_WIDTH, BASE_DEPTH, BASE_HEIGHT])
    base = _translate(base, z=-BASE_HEIGHT / 2)
    parts.append(base)

    # 2. Electronics bay — Pi Pico W sits inside the base
    pico = box(extents=[PICO_W["width"] + CLEARANCE * 2,
                        PICO_W["depth"] + CLEARANCE * 2,
                        PICO_W["height"] + CLEARANCE * 2])
    pico = _translate(pico, x=15, z=ELECTRONICS_Z + PICO_W["height"] / 2 + 2)
    parts.append(pico)

    # 3. Torso column — central structural post
    torso = cylinder(radius=TORSO_DIAMETER / 2, height=TORSO_HEIGHT)
    torso = _translate(torso, z=TORSO_HEIGHT / 2)
    parts.append(torso)

    # 4. Waist servo (SG90) — at the base of the torso, rotates upper body
    waist_servo = _servo_box(SERVO_SG90)
    waist_servo = _translate(waist_servo, z=WAIST_Z + SERVO_SG90["height"] / 2)
    parts.append(waist_servo)

    # 5. Left shoulder servo (MG90S) — arm pitch
    l_shoulder = _servo_box(SERVO_MG90S)
    l_shoulder = _rotate_z(l_shoulder, 90)  # Orient for pitch axis
    l_shoulder = _translate(l_shoulder, x=-SHOULDER_SPREAD, z=SHOULDER_Z)
    parts.append(l_shoulder)

    # 6. Right shoulder servo (MG90S)
    r_shoulder = _servo_box(SERVO_MG90S)
    r_shoulder = _rotate_z(r_shoulder, 90)
    r_shoulder = _translate(r_shoulder, x=SHOULDER_SPREAD, z=SHOULDER_Z)
    parts.append(r_shoulder)

    # 7. Head servo (SG90) — pan
    head_servo = _servo_box(SERVO_SG90)
    head_servo = _translate(head_servo, z=HEAD_Z)
    parts.append(head_servo)

    # 8. Head tilt servo (SG90) — stacked above head pan
    head_tilt = _servo_box(SERVO_SG90)
    head_tilt = _rotate_z(head_tilt, 90)
    head_tilt = _translate(head_tilt, z=HEAD_Z + SERVO_SG90["height"] + 3)
    parts.append(head_tilt)

    # 9. Wire channels — vertical channel through torso for cables
    wire_channel = box(extents=[10, 10, TORSO_HEIGHT + 20])
    wire_channel = _translate(wire_channel, x=12, z=TORSO_HEIGHT / 2)
    parts.append(wire_channel)

    # Horizontal channels from torso to each shoulder
    for x_sign in [-1, 1]:
        h_channel = box(extents=[SHOULDER_SPREAD, 8, 8])
        h_channel = _translate(h_channel, x=x_sign * SHOULDER_SPREAD / 2, z=SHOULDER_Z)
        parts.append(h_channel)

    # 10. Combine all parts into a single mesh
    combined = parts[0]
    for part in parts[1:]:
        combined = trimesh.util.concatenate([combined, part])

    return combined


def build_skeleton_for_subtraction() -> trimesh.Trimesh:
    """Build the skeleton and ensure it's a proper volume for boolean operations.

    Uses convex decomposition to create a watertight volume suitable
    for boolean subtraction from a sculpture mesh.
    """
    skeleton = build_skeleton()

    # The concatenated mesh isn't a single solid — it's overlapping parts.
    # For boolean subtraction we need the union of all parts.
    # Use manifold3d for robust boolean union.
    try:
        import manifold3d as mf

        manifolds = []
        for part_mesh in build_skeleton_parts():
            # Each part is already a simple primitive (box/cylinder), so it's watertight
            m = mf.Manifold(
                mf.Mesh(
                    vert_properties=np.array(part_mesh.vertices, dtype=np.float32),
                    tri_verts=np.array(part_mesh.faces, dtype=np.uint32),
                )
            )
            manifolds.append(m)

        # Boolean union of all parts
        result = manifolds[0]
        for m in manifolds[1:]:
            result = result + m

        # Convert back to trimesh
        out_mesh = result.to_mesh()
        return trimesh.Trimesh(
            vertices=out_mesh.vert_properties[:, :3],
            faces=out_mesh.tri_verts,
        )
    except Exception:
        # Fallback: return concatenated mesh (less clean but functional)
        return skeleton


def build_skeleton_parts() -> list[trimesh.Trimesh]:
    """Return individual skeleton parts as separate watertight meshes.

    Useful for visualization and for boolean union via manifold3d.
    """
    parts = []

    # Base plate
    base = box(extents=[BASE_WIDTH, BASE_DEPTH, BASE_HEIGHT])
    base.apply_translation([0, 0, -BASE_HEIGHT / 2])
    parts.append(base)

    # Electronics bay
    pico = box(extents=[PICO_W["width"] + CLEARANCE * 2,
                        PICO_W["depth"] + CLEARANCE * 2,
                        PICO_W["height"] + CLEARANCE * 2])
    pico.apply_translation([15, 0, ELECTRONICS_Z + PICO_W["height"] / 2 + 2])
    parts.append(pico)

    # Torso
    torso = cylinder(radius=TORSO_DIAMETER / 2, height=TORSO_HEIGHT)
    torso.apply_translation([0, 0, TORSO_HEIGHT / 2])
    parts.append(torso)

    # Waist servo
    ws = _servo_box(SERVO_SG90)
    ws.apply_translation([0, 0, WAIST_Z + SERVO_SG90["height"] / 2])
    parts.append(ws)

    # Shoulder servos
    for x_sign, name in [(-1, "left"), (1, "right")]:
        s = _servo_box(SERVO_MG90S)
        rot = trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
        s.apply_transform(rot)
        s.apply_translation([x_sign * SHOULDER_SPREAD, 0, SHOULDER_Z])
        parts.append(s)

    # Head pan servo
    hs = _servo_box(SERVO_SG90)
    hs.apply_translation([0, 0, HEAD_Z])
    parts.append(hs)

    # Head tilt servo
    ht = _servo_box(SERVO_SG90)
    rot = trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
    ht.apply_transform(rot)
    ht.apply_translation([0, 0, HEAD_Z + SERVO_SG90["height"] + 3])
    parts.append(ht)

    # Wire channels
    wc = box(extents=[10, 10, TORSO_HEIGHT + 20])
    wc.apply_translation([12, 0, TORSO_HEIGHT / 2])
    parts.append(wc)

    for x_sign in [-1, 1]:
        hc = box(extents=[SHOULDER_SPREAD, 8, 8])
        hc.apply_translation([x_sign * SHOULDER_SPREAD / 2, 0, SHOULDER_Z])
        parts.append(hc)

    return parts


def save_skeleton(path: str = "skeleton_spark.stl") -> None:
    """Build and save the Spark skeleton to an STL file."""
    skeleton = build_skeleton_for_subtraction()
    skeleton.export(path)
    print(f"Skeleton saved to {path}")
    print(f"  Vertices: {len(skeleton.vertices)}")
    print(f"  Faces: {len(skeleton.faces)}")
    print(f"  Watertight: {skeleton.is_watertight}")
    bounds = skeleton.bounds
    size = bounds[1] - bounds[0]
    print(f"  Size: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")


if __name__ == "__main__":
    save_skeleton()
