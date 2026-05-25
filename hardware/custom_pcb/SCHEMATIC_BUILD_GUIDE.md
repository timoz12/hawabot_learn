# HawaBot Controller Board — Complete Schematic Build Guide

**Version:** 1.1 | **Date:** May 24, 2026 | **Author:** Hawa Labs
**This document is self-contained. No internet or Claude session required.**

---

## How to Use This Guide

Each step has three parts:
1. **DO:** Exact KiCad actions to perform
2. **VERIFY:** How to confirm it's correct
3. **EXPECTED RESULT:** What you should see if done correctly

**Do NOT proceed to the next step until all checkboxes in VERIFY are checked.**

If something doesn't match, STOP and refer to the datasheet listed for that step. All datasheets are in `hardware/custom_pcb/datasheets/`.

---

## Reference Files (Keep These Open)

| File | When to Use |
|------|-------------|
| `datasheets/ESP32-S3-WROOM-1.pdf` | ESP32-S3 pin assignments |
| `datasheets/PCA9685.pdf` | Servo driver pinout + reference circuit |
| `datasheets/MAX98357A.pdf` | Audio amp reference circuit |
| `datasheets/C51118_AP2112K.pdf` | LDO pinout |
| `datasheets/C16581_TP4056.pdf` | Battery charger pinout (Pro only) |
| `datasheets/C351410_DW01A.pdf` | Battery protection pinout (Pro only) |
| `datasheets/C908265_FUXINSEMI_FS8205A.pdf` | Battery MOSFET pinout (Pro only) |
| `datasheets/C7519_USBLC6.pdf` | USB ESD protection pinout |
| `datasheets/MPU6050.pdf` | IMU pinout (Pro only) |

---

## Board Overview

**Single PCB, ~60×40mm, 2-layer.** Same board for Spark and Pro — Pro populates additional components (marked DNP for Spark).

```
POWER IN (USB-C) ──► PTC fuse ──► +5V ──► D_OR1 ──►─┐
                                   │                  ├──► +5V_SERVO ──► servos
                                   └──► TP4056 (Pro)  │        │
                                          ↕           │        └──► AP2112K ──► +3V3
                                       VBAT ──► Boost │             (ESP32, PCA9685)
                                        (Pro)  5.1V ──► D_OR2 ──►─┘

CONTROL:
  ESP32-S3 ──I2C──► PCA9685 ──PWM──► 7-16 servo headers
            ──I2S──► MAX98357A ──► Speaker
            ──PDM──► SPH0641 mic (Pro DNP)
            ──I2C──► MPU6050 IMU (Pro DNP)
            ──UART──► Dynamixel bus (Pro DNP)
            ──ADC──► FSRs (Pro DNP)
            ──DVP──► OV2640 camera (Pro DNP)
```

### Component Count

| Section | Components | Populated |
|---------|-----------|-----------|
| USB-C input + ESD | 8 | All tiers |
| 3.3V LDO | 3 | All tiers |
| ESP32-S3 support | 6 | All tiers |
| PCA9685 servo driver | 3 | All tiers |
| MAX98357A audio amp | 5 | All tiers |
| Servo power rail | 3 | All tiers |
| Servo headers (3-pin) | 7-16 | All tiers (7 Spark, 16 Pro) |
| Speaker + boot button | 3 | All tiers |
| TP4056 charger (Pro) | 9 | Pro only (DNP Spark) |
| DW01A/FS8205A protection (Pro) | 5 | Pro only (DNP Spark) |
| NTC thermistor (Pro) | 2 | Pro only (DNP Spark) |
| Boost converter TPS61023 (Pro) | 7 | Pro only (DNP Spark) |
| OR-ing diodes (Pro) | 2 | Pro only (DNP Spark) |
| SPH0641 mic (Pro) | 2 | Pro only (DNP Spark) |
| MPU6050 IMU (Pro) | 4 | Pro only (DNP Spark) |
| Dynamixel connector (Pro) | 1 | Pro only (DNP Spark) |
| Camera connector (Pro) | 1 | Pro only (DNP Spark) |
| FSR connectors + dividers (Pro) | 8 | Pro only (DNP Spark) |
| **TOTAL** | **~70-80** | Spark ~40, Pro ~70-80 |

---

## GPIO Pin Allocation — Master Reference

**Print this table. Reference it for every wiring step.**

| GPIO | Function | Bus/Interface | Phase | Net Label |
|------|----------|---------------|-------|-----------|
| 0 | BOOT button | Digital (strapping) | 1 | `BOOT` |
| 1 | FSR left front | ADC1_CH0 | 2 (Pro) | `FSR_LF` |
| 2 | FSR left rear | ADC1_CH1 | 2 (Pro) | `FSR_LR` |
| 4 | I2S0 BCLK (speaker) | I2S | 1 | `I2S_BCLK` |
| 5 | I2S0 LRCLK (speaker) | I2S | 1 | `I2S_LRCLK` |
| 6 | I2S0 DOUT (speaker) | I2S | 1 | `I2S_DOUT` |
| 7 | PDM DATA (mic) | PDM | 2 (Pro) | `PDM_DATA` |
| 8 | I2C SDA | I2C | 1 | `I2C_SDA` |
| 9 | I2C SCL | I2C | 1 | `I2C_SCL` |
| 11 | FSR right front | ADC2_CH0 | 2 (Pro) | `FSR_RF` |
| 12 | FSR right rear | ADC2_CH1 | 2 (Pro) | `FSR_RR` |
| 15 | PDM CLK (mic) | PDM | 2 (Pro) | `PDM_CLK` |
| 17 | UART1 TX (Dynamixel) | UART | 2 (Pro) | `DXL_TX` |
| 18 | UART1 RX (Dynamixel) | UART | 2 (Pro) | `DXL_RX` |
| 19 | USB D- | USB | 1 | `USB_D-` |
| 20 | USB D+ | USB | 1 | `USB_D+` |
| 43 | UART0 TX (debug) | USB-Serial | 1 | — |
| 44 | UART0 RX (debug) | USB-Serial | 1 | — |

**Reserved / Avoid:** GPIO0 (strapping, used as boot button with pull-up), GPIO3 (strapping), GPIO45 (strapping), GPIO46 (strapping + input only). GPIO35-37 reserved for Octal SPI PSRAM on N16R8 variant — do NOT use for camera DVP or any other function.

---

# SECTION A: CORE (All Tiers — Always Populated)

---

## Setup

**DO:**
1. File → New → Project → create in `hardware/custom_pcb/kicad/hawabot_controller/`
2. Save as `hawabot_controller.kicad_sch`
3. Edit → Sheet Properties → Title: `HawaBot Controller Board V1.0`, Rev: `1.0`, Company: `Hawa Labs LLC`
4. Add custom symbol libraries: Preferences → Manage Symbol Libraries → Project tab:
   - `SPH0641` → `../SPH0641/SPH0641LU4H-1.kicad_sym`
   - `TP4056` → `../TP4056/TP4056.kicad_sym`
   - `DW01A` → `../DW01A/DW01A.kicad_sym`
   - `FS8205A` → `../FS8205-SOT236/FS8205.kicad_sym`
5. Add custom footprint libraries: Preferences → Manage Footprint Libraries → Project tab:
   - Add paths for SPH0641, TP4056, DW01A, FS8205-SOT236 folders

**VERIFY:**
- [ ] Title block shows "HawaBot Controller Board V1.0"
- [ ] All 4 custom symbol libraries load without errors (test: Place → Add Symbol → search "SPH0641" → should find it)

---

## Step 1: USB-C Input Section (8 components)

**PURPOSE:** USB-C power input with overcurrent protection, ESD protection, and data lines for programming.

**DATASHEET:** Open `datasheets/C7519_USBLC6.pdf` page 1 (pin diagram)

**DO:**
1. Place J1: `Connector:USB_C_Receptacle_USB2.0_14P`
   - Footprint: `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`
   - LCSC: C165948
