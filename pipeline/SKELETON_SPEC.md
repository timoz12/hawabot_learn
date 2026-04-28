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

For the STS3215 and Dynamixel servo dimensions, see `docs/reference_robot/servo_mapping.json`.

---

## SolidWorks Step-by-Step Workflow

### Step 1: Create a New Part and Set Up Global Variables

1. Open SolidWorks → **File → New → Part**
2. Go to **Tools → Equations** (or click the Σ icon in the toolbar)
3. Click **"Add"** and enter each parameter from the tables above as a global variable:

```
"C_wall" = 0.3
"T_wall" = 2.5
"D_wire" = 6
"D_screw" = 2.0
"S" = 1.0
"BASE_W" = 80
"BASE_D" = 60
"BASE_H" = 10
"BASE_R" = 5
"TORSO_D" = 20
"TORSO_H" = 60
"WAIST_Z" = 5
"SHOULDER_Z" = 55
"SHOULDER_X" = 35
"HEAD_PAN_Z" = 65
"HEAD_TILT_Z" = 93
"SG90_L" = 22.7
"SG90_W" = 12.2
"SG90_H" = 27.0
"SG90_tab_L" = 32.3
"SG90_tab_T" = 2.8
"SG90_tab_Z" = 17.0
"MG90S_L" = 22.8
"MG90S_W" = 12.4
"MG90S_H" = 28.4
"MG90S_tab_L" = 32.1
"MG90S_tab_T" = 2.8
"MG90S_tab_Z" = 18.5
"PICO_L" = 51
"PICO_W" = 21
"PICO_H" = 12
```

4. Click **OK**. Now every sketch dimension can reference these variables by name.

> **Tip:** To scale the entire skeleton later, just change `"S"` and make every dimension multiply by it. For example, a sketch dimension of `"BASE_W" * "S"` becomes 80mm at S=1.0 and 96mm at S=1.2.

### Step 2: Set the Origin and Coordinate System

1. The **origin (0, 0, 0)** is the center of the base plate's top surface
2. **Top Plane** = ground level (XZ is the floor, Y is up in SolidWorks default)
3. If you prefer Z-up (matching our spec): go to **Tools → Options → System Options → View Rotation** and note that SolidWorks uses Y-up internally. You can work in Y-up and the STL export will be fine — the pipeline handles axis mapping.

### Step 3: Build the Base Section

1. **Base plate:**
   - Select **Top Plane** → **Sketch** → draw a **Center Rectangle** at origin, width = `"BASE_W"`, depth = `"BASE_D"`
   - **Sketch Fillet** the corners at radius `"BASE_R"`
   - **Exit Sketch** → **Boss-Extrude** downward by `"BASE_H"` (this puts the plate below the origin)

2. **Pi Pico W cavity:**
   - Create a **new sketch** on the bottom face of the base plate
   - Draw a rectangle: `"PICO_L" + 6` × `"PICO_W" + 4` (cavity with clearance), offset 15mm from center in +X
   - **Cut-Extrude** upward by `"PICO_H"` — this carves the pocket into the base
   - Add a slot extending to the edge for USB cable access

3. **Waist servo cavity:**
   - Create a **new sketch** on the top face of the base plate
   - Draw a rectangle centered at origin: `"SG90_L" + 2*"C_wall"` × `"SG90_W" + 2*"C_wall"`
   - **Boss-Extrude** upward by `"SG90_H" + "C_wall"` (servo cavity rises above base)
   - Add **mounting tab slots**: offset rectangles for the SG90 tabs

4. **Name this body:** In the Feature Tree, expand **Solid Bodies** → right-click the body → **Rename** → `base_section`

### Step 4: Build the Torso Section (New Body)

1. **Start a new sketch** on the Top Plane at Z = `"WAIST_Z" + 13` (2mm overlap with base)
2. Draw a circle at origin, diameter = `"TORSO_D"`
3. **Boss-Extrude** upward to Z = `"HEAD_PAN_Z" - 5` — check **"Merge result"** is **UNCHECKED** (this creates a separate body)
4. **Shoulder servo cavities:**
   - New sketch on the **Right Plane** at X = `-"SHOULDER_X"` (left shoulder)
   - Draw the MG90S servo profile: `"MG90S_L" + 2*"C_wall"` × `"MG90S_W" + 2*"C_wall"`
   - **Boss-Extrude** symmetrically by `"MG90S_H" + 2*"C_wall"` — **Merge result UNCHECKED**
   - Repeat mirrored for right shoulder at X = `+"SHOULDER_X"`
5. **Combine** the torso column and shoulder mount bodies: **Insert → Features → Combine → Add** → select torso + both shoulder mounts
6. **Wire channels:**
   - Vertical: sketch a `"D_wire"` diameter circle offset from center, extrude the full torso height as a **Cut**
   - Horizontal: sketch `"D_wire"` circles at shoulder height, cut from torso center to each shoulder cavity
