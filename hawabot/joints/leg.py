"""Leg body part — basic leg control and walking stubs."""

from __future__ import annotations

from hawabot.character.profile import CharacterProfile
from hawabot.drivers.base import BaseDriver
from hawabot.joints.base import BodyPart, Joint


class Leg(BodyPart):
    """Controls one leg (left or right): hip, knee, ankle."""

    def __init__(
        self, side: str, driver: BaseDriver, profile: CharacterProfile
    ) -> None:
        self.side = side
        prefix = f"{side}_"

        joints: dict[str, Joint] = {}
        for name in (
            f"{prefix}hip_yaw",
            f"{prefix}hip_roll",
            f"{prefix}hip_pitch",
            f"{prefix}knee",
            f"{prefix}ankle",
            f"{prefix}ankle_pitch",
            f"{prefix}ankle_roll",
        ):
            try:
                driver.get_angle(name)
                joints[name] = Joint(name, driver)
            except (ValueError, KeyError):
                pass

        super().__init__(joints, driver)
        self._profile = profile
        self._prefix = prefix

    def set_hip(self, degrees: float) -> None:
        """Set hip pitch angle."""
        hip = f"{self._prefix}hip_pitch"
        if self._has(hip):
            self._get(hip).set_angle(degrees)

    def set_knee(self, degrees: float) -> None:
        """Set knee angle."""
        knee = f"{self._prefix}knee"
        if self._has(knee):
            self._get(knee).set_angle(degrees)


class Legs:
    """Container for left and right legs."""

    def __init__(self, driver: BaseDriver, profile: CharacterProfile) -> None:
        self.left = Leg("left", driver, profile)
        self.right = Leg("right", driver, profile)
