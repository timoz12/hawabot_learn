"""Spark skeleton frame — dimensions, positions, and magnet grid.

Central reference module for the 200mm Spark humanoid skeleton.
All pipeline modules import from here rather than hardcoding dimensions.

This module defines the skeleton as a MECHANICAL FRAME — not a subtract
volume. The frame has servo positions, magnet seats, clearance envelopes,
and cut plane defaults. Shell pipeline modules use these to validate and
process character shells.

Coordinate system: Z-up, origin at center of base plate top surface.
+X right (robot's perspective), +Y forward.
All dimensions in millimeters.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ── Servo Dimensions ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class ServoSpec:
    """Physical dimensions of a servo motor."""
    name: str
    body_l: float     # Front-back
    body_w: float     # Side-side
    body_h: float     # Bottom to case top
    total_h: float    # Bottom to spline top
    tab_l: float      # Tab-to-tab length
    tab_t: float      # Tab thickness
    tab_z: float      # Tab underside height from bottom
    spline_od: float  # Output spline outer diameter
    weight_g: float   # Weight in grams


SG90 = ServoSpec(
    name="SG90",
    body_l=22.7, body_w=12.2, body_h=27.0, total_h=32.3,
    tab_l=32.3, tab_t=2.8, tab_z=17.0,
    spline_od=4.8, weight_g=9.0,
)

MG90S = ServoSpec(
    name="MG90S",
    body_l=22.8, body_w=12.4, body_h=28.4, total_h=32.5,
    tab_l=32.1, tab_t=2.8, tab_z=18.5,
    spline_od=4.8, weight_g=13.4,
)


# ── Global Tolerances ─────────────────────────────────────────────────────

C_WALL = 0.3         # Servo-to-pocket clearance per side
T_WALL = 2.5         # Minimum structural wall thickness
D_WIRE = 6.0         # Wire channel diameter
D_SCREW = 2.0        # M2 screw pilot hole diameter
SHELL_MIN_WALL = 2.0 # Minimum shell wall thickness


# ── Frame Dimensions (200mm Spark Humanoid) ───────────────────────────────

# Base plate
BASE_W = 90.0
BASE_D = 70.0
BASE_H = 20.0
BASE_R = 6.0

# Torso column
TORSO_D = 24.0
TORSO_R = 4.0   # Corner fillet radius

# Total skeleton height (base bottom to tilt servo top)
TOTAL_HEIGHT = 200.0


# ── Servo Positions ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class ServoMount:
    """A servo mounted at a specific position and orientation."""
    name: str
    servo: ServoSpec
    x: float
    y: float
    z: float           # Z of servo bottom edge
    shaft_axis: str    # "Z", "Y", or "X"
    shaft_sign: int    # +1 or -1 along the shaft axis
    joint_name: str
    joint_range_deg: tuple[float, float]  # (min, max) degrees


SERVO_MOUNTS = [
    ServoMount("waist", SG90, 0, 0, 10,
               shaft_axis="Z", shaft_sign=1,
               joint_name="waist_yaw", joint_range_deg=(-90, 90)),

    ServoMount("left_shoulder", MG90S, -40, 0, 110,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_shoulder_pitch", joint_range_deg=(-90, 90)),

    ServoMount("right_shoulder", MG90S, 40, 0, 110,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_shoulder_pitch", joint_range_deg=(-90, 90)),

    ServoMount("head_pan", SG90, 0, 0, 120,
               shaft_axis="Z", shaft_sign=1,
               joint_name="head_pan_yaw", joint_range_deg=(-90, 90)),

    ServoMount("head_tilt", SG90, 0, 0, 148,
               shaft_axis="Y", shaft_sign=1,
               joint_name="head_tilt_pitch", joint_range_deg=(-30, 30)),
]

# Convenience lookups
WAIST_Z = 10.0
SHOULDER_Z = 110.0
SHOULDER_X = 40.0
HEAD_PAN_Z = 120.0
HEAD_TILT_Z = 148.0


# ── Magnet Positions ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class MagnetSeat:
    """A magnet pocket position on the skeleton frame."""
    id: str
    zone: str       # "head", "torso", "left_arm", "right_arm", "base"
    x: float
    y: float
    z: float
    normal: tuple[float, float, float]  # Outward-facing direction


MAG_D = 6.0       # Magnet diameter
MAG_H = 3.0       # Magnet height
MAG_POCKET_D = 6.1 # Press-fit pocket diameter
MAG_POCKET_H = 3.1 # Pocket depth

MAGNET_SEATS: list[MagnetSeat] = [
    # ── Head zone (8) — ring at Z=125 ──
    MagnetSeat("H1", "head", 0, -14, 125, (0, -1, 0)),
    MagnetSeat("H2", "head", 0, 14, 125, (0, 1, 0)),
    MagnetSeat("H3", "head", -14, 0, 125, (-1, 0, 0)),
    MagnetSeat("H4", "head", 14, 0, 125, (1, 0, 0)),
    MagnetSeat("H5", "head", -10, -10, 125, (-1, -1, 0)),
    MagnetSeat("H6", "head", 10, -10, 125, (1, -1, 0)),
    MagnetSeat("H7", "head", -10, 10, 125, (-1, 1, 0)),
    MagnetSeat("H8", "head", 10, 10, 125, (1, 1, 0)),

    # ── Torso zone (12) — 3 rings of 4 ──
    MagnetSeat("T1", "torso", 0, -14, 30, (0, -1, 0)),
    MagnetSeat("T2", "torso", 0, 14, 30, (0, 1, 0)),
    MagnetSeat("T3", "torso", 0, -14, 70, (0, -1, 0)),
    MagnetSeat("T4", "torso", 0, 14, 70, (0, 1, 0)),
    MagnetSeat("T5", "torso", 0, -14, 100, (0, -1, 0)),
    MagnetSeat("T6", "torso", 0, 14, 100, (0, 1, 0)),
    MagnetSeat("T7", "torso", -14, 0, 30, (-1, 0, 0)),
    MagnetSeat("T8", "torso", 14, 0, 30, (1, 0, 0)),
    MagnetSeat("T9", "torso", -14, 0, 70, (-1, 0, 0)),
    MagnetSeat("T10", "torso", 14, 0, 70, (1, 0, 0)),
    MagnetSeat("T11", "torso", -14, 0, 100, (-1, 0, 0)),
    MagnetSeat("T12", "torso", 14, 0, 100, (1, 0, 0)),

    # ── Left arm zone (6) ──
    MagnetSeat("LA1", "left_arm", -40, -10, 110, (0, -1, 0)),
    MagnetSeat("LA2", "left_arm", -40, 10, 110, (0, 1, 0)),
    MagnetSeat("LA3", "left_arm", -40, 0, 100, (0, 0, -1)),
    MagnetSeat("LA4", "left_arm", -40, 0, 120, (0, 0, 1)),
    MagnetSeat("LA5", "left_arm", -52, -8, 110, (-1, 0, 0)),
    MagnetSeat("LA6", "left_arm", -52, 8, 110, (-1, 0, 0)),

    # ── Right arm zone (6) — mirror of left ──
    MagnetSeat("RA1", "right_arm", 40, -10, 110, (0, -1, 0)),
    MagnetSeat("RA2", "right_arm", 40, 10, 110, (0, 1, 0)),
    MagnetSeat("RA3", "right_arm", 40, 0, 100, (0, 0, -1)),
    MagnetSeat("RA4", "right_arm", 40, 0, 120, (0, 0, 1)),
    MagnetSeat("RA5", "right_arm", 52, -8, 110, (1, 0, 0)),
    MagnetSeat("RA6", "right_arm", 52, 8, 110, (1, 0, 0)),

    # ── Base zone (8) — perimeter at Z=-10 ──
    MagnetSeat("B1", "base", -35, -28, -10, (0, -1, 0)),
    MagnetSeat("B2", "base", 35, -28, -10, (0, -1, 0)),
    MagnetSeat("B3", "base", -35, 28, -10, (0, 1, 0)),
    MagnetSeat("B4", "base", 35, 28, -10, (0, 1, 0)),
    MagnetSeat("B5", "base", 0, -28, -10, (0, -1, 0)),
    MagnetSeat("B6", "base", 0, 28, -10, (0, 1, 0)),
    MagnetSeat("B7", "base", -40, 0, -10, (-1, 0, 0)),
    MagnetSeat("B8", "base", 40, 0, -10, (1, 0, 0)),
]


def magnets_for_zone(zone: str) -> list[MagnetSeat]:
    """Return all magnet seats for a given body zone."""
    return [m for m in MAGNET_SEATS if m.zone == zone]


# ── Cut Plane Defaults ────────────────────────────────────────────────────

@dataclass
class CutPlane:
    """A default cut plane for dissecting a character into body zones."""
    name: str
    axis: str           # "Z" for horizontal, "X" for vertical
    position: float     # Default position along the axis
    min_pos: float      # Minimum adjustable position
    max_pos: float      # Maximum adjustable position
    zones: tuple[str, str]  # (zone_above/right, zone_below/left)


DEFAULT_CUT_PLANES = [
    CutPlane("head_torso", "Z", 115, 105, 130, ("head", "torso")),
    CutPlane("torso_base", "Z", 10, 0, 20, ("torso", "base")),
    CutPlane("left_arm", "X", -28, -35, -24, ("torso", "left_arm")),
    CutPlane("right_arm", "X", 28, 24, 35, ("torso", "right_arm")),
]

BODY_ZONES = ["head", "torso", "left_arm", "right_arm", "base"]


# ── Clearance Envelopes ──────────────────────────────────────────────────

@dataclass(frozen=True)
class ClearanceEnvelope:
    """Minimum clearance a shell must maintain from the skeleton."""
    zone: str
    min_gap_from_frame: float    # mm, radial clearance from frame surface
    min_inner_radius: float      # mm, at the attachment opening (0 = N/A)
    min_opening_diameter: float  # mm, shell must fit over this
    max_shell_weight_g: float    # grams, servo torque limit


CLEARANCE_ENVELOPES = [
    ClearanceEnvelope("head", 2.0, 18.0, 36.0, 30.0),
    ClearanceEnvelope("torso", 3.0, 0.0, 0.0, 50.0),
    ClearanceEnvelope("left_arm", 2.0, 20.0, 0.0, 15.0),
    ClearanceEnvelope("right_arm", 2.0, 20.0, 0.0, 15.0),
    ClearanceEnvelope("base", 2.0, 0.0, 0.0, 100.0),
]


def envelope_for_zone(zone: str) -> ClearanceEnvelope:
    """Return clearance envelope for a given zone."""
    for env in CLEARANCE_ENVELOPES:
        if env.zone == zone:
            return env
    raise ValueError(f"Unknown zone: {zone}")


# ── Magnet Selection Constraints ──────────────────────────────────────────

MAGNET_MIN_COUNT = {
    "head": 3,
    "torso": 4,
    "left_arm": 2,
    "right_arm": 2,
    "base": 3,
}

MAGNET_MAX_COUNT = {
    "head": 8,
    "torso": 12,
    "left_arm": 6,
    "right_arm": 6,
    "base": 8,
}

MAGNET_PULL_FORCE_KG = 0.5  # Per 6×3mm neodymium disc magnet
MAGNET_BOSS_OD = 10.0       # Shell-side boss outer diameter
MAGNET_BOSS_H = 4.0         # Shell-side boss height
MIN_WALL_BEHIND_BOSS = 1.5  # Don't punch through shell
MIN_SHELL_THICKNESS_FOR_BOSS = 6.0  # Boss needs 4mm + 2mm wall behind
