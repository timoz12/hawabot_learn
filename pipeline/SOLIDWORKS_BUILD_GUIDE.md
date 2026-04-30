# HawaBot Pro — Kinematic Skeleton Assembly Guide (SolidWorks 2025)

Build the robot skeleton using the **Skeleton Sketch Part (SSP) method**: define all joint axes and link lengths as construction geometry first, then place real components at each joint. This enables kinematic simulation before you design any structural parts.

---

## Overview

```
Step 1: Create the Skeleton Sketch Part (SSP)
         → All joint axes, link centerlines, key planes
         → Pure construction geometry — no solid features

Step 2: Create the Master Assembly
         → Insert SSP as first (fixed) component
         → All other parts mate to SSP geometry

Step 3: Place servo components at each joint
         → Mate servo output shaft to SSP joint axis
         → Verify rotation ranges

Step 4: Place electronics, sensors, audio
         → Mate boards to SSP reference planes
         → Verify clearances

Step 5: Define magnet positions
         → Reference points on SSP for shell interface

Step 6: Run kinematic simulation
         → Motion Study using SSP mates
         → Verify joint ranges, collisions

Step 7: Design structural frame around components
         → YOUR creative work — build brackets, housings, columns
         → Reference SSP geometry so everything updates together
```

---

## Step 1: Create the Skeleton Sketch Part (SSP)

This is the most important step. The SSP contains NO solid geometry — only construction lines, planes, axes, and points that define the kinematic chain.

### 1.1 New Part

1. **File → New → Part** (mmgs template)
2. **Save As:** `hawabot_skeleton_sketch.sldprt`
3. Add all global variables via **Tools → Equations → Add** (reference `equations_250mm.txt`):

**Start with these essential variables:**
```
"TOTAL_H" = 250
"BASE_W" = 100
"BASE_D" = 80
"BASE_H" = 25
"WAIST_YAW_Z" = 15
"WAIST_ROLL_Z" = 45
"SHOULDER_Z" = 140
"SHOULDER_X" = 48
"ELBOW_Z" = 105
"ELBOW_X" = 65
"HEAD_PAN_Z" = 155
"HEAD_TILT_Z" = 185
"HIP_Z" = 0
"KNEE_Z" = -60
"ANKLE_Z" = -105
```

### 1.2 Master Layout Sketch — Front View (XZ Plane)

This sketch defines the kinematic chain as seen from the front.

1. Select **Front Plane** → **Insert Sketch**
2. Draw ALL of the following as **Construction Lines** (check "For construction" or select construction line mode):

**Spine chain (vertical centerline):**
```
Line 1: (0, -"BASE_H") to (0, 0)              → Base plate height
Line 2: (0, 0) to (0, "WAIST_YAW_Z")          → Ground to waist yaw
Line 3: (0, "WAIST_YAW_Z") to (0, "WAIST_ROLL_Z")  → Waist yaw to roll
Line 4: (0, "WAIST_ROLL_Z") to (0, "SHOULDER_Z")    → Waist to shoulders
Line 5: (0, "SHOULDER_Z") to (0, "HEAD_PAN_Z")      → Shoulders to neck
Line 6: (0, "HEAD_PAN_Z") to (0, "HEAD_TILT_Z")     → Head pan to tilt
```

**Left arm chain:**
```
Line 7: (0, "SHOULDER_Z") to (-"SHOULDER_X", "SHOULDER_Z")    → Shoulder link
Line 8: (-"SHOULDER_X", "SHOULDER_Z") to (-"ELBOW_X", "ELBOW_Z")  → Upper arm
Line 9: (-"ELBOW_X", "ELBOW_Z") to (-"ELBOW_X", "ELBOW_Z"-35)    → Forearm to hand
```

**Right arm chain (mirror):**
```
Line 10: (0, "SHOULDER_Z") to ("SHOULDER_X", "SHOULDER_Z")
Line 11: ("SHOULDER_X", "SHOULDER_Z") to ("ELBOW_X", "ELBOW_Z")
Line 12: ("ELBOW_X", "ELBOW_Z") to ("ELBOW_X", "ELBOW_Z"-35)
```

