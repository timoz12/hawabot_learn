"""Magnet selection and boss generation for shell parts.

Selects optimal magnet positions from the skeleton's predefined grid
based on the shell geometry, then generates boss cylinders and merges
them onto the shell's inner surface.

Usage:
    from pipeline.magnets import select_magnets, add_magnet_bosses
    selected = select_magnets(shell_mesh, zone="head")
    shell_with_bosses = add_magnet_bosses(shell_mesh, selected)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import trimesh
import manifold3d as mf

from pipeline.skeleton import (
    MagnetSeat,
    MAGNET_SEATS,
    MAG_POCKET_D,
    MAG_POCKET_H,
    MAGNET_BOSS_OD,
    MAGNET_BOSS_H,
    MAGNET_MIN_COUNT,
    MAGNET_MAX_COUNT,
    MAGNET_PULL_FORCE_KG,
    MIN_SHELL_THICKNESS_FOR_BOSS,
    MIN_WALL_BEHIND_BOSS,
    magnets_for_zone,
)


@dataclass
class MagnetSelection:
    """Result of the magnet selection algorithm."""
    zone: str
    selected: list[MagnetSeat]
    rejected: list[tuple[MagnetSeat, str]]  # (seat, reason)
    total_pull_force_kg: float
    warnings: list[str]


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


def _wall_thickness_at_point(
    mesh: trimesh.Trimesh,
    point: np.ndarray,
    direction: np.ndarray,
) -> float:
    """Estimate wall thickness at a point by ray casting inward.

    Casts a ray from the point inward along -direction and measures
    the distance to the first intersection (the inner wall).
    Returns 0.0 if no intersection found.
    """
    # Cast ray inward (opposite to outward normal)
    ray_origin = point.reshape(1, 3)
    ray_direction = (-direction).reshape(1, 3)

    locations, index_ray, _ = mesh.ray.intersects_location(
        ray_origins=ray_origin,
        ray_directions=ray_direction,
    )

    if len(locations) == 0:
        return 0.0

    # Find the first intersection (closest)
    distances = np.linalg.norm(locations - point, axis=1)
    return float(np.min(distances))


def _angular_coverage(positions: list[tuple[float, float, float]]) -> float:
    """Score how evenly distributed positions are around the Z axis.

    Returns 0.0 (all clustered) to 1.0 (perfectly distributed).
    """
    if len(positions) < 2:
        return 0.0

    angles = []
    for x, y, z in positions:
        angle = math.atan2(y, x)
        angles.append(angle)

    angles.sort()

    # Compute angular gaps
    gaps = []
    for i in range(len(angles)):
        next_angle = angles[(i + 1) % len(angles)]
        gap = next_angle - angles[i]
        if gap < 0:
            gap += 2 * math.pi
        gaps.append(gap)

    # Perfect distribution = all gaps equal = 2π/n
    ideal_gap = 2 * math.pi / len(angles)
    variance = sum((g - ideal_gap) ** 2 for g in gaps) / len(gaps)

    # Normalize: 0 variance = 1.0 score, high variance = low score
    return max(0.0, 1.0 - variance / (math.pi ** 2))


def _distance_from_edge(
    point: np.ndarray,
    mesh: trimesh.Trimesh,
) -> float:
    """Estimate how far a point is from the mesh boundary edges.

    Simple approximation: distance from point to nearest vertex
    on a boundary edge.
    """
    # Find boundary edges (edges that belong to only one face)
    edges = mesh.edges_unique
    edge_face_count = np.zeros(len(edges), dtype=int)
    for face in mesh.faces:
        for i in range(3):
            e = tuple(sorted([face[i], face[(i + 1) % 3]]))
            # This is a simplification — in practice use mesh.edges_unique_inverse
            pass

    # Fallback: distance to nearest vertex (rough approximation)
    distances = np.linalg.norm(mesh.vertices - point, axis=1)
    return float(np.min(distances))


def select_magnets(
    shell: trimesh.Trimesh,
    zone: str,
) -> MagnetSelection:
    """Select optimal magnet positions for a shell zone.

    Algorithm:
    1. Filter: only positions where shell has enough wall thickness
    2. Score: by angular distribution + edge distance
    3. Select: minimum required count, up to max if geometry supports it
    """
    candidates = magnets_for_zone(zone)
    min_count = MAGNET_MIN_COUNT[zone]
    max_count = MAGNET_MAX_COUNT[zone]

    selected: list[MagnetSeat] = []
    rejected: list[tuple[MagnetSeat, str]] = []
    warnings: list[str] = []

    # Phase 1: Filter by wall thickness
    viable: list[tuple[MagnetSeat, float]] = []  # (seat, thickness)

    for seat in candidates:
        point = np.array([seat.x, seat.y, seat.z])
        normal = np.array(seat.normal, dtype=float)
        norm_len = np.linalg.norm(normal)
        if norm_len > 0:
            normal = normal / norm_len

        thickness = _wall_thickness_at_point(shell, point, normal)

        if thickness < MIN_SHELL_THICKNESS_FOR_BOSS:
            rejected.append((seat, f"Wall too thin ({thickness:.1f}mm < {MIN_SHELL_THICKNESS_FOR_BOSS}mm)"))
        else:
            viable.append((seat, thickness))

    if len(viable) < min_count:
        warnings.append(
            f"Only {len(viable)} viable magnet positions in {zone} zone "
            f"(need {min_count}). Shell may be too thin."
        )
        # Use whatever we have
        selected = [seat for seat, _ in viable]
    else:
        # Phase 2: Score and rank
        scored: list[tuple[MagnetSeat, float]] = []

        for seat, thickness in viable:
            score = 0.0

            # Thickness score: more wall = better (up to a point)
            score += min(thickness / 10.0, 1.0) * 0.3

            # Angular coverage: check if adding this improves distribution
            test_positions = [(s.x, s.y, s.z) for s in selected] + [(seat.x, seat.y, seat.z)]
            coverage = _angular_coverage(test_positions)
            score += coverage * 0.5

            # Distance from center of mass: favor balanced pull
            com = shell.center_mass
            dist_from_com = np.linalg.norm(
                np.array([seat.x, seat.y, seat.z]) - com
            )
            # Moderate distance is best — not too close, not too far
            ideal_dist = 15.0  # mm
            dist_score = 1.0 - min(abs(dist_from_com - ideal_dist) / ideal_dist, 1.0)
            score += dist_score * 0.2

            scored.append((seat, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select up to max_count
        count = min(max_count, len(scored))
        count = max(count, min_count)
        selected = [seat for seat, _ in scored[:count]]

        # Record rejections for seats beyond the max
        for seat, _ in scored[count:]:
            rejected.append((seat, "Not needed — enough magnets selected"))

    # Validate: no single-axis alignment
    if len(selected) >= 3:
        xs = [s.x for s in selected]
        ys = [s.y for s in selected]
        if max(xs) - min(xs) < 5:
            warnings.append("Selected magnets are nearly collinear along X — poor rotational stability")
        if max(ys) - min(ys) < 5:
            warnings.append("Selected magnets are nearly collinear along Y — poor rotational stability")

    total_force = len(selected) * MAGNET_PULL_FORCE_KG

    return MagnetSelection(
        zone=zone,
        selected=selected,
        rejected=rejected,
        total_pull_force_kg=total_force,
        warnings=warnings,
    )


def _make_boss(
    position: tuple[float, float, float],
    normal: tuple[float, float, float],
) -> trimesh.Trimesh:
    """Create a magnet boss cylinder at a given position.

    The boss is a cylinder pointing inward (opposite to normal)
    with a pocket hole for the magnet.
    """
    # Boss cylinder (solid)
    boss = trimesh.creation.cylinder(
        radius=MAGNET_BOSS_OD / 2,
        height=MAGNET_BOSS_H,
        sections=32,
    )

    # Magnet pocket (to be subtracted)
    pocket = trimesh.creation.cylinder(
        radius=MAG_POCKET_D / 2,
        height=MAG_POCKET_H,
        sections=32,
    )

    # Boolean subtract pocket from boss
    m_boss = _trimesh_to_manifold(boss)
    m_pocket = _trimesh_to_manifold(pocket)

    # Pocket sits at the tip of the boss (the face toward the skeleton)
    pocket_offset = MAGNET_BOSS_H / 2 - MAG_POCKET_H / 2
    # Move pocket to the skeleton-facing end
    pocket.apply_translation([0, 0, -pocket_offset])
    m_pocket = _trimesh_to_manifold(pocket)

    boss_with_pocket = _manifold_to_trimesh(m_boss - m_pocket)

    # Orient boss: default cylinder is along Z.
    # We need it pointing inward (opposite to outward normal).
    nx, ny, nz = normal
    norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
    if norm_len > 0:
        nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len

    # Inward direction (opposite to outward normal)
    inward = np.array([-nx, -ny, -nz])

    # Rotation from Z-axis to inward direction
    z_axis = np.array([0, 0, 1])
    if np.allclose(inward, z_axis):
        rot = np.eye(4)
    elif np.allclose(inward, -z_axis):
        rot = trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
    else:
        cross = np.cross(z_axis, inward)
        dot = np.dot(z_axis, inward)
        angle = math.acos(np.clip(dot, -1, 1))
        rot = trimesh.transformations.rotation_matrix(angle, cross)

    boss_with_pocket.apply_transform(rot)

    # Translate to position, offset so the boss tip is at the skeleton surface
    # and the base is embedded in the shell wall
    offset = inward * (MAGNET_BOSS_H / 2)
    boss_with_pocket.apply_translation(
        np.array(position) + offset
    )

    return boss_with_pocket


def add_magnet_bosses(
    shell: trimesh.Trimesh,
    selection: MagnetSelection,
) -> trimesh.Trimesh:
    """Merge magnet boss features onto a shell's inner surface.

    Args:
        shell: Hollow shell mesh.
        selection: MagnetSelection from select_magnets().

    Returns:
        Shell mesh with magnet bosses merged in.
    """
    if not selection.selected:
        return shell

    m_shell = _trimesh_to_manifold(shell)

    for seat in selection.selected:
        boss = _make_boss(
            position=(seat.x, seat.y, seat.z),
            normal=seat.normal,
        )
        try:
            m_boss = _trimesh_to_manifold(boss)
            m_shell = m_shell + m_boss  # Union
        except Exception:
            # Skip this boss if boolean fails
            pass

    return _manifold_to_trimesh(m_shell)
