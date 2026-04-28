"""Student entry point — the Robot class that ties everything together."""

from __future__ import annotations

import os
from typing import Any

from hawabot.character.animations import get_animation, play_animation
from hawabot.character.profile import CharacterProfile
from hawabot.config.tiers import MOCK_TIER, TierName, get_tier
from hawabot.drivers.base import BaseDriver
from hawabot.drivers.mock import MockDriver
from hawabot.joints.arm import Arms
from hawabot.joints.head import Head
from hawabot.joints.waist import Waist
from hawabot.sim.engine import SimulationEngine
from hawabot.teach import Recording, playback, record


class Robot:
    """The main HawaBot interface.

    Usage::

        from hawabot import Robot

        robot = Robot()              # Auto-detects hardware or uses simulation
        robot.head.pan(45)           # Turn head 45° right
        robot.arm.left.wave()        # Wave left arm
        robot.waist.turn(-30)        # Turn upper body left
        robot.express("happy")       # Play a character expression

        recording = robot.teach(3)   # Record 3 seconds of motion
        robot.play(recording)        # Play it back

        robot.shutdown()             # Return to rest
    """

    def __init__(
        self,
        character_path: str | None = None,
        tier: str | None = None,
        mock: bool | None = None,
    ) -> None:
        # Load character profile
        self._profile = CharacterProfile.load(character_path)

        # Determine if we're in mock/simulation mode
        if mock is None:
            mock = os.environ.get("HAWABOT_MOCK", "1") == "1"

        # Resolve tier
        if mock:
            tier_name = tier or self._profile.tier
            try:
                self._tier = get_tier(tier_name)
            except (ValueError, KeyError):
                self._tier = MOCK_TIER
            self._driver: BaseDriver = MockDriver(self._tier)
        else:
            if tier is None:
                tier = self._profile.tier
            self._tier = get_tier(tier)
            if self._tier.name == TierName.SPARK:
                from hawabot.drivers.pico import PicoDriver
                self._driver = PicoDriver(self._tier)
            else:
                from hawabot.drivers.pi5 import Pi5Driver
                self._driver = Pi5Driver()

        # Build body parts — always available
        self.head = Head(self._driver, self._profile)
        self.arm = Arms(self._driver, self._profile)
        self.waist = Waist(self._driver, self._profile)

        # Legs only on tiers that have them
        self.leg = None
        if self._tier.has_legs:
            from hawabot.joints.leg import Legs
            self.leg = Legs(self._driver, self._profile)

        # Simulation engine (only available in mock mode)
        self._sim: SimulationEngine | None = None
        if isinstance(self._driver, MockDriver):
            self._sim = SimulationEngine(self._driver, self._tier)

    # --- Identity ---

    @property
    def name(self) -> str:
        """The character's name from the profile."""
        return self._profile.name

    @property
    def tier_name(self) -> str:
        return self._tier.display_name

    @property
    def form_factor(self) -> str:
        return self._tier.form_factor.value

    @property
    def dof(self) -> int:
        return len(self._tier.joints)

    @property
    def has_legs(self) -> bool:
        return self._tier.has_legs

    # --- High-level actions ---

    def wave(self) -> None:
        """Wave! Uses the character's wave animation or falls back to left arm."""
        self.arm.left.wave()

    def express(self, emotion: str) -> None:
        """Play a character-specific expression animation.

        Built-in emotions for the default character:
        "happy", "thinking", "greeting", "nod", "shake_head"
        """
        frames = get_animation(self._profile, emotion)
        if frames:
            play_animation(frames, self._driver)

    # --- Teach-by-demo ---

    def teach(
        self,
        duration: float = 5.0,
        sample_rate_hz: float = 20.0,
    ) -> Recording:
        """Record the robot's joint positions for *duration* seconds.

        On real hardware with smart servos (Core/Pro), the servos enter
        compliance mode so you can move them by hand. The positions are
        recorded and can be played back.

        In simulation mode, gentle motion is simulated for testing.

        Args:
            duration: How long to record (seconds).
            sample_rate_hz: Samples per second (default 20 Hz).

        Returns:
            A Recording that can be played back or saved to file.
        """
        joint_names = list(self._tier.joints.keys())
        rec = record(
            self._driver,
            joint_names,
            duration=duration,
            sample_rate_hz=sample_rate_hz,
        )
        rec.character_name = self.name
        rec.tier = self._tier.name.value
        return rec

    def play(self, recording: Recording, speed: float = 1.0) -> None:
        """Play back a recorded motion.

        Args:
            recording: A Recording from teach() or Recording.load().
            speed: Playback speed multiplier (2.0 = double speed).
        """
        playback(recording, self._driver, speed=speed)

    # --- Simulation helpers ---

    def show(self) -> None:
        """Display the robot's current pose (simulation mode only)."""
        if self._sim is None:
            print("show() is only available in simulation mode.")
            return
        from hawabot.sim.visualizer import show
        show(self._sim)

    def status(self) -> str:
        """Return a text summary of all joint angles."""
        if self._sim:
            return self._sim.summary()
        return f"Robot '{self.name}' ({self.tier_name})"

    def print_status(self) -> None:
        """Print the robot's current state."""
        print(f"{self.name} ({self.tier_name} — {self.form_factor})")
        print(self.status())

    def event_log(self) -> list[dict[str, Any]]:
        """Return the driver's event log (for curriculum validation)."""
        return self._driver.get_event_log()

    # --- Lifecycle ---

    def shutdown(self) -> None:
        """Return all joints to rest position."""
        frames = get_animation(self._profile, "rest")
        if frames:
            play_animation(frames, self._driver)
        else:
            self._driver.shutdown()

    def __repr__(self) -> str:
        return (
            f"Robot(name={self.name!r}, tier={self.tier_name!r}, "
            f"form={self.form_factor!r}, dof={self.dof})"
        )
