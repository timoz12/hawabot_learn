"""Animation playback utilities for character-defined animation sequences."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hawabot.character.profile import CharacterProfile, Keyframe
    from hawabot.drivers.base import BaseDriver


def play_animation(
    keyframes: list[Keyframe],
    driver: BaseDriver,
    *,
    speed_factor: float = 1.0,
) -> None:
    """Play a sequence of keyframes on the given driver.

    Each keyframe specifies target joint angles and a duration.
    The driver moves joints to the target positions, then waits
    for the specified duration before advancing to the next frame.
    """
    for kf in keyframes:
        for joint_name, angle in kf.joints.items():
            driver.set_angle(joint_name, angle)

        wait_sec = (kf.duration_ms / 1000.0) / speed_factor
        driver.wait(wait_sec)


def get_animation(
    profile: CharacterProfile,
    name: str,
) -> list[Keyframe] | None:
    """Look up a named animation from the character profile."""
    return profile.animations.get(name)
