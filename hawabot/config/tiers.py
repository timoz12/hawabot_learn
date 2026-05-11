"""Hardware tier definitions for Spark, Pro, and Max.

Two tiers at launch, one future flagship:

Spark = tabletop desk companion, ESP32-S3, upper body only (7 DOF, $199)
Pro   = walking humanoid, ESP32-S3, full body with legs + FSRs (19 DOF, $599)
Max   = future flagship, 400-500mm, on-board AI, autonomous ($999+)

Spark and Pro share the same 250mm skeleton and ESP32-S3 custom PCB.
Pro is an upgrade from Spark (add legs, arms, sensors, battery).
Max is a separate, larger robot for enthusiasts who completed the curriculum.

Friendly joint names map internally to Poppy convention:
  head_pan → head_z, head_tilt → head_y
  left_shoulder_pitch → l_shoulder_y, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TierName(str, Enum):
    SPARK = "spark"
    PRO = "pro"
    MAX = "max"
    MOCK = "mock"


class FormFactor(str, Enum):
    TABLETOP = "tabletop"
    BIPEDAL = "bipedal"
    BIPEDAL_LARGE = "bipedal_large"


@dataclass(frozen=True)
class ServoSpec:
    model: str
    torque_kg_cm: float
    speed_deg_per_sec: float
    angle_range: tuple[float, float] = (-90.0, 90.0)
    has_feedback: bool = False
    supports_compliance: bool = False  # Mode 5 / current-based position


@dataclass(frozen=True)
class JointSpec:
    """Defines a single joint's capabilities at a given tier."""

    servo: ServoSpec
    default_angle: float = 0.0
    min_angle: float = -90.0
    max_angle: float = 90.0
    speed_limit: float | None = None  # deg/s, None = use servo default
    poppy_name: str = ""  # Internal Poppy convention name (e.g. "l_shoulder_y")


@dataclass(frozen=True)
class TierDefinition:
    name: TierName
    display_name: str
    form_factor: FormFactor
    compute: str
    bom_cost_usd: int
    dof: int
    sensors: tuple[str, ...]
    joints: dict[str, JointSpec]
    has_legs: bool = False
    has_waist: bool = False
    description: str = ""


# ---------------------------------------------------------------------------
# Servo catalogue
# ---------------------------------------------------------------------------

SG90 = ServoSpec(
    model="SG90",
    torque_kg_cm=1.8,
    speed_deg_per_sec=360.0,
    angle_range=(-90.0, 90.0),
    has_feedback=False,
    supports_compliance=False,
)

MG90S = ServoSpec(
    model="MG90S",
    torque_kg_cm=2.2,
    speed_deg_per_sec=300.0,
    angle_range=(-90.0, 90.0),
    has_feedback=False,
    supports_compliance=False,
)

XL330 = ServoSpec(
    model="Dynamixel XL330-M288",
    torque_kg_cm=6.5,
    speed_deg_per_sec=300.0,
    angle_range=(-180.0, 180.0),
    has_feedback=True,
    supports_compliance=True,
)

# XL430 — reserved for Max tier (future). Not used in Spark or Pro.
XL430 = ServoSpec(
    model="Dynamixel XL430-W250",
    torque_kg_cm=16.0,
    speed_deg_per_sec=230.0,
    angle_range=(-180.0, 180.0),
    has_feedback=True,
    supports_compliance=True,
)


# ---------------------------------------------------------------------------
# Joint definitions per tier
# ---------------------------------------------------------------------------


def _spark_joints() -> dict[str, JointSpec]:
    """Spark: 7 DOF tabletop companion — head + shoulders + shoulder roll + waist.

    No legs. Desk-mounted upper body that can look around, wave, gesture,
    and serve as an AI-powered study companion. $199.
    """
    return {
        # Head
        "head_pan": JointSpec(
            servo=SG90, min_angle=-90, max_angle=90, poppy_name="head_z",
        ),
        "head_tilt": JointSpec(
            servo=SG90, min_angle=-30, max_angle=30, poppy_name="head_y",
        ),
        # Left arm
        "left_shoulder_pitch": JointSpec(
            servo=MG90S, min_angle=-90, max_angle=90, poppy_name="l_shoulder_y",
        ),
        "left_shoulder_roll": JointSpec(
            servo=SG90, min_angle=-45, max_angle=45, poppy_name="l_shoulder_x",
        ),
        # Right arm
        "right_shoulder_pitch": JointSpec(
            servo=MG90S, min_angle=-90, max_angle=90, poppy_name="r_shoulder_y",
        ),
        "right_shoulder_roll": JointSpec(
            servo=SG90, min_angle=-45, max_angle=45, poppy_name="r_shoulder_x",
        ),
        # Waist yaw — lets the whole upper body turn on its base
        "waist_yaw": JointSpec(
            servo=MG90S, min_angle=-90, max_angle=90, poppy_name="abs_z",
        ),
    }


