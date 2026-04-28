"""Joint clearance cuts — carve rotation volumes at each joint so parts can move.

For each joint in the Spark skeleton, we define a clearance volume: a swept
shape representing the range of motion for that joint. These volumes are
subtracted from the shell so the arms/head can actually rotate.

We also define split planes — the boundaries where the shell gets cut into
separate printable sections (head, torso, left arm, right arm).
"""

from __future__ import annotations

import numpy as np
import trimesh
import manifold3d as mf

from pipeline.skeleton import (
    SHOULDER_Z, SHOULDER_SPREAD, HEAD_Z, SERVO_SG90,
    TORSO_HEIGHT, BASE_HEIGHT,
)


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


def _make_clearance_ring(
    center: tuple[float, float, float],
    axis: str,
    inner_radius: float,
    outer_radius: float,
    height: float,
) -> trimesh.Trimesh:
    """Create a ring/annular cylinder for joint clearance.

    This represents the gap needed around a joint so that the rotating
    part doesn't collide with the stationary part.
    """
    outer = trimesh.creation.cylinder(radius=outer_radius, height=height)
    inner = trimesh.creation.cylinder(radius=inner_radius, height=height)

    outer_mf = _trimesh_to_manifold(outer)
    inner_mf = _trimesh_to_manifold(inner)
    ring_mf = outer_mf - inner_mf

    ring = _manifold_to_trimesh(ring_mf)

    # Rotate based on axis
    if axis == "y":  # Pitch — rotation around Y axis
        rot = trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0])
        ring.apply_transform(rot)
    elif axis == "x":  # Roll — rotation around X axis
        rot = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
        ring.apply_transform(rot)
    # axis == "z" is default (yaw — rotation around Z axis)

    ring.apply_translation(center)
    return ring


def build_joint_clearances(scale_factor: float = 1.0) -> list[trimesh.Trimesh]:
    """Build clearance volumes for all Spark joints.

    Returns a list of meshes to subtract from the shell.

    Args:
        scale_factor: How much the skeleton was scaled to fit the sculpture.
    """
    s = scale_factor
    clearances = []

    # Gap width — how much space to leave around each joint
    gap = 3.0 * s  # 3mm gap scaled

    # 1. Head pan joint — yaw rotation at top of torso
    # Ring around the neck so the head can turn
    head_clearance = _make_clearance_ring(
        center=(0, 0, (HEAD_Z - 5) * s),
        axis="z",
        inner_radius=12 * s,
        outer_radius=20 * s,
        height=gap * 2,
    )
    clearances.append(head_clearance)

    # 2. Left shoulder — pitch rotation
    # Ring around the shoulder joint so the arm can raise/lower
    l_shoulder_clearance = _make_clearance_ring(
        center=(-SHOULDER_SPREAD * s, 0, SHOULDER_Z * s),
        axis="y",
        inner_radius=8 * s,
        outer_radius=18 * s,
        height=gap * 2,
    )
    clearances.append(l_shoulder_clearance)

    # 3. Right shoulder — pitch rotation
    r_shoulder_clearance = _make_clearance_ring(
        center=(SHOULDER_SPREAD * s, 0, SHOULDER_Z * s),
        axis="y",
        inner_radius=8 * s,
        outer_radius=18 * s,
        height=gap * 2,
    )
    clearances.append(r_shoulder_clearance)

    # 4. Waist — yaw rotation at the base
    # Ring so the upper body can turn on the base
    waist_clearance = _make_clearance_ring(
        center=(0, 0, 5 * s),
        axis="z",
        inner_radius=15 * s,
        outer_radius=30 * s,
        height=gap,
    )
    clearances.append(waist_clearance)

    return clearances


