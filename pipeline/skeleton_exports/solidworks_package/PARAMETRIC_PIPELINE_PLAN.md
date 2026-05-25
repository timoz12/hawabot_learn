# HawaBot Parametric Skeleton Pipeline — Plan

This document explains the hybrid SolidWorks + CadQuery pipeline strategy and tracks where you are in the process. Use this as context when working with Claude on your SolidWorks machine.

---

## Current Status

- **Phase 1 (SSP): DONE** — v17 macro builds all planes, axes, and layout sketch successfully
- **Phase 2 (Verification): DONE** — geometry verified, Poppy-informed proportions confirmed
- **Phase 3 (Master Assembly): NEXT** — create assembly, insert SSP, fix at origin
- **Phase 4 (Servo Placement): TODO** — mate servos to axes/planes
- **Phase 5 (Electronics): TODO**
- **Phase 6 (Kinematics Test): TODO**

---

## Servo Strategy: Prototype vs Production

### Prototype Build (What You're Building Now)

Build the **Pro (19 DOF)** with XL330 at shoulders for proper dual-shaft support. Validate the full skeleton, then strip down to Spark.

**Servo selection:**
- **8x SG90** ($2 each) — head, shoulder roll, elbows, hands (low-load joints)
- **1x MG90S** ($4) — waist yaw (vertical axis, no cantilever concern)
- **10x XL330-M288-T** ($27 each) — L/R shoulder pitch + all 8 leg joints
- **1x FPX330-H101** ($11) — XL330 idler frame kit (4-pack, use 2 for shoulders)

| Bus | Servos | Controller |
|---|---|---|
| Dynamixel UART | 10x XL330 (shoulders + legs) | UART via MCU |
| PWM | 8x SG90 + 1x MG90S | PCA9685 (or on-board PWM driver) |

**Prototype BOM: ~$417**

### Production Retrofit (Spark Tier at $199)

For Spark production, the shoulders downgrade from XL330 to MG90S. This is safe because Spark has no elbows/hands — shoulder load is only ~15-20g (one SG90 + short shell piece).

| Joint | Prototype (Pro) | Production (Spark) |
|---|---|---|
| Shoulder pitch | XL330 ($27) + idler | MG90S ($4) — cantilever OK at this load |
| Shoulder roll | SG90 | SG90 |
| Head pan/tilt | SG90 | SG90 |
| Waist yaw | MG90S | MG90S |
| Elbows, hands | SG90 | Not in Spark |
| Legs (8 joints) | XL330 | Not in Spark |

**Spark production BOM: ~$53 servos+electronics, ~$99 total, $199 retail**

### Future Production Servo Upgrade Options (Deferred)

These were researched but deferred due to sourcing constraints:
- **Option B:** FT90M-C012 (dual shaft, $7.50) at shoulders + SCS0009 (serial bus, $10) elsewhere. Eliminates PCA9685. BUT: FT90M has only 8 units at RobotShop, SCS0009 out of stock at DFRobot.
- **Option C (best long-term):** All SCS0009 + 623ZZ bearing brackets at shoulders. One servo type, one bus, one protocol, feedback on every joint. Requires bearing bracket design.
- **Action item:** Email Feetech (service@feetechrc.com) for bulk pricing on FT90M-C012 and SCS0009.

---

## Compute Strategy: ESP32-S3

### Why ESP32-S3

Consumer products with WiFi/Bluetooth need FCC certification. Boards with **modular certification** skip expensive RF re-testing. This rules out Pi Zero 2W and Pi 5 for production.

| Board | FCC Modular Cert | Compliance Cost | Production? |
|---|---|---|---|
| Pi Zero 2W | No | ~$15,000 | Prototype only |
| Pi 5 | No | ~$15,000 | Prototype only |
| Pi CM4/CM5 | Yes | ~$3,000 | Yes, but $30/unit |
| **ESP32-S3-WROOM-1-N16R8** | **Yes** | **~$2,000-3,000** | **Yes — $3/unit** |

**ESP32-S3-WROOM-1-N16R8 selected** for Spark and Pro production. Team has direct ESP32 experience (WiFi, cloud SQL, OTA updates from environmental sensing project).

### ESP32-S3-WROOM-1-N16R8 Specs