def _pro_joints() -> dict[str, JointSpec]:
    """Pro: 19 DOF walking humanoid — Spark + elbows + hands + 8 leg joints.

    Same 250mm skeleton as Spark. Upgrade adds arms, legs, sensors, battery.
    Shoulders and waist upgraded to XL330 for feedback and load bearing.
    FSRs in feet required for walking (not defined here — sensor-level).
    $599 all-in, or $399 upgrade from Spark.
    """
    joints = _spark_joints()

    # Upgrade shoulders and waist to XL330 for feedback + dual shaft support
    joints["left_shoulder_pitch"] = JointSpec(
        servo=XL330, min_angle=-90, max_angle=90, poppy_name="l_shoulder_y",
    )
    joints["right_shoulder_pitch"] = JointSpec(
        servo=XL330, min_angle=-90, max_angle=90, poppy_name="r_shoulder_y",
    )
    joints["waist_yaw"] = JointSpec(
        servo=XL330, min_angle=-90, max_angle=90, poppy_name="abs_z",
    )

    # Arm additions (elbows + hands)
    joints.update({
        "left_elbow_pitch": JointSpec(
            servo=SG90, min_angle=-90, max_angle=90, poppy_name="l_elbow_y",
        ),
        "left_hand_pitch": JointSpec(
            servo=SG90, min_angle=0, max_angle=45, poppy_name="l_hand_y",
        ),
        "right_elbow_pitch": JointSpec(
            servo=SG90, min_angle=-90, max_angle=90, poppy_name="r_elbow_y",
        ),
        "right_hand_pitch": JointSpec(
            servo=SG90, min_angle=0, max_angle=45, poppy_name="r_hand_y",
        ),
    })

    # Leg joints (8 DOF — hip yaw/pitch + knee + ankle per side)
    joints.update({
        "left_hip_yaw": JointSpec(
            servo=XL330, min_angle=-45, max_angle=45, poppy_name="l_hip_z",
        ),
        "left_hip_pitch": JointSpec(
            servo=XL330, min_angle=-90, max_angle=90, poppy_name="l_hip_y",
        ),
        "left_knee_pitch": JointSpec(
            servo=XL330, min_angle=0, max_angle=120, poppy_name="l_knee_y",
        ),
        "left_ankle_pitch": JointSpec(
            servo=XL330, min_angle=-30, max_angle=30, poppy_name="l_ankle_y",
        ),
        "right_hip_yaw": JointSpec(
            servo=XL330, min_angle=-45, max_angle=45, poppy_name="r_hip_z",
        ),
        "right_hip_pitch": JointSpec(
            servo=XL330, min_angle=-90, max_angle=90, poppy_name="r_hip_y",
        ),
        "right_knee_pitch": JointSpec(
            servo=XL330, min_angle=0, max_angle=120, poppy_name="r_knee_y",
        ),
        "right_ankle_pitch": JointSpec(
            servo=XL330, min_angle=-30, max_angle=30, poppy_name="r_ankle_y",
        ),
    })
    return joints


def _max_joints() -> dict[str, JointSpec]:
    """Max: 19+ DOF — future flagship, 400-500mm, on-board AI.

    Uses XL330 throughout + XL430 for high-torque joints.
    Separate skeleton from Spark/Pro. Not upgrade-compatible.
    Aspirational product for enthusiasts who completed the full curriculum.
    $999+ depending on options.
    """
    # Start from Pro layout, upgrade all servos to XL330/XL430
    joints = _pro_joints()
    # All joints already use XL330 for legs/shoulders.
    # Max may add hip roll, wrist rotation, etc. in future.
    return joints


# ---------------------------------------------------------------------------
# Tier registry
# ---------------------------------------------------------------------------

TIERS: dict[TierName, TierDefinition] = {
    TierName.SPARK: TierDefinition(
        name=TierName.SPARK,
        display_name="Spark",
        form_factor=FormFactor.TABLETOP,
        compute="ESP32-S3",
        bom_cost_usd=45,
        dof=7,
        sensors=("speaker",),
        joints=_spark_joints(),
        has_legs=False,
        has_waist=True,
        description=(
            "Tabletop desk companion: 7-DOF upper body on a flat base. "
            "Speaker for voice output. AI tutor runs on phone/tablet via WiFi. $199."
        ),
    ),
    TierName.PRO: TierDefinition(
        name=TierName.PRO,
        display_name="Pro",
        form_factor=FormFactor.BIPEDAL,
        compute="ESP32-S3",
        bom_cost_usd=361,
        dof=19,
        sensors=("speaker", "microphone", "imu", "fsr", "camera"),
        joints=_pro_joints(),
        has_legs=True,
        has_waist=True,
        description=(
            "Walking humanoid: 19-DOF, same 250mm skeleton as Spark. "
            "Adds legs (XL330), elbows, hands, FSRs, IMU, mic, camera, battery. "
            "AI tutor runs on phone/tablet via WiFi. $599 all-in or $399 upgrade."
        ),
    ),
    TierName.MAX: TierDefinition(
        name=TierName.MAX,
        display_name="Max",
        form_factor=FormFactor.BIPEDAL_LARGE,
        compute="Raspberry Pi 5 / CM5",
        bom_cost_usd=500,
        dof=19,
        sensors=("speaker", "microphone", "imu", "fsr", "camera", "ultrasonic", "lidar"),
        joints=_max_joints(),
        has_legs=True,
        has_waist=True,
        description=(
            "Future flagship: 400-500mm walking humanoid with on-board AI. "
            "Fully autonomous, battery powered. For enthusiasts who completed "
            "the Spark → Pro curriculum. Aspirational marketing vehicle. $999+."
        ),
    ),
}


def get_tier(name: str | TierName) -> TierDefinition:
    """Look up a tier by name string or enum."""
    if isinstance(name, str):
        name = TierName(name.lower())
    return TIERS[name]


# Mock tier mirrors Spark layout (7 DOF) for simulation but enables all sensors
MOCK_TIER = TierDefinition(
    name=TierName.MOCK,
    display_name="Mock (Simulation)",
    form_factor=FormFactor.TABLETOP,
    compute="Local machine",
    bom_cost_usd=0,
    dof=7,
    sensors=("speaker", "microphone", "imu", "fsr", "camera", "ultrasonic"),
    joints=_spark_joints(),
    has_legs=False,
    has_waist=True,
    description="Simulation mode — all sensors available, Spark joint layout (7 DOF)",
)