def build_split_planes(
    scale_factor: float = 1.0,
    shell_bounds: np.ndarray | None = None,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Define the planes where the shell gets split into sections.

    Uses proportional positions relative to the shell bounds for robustness
    across different character shapes.

    Returns dict of section_name → (plane_origin, plane_normal).
    """
    s = scale_factor

    if shell_bounds is not None:
        mins, maxs = shell_bounds[0], shell_bounds[1]
        center_x = (mins[0] + maxs[0]) / 2
        center_y = (mins[1] + maxs[1]) / 2
        height = maxs[2] - mins[2]
        width = maxs[0] - mins[0]

        # Head split: 80% up the height
        head_z = mins[2] + height * 0.80
        # Waist split: 25% up the height
        waist_z = mins[2] + height * 0.25
        # Arm splits: 25% in from each side
        left_x = mins[0] + width * 0.25
        right_x = maxs[0] - width * 0.25
    else:
        center_x, center_y = 0, 0
        head_z = (HEAD_Z - 8) * s
        waist_z = 8 * s
        left_x = (-SHOULDER_SPREAD + 5) * s
        right_x = (SHOULDER_SPREAD - 5) * s

    return {
        "head_split": (
            np.array([center_x, center_y, head_z]),
            np.array([0, 0, 1.0]),
        ),
        "left_arm_split": (
            np.array([left_x, center_y, head_z * 0.9]),
            np.array([-1.0, 0, 0]),
        ),
        "right_arm_split": (
            np.array([right_x, center_y, head_z * 0.9]),
            np.array([1.0, 0, 0]),
        ),
        "waist_split": (
            np.array([center_x, center_y, waist_z]),
            np.array([0, 0, 1.0]),
        ),
    }


def cut_joint_clearances(
    shell: trimesh.Trimesh,
    scale_factor: float = 1.0,
) -> trimesh.Trimesh:
    """Subtract joint clearance volumes from the shell.

    This creates the gaps needed for joints to rotate freely.
    """
    shell_mf = _trimesh_to_manifold(shell)

    for clearance in build_joint_clearances(scale_factor):
        try:
            clearance_mf = _trimesh_to_manifold(clearance)
            shell_mf = shell_mf - clearance_mf
        except Exception as e:
            print(f"  Warning: clearance cut failed: {e}")

    return _manifold_to_trimesh(shell_mf)


def split_shell(
    shell: trimesh.Trimesh,
    scale_factor: float = 1.0,
) -> dict[str, trimesh.Trimesh]:
    """Split the shell into printable sections at joint boundaries.

    Uses manifold3d's trim_by_plane for watertight cuts.
    Returns dict of section_name → mesh.
    Sections: head, torso, left_arm, right_arm, base.
    """
    planes = build_split_planes(scale_factor, shell_bounds=shell.bounds)
    sections = {}

    shell_mf = _trimesh_to_manifold(shell)

    # Helper: split a manifold by a plane, returning (above, below)
    def split_at_plane(manifold, origin, normal):
        # trim_by_plane(normal, origin_offset) — keeps the +normal side
        offset = float(np.dot(origin, normal))
        n = (float(normal[0]), float(normal[1]), float(normal[2]))
        neg_n = (-n[0], -n[1], -n[2])
        above = manifold.trim_by_plane(n, offset)
        below = manifold.trim_by_plane(neg_n, -offset)
        return above, below

    remaining = shell_mf

    # 1. Split head off the top (everything above head_split plane)
    origin, normal = planes["head_split"]
    try:
        head_mf, remaining = split_at_plane(remaining, origin, normal)
        if head_mf.num_vert() > 10:
            sections["head"] = _manifold_to_trimesh(head_mf)
    except Exception as e:
        print(f"  Warning: head split failed: {e}")

    # 2. Split base off the bottom (everything below waist_split plane)
    origin, normal = planes["waist_split"]
    try:
        _, base_mf = split_at_plane(remaining, origin, normal)
        remaining_above, _ = split_at_plane(remaining, origin, normal)
        if base_mf.num_vert() > 10:
            sections["base"] = _manifold_to_trimesh(base_mf)
        remaining = remaining_above
    except Exception as e:
        print(f"  Warning: waist split failed: {e}")

    # 3. Split left arm (everything left of left_arm_split plane)
    origin, normal = planes["left_arm_split"]
    try:
        _, left_arm_mf = split_at_plane(remaining, origin, normal)
        remaining, _ = split_at_plane(remaining, origin, normal)
        if left_arm_mf.num_vert() > 10:
            sections["left_arm"] = _manifold_to_trimesh(left_arm_mf)
    except Exception as e:
        print(f"  Warning: left arm split failed: {e}")

    # 4. Split right arm (everything right of right_arm_split plane)
    origin, normal = planes["right_arm_split"]
    try:
        right_arm_mf, remaining = split_at_plane(remaining, origin, normal)
        if right_arm_mf.num_vert() > 10:
            sections["right_arm"] = _manifold_to_trimesh(right_arm_mf)
    except Exception as e:
        print(f"  Warning: right arm split failed: {e}")

    # 5. Whatever remains is the torso
    if remaining.num_vert() > 10:
        sections["torso"] = _manifold_to_trimesh(remaining)

    return sections


if __name__ == "__main__":
    import sys

    shell_path = sys.argv[1] if len(sys.argv) > 1 else "shell_naruto.stl"

    print(f"Loading shell: {shell_path}")
    shell = trimesh.load(shell_path, force="mesh")
    print(f"  {len(shell.vertices):,} vertices, {len(shell.faces):,} faces")

    # Compute scale factor (skeleton was scaled to fit this shell)
    from pipeline.skeleton import build_skeleton_for_subtraction
    skeleton = build_skeleton_for_subtraction()
    skel_height = skeleton.bounding_box.extents[2]
    shell_height = shell.bounding_box.extents[2]
    scale_factor = shell_height / (skel_height * 1.3)  # approximate
    print(f"  Estimated scale factor: {scale_factor:.2f}")

    # Step 1: Joint clearance cuts
    print("\nCutting joint clearances...")
    shell_cut = cut_joint_clearances(shell, scale_factor)
    print(f"  Result: {len(shell_cut.vertices):,} verts, watertight={shell_cut.is_watertight}")

    # Step 2: Split into sections
    print("\nSplitting into sections...")
    sections = split_shell(shell_cut, scale_factor)
    print(f"  Sections created: {len(sections)}")

    for name, section in sections.items():
        section.export(f"section_{name}.stl")
        bounds = section.bounds
        size = bounds[1] - bounds[0]
        print(f"  {name:12s}: {len(section.vertices):5,} verts, "
              f"{size[0]:.0f}x{size[1]:.0f}x{size[2]:.0f}mm, "
              f"watertight={section.is_watertight}")

    print("\nDone! Check section_*.stl files.")
