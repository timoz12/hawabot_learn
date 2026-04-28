"""Mock driver — simulates hardware in-memory for development and testing."""

from __future__ import annotations

import time
from typing import Any

from hawabot.config.tiers import JointSpec, TierDefinition
from hawabot.drivers.base import BaseDriver


class MockDriver(BaseDriver):
    """Simulates servo hardware without any physical devices.

    Maintains joint state in memory, respects angle limits from the tier
    definition, and logs every action for curriculum validation.
    """

    def __init__(self, tier: TierDefinition) -> None:
        self._tier = tier
        self._angles: dict[str, float] = {}
        self._events: list[dict[str, Any]] = []
        self._start_time = time.monotonic()

        # Initialise all joints to their default angles
        for name, spec in tier.joints.items():
            self._angles[name] = spec.default_angle

    def set_angle(self, joint_name: str, angle: float) -> None:
        spec = self._tier.joints.get(joint_name)
        if spec is None:
            available = ", ".join(sorted(self._tier.joints))
            raise ValueError(
                f"Joint '{joint_name}' not found in tier '{self._tier.display_name}'. "
                f"Available joints: {available}"
            )

        clamped = max(spec.min_angle, min(spec.max_angle, angle))
        old_angle = self._angles[joint_name]
        self._angles[joint_name] = clamped

        self._log("set_angle", joint=joint_name, from_angle=old_angle, to_angle=clamped,
                  requested=angle, clamped=clamped != angle)

    def get_angle(self, joint_name: str) -> float:
        if joint_name not in self._angles:
            raise ValueError(f"Joint '{joint_name}' not found")
        return self._angles[joint_name]

    def get_temperature(self, joint_name: str) -> float | None:
        if joint_name not in self._angles:
            return None
        return 35.0  # simulated ambient

    def get_voltage(self) -> float | None:
        return 5.0  # simulated nominal

    def wait(self, seconds: float) -> None:
        self._log("wait", duration_s=seconds)
        # In mock mode, don't actually sleep — just record the intent.
        # This keeps tests fast. Set HAWABOT_MOCK_REALTIME=1 to sleep.
        import os
        if os.environ.get("HAWABOT_MOCK_REALTIME") == "1":
            time.sleep(seconds)

    def get_event_log(self) -> list[dict]:
        return list(self._events)

    def shutdown(self) -> None:
        for name, spec in self._tier.joints.items():
            self._angles[name] = spec.default_angle
        self._log("shutdown")

    @property
    def joint_states(self) -> dict[str, float]:
        """Snapshot of all current joint angles."""
        return dict(self._angles)

    def _log(self, event_type: str, **data: Any) -> None:
        self._events.append({
            "type": event_type,
            "time": time.monotonic() - self._start_time,
            **data,
        })
