# HawaBot Pro — SolidWorks Build Package

Everything you need to build the kinematic skeleton in SolidWorks 2025.

---

## What's In This Package

```
solidworks_package/
├── README_START_HERE.md          ← You are here
├── hawabot_ssp_macro.bas         ← VBA macro — creates the full SSP in one click
├── equations_250mm.txt           ← All global variables (backup reference)
├── spark_skeleton_frame.step     ← CadQuery-generated frame (visual reference only)
├── sg90_reference.step           ← Simple SG90 model (use until you get GrabCAD version)
├── mg90s_reference.step          ← Simple MG90S model
├── magnet_6x3_reference.step     ← Magnet cylinder reference
├── COMPONENT_REFERENCE.md        ← Every component's dimensions, pockets, clearances
└── SOLIDWORKS_BUILD_GUIDE.md     ← Full kinematic skeleton build instructions
```

---

## Before You Start — Download Real Component STEP Files

Download these and save into a `components/` folder on your SolidWorks machine:

| Component | Source | Priority |
|---|---|---|
| SG90 Servo | https://grabcad.com/library/sg90-micro-servo-9g-tower-pro-1 | ✓ Already have |
| MG90S Servo | https://grabcad.com/library/mg90s-servo-high-detail-1 | ✓ Already have |
| Pi Pico W | https://datasheets.raspberrypi.com/picow/PicoW-step.zip | ✓ Already have |
| **XL330-M288-T** | Official: https://en.robotis.com/service/downloadpage.php?ca_id=70 (Drawing → DYNAMIXEL → XL330, STEP format). Alt: https://grabcad.com/library/xl330-288-t-1 | **Download now** |
| **Pi 5 (4GB)** | https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-step.zip | **Download now** |
| **Pi Zero 2W** | https://grabcad.com/library/raspberry-pi-zero-2-w-1 | **Download now** |
| **PCA9685** | https://grabcad.com/library/pca9685-pwm-servo-driver-for-arduino-1 | **Download now** |
| **MPU6050 GY-521** | https://grabcad.com/library/gy-521-mpu6050-accelerometer-and-gyroscope-module-1 | **Download now** |

Simple components (speaker, amp, mic, battery, charger) — just model as blocks using dimensions in COMPONENT_REFERENCE.md.

---

## Step-by-Step Build Instructions

### Phase 1: Create the Skeleton Sketch Part (SSP) — 5 minutes

This creates all the kinematic construction geometry — no solid parts yet.

1. Open SolidWorks 2025
2. **File → New → Part** (use mmgs template — millimeters)
3. **File → Save As** → `hawabot_skeleton_sketch.sldprt`
4. **Tools → Macro → New** → save as `hawabot_ssp.swp` (anywhere is fine)
5. The VBA editor opens. Go to **File → Import File**
6. Browse to `hawabot_ssp_macro.bas` from this package → Open
7. In the Project tree (left side), you'll see `HawaBotSSP` module appear
8. If there's an empty `Module1`, right-click it → **Remove Module1** → No (don't export)
9. Click inside the `HawaBotSSP` code → Press **F5** (Run)
10. Wait ~30 seconds. A success message will appear.
11. Close the VBA editor (File → Close and Return to SolidWorks)
12. **File → Save**

**What you should see:**
- In the Feature Tree: 18 planes (PL_*), 18 axes (AX_*), and a `KINEMATIC_LAYOUT` 3D sketch
- In the Equations dialog (Tools → Equations): 70+ global variables
- In the viewport: a stick-figure skeleton made of construction lines showing spine, arms, legs

**If the macro fails:**
- Check the VBA Immediate Window (View → Immediate Window or Ctrl+G) for error messages
- Most common issue: `Add2` equation method — if it fails, you'll need to add variables manually through Tools → Equations → Add
- Reference `equations_250mm.txt` for all variable names and values

### Phase 2: Verify the SSP — 5 minutes

Before proceeding, verify everything was created correctly:

1. **Tools → Equations** — confirm you see 70+ global variables with correct values
2. **View → Planes** (toggle ON) — you should see 18 colored planes at different heights/positions
3. **View → Axes** (toggle ON) — you should see 18 axes at joint intersections
4. Click on `KINEMATIC_LAYOUT` in the Feature Tree to highlight the stick figure
5. **Rotate the view** — verify the stick figure looks like a humanoid:
   - Vertical spine from Z=-25 to Z=210
   - Arms spreading out at Z=140 to X=±65
   - Legs going down from Z=0 to Z=-115
   - Base plate rectangle at Z=-25

