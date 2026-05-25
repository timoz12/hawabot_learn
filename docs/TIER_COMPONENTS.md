# HawaBot — Tier Component Reference

_Last updated: 2026-05-12_

Three tiers. Spark and Pro share the same 250mm skeleton and custom PCB. Max is a separate, larger robot.

---

## Spark ($199 — 7 DOF Desk Companion, 250mm)

Upper-body humanoid on a flat base. Entry point for the curriculum.

| Component | Qty | Interface | Intent |
|---|---|---|---|
| ESP32-S3-WROOM-1-N16R8 | 1 | — | Main MCU: 16MB flash, 8MB PSRAM, WiFi, I2C, I2S, GPIO. FCC modular cert. |
| PCA9685 PWM driver | 1 | I2C (0x40) | 16-ch servo control over single I2C bus |
| SG90 micro servo | 5 | PCA9685 PWM | Head pan, head tilt, L/R shoulder roll, waist yaw |
| MG90S metal gear servo | 2 | PCA9685 PWM | L/R shoulder pitch (higher torque for arm lift) |
| MAX98357A I2S amp | 1 | I2S0 | Audio output — voice, sound effects, personality |
| Speaker (28mm, 3W, 4ohm) | 1 | MAX98357A | Physical audio output |
| USB-C power supply (5V 3A) | 1 | — | Wall power for servos + logic |
| Neodymium magnets (6x3mm N52) | ~20 | — | Snap-on shell attachment to skeleton |
| M2x5mm self-tapping screws | ~10 | — | Servo mounting to skeleton frame |
| Custom PCB (~55x35mm, 2-layer) | 1 | — | Integrates ESP32-S3 + PCA9685 + MAX98357A + power reg |
| 3D printed skeleton (PLA/PETG) | 1 | — | Structural frame: head, torso, arms, base |
| 3D printed character shell (5 pcs) | 1 set | — | Cosmetic magnetic snap-on: head, torso, L arm, R arm, base |

**Servo allocation (7 joints):**

| PCA9685 Ch | Joint | Servo | Load |
|---|---|---|---|
| CH0 | head_pan | SG90 | Light (~5g head shell) |
| CH1 | head_tilt | SG90 | Light |
| CH2 | left_shoulder_pitch | MG90S | Medium (~15-20g arm) |
| CH3 | left_shoulder_roll | SG90 | Light |
| CH4 | right_shoulder_pitch | MG90S | Medium (~15-20g arm) |
| CH5 | right_shoulder_roll | SG90 | Light |
| CH6 | waist_yaw | SG90 | Light (upper body rotation on base) |

**What Spark does:** Head tracks, shoulders wave, waist turns, speaker talks. AI tutor runs on phone/tablet via WiFi. No cables to phone.

---

## Pro ($599 all-in / $399 upgrade — 19 DOF Walking Humanoid, 250mm)

Same skeleton as Spark. Adds legs, arms, full sensor suite, and battery. Walks untethered.

### Everything in Spark, plus:

| Component | Qty | Interface | Intent |
|---|---|---|---|
| XL330-M288-T servo | 10 | UART1 Dynamixel bus | Shoulders upgraded (2) + 8 leg joints. Feedback + compliance for walking. |
| SG90 micro servo | +4 | PCA9685 PWM | L/R elbow pitch, L/R hand pitch |
| SPH0641LU4H-1 PDM MEMS mic | 1 | PDM (CLK + DATA) | Audio input — voice commands, sound detection |
| MPU6050 IMU | 1 | I2C (0x68) | Tilt + acceleration sensing for balance during walking |
| FSR 402 | 4 | ADC (GPIO1-3, 10) | Foot ground-contact detection — required for gait control |
| 10K resistors (FSR dividers) | 4 | — | Voltage dividers for FSR analog reading |
| OV2640 camera | 1 | DVP | Vision — face tracking, object recognition |
| LiPo battery (7.4V 2S, 1000mAh) | 1 | — | Untethered operation (can't walk on a cable) |
| TP4056 charger module | 1 | USB-C | Battery charging |
| 5V buck converter | 1 | — | Regulate LiPo 7.4V → 5V for servos + logic |
| XL330 idler frame kit (FPX330-H101) | 1 | — | Dual-shaft support for shoulder and leg joints |
| XL330 cables (3-pin, 100mm) | 10 | — | Daisy-chain Dynamixel bus wiring |
| 3D printed leg frame + feet | 1 | — | Leg structure with FSR mounting points |

**Servo allocation (19 joints):**

| Bus | Joint | Servo | Notes |
|---|---|---|---|
| PCA9685 CH0 | head_pan | SG90 | Same as Spark |
| PCA9685 CH1 | head_tilt | SG90 | Same as Spark |
| PCA9685 CH3 | left_shoulder_roll | SG90 | Same as Spark |
| PCA9685 CH5 | right_shoulder_roll | SG90 | Same as Spark |
| PCA9685 CH7 | left_elbow_pitch | SG90 | New — Pro only |
| PCA9685 CH8 | left_hand_pitch | SG90 | New — Pro only |
| PCA9685 CH9 | right_elbow_pitch | SG90 | New — Pro only |
| PCA9685 CH10 | right_hand_pitch | SG90 | New — Pro only |
| Dynamixel | left_shoulder_pitch | XL330 | Upgraded from MG90S |
| Dynamixel | right_shoulder_pitch | XL330 | Upgraded from MG90S |
| Dynamixel | left_hip_yaw | XL330 | New — Pro only |
| Dynamixel | left_hip_pitch | XL330 | New — Pro only |
| Dynamixel | left_knee_pitch | XL330 | New — Pro only |
| Dynamixel | left_ankle_pitch | XL330 | New — Pro only |
| Dynamixel | right_hip_yaw | XL330 | New — Pro only |
| Dynamixel | right_hip_pitch | XL330 | New — Pro only |
| Dynamixel | right_knee_pitch | XL330 | New — Pro only |
| Dynamixel | right_ankle_pitch | XL330 | New — Pro only |
| Dynamixel | waist_yaw | XL330 | Upgraded from SG90 |

**Pro servo summary:** 8x SG90 (PCA9685 PWM) + 10x XL330 (Dynamixel bus) + 1x waist XL330 = 19 DOF

**What Pro adds over Spark:** Walking gait, arms with elbows and hands, voice input (mic), balance sensing (IMU), ground contact detection (FSRs), vision (camera), untethered battery operation. Full systems engineering experience.

---

## Max ($999+ — 19+ DOF Autonomous Humanoid, 400-500mm, Future)

Separate, larger robot. Not upgrade-compatible with the 250mm Spark/Pro skeleton. Aspirational flagship for enthusiasts who completed the Spark → Pro curriculum. Low volume, high margin, marketing halo.

| Component | Qty | Interface | Intent |
|---|---|---|---|
| Raspberry Pi 5 / CM5 | 1 | — | On-board AI inference — fully autonomous, no phone needed |
| XL330-M288-T servo | 19+ | Dynamixel bus | All joints on serial bus — position feedback + compliance on every joint |
| XL430-W250 servo | 2-4 | Dynamixel bus | High-torque joints (hips, shoulders) — 16 kg-cm for larger frame |
| MAX98357A I2S amp | 1 | I2S | Audio output |
| Speaker | 1 | MAX98357A | Voice, sound effects |
| MEMS mic (array) | 2-4 | I2S | Directional audio input — sound localization |
| IMU (ICM-42688-P or MPU6050) | 1 | I2C | Balance + orientation sensing |
| FSR 402 | 4+ | ADC | Foot contact detection for advanced gait |
| Camera (wide-angle) | 1 | CSI / USB | Vision — face tracking, object recognition, navigation |
| LIDAR (TFmini-S or similar) | 1 | UART / I2C | Obstacle detection + mapping |
| Ultrasonic sensor | 1-2 | GPIO | Close-range obstacle avoidance |
| LiPo battery (11.1V 3S, 2000mAh+) | 1 | — | Extended untethered operation |
| BMS + charging circuit | 1 | USB-C | Battery management + safe charging |
| Buck converters (12V→5V, 12V→3.3V) | 2 | — | Regulated power rails for servos + logic |
| Custom PCB (larger, 4-layer) | 1 | — | Integrates Pi CM5 + Dynamixel hub + power management + sensors |
| 3D printed skeleton (PETG/Nylon) | 1 | — | Larger structural frame — stiffer material for heavier loads |
| 3D printed character shell | 1 set | — | Magnetic snap-on cosmetic parts (larger) |

**What Max does differently:**
- **On-board AI** — runs inference locally on Pi 5/CM5, no phone required
- **Fully autonomous** — navigates, avoids obstacles, interacts without supervision
- **All-Dynamixel** — every joint has position feedback and compliance control
- **XL430 at high-load joints** — 16 kg-cm torque handles the heavier 400-500mm frame
- **Advanced sensing** — LIDAR + ultrasonic for spatial awareness, mic array for sound localization
- **Larger battery** — 3S LiPo for extended runtime with higher compute + servo draw

---

## Tier Comparison

| | Spark | Pro | Max |
|---|---|---|---|
| **Price** | $199 | $599 ($399 upgrade) | $999+ |
| **Size** | 250mm | 250mm | 400-500mm |
| **DOF** | 7 | 19 | 19+ |
| **Compute** | ESP32-S3 | ESP32-S3 | Pi 5 / CM5 |
| **AI brain** | Phone via WiFi | Phone via WiFi | On-board (autonomous) |
| **Servo types** | SG90 + MG90S | SG90 + XL330 | XL330 + XL430 |
| **Servo buses** | PCA9685 only | PCA9685 + Dynamixel | Dynamixel only |
| **Audio** | Speaker out | Speaker + mic | Speaker + mic array |
| **Sensors** | None | IMU, 4x FSR, camera | IMU, FSR, camera, LIDAR, ultrasonic |
| **Power** | USB-C wall | Battery (7.4V 2S) | Battery (11.1V 3S) |
| **Locomotion** | Stationary (base) | Walking biped | Advanced gait |
| **Legs** | No | Yes | Yes |
| **Arms** | Shoulder only | + elbows + hands | Full articulation |
| **PCB** | Custom 2-layer (shared) | Custom 2-layer (shared) | Custom 4-layer (separate) |
| **Skeleton** | 250mm (shared) | 250mm (shared) | 400-500mm (separate) |
| **Upgrade path** | → Pro ($399) | → Max (separate purchase) | — |
| **Target** | Kids + parents, entry | Serious learners | Enthusiasts, graduates |
| **Volume** | High | Medium | Low (aspirational) |
| **BOM** | ~$57 | ~$383 | ~$500+ |
| **Margin** | ~71% | ~36% | TBD |
