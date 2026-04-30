# HawaBot — Component Reference & Placement Guide

Every component in the Pro skeleton with exact dimensions, mounting specifications, pocket/clearance requirements, and CAD file download links.

**Design for Pro (250mm), strip down for Core/Spark.**

---

## Quick Reference — What Goes Where

```
HEAD:
├── SG90 × 2 (pan + tilt)
├── INMP441 mic breakout (face area)               Pro only
├── HC-SR04 mini ultrasonic (front, "eyes")         Pro only
└── WS2812B LEDs × 2 (eyes)                         Core+

TORSO:
├── MG90S × 2 (shoulders)
├── SG90 × 2 (elbows)                               Core+
├── SG90 × 2 (hands/grippers)                       Core+ / Pro
├── MG90S × 1 (waist yaw)
├── SG90 × 1 (waist roll)                           Core+
├── Speaker ⌀28mm (chest front)                     Core+
├── MAX98357A amp board (behind speaker)             Core+
├── WS2812B LED × 1 (chest)                          Core+
└── MPU6050 IMU (torso center)                       Pro only

BASE PLATE / HIP:
├── Raspberry Pi 5 (4GB)                             Pro (Pico W for Spark, Zero 2W for Core)
├── PCA9685 servo driver                             Core+
├── TP4056 USB-C charging board                      Pro
├── LiPo battery 3.7V 1000mAh                       Pro
├── USB-C breakout (power input)                     All tiers
└── Power switch                                     All tiers

LEGS (Pro only):
├── XL330 × 2 (hip yaw)
├── XL330 × 2 (hip pitch)
├── XL330 × 2 (knee)
├── XL330 × 2 (ankle)
└── Foot plates with rubber pads
```

---

## 1. Servos

### 1.1 SG90 Micro Servo (×7 in Pro)

**Used for:** Head pan, head tilt, L/R elbow, L/R hand grip, waist roll

| Spec | Value |
|---|---|
| Body L × W × H | 22.7 × 12.2 × 22.7 mm (body only) |
| Overall H (with shaft) | 32.3 mm |
| Tab-to-tab length | 32.3 mm |
| Tab thickness | 2.8 mm |
| Tab underside from bottom | 17.0 mm |
| Mounting holes | 2 per tab, ⌀2.0 mm, inset 2.0 mm from tab edge |
| Shaft center from front | 6.2 mm |
| Spline OD | 4.8 mm |
| Turret ⌀ | 11.8 mm |
| Turret height above body | 5.96 mm |
| Weight | 9 g |
| Torque | 1.8 kg·cm at 4.8V |
| Wire length | ~150 mm, 3-pin (signal, VCC, GND) |
| **Pocket size (with clearance)** | **23.3 × 12.8 × 23.3 mm** (body + 0.3mm/side) |
| **Tab slot size** | **32.9 × 12.8 × 3.4 mm** |
| **Turret clearance** | **⌀12.4 mm × 6.6 mm above body** |

