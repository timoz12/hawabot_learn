"""Simulation engine — tracks joint state and provides a queryable robot model."""

from __future__ import annotations

from typing import Any

from hawabot.config.tiers import TierDefinition
from hawabot.drivers.mock import MockDriver


class SimulationEngine:
    """Wraps a MockDriver to provide higher-level simulation queries.

    Used by the visualizer and curriculum validator to inspect robot state
    without going through the student-facing API.
    """

    def __init__(self, driver: MockDriver, tier: TierDefinition) -> None:
        self._driver = driver
        self._tier = tier

    @property
    def joint_angles(self) -> dict[str, float]:
        """Current angle of every joint."""
        return self._driver.joint_states

    @property
    def joint_names(self) -> list[str]:
        return sorted(self._tier.joints.keys())

    def joint_limits(self, joint_name: str) -> tuple[float, float]:
        spec = self._tier.joints[joint_name]
        return (spec.min_angle, spec.max_angle)

    @property
    def event_log(self) -> list[dict[str, Any]]:
        return self._driver.get_event_log()

    @property
    def dof(self) -> int:
        return len(self._tier.joints)

    def summary(self) -> str:
        """Human-readable state summary."""
        lines = [f"Tier: {self._tier.display_name} ({self.dof} DOF)"]
        for name in self.joint_names:
            angle = self._driver.get_angle(name)
            lo, hi = self.joint_limits(name)
            lines.append(f"  {name:30s}  {angle:7.1f}°  [{lo:.0f}°, {hi:.0f}°]")
        return "\n".join(lines)
