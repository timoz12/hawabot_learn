"""Event logger for curriculum validation and debugging."""

from __future__ import annotations

from typing import Any


class EventLogger:
    """Records robot events for curriculum mission validation.

    The curriculum validator checks this log to determine if a student's
    code achieved the mission's success criteria (e.g., "head_pan was moved").
    """

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def log(self, event_type: str, **data: Any) -> None:
        self._events.append({"type": event_type, **data})

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)

    def joints_moved(self) -> set[str]:
        """Return the set of joint names that received a set_angle command."""
        return {
            e["joint"]
            for e in self._events
            if e["type"] == "set_angle" and e.get("from_angle") != e.get("to_angle")
        }

    def was_joint_moved(self, joint_name: str) -> bool:
        return joint_name in self.joints_moved()

    def clear(self) -> None:
        self._events.clear()
