"""Base classes for the joint / body-part system."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hawabot.drivers.base import BaseDriver


class Joint:
    """A single controllable joint (e.g. head_pan, left_elbow)."""

    def __init__(self, name: str, driver: BaseDriver) -> None:
        self.name = name
        self._driver = driver

    @property
    def angle(self) -> float:
        return self._driver.get_angle(self.name)

    def set_angle(self, degrees: float) -> None:
        """Move this joint to *degrees*."""
        self._driver.set_angle(self.name, degrees)

    @property
    def temperature(self) -> float | None:
        return self._driver.get_temperature(self.name)

    def __repr__(self) -> str:
        return f"Joint({self.name!r}, angle={self.angle:.1f}°)"


class BodyPart:
    """A group of related joints (e.g. Head = pan + tilt)."""

    def __init__(self, joints: dict[str, Joint], driver: BaseDriver) -> None:
        self._joints = joints
        self._driver = driver

    def _has(self, joint_name: str) -> bool:
        return joint_name in self._joints

    def _get(self, joint_name: str) -> Joint:
        return self._joints[joint_name]

    def rest(self) -> None:
        """Return all joints in this body part to 0°."""
        for joint in self._joints.values():
            joint.set_angle(0.0)