2. Place R1, R2: `Device:R` → Value: `5.1k`, Footprint: `R_0402_1005Metric`, LCSC: C25905
   - Wire: J1 CC1 → R1 → GND
   - Wire: J1 CC2 → R2 → GND
3. Place F1: `Device:Polyfuse` → Value: `1.5A`, Footprint: `R_1206_3216Metric`
   - Wire: J1 VBUS → F1 pin 1, F1 pin 2 → label `+5V`
   - **NOTE:** 1.5A rating (not 750mA like Pod) — servo current can exceed 1A
4. Place D1: `Device:D_TVS` → Value: `ESD5Z5.0T1G`, Footprint: `D_SOD-523`, LCSC: C82044
   - Wire: `+5V` to GND (clamps ESD/transient spikes)
5. Place U5: `Power_Protection:USBLC6-2SC6` → Footprint: `SOT-23-6`, LCSC: C7519
   - Wire per USBLC6 datasheet:
   - J1 D+ → U5 pin 3 (I/O2) → U5 pin 4 (I/O2) → label `USB_D+`
   - J1 D- → U5 pin 1 (I/O1) → U5 pin 6 (I/O1) → label `USB_D-`
   - U5 pin 5 (VBUS) → `+5V`
   - U5 pin 2 (GND) → GND
6. Place C1: `Device:C` → `100nF`, 0402, C1525 → between `+5V` and GND
7. Place C2: `Device:C` → `10uF`, 0805, C15850 → between `+5V` and GND

**VERIFY:**
- [ ] Power path: J1 VBUS → F1 (1.5A PTC) → `+5V` rail with D1 TVS and C1/C2 decoupling
- [ ] USB data: J1 D+/D- pass through U5 → `USB_D+`/`USB_D-` labels
- [ ] CC resistors: R1/R2 (5.1k) from CC1/CC2 to GND
- [ ] Open USBLC6 datasheet: Pin 1=I/O1(D-), Pin 2=GND, Pin 3=I/O2(D+), Pin 4=I/O2(D+), Pin 5=VBUS, Pin 6=I/O1(D-)
- [ ] F1 is rated **1.5A** (NOT 750mA)
- [ ] Component count: 8 (J1, R1, R2, F1, D1, U5, C1, C2)

**EXPECTED RESULT:** USB-C connector with overcurrent protection (F1), ESD protection (D1 + U5), CC pull-downs for power negotiation, and data lines for ESP32 programming.

---

## Step 2: 3.3V LDO (3 components)

**PURPOSE:** Regulate +5V down to +3V3 for ESP32, PCA9685 logic, and I2C sensors.

**DATASHEET:** Open `datasheets/C51118_AP2112K.pdf` page 1-2 (SOT-25 pin diagram)

**DO:**
1. Place U2: `Regulator_Linear:AP2112K-3.3` → Footprint: `SOT-23-5`, LCSC: C51118
2. Wire:

| U2 Pin | Name | Wire To |
|--------|------|---------|
| 1 | VIN | `+5V` |
| 2 | GND | GND |
| 3 | EN | `+5V` (tie to VIN = always enabled) |
| 4 | NC | No connect marker (X) |
| 5 | VOUT | Label `+3V3` |

3. Place C3: `Device:C` → `10uF`, 0805, C15850 → between `+5V` (U2 VIN) and GND
4. Place C4: `Device:C` → `10uF`, 0805, C15850 → between `+3V3` (U2 VOUT) and GND

**VERIFY:**
- [ ] Pin 1 = VIN → `+5V`
- [ ] Pin 3 = EN → tied to VIN (active HIGH, always enabled)
- [ ] Pin 4 = NC → no connect marker
- [ ] Pin 5 = VOUT → `+3V3`
- [ ] C3 on input, C4 on output — both to GND
- [ ] Component count: 3 (U2, C3, C4)

**EXPECTED RESULT:** 3.3V regulated output from USB 5V. Powers ESP32-S3, PCA9685 VDD, I2C bus.

---

## Step 3: ESP32-S3 Module + Support (5 components)

**PURPOSE:** Place the MCU module with boot/reset circuitry.

**DATASHEET:** Open `datasheets/ESP32-S3-WROOM-1.pdf` — pin table

**DO:**
1. Place U1: `RF_Module:ESP32-S3-WROOM-1` → Footprint: `RF_Module:ESP32-S3-WROOM-1`
   - LCSC: C2913202 (N16R8 variant — same footprint as all WROOM-1 variants)
2. Wire power:
   - U1 3V3 → `+3V3`
   - U1 GND (all GND pins) → GND
3. Wire USB:
   - U1 GPIO19 → `USB_D-` (from Step 1)
   - U1 GPIO20 → `USB_D+` (from Step 1)
4. Place R3: `Device:R` → `10k`, 0402, C25744 — EN pull-up
   - Wire: `+3V3` → R3 → U1 EN pin
5. Place C5: `Device:C` → `100nF`, 0402, C1525 — EN decoupling
   - Wire: U1 EN → C5 → GND (RC reset circuit with R3)
6. Place R4: `Device:R` → `10k`, 0402, C25744 — BOOT pull-up
   - Wire: `+3V3` → R4 → U1 GPIO0
7. Place SW1: `Switch:SW_Push` → Footprint: tactile switch, LCSC: C318884
   - Wire: U1 GPIO0 → SW1 → GND (pressing SW1 pulls GPIO0 LOW for boot mode)
8. Place SW2: `Switch:SW_Push` → Footprint: tactile switch, LCSC: C318884
   - Wire: U1 EN → SW2 → GND (pressing SW2 resets the ESP32)

**VERIFY:**
- [ ] U1 3V3 → `+3V3`, all GND pins → GND
- [ ] GPIO19 → `USB_D-`, GPIO20 → `USB_D+` — **NOT swapped** (check datasheet)
- [ ] R3 (10k) pulls EN HIGH through to +3V3
- [ ] C5 (100nF) from EN to GND — creates RC reset delay
- [ ] R4 (10k) pulls GPIO0 HIGH (normal boot)
- [ ] SW1 (BOOT) pulls GPIO0 LOW when pressed
- [ ] SW2 (RESET) pulls EN LOW when pressed — resets the ESP32
- [ ] **Boot mode entry:** hold SW1, press SW2, release SW2, release SW1
- [ ] Component count: 6 (R3, R4, C5, SW1, SW2 + U1 already placed)

**EXPECTED RESULT:** ESP32-S3 module with power, USB data, boot button (SW1), and reset button (SW2). Hold BOOT + press RESET to enter download mode.

---

## Step 4: I2C Bus (2 components)

**PURPOSE:** Shared I2C bus for PCA9685 servo driver and MPU6050 IMU (Pro).

**DO:**
1. Place R5: `Device:R` → `4.7k`, 0402, C25900 — SDA pull-up
   - Wire: `+3V3` → R5 → label `I2C_SDA`
   - Wire: U1 GPIO8 → `I2C_SDA`
2. Place R6: `Device:R` → `4.7k`, 0402, C25900 — SCL pull-up
   - Wire: `+3V3` → R6 → label `I2C_SCL`
   - Wire: U1 GPIO9 → `I2C_SCL`

**VERIFY:**
- [ ] R5 (4.7k) pulls SDA to +3V3
- [ ] R6 (4.7k) pulls SCL to +3V3
- [ ] GPIO8 = SDA, GPIO9 = SCL (matches Pod and all documentation)
- [ ] Net labels `I2C_SDA` and `I2C_SCL` placed — these will connect to PCA9685, MPU6050

**EXPECTED RESULT:** I2C bus with pull-ups. Ready for PCA9685 (Step 5) and MPU6050 (Section B).

---

## Step 5: PCA9685 Servo PWM Driver (3 components)

**PURPOSE:** 16-channel PWM driver for SG90/MG90S hobby servos. This is the core servo control IC.

**DATASHEET:** Open `datasheets/PCA9685.pdf` — page 6, Table 4 (TSSOP-28 pinout)

