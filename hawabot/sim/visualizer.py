"""2D skeleton visualizer using matplotlib.

Supports both tabletop (no legs) and bipedal form factors.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hawabot.sim.engine import SimulationEngine


_HEAD_RADIUS = 0.12
_UPPER_ARM = 0.25
_LOWER_ARM = 0.2
_UPPER_LEG = 0.3
_LOWER_LEG = 0.25
_SHOULDER_WIDTH = 0.2
_TORSO_HEIGHT = 0.35
_BASE_WIDTH = 0.3
_BASE_HEIGHT = 0.08


def _deg_to_rad(d: float) -> float:
    return d * math.pi / 180.0


def compute_skeleton_points(
    angles: dict[str, float], has_legs: bool = False
) -> dict[str, tuple[float, float]]:
    """Compute 2D (x, y) positions for key body points given current joint angles."""

    waist_yaw = angles.get("waist_yaw", 0.0)
    waist_offset = 0.15 * math.sin(_deg_to_rad(waist_yaw))

    if has_legs:
        torso_bottom = (0.0, 0.0)
    else:
        # Tabletop: base sits at bottom, torso rises from it
        torso_bottom = (waist_offset * 0.5, -0.3)

    torso_top = (torso_bottom[0] + waist_offset, torso_bottom[1] + _TORSO_HEIGHT)

    # Head
    head_pan = angles.get("head_pan", 0.0)
    head_tilt = angles.get("head_tilt", 0.0)
    head_center = (
        torso_top[0] + 0.08 * math.sin(_deg_to_rad(head_pan)),
        torso_top[1] + _HEAD_RADIUS + 0.02 + 0.04 * math.sin(_deg_to_rad(-head_tilt)),
    )

    # Shoulders
    left_shoulder = (torso_top[0] - _SHOULDER_WIDTH, torso_top[1])
    right_shoulder = (torso_top[0] + _SHOULDER_WIDTH, torso_top[1])

    # Arms
    def arm_endpoint(shoulder: tuple[float, float], side: str):
        pitch = angles.get(f"{side}_shoulder_pitch", 0.0)
        roll = angles.get(f"{side}_shoulder_roll", 0.0)
        sign = -1 if side == "left" else 1

        arm_angle = -90 + pitch * 0.7 + roll * 0.3 * sign
        rad = _deg_to_rad(arm_angle)
        elbow_pt = (
            shoulder[0] + _UPPER_ARM * math.cos(rad),
            shoulder[1] + _UPPER_ARM * math.sin(rad),
        )

        elbow_angle = angles.get(f"{side}_elbow", 0.0)
        forearm_rad = rad + _deg_to_rad(elbow_angle * 0.5)
        hand_pt = (
            elbow_pt[0] + _LOWER_ARM * math.cos(forearm_rad),
            elbow_pt[1] + _LOWER_ARM * math.sin(forearm_rad),
        )
        return elbow_pt, hand_pt

    left_elbow, left_hand = arm_endpoint(left_shoulder, "left")
    right_elbow, right_hand = arm_endpoint(right_shoulder, "right")

    points = {
        "torso_top": torso_top,
        "torso_bottom": torso_bottom,
        "head_center": head_center,
        "left_shoulder": left_shoulder,
        "right_shoulder": right_shoulder,
        "left_elbow": left_elbow,
        "left_hand": left_hand,
        "right_elbow": right_elbow,
        "right_hand": right_hand,
    }

    if not has_legs:
        # Tabletop base
        base_center = (torso_bottom[0], torso_bottom[1] - _BASE_HEIGHT)
        points["base_left"] = (base_center[0] - _BASE_WIDTH, base_center[1])
        points["base_right"] = (base_center[0] + _BASE_WIDTH, base_center[1])
        points["base_center"] = base_center
    else:
        # Legs
        hip_width = _SHOULDER_WIDTH * 0.5
        left_hip = (torso_bottom[0] - hip_width, torso_bottom[1])
        right_hip = (torso_bottom[0] + hip_width, torso_bottom[1])

        def leg_endpoint(hip, side):
            pitch = angles.get(f"{side}_hip_pitch", 0.0)
            knee_a = angles.get(f"{side}_knee", 0.0)
            leg_rad = _deg_to_rad(-90 + pitch)
            knee_pt = (
                hip[0] + _UPPER_LEG * math.cos(leg_rad),
                hip[1] + _UPPER_LEG * math.sin(leg_rad),
            )
            lower_rad = leg_rad + _deg_to_rad(knee_a * 0.5)
            foot_pt = (
                knee_pt[0] + _LOWER_LEG * math.cos(lower_rad),
                knee_pt[1] + _LOWER_LEG * math.sin(lower_rad),
            )
            return knee_pt, foot_pt

        left_knee, left_foot = leg_endpoint(left_hip, "left")
        right_knee, right_foot = leg_endpoint(right_hip, "right")
        points.update({
            "left_hip": left_hip, "right_hip": right_hip,
            "left_knee": left_knee, "left_foot": left_foot,
            "right_knee": right_knee, "right_foot": right_foot,
        })

    return points


def render_to_ascii(engine: SimulationEngine, width: int = 50, height: int = 20) -> str:
    """Render a simple ASCII skeleton for terminal output."""
    has_legs = engine._tier.has_legs
    points = compute_skeleton_points(engine.joint_angles, has_legs)

    canvas = [[" "] * width for _ in range(height)]

    def plot(x: float, y: float, char: str = "*") -> None:
        cx = int((x + 1.0) / 2.0 * (width - 1))
        cy = int((1.0 - (y + 1.0) / 2.0) * (height - 1))
        if 0 <= cx < width and 0 <= cy < height:
            canvas[cy][cx] = char

    def draw_line(p1, p2, char="|"):
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            x = p1[0] + t * (p2[0] - p1[0])
            y = p1[1] + t * (p2[1] - p1[1])
            plot(x, y, char)

    # Draw body
    draw_line(points["torso_top"], points["torso_bottom"], "|")
    draw_line(points["left_shoulder"], points["right_shoulder"], "-")
    draw_line(points["left_shoulder"], points["left_elbow"], "/")
    draw_line(points["left_elbow"], points["left_hand"], "/")
    draw_line(points["right_shoulder"], points["right_elbow"], "\\")
    draw_line(points["right_elbow"], points["right_hand"], "\\")
    plot(*points["head_center"], "O")

    if not has_legs and "base_left" in points:
        draw_line(points["base_left"], points["base_right"], "=")
        draw_line(points["torso_bottom"], points["base_center"], "|")
    elif has_legs:
        draw_line(points["left_hip"], points["left_knee"], "/")
        draw_line(points["left_knee"], points["left_foot"], "/")
        draw_line(points["right_hip"], points["right_knee"], "\\")
        draw_line(points["right_knee"], points["right_foot"], "\\")

    return "\n".join("".join(row) for row in canvas)


def show(engine: SimulationEngine) -> None:
    """Display the robot skeleton using matplotlib (requires hawabot[sim])."""
    try:
        import matplotlib.patches as patches
        import matplotlib.pyplot as plt
    except ImportError:
        print(render_to_ascii(engine))
        print("\nInstall matplotlib for graphical view: pip install hawabot[sim]")
        return

    has_legs = engine._tier.has_legs
    points = compute_skeleton_points(engine.joint_angles, has_legs)
    fig, ax = plt.subplots(1, 1, figsize=(6, 8))

    if has_legs:
        ax.set_ylim(-1.2, 1.0)
    else:
        ax.set_ylim(-0.8, 0.8)
    ax.set_xlim(-1, 1)
    ax.set_aspect("equal")
    form = engine._tier.form_factor.value
    ax.set_title(f"HawaBot — {engine.dof} DOF ({form})")
    ax.grid(True, alpha=0.3)

    # Head
    hc = points["head_center"]
    head = patches.Circle(hc, _HEAD_RADIUS, fill=False, linewidth=2, color="#3B82F6")
    ax.add_patch(head)

    # Body segments
    segments = [
        ("torso_top", "torso_bottom", "#333"),
        ("left_shoulder", "right_shoulder", "#333"),
        ("left_shoulder", "left_elbow", "#3B82F6"),
        ("left_elbow", "left_hand", "#3B82F6"),
        ("right_shoulder", "right_elbow", "#3B82F6"),
        ("right_elbow", "right_hand", "#3B82F6"),
    ]

    if not has_legs and "base_left" in points:
        segments.append(("torso_bottom", "base_center", "#666"))
        segments.append(("base_left", "base_right", "#666"))
    elif has_legs:
        for side_color in [("left", "#EF4444"), ("right", "#EF4444")]:
            side, color = side_color
            segments.append((f"{side}_hip", f"{side}_knee", color))
            segments.append((f"{side}_knee", f"{side}_foot", color))

    for p1_name, p2_name, color in segments:
        if p1_name in points and p2_name in points:
            p1, p2 = points[p1_name], points[p2_name]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=2.5)

    # Joint dots
    for name, pt in points.items():
        if name not in ("head_center", "base_center", "base_left", "base_right"):
            ax.plot(pt[0], pt[1], "o", color="#666", markersize=5)

    # Base platform for tabletop
    if not has_legs and "base_left" in points:
        bl = points["base_left"]
        br = points["base_right"]
        base = patches.FancyBboxPatch(
            (bl[0], bl[1] - 0.03), br[0] - bl[0], 0.06,
            boxstyle="round,pad=0.02", facecolor="#94A3B8", edgecolor="#475569",
            linewidth=2,
        )
        ax.add_patch(base)

    plt.tight_layout()
    plt.show()