7. **Name this body:** `torso_section`

### Step 5: Build the Arm Sections (New Bodies)

1. **Left arm:**
   - New sketch at X = `-"SHOULDER_X"`, Z = `"SHOULDER_Z"`
   - Draw the outer housing: a box or rounded shape that encloses the MG90S servo + clearance
   - **Boss-Extrude** outward (in -X direction) by ~25mm — **Merge result UNCHECKED**
   - Add a cylindrical tube for the servo horn/shaft to pass through (diameter = `"MG90S_spline_OD" + 4`)
   - **Cut** the rotation clearance: a swept arc (180°, radius 30mm) around the shaft axis
   - The inner face should extend to X = `-"SHOULDER_X" + 12` (2mm overlap with torso)
   - **Name:** `left_arm_section`

2. **Right arm:**
   - **Insert → Mirror → Mirror Body** of left_arm_section across the Right Plane (YZ plane)
   - **Name:** `right_arm_section`

### Step 6: Build the Head Section (New Body)

1. **Head pan servo:**
   - New sketch at Z = `"HEAD_PAN_Z"`, centered at origin
   - Draw SG90 cavity profile: `"SG90_L" + 2*"C_wall"` × `"SG90_W" + 2*"C_wall"`
   - **Boss-Extrude** upward by `"SG90_H_total" + "C_wall"` — **Merge result UNCHECKED**

2. **Head tilt servo:**
   - New sketch at Z = `"HEAD_TILT_Z"`, rotated 90° (shaft pointing forward)
   - Draw SG90 cavity profile rotated
   - **Boss-Extrude** — merge with head pan body via **Combine → Add**

3. **Head mounting plate:**
   - Add a flat plate on top of the tilt servo (this is where the character's head shell attaches)
   - Include M2 screw holes for mounting

4. **Rotation clearance:**
   - At Z = `"HEAD_PAN_Z" - 3` (the boundary with torso), cut an annular ring: inner R=10mm, outer R=20mm, height 4mm
   - This ensures the head can rotate without the shell colliding

5. **Bottom boundary** extends to Z = `"HEAD_PAN_Z" - 3` (2mm overlap with torso)
6. **Name:** `head_section`

### Step 7: Verify the Assembly

1. **Section view:** Use **Insert → Reference Geometry → Section View** to slice through the skeleton and verify:
   - Servo cavities are correctly sized (servos should drop in with ~0.3mm gap on each side)
   - Wire channels connect from base through torso to shoulders and head
   - Section boundaries overlap by 2mm where they meet
   - Pi Pico cavity has USB access

2. **Interference check:** **Tools → Evaluate → Interference Detection** — there should be deliberate overlaps at boundaries but no unintended collisions

3. **Measure:** Spot-check critical dimensions against the tables in this document

### Step 8: Export STL Files

1. **File → Save As → STL**
2. In the STL dialog, select **"Export bodies in separate files"** (or use **Insert → Features → Save Bodies**)
3. For each body, ensure:
   - File name matches: `base_section.stl`, `torso_section.stl`, etc.
   - **Resolution:** Fine (deviation = 0.01mm, angle = 5°)
   - **Units:** Millimeters
4. Save all 5 files to `pipeline/skeleton_exports/`

### Step 9: Test in the Pipeline

```bash
cd ~/projects/hawabot
source .venv/bin/activate

# Quick test — subtract each section from a sculpture
python3 -c "
from pipeline.shell_pipeline import run_pipeline
# Test with the Naruto mesh or any sculpture STL
run_pipeline('path/to/sculpture.stl', 'pipeline/skeleton_exports/base_section.stl', 'test_base_shell.stl')
"
```

The pipeline will be updated to accept a folder of section STLs instead of a single skeleton file. Each section gets subtracted independently, producing separate shell pieces that match exactly at the boundaries.

### Step 10: Iterate

If something doesn't fit:
1. Open SolidWorks → **Tools → Equations** → adjust the relevant variable
2. All features rebuild automatically
3. Re-export STLs
4. Re-run the pipeline

Common adjustments:
- Servo too tight? Increase `C_wall` from 0.3 to 0.5
- Shell too thin? Increase `T_wall` from 2.5 to 3.0
- Robot too small for the character? Increase `S` from 1.0 to 1.3
- Shoulders too narrow? Increase `SHOULDER_X` from 35 to 40

---

## General SolidWorks Tips

- **Merge result UNCHECKED** is critical when extruding new bodies — if you forget, everything fuses into one body and you can't export sections separately
- **Name bodies immediately** after creating them — it's easy to lose track
- Use **Appearance → Transparency** to make it easier to see internal cavities
- **Save frequently** — multi-body parts can get complex
- Download the official **Pi Pico W STEP file** from [raspberrypi.com](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) and insert it as a reference body (don't include it in exports)