**CRITICAL: The PCA9685 TSSOP-28 pin numbers are NOT intuitive. Verify every pin against the datasheet. The bare IC has NO "VSERVO" pin — that is a breakout board concept.**

**PCA9685 TSSOP-28 Complete Pin Map (from datasheet Table 4):**

| Pin | Function | Pin | Function |
|-----|----------|-----|----------|
| 1 | A0 | 15 | LED8 |
| 2 | A1 | 16 | LED9 |
| 3 | A2 | 17 | LED10 |
| 4 | A3 | 18 | LED11 |
| 5 | A4 | 19 | LED12 |
| 6 | LED0 | 20 | LED13 |
| 7 | LED1 | 21 | LED14 |
| 8 | LED2 | 22 | LED15 |
| 9 | LED3 | 23 | OE (active LOW) |
| 10 | LED4 | 24 | A5 |
| 11 | LED5 | 25 | EXTCLK |
| 12 | LED6 | 26 | SCL |
| 13 | LED7 | 27 | SDA |
| 14 | VSS | 28 | VDD |

**DO:**
1. Place U3: `LED_Driver:PCA9685PW` → Footprint: `Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm`
   - LCSC: C2678753
2. Wire power:
   - U3 VDD (**pin 28**) → `+3V3` (logic power)
   - U3 VSS (**pin 14**) → GND
3. Wire I2C:
   - U3 SDA (**pin 27**) → `I2C_SDA`
   - U3 SCL (**pin 26**) → `I2C_SCL`
4. Wire address pins (all to GND = address 0x40):
   - U3 A0 (**pin 1**) → GND
   - U3 A1 (**pin 2**) → GND
   - U3 A2 (**pin 3**) → GND
   - U3 A3 (**pin 4**) → GND
   - U3 A4 (**pin 5**) → GND
   - U3 A5 (**pin 24**) → GND
5. Wire control pins:
   - U3 OE (**pin 23**) → GND (output always enabled — OE is active LOW)
   - U3 EXTCLK (**pin 25**) → GND (use internal 25MHz oscillator — no external crystal needed)
6. Place C6: `Device:C` → `100nF`, 0402, C1525 — VDD decoupling
   - Wire: `+3V3` → C6 → GND (close to U3 VDD pin 28)
7. Place C7: `Device:C` → `10uF`, 0805, C15850 — VDD bulk
   - Wire: `+3V3` → C7 → GND

**PWM outputs (pins 6-13, 15-22) — leave FLOATING for now. Servo headers are wired in Step 7.**

**NOTE:** The PCA9685 IC has NO "VSERVO" pin. On the Adafruit breakout board, "V+" is a separate screw terminal for servo power that connects directly to servo header power pins, bypassing the IC entirely. On our custom PCB, servo 5V power goes directly from the `+5V_SERVO` rail to the servo header power pins (Step 6) — it does not pass through the PCA9685 IC at all.

**VERIFY:**
- [ ] VDD (**pin 28**) → `+3V3` — **NOT +5V**
- [ ] VSS (**pin 14**) → GND
- [ ] SDA (**pin 27**) → `I2C_SDA` — **NOT pin 23** (pin 23 is OE)
- [ ] SCL (**pin 26**) → `I2C_SCL` — **NOT pin 24** (pin 24 is A5)
- [ ] A0-A4 (**pins 1-5**) → GND — **NOT pins 17-21** (those are LED10-LED14)
- [ ] A5 (**pin 24**) → GND
- [ ] OE (**pin 23**) → GND (enabled) — **NOT pin 22** (pin 22 is LED15)
- [ ] EXTCLK (**pin 25**) → GND (internal oscillator, no crystal needed)
- [ ] **No crystal (Y1) needed** — PCA9685 has internal 25MHz oscillator. ±10% is fine for 50Hz servo PWM.
- [ ] **No "VSERVO" connection to the IC** — servo power goes to headers directly
- [ ] C6 (100nF) + C7 (10µF) decoupling on VDD
- [ ] Cross-check EVERY pin against PCA9685.pdf Table 4 (page 6)
- [ ] Component count: 3 (U3, C6, C7)

**EXPECTED RESULT:** PCA9685 connected to ESP32-S3 via I2C at address 0x40. 16 PWM outputs available. Logic at 3.3V. No crystal. Servo power handled separately in Step 6.

---

## Step 6: Servo Power Rail (3 components)

**PURPOSE:** Separate 5V high-current power rail for servos. This is critical — servos can draw 2A+ at stall and must NOT be powered through the LDO.

**DO:**
1. Create net label `+5V_SERVO`
2. **Spark (no battery):** Wire `+5V` → `+5V_SERVO` directly (or through D_OR1 if OR-ing diode pads are populated)
   **Pro (with battery):** `+5V_SERVO` is fed through OR-ing diodes from BOTH USB and boost converter — see Step 13c. For now, wire `+5V` → `+5V_SERVO` directly. Step 13c will insert OR-ing diodes.
   - **NOTE:** `+5V_SERVO` does NOT connect to any PCA9685 pin — it goes directly to servo header power pins (Step 7)
3. Place C8: `Device:C_Polarized` → `470uF`, electrolytic, ⌀8×10mm or larger
   - Wire: `+5V_SERVO` → C8+ → C8- → GND
   - **PURPOSE:** Absorbs servo inrush current spikes. Without this, servos will brown out the ESP32.
4. Place C9: `Device:C` → `100uF`, 1206, ceramic
   - Wire: `+5V_SERVO` → C9 → GND (close to servo headers)
5. Place C10: `Device:C` → `100nF`, 0402, C1525
   - Wire: `+5V_SERVO` → C10 → GND (high-frequency bypass)

**VERIFY:**
- [ ] `+5V_SERVO` connects to `+5V` (USB power) — direct, no regulator
- [ ] `+5V_SERVO` does NOT connect to any PCA9685 pin — it only goes to servo header power pins
- [ ] `+5V_SERVO` does NOT connect through the AP2112K LDO — it's direct from USB
- [ ] C8 (470µF electrolytic) is the bulk cap — largest cap on the board
- [ ] C9 (100µF ceramic) for mid-frequency filtering
- [ ] C10 (100nF) for high-frequency bypass
- [ ] All three caps between `+5V_SERVO` and GND
- [ ] Component count: 3 (C8, C9, C10)

**EXPECTED RESULT:** Robust 5V servo power rail with bulk capacitance to handle servo inrush. Servos get 5V directly from USB, not through the LDO.

---

## Step 7: Servo Headers (7-16 connectors)

**PURPOSE:** 3-pin headers for connecting hobby servos (signal, +5V, GND).

**DO:**
1. Place J_SRV0 through J_SRV6 (Spark minimum — 7 headers):
   - Symbol: `Connector_Generic:Conn_01x03`
   - Footprint: 2.54mm pitch 3-pin header
2. Wire each header:
   - Pin 1 (Signal) → PCA9685 PWM output (LED0-LED6)
   - Pin 2 (+V) → `+5V_SERVO`
   - Pin 3 (GND) → GND

**Servo channel allocation:**

| Header | PCA9685 CH | Joint | Servo | Tier |
|--------|-----------|-------|-------|------|
| J_SRV0 | LED0 | head_pan | SG90 | All |
| J_SRV1 | LED1 | head_tilt | SG90 | All |
| J_SRV2 | LED2 | left_shoulder_pitch | MG90S | All |
| J_SRV3 | LED3 | left_shoulder_roll | SG90 | All |
| J_SRV4 | LED4 | right_shoulder_pitch | MG90S | All |
| J_SRV5 | LED5 | right_shoulder_roll | SG90 | All |
| J_SRV6 | LED6 | waist_yaw | MG90S | All |
| J_SRV7 | LED7 | left_elbow | SG90 | Pro |
| J_SRV8 | LED8 | left_hand | SG90 | Pro |
| J_SRV9 | LED9 | right_elbow | SG90 | Pro |
| J_SRV10 | LED10 | right_hand | SG90 | Pro |