| Spec | Value |
|---|---|
| Price | ~$3 |
| FCC ID | 2AC7Z-ESPS3WROOM1 |
| CPU | Dual-core Xtensa LX7, 240 MHz |
| RAM | 512 KB SRAM + 8 MB PSRAM (module variant) |
| WiFi / BT | Yes / Yes (BLE 5.0) |
| Audio | I2S (speaker) + PDM (mic) natively |
| Camera | DVP interface (OV2640 etc.) |
| GPIO | 36+ pins |
| PWM | 8 LEDC channels (hardware PWM) |
| UART | 3x hardware UART |
| OS | FreeRTOS / Arduino / MicroPython |
| Size (module) | 18 x 25.5 x 3.1 mm |
| Power consumption | Very low (~50-100mA active WiFi) |
| Startup time | ~100ms (instant-on, no Linux boot) |

### Architecture: Offloaded AI

Heavy AI runs on the user's phone/tablet/computer via WiFi. The ESP32-S3 handles real-time control:

```
[PHONE / TABLET / COMPUTER]          [ROBOT - 250mm]
                                      
  AI Tutor engine                     ESP32-S3 on custom PCB:
  Voice recognition (STT)    <-WiFi->   Servo control (PWM via PCA9685)
  Movement planning                     Speaker output (I2S)
  Curriculum UI                         Mic input (PDM, Pro only)
  Character personality                 IMU reading (I2C, Pro only)
  3D viewer                             Camera stream (DVP, Pro only)
                                        OTA firmware updates
```

No cables — WiFi only. Robot moves freely. Phone/laptop must be within WiFi range.

### Custom PCB: HawaBot Controller Board

One custom PCB replaces 4-5 separate breakout boards. **Same PCB for Spark and Pro** — Pro just populates additional components.

#### What the Custom PCB Integrates

| Replaces | Function | IC on Custom PCB | Populated |
|---|---|---|---|
| PCA9685 breakout | 16-ch PWM servo driver | PCA9685 IC (I2C) | Spark + Pro |
| Audio amp board | Speaker amplification | MAX98357A (I2S) | Spark + Pro |
| Mic breakout | Microphone input | SPH0641LU4H-1 (PDM MEMS) | Pro only |
| IMU breakout | Motion sensing | MPU6050 (I2C) | Pro only |
| Power regulation | 5V servos, 3.3V logic | Buck converter + LDO | Spark + Pro |
| Camera connector | DVP camera interface | Header (OV2640) | Pro only |
| — | WiFi + BT + compute | ESP32-S3-WROOM-1-N16R8 module | Spark + Pro |
| — | Power input + programming | USB-C connector | Spark + Pro |
| — | Servo connections | 9x 3-pin JST headers | Spark + Pro |
| — | Speaker connection | 2-pin JST header | Spark + Pro |

#### PCB Size and Layout

**Estimated size: ~60 x 40 x 8 mm** (about the size of a PCA9685 board)

The ESP32-S3-WROOM-1-N16R8 module is only 18x25.5mm. Board size is driven by the 9 servo connectors and peripheral ICs.

```
+--------------------------------------------------+
|  [USB-C]                          [speaker JST]  |
|                                                  |
|  [ESP32-S3-WROOM-1-N16R8 module]     [PCA9685 IC]     |
|  (18 x 25.5mm, antenna         (TSSOP-28)       |
|   keep-out zone above)                           |
|                                                  |
|  [MAX98357A]  [SPH0641]  [MPU6050]  [camera hdr] |
|  (amp)        (mic*)     (IMU*)     (DVP*)       |
|                                                  |
|  [buck]  [LDO]                                   |
|                                                  |
|  [servo1][servo2][servo3][servo4][servo5]         |
|  [servo6][servo7][servo8][servo9]                 |
+--------------------------------------------------+

  * = Pro only (unpopulated on Spark)
  
  55 mm wide x 35 mm tall x ~8 mm high
  2-layer PCB (no impedance matching needed)
  ~$2-3/board at JLCPCB + ~$15 assembly (prototype)
```

Fits comfortably in the 250mm robot's torso cavity (125mm tall gap from waist to shoulder, 28mm+ deep).

#### Spark vs Pro — Same Board, Different Population

