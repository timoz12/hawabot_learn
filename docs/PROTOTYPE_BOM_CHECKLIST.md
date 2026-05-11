# HawaBot Prototype BOM Checklist

_Last updated: 2026-05-05_

Build Spark first, validate, then expand to Pro with Dynamixel legs.

---

## Phase 1: Spark Prototype (7 DOF + Speaker)

Build and validate the Spark experience: servos, speaker, WiFi API.

### Already Have
- [x] ESP32-S3-DevKitC-1 dev board

### Purchased

| Item | Qty | Source | Price | Status |
|---|---|---|---|---|
| HiLetgo PCA9685 16-ch PWM breakout (2-pack) | 2 | Amazon (B07BRS249H) | $14 | [x] Ordered |
| SG90 micro servos | 5 | Amazon | $10 | [x] Ordered |
| MG90S metal gear servos | 2 | Amazon | $8 | [x] Ordered |
| MAX98357A I2S amp breakout | 1 | Adafruit (#3006) | $6 | [x] Ordered |
| Speaker (3W, 4ohm, 28mm) | 1 | Adafruit / Amazon | $2 | [x] Ordered |
| Breadboard (full size) | 1 | Amazon | $5 | [x] Ordered |
| Jumper wires (M-M) | 1 pack | Amazon | $3 | [x] Ordered |
| Jumper wires (M-F) | 1 pack | Amazon | $3 | [x] Ordered |
| 5V 3A USB-C power supply | 1 | Amazon | $10 | [x] Ordered |

Servo allocation:
- SG90 × 5: head pan, head tilt, L shoulder roll, R shoulder roll, waist yaw
- MG90S × 2: L shoulder pitch, R shoulder pitch
- PCA9685: 1 for use, 1 spare

### Phase 1 Total: ~$61

### What Phase 1 Validates

- [ ] ESP32-S3 → I2C → PCA9685 → 7 servos moving
- [ ] I2S audio out (speaker playback via MAX98357A)
- [ ] WiFi REST/WebSocket API (phone ↔ robot)
- [ ] OTA firmware updates
- [ ] Full Spark experience: head tracks, shoulders wave, waist turns, speaker talks

### Wiring (Phase 1)

```
ESP32-S3-DevKitC-1
  │
  ├─ I2C (GPIO8 SDA, GPIO9 SCL)
  │    └─ PCA9685 (addr 0x40) ──► 7 servo PWM channels
  │         ├─ CH0: head_pan (SG90)
  │         ├─ CH1: head_tilt (SG90)
  │         ├─ CH2: left_shoulder_pitch (MG90S)
  │         ├─ CH3: left_shoulder_roll (SG90)
  │         ├─ CH4: right_shoulder_pitch (MG90S)
  │         ├─ CH5: right_shoulder_roll (SG90)
  │         └─ CH6: waist_yaw (SG90)
  │
  ├─ I2S0 (GPIO4 BCLK, GPIO5 LRCLK, GPIO6 DOUT)
  │    └─ MAX98357A ──► Speaker (28mm, 3W, 4ohm)
  │
  └─ WiFi ──► Phone/tablet app

Power:
  5V 3A USB-C supply ──► PCA9685 V+ screw terminal (servo power)
  Dev board USB ──► ESP32-S3 logic power (separate from servo power)
```

---

## Phase 2: Pro Expansion (Add Legs + Arms + Sensors — 19 DOF)

Once Spark firmware and control are validated, add Dynamixel legs, arm servos, sensors, mic, and battery for walking.

### To Purchase

#### Dynamixel Servos + Wiring

| Item | Qty | Source | Est. Price | Status |
|---|---|---|---|---|
| XL330-M288-T servos | 8 | Robotis | $216 | [ ] |
| XL330 cable (3-pin, 100mm) | 10 | Robotis | $10 | [ ] |
| U2D2 (USB-Dynamixel adapter) | 1 | Robotis | $30 | [ ] |
| XL330 power board / 5V hub | 1 | Robotis | $10 | [ ] |
| FPX330-H101 idler frame kit (4-pack) | 1 | Robotis | $11 | [ ] |

Servo allocation (8x XL330):
- L/R hip yaw (2), L/R hip pitch (2), L/R knee pitch (2), L/R ankle pitch (2)

Note: Shoulders stay MG90S. Upgrade to XL330 later only if cantilever proves problematic under full arm load.

#### Additional Arm Servos

| Item | Qty | Source | Est. Price | Status |
|---|---|---|---|---|
| SG90 micro servos (elbows + hands) | 4 | Amazon | $8 | [ ] |

Servo allocation: L/R elbow pitch (2x SG90), L/R hand pitch (2x SG90)

#### Sensors

| Item | Qty | Source | Est. Price | Status |
|---|---|---|---|---|
| GY-521 (MPU6050 IMU breakout) | 1 | Amazon | $3 | [ ] |
| FSR 402 (force sensitive resistors) | 4 | Adafruit (#166) / Amazon | $8 | [ ] |
| 10K resistors (for FSR voltage dividers) | 4 | Amazon (assortment) | $1 | [ ] |
| INMP441 I2S MEMS mic breakout | 1 | Amazon | $3 | [ ] |
| OV2640 camera module (DVP) | 1 | Amazon / AliExpress | $5 | [ ] |

#### Power (Walking Needs Battery)

| Item | Qty | Source | Est. Price | Status |
|---|---|---|---|---|
| LiPo battery (7.4V 2S, 1000mAh) | 1 | Amazon | $12 | [ ] |
| TP4056 charger module | 1 | Amazon | $2 | [ ] |
| 5V buck converter (LiPo → 5V) | 1 | Amazon | $3 | [ ] |

### Phase 2 Total: ~$322

### What Phase 2 Validates

- [ ] Dynamixel bus control from ESP32-S3 UART1
- [ ] Mixed bus: PCA9685 (SG90/MG90S) + Dynamixel (XL330) simultaneously
- [ ] I2S audio in (mic capture + WiFi stream to phone)
- [ ] I2C IMU reading (tilt/acceleration)
- [ ] FSR analog reading (foot contact detection)
- [ ] DVP camera streaming (if applicable)
- [ ] Basic walking gait (pre-programmed)
- [ ] IMU + FSR assisted balance
- [ ] Battery operation (untethered walking)
- [ ] Full Pro experience: walks, talks, gestures, senses

### Wiring (Phase 2 additions)

```
ESP32-S3-DevKitC-1 (added to Phase 1 wiring)
  │
  ├─ I2C (shared bus, same GPIO8/9)
  │    └─ MPU6050 (addr 0x68) ──► IMU
  │
  ├─ I2S1 (GPIO15 BCLK, GPIO16 LRCLK, GPIO7 DIN)
  │    └─ INMP441 ──► Mic
  │
  ├─ ADC (GPIO1, GPIO2, GPIO3, GPIO10)
  │    └─ 4x FSR 402 (via 10K voltage dividers) ──► Foot contact
  │
  ├─ DVP (GPIO10-14, GPIO38-40) — if camera used
  │    └─ OV2640 ──► Camera
  │
  ├─ PCA9685 CH7-CH10 ──► 4x SG90 (elbows + hands)
  │
  └─ UART1 (GPIO17 TX, GPIO18 RX)
       └─ Dynamixel half-duplex bus ──► 8x XL330 (daisy-chained)

Power (Phase 2):
  LiPo 7.4V ──► 5V buck converter ──► PCA9685 V+ (servos)
                                   ──► XL330 power hub
                                   ──► ESP32-S3 (via 5V pin)
```

---

## Grand Total

| Phase | Cost | Status |
|---|---|---|
| ESP32-S3-DevKitC-1 | (already had) | [x] |
| **Phase 1: Spark** | **$61** | **[x] Ordered** |
| **Phase 2: Pro expansion** | **$322** | [ ] After Spark validated |
| **Combined** | **$383** | |

---

## Custom PCB Reference (Future — After Breadboard Prototype Validated)

Once Phase 1 is working on the breadboard, design a custom PCB (~55×35mm, 2-layer) in KiCad that consolidates everything onto one board. This replaces the breadboard + breakout boards for production.

### PCB Component Mapping (Breakout → IC)

| Breadboard Breakout | Production PCB Equivalent | Package | I/F |
|---|---|---|---|
| ESP32-S3-DevKitC-1 | ESP32-S3-WROOM-1 module | Castellated SMD | — |
| HiLetgo PCA9685 board | PCA9685PW IC (TSSOP-28) + 25MHz crystal | SMD | I2C |
| MAX98357A breakout | MAX98357AETE+T IC (TQFN-16) | SMD | I2S |
| INMP441 mic breakout (Phase 2) | INMP441ACEZ IC (LGA) | SMD | I2S |
| GY-521 IMU breakout (Phase 2) | MPU-6050 IC (QFN-24) or ICM-42688-P | SMD | I2C |
| FSR voltage dividers (Phase 2) | 4x 10K resistors + ADC input traces | 0402/0603 | Analog |
| 5V USB-C power supply | USB-C connector + AMS1117-3.3 LDO | SMD | — |
| Breadboard + jumpers | PCB traces + JST-SH servo headers | — | — |

### PCB Features

| Feature | Spark (populated) | Pro (additionally populated) |
|---|---|---|
| ESP32-S3-WROOM-1 module | Yes | Yes |
| PCA9685 PWM driver + 25MHz xtal | Yes | Yes |
| MAX98357A I2S amp | Yes | Yes |
| 9× 3-pin servo JST headers | 7 used | All 11 used |
| USB-C power + programming | Yes | Yes |
| 3.3V LDO (AMS1117-3.3) | Yes | Yes |
| 5V servo power rail + bulk caps | Yes | Yes |
| Boot + Reset buttons | Yes | Yes |
| INMP441 MEMS mic | **DNP** | Yes |
| MPU6050 IMU | **DNP** | Yes |
| 4× FSR analog inputs + dividers | **DNP** | Yes |
| OV2640 camera FPC connector | **DNP** | Yes |
| UART1 Dynamixel bus header | **DNP** | Yes |
| Battery connector (JST-PH 2-pin) | **DNP** | Yes |
| TP4056 charging circuit | **DNP** | Yes |

DNP = Do Not Populate (pads on PCB but no component soldered — saves cost for Spark, populated for Pro)

### PCB Design Notes

- **2-layer sufficient** — no impedance matching needed
- **Antenna keep-out:** No copper/ground pour within 15mm of ESP32-S3 antenna end
- **PCA9685:** Needs 25MHz crystal + 2× 22pF load caps + 10µF decoupling
- **MAX98357A:** Needs ferrite bead on PVDD + 10µF decoupling + gain select resistor
- **USB-C:** CC1/CC2 need 5.1K pull-down resistors for 5V power delivery
- **Servo power rail:** Separate from 3.3V logic. Common GND. Bulk cap (470µF) near PCA9685.
- **Design tool:** KiCad → fabricate at JLCPCB with SMT assembly
- **Estimated size:** ~55 × 35 × 8mm (fits in 250mm robot torso cavity)
- **Estimated cost:** ~$2-3/board + ~$15 assembly (prototype qty at JLCPCB)

### PCB Pin Allocation (Matching Breadboard Prototype)

| ESP32-S3 GPIO | Function | Phase |
|---|---|---|
| GPIO8 | I2C SDA (PCA9685 + MPU6050) | 1 |
| GPIO9 | I2C SCL (PCA9685 + MPU6050) | 1 |
| GPIO4 | I2S0 BCLK (MAX98357A) | 1 |
| GPIO5 | I2S0 LRCLK (MAX98357A) | 1 |
| GPIO6 | I2S0 DOUT (MAX98357A) | 1 |
| GPIO15 | I2S1 BCLK (INMP441) | 2 |
| GPIO16 | I2S1 LRCLK (INMP441) | 2 |
| GPIO7 | I2S1 DIN (INMP441) | 2 |
| GPIO17 | UART1 TX (Dynamixel bus) | 2 |
| GPIO18 | UART1 RX (Dynamixel bus) | 2 |
| GPIO1 | ADC — FSR left front | 2 |
| GPIO2 | ADC — FSR left rear | 2 |
| GPIO3 | ADC — FSR right front | 2 |
| GPIO10 | ADC — FSR right rear | 2 |
| GPIO43 | UART0 TX (USB debug) | 1 |
| GPIO44 | UART0 RX (USB debug) | 1 |
| GPIO48 | Status LED (on-board RGB) | 1 |

**Avoid:** GPIO0, 45, 46 (strapping pins). GPIO19, 20 (USB OTG). GPIO35-37 (reserved on N8R8).

When you breadboard prototype works, these exact pin assignments transfer to the KiCad schematic — no firmware changes needed.