3. For Pro, add J_SRV7 through J_SRV10 (same wiring pattern)
4. PCA9685 outputs LED11-LED15 left unconnected (available for future use)

**VERIFY:**
- [ ] Each header pin 1 (signal) connects to the correct PCA9685 LEDn output
- [ ] Each header pin 2 → `+5V_SERVO` (NOT +3V3, NOT +5V logic)
- [ ] Each header pin 3 → GND
- [ ] Minimum 7 headers for Spark, 11 for Pro
- [ ] PCA9685 LED0-LED6 → J_SRV0-J_SRV6 (always populated)
- [ ] PCA9685 LED7-LED10 → J_SRV7-J_SRV10 (Pro only, DNP Spark)

**EXPECTED RESULT:** 7-11 servo connectors, each receiving PWM from PCA9685 and power from the 5V servo rail.

---

## Step 8: MAX98357A Audio Amplifier (5 components)

**PURPOSE:** I2S Class-D mono amplifier driving a 4Ω/8Ω speaker.

**DATASHEET:** Open `datasheets/MAX98357A.pdf` — reference circuit

**DO:**
1. Place U4: search for `MAX98357AETE` or use generic opamp symbol and assign footprint
   - Footprint: `Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm`
   - LCSC: C910544
2. Wire:

| U4 Pin | Name | Wire To | Notes |
|--------|------|---------|-------|
| 1 | DIN | ESP32 GPIO6 → label `I2S_DOUT` | I2S serial data |
| 2 | GAIN | GND | 9dB gain (for 4Ω speaker) |
| 3 | GND | GND | |
| 4 | SD_MODE | `+3V3` (direct or via 100k pull-up) | Shutdown + channel select. HIGH = left channel + enabled. LOW = shutdown. See pin 15 note. |
| 5-6 | OUT+ / OUT- | → Speaker connector J_SPK | Differential speaker output |
| 7 | GND | GND | |
| 8 | BCLK | ESP32 GPIO4 → label `I2S_BCLK` | I2S bit clock |
| 9 | GND | GND | |
| 10 | PVDD | `+5V` → through FB2 (ferrite bead) | Analog power — filter with ferrite |
| 11 | PVDD | Same as pin 10 | |
| 12 | GND | GND | Exposed pad |
| 13 | DVDD | `+3V3` | Digital power (1.8V internal LDO, 3.3V input OK) |
| 14 | LRCLK | ESP32 GPIO5 → label `I2S_LRCLK` | I2S word select |
| 15 | SD_MODE | Same pin as pin 4 — see above | **Pin 4 and pin 15 are the SAME function.** Wire once. |
| 16 | GND | GND | |

3. Place FB2: `Device:FerriteBead` → Value: `600R@100MHz`, 0603, LCSC: C85834
   - Wire: `+5V` → FB2 → U4 PVDD (pins 10, 11)
4. Place C11: `Device:C` → `10uF`, 0805, C15850
   - Wire: U4 PVDD (post-FB2) → C11 → GND
5. Place C12: `Device:C` → `100nF`, 0402, C1525
   - Wire: U4 DVDD (pin 13) → C12 → GND
6. Place J_SPK: `Connector_Generic:Conn_01x02` → JST-PH 2-pin
   - Wire: pin 1 → U4 OUT+, pin 2 → U4 OUT-

**VERIFY:**
- [ ] DIN (pin 1) → GPIO6 (`I2S_DOUT`) — ESP32 outputs data, MAX98357A receives
- [ ] BCLK (pin 8) → GPIO4 (`I2S_BCLK`)
- [ ] LRCLK (pin 14) → GPIO5 (`I2S_LRCLK`)
- [ ] GAIN (pin 2) → GND (9dB for 4Ω speaker)
- [ ] SD (pin 4) → HIGH (enabled). If LOW, amp is in shutdown.
- [ ] PVDD (pins 10, 11) fed through FB2 ferrite bead from +5V, with C11 (10µF) decoupling
- [ ] DVDD (pin 13) → `+3V3` with C12 (100nF) decoupling
- [ ] OUT+/OUT- → speaker connector (differential, NO ground reference on speaker)
- [ ] **Speaker wires are NOT referenced to GND** — they are differential
- [ ] Component count: 5 (FB2, C11, C12, J_SPK + U4 already placed)

**EXPECTED RESULT:** I2S audio amplifier receiving digital audio from ESP32 and driving a speaker. Powered from filtered +5V (analog) and +3V3 (digital).

---

## Step 8b: Status LEDs (4 components)

**PURPOSE:** Power indicator + firmware-controlled RGB status LED for boot mode, WiFi status, errors, OTA progress.

**DO:**

**Power LED (always on when 3.3V rail is live):**
1. Place D_PWR: `Device:LED` → GREEN, 0402, LCSC: C130723
2. Place R_PWR: `Device:R` → `1k`, 0402, C11702
3. Wire: `+3V3` → R_PWR → D_PWR anode → D_PWR cathode → GND

**Status LED (firmware-controlled RGB):**
4. Place D_STATUS: `LED:WS2812B` → Footprint: `LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm`, LCSC: C2761795
5. Wire:
   - D_STATUS VDD → `+5V`
   - D_STATUS VSS → GND
   - D_STATUS DIN → ESP32 GPIO48 → label `NEOPIXEL`
   - D_STATUS DOUT → No Connect marker (single LED, no chain)
6. Place C_NEO: `Device:C` → `100nF`, 0402, C1525
   - Wire: D_STATUS VDD → C_NEO → GND (decoupling, close to LED)

**GPIO48 note:** On Pro with camera, GPIO48 is also camera SIOC (config I2C clock). Camera config happens briefly at init — LED is firmware-controlled the rest of the time. No conflict in practice.

**VERIFY:**
- [ ] D_PWR (green) lights whenever +3V3 is live — no GPIO needed
- [ ] D_STATUS (WS2812B) on GPIO48 (`NEOPIXEL`) — addressable RGB
- [ ] C_NEO (100nF) decoupling close to WS2812B VDD
- [ ] WS2812B VDD → `+5V` (NOT +3V3 — WS2812B needs 5V)
- [ ] Component count: 4 (D_PWR, R_PWR, D_STATUS, C_NEO)

**Status LED firmware color map (reference for firmware team):**

| Color | Meaning |
|-------|---------|
| Blue pulse | Booting / initializing |
| Green solid | WiFi connected, ready |
| Yellow pulse | OTA firmware update in progress |
| Red solid | Error / boot failure |
| White pulse | Bluetooth pairing mode |
| Off | Shutdown / deep sleep |

**EXPECTED RESULT:** Green power LED always on when board is powered. RGB status LED shows system state via firmware control.

---

## Step 9: Power Flags + Net Labels

**PURPOSE:** Prevent ERC warnings about undriven power nets.

**DO:**
1. Place `PWR_FLAG` on `+5V` net
2. Place `PWR_FLAG` on `+3V3` net
3. Place `PWR_FLAG` on `+5V_SERVO` net (if separate from `+5V`)
4. Place `PWR_FLAG` on `GND` net

**VERIFY:**
- [ ] PWR_FLAG on each power net
- [ ] No ERC "power pin not driven" warnings

---

## Step 10: Run ERC — Core Section

**DO:**
1. Inspect → Electrical Rules Check → Run

**VERIFY:**
- [ ] **Zero errors** (red)
- [ ] Warnings are only for unconnected PCA9685 LED outputs (LED11-LED15) or Pro DNP connectors
- [ ] No "different net names on same wire"
- [ ] No "power pin not driven"

**EXPECTED RESULT:** Clean ERC for the core section. Ready to add Pro components.

---

# SECTION B: PRO ONLY (DNP on Spark)

All components in this section have pads on the PCB but are NOT populated for Spark kits. Mark each with a `DNP` (Do Not Populate) note in the schematic.

---

## Step 11: TP4056 Battery Charger (9 components)

**PURPOSE:** Single-cell LiPo charging from USB-C. Identical circuit to Aerwyz Pod.

