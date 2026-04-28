"""Pi Pico W driver stub — Spark tier hardware (not yet implemented)."""

from hawabot.drivers.base import BaseDriver


class PicoDriver(BaseDriver):
    """Controls SG90/MG90S servos via a Raspberry Pi Pico W over WiFi.

    This is a stub. Implementation will use MicroPython on the Pico W
    with PWM servo control, communicating with the host over WiFi/HTTP.
    """

    def __init__(self, host: str = "hawabot.local", port: int = 8080):
        raise NotImplementedError(
            "PicoDriver is not yet implemented. "
            "Use HAWABOT_MOCK=1 or Robot(mock=True) for simulation mode."
        )

    def set_angle(self, joint_name: str, angle: float) -> None: ...
    def get_angle(self, joint_name: str) -> float: ...
    def get_temperature(self, joint_name: str) -> float | None: ...
    def get_voltage(self) -> float | None: ...
    def wait(self, seconds: float) -> None: ...
    def get_event_log(self) -> list[dict]: ...
