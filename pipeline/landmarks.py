"""Detect anatomical landmarks on a T-pose character mesh.

The dissection cuts a character into zones (head, torso, arms, base/legs).
Rather than cutting at the skeleton's fixed joint positions — which only
works if the character happens to share the skeleton's proportions — we
detect the *character's own* landmarks and cut there:

    neck      -> head / torso boundary
    shoulder  -> the height where arms stick out (T-pose arm line)
    armpit    -> the |X| where arms separate from the torso
    hip/crotch-> torso / base (legs) boundary
    leg split -> X=0 between the two legs (if present)

This makes the pipeline work for any body type — humanoid, animal,
mystic creature — as long as it is in a T-pose. The chosen skeleton
variant (see SkeletonSpec) is then scaled to fit the detected zones.

All measurements assume the mesh has already been through
load_and_prepare(): Z-up, centered on X/Y, scaled to target height.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import trimesh

from pipeline.skeleton import CutPlane


@dataclass
class Landmarks:
    """Detected anatomical landmarks, in the prepared mesh's own coordinates (mm)."""
    bottom_z: float
    top_z: float
    height: float
    neck_z: float            # head / torso cut
    shoulder_z: float        # arm line height
    arm_cut_x: float         # |X| where arms separate from torso
    hip_z: float             # torso / base cut
    leg_split_x: float       # X between legs (≈0)
    torso_half_width: float  # core torso |X| below the arms
    armspan: float           # max |X| (fingertip to fingertip / 2 -> *2)
    has_arms: bool           # arms extend meaningfully past the torso
    has_legs: bool           # two separated legs detected below the hip


def _profile(verts: np.ndarray, nbins: int = 64) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (z_centers, half_width, center_clear) per horizontal slab.

    half_width[i]   : 97th-percentile |X| in slab i (robust outer extent)
    center_clear[i] : True if the slab has a hole near X=0 (two clusters)
    """
    z = verts[:, 2]
    x = verts[:, 0]
    bottom, top = float(z.min()), float(z.max())
    edges = np.linspace(bottom, top, nbins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    half_width = np.zeros(nbins)
    center_clear = np.zeros(nbins, dtype=bool)

    H = top - bottom
    gap_thresh = max(2.0, 0.05 * H)

    for i in range(nbins):
        m = (z >= edges[i]) & (z < edges[i + 1])
        n = int(m.sum())
        if n < 8:
            continue
        ax = np.abs(x[m])
        half_width[i] = float(np.percentile(ax, 97))
        # center hole: almost no geometry within gap_thresh of X=0
        near_center = int((ax < gap_thresh).sum())
        center_clear[i] = (near_center / n) < 0.01

    return centers, half_width, center_clear


def detect_landmarks(mesh: trimesh.Trimesh) -> Landmarks:
    v = np.asarray(mesh.vertices, dtype=float)
    z = v[:, 2]
    bottom, top = float(z.min()), float(z.max())
    H = top - bottom

    centers, hw, clear = _profile(v)
    armspan = float(np.percentile(np.abs(v[:, 0]), 99.5))

    # ── Shoulder line: widest slab in the upper ~55% of height ──────────
    upper = centers >= bottom + 0.45 * H
    if upper.any() and hw[upper].max() > 0:
        sh_idx = np.where(upper)[0][np.argmax(hw[upper])]
    else:
        sh_idx = int(np.argmax(hw))
    shoulder_z = float(centers[sh_idx])
    shoulder_hw = float(hw[sh_idx])

    # ── Torso core width: median half-width in the band below the arms ──
    core_band = (centers >= bottom + 0.30 * H) & (centers <= shoulder_z - 0.10 * H)
    core_vals = hw[core_band][hw[core_band] > 0]
    torso_half_width = float(np.median(core_vals)) if core_vals.size else shoulder_hw * 0.4

    # Arms exist only if the shoulder band is clearly wider than the torso
    has_arms = shoulder_hw > torso_half_width * 1.35
    arm_cut_x = torso_half_width * 1.12 if has_arms else max(armspan * 0.9, torso_half_width)

    # ── Neck: the pinch BETWEEN the shoulder line and the head bulge ────
    # First locate the head (widest slab above the shoulders), then take
    # the narrowest slab between shoulders and head — that's the neck.
    head_region = centers > shoulder_z + 0.05 * H
    if head_region.any() and hw[head_region].max() > 0:
        head_idx = np.where(head_region)[0][int(np.argmax(hw[head_region]))]
        head_z = float(centers[head_idx])
        between = (centers > shoulder_z) & (centers < head_z)
        bw = hw.copy()
        bw[~between] = np.inf
        bw[bw <= 0] = np.inf
        if np.isfinite(bw.min()):
            neck_z = float(centers[int(np.argmin(bw))])
        else:
            neck_z = (shoulder_z + head_z) / 2
    else:
        neck_z = shoulder_z + 0.06 * H
    neck_z = min(max(neck_z, shoulder_z + 0.02 * H), top - 0.01 * H)

    # ── Hip / crotch: highest slab in the lower half with a center hole ─
    # Require two consecutive "clear" slabs to avoid single-bin noise.
    lower_idx = np.where(centers <= bottom + 0.55 * H)[0]
    crotch_idx = None
    for i in lower_idx[::-1]:  # from high to low
        if clear[i] and i - 1 >= 0 and clear[i - 1]:
            crotch_idx = i
            break
    has_legs = crotch_idx is not None
    if has_legs:
        hip_z = float(centers[crotch_idx]) + 0.03 * H
    else:
        hip_z = bottom + 0.13 * H  # fallback: just above the base/stand
    hip_z = min(hip_z, shoulder_z - 0.05 * H)

    return Landmarks(
        bottom_z=bottom, top_z=top, height=H,
        neck_z=neck_z, shoulder_z=shoulder_z, arm_cut_x=arm_cut_x,
        hip_z=hip_z, leg_split_x=0.0,
        torso_half_width=torso_half_width, armspan=armspan,
        has_arms=has_arms, has_legs=has_legs,
    )


def adaptive_cut_planes(mesh: trimesh.Trimesh, pro: bool = False) -> list[CutPlane]:
    """Build cut planes from the character's own detected landmarks.

    Drop-in replacement for the fixed DEFAULT_CUT_PLANES. min/max give the
    UI a ±range to nudge each cut during guided dissection.
    """
    lm = detect_landmarks(mesh)
    pad = 0.04 * lm.height  # adjustable range around each cut

    planes = [
        CutPlane("head_torso", "Z", lm.neck_z,
                 lm.neck_z - pad, lm.neck_z + pad, ("head", "torso")),
        CutPlane("torso_base", "Z", lm.hip_z,
                 lm.hip_z - pad, lm.hip_z + pad, ("torso", "base")),
        CutPlane("left_arm", "X", -lm.arm_cut_x,
                 -lm.arm_cut_x - pad, -lm.arm_cut_x + pad, ("torso", "left_arm")),
        CutPlane("right_arm", "X", lm.arm_cut_x,
                 lm.arm_cut_x - pad, lm.arm_cut_x + pad, ("torso", "right_arm")),
    ]
    if pro and lm.has_legs:
        planes += [
            CutPlane("left_leg", "X", -lm.leg_split_x - 2, -10, 0, ("base", "left_leg")),
            CutPlane("right_leg", "X", lm.leg_split_x + 2, 0, 10, ("base", "right_leg")),
        ]
    return planes
