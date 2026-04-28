"""Hardware tier definitions for Spark, Core, and Pro.

Spark = tabletop companion (upper body only, no legs)
Core  = articulated companion with elbows + waist, smart servos with feedback
Pro   = full bipedal humanoid with legs, advanced sensors

Friendly joint names map internally to Poppy convention:
  head_pan → head_z, head_tilt → head_y
  left_shoulder_pitch → l_shoulder_y, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TierName(str, Enum):
    SPARK = "spark"
    CORE = "core"
    PRO = "pro"
    MOCK = "mock"


class FormFactor(str, Enum):
    TABLETOP = "tabletop"
    MOBILE = "mobile"
    BIPEDAL = "bipedal"


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

STS3215 = ServoSpec(
    model="Feetech STS3215",
    torque_kg_cm=15.0,
    speed_deg_per_sec=250.0,
    angle_range=(-150.0, 150.0),
    has_feedback=True,
    supports_compliance=True,
)

XL430 = ServoSpec(
    model="Dynamixel XL430-W250",
    torque_kg_cm=16.0,
    speed_deg_per_sec=230.0,
    angle_range=(-180.0, 180.0),
    has_feedback=True,
    supports_compliance=True,
)

XL330 = ServoSpec(
    model="Dynamixel XL330-M288",
    torque_kg_cm=6.5,
    speed_deg_per_sec=300.0,
    angle_range=(-180.0, 180.0),
    has_feedback=True,
    supports_compliance=True,
)

# ---------------------------------------------------------------------------
# Joint definitions per tier
# ---------------------------------------------------------------------------


def _spark_joints() -> dict[str, JointSpec]:
    """Spark: 5 DOF tabletop companion — head pan/tilt + 2×shoulder pitch + 1 waist.

    No legs. Desk-mounted upper body that can look around, wave, gesture,
    and serve as an AI-powered office/study companion.
    """
    return {
        # Head
        "head_pan": JointSpec(
            servo=SG90, min_angle=-90, max_angle=90, poppy_name="head_z",
        ),
        "head_tilt": JointSpec(
            servo=SG90, min_angle=-30, max_angle=30, poppy_name="head_y",
        ),
        # Left arm (single servo — shoulder pitch for raise/lower)
        "left_shoulder_pitch": JointSpec(
            servo=MG90S, min_angle=-90, max_angle=90, poppy_name="l_shoulder_y",
        ),
        # Right arm (single servo — shoulder pitch for raise/lower)
        "right_shoulder_pitch": JointSpec(
            servo=MG90S, min_angle=-90, max_angle=90, poppy_name="r_shoulder_y",
        ),
        # Waist yaw — lets the whole upper body turn on its base
        "waist_yaw": JointSpec(
            servo=SG90, min_angle=-90, max_angle=90, poppy_name="abs_z",
        ),
    }


def _core_joints() -> dict[str, JointSpec]:
    """Core: 10 DOF — enhanced upper body with elbows, shoulder roll, waist.

    Still tabletop/mobile (no bipedal legs), but smart servos with feedback
    and compliance. Can do teach-by-demo natively.
    """
    return {
        # Head
        "head_pan": JointSpec(
            servo=STS3215, min_angle=-120, max_angle=120, poppy_name="head_z",
        ),
        "head_tilt": JointSpec(
            servo=STS3215, min_angle=-45, max_angle=45, poppy_name="head_y",
        ),
        # Left arm
        "left_shoulder_pitch": JointSpec(
            servo=STS3215, min_angle=-120, max_angle=155, poppy_name="l_shoulder_y",
        ),
        "left_shoulder_roll": JointSpec(
            servo=STS3215, min_angle=-105, max_angle=110, poppy_name="l_shoulder_x",
        ),
        "left_elbow": JointSpec(
            servo=STS3215, min_angle=-148, max_angle=1, poppy_name="l_elbow_y",
        ),
        # Right arm
        "right_shoulder_pitch": JointSpec(
            servo=STS3215, min_angle=-155, max_angle=120, poppy_name="r_shoulder_y",
        ),
        "right_shoulder_roll": JointSpec(
            servo=STS3215, min_angle=-110, max_angle=105, poppy_name="r_shoulder_x",
        ),
        "right_elbow": JointSpec(
            servo=STS3215, min_angle=-1, max_angle=148, poppy_name="r_elbow_y",
        ),
        # Waist
        "waist_yaw": JointSpec(
            servo=STS3215, min_angle=-90, max_angle=90, poppy_name="abs_z",
        ),
        # Arm rotation (one side for gestures)
        "left_arm_rotation": JointSpec(
            servo=STS3215, min_angle=-105, max_angle=105, poppy_name="l_arm_z",
        ),
    }


def _pro_joints() -> dict[str, JointSpec]:
    """Pro: 20 DOF — full bipedal humanoid matching Hawabot reference.

    Joint limits derived from Poppy Humanoid convention / calibrated Hawabot.
    """
    return {
        # Head
        "head_pan": JointSpec(
            servo=XL330, min_angle=-90, max_angle=90, poppy_name="head_z",
        ),
        "head_tilt": JointSpec(
            servo=XL330, min_angle=-45, max_angle=6, poppy_name="head_y",
        ),
        # Left arm
        "left_shoulder_pitch": JointSpec(
            servo=XL430, min_angle=-120, max_angle=155, poppy_name="l_shoulder_y",
        ),
        "left_shoulder_roll": JointSpec(
            servo=XL430, min_angle=-105, max_angle=110, poppy_name="l_shoulder_x",
        ),
        "left_arm_rotation": JointSpec(
            servo=XL330, min_angle=-105, max_angle=105, poppy_name="l_arm_z",
        ),
        "left_elbow": JointSpec(
            servo=XL330, min_angle=-148, max_angle=1, poppy_name="l_elbow_y",
        ),
        # Right arm
        "right_shoulder_pitch": JointSpec(
            servo=XL430, min_angle=-155, max_angle=120, poppy_name="r_shoulder_y",
        ),
        "right_shoulder_roll": JointSpec(
            servo=XL430, min_angle=-110, max_angle=105, poppy_name="r_shoulder_x",
        ),
        "right_arm_rotation": JointSpec(
            servo=XL330, min_angle=-105, max_angle=105, poppy_name="r_arm_z",
        ),
        "right_elbow": JointSpec(
            servo=XL330, min_angle=-1, max_angle=148, poppy_name="r_elbow_y",
        ),
        # Waist
        "waist_yaw": JointSpec(
            servo=XL430, min_angle=-90, max_angle=90, poppy_name="abs_z",
        ),
        # Left leg
        "left_hip_roll": JointSpec(
            servo=XL430, min_angle=-30, max_angle=28.5, poppy_name="l_hip_x",
        ),
        "left_hip_yaw": JointSpec(
            servo=XL430, min_angle=-25, max_angle=90, poppy_name="l_hip_z",
        ),
        "left_hip_pitch": JointSpec(
            servo=XL430, min_angle=-104, max_angle=84, poppy_name="l_hip_y",
        ),
        "left_knee": JointSpec(
            servo=XL430, min_angle=-3.5, max_angle=134, poppy_name="l_knee_y",
        ),
        "left_ankle": JointSpec(
            servo=XL330, min_angle=-45, max_angle=45, poppy_name="l_ankle_y",
        ),
        # Right leg
        "right_hip_roll": JointSpec(
            servo=XL430, min_angle=-28.5, max_angle=30, poppy_name="r_hip_x",
        ),
        "right_hip_yaw": JointSpec(
            servo=XL430, min_angle=-90, max_angle=25, poppy_name="r_hip_z",
        ),
        "right_hip_pitch": JointSpec(
            servo=XL430, min_angle=-85, max_angle=105, poppy_name="r_hip_y",
        ),
        "right_knee": JointSpec(
            servo=XL430, min_angle=-134, max_angle=3.5, poppy_name="r_knee_y",
        ),
        "right_ankle": JointSpec(
            servo=XL330, min_angle=-45, max_angle=45, poppy_name="r_ankle_y",
        ),
    }


# ---------------------------------------------------------------------------
# Tier registry
# ---------------------------------------------------------------------------

TIERS: dict[TierName, TierDefinition] = {
    TierName.SPARK: TierDefinition(
        name=TierName.SPARK,
        display_name="Spark",
        form_factor=FormFactor.TABLETOP,
        compute="Raspberry Pi Pico W",
        bom_cost_usd=69,
        dof=5,
        sensors=("ultrasonic", "buzzer"),
        joints=_spark_joints(),
        has_legs=False,
        has_waist=True,
        description=(
            "Tabletop companion: head + arms + waist on a desk base. "
            "Buzzer for feedback sounds. AI tutor runs on laptop via Studio app."
        ),
    ),
    TierName.CORE: TierDefinition(
        name=TierName.CORE,
        display_name="Core",
        form_factor=FormFactor.MOBILE,
        compute="Raspberry Pi 5",
        bom_cost_usd=200,
        dof=10,
        sensors=("ultrasonic", "imu", "microphone", "speaker"),
        joints=_core_joints(),
        has_legs=False,
        has_waist=True,
        description=(
            "Enhanced companion: smart servos with feedback + compliance for "
            "teach-by-demo, elbows for richer gestures, IMU, voice AI (mic + speaker)."
        ),
    ),
    TierName.PRO: TierDefinition(
        name=TierName.PRO,
        display_name="Pro",
        form_factor=FormFactor.BIPEDAL,
        compute="Raspberry Pi 5",
        bom_cost_usd=400,
        dof=21,
        sensors=("ultrasonic", "imu", "camera", "microphone", "speaker_hq", "temperature"),
        joints=_pro_joints(),
        has_legs=True,
        has_waist=True,
        description=(
            "Full bipedal humanoid: 21 DOF, camera, high-quality voice (mic array + "
            "40mm speaker), walking, computer vision, full curriculum."
        ),
    ),
}


def get_tier(name: str | TierName) -> TierDefinition:
    """Look up a tier by name string or enum."""
    if isinstance(name, str):
        name = TierName(name.lower())
    return TIERS[name]


# Mock tier mirrors Spark layout for simulation but enables all sensors
MOCK_TIER = TierDefinition(
    name=TierName.MOCK,
    display_name="Mock (Simulation)",
    form_factor=FormFactor.TABLETOP,
    compute="Local machine",
    bom_cost_usd=0,
    dof=5,
    sensors=("ultrasonic", "imu", "camera", "microphone", "speaker", "temperature"),
    joints=_spark_joints(),
    has_legs=False,
    has_waist=True,
    description="Simulation mode — all sensors available, Spark joint layout",
)
