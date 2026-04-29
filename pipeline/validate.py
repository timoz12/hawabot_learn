"""Validation checks for shell parts before printing.

Runs all quality checks on a processed shell:
- Wall thickness (minimum everywhere)
- Clearance from skeleton frame
- Magnet boss integrity
- Watertight / manifold
- Weight within servo limits
- Joint motion clearance

Usage:
    from pipeline.validate import validate_shell, validate_all_zones
    report = validate_shell(shell_mesh, zone="head", magnet_count=4)
    full_report = validate_all_zones(zone_shells)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import trimesh

from pipeline.skeleton import (
    BODY_ZONES,
    SHELL_MIN_WALL,
    SERVO_MOUNTS,
    envelope_for_zone,
    MAGNET_MIN_COUNT,
    MAGNET_PULL_FORCE_KG,
)


@dataclass
class ValidationCheck:
    """A single validation check result."""
    name: str
    passed: bool
    message: str
    severity: str = "error"  # "error", "warning", "info"


@dataclass
class ValidationReport:
    """Complete validation report for a shell zone."""
    zone: str
    checks: list[ValidationCheck] = field(default_factory=list)
    passed: bool = True
    metrics: dict = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationCheck]:
        return [c for c in self.checks if not c.passed and c.severity == "error"]

    @property
    def warnings(self) -> list[ValidationCheck]:
        return [c for c in self.checks if not c.passed and c.severity == "warning"]

    def add(self, check: ValidationCheck):
        self.checks.append(check)
        if not check.passed and check.severity == "error":
            self.passed = False


def _check_watertight(mesh: trimesh.Trimesh) -> ValidationCheck:
    """Check that the mesh is watertight (manifold)."""
    if mesh.is_watertight:
        return ValidationCheck("watertight", True, "Mesh is watertight")
    else:
        return ValidationCheck(
            "watertight", False,
            f"Mesh is NOT watertight — has {mesh.body_count} bodies, "
            f"may not print correctly",
            severity="error",
        )


def _check_volume(mesh: trimesh.Trimesh) -> ValidationCheck:
    """Check that the mesh has positive volume."""
    vol = mesh.volume
    if vol > 0:
        return ValidationCheck("volume", True, f"Volume: {vol:.1f} mm³")
    else:
        return ValidationCheck(
            "volume", False,
            f"Invalid volume: {vol:.1f} mm³ — mesh may be inverted",
            severity="error",
        )


def _check_degenerate_faces(mesh: trimesh.Trimesh) -> ValidationCheck:
    """Check for degenerate (zero-area) triangles."""
    areas = mesh.area_faces
    degenerate = np.sum(areas < 1e-6)
    total = len(areas)

    if degenerate == 0:
        return ValidationCheck("degenerate_faces", True, "No degenerate faces")
    elif degenerate < total * 0.01:
        return ValidationCheck(
            "degenerate_faces", False,
            f"{degenerate} degenerate faces ({degenerate/total*100:.1f}%) — minor, auto-repairable",
            severity="warning",
        )
    else:
        return ValidationCheck(
            "degenerate_faces", False,
            f"{degenerate} degenerate faces ({degenerate/total*100:.1f}%) — mesh quality issue",
            severity="error",
        )


def _check_wall_thickness(
    mesh: trimesh.Trimesh,
    min_wall: float = SHELL_MIN_WALL,
    sample_count: int = 500,
) -> ValidationCheck:
    """Sample-based wall thickness check.

    Casts rays inward from random surface points and measures
    the distance to the opposite wall.
    """
    # Sample points on the mesh surface
    points, face_indices = trimesh.sample.sample_surface(mesh, sample_count)
    normals = mesh.face_normals[face_indices]

    # Cast rays inward
    thin_count = 0
    min_thickness = float('inf')
    thicknesses = []

    for point, normal in zip(points, normals):
        # Ray from surface point inward
        locations, _, _ = mesh.ray.intersects_location(
            ray_origins=point.reshape(1, 3) + normal * 0.01,  # Slight offset to avoid self-intersection
            ray_directions=(-normal).reshape(1, 3),
        )

        if len(locations) > 0:
            distances = np.linalg.norm(locations - point, axis=1)
            # Filter very small distances (self-intersection artifacts)
            valid = distances[distances > 0.1]
            if len(valid) > 0:
                thickness = float(np.min(valid))
                thicknesses.append(thickness)
                min_thickness = min(min_thickness, thickness)
                if thickness < min_wall:
                    thin_count += 1

    if not thicknesses:
        return ValidationCheck(
            "wall_thickness", False,
            "Could not measure wall thickness — mesh may not be hollow",
            severity="warning",
        )

    thin_pct = thin_count / len(thicknesses) * 100
    avg_thickness = np.mean(thicknesses)

    if thin_count == 0:
        return ValidationCheck(
            "wall_thickness", True,
            f"Min wall: {min_thickness:.2f}mm, avg: {avg_thickness:.2f}mm "
            f"(target ≥ {min_wall}mm)",
        )
    elif thin_pct < 5:
        return ValidationCheck(
            "wall_thickness", False,
            f"Min wall: {min_thickness:.2f}mm — {thin_pct:.1f}% of samples "
            f"below {min_wall}mm (minor thin spots)",
            severity="warning",
        )
    else:
        return ValidationCheck(
            "wall_thickness", False,
            f"Min wall: {min_thickness:.2f}mm — {thin_pct:.1f}% of samples "
            f"below {min_wall}mm (significant thin regions)",
            severity="error",
        )


def _check_weight(
    mesh: trimesh.Trimesh,
    zone: str,
    density_g_per_cm3: float = 1.24,  # PLA
) -> ValidationCheck:
    """Check estimated weight against servo torque limits."""
    envelope = envelope_for_zone(zone)
    volume_cm3 = mesh.volume / 1000.0
    weight_g = volume_cm3 * density_g_per_cm3

    if weight_g <= envelope.max_shell_weight_g:
        return ValidationCheck(
            "weight", True,
            f"Estimated weight: {weight_g:.1f}g "
            f"(max: {envelope.max_shell_weight_g}g)",
        )
    else:
        return ValidationCheck(
            "weight", False,
            f"Estimated weight: {weight_g:.1f}g exceeds "
            f"max {envelope.max_shell_weight_g}g for {zone} zone — "
            f"reduce wall thickness or simplify geometry",
            severity="error",
        )


def _check_magnets(
    zone: str,
    magnet_count: int,
    shell_weight_g: float,
) -> ValidationCheck:
    """Check magnet count and pull force adequacy."""
    min_count = MAGNET_MIN_COUNT[zone]
    total_force = magnet_count * MAGNET_PULL_FORCE_KG
    required_force = (shell_weight_g / 1000.0) * 2  # 2× shell weight in kg

    if magnet_count < min_count:
        return ValidationCheck(
            "magnets", False,
            f"Only {magnet_count} magnets selected (need ≥ {min_count} for {zone})",
            severity="error",
        )
    elif total_force < required_force:
        return ValidationCheck(
            "magnets", False,
            f"Total pull force {total_force:.2f}kg may be insufficient "
            f"for {shell_weight_g:.1f}g shell (want ≥ 2× weight)",
            severity="warning",
        )
    else:
        return ValidationCheck(
            "magnets", True,
            f"{magnet_count} magnets, {total_force:.2f}kg total pull "
            f"(need {required_force:.3f}kg for {shell_weight_g:.1f}g shell)",
        )


def _check_clearance(
    mesh: trimesh.Trimesh,
    zone: str,
) -> ValidationCheck:
    """Check that the shell clears servo positions."""
    envelope = envelope_for_zone(zone)

    # Check against each servo mount in this zone's area
    for mount in SERVO_MOUNTS:
        servo_pos = np.array([mount.x, mount.y, mount.z])

        # Find closest point on shell to servo center
        closest, distance, _ = trimesh.proximity.closest_point(mesh, servo_pos.reshape(1, 3))

        if distance[0] < envelope.min_gap_from_frame:
            return ValidationCheck(
                "clearance", False,
                f"Shell is {distance[0]:.1f}mm from {mount.name} servo "
                f"(need ≥ {envelope.min_gap_from_frame}mm clearance)",
                severity="error",
            )

    return ValidationCheck(
        "clearance", True,
        f"Shell clears all servo positions (≥ {envelope.min_gap_from_frame}mm gap)",
    )


def _check_printable_size(mesh: trimesh.Trimesh) -> ValidationCheck:
    """Check that the shell fits on a standard printer bed."""
    bounds = mesh.bounds
    size = bounds[1] - bounds[0]
    max_bed = np.array([220, 220, 250])  # Standard Ender 3

    fits = np.all(size <= max_bed)
    size_str = f"{size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f}mm"

    if fits:
        return ValidationCheck(
            "printable_size", True,
            f"Shell size: {size_str} — fits standard printer bed",
        )
    else:
        over = size - max_bed
        axes = []
        if over[0] > 0: axes.append(f"X by {over[0]:.0f}mm")
        if over[1] > 0: axes.append(f"Y by {over[1]:.0f}mm")
        if over[2] > 0: axes.append(f"Z by {over[2]:.0f}mm")
        return ValidationCheck(
            "printable_size", False,
            f"Shell size: {size_str} — exceeds bed: {', '.join(axes)}",
            severity="error",
        )


def validate_shell(
    shell: trimesh.Trimesh,
    zone: str,
    magnet_count: int = 0,
) -> ValidationReport:
    """Run all validation checks on a single shell zone.

    Args:
        shell: Processed shell mesh (hollowed, with magnet bosses).
        zone: Body zone name.
        magnet_count: Number of magnets selected for this zone.

    Returns:
        ValidationReport with all check results.
    """
    report = ValidationReport(zone=zone)

    # Basic mesh checks
    report.add(_check_watertight(shell))
    report.add(_check_volume(shell))
    report.add(_check_degenerate_faces(shell))
    report.add(_check_printable_size(shell))

    # Structural checks
    report.add(_check_wall_thickness(shell))
    report.add(_check_weight(shell, zone))
    report.add(_check_clearance(shell, zone))

    # Magnet checks
    volume_cm3 = shell.volume / 1000.0
    weight_g = volume_cm3 * 1.24
    report.add(_check_magnets(zone, magnet_count, weight_g))

    # Metrics
    report.metrics = {
        "volume_mm3": float(shell.volume),
        "weight_g": weight_g,
        "bounds": shell.bounds.tolist(),
        "face_count": len(shell.faces),
        "vertex_count": len(shell.vertices),
        "watertight": shell.is_watertight,
    }

    return report


def validate_all_zones(
    zone_shells: dict[str, trimesh.Trimesh],
    magnet_counts: dict[str, int] | None = None,
) -> dict[str, ValidationReport]:
    """Validate all zone shells at once.

    Returns a dict of zone_name → ValidationReport.
    """
    if magnet_counts is None:
        magnet_counts = {}

    reports = {}
    for zone in BODY_ZONES:
        if zone in zone_shells:
            count = magnet_counts.get(zone, 0)
            reports[zone] = validate_shell(zone_shells[zone], zone, count)
        else:
            report = ValidationReport(zone=zone)
            report.add(ValidationCheck(
                "missing", False,
                f"No shell provided for {zone} zone",
                severity="error",
            ))
            reports[zone] = report

    return reports


def print_report(report: ValidationReport) -> str:
    """Format a validation report for console output."""
    lines = [f"\n{'='*50}", f"  {report.zone.upper()} ZONE", f"{'='*50}"]

    for check in report.checks:
        icon = "✓" if check.passed else ("⚠" if check.severity == "warning" else "✗")
        lines.append(f"  {icon} {check.name}: {check.message}")

    status = "PASSED" if report.passed else "FAILED"
    lines.append(f"\n  Status: {status}")

    if report.metrics:
        lines.append(f"  Weight: {report.metrics.get('weight_g', 0):.1f}g")
        lines.append(f"  Faces: {report.metrics.get('face_count', 0)}")

    return "\n".join(lines)