| Component | Spark | Pro |
|---|---|---|
| ESP32-S3 module | Yes | Yes |
| PCA9685 PWM driver | Yes | Yes |
| MAX98357A amp | Yes | Yes |
| Speaker connector | Yes | Yes |
| USB-C | Yes | Yes |
| Power regulation | Yes | Yes |
| 9x servo headers | 7 used | 11 used (2 extra for elbows) |
| SPH0641LU4H-1 PDM mic | **Not populated** | Yes |
| MPU6050 IMU | **Not populated** | Yes |
| Camera connector | **Not populated** | Yes |

One PCB design. One assembly line. Two tiers by populating different components.

### Tier MCU Summary

| | Spark ($199) | Pro ($599) | Max (future, $999+) |
|---|---|---|---|
| MCU | ESP32-S3 | ESP32-S3 (same board) | CM5 or Pi 5 (larger robot) |
| Audio | Speaker (I2S) | Speaker (I2S) + mic (PDM) | Speaker + mic array |
| Sensors | None | IMU + FSRs + camera | Full sensor suite |
| AI brain | Phone/tablet via WiFi | Phone/tablet via WiFi | On-board (autonomous) |
| Power | USB-C (wall powered) | Battery | Battery (large) |
| Custom PCB | HawaBot Controller Board | Same board, more populated | Different board |

### Rejected Alternatives (for reference)
- **Pi CM4/CM5 ($30):** FCC modular cert, Linux, but 10x cost, 20x power draw, 4-layer PCB, 30-second boot. Overkill when AI is offloaded.
- **Pi Zero 2W ($15):** No FCC modular cert — $15,000 compliance cost. Prototype only.
- **Pi 5 ($60):** 85x56mm — physically too large for 250mm torso. No modular cert.
- **Pi Pico W ($6):** No native audio I/O, no Linux. Prototype only.

---

## Tier Architecture

Two tiers at launch. Max is a future aspirational product.

```
SPARK ($199)                    PRO ($599)
7 DOF                           19 DOF

   [HEAD]                         [HEAD]
     |                              |
 [SHOULDERS]                    [SHOULDERS]
                                  / \
                               [ELBOW]
                                  |
                               [HAND]
     |                              |
  [WAIST]                       [WAIST]
     |                              |
 [FLAT BASE]                     [HIPS]
                                  / \
                               [KNEE]
                                  |
                               [ANKLE] + FSRs
                                  |
                               [FOOT]

MAX (future, $999+) — 400-500mm, on-board AI, fully autonomous
```

| | Spark ($199) | Pro ($599) | Max (future, $999+) |
|---|---|---|---|
| DOF | 7 | 19 | 19+ |
| Size | 250mm | 250mm (same skeleton) | 400-500mm (separate) |
| Compute | ESP32-S3 | ESP32-S3 (same PCB) | CM5 / Pi 5 |
| Audio | Speaker | Speaker + mic | Speaker + mic array |
| Sensors | None | IMU + FSRs + camera | Full suite + LIDAR |
| Power | USB-C tethered | **Battery** | Battery (large) |
| Legs | No (flat base) | **Yes (walking)** | Yes (advanced gait) |
| AI brain | Phone via WiFi | Phone via WiFi | On-board (autonomous) |
| Retail | $199 | $599 ($399 upgrade) | $999+ |
| Subscription | $39/mo x 6 | TBD | N/A |
| Custom PCB | Same board | Same board (more populated) | Different board |
| Upgrade from Spark? | — | **Yes** | No (separate robot) |

---

## What Changed from the Original Plan (v17 Updates)

### Proportions (Poppy Humanoid-informed)
| Variable | Old | New | Why |
|---|---|---|---|
| `SHOULDER_X` | 48 | 40 | Narrower shoulders (Poppy ratio) |
| `ELBOW_X` | 65 | 75 | Longer outward reach |
| `ELBOW_Z` | 105 | 100 | Drops elbow slightly |
| `HAND_X` | (same as elbow) | 55 | Hand inward of elbow |
| `HAND_Z` | 70 | 50 | Longer forearm |
| `KNEE_Z` | -60 | -55 | Slightly higher knee |
| `ANKLE_Z` | -105 | -110 | Lower ankle, longer shin |

