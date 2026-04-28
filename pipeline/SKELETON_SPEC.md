# HawaBot Spark Skeleton — Parametric SolidWorks Reference

This document defines every dimension needed to build the Spark skeleton in SolidWorks. The skeleton is exported as **separate STL bodies per section**, and each body defines both the internal cavity and the split boundary for the shell pipeline.

---

## Design Philosophy

The skeleton is the **subtract volume** — everything inside it gets carved out of the customer's character sculpture. It must include:
- Servo body cavities + clearance
- Mounting features (screw bosses, snap-fit clips)
- Wire channels between components
- Electronics bay
- Joint rotation clearance zones

Export as **5 separate STL files** (one per section). The shell pipeline subtracts each independently from the sculpture, so splits happen naturally at the boundaries.

---

## Output Files

```
skeleton_exports/
├── base_section.stl         → Base plate + Pi Pico + waist servo lower half
├── torso_section.stl        → Torso column + shoulder servo mounts
├── left_arm_section.stl     → Left arm servo housing + arm shaft
├── right_arm_section.stl    → Right arm servo housing + arm shaft
└── head_section.stl         → Head pan + tilt servo stack
```

---

## Global Parameters

| Parameter | Symbol | Value | Notes |
|---|---|---|---|
| Wall clearance (servo to shell) | `C_wall` | 0.3 mm | Tolerance between servo body and cavity wall |
| Shell min wall thickness | `T_wall` | 2.5 mm | Minimum printable wall |
| Wire channel diameter | `D_wire` | 6 mm | Fits 3-4 servo cables side by side |
| Screw hole diameter | `D_screw` | 2.0 mm | M2 screws throughout |
| Snap-fit clearance | `C_snap` | 0.2 mm | Between mating snap-fit surfaces |
| Target robot height | `H_total` | 150 mm | Adjustable — scale all Z values proportionally |
| Scale factor | `S` | 1.0 | Multiply all dimensions by S for different sizes |

---

## Component Dimensions

### SG90 Micro Servo (Head pan, head tilt, waist)

| Dimension | Value | CAD Variable |
|---|---|---|
| Body length (front-back) | 22.7 mm | `SG90_L` |
| Body width (side-side) | 12.2 mm | `SG90_W` |
| Body height (bottom to case top, no shaft) | 27.0 mm | `SG90_H` |
| Overall height (bottom to spline top) | 32.3 mm | `SG90_H_total` |
| Tab-to-tab length | 32.3 mm | `SG90_tab_L` |
| Tab thickness | 2.8 mm | `SG90_tab_T` |
| Tab underside height from bottom | 17.0 mm | `SG90_tab_Z` |
| Mounting hole diameter | 2.0 mm | `SG90_hole_D` |
| Mounting hole inset from tab edge | 2.0 mm | `SG90_hole_inset` |
| Shaft center from front face | 6.2 mm | `SG90_shaft_offset` |
| Shaft spline OD | 4.8 mm | `SG90_spline_OD` |
| Turret height above body | 5.96 mm | `SG90_turret_H` |
| Turret diameter | 11.8 mm | `SG90_turret_D` |
| Weight | 9 g | — |
| **Cavity size (body + clearance)** | **23.3 × 12.8 × 27.6 mm** | `SG90_L + 2*C_wall` etc. |

### MG90S Micro Servo (Left shoulder, right shoulder)

| Dimension | Value | CAD Variable |
|---|---|---|
| Body length (front-back) | 22.8 mm | `MG90S_L` |
| Body width (side-side) | 12.4 mm | `MG90S_W` |
| Body height (bottom to case top) | 28.4 mm | `MG90S_H` |
| Overall height (bottom to spline top) | 32.5 mm | `MG90S_H_total` |
| Tab-to-tab length | 32.1 mm | `MG90S_tab_L` |
| Tab thickness | 2.8 mm | `MG90S_tab_T` |
| Tab underside height from bottom | 18.5 mm | `MG90S_tab_Z` |
| Mounting hole diameter | 2.0 mm | `MG90S_hole_D` |
| Shaft spline OD | 4.8 mm | `MG90S_spline_OD` |
| Weight | 13.4 g | — |
| **Cavity size (body + clearance)** | **23.4 × 13.0 × 29.0 mm** | `MG90S_L + 2*C_wall` etc. |

