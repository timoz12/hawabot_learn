"""Abstract base driver — the contract every hardware driver must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseDriver(ABC):
    """Interface between the SDK's joint system and physical (or simulated) hardware."""

    @abstractmethod
    def set_angle(self, joint_name: str, angle: float) -> None:
        """Command a joint to move to *angle* degrees."""

    @abstractmethod
    def get_angle(self, joint_name: str) -> float:
        """Return the current angle (degrees) of a joint."""

    @abstractmethod
    def get_temperature(self, joint_name: str) -> float | None:
        """Return actuator temperature in °C, or None if unsupported."""

    @abstractmethod
    def get_voltage(self) -> float | None:
        """Return supply voltage, or None if unsupported."""

    @abstractmethod
    def wait(self, seconds: float) -> None:
        """Block for *seconds* (used for animation timing)."""

    @abstractmethod
    def get_event_log(self) -> list[dict]:
        """Return the ordered list of events recorded by this driver."""

    def shutdown(self) -> None:
        """Return all joints to rest position and release resources."""