### DOF Changes (19 DOF total, was 18)
- **Added:** Shoulder roll (2 axes — `AX_L_SHOULDER_ROLL`, `AX_R_SHOULDER_ROLL`)
- **Removed:** Waist roll (no more `PL_WAIST_ROLL` / `AX_WAIST_ROLL`)
- Net: 18 - 1 + 2 = **19 DOF**

### Verified Skeleton Math (foot to head)
```
Foot bottom:  Z = -115
Ankle:        Z = -110   (5mm above foot)
Knee:         Z = -55    (55mm shin)
Hip:          Z = 0      (55mm thigh)
Waist yaw:    Z = 15
Shoulder:     Z = 140    (125mm torso gap — electronics + IMU here)
Elbow:        Z = 100    (upper arm ~53mm)
Hand:         Z = 50     (forearm ~54mm)
Head pan:     Z = 155
Head tilt:    Z = 185
Head top:     Z = 210
Total:        325mm foot-to-head
Leg ratio:    35%
Arm ratio:    33%
```

### Axis Architecture (13 SW features for 19 servos)
Pitch axes are **shared L/R** — one feature, both servos mate to it. Distinguish L vs R via the coincident plane only.

Yaw axes are **vertical Z lines** — servo shafts point straight up.

---

## Phase 3: Create the Master Assembly (DO THIS NEXT)

1. **File > New > Assembly** (use mmgs template)
2. **File > Save As** > `hawabot_pro_assembly.sldasm` (same folder as the SSP)
3. **Insert Component** > browse to `hawabot_skeleton_sketch.sldprt` > place at origin
4. Right-click `hawabot_skeleton_sketch` in Feature Tree > **Fix** (green pin)

The SSP is now the assembly foundation. Everything mates to it.

---

## Phase 4: Servo Placement — Mate Table (v17)

For each servo: **Concentric** (shaft axis > SSP axis) + **Coincident** (body face > SSP plane) + **Limit Mate** (range).

### Important Notes
- **Pitch axes are shared L/R.** Both L and R shoulder pitch servos mate concentrically to the same `AX_SHOULDER_PITCH`. The coincident plane (`PL_L_SHOULDER` vs `PL_R_SHOULDER`) is what separates them.
- **Yaw axes are vertical Z lines.** Waist yaw, head pan, and hip yaw servo shafts point straight up (+Z).
- Copy+paste servos of the same type to save time — then just re-mate.
- **Shoulder pitch uses XL330 (not MG90S)** for the prototype — dual shaft + idler for proper support. Use FPX330-H101 idler frame kit on the back side.

### Full Mate Table (19 servos)

| # | Joint | Servo | Concentric Axis | Coincident Plane | Limit | Shaft Direction |
|---|---|---|---|---|---|---|
| 1 | Waist yaw | MG90S | AX_WAIST_YAW | PL_WAIST_YAW | +/-90 deg | Up (+Z) |
| 2 | Head pan | SG90 | AX_HEAD_PAN | PL_HEAD_PAN | +/-90 deg | Up (+Z) |
| 3 | Head tilt | SG90 | AX_HEAD_TILT | PL_HEAD_TILT | +/-30 deg | Out (+X) |
| 4 | L shoulder pitch | **XL330** | AX_SHOULDER_PITCH | PL_L_SHOULDER | +/-90 deg | Out (-X) |
| 5 | R shoulder pitch | **XL330** | AX_SHOULDER_PITCH | PL_R_SHOULDER | +/-90 deg | Out (+X) |
| 6 | L shoulder roll | SG90 | AX_L_SHOULDER_ROLL | PL_L_SHOULDER | +/-45 deg | Forward (+Y) |
| 7 | R shoulder roll | SG90 | AX_R_SHOULDER_ROLL | PL_R_SHOULDER | +/-45 deg | Forward (+Y) |
| 8 | L elbow pitch | SG90 | AX_ELBOW_PITCH | PL_L_ELBOW | +/-90 deg | Out (-X) |
| 9 | R elbow pitch | SG90 | AX_ELBOW_PITCH | PL_R_ELBOW | +/-90 deg | Out (+X) |
| 10 | L hand pitch | SG90 | AX_HAND_PITCH | PL_L_HAND | 0-45 deg | Out (-X) |
| 11 | R hand pitch | SG90 | AX_HAND_PITCH | PL_R_HAND | 0-45 deg | Out (+X) |
| 12 | L hip yaw | XL330 | AX_L_HIP_YAW | PL_HIP | +/-45 deg | Up (+Z) |
| 13 | R hip yaw | XL330 | AX_R_HIP_YAW | PL_HIP | +/-45 deg | Up (+Z) |
| 14 | L hip pitch | XL330 | AX_HIP_PITCH | PL_L_HIP | +/-90 deg | Out (-X) |
| 15 | R hip pitch | XL330 | AX_HIP_PITCH | PL_R_HIP | +/-90 deg | Out (+X) |
| 16 | L knee pitch | XL330 | AX_KNEE_PITCH | PL_L_KNEE_X | 0-120 deg | Out (-X) |
| 17 | R knee pitch | XL330 | AX_KNEE_PITCH | PL_R_KNEE_X | 0-120 deg | Out (+X) |
| 18 | L ankle pitch | XL330 | AX_ANKLE_PITCH | PL_L_ANKLE_X | +/-30 deg | Out (-X) |
| 19 | R ankle pitch | XL330 | AX_ANKLE_PITCH | PL_R_ANKLE_X | +/-30 deg | Out (+X) |