**Key dimensions to spot-check:**
| What | Where | Value |
|---|---|---|
| Shoulder height | Z | 140 mm |
| Head top | Z | ~210 mm |
| Knee | Z | -60 mm |
| Shoulder spread | X | ±48 mm |
| Elbow | X | ±65 mm |
| Hip spread | X | ±20 mm |

### Phase 3: Create the Master Assembly — 10 minutes

1. **File → New → Assembly**
2. **File → Save As** → `hawabot_pro_assembly.sldasm`
3. **Insert Component** → browse to `hawabot_skeleton_sketch.sldprt` → place at origin
4. Right-click `hawabot_skeleton_sketch` in the Feature Tree → **Fix** (green pin icon)

The SSP is now the foundation — everything mates to it.

### Phase 4: Place Servos at Joint Axes — 30 minutes

For each servo, you need TWO mates:
- **Concentric:** Servo shaft axis → SSP joint axis (allows rotation)
- **Coincident:** Servo body face → SSP joint plane (positions it at the right height)

#### 4.1 Waist Yaw — MG90S

1. **Insert Component** → select your MG90S STEP file
2. Position it roughly near the waist area
3. **Mate** (click the mate icon or Ctrl+M):
   - Select the MG90S output shaft axis + `AX_WAIST_YAW` → **Concentric**
   - Select the MG90S bottom face + `PL_WAIST_YAW` → **Coincident**
4. Add **Limit Mate:**
   - In Mate dialog, expand **Advanced Mates**
   - Select **Limit** → pick the concentric mate
   - Set: Min = -90°, Max = +90°
5. Verify: the servo should sit at Z=15 with shaft pointing up

#### 4.2 Repeat for all servos

Follow the same pattern — concentric to axis, coincident to plane, limit mate for range:

| Servo | Component | Axis | Plane | Limit | Shaft |
|---|---|---|---|---|---|
| Waist yaw | MG90S | AX_WAIST_YAW | PL_WAIST_YAW | ±90° | Up (+Z) |
| Waist roll | SG90 | AX_WAIST_ROLL | PL_WAIST_ROLL | ±30° | Forward (+Y) |
| L shoulder | MG90S | AX_L_SHOULDER | PL_L_SHOULDER | ±90° | Out (-X) |
| R shoulder | MG90S | AX_R_SHOULDER | PL_R_SHOULDER | ±90° | Out (+X) |
| L elbow | SG90 | AX_L_ELBOW | PL_L_ELBOW | ±90° | Out (-X) |
| R elbow | SG90 | AX_R_ELBOW | PL_R_ELBOW | ±90° | Out (+X) |
| L hand | SG90 | AX_L_HAND | PL_L_HAND | 0–45° | Out (-X) |
| R hand | SG90 | AX_R_HAND | PL_R_HAND | 0–45° | Out (+X) |
| Head pan | SG90 | AX_HEAD_PAN | PL_HEAD_PAN | ±90° | Up (+Z) |
| Head tilt | SG90 | AX_HEAD_TILT | PL_HEAD_TILT | ±30° | Forward (+Y) |
| L hip yaw | XL330 | AX_L_HIP_YAW | PL_HIP | ±45° | Up (+Z) |
| R hip yaw | XL330 | AX_R_HIP_YAW | PL_HIP | ±45° | Up (+Z) |
| L hip pitch | XL330 | AX_L_HIP_PITCH | PL_L_HIP | ±90° | Out (-X) |
| R hip pitch | XL330 | AX_R_HIP_PITCH | PL_R_HIP | ±90° | Out (+X) |
| L knee | XL330 | AX_L_KNEE | PL_KNEE | 0–120° | Out (-X) |
| R knee | XL330 | AX_R_KNEE | PL_KNEE | 0–120° | Out (+X) |
| L ankle | XL330 | AX_L_ANKLE | PL_ANKLE | ±30° | Out (-X) |
| R ankle | XL330 | AX_R_ANKLE | PL_ANKLE | ±30° | Out (+X) |

**Tip:** After placing the first MG90S, you can copy+paste it (Ctrl+C, Ctrl+V) and just re-mate to the next axis/plane. Same for SG90s and XL330s.

### Phase 5: Place Electronics & Sensors — 15 minutes

These don't rotate — use **Coincident + Lock** mates:

1. **Pi 5:** Place at base plate center (0, 0, -12.5mm). Flat on Top Plane, USB ports toward +X edge.
2. **PCA9685:** Beside Pi 5 at (+35, 0, -12.5mm).
3. **Battery:** Opposite side at (-30, 0, -12.5mm).
4. **Speaker (⌀28mm cylinder):** Torso front at (0, -14, 100mm). Cone faces -Y.
5. **Amp board:** Behind speaker at (0, -8, 100mm).
6. **IMU (MPU6050):** Torso center at (0, 0, 90mm). Must be level.
7. **Mic:** Head face at (0, -10, 175mm).
8. **Ultrasonic:** Head front at (0, -12, 180mm).

