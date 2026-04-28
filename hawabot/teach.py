"""Teach-by-demo: record and play back robot motions.

Inspired by the full-scale Hawabot's teach_and_play.py workflow.
On real hardware with smart servos (Core/Pro), this uses compliance mode
(current-based position / Mode 5) so the kid can physically move the joints
while positions are recorded. In mock mode, positions are simulated.

Usage::

    from hawabot import Robot

    robot = Robot()

    # Record a motion
    recording = robot.teach(duration=5.0)   # Records for 5 seconds

    # Play it back
    robot.play(recording)

    # Save / load
    recording.save("my_wave.json")
    loaded = Recording.load("my_wave.json")
    robot.play(loaded)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Frame:
    """A single snapshot of all joint angles at a point in time."""

    timestamp: float  # seconds from start of recording
    angles: dict[str, float]  # joint_name → angle in degrees


@dataclass
class Recording:
    """A sequence of frames captured during teach-by-demo."""

    frames: list[Frame] = field(default_factory=list)
    sample_rate_hz: float = 20.0
    character_name: str = ""
    tier: str = ""

    @property
    def duration(self) -> float:
        if not self.frames:
            return 0.0
        return self.frames[-1].timestamp - self.frames[0].timestamp

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def save(self, path: str | Path) -> None:
        """Save recording to JSON."""
        data = {
            "character_name": self.character_name,
            "tier": self.tier,
            "sample_rate_hz": self.sample_rate_hz,
            "duration_s": self.duration,
            "frame_count": self.frame_count,
            "frames": [
                {"t": round(f.timestamp, 4), "angles": f.angles}
                for f in self.frames
            ],
        }
        path = Path(path)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> Recording:
        """Load a recording from JSON."""
        path = Path(path)
        with open(path) as f:
            data = json.load(f)

        frames = [
            Frame(timestamp=fr["t"], angles=fr["angles"])
            for fr in data["frames"]
        ]
        return cls(
            frames=frames,
            sample_rate_hz=data.get("sample_rate_hz", 20.0),
            character_name=data.get("character_name", ""),
            tier=data.get("tier", ""),
        )


def record(
    driver: Any,
    joint_names: list[str],
    duration: float = 5.0,
    sample_rate_hz: float = 20.0,
    on_frame: Any = None,
) -> Recording:
    """Record joint positions for *duration* seconds.

    On real hardware, the driver should be in compliance mode before calling
    this (servos are back-drivable so the kid can move them by hand).
    In mock mode, we simulate smooth random-ish motion for testing.

    Args:
        driver: The hardware or mock driver.
        joint_names: Which joints to record.
        duration: How long to record in seconds.
        sample_rate_hz: Samples per second.
        on_frame: Optional callback(frame_index, frame) for progress reporting.
    """
    import os

    recording = Recording(sample_rate_hz=sample_rate_hz)
    interval = 1.0 / sample_rate_hz
    num_frames = int(duration * sample_rate_hz)
    is_mock = os.environ.get("HAWABOT_MOCK", "1") == "1"

    start = time.monotonic()

    for i in range(num_frames):
        t = i * interval

        if is_mock:
            # In mock mode, simulate gentle motion for testing
            import math
            angles = {}
            for j, name in enumerate(joint_names):
                base = driver.get_angle(name)
                # Smooth sinusoidal drift at different frequencies per joint
                offset = 15.0 * math.sin(2.0 * math.pi * (0.3 + j * 0.1) * t)
                angles[name] = round(base + offset, 2)
        else:
            # On real hardware, read current servo positions
            angles = {name: driver.get_angle(name) for name in joint_names}

        frame = Frame(timestamp=round(t, 4), angles=angles)
        recording.frames.append(frame)

        if on_frame:
            on_frame(i, frame)

        # In mock mode, don't actually wait (keeps tests fast)
        if not is_mock or os.environ.get("HAWABOT_MOCK_REALTIME") == "1":
            # Sleep until next sample time
            elapsed = time.monotonic() - start
            sleep_until = (i + 1) * interval
            if sleep_until > elapsed:
                time.sleep(sleep_until - elapsed)

    return recording


def playback(
    recording: Recording,
    driver: Any,
    *,
    speed: float = 1.0,
    on_frame: Any = None,
) -> None:
    """Play back a recording by writing joint positions to the driver.

    Uses synchronized writes — all joints in a frame are set before
    advancing to the next frame. This matches the GroupSyncWrite pattern
    from the full-scale Hawabot.

    Args:
        recording: The recording to play.
        driver: The hardware or mock driver.
        speed: Playback speed multiplier (2.0 = double speed).
        on_frame: Optional callback(frame_index, frame) for progress reporting.
    """
    import os

    if not recording.frames:
        return

    is_mock = os.environ.get("HAWABOT_MOCK", "1") == "1"
    start = time.monotonic()

    for i, frame in enumerate(recording.frames):
        # Write all joints simultaneously (synchronized write)
        for joint_name, angle in frame.angles.items():
            try:
                driver.set_angle(joint_name, angle)
            except ValueError:
                pass  # Joint not available on this tier — skip

        if on_frame:
            on_frame(i, frame)

        # Timing
        if i < len(recording.frames) - 1:
            next_t = recording.frames[i + 1].timestamp
            wait_s = (next_t - frame.timestamp) / speed

            if not is_mock or os.environ.get("HAWABOT_MOCK_REALTIME") == "1":
                elapsed = time.monotonic() - start
                target = frame.timestamp / speed
                if target > elapsed:
                    time.sleep(target - elapsed)
            else:
                driver.wait(wait_s)