**Left leg chain:**
```
Line 13: (0, "HIP_Z") to (-20, "HIP_Z")           → Hip offset
Line 14: (-20, "HIP_Z") to (-20, "KNEE_Z")         → Upper leg (thigh)
Line 15: (-20, "KNEE_Z") to (-20, "ANKLE_Z")        → Lower leg (shin)
Line 16: (-20, "ANKLE_Z") to (-20, "ANKLE_Z"-10)    → Foot
```

**Right leg chain (mirror):**
```
Line 17-20: Mirror of lines 13-16 at X = +20
```

3. **Add Construction Points** at every joint intersection — these become your joint centers:

| Point | Location | Joint Name |
|---|---|---|
| P1 | (0, 0) | Ground / base top |
| P2 | (0, 15) | Waist yaw |
| P3 | (0, 45) | Waist roll |
| P4 | (0, 140) | Spine top / shoulder center |
| P5 | (-48, 140) | Left shoulder |
| P6 | (48, 140) | Right shoulder |
| P7 | (-65, 105) | Left elbow |
| P8 | (65, 105) | Right elbow |
| P9 | (-65, 70) | Left hand |
| P10 | (65, 70) | Right hand |
| P11 | (0, 155) | Head pan |
| P12 | (0, 185) | Head tilt |
| P13 | (-20, 0) | Left hip |
| P14 | (20, 0) | Right hip |
| P15 | (-20, -60) | Left knee |
| P16 | (20, -60) | Right knee |
| P17 | (-20, -105) | Left ankle |
| P18 | (20, -105) | Right ankle |

4. **Exit Sketch**
5. **Rename** the sketch: `LAYOUT_FRONT`

### 1.3 Master Layout Sketch — Side View (YZ Plane)

1. Select **Right Plane** → **Insert Sketch**
2. Draw construction lines for the side profile:

**Spine (same Z values, Y shows front-back offset):**
```
Line: (0, -"BASE_H") to (0, "HEAD_TILT_Z")    → Full spine centerline
```

**Leg side view (shows knee bend direction):**
```
Line: (0, 0) to (0, "KNEE_Z")        → Upper leg (straight down)
Line: (0, "KNEE_Z") to (0, "ANKLE_Z") → Lower leg
```

3. **Exit Sketch** → rename `LAYOUT_SIDE`

### 1.4 Create Reference Planes for Each Joint Axis

Each servo rotation needs a **reference plane** perpendicular to its rotation axis. This is what you'll mate servo shafts to.

**Insert → Reference Geometry → Plane** for each:

| Plane Name | Definition | Joint | Rotation Axis |
|---|---|---|---|
| `PL_WAIST_YAW` | Parallel to Top Plane, offset Z = 15mm | Waist yaw | Z (vertical) |
| `PL_WAIST_ROLL` | Parallel to Right Plane, offset Z = 45mm | Waist roll | Y (front-back) |
| `PL_L_SHOULDER` | Parallel to Right Plane, through P5 (-48, 140) | L shoulder pitch | X (left-right) |
| `PL_R_SHOULDER` | Parallel to Right Plane, through P6 (48, 140) | R shoulder pitch | X (left-right) |
| `PL_L_ELBOW` | Parallel to Right Plane, through P7 (-65, 105) | L elbow pitch | X |
| `PL_R_ELBOW` | Parallel to Right Plane, through P8 (65, 105) | R elbow pitch | X |
| `PL_L_HAND` | Parallel to Right Plane, through P9 (-65, 70) | L hand grip | X |
| `PL_R_HAND` | Parallel to Right Plane, through P10 (65, 70) | R hand grip | X |
| `PL_HEAD_PAN` | Parallel to Top Plane, offset Z = 155mm | Head pan yaw | Z |
| `PL_HEAD_TILT` | Parallel to Front Plane, offset Z = 185mm | Head tilt pitch | Y |
| `PL_L_HIP_YAW` | Parallel to Top Plane, through P13 (-20, 0) | L hip yaw | Z |
| `PL_R_HIP_YAW` | Parallel to Top Plane, through P14 (20, 0) | R hip yaw | Z |
| `PL_L_HIP_PITCH` | Parallel to Right Plane, through P13 | L hip pitch | X |
| `PL_R_HIP_PITCH` | Parallel to Right Plane, through P14 | R hip pitch | X |
| `PL_L_KNEE` | Parallel to Right Plane, through P15 (-20, -60) | L knee pitch | X |
| `PL_R_KNEE` | Parallel to Right Plane, through P16 (20, -60) | R knee pitch | X |
| `PL_L_ANKLE` | Parallel to Right Plane, through P17 (-20, -105) | L ankle pitch | X |
| `PL_R_ANKLE` | Parallel to Right Plane, through P18 (20, -105) | R ankle pitch | X |

