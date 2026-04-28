"""Head body part — pan, tilt, nod, shake."""

from __future__ import annotations

from hawabot.character.animations import get_animation, play_animation
from hawabot.character.profile import CharacterProfile
from hawabot.drivers.base import BaseDriver
from hawabot.joints.base import BodyPart, Joint


class Head(BodyPart):
    """Controls the robot's head: pan (left/right) and tilt (up/down)."""

    def __init__(self, driver: BaseDriver, profile: CharacterProfile) -> None:
        joints: dict[str, Joint] = {}
        for name in ("head_pan", "head_tilt", "neck_roll"):
            try:
                driver.get_angle(name)
                joints[name] = Joint(name, driver)
            except (ValueError, KeyError):
                pass
        super().__init__(joints, driver)
        self._profile = profile

    def pan(self, degrees: float) -> None:
        """Turn head left (negative) or right (positive)."""
        if self._has("head_pan"):
            self._get("head_pan").set_angle(degrees)

    def tilt(self, degrees: float) -> None:
        """Tilt head up (negative) or down (positive)."""
        if self._has("head_tilt"):
            self._get("head_tilt").set_angle(degrees)

    def nod(self) -> None:
        """Play the nod animation."""
        frames = get_animation(self._profile, "nod")
        if frames:
            play_animation(frames, self._driver)
        else:
            self.tilt(-15)
            self._driver.wait(0.2)
            self.tilt(0)
            self._driver.wait(0.2)
            self.tilt(-15)
            self._driver.wait(0.2)
            self.tilt(0)

    def shake(self) -> None:
        """Play the shake-head animation."""
        frames = get_animation(self._profile, "shake_head")
        if frames:
            play_animation(frames, self._driver)
        else:
            self.pan(-30)
            self._driver.wait(0.2)
            self.pan(30)
            self._driver.wait(0.3)
            self.pan(-30)
            self._driver.wait(0.3)
            self.pan(0)
