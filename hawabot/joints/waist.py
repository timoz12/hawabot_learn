"""Waist body part — yaw rotation of the upper body."""

from __future__ import annotations

from hawabot.character.profile import CharacterProfile
from hawabot.drivers.base import BaseDriver
from hawabot.joints.base import BodyPart, Joint


class Waist(BodyPart):
    """Controls the waist: yaw rotation of the upper body on its base."""

    def __init__(self, driver: BaseDriver, profile: CharacterProfile) -> None:
        joints: dict[str, Joint] = {}
        for name in ("waist_yaw",):
            try:
                driver.get_angle(name)
                joints[name] = Joint(name, driver)
            except (ValueError, KeyError):
                pass
        super().__init__(joints, driver)
        self._profile = profile

    def turn(self, degrees: float) -> None:
        """Turn upper body left (negative) or right (positive)."""
        if self._has("waist_yaw"):
            self._get("waist_yaw").set_angle(degrees)

    @property
    def angle(self) -> float:
        if self._has("waist_yaw"):
            return self._get("waist_yaw").angle
        return 0.0