**DATASHEET:** Open `datasheets/C16581_TP4056.pdf` page 2 (pin table)

**DO:**
1. Place U6: `TP4056:TP4056` → Footprint: `TP4056:SOP127P600X175-9N`, LCSC: C16581
2. Wire pin-by-pin:

| U6 Pin | Name | Wire To |
|--------|------|---------|
| 1 | TEMP | NTC voltage divider (Step 12) |
| 2 | PROG | R7 (2k, C4109) → GND |
| 3 | GND | GND |
| 4 | VCC | `+5V` |
| 5 | BAT | Label `VBAT` |
| 6 | STDBY | `+5V` → D3 anode (GREEN LED) → D3 cathode → R9 (1k) → U6 pin 6 |
| 7 | CHRG | `+5V` → D2 anode (RED LED) → D2 cathode → R8 (1k) → U6 pin 7 |
| 8 | CE | `+5V` (always enabled) |
| 9 | EP | GND |

3. Place R7: 2k → PROG to GND (sets 500mA charge current)
4. Place R8, R9: 1k → LED current limiters
5. Place D2: RED LED (0402, C130719), D3: GREEN LED (0402, C130723) — charge status
6. Place C13: 10µF, 0805 → `+5V` (VCC) to GND
7. Place C14: 10µF, 0805 → `VBAT` (BAT) to GND
8. Place J_BAT: `Connector_Generic:Conn_01x02` → JST-PH 2-pin, C131337
   - Wire: J_BAT pin 1 → `VBAT`, pin 2 → GND

**VERIFY:**
- [ ] R7 = 2k → charge current = 1000/2000 = **500mA**
- [ ] Pin 7 (CHRG) drives RED LED (active-low, sinks current)
- [ ] Pin 6 (STDBY) drives GREEN LED
- [ ] LED wiring: `+5V` → LED anode → LED cathode → R → TP4056 pin (TP4056 sinks current, pins are active-LOW open-drain)
- [ ] CE (pin 8) tied to VCC (always enabled)
- [ ] C13 on VCC, C14 on BAT — both to GND
- [ ] Component count: 9 (U6, R7, R8, R9, D2, D3, C13, C14, J_BAT)

**EXPECTED RESULT:** LiPo charger that takes USB 5V, charges at 500mA, with red/green status LEDs.

---

## Step 12: NTC Battery Temperature Monitor (2 components)

**PURPOSE:** MANDATORY safety feature for CPSIA compliance with LiPo battery. Suspends charging if battery is too hot (>45°C) or too cold (<0°C).

**DO:**
1. Place TH1: NTC Thermistor, 10K B3380, 0402, LCSC: C77131
2. Place R10: `Device:R` → 10K, 0402, C25744
3. Wire the voltage divider:
   - R10: `+5V` → R10 → junction
   - TH1: junction → TH1 → GND
   - Junction → U6 pin 1 (TEMP)

```
+5V ─── R10 (10K) ─── junction ─── TH1 (10K NTC) ─── GND
                           │
                           └──→ U6 TEMP (pin 1)
```

**VERIFY:**
- [ ] TH1 is a 10K NTC thermistor (NOT a regular 10K resistor)
- [ ] Voltage divider: R10 from +5V to TEMP, TH1 from TEMP to GND
- [ ] U6 TEMP is NOT tied directly to GND
- [ ] TH1 physically placed near J_BAT (battery connector) in PCB layout
- [ ] Component count: 2 (TH1, R10)

**EXPECTED RESULT:** TP4056 suspends charging when battery temperature is outside 0-45°C range.

---

## Step 13: Battery Protection — DW01A + FS8205A (5 components)

**PURPOSE:** Protects LiPo from over-discharge (<2.4V), over-charge (>4.3V), and overcurrent.

**DATASHEET:** Open `datasheets/C351410_DW01A.pdf` page 2 and `datasheets/C908265_FUXINSEMI_FS8205A.pdf`

**CRITICAL: This step had a pin swap bug in Pod Rev 1. Follow carefully.**

**DO:**
1. Place U7: `DW01A:DW01A` → Footprint: `DW01A:SOT95P280X145-6N`, LCSC: C351410
2. Place Q1: `FS8205A:FS8205` → Footprint: `FS8205-SOT236:SOT95P280X145-6N`, LCSC: C908265
3. Place R11: `Device:R` → `100mR` (0.1 ohm), 0402, C724023
4. Place R12: `Device:R` → `100R`, 0402, C25076 — VCC inrush limiter
5. Place C15: `Device:C` → `100nF`, 0402, C1525 — VCC decoupling

Wire U7 (DW01A):

| U7 Pin | Name | Wire To |
|--------|------|---------|
| 1 | OD | Q1 **pin 6** (G1) — GND-side FET gate |
| 2 | CS | R11 → junction between Q1 S1 and GND |
| 3 | OC | Q1 **pin 4** (G2) — BAT-side FET gate |
| 4 | TD | NC or 100nF to GND |
| 5 | VCC | R12 (100R) → `VBAT` + C15 from VCC to GND |
| 6 | GND | Q1 pin 1 (S1) — NOT system GND directly |

Wire Q1 (FS8205A SOT-23-6):

| Q1 Pin | Function | Wire To |
|--------|----------|---------|
| 1 | S1 (GND-side source) | → R11 (100mR) → GND. Also → U7 GND (pin 6) |
| 2 | D1/D2 (shared drain) | NOT connected externally |
| 3 | S2 (BAT-side source) | → `VBAT` |
| 4 | G2 (BAT-side gate) | → U7 OC (pin 3) |
| 5 | D1/D2 (shared drain) | NOT connected externally |
| 6 | G1 (GND-side gate) | → U7 OD (pin 1) |

**VERIFY — TRIPLE CHECK (Pod Rev 1 had these swapped):**
- [ ] U7 pin 1 (OD) → Q1 **pin 6** (G1). OD controls the GND-side FET.
- [ ] U7 pin 3 (OC) → Q1 **pin 4** (G2). OC controls the BAT-side FET.
- [ ] Q1 has exactly **6 pins** (SOT-23-6), NOT 8 pins
- [ ] U7 pin 6 (GND) connects to Q1 **pin 1** (S1), NOT to system GND directly
- [ ] R11 = **0.1 ohm** (100mR), NOT 1k
- [ ] R12 (100R) in series between VBAT and U7 VCC (pin 5)
- [ ] C15 (100nF) from U7 VCC to GND
- [ ] Component count: 5 (U7, Q1, R11, R12, C15)

**EXPECTED RESULT:** Battery protection that disconnects on over-discharge, over-charge, or overcurrent.

---

## Step 13b: Boost Converter — TPS61023 (7 components)

**PURPOSE:** Boost battery voltage (3.7V) to 5.1V for servo power when running on battery. Without this, servos cannot operate untethered.

**DATASHEET:** TPS61023 datasheet from TI (download from LCSC C919459 page)

**DESIGN DECISION:** Single-cell LiPo (3.7V) + boost converter. Not 2S (7.4V) + buck. Reasoning:
- TP4056 single-cell charger proven on Pod (reuse entire charging circuit)
- Single cell = lower voltage = safer for ages 12-15 (CPSIA)
- DW01A/FS8205A protection already designed for single cell
- Trade-off: lower runtime (mitigated by using 2000mAh cell)

**DO:**
1. Place U9: `Regulator_Switching:TPS61023` (or generic boost symbol + assign footprint)
   - Footprint: SOT-563 (1.6×1.2mm, 6-pin)
   - LCSC: C919459
   - Price: ~$0.14
2. Wire per TPS61023 datasheet reference circuit:

| U9 Pin | Name | Wire To |
|--------|------|---------|
| 1 | VIN | `VBAT` (from battery protection output) |
| 2 | GND | GND |
| 3 | EN | `VBAT` (tie to VIN = always enabled when battery present) |
| 4 | SW | → L3 inductor → D_BOOST Schottky cathode → `+5V_BOOST` |
| 5 | FB | Feedback divider midpoint (R17/R18) |
| 6 | VOUT | `+5V_BOOST` (direct connection for internal LDO) |