### 1.5 Create Reference Axes for Each Joint

Each joint needs a **reference axis** representing the servo output shaft rotation.

**Insert → Reference Geometry → Axis** for each:

| Axis Name | Definition | Direction |
|---|---|---|
| `AX_WAIST_YAW` | Through P2, perpendicular to PL_WAIST_YAW | Vertical (Z) |
| `AX_WAIST_ROLL` | Through P3, perpendicular to PL_WAIST_ROLL | Front-back (Y) |
| `AX_L_SHOULDER` | Through P5, perpendicular to PL_L_SHOULDER | Left-right (X) |
| `AX_R_SHOULDER` | Through P6, perpendicular to PL_R_SHOULDER | Left-right (X) |
| `AX_L_ELBOW` | Through P7, perpendicular to PL_L_ELBOW | Left-right (X) |
| `AX_R_ELBOW` | Through P8, perpendicular to PL_R_ELBOW | Left-right (X) |
| `AX_L_HAND` | Through P9, perpendicular to PL_L_HAND | Left-right (X) |
| `AX_R_HAND` | Through P10, perpendicular to PL_R_HAND | Left-right (X) |
| `AX_HEAD_PAN` | Through P11, perpendicular to PL_HEAD_PAN | Vertical (Z) |
| `AX_HEAD_TILT` | Through P12, perpendicular to PL_HEAD_TILT | Front-back (Y) |
| `AX_L_HIP_YAW` | Through P13, perpendicular to PL_L_HIP_YAW | Vertical (Z) |
| `AX_R_HIP_YAW` | Through P14, perpendicular to PL_R_HIP_YAW | Vertical (Z) |
| `AX_L_HIP_PITCH` | Through P13, perpendicular to PL_L_HIP_PITCH | Left-right (X) |
| `AX_R_HIP_PITCH` | Through P14, perpendicular to PL_R_HIP_PITCH | Left-right (X) |
| `AX_L_KNEE` | Through P15, perpendicular to PL_L_KNEE | Left-right (X) |
| `AX_R_KNEE` | Through P16, perpendicular to PL_R_KNEE | Left-right (X) |
| `AX_L_ANKLE` | Through P17, perpendicular to PL_L_ANKLE | Left-right (X) |
| `AX_R_ANKLE` | Through P18, perpendicular to PL_R_ANKLE | Left-right (X) |

### 1.6 Create Reference Points for Component Placement

Add points for non-joint components:

| Point Name | Location (X, Y, Z) | Component |
|---|---|---|
| `PT_PI5` | (0, 0, -12.5) | Pi 5 center (inside base plate) |
| `PT_PCA9685` | (35, 0, -12.5) | PCA9685 board (beside Pi) |
| `PT_BATTERY` | (-30, 0, -12.5) | LiPo battery |
| `PT_TP4056` | (45, 30, -12.5) | Charging board (near base edge) |
| `PT_USB_C` | (50, 0, -12.5) | USB-C power input (base edge) |
| `PT_SPEAKER` | (0, -14, 100) | Speaker (torso front, chest height) |
| `PT_AMP` | (0, -8, 100) | Amp board (behind speaker) |
| `PT_IMU` | (0, 0, 90) | IMU (torso center) |
| `PT_MIC` | (0, -10, 175) | Microphone (head, face area) |
| `PT_ULTRASONIC` | (0, -12, 180) | Ultrasonic sensor (head front) |
| `PT_LED_L_EYE` | (-8, -12, 182) | Left eye LED |
| `PT_LED_R_EYE` | (8, -12, 182) | Right eye LED |
| `PT_LED_CHEST` | (0, -14, 110) | Chest LED |