### Servo Count Summary
| Servo | Count | Joints |
|---|---|---|
| MG90S | 1 | Waist yaw |
| SG90 | 8 | Head pan, head tilt, L/R shoulder roll, L/R elbow, L/R hand |
| XL330 | 10 | L/R shoulder pitch, L/R hip yaw, L/R hip pitch, L/R knee, L/R ankle |
| **Total** | **19** | |

### STEP Files Needed
| Servo | Status | Source |
|---|---|---|
| SG90 | `sg90_reference.step` in package | Ready |
| MG90S | `mg90s_reference.step` in package | Ready |
| XL330-M288-T | **DOWNLOAD** | Robotis: https://en.robotis.com/service/downloadpage.php?ca_id=70 (Drawing > DYNAMIXEL > XL330, STEP) or GrabCAD: https://grabcad.com/library/xl330-288-t-1 |
| FPX330-H101 idler frame | **DOWNLOAD** | Robotis same page, look for frame STEP files |

---

## The Big Picture — Why We're Doing This

### Problem
SolidWorks is manual — great for engineering one skeleton, but can't scale to hundreds of characters.

### Solution: Hybrid Pipeline
SolidWorks builds and validates ONE golden baseline. CadQuery handles per-character parametric variations at volume.

### How It Works

```
YOU (once, in SolidWorks):
  1. Build + validate the 250mm skeleton (Phase 1-2: DONE)
  2. Create master assembly with all servos + electronics (Phase 3-6: IN PROGRESS)
  3. Test kinematics, run interference detection
  4. Document safe adjustment ranges per variable (min/max before collisions)
  5. Export golden baseline as STEP + validated equations

PIPELINE (per character, automated):
  1. AI extracts proportions from uploaded 3D model (limb ratios)
  2. Python maps ratios to skeleton variables
  3. Clamps all values to your validated safe ranges
  4. CadQuery generates skeleton + simple frame geometry
  5. Interference check (bounding box — no servo overlaps)
  6. Export STEP/STL — user sees REAL geometry in web 3D viewer

YOU (only when needed):
  - New skeleton topology (quadruped, desk buddy, etc.)
  - Edge cases outside safe ranges
  - Premium cosmetic shell design
```

### What CadQuery Does (Reliable)
- Move joint positions (translate coordinates)
- Resize bounding boxes (servo pockets)
- Cut cylindrical holes (wire channels, magnets, screws)
- Boolean operations on simple shapes
- Export STEP/STL

### What CadQuery Does NOT Do (Unreliable)
- Complex fillets on organic shapes
- Lofted transitions
- Surface modeling
- Cosmetic shell design

The skeleton frame is fundamentally just rectangular tubes, rectangular pockets, cylindrical holes, and flat plates. CadQuery handles this reliably. Complex/organic geometry lives in the **shell** (cosmetic snap-on pieces), designed separately.

