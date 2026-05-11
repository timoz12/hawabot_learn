"""Raspberry Pi 5 driver stub — Pro tier only (future 400-500mm walking humanoid).

NOTE: This driver is NOT used for Spark or Core tiers. Those use ESP32-S3
with WiFi (see esp32.py when available). This stub exists for the future Pro
tier, which is a separate, larger robot with on-board Pi 5/CM5 compute and
Dynamixel XL330 serial bus servos.
"""

from hawabot.drivers.base import BaseDriver


class Pi5Driver(BaseDriver):
    """Controls Dynamixel servos via Raspberry Pi 5 — Pro tier only (future).

    This is a stub for the future Pro tier (400-500mm walking humanoid).
    Not used in Spark (7 DOF) or Core (11 DOF) — those use ESP32-S3.
    """

    def __init__(self, port: str = "/dev/ttyUSB0"):
        raise NotImplementedError(
            "Pi5Driver is not yet implemented. Pro tier is a future product. "
            "Use HAWABOT_MOCK=1 or Robot(mock=True) for simulation mode."
        )

    def set_angle(self, joint_name: str, angle: float) -> None: ...
    def get_angle(self, joint_name: str) -> float: ...
    def get_temperature(self, joint_name: str) -> float | None: ...
    def get_voltage(self) -> float | None: ...
    def wait(self, seconds: float) -> None: ...
    def get_event_log(self) -> list[dict]: ...