3. Place L3: `Device:L` → `2.2µH`, 3×3mm or 4×4mm, rated ≥4A saturation
   - Wire: `VBAT` → L3 → U9 SW (pin 4)
   - LCSC: Search "2.2uH inductor 4A" — e.g., C408412 or similar
4. Place D_BOOST: `Device:D_Schottky` → `SS34` (3A/40V), SMA, LCSC: C8678
   - Wire: anode → U9 SW (pin 4) / L3 junction, cathode → label `+5V_BOOST`
5. Place C_BIN: `Device:C` → `10uF`, 0805, C15850 — boost input cap
   - Wire: `VBAT` → C_BIN → GND (close to U9 VIN)
6. Place C_BOUT: `Device:C` → `22uF`, 0805, C45783 — boost output cap
   - Wire: `+5V_BOOST` → C_BOUT → GND
7. Place feedback divider (sets Vout = 5.1V):
   - R17: `750k 1%`, 0402, C137937 — top resistor
   - R18: `100k 1%`, 0402, C25741 — bottom resistor
   - Wire: `+5V_BOOST` → R17 → junction → R18 → GND
   - Wire: junction → U9 FB (pin 5)
   - Vout = 0.5V × (1 + 750k/100k) = 0.5V × 8.5 = **4.25V**... 

   **CORRECTION:** TPS61023 reference voltage is 0.5V (not 0.6V like MT3608).
   For Vout = 5.1V: R17/R18 = (5.1/0.5) - 1 = 9.2
   Use R17 = **920k** (C25810), R18 = **100k** (C25741) → Vout = 0.5 × (1 + 920k/100k) = **5.1V**

**Topology:**
```
VBAT ──[L3 2.2µH]──┬──[D_BOOST SS34]── +5V_BOOST
                    │                    │
                  SW (pin 4)           C_BOUT (22µF)
                                        │
                              R17 (920k) ── FB (pin 5) ── R18 (100k) ── GND
```

**VERIFY:**
- [ ] L3 connects VBAT → SW junction (NOT between SW and diode output)
- [ ] D_BOOST anode at SW junction, cathode at `+5V_BOOST` output
- [ ] Feedback: R17 (920k) from +5V_BOOST to FB, R18 (100k) from FB to GND
- [ ] Vout = 0.5V × (1 + 920k/100k) = **5.1V**
- [ ] EN tied to VIN (always on when battery present)
- [ ] C_BIN (10µF) on input, C_BOUT (22µF) on output
- [ ] L3 rated ≥ 4A saturation current (TPS61023 peaks at 3.7A)
- [ ] Component count: 7 (U9, L3, D_BOOST, C_BIN, C_BOUT, R17, R18)

**EXPECTED RESULT:** When on battery (3.7V), boost converter produces 5.1V for servos. Current capability: ~2A continuous at 5.1V output from 3.7V input (efficiency ~90%).

---

## Step 13c: Power OR-ing Diodes (2 components)

**PURPOSE:** Merge USB 5V and boosted battery 5V into the single `+5V_SERVO` rail. Diodes prevent backfeeding between sources. Whichever source is higher voltage wins.

**DO:**
1. Place D_OR1: `Device:D_Schottky` → `SS34`, SMA, LCSC: C2480
   - Wire: anode → `+5V` (from USB input, Step 1), cathode → `+5V_SERVO`
2. Place D_OR2: `Device:D_Schottky` → `SS34`, SMA, LCSC: C2480
   - Wire: anode → `+5V_BOOST` (from boost converter, Step 13b), cathode → `+5V_SERVO`

**Update Step 6 wiring:** The `+5V_SERVO` rail is now fed through OR-ing diodes, NOT directly from `+5V`. Go back to Step 6 and change:
- **OLD:** `+5V` → `+5V_SERVO` (direct)
- **NEW:** `+5V` → D_OR1 → `+5V_SERVO` (through Schottky diode)

**Updated power architecture:**
```
USB-C (+5V) ──► D_OR1 (SS34) ──►──┐
                                    ├──► +5V_SERVO ──► servo headers + PCA9685 logic (via LDO)
VBAT (3.7V) ──► Boost (5.1V) ──► D_OR2 (SS34) ──►──┘
```

**VERIFY:**
- [ ] Both D_OR1 and D_OR2 cathodes connect to the SAME net: `+5V_SERVO`
- [ ] D_OR1 anode = `+5V` (from USB)
- [ ] D_OR2 anode = `+5V_BOOST` (from battery boost)
- [ ] Current flows FROM either source TO +5V_SERVO, but NOT back
- [ ] When USB is connected: USB 5V dominates (~5V vs boost 5.1V minus diode drop)
- [ ] When on battery only: boost 5.1V feeds servos through D_OR2
- [ ] `+5V_SERVO` is now the main 5V bus (feeds LDO input too — change U2 VIN from `+5V` to `+5V_SERVO`)
- [ ] Component count: 2 (D_OR1, D_OR2)

**NOTE:** Schottky diode forward drop is ~0.3V. So servo rail gets ~4.7V from USB or ~4.8V from boost. SG90/MG90S work fine at 4.7V (rated 4.8-6V). XL330 works at 3.7-6V.

**EXPECTED RESULT:** Seamless power switching between USB and battery. Unplug USB → battery boost takes over. Plug USB back in → USB takes over and TP4056 charges battery.

---

## Step 14: SPH0641LU4H-1 PDM Microphone (2 components)

**PURPOSE:** Digital MEMS microphone for voice input. PDM interface — ESP32-S3 has hardware PDM-to-PCM converter.

**DATASHEET:** Open `datasheets/SPH0641LU4H-1.pdf` (from Pod) page 9

**DO:**
1. Place M1: `SPH0641LU4H-1:SPH0641LU4H-1`
   - Footprint: `SPH0641LU4H-1:MIC_SPH0641LU4H-1`
   - LCSC: C2879853
2. Wire:

| M1 Pin | Name | Wire To | Net Label |
|--------|------|---------|-----------|
| 1 | DATA | ESP32 GPIO7 | `PDM_DATA` |
| 2 | SELECT | GND (directly) | GND |
| 3 | GND | GND | GND |
| 4 | CLOCK | ESP32 GPIO15 | `PDM_CLK` |
| 5 | VDD | `+3V3` | `+3V3` |

3. Place C16: `Device:C` → `100nF`, 0402, C1525
   - Wire: M1 VDD (pin 5) → C16 → GND (place close to M1)

**VERIFY:**
- [ ] Pin 1 (DATA) → GPIO7 (`PDM_DATA`)
- [ ] Pin 2 (SELECT) → GND (left channel)
- [ ] Pin 3 (GND) → GND
- [ ] Pin 4 (CLOCK) → GPIO15 (`PDM_CLK`)
- [ ] Pin 5 (VDD) → `+3V3`
- [ ] C16 (100nF) decoupling on VDD
- [ ] **SELECT is NOT floating** — must be tied to GND or VDD
- [ ] Component count: 2 (M1, C16)

**EXPECTED RESULT:** PDM microphone on GPIO7 (data) and GPIO15 (clock). Only 2 GPIO pins used.

---

## Step 15: MPU6050 IMU (2 components)

**PURPOSE:** 6-axis accelerometer/gyroscope for balance sensing during walking.

**DATASHEET:** Open `datasheets/MPU6050.pdf`

**DO:**
1. Place U8: `Sensor_Motion:MPU-6050` → Footprint: `Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm`
   - LCSC: C24112
2. Wire:
   - U8 VDD → `+3V3`
   - U8 VLOGIC → `+3V3` (**CRITICAL** — sets I2C voltage level, must match bus voltage)
   - U8 GND → GND
   - U8 SDA → `I2C_SDA` (shared with PCA9685)
   - U8 SCL → `I2C_SCL` (shared with PCA9685)
   - U8 AD0 → GND (I2C address = 0x68)
   - U8 INT → leave unconnected or wire to a spare GPIO (optional)
   - U8 FSYNC → GND
   - U8 CLKIN → leave unconnected
   - U8 AUX_SDA, AUX_SCL → leave unconnected (no auxiliary I2C devices)
   - U8 REGOUT → C17 (100nF) → GND (internal regulator bypass)
   - U8 CPOUT → C19 (10nF) → GND (charge pump cap — **required**)
