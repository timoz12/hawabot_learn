"""Raspberry Pi 5 driver stub — Core and Pro tier hardware (not yet implemented)."""

from hawabot.drivers.base import BaseDriver


class Pi5Driver(BaseDriver):
    """Controls serial bus servos (STS3215 / Dynamixel) via Raspberry Pi 5.

    This is a stub. Implementation will use GPIO + serial protocols
    (Feetech SCS for Core, Dynamixel Protocol 2.0 for Pro).
    """

    def __init__(self, port: str = "/dev/ttyUSB0"):
        raise NotImplementedError(
            "Pi5Driver is not yet implemented. "
            "Use HAWABOT_MOCK=1 or Robot(mock=True) for simulation mode."
        )

    def set_angle(self, joint_name: str, angle: float) -> None: ...
    def get_angle(self, joint_name: str) -> float: ...
    def get_temperature(self, joint_name: str) -> float | None: ...
    def get_voltage(self) -> float | None: ...
    def wait(self, seconds: float) -> None: ...
    def get_event_log(self) -> list[dict]: ...