**CAD file:** [GrabCAD — SG90](https://grabcad.com/library/sg90-micro-servo-9g-tower-pro-1) (STEP, free account)

**Clearances:**
- 0.3 mm per side around body (press fit, holds by tabs)
- Tab ledge: horizontal shelf at 17mm from bottom, servo rests on it
- Turret + horn: needs ⌀25mm × 10mm open space above body for horn rotation
- Cable exit: 4 × 6mm slot in pocket wall

---

### 1.2 MG90S Metal Gear Servo (×3 in Pro)

**Used for:** L/R shoulder, waist yaw

| Spec | Value |
|---|---|
| Body L × W × H | 22.8 × 12.4 × 22.5 mm |
| Overall H (with shaft) | 32.5 mm |
| Tab-to-tab length | 32.1 mm |
| Tab thickness | 2.8 mm |
| Tab underside from bottom | 18.5 mm |
| Mounting holes | 2 per tab, ⌀2.0 mm |
| Spline OD | 4.8 mm |
| Weight | 13.4 g |
| Torque | 2.2 kg·cm at 4.8V |
| **Pocket size (with clearance)** | **23.4 × 13.0 × 23.1 mm** |
| **Tab slot size** | **32.7 × 13.0 × 3.4 mm** |

**CAD file:** [GrabCAD — MG90S](https://grabcad.com/library/mg90s-servo-high-detail-1) (STEP, free account)

**Clearances:** Same as SG90 — 0.3mm/side, tab mounting, horn clearance.

---

### 1.3 Dynamixel XL330-M288-T (×8 in Pro — legs only)

**Used for:** L/R hip yaw, L/R hip pitch, L/R knee, L/R ankle

| Spec | Value |
|---|---|
| Body W × H × D | 20.0 × 34.0 × 26.0 mm |
| Weight | 18 g |
| Stall torque (5V) | 0.52 N·m (5.3 kg·cm) |
| Stall torque (6V) | 0.60 N·m (6.1 kg·cm) |
| Voltage range | 3.7–6.0 V (recommended 5.0V) |
| Protocol | TTL half-duplex serial, 9600–4Mbps |
| Connector | JST 3-pin (daisy-chain: 2 ports per servo) |
| Resolution | 4096 steps/rev (0.088°) |
| Gear ratio | 288.4:1 |
| Mounting | 4× M2 holes on bottom face, 8mm × 16mm pattern |
| Horn | Cross-type, 4-arm, spline: 20-tooth |
| Horn screws | M2×4 (center) |
| **Pocket size (with clearance)** | **21.0 × 35.0 × 27.0 mm** (0.5mm/side) |
| **Horn clearance above body** | **⌀30 mm × 8 mm** |

**CAD file:** [GrabCAD — XL330-288-T](https://grabcad.com/library/xl330-288-t-1) (STEP, free account)
**Datasheet:** [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/)

**Clearances:**
- 0.5 mm per side (tighter tolerance than hobby servos — precision housing)
- Daisy-chain cable clearance: 8mm channel from servo to servo
- Horn rotation: ⌀30mm swept clear above mounting face
- M2 screw bosses: ⌀4mm posts at each mounting hole position

**Wiring note:** XL330 uses daisy-chain — each servo has 2 JST ports. Wire goes: Pi UART → first hip servo → knee → ankle. Only ONE data wire needed per leg (plus VCC + GND).

---

### 1.4 STS3215 Serial Bus Servo (alternative to XL330)

**Cheaper alternative for legs ($8-12 vs $24 per servo)**

| Spec | Value |
|---|---|
| Body L × W × H | 45.2 × 24.7 × 35.0 mm |
| Weight | 55 g |
| Stall torque (7.4V) | 19.5 kg·cm |
| Stall torque (12V) | 30 kg·cm |
| Voltage range | 6.0–14.0 V |
| Protocol | Half-duplex TTL serial (Feetech SCS/STS protocol), 38.4k–1Mbps |
| Connector | 5264-3P, 3-pin (GND/VCC/Signal), daisy-chain |
| Resolution | 4096 steps/rev (12-bit magnetic encoder) |
| Horn | 25T spline, OD 5.9mm |
| Mounting | 4× M3 holes on multiple faces |
| **Pocket size** | **47 × 26 × 37 mm** (0.5mm/side + tolerance) |

**Tradeoffs vs XL330:**
- ✓ Much cheaper ($8-12 vs $24)
- ✓ Much higher torque (19.5 vs 5.3 kg·cm at operating voltage)
- ✗ Much larger (45×25×35 vs 20×34×26)
- ✗ Much heavier (55g vs 18g)
- ✗ Needs separate higher voltage (7.4V+ vs 5V — can't share USB power)

**Recommendation:** Start with XL330 for the 250mm skeleton. STS3215 is better suited for a larger Pro skeleton (300mm+). At 250mm the STS3215 would dominate the leg cavity.

**CAD file:** [GrabCAD — FEETECH_STS3215](https://grabcad.com/library/feetech_sts3215-1) (STEP, free account)
**Datasheet:** [Feetech official PDF](https://www.feetechrc.com/Data/feetechrc/upload/file/20200611/6372749961523760249976542.pdf)

---

## 2. Compute Boards

### 2.1 Raspberry Pi Pico W (Spark tier)

| Spec | Value |
|---|---|
| Board L × W | 51.0 × 21.0 mm |
| Board thickness | 1.0 mm |
| Component height | 3.9 mm |
| Total H with headers | ~10 mm |
| Mounting holes | 4×, ⌀2.1 mm, spacing 47.0 × 11.4 mm, 2.0 mm from short edge |
| Weight | ~3 g |
| USB | Micro-USB on short edge |
| **Pocket size** | **57 × 25 × 12 mm** (with standoffs + cable space) |
| **Standoffs** | **4×, ⌀4.5 × 5mm tall, ⌀2.1 pilot hole** |

**CAD file:** [Official STEP](https://datasheets.raspberrypi.com/picow/PicoW-step.zip) (direct download, no login)

---

### 2.2 Raspberry Pi Zero 2 W (Core tier)

| Spec | Value |
|---|---|
| Board L × W | 65.0 × 30.0 mm |
| Height | ~5 mm |
| Mounting holes | 4× M2.5, ⌀2.75 mm, spacing 58 × 23 mm, 3.5 mm from edges |
| Weight | ~10 g |
| Connectors | mini-HDMI, 2× micro-USB (data + power), CSI camera, 40-pin GPIO |
| **Pocket size** | **70 × 35 × 15 mm** (with standoffs + cables) |
| **Standoffs** | **4×, ⌀5 × 5mm tall, ⌀2.75 pilot hole** |

**CAD file:** [GrabCAD](https://grabcad.com/library/raspberry-pi-zero-2-w-1) or [Geekworm Wiki STEP](https://wiki.geekworm.com/File:Raspberry-Pi-Zero-2-W.STEP)
**Mechanical drawing:** [Official PDF](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf)

---

### 2.3 Raspberry Pi 5 (4GB) (Pro tier)

| Spec | Value |
|---|---|
| Board L × W | 85.0 × 56.0 mm |
| Height | ~21 mm (USB/Ethernet stack is tallest) |
| Mounting holes | 4× M2.5, ⌀2.7 mm, spacing 58 × 49 mm, 3.5 mm from edges |
| Weight | ~46 g |
| Connectors | 2× USB 3.0, 2× USB 2.0, 2× micro-HDMI, USB-C power, GbE RJ45, 40-pin GPIO, microSD |
| **Pocket size** | **90 × 60 × 25 mm** (with standoffs + connector clearance) |
| **Standoffs** | **4×, ⌀5 × 6mm tall, ⌀2.7 pilot hole** |

**CAD file:** [Official STEP](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-step.zip) (direct download)
**Mechanical drawing:** [Official PDF](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf)

**Design note:** The Pi 5 is BIG (85×56mm). At 250mm skeleton height with a 100×80mm base plate, it fits but dominates the base cavity. Mount flat with the USB/Ethernet ports facing one edge for access. The GPIO header should face upward or inward toward the torso wire channel.

---

### 2.4 PCA9685 16-Channel PWM Servo Driver (Core+)

| Spec | Value |
|---|---|
| Board L × W | 62.5 × 25.4 mm |
| Height | ~12 mm (with pin headers + screw terminals) |
| Mounting holes | 4×, ⌀2.54 mm, spacing 55.9 × 19.1 mm |
| Communication | I2C (SDA, SCL) — only 2 wires to Pi |
| Servo headers | 16× 3-pin (on board edge) |
| **Pocket size** | **65 × 28 × 15 mm** |
| **Standoffs** | **4×, ⌀4.5 × 3mm tall, ⌀2.5 pilot hole** |

**CAD file:** [GrabCAD — PCA9685](https://grabcad.com/library/pca9685-pwm-servo-driver-for-arduino-1)

**Placement:** Stack above or beside the Pi in the base plate. Connect to Pi via 2-wire I2C. All PWM servo wires connect here.

---

## 3. Audio Components

### 3.1 Speaker — 28mm, 8Ω, 2W (Core+)

| Spec | Value |
|---|---|
| Diameter | 28.0 mm |
| Depth | 11–12 mm |
| Cone face / baffle opening | 25 mm |
| Weight | ~8 g |
| Mounting | Friction-fit in ⌀28mm recess, or adhesive |
| **Pocket size** | **⌀29 × 13 mm** (friction fit with 0.5mm clearance + 1mm behind) |

**Placement:** Front of torso (chest area). Cut a ⌀25mm sound port through the frame wall. The shell above it should have small holes or a grille pattern for sound to escape.

**CAD file:** Simple cylinder — model as ⌀28 × 12mm disc.

---

### 3.2 MAX98357A I2S Amplifier Breakout (Core+)

| Spec | Value |
|---|---|
| Board L × W × H | 19.4 × 17.8 × 3.0 mm |
| Mounting | No mounting holes — solder header or friction-mount in slot |
| Output | 2-pin screw terminal to speaker |
| Input | I2S from Pi (3 wires: BCLK, LRCLK, DIN) |
| **Pocket size** | **22 × 20 × 5 mm** (with header clearance) |

**Placement:** Directly behind the speaker in the torso. Wire runs to Pi GPIO.

**CAD file:** Model as a 19.4 × 17.8 × 3mm block.

---

### 3.3 INMP441 MEMS Microphone Breakout (Pro only)

| Spec | Value |
|---|---|
| Board L × W | 14.0 × 14.0 mm (square) |
| Height | ~3 mm |
| Sound port | Bottom-port — needs ⌀1mm hole in mounting surface |
| Pins | 6-pin: VDD, GND, SD, WS, SCK, L/R |
| Mounting | Adhesive or friction slot (no mounting holes) |
| **Pocket size** | **16 × 16 × 5 mm** |
| **Sound hole** | **⌀1.5 mm through frame wall** |

**Placement:** Head front (face area), behind a small hole in the frame. Position at approximately mouth or chin height on the character.

---

## 4. Sensors

### 4.1 MPU6050 IMU — GY-521 Breakout (Pro only)

| Spec | Value |
|---|---|
| Board L × W × H | 21 × 16 × 3.8 mm |
| Mounting holes | 2×, ~⌀3.0 mm (M2.5/M3) |
| Pins | 8-pin header (VCC, GND, SCL, SDA, XDA, XCL, AD0, INT) |
| Communication | I2C (shares bus with PCA9685) |
| **Pocket size** | **23 × 18 × 6 mm** |
| **Standoffs** | **2×, ⌀5 × 3mm, ⌀3.0 pilot hole** |

**Placement:** Center of torso, mounted flat and level. Critical for walking balance — must be firmly attached, not vibrating. Use rubber standoffs if possible to dampen servo vibration.

**CAD file:** [GrabCAD — GY-521](https://grabcad.com/library/gy-521-mpu6050-accelerometer-and-gyroscope-module-1)

---

### 4.2 HC-SR04 Mini Ultrasonic Sensor (Pro only)

| Spec | Value |
|---|---|
| Board L × W × H | 40 × 18 × 15.6 mm |
| Transducer ⌀ | ~10 mm each |
| Transducer spacing | ~16 mm center-to-center |
| Voltage | 3.0–5.5 V |
| Pins | 4 (VCC, Trig, Echo, GND) |
| **Pocket size** | **42 × 20 × 17 mm** |
| **Face openings** | **2× ⌀11 mm holes** for transducers, 16mm apart |

**Placement:** Head front — the two transducers look like "eyes." The shell needs two ⌀11mm holes aligned with the transducers.

**Note:** At 40×18mm this is large for a 250mm robot head. Consider the **RCWL-1601** (same pinout, slightly smaller) or a **VL53L0X ToF laser sensor** (12×18×2mm, I2C, single small lens) as a more compact alternative.

---

### 4.3 WS2812B NeoPixel LEDs (Core+)

| Spec | Value |
|---|---|
| Package (5050 SMD) | 5.0 × 5.0 × 1.6 mm |
| Through-hole (5mm) | ⌀5 mm × 8 mm tall |
| Pins | 4: VDD, GND, DIN, DOUT (daisy-chain) |
| Voltage | 3.5–5.3 V |
| Data | Single wire, daisy-chainable |
| **Pocket per LED** | **⌀6 × 3 mm** (for SMD) or **⌀5.5 × 9 mm** (through-hole) |

**Placement:**
- 2× in head (eyes) — behind ⌀5mm holes in frame, light shines through shell
- 1× in chest — behind small window in torso frame

**Wiring:** Daisy chain: Pi GPIO → eye 1 → eye 2 → chest LED. One data wire total.

---

## 5. Power Components

### 5.1 TP4056 USB-C LiPo Charging Board (Pro)

| Spec | Value |
|---|---|
| Board L × W × H | 25 × 17 × 4 mm |
| Mounting holes | 2× M2.5 |
| USB-C | Centered on short edge |
| Output | B+/B- (to battery), OUT+/OUT- (to load) |
| **Pocket size** | **27 × 19 × 6 mm** |

**Placement:** Base plate, near edge — USB-C port must be accessible through the frame and shell.

---

### 5.2 LiPo Battery 3.7V 1000mAh (Pro)

| Spec | Value |
|---|---|
| Model | 803040 (common pouch cell) |
| Dimensions | 40 × 30 × 8 mm |
| Weight | 18–20 g |
| Alt. slimmer | 502470: 70 × 24 × 5 mm, ~19 g |
| **Pocket size** | **42 × 32 × 10 mm** (with 1mm clearance + wire routing) |

**Placement:** Base plate cavity, beside or below the Pi. Must be removable for replacement/safety. Consider a slide-in tray.

**Safety:** Design a retaining clip or strap — LiPo should not rattle loose. Keep away from heat sources (servos under load).

---

### 5.3 USB-C Breakout Board (All tiers)

| Spec | Value |
|---|---|
| Board size | 20.4 × 14.2 × 5.0 mm (Adafruit 4090) |
| Pins | VBUS, GND, CC1, CC2, D+, D- |
| **Pocket size** | **22 × 16 × 7 mm** |

**Placement:** Base plate edge — port flush with frame exterior. Shell must have a matching cutout.

---

### 5.4 Power Switch (All tiers)

| Spec | Value |
|---|---|
| Type | Slide switch, SPDT |
| Common size | 12 × 6 × 5 mm |
| **Pocket size** | **14 × 8 × 7 mm** |

**Placement:** Base plate edge, accessible without removing shell. Toggle slot through frame + shell.

---

## 6. Skeleton Frame Dimensions (250mm)

### Updated Positions (scaled from 200mm)

| Parameter | Value | Notes |
|---|---|---|
| **Total height** | 250 mm | Base bottom to top of head servo stack |
| **Base plate** | 100 × 80 × 25 mm | Must contain Pi 5 (85×56mm) |
| **Base plate corner R** | 8 mm | |
| **Torso column** | ⌀28 mm (or 28×28 rounded rect) | Room for speaker + wiring |
| **Waist yaw servo Z** | 15 mm | Above base surface |
| **Waist roll servo Z** | 45 mm | Above waist yaw |
| **Shoulder Z** | 140 mm | ~56% of height |
| **Shoulder X** | ±48 mm | Shoulder spread from center |
| **Elbow Z** | 105 mm | Below shoulder |
| **Elbow X** | ±65 mm | Outward from shoulder |
| **Head pan Z** | 155 mm | Top of torso |
| **Head tilt Z** | 185 mm | Above pan |
| **Hip joint Z** | 0 mm | At base plate top surface |
| **Knee Z** | -60 mm | Below base |
| **Ankle Z** | -105 mm | Near ground |
| **Foot plate** | 40 × 25 × 5 mm | Each foot |

### Wire Channel Diameter

| Route | ⌀ | Notes |
|---|---|---|
| Main vertical (torso) | 8 mm | 16 servo wires + I2C + audio |
| Horizontal to shoulders | 6 mm | 2 servo cables per side |
| Leg channels | 6 mm | XL330 daisy-chain (3 wires per leg) |
| Speaker/mic wires | 4 mm | Separate from servo bundle |

---

## 7. CAD File Download Checklist

| Component | Source | Status |
|---|---|---|
| SG90 Servo | [GrabCAD](https://grabcad.com/library/sg90-micro-servo-9g-tower-pro-1) | You have this ✓ |
| MG90S Servo | [GrabCAD](https://grabcad.com/library/mg90s-servo-high-detail-1) | You have this ✓ |
| Pi Pico W | [Official STEP](https://datasheets.raspberrypi.com/picow/PicoW-step.zip) | You have this ✓ |
| Pi Zero 2W | [GrabCAD](https://grabcad.com/library/raspberry-pi-zero-2-w-1) | Download needed |
| Pi 5 (4GB) | [Official STEP](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-step.zip) | Download needed |
| XL330-M288-T | [GrabCAD — XL330-288-T](https://grabcad.com/library/xl330-288-t-1) | Download needed |
| STS3215 (reference) | [GrabCAD — FEETECH_STS3215](https://grabcad.com/library/feetech_sts3215-1) | Optional — for size comparison |
| PCA9685 | [GrabCAD](https://grabcad.com/library/pca9685-pwm-servo-driver-for-arduino-1) | Download needed |
| MPU6050 GY-521 | [GrabCAD](https://grabcad.com/library/gy-521-mpu6050-accelerometer-and-gyroscope-module-1) | Download needed |
| MAX98357A | Model as 19.4 × 17.8 × 3mm block | Simple geometry |
| INMP441 mic | Model as 14 × 14 × 3mm block | Simple geometry |
| TP4056 charger | Model as 25 × 17 × 4mm block | Simple geometry |
| Speaker 28mm | Model as ⌀28 × 12mm cylinder | Simple geometry |
| LiPo battery | Model as 40 × 30 × 8mm block | Simple geometry |
| USB-C breakout | Model as 20 × 14 × 5mm block | Simple geometry |
| WS2812B LED | Model as 5 × 5 × 1.6mm block | Tiny — just mark positions |

---

## 8. Clearance Rules Summary

| Rule | Value | Applies to |
|---|---|---|
| Servo body clearance | 0.3 mm/side (SG90/MG90S) | All hobby servo pockets |
| Servo body clearance | 0.5 mm/side (XL330) | All Dynamixel pockets |
| Horn rotation clearance | ⌀25 mm above SG90/MG90S | Every servo with external horn |
| Horn rotation clearance | ⌀30 mm above XL330 | Leg servos |
| Board standoff height | 5–6 mm | All PCBs (airflow underneath) |
| Board perimeter clearance | 2 mm/side | Connector access + tolerance |
| Speaker front clearance | Need ⌀25mm sound hole in frame | Torso front wall |
| Mic sound hole | ⌀1.5 mm through frame | Head face |
| Wire channel minimum | ⌀4 mm | Any cable run |
| Magnet pocket | ⌀6.1 × 3.1 mm deep | All 40+ magnet positions |
| Shell clearance from frame | 1.5–3.0 mm | Depends on zone (see INTERFACE_SPEC) |
| Draft taper for shell removal | 1.5–2.0° | Along removal direction |