### What the User Sees in the App
Real CadQuery-generated geometry in the 3D viewer — not a mockup. What they see is what they print.

---

## Safe Range Validation (Phase 6 Output — Do After Assembly)

After Phase 6 kinematics testing, fill in actual min/max per variable. Each row records not just the limit but **why** it exists, so the CadQuery pipeline can solve dependent variables as a system rather than clamping each independently.

### Constraint type taxonomy
- **structural** — physical strength of the printed/extruded frame holding under load
- **collision** — two parts overlap in a static pose (caught by interference detection)
- **kinematic** — two parts collide during motion (only caught in motion study)
- **geometric** — pure math relationship that must hold (e.g. `ELBOW_X > SHOULDER_X`, no test needed)

### Validation method
- **interference** — Tools > Evaluate > Interference Detection on the assembly
- **motion study** — sweep the joint through full range in a Basic Motion study
- **manual** — visual inspection or dimensional check
- **calc** — formula check, no SW test needed

### Test pose
The pose under which the limit must hold. Most collisions only appear in non-neutral poses, so each variable needs at least one stress-test pose recorded.

### Per-variable safe range table

| Variable | Default | Min | Max | Type | Validation | Test Pose | Affects | Limited By |
|---|---|---|---|---|---|---|---|---|
| `TOTAL_H` | 250 | ? | ? | structural | manual | T-pose | all segments | overall scale, BOM cost |
| `SHOULDER_Z` | 140 | ? | ? | collision | interference | T-pose, arms-up | HEAD_PAN_Z, HEAD_TILT_Z, ELBOW_Z | clear waist yaw servo + XL330 body |
| `SHOULDER_X` | 40 | ? | ? | geometric+collision | interference | T-pose | ELBOW_X, HAND_X | XL330 body width + TORSO_D clearance |
| `ELBOW_Z` | 100 | ? | ? | kinematic | motion study | arm-folded (elbow flexed 120 deg) | HAND_Z | gap to SHOULDER_Z >= SG90_H_total + clearance |
| `ELBOW_X` | 75 | ? | ? | geometric | calc | T-pose | HAND_X | must be > SHOULDER_X (arm extends outward) |
| `HAND_Z` | 50 | ? | ? | kinematic | motion study | arm-folded | (none) | gap to ELBOW_Z >= SG90_H_total + clearance |
| `HAND_X` | 55 | ? | ? | geometric | calc | T-pose | (none) | between SHOULDER_X and ELBOW_X (forearm bent inward) |
| `HEAD_PAN_Z` | 155 | ? | ? | collision | interference | head-rotated +/-90 | HEAD_TILT_Z | clear SHOULDER_Z + servo body height |
| `HEAD_TILT_Z` | 185 | ? | ? | kinematic | motion study | head-extreme tilt | (none) | gap to HEAD_PAN_Z >= SG90_H_total |
| `HIP_X` | 20 | ? | ? | geometric+collision | interference | T-pose, walking | KNEE_X (=HIP_X), ANKLE_X (=HIP_X) | XL330 body width + BASE_W clearance |
| `KNEE_Z` | -55 | ? | ? | kinematic | motion study + interference | crouch (knee 90-120 deg flex) | ANKLE_Z | gap to HIP_Z >= XL330_H + clearance, AND gap to ANKLE_Z >= XL330_H |
| `ANKLE_Z` | -110 | ? | ? | kinematic | interference | walk (ankle pitched +/-30) | (none) | gap to KNEE_Z >= XL330_H, gap to FOOT_H >= XL330 horn |

### Workflow per variable
1. Open the assembly. Tools > Equations.
2. Bracket-test the variable: set it to a value, rebuild (Ctrl+B), run the listed validation method in the listed test pose.
3. Find the smallest/largest value that doesn't fail. Record min/max.
4. If the variable has dependents listed in "Affects", repeat tests for each affected variable at the bracketed extreme.
5. Update this table.

Once all rows have concrete min/max, export to `safe_ranges.json`:

```json
{
  "version": "v17",
  "baseline": {"TOTAL_H": 250, "SHOULDER_Z": 140, ...},
  "ranges": {
    "SHOULDER_Z": {"min": 130, "max": 155, "type": "collision", "affects": ["HEAD_PAN_Z", "HEAD_TILT_Z", "ELBOW_Z"]},
    ...
  }
}
```