### Raspberry Pi Pico W

| Dimension | Value | CAD Variable |
|---|---|---|
| Board length | 51 mm | `PICO_L` |
| Board width | 21 mm | `PICO_W` |
| Board thickness | 1 mm | `PICO_T` |
| Component height (total) | 3.9 mm | `PICO_H` |
| Mounting hole diameter | 2.1 mm | `PICO_hole_D` |
| Mounting hole spacing (length) | 47.0 mm | `PICO_hole_L` |
| Mounting hole spacing (width) | 11.4 mm | `PICO_hole_W` |
| Hole center from short edge | 2.0 mm | `PICO_hole_edge` |
| USB connector overhang | ~2 mm beyond board edge | — |
| **Cavity size (board + clearance + USB access)** | **58 × 25 × 12 mm** | Includes standoffs + cable access |

**Note:** Download the official STEP file from [raspberrypi.com/documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) and import into SolidWorks for exact geometry.

---

## Assembly Layout — Spark Skeleton

All coordinates relative to **center of base plate top surface**. +Z is up, +X is right (robot's perspective), +Y is forward.

```
                    HEAD TILT SERVO (SG90)
                    ┌───┐  Z = 93 mm
                    │   │
                    HEAD PAN SERVO (SG90)
                    ┌───┐  Z = 65 mm
                    │   │
    LEFT ARM ───────┤   ├─────── RIGHT ARM
    MG90S           │   │        MG90S
    Z = 55          │   │        Z = 55
    X = -35         │   │        X = +35
                    │   │  TORSO COLUMN
                    │   │
                    WAIST SERVO (SG90)
                    ┌───┐  Z = 5 mm
                    │   │
              ══════╧═══╧══════  BASE PLATE
                   Z = 0
              ┌─────────────────┐
              │   Pi Pico W     │
              │                 │
              └─────────────────┘
                   Z = -8 (inside base)
```

### Section Positions (Parametric)

| Parameter | Symbol | Default | Notes |
|---|---|---|---|
| **Base plate** | | | |
| Width | `BASE_W` | 80 mm | Stability footprint |
| Depth | `BASE_D` | 60 mm | |
| Height | `BASE_H` | 10 mm | Thick enough for Pi Pico + wiring |
| Corner radius | `BASE_R` | 5 mm | Rounded for aesthetics |
| | | | |
| **Waist servo** | | | |
| Center Z | `WAIST_Z` | 5 mm | Just above base surface |
| Orientation | — | Shaft pointing UP | Rotates upper body on base |
| | | | |
| **Torso column** | | | |
| Diameter | `TORSO_D` | 20 mm | Central structural post |
| Height | `TORSO_H` | 60 mm | From waist to shoulders |
| | | | |
| **Shoulders** | | | |
| Center Z | `SHOULDER_Z` | 55 mm | Height of shoulder joint axis |
| Spread (center to each) | `SHOULDER_X` | 35 mm | Distance from centerline |
| Orientation | — | Shaft pointing OUTWARD | Pitch axis for arm raise/lower |
| | | | |
| **Head servos** | | | |
| Pan servo Z | `HEAD_PAN_Z` | 65 mm | Top of torso |
| Pan orientation | — | Shaft pointing UP | Yaw rotation |
| Tilt servo Z | `HEAD_TILT_Z` | 93 mm | Stacked above pan |
| Tilt orientation | — | Shaft pointing FORWARD | Pitch rotation |
| | | | |
| **Total skeleton height** | `SKEL_H` | ~115 mm | Bottom of base to top of head tilt |

---

## Section Boundary Rules

Each section body should **overlap by 2mm** at the boundary with adjacent sections. This overlap creates the mating surface for assembly. The shell pipeline subtracts each section independently, so the 2mm overlap ensures no gap between shell pieces.

### base_section.stl
- **Contains:** Base plate + Pi Pico cavity + waist servo (lower half)
- **Boundary:** Top surface at Z = `WAIST_Z` + 15 mm (midpoint of waist servo)
- **Mating features:** Circular lip at top for torso section to sit into

### torso_section.stl
- **Contains:** Torso column + shoulder servo mounts (inner halves)
- **Boundary bottom:** Z = `WAIST_Z` + 13 mm (overlaps with base by 2mm)
- **Boundary top:** Z = `HEAD_PAN_Z` - 5 mm
- **Boundary left:** X = `-SHOULDER_X` + 10 mm (overlaps with left arm by 2mm)
- **Boundary right:** X = `SHOULDER_X` - 10 mm (overlaps with right arm by 2mm)
- **Wire channels:** Vertical channel from base to head, horizontal channels to each shoulder

### left_arm_section.stl
- **Contains:** Left shoulder servo housing + arm shaft tube
- **Boundary:** Inner face at X = `-SHOULDER_X` + 12 mm (overlaps with torso by 2mm)
- **Shaft tube:** Extends outward for the arm horn attachment
- **Rotation clearance:** Swept cylinder around shaft axis, radius = arm length

### right_arm_section.stl
- **Mirror of left_arm_section** across YZ plane

### head_section.stl
- **Contains:** Head pan servo + tilt servo stack + head mounting plate
- **Boundary:** Bottom surface at Z = `HEAD_PAN_Z` - 3 mm (overlaps with torso by 2mm)
- **Rotation clearance:** Annular ring around pan axis for head turning

---

## Joint Rotation Clearances

These are volumes that must be subtracted to allow joints to move. Include them in the appropriate section body.

| Joint | Axis | Range | Clearance Shape |
|---|---|---|---|
| Waist yaw | Z | ±90° | Annular ring, R_inner=15mm, R_outer=`BASE_W/2`, H=4mm, at Z = boundary |
| Head pan | Z | ±90° | Annular ring, R_inner=10mm, R_outer=20mm, H=4mm, at Z = boundary |
| Head tilt | Y | -30° to +30° | Sector cut, 60° arc, R=25mm, at tilt axis |
| Left shoulder | Y | ±90° | Sector cut, 180° arc, R=30mm, around shaft |
| Right shoulder | Y | ±90° | Sector cut, 180° arc, R=30mm, around shaft |

---

## Scaling Guide

To create Core or Pro skeletons from the Spark base:

| Change | Spark → Core | Spark → Pro |
|---|---|---|
| Servos | Replace SG90/MG90S with STS3215 | Replace with Dynamixel XL430/330 |
| Add elbows | Add STS3215 at X=±55, Z=45 | Add XL330 at X=±60, Z=45 |
| Add waist roll | — | Add XL430 below waist yaw |
| Add legs | — | Full leg assembly below base |
| Scale factor `S` | 1.2 | 1.5 |
| Compute | Replace Pico W cavity with Pi 5 | Same as Core |

For the STS3215 and Dynamixel servo dimensions, see `hawabot_reference/servo_mapping.json`.

---

## SolidWorks Tips

1. **Use a global variable table** for all parameters — makes resizing the skeleton a single spreadsheet edit
2. **Design each section as a separate body** in a multi-body part, or as separate parts in an assembly
3. **Export each section as a separate STL** using "Save Bodies" or "Save As > STL > Selected Bodies"
4. **Include 0.3mm clearance** around all servo bodies (servo should drop in without force)
5. **Fillet internal edges** at 1-2mm radius — prevents stress concentration during printing and makes assembly easier
6. **Test print the base_section first** — if the Pi Pico fits and the waist servo drops in cleanly, the tolerances are right
7. **Name bodies clearly** — `base_section`, `torso_section`, etc. — the pipeline uses filenames to identify sections