For simple components without STEP files, create quick block parts:
- **File → New → Part** → sketch rectangle → extrude to height → save
- Use dimensions from COMPONENT_REFERENCE.md

### Phase 6: Test Kinematics — 10 minutes

1. At the bottom of the SolidWorks window, click the **Motion Study 1** tab
2. Change dropdown from "Animation" to **"Basic Motion"**
3. **Drag servos manually:** Right-click a servo → **Move Component** → drag to rotate
4. Check that joints move within their limits and nothing collides
5. **Test key poses:**
   - T-pose: all at 0° (neutral)
   - Arms up: shoulders +90°
   - Wave: R shoulder +60°, R elbow +90°
   - Walk: L hip +30°, L knee -60°, L ankle +30°
   - Crouch: both hips +45°, both knees -90°

6. **Collision check:** Tools → Evaluate → Interference Detection → Calculate
   - Expected: no collisions in T-pose
   - Fix any overlaps by adjusting positions in the SSP global variables

### Phase 7: Design Your Frame — Your Creative Work

With all components placed and kinematics verified, design the 3D printed structural frame:

1. Create separate part files per section:
   - `frame_base.sldprt` — base plate housing
   - `frame_torso.sldprt` — torso column + brackets
   - `frame_head.sldprt` — head housing
   - `frame_arm_L.sldprt` / `frame_arm_R.sldprt`
   - `frame_leg_L.sldprt` / `frame_leg_R.sldprt`

2. Design each frame part to:
   - Reference SSP planes/axes (not servo faces) — so changes propagate
   - Include servo pockets with clearances from COMPONENT_REFERENCE.md
   - Include wire channels (⌀8mm main, ⌀6mm branches)
   - Include magnet pockets (⌀6.1 × 3.1mm) on external surfaces
   - Include screw bosses at servo tab holes (⌀4mm posts, ⌀2mm pilot holes)

3. Insert each frame part into the assembly and mate to SSP geometry

---

## Quick Reference — Pocket Sizes

| Component | Pocket Dimensions | Clearance |
|---|---|---|
| SG90 body | 23.3 × 12.8 × 23.3 mm | 0.3mm/side |
| SG90 tab slot | 32.9 × 12.8 × 3.4 mm | 0.3mm/side |
| SG90 horn clearance | ⌀25 × 10 mm above body | Free rotation |
| MG90S body | 23.4 × 13.0 × 23.1 mm | 0.3mm/side |
| MG90S tab slot | 32.7 × 13.0 × 3.4 mm | 0.3mm/side |
| XL330 body | 21.0 × 35.0 × 27.0 mm | 0.5mm/side |
| XL330 horn clearance | ⌀30 × 8 mm | Free rotation |
| Pi 5 | 90 × 60 × 25 mm | 2mm/side + connector clearance |
| PCA9685 | 65 × 28 × 15 mm | 1mm/side |
| Speaker | ⌀29 × 13 mm recess | 0.5mm radial |
| Magnet pocket | ⌀6.1 × 3.1 mm deep | Press-fit |

---

## Tier Stripping Guide

Once the Pro skeleton is designed, create Spark/Core by removing components:

| Remove for Spark | Remove for Core |
|---|---|
| All leg servos (8× XL330) | All leg servos (8× XL330) |
| Elbow servos (2× SG90) | Hand servos (1× SG90 — keep one for Core) |
| Hand servos (2× SG90) | |
| Waist roll servo (1× SG90) | |
| Speaker + amp | |
| Mic | |
| IMU | |
| Ultrasonic sensor | |
| Battery + charger | |
| Replace Pi 5 with Pi Pico W | Replace Pi 5 with Pi Zero 2W |
| Remove PCA9685 | |
| Cap leg sockets with flat base plate | Cap leg sockets with flat base plate |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Macro doesn't run | Make sure you imported the .bas file, deleted empty Module1, and the active document is a Part (not Assembly) |
| Variables not created | Check VBA Immediate Window (Ctrl+G) for errors. Try changing `Add2(0, ...)` to `Add2(-1, ...)` in the code |
| Planes at wrong position | Verify global variables in Tools → Equations. Planes reference these values. |
| Servo won't mate | Make sure you're selecting the shaft AXIS (not a face) for the concentric mate |
| Assembly over-constrained | Each servo should have exactly 2 mates (concentric + coincident). Remove any extras. |
| Motion study won't run | Change type from "Animation" to "Basic Motion". Ensure limit mates are defined. |