The pipeline reads this and clamps any AI-extracted character proportions to validated values before generating geometry.

---

## Servo Research Summary (for Future Reference)

A comprehensive servo survey was conducted. Key findings:

| Servo | Size (mm) | Dual Shaft | Serial Bus | Feedback | Price | Verdict |
|---|---|---|---|---|---|---|
| SG90 | 23x12x23 | No | No | No | $2 | Use for low-load joints |
| MG90S | 23x12x23 | No | No | No | $4 | Use for waist yaw (vertical axis) |
| FT90M-C012 | ~23x12x27 | **Yes** | No | No | $7.50 | Best micro dual-shaft, only 8 at RobotShop |
| SCS0009 | 23x12x27 | No | **Yes** | **Yes** | $10 | Best micro serial bus, out of stock at DFRobot |
| STS3032 | 24x18x35 | Yes | Yes | Yes | **$40** (not $16) | AliExpress price is deceptive |
| RDS3225 | 40x20x40 | Yes | No | No | $9 | Too large for 250mm robot |
| LX-224 | 40x20x51 | No | Yes | Yes | $16 | Too large, incompatible protocol with Feetech |
| XL330 | 20x34x26 | Yes (w/kit) | Yes | Yes | $27 | Best overall, use for load-bearing joints |

**Protocol incompatibilities:** HiWonder LX (0x55 0x55 header) and Feetech SCS/STS (0xFF 0xFF header) cannot share a bus. Dynamixel Protocol 2.0 (XL330) is also separate. Pick one ecosystem per bus.

**Production action item:** Contact Feetech (service@feetechrc.com) for bulk pricing on FT90M-C012 and SCS0009. If volume pricing is viable ($4-7/unit), revisit Option B or C for production Spark BOM.

---

## Files in This Package

| File | Status | Purpose |
|---|---|---|
| `hawabot_ssp_macro_v17.bas` | CANONICAL | VBA macro — creates full SSP (planes, axes, layout sketch) |
| `hawabot_skeleton_sketch.SLDPRT` | VALIDATED | The built SSP part file (Phase 1+2 complete) |
| `equations_250mm.txt` | Reference | Original 250mm equations (pre-v17, for reference) |
| `sg90_reference.step` | Ready | Simple SG90 servo model |
| `mg90s_reference.step` | Ready | Simple MG90S servo model |
| `magnet_6x3_reference.step` | Ready | Magnet cylinder reference |
| `COMPONENT_REFERENCE.md` | Ready | All component dimensions and clearances |
| `SOLIDWORKS_BUILD_GUIDE.md` | Ready | Full kinematic build instructions |
| `README_START_HERE.md` | Ready | Quick-start guide (Phase 1-2 steps) |
| `PARAMETRIC_PIPELINE_PLAN.md` | THIS FILE | Pipeline strategy + current progress |

### STEP Files to Download Before Phase 4
| File | Source | Priority |
|---|---|---|
| XL330-M288-T STEP | Robotis download page or GrabCAD | **Required** |
| FPX330-H101 idler frame STEP | Robotis download page | **Required** |

### STEP Files Needed for Phase 5 (Electronics)
For prototyping, use bounding-box placeholders based on dimensions above. Download real STEP files when available:
| File | Dimensions (placeholder) | Source |
|---|---|---|
| Custom PCB (ESP32-S3 version) | 60 x 40 x 8 mm | Model as block for now |
| Custom PCB (CM4 version) | 65 x 45 x 15 mm | Model as block for now |
| Speaker | dia28 x 12 mm cylinder | Model as cylinder |
| Battery | 40 x 30 x 8 mm | Model as block |

### Deleted (superseded by v17)
- `hawabot_ssp_macro.bas` (v1-v16 — all replaced by v17)

### To Be Created (after Phase 6)
| File | Purpose |
|---|---|
| `hawabot_pro_assembly.sldasm` | Master assembly with all servos + electronics |
| `hawabot_golden_250mm.step` | STEP export of validated golden baseline |
| `safe_ranges.json` | Machine-readable min/max per variable for CadQuery |
