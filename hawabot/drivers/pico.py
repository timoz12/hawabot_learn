"""Pi Pico W driver — controls SG90/MG90S PWM servos via USB serial.

Architecture
------------
Host (laptop / Pi)                     Pi Pico W (MicroPython)
  PicoDriver  ── USB serial ──►  main.py (firmware)
               ◄── responses ──         │
                                        ├─ GP0  → waist_yaw servo
                                        ├─ GP1  → left_shoulder_pitch servo
                                        ├─ GP2  → right_shoulder_pitch servo
                                        ├─ GP3  → head_pan servo
                                        └─ GP4  → head_tilt servo

Protocol (newline-terminated text, 115200 baud):
  Host → Pico:   S <pin> <pulse_us>     Set servo PWM
  Pico → Host:   OK
  Host → Pico:   V                       Read supply voltage (via ADC)
  Pico → Host:   V <float>              (or V NONE if not wired)
  Host → Pico:   P                       Ping
  Pico → Host:   PONG
"""

from __future__ import annotations

import time
from typing import Any

import serial  # pyserial

from hawabot.config.tiers import TierDefinition
from hawabot.drivers.base import BaseDriver

# Default GPIO pin assignments for the Spark tier (5 DOF).
# These match the firmware's default wiring — override via pin_map if needed.
DEFAULT_PIN_MAP: dict[str, int] = {
    "waist_yaw": 0,
    "left_shoulder_pitch": 1,
    "right_shoulder_pitch": 2,
    "head_pan": 3,
    "head_tilt": 4,
}

# Servo PWM calibration.  Hobby servos accept 500-2500 µs pulses.
# Centre (0 deg) = 1500 µs.  ±90 deg maps linearly to ±1000 µs.
_PULSE_CENTER_US = 1500
_PULSE_RANGE_US = 1000  # ±1000 µs for ±90 deg
_ANGLE_RANGE_DEG = 90.0


def _angle_to_pulse(angle: float) -> int:
    """Convert angle (degrees, 0 = centre) to PWM pulse width (µs)."""
    us = _PULSE_CENTER_US + (angle / _ANGLE_RANGE_DEG) * _PULSE_RANGE_US
    return int(max(500, min(2500, us)))


class PicoDriver(BaseDriver):
    """Controls SG90/MG90S servos via a Raspberry Pi Pico W over USB serial.

    The Pico W runs the companion MicroPython firmware
    (``firmware/pico_w/main.py``) which receives simple text commands
    and drives PWM outputs on the configured GPIO pins.

    Parameters
    ----------
    tier : TierDefinition
        Hardware tier spec (used for joint name validation and angle limits).
    port : str
        Serial port path (e.g. ``/dev/ttyACM0`` on Linux,
        ``/dev/cu.usbmodem*`` on macOS, ``COM3`` on Windows).
    baudrate : int
        Serial baud rate — must match the firmware (default 115200).
    pin_map : dict[str, int] | None
        Joint-name → GPIO-pin mapping.  Defaults to ``DEFAULT_PIN_MAP``.
    timeout : float
        Serial read timeout in seconds.
    """

    def __init__(
        self,
        tier: TierDefinition,
        port: str = "/dev/ttyACM0",
        baudrate: int = 115_200,
        pin_map: dict[str, int] | None = None,
        timeout: float = 1.0,
    ) -> None:
        self._tier = tier
        self._pin_map = dict(pin_map or DEFAULT_PIN_MAP)
        self._events: list[dict[str, Any]] = []
        self._start_time = time.monotonic()

        # Track angles locally — SG90/MG90S have no position feedback.
        self._angles: dict[str, float] = {
            name: spec.default_angle for name, spec in tier.joints.items()
        }

        # Open serial connection to the Pico W.
        self._serial = serial.Serial(port, baudrate, timeout=timeout)
        # Wait for the Pico to reset after USB connection.
        time.sleep(0.5)
        self._serial.reset_input_buffer()

        # Verify the firmware is responding.
        self._send("P")
        resp = self._recv()
        if resp != "PONG":
            self._serial.close()
            raise ConnectionError(
                f"Pico W did not respond to ping on {port} "
                f"(got {resp!r}).  Is the firmware running?"
            )

        # Drive all servos to their default (rest) positions.
        for name, spec in tier.joints.items():
            self._set_servo(name, spec.default_angle)

        self._log("connected", port=port, baudrate=baudrate)

    # ------------------------------------------------------------------
    # BaseDriver interface
    # ------------------------------------------------------------------

    def set_angle(self, joint_name: str, angle: float) -> None:
        spec = self._tier.joints.get(joint_name)
        if spec is None:
            available = ", ".join(sorted(self._tier.joints))
            raise ValueError(
                f"Joint '{joint_name}' not found in tier "
                f"'{self._tier.display_name}'.  "
                f"Available joints: {available}"
            )

        clamped = max(spec.min_angle, min(spec.max_angle, angle))
        old_angle = self._angles[joint_name]
        self._set_servo(joint_name, clamped)
        self._angles[joint_name] = clamped

        self._log(
            "set_angle",
            joint=joint_name,
            from_angle=old_angle,
            to_angle=clamped,
            requested=angle,
            clamped=clamped != angle,
        )

    def get_angle(self, joint_name: str) -> float:
        if joint_name not in self._angles:
            raise ValueError(f"Joint '{joint_name}' not found")
        return self._angles[joint_name]

    def get_temperature(self, joint_name: str) -> float | None:
        # SG90 / MG90S servos have no temperature sensor.
        return None

    def get_voltage(self) -> float | None:
        self._send("V")
        resp = self._recv()
        if resp and resp.startswith("V "):
            value = resp[2:]
            if value == "NONE":
                return None
            return float(value)
        return None

    def wait(self, seconds: float) -> None:
        self._log("wait", duration_s=seconds)
        time.sleep(seconds)

    def get_event_log(self) -> list[dict]:
        return list(self._events)

    def shutdown(self) -> None:
        for name, spec in self._tier.joints.items():
            self._set_servo(name, spec.default_angle)
            self._angles[name] = spec.default_angle
        self._log("shutdown")
        self._serial.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_servo(self, joint_name: str, angle: float) -> None:
        """Send a servo command to the Pico W."""
        pin = self._pin_map.get(joint_name)
        if pin is None:
            raise ValueError(
                f"No GPIO pin mapped for joint '{joint_name}'.  "
                f"Check pin_map — mapped joints: "
                f"{', '.join(sorted(self._pin_map))}"
            )
        pulse_us = _angle_to_pulse(angle)
        self._send(f"S {pin} {pulse_us}")
        resp = self._recv()
        if resp != "OK":
            raise RuntimeError(
                f"Servo command failed for {joint_name} "
                f"(pin {pin}, {pulse_us} µs): {resp!r}"
            )

    def _send(self, cmd: str) -> None:
        """Send a newline-terminated command."""
        self._serial.write(f"{cmd}\n".encode())
        self._serial.flush()

    def _recv(self) -> str:
        """Read one newline-terminated response."""
        line = self._serial.readline()
        return line.decode().strip()

    def _log(self, event_type: str, **data: Any) -> None:
        self._events.append({
            "type": event_type,
            "time": time.monotonic() - self._start_time,
            **data,
        })
