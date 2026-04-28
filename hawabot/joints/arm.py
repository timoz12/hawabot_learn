"""Arm body part — wave, reach, and raw joint control."""

from __future__ import annotations

from hawabot.character.animations import get_animation, play_animation
from hawabot.character.profile import CharacterProfile
from hawabot.drivers.base import BaseDriver
from hawabot.joints.base import BodyPart, Joint


class Arm(BodyPart):
    """Controls one arm (left or right): shoulder, elbow, wrist, rotation."""

    def __init__(
        self, side: str, driver: BaseDriver, profile: CharacterProfile
    ) -> None:
        self.side = side  # "left" or "right"
        prefix = f"{side}_"

        joints: dict[str, Joint] = {}
        for name in (
            f"{prefix}shoulder_pitch",
            f"{prefix}shoulder_roll",
            f"{prefix}elbow",
            f"{prefix}wrist",
            f"{prefix}arm_rotation",
        ):
            try:
                driver.get_angle(name)
                joints[name] = Joint(name, driver)
            except (ValueError, KeyError):
                pass

        super().__init__(joints, driver)
        self._profile = profile
        self._prefix = prefix

    def wave(self) -> None:
        """Play the wave animation."""
        frames = get_animation(self._profile, "wave")
        if frames:
            play_animation(frames, self._driver)
        else:
            # Fallback wave using this arm's shoulder
            pitch = f"{self._prefix}shoulder_pitch"
            if self._has(pitch):
                self._get(pitch).set_angle(-90)
                self._driver.wait(0.3)
                self._get(pitch).set_angle(-45)
                self._driver.wait(0.2)
                self._get(pitch).set_angle(-90)
                self._driver.wait(0.2)
                self._get(pitch).set_angle(-45)
                self._driver.wait(0.2)
                self._get(pitch).set_angle(0)

    def reach(self, degrees: float = 90) -> None:
        """Raise the arm forward by *degrees*."""
        pitch = f"{self._prefix}shoulder_pitch"
        if self._has(pitch):
            self._get(pitch).set_angle(-degrees)

    def set_shoulder_pitch(self, degrees: float) -> None:
        pitch = f"{self._prefix}shoulder_pitch"
        if self._has(pitch):
            self._get(pitch).set_angle(degrees)

    def set_shoulder_roll(self, degrees: float) -> None:
        roll = f"{self._prefix}shoulder_roll"
        if self._has(roll):
            self._get(roll).set_angle(degrees)

    def set_elbow(self, degrees: float) -> None:
        elbow = f"{self._prefix}elbow"
        if self._has(elbow):
            self._get(elbow).set_angle(degrees)


class Arms:
    """Container for left and right arms."""

    def __init__(self, driver: BaseDriver, profile: CharacterProfile) -> None:
        self.left = Arm("left", driver, profile)
        self.right = Arm("right", driver, profile)
