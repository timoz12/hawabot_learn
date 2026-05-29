"""250mm Pro skeleton frame — dimensions, positions, and magnet grid.

Central reference module for the 250mm humanoid skeleton (v17 geometry).
All pipeline modules import from here rather than hardcoding dimensions.

This module defines the skeleton as a MECHANICAL FRAME — not a subtract
volume. The frame has servo positions, magnet seats, clearance envelopes,
and cut plane defaults. Shell pipeline modules use these to validate and
process character shells.

Spark and Pro share this 250mm skeleton — Spark is a subset (7 DOF,
no legs). The pipeline uses Pro geometry for all calculations; Spark
simply ignores leg zones.

Coordinate system: Z-up, origin at center of base plate top surface.
+X right (robot's perspective), +Y forward.
All dimensions in millimeters.

STEP v1 key coordinates (SolidWorks Y-up → Pipeline Z-up):
  Head top:      Z = 165      Hip:        Z = 0, X = ±20
  Head pan:      Z = 155      Frame bottom: Z = 12
  Shoulder MG90: X = ±74      Knee:       Z = -55 (Pro, future)
  Elbow SG90:    X = ±107     Ankle:      Z = -110 (Pro, future)
  Forearm SG90:  X = ±164     Waist MG90: Z = 15
  Shoulder Z:    140 (all arm components horizontal at this height)
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

XL330 = ServoSpec(
    name="XL330-M288-T",
    body_l=26.0, body_w=20.0, body_h=34.0, total_h=34.0,
    tab_l=20.0, tab_t=0.0, tab_z=0.0,  # No tabs — M2 bolt mounting
    spline_od=8.0, weight_g=18.0,       # 20-tooth cross horn
)

# Convenience aliases for importers
SERVO_SG90 = SG90
SERVO_MG90S = MG90S
SERVO_XL330 = XL330


# ── Global Tolerances ─────────────────────────────────────────────────────

C_WALL = 0.3         # Servo-to-pocket clearance per side (SG90/MG90S)
C_WALL_XL = 0.5      # Servo-to-pocket clearance per side (XL330, tighter housing)
T_WALL = 2.5         # Minimum structural wall thickness
D_WIRE = 6.0         # Wire channel diameter
D_WIRE_XL = 8.0      # XL330 daisy-chain cable channel diameter
D_SCREW = 2.0        # M2 screw pilot hole diameter
SHELL_MIN_WALL = 2.0 # Minimum shell wall thickness


# ── Frame Dimensions (250mm Pro Humanoid, v17) ───────────────────────────

# Base plate (Spark: flat base, Pro: removed when legs added)
BASE_W = 90.0
BASE_D = 70.0
BASE_H = 20.0
BASE_R = 6.0

# Torso column
TORSO_D = 24.0
TORSO_R = 4.0   # Corner fillet radius

# Total skeleton height for shell scaling
# This is the shell target height (foot bottom to head top = 325mm,
# but shells only cover the visible portion — head top to base bottom)
TOTAL_HEIGHT = 250.0

# Segment lengths (verified against STEP v1 mockup)
TORSO_GAP = 128.0    # Frame chest bottom (Z=12) to shoulder (Z=140)
UPPER_ARM = 33.0     # Shoulder (X=74) to elbow (X=107) — horizontal
FOREARM = 57.0        # Elbow (X=107) to hand (X=164) — horizontal
THIGH = 55.0          # Hip to knee (Pro, future)
SHIN = 55.0           # Knee to ankle (Pro, future)
FOOT_H = 5.0          # Ankle to foot bottom (Pro, future)

# Convenience aliases for importers that reference older names
TORSO_HEIGHT = TORSO_GAP
BASE_HEIGHT = BASE_H


# ── Servo Positions (v17 geometry) ────────────────────────────────────────

@dataclass(frozen=True)
class ServoMount:
    """A servo mounted at a specific position and orientation."""
    name: str
    servo: ServoSpec
    x: float
    y: float
    z: float           # Z of servo center / joint axis
    shaft_axis: str    # "Z", "Y", or "X"
    shaft_sign: int    # +1 or -1 along the shaft axis
    joint_name: str
    joint_range_deg: tuple[float, float]  # (min, max) degrees
    tier: str          # "spark" = both tiers, "pro" = Pro only


SERVO_MOUNTS = [
    # ── Head (both tiers) ──
    ServoMount("head_pan", SG90, 0, 0, 155,
               shaft_axis="Z", shaft_sign=1,
               joint_name="head_pan", joint_range_deg=(-90, 90),
               tier="spark"),

    ServoMount("head_tilt", SG90, 0, 0, 185,
               shaft_axis="X", shaft_sign=1,
               joint_name="head_tilt", joint_range_deg=(-30, 30),
               tier="spark"),

    # ── Shoulders (both tiers — MG90S, verified from STEP v1) ──
    ServoMount("left_shoulder_pitch", MG90S, -74, 0, 140,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_shoulder_pitch", joint_range_deg=(-90, 90),
               tier="spark"),

    ServoMount("right_shoulder_pitch", MG90S, 74, 0, 140,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_shoulder_pitch", joint_range_deg=(-90, 90),
               tier="spark"),

    # NOTE: shoulder_roll not in STEP v1 mockup — add when v2 includes it

    # ── Waist (both tiers — MG90S, verified from STEP v1) ──
    ServoMount("waist_yaw", MG90S, 0, 0, 15,
               shaft_axis="Z", shaft_sign=1,
               joint_name="waist_yaw", joint_range_deg=(-90, 90),
               tier="spark"),

    # ── Elbows (Pro only — SG90, horizontal at shoulder height) ──
    ServoMount("left_elbow_pitch", SG90, -107, 0, 140,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_elbow_pitch", joint_range_deg=(-120, 0),
               tier="pro"),

    ServoMount("right_elbow_pitch", SG90, 107, 0, 140,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_elbow_pitch", joint_range_deg=(-120, 0),
               tier="pro"),

    # ── Hands / forearm (Pro only — SG90, at wrist) ──
    ServoMount("left_hand_pitch", SG90, -164, 0, 140,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_hand_pitch", joint_range_deg=(-45, 45),
               tier="pro"),

    ServoMount("right_hand_pitch", SG90, 164, 0, 140,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_hand_pitch", joint_range_deg=(-45, 45),
               tier="pro"),

    # ── Hips (Pro only) ──
    ServoMount("left_hip_yaw", XL330, -20, 0, 0,
               shaft_axis="Z", shaft_sign=1,
               joint_name="left_hip_yaw", joint_range_deg=(-30, 30),
               tier="pro"),

    ServoMount("right_hip_yaw", XL330, 20, 0, 0,
               shaft_axis="Z", shaft_sign=1,
               joint_name="right_hip_yaw", joint_range_deg=(-30, 30),
               tier="pro"),

    ServoMount("left_hip_pitch", XL330, -20, 0, 0,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_hip_pitch", joint_range_deg=(-90, 45),
               tier="pro"),

    ServoMount("right_hip_pitch", XL330, 20, 0, 0,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_hip_pitch", joint_range_deg=(-90, 45),
               tier="pro"),

    # ── Knees (Pro only) ──
    ServoMount("left_knee_pitch", XL330, -20, 0, -55,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_knee_pitch", joint_range_deg=(0, 120),
               tier="pro"),

    ServoMount("right_knee_pitch", XL330, 20, 0, -55,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_knee_pitch", joint_range_deg=(0, 120),
               tier="pro"),

    # ── Ankles (Pro only) ──
    ServoMount("left_ankle_pitch", XL330, -20, 0, -110,
               shaft_axis="X", shaft_sign=-1,
               joint_name="left_ankle_pitch", joint_range_deg=(-30, 30),
               tier="pro"),

    ServoMount("right_ankle_pitch", XL330, 20, 0, -110,
               shaft_axis="X", shaft_sign=1,
               joint_name="right_ankle_pitch", joint_range_deg=(-30, 30),
               tier="pro"),
]

# ── Skeleton Variant Spec ─────────────────────────────────────────────────
#
# The skeleton is a family of variants, not one fixed frame. The user authors
# STEP variants (different torso/arm/leg dimensions) to cover body types —
# humanoid, animal, mystic creature, etc. SkeletonSpec captures the dimensions
# that CHANGE per variant; the servo pockets, fixtures, clearance tolerances,
# and magnet seats stay STANDARD across all variants (same servos, same
# mounting). Joint positions are derived from the variable segment lengths.
#
# To make a variant:  dataclasses.replace(DEFAULT_SPEC, torso_gap=150, ...)

@dataclass(frozen=True)
class SkeletonSpec:
    """Per-variant dimensions. Standard servo/fixture geometry lives elsewhere."""
    name: str
    body_type: str                 # "humanoid" | "animal" | "creature"
    total_height: float

    # Torso column
    frame_chest_bottom_z: float    # torso/base boundary (hip cut)
    torso_gap: float               # frame_chest_bottom_z -> shoulder line
    torso_d: float                 # torso depth (Y)
    waist_z: float                 # waist servo height

    # Shoulders / arms (horizontal in T-pose, all at shoulder_z)
    shoulder_x: float              # shoulder pitch servo X (half-spread)
    upper_arm: float               # shoulder -> elbow (X)
    forearm: float                 # elbow -> hand (X)

    # Head
    head_pan_z: float
    head_tilt_z: float
    head_top_z: float

    # Legs (Pro/Max; ignored for Spark)
    leg_hip_z: float
    leg_hip_x: float
    thigh: float
    shin: float
    foot_h: float

    # Base / stand
    base_w: float
    base_d: float
    base_h: float

    # ── Derived joint positions ──
    @property
    def shoulder_z(self) -> float:
        return self.frame_chest_bottom_z + self.torso_gap

    @property
    def shoulder_spread(self) -> float:
        return self.shoulder_x * 2

    @property
    def elbow_x(self) -> float:
        return self.shoulder_x + self.upper_arm

    @property
    def hand_x(self) -> float:
        return self.elbow_x + self.forearm

    @property
    def knee_z(self) -> float:
        return self.leg_hip_z - self.thigh

    @property
    def ankle_z(self) -> float:
        return self.knee_z - self.shin

    @property
    def foot_bottom_z(self) -> float:
        return self.ankle_z - self.foot_h

    def cut_planes(self, pro: bool = False) -> list["CutPlane"]:
        """Skeleton-driven cut planes (joints fixed by this variant).

        The character-driven alternative is landmarks.adaptive_cut_planes().
        """
        head_torso_z = (self.shoulder_z + self.head_pan_z) / 2
        planes = [
            CutPlane("head_torso", "Z", head_torso_z,
                     self.shoulder_z + 2, self.head_pan_z, ("head", "torso")),
            CutPlane("torso_base", "Z", self.frame_chest_bottom_z,
                     self.frame_chest_bottom_z - 8, self.frame_chest_bottom_z + 8,
                     ("torso", "base")),
            CutPlane("left_arm", "X", -self.shoulder_x,
                     -self.shoulder_x - 8, -self.shoulder_x + 8, ("torso", "left_arm")),
            CutPlane("right_arm", "X", self.shoulder_x,
                     self.shoulder_x - 8, self.shoulder_x + 8, ("torso", "right_arm")),
        ]
        if pro:
            split = self.leg_hip_x * 0.25
            planes += [
                CutPlane("left_leg", "X", -split, -self.leg_hip_x, 0, ("base", "left_leg")),
                CutPlane("right_leg", "X", split, 0, self.leg_hip_x, ("base", "right_leg")),
            ]
        return planes


# The current STEP v1 250mm humanoid — baseline variant.
DEFAULT_SPEC = SkeletonSpec(
    name="spark_pro_250",
    body_type="humanoid",
    total_height=TOTAL_HEIGHT,
    frame_chest_bottom_z=12.0,
    torso_gap=TORSO_GAP,
    torso_d=TORSO_D,
    waist_z=15.0,
    shoulder_x=74.0,
    upper_arm=UPPER_ARM,
    forearm=FOREARM,
    head_pan_z=155.0,
    head_tilt_z=185.0,
    head_top_z=165.0,
    leg_hip_z=0.0,
    leg_hip_x=20.0,
    thigh=THIGH,
    shin=SHIN,
    foot_h=FOOT_H,
    base_w=BASE_W,
    base_d=BASE_D,
    base_h=BASE_H,
)


# The three planned variants (SKELETON_SPEC.md "Future Skeleton Variants").
# Only Spark Humanoid is in production. Spark Stumpy (creatures: wider base,
# shorter torso, 4 limb mounts) and Max Humanoid (400-500mm, XL330+XL430) are
# future — register them here once their dimensions are confirmed.
SPARK_HUMANOID = DEFAULT_SPEC
SKELETON_VARIANTS = {"spark_humanoid": SPARK_HUMANOID}


# Convenience lookups — derived from DEFAULT_SPEC (single source of truth).
WAIST_Z = DEFAULT_SPEC.waist_z
SHOULDER_Z = DEFAULT_SPEC.shoulder_z
SHOULDER_X = DEFAULT_SPEC.shoulder_x
SHOULDER_SPREAD = DEFAULT_SPEC.shoulder_spread  # shoulder-to-shoulder
HEAD_PAN_Z = DEFAULT_SPEC.head_pan_z
HEAD_TILT_Z = DEFAULT_SPEC.head_tilt_z
HEAD_Z = HEAD_TILT_Z              # Alias for importers
ELBOW_Z = DEFAULT_SPEC.shoulder_z  # Same as shoulder — arms horizontal
ELBOW_X = DEFAULT_SPEC.elbow_x
HAND_Z = DEFAULT_SPEC.shoulder_z   # Same as shoulder — arms horizontal
HAND_X = DEFAULT_SPEC.hand_x
HIP_Z = DEFAULT_SPEC.leg_hip_z
HIP_X = DEFAULT_SPEC.leg_hip_x
KNEE_Z = DEFAULT_SPEC.knee_z
ANKLE_Z = DEFAULT_SPEC.ankle_z
FOOT_BOTTOM_Z = DEFAULT_SPEC.foot_bottom_z
HEAD_TOP_Z = DEFAULT_SPEC.head_top_z
FRAME_CHEST_BOTTOM_Z = DEFAULT_SPEC.frame_chest_bottom_z


def mounts_for_tier(tier: str) -> list[ServoMount]:
    """Return servo mounts for a given tier ('spark' or 'pro')."""
    if tier == "pro":
        return list(SERVO_MOUNTS)
    elif tier == "spark":
        return [m for m in SERVO_MOUNTS if m.tier == "spark"]
    else:
        raise ValueError(f"Unknown tier: {tier}. Must be 'spark' or 'pro'.")


# ── Magnet Positions ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class MagnetSeat:
    """A magnet pocket position on the skeleton frame."""
    id: str
    zone: str       # "head", "torso", "left_arm", "right_arm", "base",
                    # "left_leg", "right_leg"
    x: float
    y: float
    z: float
    normal: tuple[float, float, float]  # Outward-facing direction


MAG_D = 6.0       # Magnet diameter
MAG_H = 3.0       # Magnet height
MAG_POCKET_D = 6.1 # Press-fit pocket diameter
MAG_POCKET_H = 3.1 # Pocket depth

MAGNET_SEATS: list[MagnetSeat] = [
    # ── Head zone (8) — ring at Z=155 (at head pan joint) ──
    MagnetSeat("H1", "head", 0, -14, 155, (0, -1, 0)),
    MagnetSeat("H2", "head", 0, 14, 155, (0, 1, 0)),
    MagnetSeat("H3", "head", -14, 0, 155, (-1, 0, 0)),
    MagnetSeat("H4", "head", 14, 0, 155, (1, 0, 0)),
    MagnetSeat("H5", "head", -10, -10, 155, (-1, -1, 0)),
    MagnetSeat("H6", "head", 10, -10, 155, (1, -1, 0)),
    MagnetSeat("H7", "head", -10, 10, 155, (-1, 1, 0)),
    MagnetSeat("H8", "head", 10, 10, 155, (1, 1, 0)),

    # ── Torso zone (12) — 3 rings of 4, spaced through torso cavity ──
    MagnetSeat("T1", "torso", 0, -14, 40, (0, -1, 0)),
    MagnetSeat("T2", "torso", 0, 14, 40, (0, 1, 0)),
    MagnetSeat("T3", "torso", 0, -14, 80, (0, -1, 0)),
    MagnetSeat("T4", "torso", 0, 14, 80, (0, 1, 0)),
    MagnetSeat("T5", "torso", 0, -14, 120, (0, -1, 0)),
    MagnetSeat("T6", "torso", 0, 14, 120, (0, 1, 0)),
    MagnetSeat("T7", "torso", -14, 0, 40, (-1, 0, 0)),
    MagnetSeat("T8", "torso", 14, 0, 40, (1, 0, 0)),
    MagnetSeat("T9", "torso", -14, 0, 80, (-1, 0, 0)),
    MagnetSeat("T10", "torso", 14, 0, 80, (1, 0, 0)),
    MagnetSeat("T11", "torso", -14, 0, 120, (-1, 0, 0)),
    MagnetSeat("T12", "torso", 14, 0, 120, (1, 0, 0)),

    # ── Left arm zone (6) — along horizontal arm bracket ──
    MagnetSeat("LA1", "left_arm", -90, -10, 140, (0, -1, 0)),
    MagnetSeat("LA2", "left_arm", -90, 10, 140, (0, 1, 0)),
    MagnetSeat("LA3", "left_arm", -120, -10, 140, (0, -1, 0)),
    MagnetSeat("LA4", "left_arm", -120, 10, 140, (0, 1, 0)),
    MagnetSeat("LA5", "left_arm", -150, -8, 140, (-1, 0, 0)),
    MagnetSeat("LA6", "left_arm", -150, 8, 140, (-1, 0, 0)),

    # ── Right arm zone (6) — mirror of left ──
    MagnetSeat("RA1", "right_arm", 90, -10, 140, (0, -1, 0)),
    MagnetSeat("RA2", "right_arm", 90, 10, 140, (0, 1, 0)),
    MagnetSeat("RA3", "right_arm", 120, -10, 140, (0, -1, 0)),
    MagnetSeat("RA4", "right_arm", 120, 10, 140, (0, 1, 0)),
    MagnetSeat("RA5", "right_arm", 150, -8, 140, (1, 0, 0)),
    MagnetSeat("RA6", "right_arm", 150, 8, 140, (1, 0, 0)),

    # ── Base zone (8) — perimeter at Z=-10 ──
    MagnetSeat("B1", "base", -35, -28, -10, (0, -1, 0)),
    MagnetSeat("B2", "base", 35, -28, -10, (0, -1, 0)),
    MagnetSeat("B3", "base", -35, 28, -10, (0, 1, 0)),
    MagnetSeat("B4", "base", 35, 28, -10, (0, 1, 0)),
    MagnetSeat("B5", "base", 0, -28, -10, (0, -1, 0)),
    MagnetSeat("B6", "base", 0, 28, -10, (0, 1, 0)),
    MagnetSeat("B7", "base", -40, 0, -10, (-1, 0, 0)),
    MagnetSeat("B8", "base", 40, 0, -10, (1, 0, 0)),

    # ── Left leg zone (6) — Pro only ──
    MagnetSeat("LL1", "left_leg", -20, -10, -30, (0, -1, 0)),
    MagnetSeat("LL2", "left_leg", -20, 10, -30, (0, 1, 0)),
    MagnetSeat("LL3", "left_leg", -20, -10, -80, (0, -1, 0)),
    MagnetSeat("LL4", "left_leg", -20, 10, -80, (0, 1, 0)),
    MagnetSeat("LL5", "left_leg", -28, 0, -55, (-1, 0, 0)),
    MagnetSeat("LL6", "left_leg", -12, 0, -55, (1, 0, 0)),

    # ── Right leg zone (6) — Pro only, mirror of left ──
    MagnetSeat("RL1", "right_leg", 20, -10, -30, (0, -1, 0)),
    MagnetSeat("RL2", "right_leg", 20, 10, -30, (0, 1, 0)),
    MagnetSeat("RL3", "right_leg", 20, -10, -80, (0, -1, 0)),
    MagnetSeat("RL4", "right_leg", 20, 10, -80, (0, 1, 0)),
    MagnetSeat("RL5", "right_leg", 28, 0, -55, (1, 0, 0)),
    MagnetSeat("RL6", "right_leg", -12, 0, -55, (-1, 0, 0)),
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


# Head/torso cut at Z=148 — between shoulder (140) and head pan (155)
# Torso/base cut at Z=12 — bottom of frame_chest (STEP v1 verified)
# Arm cuts at X=±74 — at shoulder MG90S servo position
# Leg cut at X=0 — between left and right legs (Pro only)
DEFAULT_CUT_PLANES = [
    CutPlane("head_torso", "Z", 148, 142, 153, ("head", "torso")),
    CutPlane("torso_base", "Z", 12, 0, 20, ("torso", "base")),
    CutPlane("left_arm", "X", -74, -80, -60, ("torso", "left_arm")),
    CutPlane("right_arm", "X", 74, 60, 80, ("torso", "right_arm")),
]

# Pro adds leg zone cuts (split base zone into base + left_leg + right_leg)
PRO_CUT_PLANES = DEFAULT_CUT_PLANES + [
    CutPlane("left_leg", "X", -5, -15, 0, ("base", "left_leg")),
    CutPlane("right_leg", "X", 5, 0, 15, ("base", "right_leg")),
]

BODY_ZONES = ["head", "torso", "left_arm", "right_arm", "base"]
PRO_BODY_ZONES = ["head", "torso", "left_arm", "right_arm", "base",
                   "left_leg", "right_leg"]


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
    ClearanceEnvelope("left_leg", 2.0, 0.0, 0.0, 20.0),
    ClearanceEnvelope("right_leg", 2.0, 0.0, 0.0, 20.0),
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
    "left_leg": 2,
    "right_leg": 2,
}

MAGNET_MAX_COUNT = {
    "head": 8,
    "torso": 12,
    "left_arm": 6,
    "right_arm": 6,
    "base": 8,
    "left_leg": 6,
    "right_leg": 6,
}

MAGNET_PULL_FORCE_KG = 0.5  # Per 6×3mm neodymium disc magnet
MAGNET_BOSS_OD = 10.0       # Shell-side boss outer diameter
MAGNET_BOSS_H = 4.0         # Shell-side boss height
MIN_WALL_BEHIND_BOSS = 1.5  # Don't punch through shell
MIN_SHELL_THICKNESS_FOR_BOSS = 6.0  # Boss needs 4mm + 2mm wall behind


# ── Removal Directions ────────────────────────────────────────────────────
# Each zone has a removal direction (how the shell slides on/off)
# and a draft angle applied along that axis for easy release.

@dataclass(frozen=True)
class RemovalSpec:
    """How a shell zone is removed from the skeleton."""
    zone: str
    direction: tuple[float, float, float]  # Unit vector: direction to REMOVE
    draft_angle_deg: float                 # Taper angle along removal direction
    is_clamshell: bool                     # True = split into front/back halves
    split_plane: str | None                # "XZ" or "YZ" — where clamshell splits


REMOVAL_SPECS = {
    "head": RemovalSpec("head", (0, 0, 1), 2.0, False, None),
    # Head lifts straight up. 2° draft taper on internal cavity.

    "torso": RemovalSpec("torso", (0, -1, 0), 1.0, True, "XZ"),
    # Torso is clamshell: front half pulls forward (-Y), back half pulls backward (+Y).
    # Split along XZ plane (Y=0). Each half has its own magnets.

    "left_arm": RemovalSpec("left_arm", (-1, 0, 0), 2.0, False, None),
    # Left arm slides outward (-X direction).

    "right_arm": RemovalSpec("right_arm", (1, 0, 0), 2.0, False, None),
    # Right arm slides outward (+X direction).

    "base": RemovalSpec("base", (0, 0, -1), 1.5, False, None),
    # Base lifts off downward (flip robot, pull off).

    "left_leg": RemovalSpec("left_leg", (0, -1, 0), 1.5, True, "XZ"),
    # Left leg is clamshell (wraps around XL330 servos).

    "right_leg": RemovalSpec("right_leg", (0, -1, 0), 1.5, True, "XZ"),
    # Right leg is clamshell (wraps around XL330 servos).
}


# ── Skeleton Clearance Volume Geometry ────────────────────────────────────
# These define the skeleton solid per zone — used for boolean subtraction.
# Each entry is a list of (shape, position, dimensions) tuples that get
# unioned together to form the clearance volume for that zone.

# Clearance expansion: how much bigger than the actual skeleton frame
# the subtraction volume should be, to ensure the shell slides on/off.
CLEARANCE_EXPANSION = 1.5  # mm per side beyond the physical frame

# Joint rotation sweep volumes
JOINT_SWEEPS = {
    "waist_yaw": {
        "center": (0, 0, 15),
        "axis": "Z",
        "range_deg": (-90, 90),
        "radius": 50,  # Sweep radius — must clear torso shell at waist
        "height": 6,   # Thin disc at the joint boundary
    },
    "head_pan": {
        "center": (0, 0, 148),  # At head/torso cut boundary
        "axis": "Z",
        "range_deg": (-90, 90),
        "radius": 25,
        "height": 6,
    },
    "head_tilt": {
        "center": (0, 0, 185),
        "axis": "X",
        "range_deg": (-30, 30),
        "radius": 20,
        "height": 6,
    },
    "left_shoulder_pitch": {
        "center": (-74, 0, 140),
        "axis": "X",
        "range_deg": (-90, 90),
        "radius": 25,
        "height": 6,
    },
    "right_shoulder_pitch": {
        "center": (74, 0, 140),
        "axis": "X",
        "range_deg": (-90, 90),
        "radius": 25,
        "height": 6,
    },
    # ── Pro-only joint sweeps ──
    "left_elbow_pitch": {
        "center": (-107, 0, 140),
        "axis": "X",
        "range_deg": (-120, 0),
        "radius": 18,
        "height": 6,
    },
    "right_elbow_pitch": {
        "center": (107, 0, 140),
        "axis": "X",
        "range_deg": (-120, 0),
        "radius": 18,
        "height": 6,
    },
    "left_hip_yaw": {
        "center": (-20, 0, 0),
        "axis": "Z",
        "range_deg": (-30, 30),
        "radius": 22,
        "height": 6,
    },
    "right_hip_yaw": {
        "center": (20, 0, 0),
        "axis": "Z",
        "range_deg": (-30, 30),
        "radius": 22,
        "height": 6,
    },
    "left_hip_pitch": {
        "center": (-20, 0, 0),
        "axis": "X",
        "range_deg": (-90, 45),
        "radius": 22,
        "height": 6,
    },
    "right_hip_pitch": {
        "center": (20, 0, 0),
        "axis": "X",
        "range_deg": (-90, 45),
        "radius": 22,
        "height": 6,
    },
    "left_knee_pitch": {
        "center": (-20, 0, -55),
        "axis": "X",
        "range_deg": (0, 120),
        "radius": 22,
        "height": 6,
    },
    "right_knee_pitch": {
        "center": (20, 0, -55),
        "axis": "X",
        "range_deg": (0, 120),
        "radius": 22,
        "height": 6,
    },
    "left_ankle_pitch": {
        "center": (-20, 0, -110),
        "axis": "X",
        "range_deg": (-30, 30),
        "radius": 22,
        "height": 6,
    },
    "right_ankle_pitch": {
        "center": (20, 0, -110),
        "axis": "X",
        "range_deg": (-30, 30),
        "radius": 22,
        "height": 6,
    },
}
