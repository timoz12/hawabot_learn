"""Check whether a T-pose character mesh aligns with the skeleton joints.

Drops a character through the same load_and_prepare() the pipeline uses,
then measures its anatomy (armspan, shoulder height, neck, hip) and compares
against the skeleton's fixed joint positions and dissection cut planes.

This answers: if I download this T-pose mesh, will the pipeline's cuts land
in the right places, or do I need to adapt the cuts / re-proportion the model?

Usage:
    python -m pipeline.check_alignment path/to/character.stl
"""

from __future__ import annotations

import sys

import numpy as np
import trimesh

from pipeline.shell_pipeline import load_and_prepare
from pipeline.skeleton import (
    DEFAULT_CUT_PLANES,
    FRAME_CHEST_BOTTOM_Z,
    HAND_X,
    HEAD_TOP_Z,
    SHOULDER_X,
    SHOULDER_Z,
    TOTAL_HEIGHT,
    BASE_H,
)


def _span_at_z(verts: np.ndarray, z: float, dz: float = 4.0) -> float:
    """Max |X| of vertices within a horizontal slab at height z."""
    m = (verts[:, 2] >= z - dz) & (verts[:, 2] <= z + dz)
    if not m.any():
        return 0.0
    return float(np.abs(verts[m, 0]).max())


def _detect_shoulder(verts: np.ndarray, zlo: float, zhi: float) -> tuple[float, float]:
    """Find the height in the upper body where horizontal span peaks.

    For a T-pose figure this is the shoulder/arm line.
    """
    zs = np.linspace(zlo + 0.45 * (zhi - zlo), zhi, 80)
    best_z, best_w = zs[0], 0.0
    for z in zs:
        w = _span_at_z(verts, z)
        if w > best_w:
            best_z, best_w = z, w
    return float(best_z), float(best_w)


def _flag(ok: bool) -> str:
    return "OK  " if ok else "MISS"


def check(path: str) -> bool:
    mesh = load_and_prepare(path)
    v = mesh.vertices
    b = mesh.bounds
    height = b[1][2] - b[0][2]

    print(f"\nMesh: {path}")
    print(f"  After load_and_prepare (scaled to {TOTAL_HEIGHT:.0f}mm tall):")
    print(f"    X[{b[0][0]:6.1f}, {b[1][0]:6.1f}]  "
          f"Y[{b[0][1]:6.1f}, {b[1][1]:6.1f}]  "
          f"Z[{b[0][2]:6.1f}, {b[1][2]:6.1f}]  (h={height:.0f})")

    armspan = float(np.abs(v[:, 0]).max())
    sh_z, sh_w = _detect_shoulder(v, b[0][2], b[1][2])

    print("\n  Anatomy vs skeleton:")
    print(f"    armspan (max|X|)      : {armspan:6.1f}mm   "
          f"skeleton shoulder X={SHOULDER_X:.0f}, hand X={HAND_X:.0f}  "
          f"[{_flag(armspan >= SHOULDER_X)}] arms reach the X={SHOULDER_X:.0f} cut")
    print(f"    shoulder line height  : Z={sh_z:6.1f}     "
          f"skeleton shoulder Z={SHOULDER_Z:.0f}  "
          f"[{_flag(abs(sh_z - SHOULDER_Z) <= 15)}] within 15mm of Z={SHOULDER_Z:.0f}")
    print(f"    skeleton head top     : Z={HEAD_TOP_Z:.0f}        "
          f"mesh top Z={b[1][2]:.0f}  "
          f"[{_flag(abs(b[1][2] - HEAD_TOP_Z) <= 15)}] skeleton reaches mesh crown "
          f"(gap {b[1][2] - HEAD_TOP_Z:.0f}mm)")

    print("\n  Cut planes (does geometry exist where we cut?):")
    all_cuts_ok = True
    for cp in DEFAULT_CUT_PLANES:
        if cp.axis == "X":
            side = v[:, 0] >= cp.position if cp.position > 0 else v[:, 0] <= cp.position
            has_outboard = bool(side.any())
            n = int(side.sum())
            ok = has_outboard
            print(f"    {cp.name:11s} X={cp.position:6.1f}  "
                  f"verts beyond cut: {n:6d}  [{_flag(ok)}]")
        else:  # Z cut
            above = bool((v[:, 2] > cp.position).any())
            below = bool((v[:, 2] < cp.position).any())
            ok = above and below
            print(f"    {cp.name:11s} Z={cp.position:6.1f}  "
                  f"geometry above={above} below={below}  [{_flag(ok)}]")
        all_cuts_ok = all_cuts_ok and ok

    # ── Adaptive dissection (what the pipeline now actually does) ───────
    from pipeline.landmarks import detect_landmarks, adaptive_cut_planes
    lm = detect_landmarks(mesh)
    print("\n  Adaptive dissection (character-driven cuts):")
    print(f"    shoulder line Z={lm.shoulder_z:6.1f}   neck Z={lm.neck_z:6.1f}   "
          f"hip Z={lm.hip_z:6.1f}")
    print(f"    torso half-width {lm.torso_half_width:5.1f}   armspan {lm.armspan:6.1f}   "
          f"arm cut X=±{lm.arm_cut_x:.1f}")
    print(f"    has_arms={lm.has_arms}   has_legs={lm.has_legs}")
    for cp in adaptive_cut_planes(mesh):
        print(f"      cut {cp.name:11s} {cp.axis}={cp.position:7.1f}")
    if not lm.has_arms:
        print("    ! arms not spread — arm zones will be thin strips (mesh is not T-pose)")

    skel_h = HEAD_TOP_Z + BASE_H  # base bottom (-BASE_H) to head top
    print("\n  Scale note:")
    print(f"    skeleton spans ~{skel_h:.0f}mm (base bottom -> head top Z={HEAD_TOP_Z:.0f}), "
          f"character scaled to {TOTAL_HEIGHT:.0f}mm")
    if abs(skel_h - TOTAL_HEIGHT) > 20:
        print(f"    -> {TOTAL_HEIGHT - skel_h:.0f}mm of the character has NO skeleton inside it. "
              f"STEP v1 is upper-body only (legs future).")

    verdict = all_cuts_ok and armspan >= SHOULDER_X
    print(f"\n  VERDICT: {'cuts will populate all zones' if verdict else 'some zones will be EMPTY — not aligned'}\n")
    return verdict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.check_alignment <character.stl>")
        sys.exit(1)
    ok = True
    for p in sys.argv[1:]:
        ok = check(p) and ok
    sys.exit(0 if ok else 1)