### 1.7 Save the SSP

Your SSP should now contain:
- 2 layout sketches (front + side views with all construction lines)
- 18 reference planes (one per joint)
- 18 reference axes (one per joint rotation)
- ~25 reference points (joints + component locations)
- Global variables driving all positions
- **ZERO solid features**

Save. This part file is the **single source of truth** for your robot's geometry.

---

## Step 2: Create the Master Assembly

1. **File → New → Assembly**
2. **Save As:** `hawabot_pro_assembly.sldasm`
3. **Insert Component** → select `hawabot_skeleton_sketch.sldprt`
4. Place at origin → **Fix** the component (right-click → Fix)

The SSP is now the foundation. All other components mate to its geometry.

---

## Step 3: Place Servo Components at Each Joint

For each servo, you create two mates:
- **Concentric:** Servo output shaft axis → SSP joint axis (allows rotation)
- **Coincident:** Servo body reference plane → SSP joint plane (positions it)

### 3.1 Waist Yaw — MG90S

1. **Insert Component** → `MG90S.sldprt`
2. **Mate:**
   - Concentric: MG90S shaft axis → `AX_WAIST_YAW`
   - Coincident: MG90S mounting face → `PL_WAIST_YAW`
3. **Limit Mate** (for simulation): Set rotation limits ±90° around `AX_WAIST_YAW`
4. Servo body is below the plane, shaft points up (+Z)

### 3.2 Waist Roll — SG90

1. **Insert Component** → `SG90.sldprt`
2. **Mate:**
   - Concentric: SG90 shaft axis → `AX_WAIST_ROLL`
   - Coincident: SG90 mounting face → `PL_WAIST_ROLL`
3. **Limit Mate:** ±30°
4. Shaft points forward (+Y)

### 3.3 Left Shoulder — MG90S

1. **Insert Component** → `MG90S.sldprt`
2. **Mate:**
   - Concentric: shaft axis → `AX_L_SHOULDER`
   - Coincident: mounting face → `PL_L_SHOULDER`
3. **Limit Mate:** ±90°
4. Shaft points outward (-X)

### 3.4 Right Shoulder — MG90S

1. Mirror of left shoulder
2. Mate to `AX_R_SHOULDER` and `PL_R_SHOULDER`
3. Shaft points outward (+X)

### 3.5 Left Elbow — SG90

1. **Insert Component** → `SG90.sldprt`
2. **Mate:**
   - Concentric: shaft axis → `AX_L_ELBOW`
   - Coincident: mounting face → `PL_L_ELBOW`
3. **Limit Mate:** ±90°

### 3.6 Right Elbow — SG90

1. Mirror of left elbow at `AX_R_ELBOW`

### 3.7 Left Hand — SG90

1. **Insert Component** → `SG90.sldprt`
2. Mate to `AX_L_HAND` / `PL_L_HAND`
3. **Limit Mate:** 0–45° (grip open to closed)

### 3.8 Right Hand — SG90

1. Mirror at `AX_R_HAND`

### 3.9 Head Pan — SG90

1. **Insert Component** → `SG90.sldprt`
2. **Mate:**
   - Concentric: shaft axis → `AX_HEAD_PAN`
   - Coincident: mounting face → `PL_HEAD_PAN`
3. **Limit Mate:** ±90°
4. Shaft points up (+Z)

### 3.10 Head Tilt — SG90

1. **Insert Component** → `SG90.sldprt`
2. **Mate:**
   - Concentric: shaft axis → `AX_HEAD_TILT`
   - Coincident: mounting face → `PL_HEAD_TILT`
3. **Limit Mate:** -30° to +30°
4. Shaft points forward (+Y)

### 3.11 Leg Servos — XL330 (×8)

For each leg joint, insert an XL330 and mate:

| Joint | Mate Axis | Mate Plane | Limit | Shaft Direction |
|---|---|---|---|---|
| L hip yaw | `AX_L_HIP_YAW` | `PL_L_HIP_YAW` | ±45° | +Z |
| L hip pitch | `AX_L_HIP_PITCH` | `PL_L_HIP_PITCH` | ±90° | +X |
| L knee | `AX_L_KNEE` | `PL_L_KNEE` | 0° to 120° | +X |
| L ankle | `AX_L_ANKLE` | `PL_L_ANKLE` | ±30° | +X |
| R hip yaw | `AX_R_HIP_YAW` | `PL_R_HIP_YAW` | ±45° | +Z |
| R hip pitch | `AX_R_HIP_PITCH` | `PL_R_HIP_PITCH` | ±90° | +X |
| R knee | `AX_R_KNEE` | `PL_R_KNEE` | 0° to 120° | +X |
| R ankle | `AX_R_ANKLE` | `PL_R_ANKLE` | ±30° | +X |

**Important:** For daisy-chained XL330s, the cable connectors (JST 3-pin) face each other between adjacent servos. Leave 8mm cable clearance between each pair.

---

## Step 4: Place Electronics, Sensors, Audio

These components don't rotate — use **Coincident + Lock** mates to fix them at their reference points.

### 4.1 Raspberry Pi 5

1. **Insert Component** → `pi5.sldprt`
2. **Mate:**
   - Coincident: board center → `PT_PI5`
   - Parallel: board flat face → Top Plane
   - Lock rotation so USB ports face +X edge of base
3. Board sits inside base plate cavity, 6mm above base floor (standoffs)

### 4.2 PCA9685 Servo Driver

1. **Insert Component** → `pca9685.sldprt`
2. **Mate:** center → `PT_PCA9685`, parallel to Top Plane
3. Sits beside Pi 5 in base, servo headers face upward

### 4.3 LiPo Battery

1. **Insert Component** → model as 40×30×8mm block
2. **Mate:** center → `PT_BATTERY`
3. Opposite side of Pi 5 in base plate

### 4.4 TP4056 Charging Board

1. **Insert Component** → model as 25×17×4mm block
2. **Mate:** center → `PT_TP4056`
3. USB-C port must face base plate edge (-Y or +X)

### 4.5 USB-C Breakout

1. **Insert Component** → 20×14×5mm block
2. **Mate:** center → `PT_USB_C`
3. Port flush with base plate edge

### 4.6 Speaker (28mm)

1. **Insert Component** → ⌀28×12mm cylinder
2. **Mate:** center → `PT_SPEAKER`
3. Cone face points forward (-Y) through torso front wall

### 4.7 MAX98357A Amp

1. **Insert Component** → 19.4×17.8×3mm block
2. **Mate:** center → `PT_AMP`
3. Sits directly behind speaker

### 4.8 MPU6050 IMU

1. **Insert Component** → `gy521.sldprt`
2. **Mate:** center → `PT_IMU`
3. Must be level (parallel to Top Plane) and firmly mounted

### 4.9 INMP441 Microphone

1. **Insert Component** → 14×14×3mm block
2. **Mate:** center → `PT_MIC`
3. Sound port faces forward — needs ⌀1.5mm hole through frame

### 4.10 HC-SR04 Mini Ultrasonic

1. **Insert Component** → 40×18×16mm block
2. **Mate:** center → `PT_ULTRASONIC`
3. Transducer faces forward — two ⌀11mm openings needed in frame

### 4.11 NeoPixel LEDs (×3)

1. Model as 5×5×2mm blocks
2. **Mate** each to `PT_LED_L_EYE`, `PT_LED_R_EYE`, `PT_LED_CHEST`
3. Light-emitting face points outward through frame

---

## Step 5: Define Magnet Positions

Create a **3D sketch** in the SSP with construction points at all magnet locations. Reference `SKELETON_SPEC.md` § Magnet Grid for coordinates. These will later guide where you place ⌀6.1mm × 3.1mm pockets in the structural frame.

