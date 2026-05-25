# HawaBot SolidWorks Cowork — Context & Reference

_Use this document when working with Claude on the SolidWorks machine. It provides the full hardware context so Claude can make informed design decisions._

_Last updated: 2026-05-12_

---

## Product Overview

HawaBot is a character-driven physical AI robotics platform for ages 12-15. Students build a humanoid robot and learn systems engineering. The robot body (servos, sensors, frame) is controlled by an ESP32-S3. AI runs on the student's phone/tablet via WiFi.

---

## Tiers (What You're Designing For)

| | Spark ($199) | Pro ($599) | Max ($999+, future) |
|---|---|---|---|
| Size | **250mm** | **250mm** (same skeleton) | 400-500mm (separate) |
| DOF | 7 | 19 | 19+ |
| Legs | No (flat base) | Yes (walking biped) | Yes |
| Arms | Shoulder pitch + roll | + elbows + hands | Full articulation |
| Power | USB-C (wall) | Battery (7.4V 2S LiPo) | Battery (11.1V 3S) |
| Compute | ESP32-S3 | ESP32-S3 (same PCB) | Pi 5 / CM5 |

**Spark and Pro share the same 250mm skeleton.** Pro adds legs, elbows, hands, sensors, and battery to the same frame. Design the Pro skeleton and Spark is a subset.

**Max is a separate, larger robot** — not upgrade-compatible with the 250mm frame.

---

## Servo Inventory

### Servo Dimensions (Critical for Pocket Design)

| Servo | Body (mm) | Shaft Side | Mount Holes | Weight |
|---|---|---|---|---|
| SG90 | 23.0 x 12.2 x 22.0 (excl tabs) | Single-sided, top | 2x tabs, 4.8mm hole spacing | 9g |
| MG90S | 22.8 x 12.0 x 22.5 (excl tabs) | Single-sided, top | 2x tabs, same as SG90 | 13.4g |
| XL330-M288-T | 20.0 x 34.0 x 26.0 | **Dual shaft** (front + back) | 4x M2 bolts, idler side | 18g |

### SG90/MG90S Pocket Dimensions
```
                ┌──────────┐
     tab ───────┤          ├─────── tab
     (4.6mm)    │  body    │       (4.6mm)
                │ 23x12mm  │
                │          │
                └────┬─────┘
                     │ shaft (horn side)
                     
Plan view:  body pocket = 23.5 x 12.5 mm (0.25mm clearance each side)
Tab pocket: full width = 32.5 mm (tab to tab)
Depth:      body depth = 23.0 mm
```

### XL330 with Idler Frame (FPX330-H101)
```
    idler side ◄── bearing + idler horn
    ┌──────────────────────┐
    │    XL330 body        │  34mm wide
    │    20 x 34 x 26mm    │
    └──────────────────────┘
    shaft side ──► output horn
    
The idler frame kit provides dual-shaft support.
Use at: shoulder pitch (L/R), all leg joints.
```

---

## Joint Allocation Table (19 DOF)

