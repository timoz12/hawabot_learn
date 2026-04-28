# HawaBot Spark Skeleton — Mechanical Frame Specification

The skeleton is a **standalone mechanical frame** — a functional robot that moves on its own. Custom character shells snap on via magnets. This spec defines the frame only. See `INTERFACE_SPEC.md` for how shells attach and `SHELL_PIPELINE_SPEC.md` for the customer workflow.

---

## Design Principles

1. **The skeleton is a complete robot.** Power it up, it moves. No shell required.
2. **One skeleton, infinite characters.** Shells are swappable — same frame, different look.
3. **Fixed size, humanoid proportions.** Optimized for action-figure scale (~150mm). Future variants (stumpy/creature) are separate skeleton designs.
4. **Magnets everywhere, use what you need.** The frame has more magnet seats than any single shell requires. Software picks the best subset per character.

---

## Fixed Dimensions — Spark Skeleton v1

**Target height:** 200mm (base bottom to top of head servo stack)
**Proportion:** Humanoid action figure (head ~1/4 height, shoulders at ~2/3 height)

### Coordinate System

- Origin: center of base plate top surface
- +Z up, +X right (robot's perspective), +Y forward
- All dimensions in millimeters

---

## Bill of Materials

| Component | Qty | Purpose |
|---|---|---|
| SG90 Micro Servo | 3 | Waist yaw, head pan, head tilt |
| MG90S Metal Gear Servo | 2 | Left shoulder, right shoulder |
| Raspberry Pi Pico W | 1 | Controller |
| 6×3mm Neodymium Disc Magnets | ~40 | Shell attachment (skeleton side) |
| M2×5mm Self-Tapping Screws | ~20 | Servo mounting, structural |
| 3D Printed Frame (PLA/PETG) | 1 | Structural body |

---

## Component Dimensions

### SG90 Micro Servo (×3: waist, head pan, head tilt)

| Dimension | Value | Symbol |
|---|---|---|
| Body L (front-back) | 22.7 mm | `SG90_L` |
| Body W (side-side) | 12.2 mm | `SG90_W` |
| Body H (bottom to case top) | 27.0 mm | `SG90_H` |
| Overall H (bottom to spline top) | 32.3 mm | `SG90_H_total` |
| Tab-to-tab length | 32.3 mm | `SG90_tab_L` |
| Tab thickness | 2.8 mm | `SG90_tab_T` |
| Tab underside from bottom | 17.0 mm | `SG90_tab_Z` |
| Mounting hole ⌀ | 2.0 mm | `SG90_hole_D` |
| Mounting hole inset from tab edge | 2.0 mm | `SG90_hole_inset` |
| Shaft center from front face | 6.2 mm | `SG90_shaft_offset` |
| Spline OD | 4.8 mm | `SG90_spline_OD` |
| Turret height above body | 5.96 mm | `SG90_turret_H` |
| Turret ⌀ | 11.8 mm | `SG90_turret_D` |
| Weight | 9 g | — |

### MG90S Metal Gear Servo (×2: shoulders)

| Dimension | Value | Symbol |
|---|---|---|
| Body L | 22.8 mm | `MG90S_L` |
| Body W | 12.4 mm | `MG90S_W` |
| Body H | 28.4 mm | `MG90S_H` |
| Overall H | 32.5 mm | `MG90S_H_total` |
| Tab-to-tab length | 32.1 mm | `MG90S_tab_L` |
| Tab thickness | 2.8 mm | `MG90S_tab_T` |
| Tab underside from bottom | 18.5 mm | `MG90S_tab_Z` |
| Mounting hole ⌀ | 2.0 mm | `MG90S_hole_D` |
| Spline OD | 4.8 mm | `MG90S_spline_OD` |
| Weight | 13.4 g | — |

### Raspberry Pi Pico W

| Dimension | Value | Symbol |
|---|---|---|
| Board L | 51 mm | `PICO_L` |
| Board W | 21 mm | `PICO_W` |
| Board thickness | 1 mm | `PICO_T` |
| Component height (total) | 3.9 mm | `PICO_H_component` |
| Mounting hole ⌀ | 2.1 mm | `PICO_hole_D` |
| Mounting hole spacing (L) | 47.0 mm | `PICO_hole_L` |
| Mounting hole spacing (W) | 11.4 mm | `PICO_hole_W` |
| Hole center from short edge | 2.0 mm | `PICO_hole_edge` |

### 6×3mm Neodymium Disc Magnet

| Dimension | Value | Symbol |
|---|---|---|
| Diameter | 6.0 mm | `MAG_D` |
| Height | 3.0 mm | `MAG_H` |
| Pocket ⌀ (press-fit) | 6.1 mm | `MAG_POCKET_D` |
| Pocket depth | 3.1 mm | `MAG_POCKET_H` |
| Pull force (each) | ~0.5 kg | — |

---

## Frame Assembly Layout

```
                    ┌─────┐
                    │TILT │ SG90  Z=148   shaft→+Y (nod)
                    │ SRV │
                    ├─────┤
                    │ PAN │ SG90  Z=120   shaft→+Z (yaw)
                    │ SRV │
    ┌───────┐       ├─────┤       ┌───────┐
    │ L ARM │ MG90S │     │ MG90S │ R ARM │
    │  SRV  │ Z=110 │     │ Z=110 │  SRV  │
    └───┤   │ X=-40 │     │ X=+40 │   ├───┘
        │   │       │TORSO│       │   │
        │horn       │COLUMN       │horn
                    │  ⌀24│
                    ├─────┤
                    │WAIST│ SG90  Z=10    shaft→+Z (yaw)
                    │ SRV │
              ══════╧═════╧══════
              │     BASE PLATE    │  90×70×20mm
              │  ┌──────────────┐ │
              │  │  Pi Pico W   │ │  Z=-4 (inside base)
              │  │  (X=+25)     │ │
              │  └──────────────┘ │
              └───────────────────┘
```

### Servo Positions

| Servo | Center Position | Orientation | Joint |
|---|---|---|---|
| Waist | (0, 0, 10) | Shaft +Z | Yaw — rotates upper body |
| Left shoulder | (-40, 0, 110) | Shaft -X (outward) | Pitch — raise/lower arm |
| Right shoulder | (40, 0, 110) | Shaft +X (outward) | Pitch — raise/lower arm |
| Head pan | (0, 0, 120) | Shaft +Z | Yaw — turn head L/R |
| Head tilt | (0, 0, 148) | Shaft +Y (forward) | Pitch — nod head |

### Joint Ranges

| Joint | Axis | Range | Notes |
|---|---|---|---|
| Waist yaw | Z | ±90° | Full left/right body rotation |
| Left shoulder pitch | X | ±90° | Arm up/down |
| Right shoulder pitch | X | ±90° | Arm up/down |
| Head pan | Z | ±90° | Head turn left/right |
| Head tilt | Y | -30° to +30° | Head nod up/down |

---

## Structural Frame

The frame is 3D printed as a **single part** (not sectioned — the skeleton doesn't split). Only the cosmetic shells are split into body zones.

### Base Plate

| Parameter | Value | Notes |
|---|---|---|
| Width | 90 mm | Stability footprint |
| Depth | 70 mm | |
| Height | 20 mm | Contains Pico cavity (12mm) + 5mm floor + 3mm top |
| Corner radius | 6 mm | |
| Pico cavity | 57×25×12 mm | Centered at X=+25, cut from bottom |
| USB slot | 14mm wide | Extends from Pico cavity to +X edge |

### Torso Column

| Parameter | Value | Notes |
|---|---|---|
| Cross-section | ⌀24mm (or 24×24 rounded rect) | Central post |
| Height | Z=0 to Z=120 | Base surface to head pan |
| Wire channel | ⌀6mm, offset from center | Runs full height |

### Servo Mounting

Each servo is held by its mounting tabs — two M2 screws through the tab holes into screw bosses printed into the frame. The frame provides:

- **Tab ledge:** horizontal shelf the tab rests on
- **Screw bosses:** cylindrical posts (⌀4mm, with ⌀2mm pilot hole) rising from the ledge
- **Body pocket:** cavity matching servo body dimensions + 0.3mm clearance per side
- **Turret clearance:** open space above servo for turret + shaft + horn rotation
- **Cable exit:** slot in pocket wall for servo wire to reach wire channel

---

## Magnet Grid — Skeleton Side

The skeleton has magnet seats at **predefined positions** on its outer surfaces. Not all are used for every shell — the software selects the optimal subset per character design.

Magnets are press-fit into ⌀6.1mm × 3.1mm pockets printed into the frame surface. **Polarity matters** — all skeleton magnets in a given zone face the same way (N-out) so any matching shell magnet (S-out) will attract.

### Head Zone Magnets

Ring of seats around the neck post, just above the head pan servo. Shells drop over this ring.

| ID | Position | Notes |
|---|---|---|
| H1 | (0, -14, 125) | Front |
| H2 | (0, +14, 125) | Back |
| H3 | (-14, 0, 125) | Left |
| H4 | (+14, 0, 125) | Right |
| H5 | (-10, -10, 125) | Front-left |
| H6 | (+10, -10, 125) | Front-right |
| H7 | (-10, +10, 125) | Back-left |
| H8 | (+10, +10, 125) | Back-right |

**8 positions**, ring radius ≈14mm at Z=125 (just above pan servo top, below tilt servo).

### Torso Zone Magnets

Distributed around the torso column surface. Shells wrap around this.

| ID | Position | Notes |
|---|---|---|
| T1 | (0, -14, 30) | Front, lower |
| T2 | (0, +14, 30) | Back, lower |
| T3 | (0, -14, 70) | Front, mid |
| T4 | (0, +14, 70) | Back, mid |
| T5 | (0, -14, 100) | Front, upper |
| T6 | (0, +14, 100) | Back, upper |
| T7 | (-14, 0, 30) | Left, lower |
| T8 | (+14, 0, 30) | Right, lower |
| T9 | (-14, 0, 70) | Left, mid |
| T10 | (+14, 0, 70) | Right, mid |
| T11 | (-14, 0, 100) | Left, upper |
| T12 | (+14, 0, 100) | Right, upper |

**12 positions**, 3 rings of 4 along torso height.

### Left Arm Zone Magnets

On the arm housing outer surface. Shell sleeve slides over.

| ID | Position | Notes |
|---|---|---|
| LA1 | (-40, -10, 110) | Front |
| LA2 | (-40, +10, 110) | Back |
| LA3 | (-40, 0, 100) | Bottom |
| LA4 | (-40, 0, 120) | Top |
| LA5 | (-52, -8, 110) | Outer front |
| LA6 | (-52, +8, 110) | Outer back |

**6 positions** per arm.

### Right Arm Zone Magnets

Mirror of left arm across YZ plane.

| ID | Position | Notes |
|---|---|---|
| RA1–RA6 | Mirror of LA1–LA6 at +X | Same layout, mirrored |

### Base Zone Magnets

Around the base plate rim. Base cover snaps onto bottom/sides.

| ID | Position | Notes |
|---|---|---|
| B1 | (-35, -28, -10) | Front-left |
| B2 | (+35, -28, -10) | Front-right |
| B3 | (-35, +28, -10) | Back-left |
| B4 | (+35, +28, -10) | Back-right |
| B5 | (0, -28, -10) | Front-center |
| B6 | (0, +28, -10) | Back-center |
| B7 | (-40, 0, -10) | Left-center |
| B8 | (+40, 0, -10) | Right-center |

**8 positions** around the base perimeter at Z=-10 (midway down the base plate side).

### Magnet Summary

| Zone | Count | Total |
|---|---|---|
| Head | 8 | 8 |
| Torso | 12 | 12 |
| Left Arm | 6 | 6 |
| Right Arm | 6 | 6 |
| Base | 8 | 8 |
| **Total** | | **40** |

---

## Wire Routing

| Route | Path | Channel ⌀ |
|---|---|---|
| Pico → Waist servo | Through base plate, up to waist | 6mm |
| Waist → Torso | Vertical channel in torso column | 6mm |
| Torso → Left shoulder | Horizontal branch at Z=110 | 6mm |
| Torso → Right shoulder | Horizontal branch at Z=110 | 6mm |
| Torso → Head pan | Vertical channel continues to Z=120 | 6mm |
| Head pan → Head tilt | Short run between stacked servos | 4mm |

All servo cables route to the Pico's GPIO pins inside the base. Total cable count: 5 servos × 3 wires = 15 wires, bundled into the 6mm channels.

---

## Fabrication Notes

- **Print orientation:** Base plate flat on bed, torso column vertical
- **Material:** PLA for prototyping, PETG for production (better layer adhesion for screw bosses)
- **Layer height:** 0.2mm
- **Infill:** 30% for structural areas, 100% for screw boss zones
- **Supports:** Needed for shoulder overhangs and horizontal wire channels
- **Magnet insertion:** Press-fit during print (pause at magnet pocket layer) or glue after
- **Servo installation:** Drop servos into pockets, secure with M2 screws through tabs

---

## CadQuery Generation

Run `python3 pipeline/generate_skeleton_step.py` (requires CadQuery) to generate the frame as a STEP file for import into SolidWorks or any CAD tool.

The generated file is at `pipeline/skeleton_exports/hawabot_spark_skeleton.step`.

---

## Future Skeleton Variants

| Variant | Use Case | Key Differences |
|---|---|---|
| **Spark Humanoid** (this doc) | Action figures, human characters | Standard proportions |
| **Spark Stumpy** | Dragons, animals, creatures | Wider base, shorter torso, 4 limb mounts |
| **Core Humanoid** | Larger/more capable | STS3215 servos, elbows, Pi 5 |