3. Place C17: 100nF, 0402, C1525 → U8 REGOUT to GND
4. Place C18: 100nF, 0402, C1525 → U8 VDD to GND (decoupling)
5. Place C19: 10nF, 0402, C15195 → U8 CPOUT to GND (charge pump)

**VERIFY:**
- [ ] VDD → `+3V3`, GND → GND
- [ ] **VLOGIC → `+3V3`** (if left floating, I2C may not work)
- [ ] SDA/SCL on same I2C bus as PCA9685
- [ ] AD0 → GND → I2C address = **0x68** (no conflict with PCA9685 at 0x40)
- [ ] FSYNC → GND
- [ ] REGOUT → C17 (100nF) → GND
- [ ] CPOUT → C19 (10nF) → GND (**required** for internal charge pump)
- [ ] Component count: 4 (C17, C18, C19 + U8)

**EXPECTED RESULT:** IMU on shared I2C bus at address 0x68. VLOGIC at 3.3V for correct I2C levels. Provides tilt and acceleration data for walking balance.

---

## Step 16: Dynamixel Bus Connector (1 component)

**PURPOSE:** Half-duplex UART connector for XL330 Dynamixel smart servos (Pro legs + shoulders).

**DO:**
1. Place J_DXL: `Connector_Generic:Conn_01x03` → JST-PH 3-pin
   - Pin 1 → `+5V_SERVO` (XL330 power, 5V)
   - Pin 2 → GND
   - Pin 3 → label `DXL_DATA`
2. Wire ESP32 UART1:
   - GPIO17 → label `DXL_TX`
   - GPIO18 → label `DXL_RX`

**NOTE:** XL330 uses half-duplex UART (single data wire). A direction-control circuit (tri-state buffer or resistor network) is needed between TX/RX and the single DXL_DATA line. For prototype, use a Robotis U2D2 adapter. For production PCB, add a 74HC126 or similar tri-state buffer.

**VERIFY:**
- [ ] J_DXL pin 1 → `+5V_SERVO` (5V power for XL330s)
- [ ] GPIO17 = TX, GPIO18 = RX (UART1)
- [ ] Half-duplex note documented in schematic

**EXPECTED RESULT:** Connector for Dynamixel servo daisy-chain. Production will need tri-state buffer for half-duplex.

---

## Step 17: Camera DVP Connector (1 component)

**PURPOSE:** FPC connector for OV2640 camera module (Pro only).

**DO:**
1. Place J_CAM: FPC connector, 24-pin, 0.5mm pitch (e.g., FH12-24S-0.5SH)
2. Wire DVP signals to ESP32 GPIOs:

**CRITICAL: GPIO35, 36, 37 are NOT available on the N16R8 variant — they are used internally for Octal SPI PSRAM. Use only GPIOs that are free on N16R8.**

| J_CAM Pin | Signal | ESP32 GPIO | Notes |
|-----------|--------|------------|-------|
| — | D0 | GPIO10 | Shared with FSR on Spark — OK because camera is Pro-only |
| — | D1 | GPIO13 | |
| — | D2 | GPIO14 | |
| — | D3 | GPIO16 | Freed by PDM mic (only uses 2 pins) |
| — | D4 | GPIO21 | |
| — | D5 | GPIO38 | Safe on N16R8 |
| — | D6 | GPIO39 | |
| — | D7 | GPIO40 | |
| — | XCLK | GPIO41 | Camera master clock |
| — | PCLK | GPIO42 | Pixel clock |
| — | VSYNC | GPIO45 | **Strapping pin** — acceptable for camera (not read at boot if pulled to default) |
| — | HREF | GPIO46 | Input-only on some variants — OK for camera input |
| — | SIOD (I2C) | GPIO47 | Camera config I2C (separate bus) |
| — | SIOC (I2C) | GPIO48 | Camera config I2C (separate bus) |
| — | 3V3 | `+3V3` | |
| — | GND | GND | |

**NOTE:** Camera DVP uses 14 GPIO pins. This assignment avoids GPIO35-37 (PSRAM), GPIO3 (strapping), and does not conflict with Spark-tier functions. Camera I2C (SIOD/SIOC) is on a SEPARATE I2C bus (GPIO47/48, not GPIO8/9). Exact FPC pinout depends on camera module — verify against your specific OV2640 module before wiring.

**VERIFY:**
- [ ] Camera I2C on GPIO47/48 — **NOT on the main I2C bus** (GPIO8/9)
- [ ] **GPIO35, 36, 37 are NOT used** (reserved for PSRAM on N16R8)
- [ ] DVP data pins do not conflict with Spark-tier functions (Spark has no camera)
- [ ] 3V3 and GND connected

**EXPECTED RESULT:** Camera connector footprint on PCB, DNP for Spark.

---

## Step 18: FSR Connectors + Voltage Dividers (8 components)

**PURPOSE:** 4 Force Sensitive Resistors in feet for ground contact detection during walking.

**DO:**
1. Place 4× FSR connectors: `Connector_Generic:Conn_01x02` → JST-SH 2-pin
   - J_FSR1 (left front), J_FSR2 (left rear), J_FSR3 (right front), J_FSR4 (right rear)
2. Place 4× voltage divider resistors: R13-R16, 10k, 0402, C25744
3. Wire each FSR circuit:

```
+3V3 ─── J_FSRn pin 1 ──┬── R_n (10K) ─── GND
                          │
                          └──→ ESP32 ADC GPIO
         J_FSRn pin 2 ──→ GND
```

| FSR | Connector | Resistor | GPIO | Net Label |
|-----|-----------|----------|------|-----------|
| Left front | J_FSR1 | R13 | GPIO1 | `FSR_LF` |
| Left rear | J_FSR2 | R14 | GPIO2 | `FSR_LR` |
| Right front | J_FSR3 | R15 | GPIO11 | `FSR_RF` |
| Right rear | J_FSR4 | R16 | GPIO12 | `FSR_RR` |

**VERIFY:**
- [ ] Each FSR has a 10K pull-down resistor forming a voltage divider
- [ ] ADC GPIOs (1, 2, 11, 12) are all ADC-capable on ESP32-S3 and NOT strapping pins
- [ ] GPIO3 is NOT used (strapping pin)
- [ ] GPIO10 is NOT used here (reserved for camera DVP on Pro)
- [ ] FSR connectors are 2-pin (signal + GND)
- [ ] Component count: 8 (4 connectors + 4 resistors)

**EXPECTED RESULT:** 4 FSR inputs with voltage dividers, reading 0-3.3V proportional to force on each foot.

---

## Step 19: Final ERC — Full Board

**DO:**
1. Inspect → Electrical Rules Check → Run

**VERIFY:**
- [ ] **Zero errors** (red)
- [ ] All Pro DNP components properly connected (they should pass ERC even if not populated)
- [ ] No I2C address conflicts: PCA9685 = 0x40, MPU6050 = 0x68
- [ ] No GPIO conflicts (cross-reference against GPIO table at top)
- [ ] No "power pin not driven" warnings

---

## Step 20: Final Footprint Assignment & LCSC Numbers

**DO:** Tools → Edit Symbol Fields → verify every component has footprint and LCSC number.

**Complete Component Checklist:**

### Core (Always Populated) — ~45 components