Magnet positions don't need planes or axes — just points. Group them by zone:
- Head ring: 8 points at Z≈160, radius ≈16mm
- Torso: 12 points at 3 heights around the column
- Arms: 6 points per arm on housing surfaces
- Base: 8 points around base perimeter

---

## Step 6: Run Kinematic Simulation

### 6.1 Set Up Motion Study

1. At the bottom of the SolidWorks window, click the **Motion Study** tab
2. Change type from **Animation** to **Motion Analysis** (for physics) or **Basic Motion** (for quick kinematics)
3. Each **Limit Mate** from Step 3 automatically constrains joint motion

### 6.2 Test Individual Joints

1. Right-click a Limit Mate → **Edit**
2. Drag the angle slider to verify the joint rotates correctly
3. Check that no servo bodies collide with adjacent servos

### 6.3 Define Motor Inputs

For each joint you want to test:
1. Right-click the Limit Mate → **Add Motor**
2. Set type: **Rotary Motor**
3. Apply to the concentric mate axis
4. Set motion: **Oscillate** with your desired range and speed

### 6.4 Run Collision Detection

1. In Motion Study, click **Calculate**
2. After simulation, go to **Results → Contact/Collision**
3. Identify any servo-to-servo or link-to-link collisions
4. Adjust link lengths in the SSP if needed (changes propagate to all mates)

### 6.5 Test Key Poses

Define these test positions to verify the kinematic chain:

| Pose | Joint Values | Tests |
|---|---|---|
| **T-pose** | All joints at 0° | Neutral, matches shell design |
| **Arms up** | Shoulders +90° | Max arm raise, check clearance |
| **Arms down** | Shoulders -90° | Arms alongside body |
| **Head full turn** | Pan ±90° | Neck clearance |
| **Head nod** | Tilt ±30° | Tilt clearance |
| **Waist twist** | Yaw ±90° | Upper/lower body clearance |
| **Walk step** | Hip pitch +30°, knee -60°, ankle +30° | Basic gait position |
| **Crouch** | Both hips pitch +45°, both knees -90° | Low stance |
| **Wave** | R shoulder +60°, R elbow +90° | Common animation |
| **Grip test** | Hand 0° to 45° | Gripper open/close |

---

## Step 7: Design Structural Frame

**This is YOUR design work.** With all components placed and kinematics verified, you build the 3D-printed frame around them.

### Guidelines

1. **Always reference SSP geometry** — don't dimension to servo faces, dimension to SSP planes/axes. This way, if you change a joint position in the SSP, everything updates.

2. **Build as separate part files, one per structural section:**
   - `frame_base.sldprt` — base plate, Pi 5 housing, battery bay
   - `frame_torso.sldprt` — torso column, speaker mount, shoulder brackets
   - `frame_head.sldprt` — head pan/tilt housing, mic mount, sensor mount
   - `frame_arm_left.sldprt` — shoulder-to-hand housing (mirror for right)
   - `frame_leg_left.sldprt` — hip-to-foot housing (mirror for right)

3. **Each structural part mates to the SSP** — not to servos or boards. The servos and boards also mate to the SSP. This keeps the reference chain clean: SSP → everything.

4. **Design pockets around components** using dimensions from `COMPONENT_REFERENCE.md`:
   - SG90 pocket: 23.3 × 12.8 × 23.3mm (body + 0.3mm/side)
   - MG90S pocket: 23.4 × 13.0 × 23.1mm
   - XL330 pocket: 21.0 × 35.0 × 27.0mm (body + 0.5mm/side)
   - Pi 5 pocket: 90 × 60 × 25mm
   - Speaker recess: ⌀29 × 13mm

5. **Wire channels:** Route ⌀8mm main channel vertically through torso, ⌀6mm branches to shoulders and legs, ⌀4mm for audio/sensor wires.

6. **Magnet pockets:** Cut ⌀6.1 × 3.1mm pockets at SSP magnet reference points on all external frame surfaces.

---

## Assembly Structure Summary