| # | Joint | Servo | Axis | Plane | Shaft Direction | Spark? | Pro? |
|---|---|---|---|---|---|---|---|
| 1 | head_pan | SG90 | AX_HEAD_PAN | PL_HEAD_PAN | Up (+Z) | Yes | Yes |
| 2 | head_tilt | SG90 | AX_HEAD_TILT | PL_HEAD_TILT | Out (+X) | Yes | Yes |
| 3 | L shoulder pitch | **XL330** | AX_SHOULDER_PITCH | PL_L_SHOULDER | Out (-X) | MG90S | XL330 |
| 4 | L shoulder roll | SG90 | AX_L_SHOULDER_ROLL | PL_L_SHOULDER | Forward (+Y) | Yes | Yes |
| 5 | R shoulder pitch | **XL330** | AX_SHOULDER_PITCH | PL_R_SHOULDER | Out (+X) | MG90S | XL330 |
| 6 | R shoulder roll | SG90 | AX_R_SHOULDER_ROLL | PL_R_SHOULDER | Forward (+Y) | Yes | Yes |
| 7 | waist_yaw | **XL330** | AX_WAIST_YAW | PL_WAIST_YAW | Up (+Z) | MG90S | XL330 |
| 8 | L elbow pitch | SG90 | AX_ELBOW_PITCH | PL_L_ELBOW | Out (-X) | — | Yes |
| 9 | R elbow pitch | SG90 | AX_ELBOW_PITCH | PL_R_ELBOW | Out (+X) | — | Yes |
| 10 | L hand pitch | SG90 | AX_HAND_PITCH | PL_L_HAND | Out (-X) | — | Yes |
| 11 | R hand pitch | SG90 | AX_HAND_PITCH | PL_R_HAND | Out (+X) | — | Yes |
| 12 | L hip yaw | XL330 | AX_L_HIP_YAW | PL_HIP | Up (+Z) | — | Yes |
| 13 | R hip yaw | XL330 | AX_R_HIP_YAW | PL_HIP | Up (+Z) | — | Yes |
| 14 | L hip pitch | XL330 | AX_HIP_PITCH | PL_L_HIP | Out (-X) | — | Yes |
| 15 | R hip pitch | XL330 | AX_HIP_PITCH | PL_R_HIP | Out (+X) | — | Yes |
| 16 | L knee pitch | XL330 | AX_KNEE_PITCH | PL_L_KNEE_X | Out (-X) | — | Yes |
| 17 | R knee pitch | XL330 | AX_KNEE_PITCH | PL_R_KNEE_X | Out (+X) | — | Yes |
| 18 | L ankle pitch | XL330 | AX_ANKLE_PITCH | PL_L_ANKLE_X | Out (-X) | — | Yes |
| 19 | R ankle pitch | XL330 | AX_ANKLE_PITCH | PL_R_ANKLE_X | Out (+X) | — | Yes |

**Note:** Pitch axes are shared L/R — one SW feature, both servos mate concentrically. The coincident plane distinguishes L vs R.

**Spark uses MG90S at shoulders and waist** (items 3, 5, 7). Pro upgrades these to XL330 for feedback + dual-shaft support. Design pockets that accommodate both — XL330 is the larger envelope.

### Servo Count Summary
| Servo | Count | Joints |
|---|---|---|
| SG90 | 8 | Head (2), shoulder roll (2), elbow (2), hand (2) |
| XL330 | 10 | Shoulder pitch (2), waist (1), hip (4), knee (2), ankle (2) |
| MG90S | 0 (Pro) / 3 (Spark) | Spark-only: shoulder pitch (2), waist (1) |
| **Total** | **18-19** | |

---

## Skeleton Geometry (v17 — Current)

### Key Coordinates (Z = vertical, X = lateral, Y = forward)

```
Head top:      Z = 210
Head tilt:     Z = 185
Head pan:      Z = 155
Shoulder:      Z = 140, X = ±40
Elbow:         Z = 100, X = ±75
Hand:          Z = 50,  X = ±55
Waist yaw:     Z = 15
Hip:           Z = 0,   X = ±20
Knee:          Z = -55
Ankle:         Z = -110
Foot bottom:   Z = -115
```

### Segment Lengths (Verified)
```
Torso gap (waist to shoulder):  125mm  ← Electronics + PCB live here
Upper arm (shoulder to elbow):   53mm
Forearm (elbow to hand):         54mm
Thigh (hip to knee):             55mm
Shin (knee to ankle):            55mm
Foot height:                      5mm
Total (foot to head top):       325mm
```

### Proportion Ratios
- Leg ratio: 35% of total height
- Arm ratio: 33% of total height
- Torso gap: 38% of total height (intentionally large for electronics)

---

## Electronics Placement

### Custom PCB (Lives in Torso Cavity)
- **Size:** ~60 x 40 x 8 mm
- **Location:** Inside torso, between waist (Z=15) and shoulders (Z=140) — 125mm gap
- **Integrates:** ESP32-S3-WROOM-1-N16R8, PCA9685, MAX98357A, power reg
- **Pro adds:** SPH0641LU4H-1 PDM mic, MPU6050 IMU, camera connector, FSR inputs, battery connector