| # | Ref | Value | LCSC | Section |
|---|-----|-------|------|---------|
| 1 | U1 | ESP32-S3-WROOM-1-N16R8 | C2913202 | Step 3 |
| 2 | U2 | AP2112K-3.3 | C51118 | Step 2 |
| 3 | U3 | PCA9685PW,118 | C2678753 | Step 5 |
| 4 | U4 | MAX98357AETE+T | C910544 | Step 8 |
| 5 | U5 | USBLC6-2SC6 | C7519 | Step 1 |
| 6 | J1 | USB-C (HRO TYPE-C-31-M-12) | C165948 | Step 1 |
| 7 | J_SPK | Speaker JST-PH 2-pin | C131337 | Step 8 |
| 8 | J_SRV0-6 | Servo headers ×7 | — | Step 7 |
| 9 | SW1 | Boot button | C318884 | Step 3 |
| 10 | SW2 | Reset button | C318884 | Step 3 |
| 11 | F1 | PTC fuse 1.5A | TBD | Step 1 |
| 12 | D1 | TVS ESD5Z5.0T1G | C82044 | Step 1 |
| 13 | D_PWR | Green power LED | C130723 | Step 8b |
| 14 | D_STATUS | WS2812B RGB | C2761795 | Step 8b |
| 15 | FB2 | Ferrite 600R | C85834 | Step 8 |
| 16 | R1-R2 | 5.1k ×2 (CC) | C25905 | Step 1 |
| 17 | R3-R4 | 10k ×2 (EN/BOOT) | C25744 | Step 3 |
| 18 | R5-R6 | 4.7k ×2 (I2C) | C25900 (both) | Step 4 |
| 19 | R_PWR | 1k (power LED) | C11702 | Step 8b |
| 20 | C1,C5,C6,C10,C12,C_NEO | 100nF ×6 | C1525 | Various |
| 21 | C2,C3,C4,C7,C11 | 10µF ×5 | C15850 | Various |
| 22 | C8 | 470µF electrolytic | TBD | Step 6 |
| 23 | C9 | 100µF ceramic | TBD | Step 6 |

### Pro Only (DNP Spark) — ~40 components

| # | Ref | Value | LCSC | Section |
|---|-----|-------|------|---------|
| 24 | U6 | TP4056 | C16581 | Step 11 |
| 25 | U7 | DW01A | C351410 | Step 13 |
| 26 | Q1 | FS8205A | C908265 | Step 13 |
| 27 | U8 | MPU-6050 | C24112 | Step 15 |
| 28 | U9 | TPS61023DRLR (boost) | C919459 | Step 13b |
| 29 | M1 | SPH0641LU4H-1 | C2879853 | Step 14 |
| 30 | TH1 | NTC 10K B3380 | C77131 | Step 12 |
| 31 | J_BAT | JST-PH 2-pin | C131337 | Step 11 |
| 32 | J_DXL | JST-PH 3-pin | C131334 | Step 16 |
| 33 | J_CAM | FPC 24-pin | TBD | Step 17 |
| 34 | J_FSR1-4 | JST-SH 2-pin ×4 | TBD | Step 18 |
| 35 | J_SRV7-10 | Servo headers ×4 | — | Step 7 |
| 36 | D2 | RED LED (charge) | C130719 | Step 11 |
| 37 | D3 | GREEN LED (full) | C130723 | Step 11 |
| 38 | D_OR1 | SS34 Schottky (USB) | C2480 | Step 13c |
| 39 | D_OR2 | SS34 Schottky (boost) | C2480 | Step 13c |
| 40 | D_BOOST | SS34 Schottky (boost rect) | C8678 | Step 13b |
| 41 | L3 | 2.2µH inductor ≥4A | TBD | Step 13b |
| 42 | R7 | 2k (PROG) | C4109 | Step 11 |
| 43 | R8-R9 | 1k ×2 (charge LED) | C11702 | Step 11 |
| 44 | R10 | 10k (NTC bias) | C25744 | Step 12 |
| 45 | R11 | 100mR (sense) | C724023 | Step 13 |
| 46 | R12 | 100R (VCC inrush) | C25076 | Step 13 |
| 47 | R13-R16 | 10k ×4 (FSR) | C25744 | Step 18 |
| 48 | R17 | 920k 1% (boost FB top) | C25810 | Step 13b |
| 49 | R18 | 100k 1% (boost FB bottom) | C25741 | Step 13b |
| 50 | C13-C19 | Various decoupling | C1525/C15850 | Various |
| 51 | C_BIN | 10µF (boost input) | C15850 | Step 13b |
| 52 | C_BOUT | 22µF (boost output) | C45783 | Step 13b |

---

## PCB Layout Rules (Apply During Layout Phase)

These don't affect the schematic but MUST be followed during PCB layout:

### Board Outline
- Shape: Rectangle, 60 × 40 mm
- Layer count: 2
- Copper weight: 1 oz

### Antenna Keepout — CRITICAL
- ESP32-S3 antenna at one edge of the board
- **15mm no-copper zone** around antenna (no traces, no pour, no vias, no components)
- Antenna points AWAY from servo headers (toward open space)

### Power Routing
- `+5V_SERVO` traces: **1.0mm minimum** (2A+ capability)
- `+5V` traces: 0.5mm minimum
- `+3V3` traces: 0.3mm minimum
- Signal traces (I2C, I2S, PDM): 0.2mm minimum
- Ground: Pour on bottom layer (with antenna keepout)

### Component Placement
- ESP32-S3 at top edge (antenna facing outward)
- PCA9685 near center (close to servo headers)
- Servo headers along long edges (3 on one side, 4 on other)
- MAX98357A near speaker connector
- USB-C at board edge (accessible)
- Pro DNP components grouped together (bottom area)

### DRC Settings (JLCPCB compatible)
```
Minimum clearance:      0.15mm
Minimum trace width:    0.15mm
Minimum via diameter:   0.6mm
Minimum via drill:      0.3mm
Copper to edge:         0.3mm
```

Zero DRC errors required before Gerber export.

---

## Design Decisions Log

| Decision | Rationale |
|----------|-----------|
| Single-cell LiPo + boost (not 2S + buck) | TP4056 charger + DW01A protection proven on Pod. Lower voltage = safer for kids. Full reuse of Pod charging circuit. 2000mAh cell mitigates runtime. |
| TPS61023 boost converter | 3.7A peak current, SOT-563 (tiny), $0.14 on LCSC. Handles servo loads. OR-ing diodes merge USB and battery power seamlessly. |
| WS2812B RGB status LED | Single addressable LED on GPIO48. Provides boot/WiFi/error/OTA status via firmware color codes. Same part as Pod. |
| PCA9685 internal oscillator (no crystal) | PCA9685 has NO external oscillator pins (TSSOP-28). Internal 25MHz is ±10%, fine for 50Hz servo PWM. |
| GPIO35-37 reserved for PSRAM | N16R8 uses Octal SPI PSRAM on GPIO35-37. Camera DVP reassigned to avoid these. |
| Reset button (SW2) added | Standard ESP32 practice. Simplifies boot mode entry (hold BOOT + press RESET). Without it, must power-cycle. |
| Single-cell LiPo (not 2S) | TP4056 only charges single-cell. Simplifies power. Servos run fine on 5V from USB. |
| SPH0641 PDM mic (not INMP441 I2S) | INMP441 unavailable at LCSC. SPH0641 proven on Pod, cheaper, smaller, saves 1 GPIO pin. |
| AP2112K LDO (not AMS1117) | Proven on Pod. Lower dropout (250mV vs 1V). Same SOT-23-5 footprint. |
| Separate +5V_SERVO rail | Servo inrush can brown out ESP32 if shared. Direct USB-to-servo with bulk caps. |
| Camera I2C on separate bus (GPIO47/48) | DVP camera SCCB protocol can interfere with main I2C bus. Separate bus avoids conflicts. |

---

## Next Steps After Schematic

1. **Assign footprints** — Tools → Edit Symbol Fields → verify all footprints
2. **Export netlist** — File → Export → Netlist
3. **PCB layout** — Transfer netlist, place components per layout rules above
4. **DRC** — Zero errors before Gerber export
5. **Generate Gerbers + BOM + CPL** for JLCPCB
6. **Order prototype run** (qty 5, ~$30-50 total with assembly)