```
hawabot_pro_assembly.sldasm
│
├── hawabot_skeleton_sketch.sldprt    [FIXED at origin]
│   ├── LAYOUT_FRONT (construction sketch)
│   ├── LAYOUT_SIDE (construction sketch)
│   ├── 18 Reference Planes (PL_*)
│   ├── 18 Reference Axes (AX_*)
│   ├── ~25 Reference Points (PT_*)
│   └── Global Variables (equations)
│
├── SERVOS (mate to AX_* and PL_*)
│   ├── MG90S_waist_yaw.sldprt        → AX_WAIST_YAW
│   ├── SG90_waist_roll.sldprt        → AX_WAIST_ROLL
│   ├── MG90S_L_shoulder.sldprt       → AX_L_SHOULDER
│   ├── MG90S_R_shoulder.sldprt       → AX_R_SHOULDER
│   ├── SG90_L_elbow.sldprt           → AX_L_ELBOW
│   ├── SG90_R_elbow.sldprt           → AX_R_ELBOW
│   ├── SG90_L_hand.sldprt            → AX_L_HAND
│   ├── SG90_R_hand.sldprt            → AX_R_HAND
│   ├── SG90_head_pan.sldprt          → AX_HEAD_PAN
│   ├── SG90_head_tilt.sldprt         → AX_HEAD_TILT
│   ├── XL330_L_hip_yaw.sldprt        → AX_L_HIP_YAW
│   ├── XL330_L_hip_pitch.sldprt      → AX_L_HIP_PITCH
│   ├── XL330_L_knee.sldprt           → AX_L_KNEE
│   ├── XL330_L_ankle.sldprt          → AX_L_ANKLE
│   ├── XL330_R_hip_yaw.sldprt        → AX_R_HIP_YAW
│   ├── XL330_R_hip_pitch.sldprt      → AX_R_HIP_PITCH
│   ├── XL330_R_knee.sldprt           → AX_R_KNEE
│   └── XL330_R_ankle.sldprt          → AX_R_ANKLE
│
├── ELECTRONICS (mate to PT_*)
│   ├── pi5.sldprt                    → PT_PI5
│   ├── pca9685.sldprt                → PT_PCA9685
│   ├── battery.sldprt                → PT_BATTERY
│   ├── tp4056.sldprt                 → PT_TP4056
│   └── usb_c_breakout.sldprt         → PT_USB_C
│
├── AUDIO + SENSORS (mate to PT_*)
│   ├── speaker_28mm.sldprt           → PT_SPEAKER
│   ├── max98357a.sldprt              → PT_AMP
│   ├── inmp441_mic.sldprt            → PT_MIC
│   ├── mpu6050.sldprt                → PT_IMU
│   ├── hcsr04_mini.sldprt            → PT_ULTRASONIC
│   ├── led_eye_L.sldprt              → PT_LED_L_EYE
│   ├── led_eye_R.sldprt              → PT_LED_R_EYE
│   └── led_chest.sldprt              → PT_LED_CHEST
│
└── STRUCTURAL FRAME (YOUR DESIGN — mate to SSP)
    ├── frame_base.sldprt
    ├── frame_torso.sldprt
    ├── frame_head.sldprt
    ├── frame_arm_left.sldprt
    ├── frame_arm_right.sldprt
    ├── frame_leg_left.sldprt
    └── frame_leg_right.sldprt
```

---

## Reference Links

- [SolidWorks Skeleton Part Method (Javelin)](https://www.javelin-tech.com/blog/2017/07/solidworks-skeleton-part/)
- [Analyzing Kinematics with Layout Tools (CATI)](https://www.cati.com/blog/solidworks-analyzing-kinematics-with-2d-sketch-layout-tools/)
- [Kinematic & Dynamic Analysis (SolidWorks Blog)](https://blogs.solidworks.com/solidworksblog/2023/03/put-your-studies-in-quick-motion-with-kinematic-and-dynamic-analysis.html)
- [Poppy Humanoid CAD files (GrabCAD)](https://grabcad.com/library/poppy-humanoid-1)
- [Poppy Assembly Guide](https://docs.poppy-project.org/en/assembly-guides/poppy-humanoid/index.html)