### Speaker
- 28mm diameter x 12mm cylinder
- Mounts in torso cavity near PCB

### Battery (Pro Only)
- ~40 x 30 x 8 mm LiPo
- Mounts in torso cavity or base
- 7.4V 2S, 1000mAh

### Antenna Keep-Out
- ESP32-S3-WROOM-1-N16R8 antenna is at one end of the module
- **15mm keep-out zone** — no copper, no ground pour, no metal within 15mm of antenna
- Orient antenna toward shell opening or thin wall section

---

## SolidWorks Project Status

| Phase | Status | Description |
|---|---|---|
| 1. SSP (Skeleton Sketch Part) | **DONE** | v17 macro: 21 planes, 13 axes, KINEMATIC_LAYOUT sketch |
| 2. Verification | **DONE** | Geometry verified, Poppy-informed proportions confirmed |
| 3. Master Assembly | **NEXT** | Create assembly, insert SSP, fix at origin |
| 4. Servo Placement | TODO | Mate servos to axes/planes using mate table above |
| 5. Electronics | TODO | Place PCB, speaker, battery bounding boxes |
| 6. Kinematics Test | TODO | Motion studies, interference detection, safe range validation |

### Phase 3 Quick Start
1. File > New > Assembly (mmgs template)
2. Save As: `hawabot_pro_assembly.sldasm`
3. Insert Component: browse to `hawabot_skeleton_sketch.sldprt`, place at origin
4. Right-click part in tree > Fix (green pin)

### Phase 4 Mate Pattern (Per Servo)
1. **Concentric:** servo shaft axis → SSP axis (from table above)
2. **Coincident:** servo body face → SSP plane (from table above)
3. **Limit Mate:** angular range (from table above)

### STEP Files Needed
| File | Source | Status |
|---|---|---|
| SG90 | `sg90_reference.step` in this package | Ready |
| MG90S | `mg90s_reference.step` in this package | Ready |
| Magnet 6x3mm | `magnet_6x3_reference.step` in this package | Ready |
| XL330-M288-T | Robotis download page or GrabCAD | **Download before Phase 4** |
| FPX330-H101 idler | Robotis download page | **Download before Phase 4** |

---

## Design Constraints

### Shell System
- Character shells are **magnetic snap-on** cosmetic parts (5 zones: head, torso, L arm, R arm, base)
- 6x3mm N52 neodymium magnets (~20 per robot)
- Shell wall thickness: minimum 1mm, target 2-3mm
- Shells must clear all joint ranges of motion (joint clearance cuts in pipeline)

### Printing Constraints
- Material: PLA/PETG
- Minimum wall: 1mm
- No support material inside servo pockets (design for print-in-place or side-entry)
- All parts must be printable on 180x180mm bed (Bambu Lab A1 Mini)

### Mechanical
- SG90/MG90S are **cantilevered** (single shaft) — acceptable for low-load joints
- XL330 uses **idler frame** for dual-shaft support at high-load joints
- M2x5mm self-tapping screws for servo mounting
- Wire routing channels: minimum 4mm diameter for servo cables

---

## Files in This Package

| File | Purpose |
|---|---|
| `hawabot_ssp_macro_v17.bas` | VBA macro — creates full SSP (CANONICAL) |
| `hawabot_skeleton_sketch.SLDPRT` | Built SSP part file (Phase 1+2 validated) |
| `equations_250mm.txt` | Original equations (pre-v17, reference only) |
| `sg90_reference.step` | SG90 servo model |
| `mg90s_reference.step` | MG90S servo model |
| `magnet_6x3_reference.step` | Magnet cylinder reference |
| `COMPONENT_REFERENCE.md` | All component dimensions and clearances |
| `SOLIDWORKS_BUILD_GUIDE.md` | Full kinematic build instructions |
| `README_START_HERE.md` | Quick-start guide |
| `PARAMETRIC_PIPELINE_PLAN.md` | Pipeline strategy + full mate table + safe ranges |
| **SOLIDWORKS_CONTEXT.md** | **THIS FILE — cowork context reference** |
