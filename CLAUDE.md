# Project: HawaBot Learn

A character-driven physical AI robotics platform that teaches systems engineering to ages 12-15. Students build and operate a humanoid robot while learning how mechanical, electrical, firmware, networking, and AI layers connect.

**This is NOT a "learn to code" platform.** Students use AI to help with code. The curriculum teaches how systems work.

---

## Tech Stack

### Robot Hardware (Spark + Pro — 250mm)
- **MCU:** ESP32-S3-WROOM-1-N16R8 (16MB flash, 8MB PSRAM, FCC modular cert, WiFi/BT)
- **Servo control:** PCA9685 (I2C, 16-ch PWM) for SG90/MG90S; Dynamixel bus for XL330 (Pro)
- **Audio out:** MAX98357A (I2S amp)
- **Audio in:** SPH0641LU4H-1 (PDM MEMS mic, Knowles, Pro only)
- **IMU:** MPU6050 (I2C, Pro only)
- **FSRs:** Force Sensitive Resistors in feet (Pro only, required for walking)
- **Camera:** OV2640 DVP (Pro only)
- **Servos:** SG90 (low-load), MG90S (waist/shoulders), XL330 (shoulders+legs on Pro)
- **Custom PCB:** ~55x35mm 2-layer, same board for Spark and Pro (Pro populates more components)
- **Dev board for prototyping:** ESP32-S3-DevKitC-1

### Robot Hardware (Max — future flagship, 400-500mm)
- **Size:** 400-500mm (different skeleton, not upgrade-compatible with 250mm)
- **MCU:** CM5 or Pi 5 (on-board AI, fully autonomous)
- **Servos:** XL330 throughout + XL430 for high-torque joints
- **Power:** On-board battery, untethered
- **Target:** Enthusiasts who completed Spark → Pro curriculum. Aspirational flagship for marketing.
- **Price:** $999+ depending on options

### Software
- **Robot firmware:** ESP-IDF / Arduino / MicroPython on ESP32-S3
- **SDK:** Python 3.10+ (`hawabot` package)
- **Pipeline:** CadQuery + trimesh + manifold3d (3D geometry)
- **Web app:** Flask + Three.js (prototype), Next.js (production)
- **AI tutor:** Anthropic Claude API (runs on phone/tablet, not robot)
- **3D generation:** Meshy AI API

### Architecture
- AI is **offloaded** to phone/tablet/computer via WiFi
- Robot handles real-time: servo control, audio, sensors
- Phone handles heavy: AI inference, voice recognition, curriculum UI
- No cables — WiFi only (robot moves freely within WiFi range)

---

## Tiers

Two tiers at launch. Max is a future aspirational product.

| | Spark ($199) | Pro ($599) | Max (future, $999+) |
|---|---|---|---|
| DOF | 7 | 19 | 19+ |
| Size | 250mm | 250mm (same skeleton) | 400-500mm (separate product) |
| Compute | ESP32-S3 | ESP32-S3 (same PCB) | CM5 / Pi 5 (on-board AI) |
| Audio | Speaker | Speaker + mic | Speaker + mic array |
| Sensors | None | IMU + FSRs + camera | Full suite + LIDAR |
| Legs | No (flat base) | **Yes (walking)** | Yes (advanced gait) |
| Arms | Shoulder pitch + roll | + elbows + hands | Full articulation |
| Power | USB-C (wall) | **Battery** | Battery (large) |
| AI brain | Phone via WiFi | Phone via WiFi | **On-board (autonomous)** |
| Upgrade from Spark? | — | **Yes** ($399 add-on) | No (separate robot) |
| Target | Entry, kids + parents | Serious learners | Enthusiasts, graduates |

### Upgrade Path
```
Spark ($199) ──add legs+arms+sensors──> Pro ($599 all-in, or $399 upgrade)
                                            │
                                            │ (complete full curriculum)
                                            v
                                        Max ($999+) — the "real deal"
                                        400-500mm, on-board AI, autonomous
                                        Aspirational. Marketing flagship.
                                        Few units sold to enthusiasts.
```

---

## Conventions

### Code
- Python 3.10+ for SDK and pipeline
- Use `ruff` for linting
- Type hints on public APIs
- No docstrings on internal/private methods unless logic is non-obvious
- ESP32 firmware: Arduino framework or ESP-IDF (C/C++)

### Git
- Branch from `main` for features
- Conventional commit messages (feat:, fix:, docs:, refactor:)
- Don't commit .env, credentials, or large binary files

### File Organization
- `hawabot/` — Python SDK (shipped with kits)
- `pipeline/` — 3D geometry pipeline (server-side)
- `firmware/` — ESP32 and microcontroller firmware
- `web/` — Web app (design platform)
- `missions/` — Curriculum content
- `docs/` — Strategy, architecture, research
- `pipeline/skeleton_exports/solidworks_package/` — SolidWorks build package (copied to SW machine)

### 3D Models
- All character models must be T-pose for clean dissection
- Skeleton is standalone frame; shells are magnetic snap-on cosmetic parts
- 5 body zones: head, torso, L arm, R arm, base (+ legs for Pro)

### Hardware Design
- SolidWorks for prototype validation (golden baseline)
- CadQuery for automated per-character skeleton generation
- Custom PCB designed in KiCad, fabricated at JLCPCB
- FCC modular certification required for production MCU
- FSRs in feet required for walking (Pro tier)

---

## Current State

### What's Built
- Python SDK: robot.py, drivers (mock, pico), joints, sim engine, character profiles
- Pipeline: skeleton generator, shell pipeline, dissection, magnet placement
- SolidWorks: v17 macro (21 planes, 13 axes, layout sketch), SSP validated (Phase 1-2 done)
- Firmware: Pi Pico W MicroPython servo controller (legacy, needs ESP32-S3 port)
- Web: Flask prototype with Meshy AI integration
- Docs: strategy, architecture, competitive analysis, build guides

### What's In Progress
- SolidWorks Phase 3-6: master assembly, servo placement, kinematics testing
- Custom PCB design (prototyping with ESP32-S3-DevKitC-1 + breakout boards)
- Curriculum content (month structure exists, content TBD)

---

## Key Design Decisions (Current)

1. **Two tiers at launch** — Spark ($199, desk companion) and Pro ($599, walking humanoid). No Core tier.
2. **Max is aspirational** — 400-500mm flagship, $999+, on-board AI. Few units. Marketing vehicle. For graduates.
3. **ESP32-S3 for production** — FCC modular cert, $3/unit, team has ESP32 experience
4. **AI offloaded to phone** — robot is the body, phone is the brain
5. **Prototype with SG90/MG90S/XL330** — then optimize servos for production
6. **XL330 at shoulders+legs for Pro** — dual shaft + idler, Dynamixel bus
7. **MG90S at shoulders for Spark production** — only 15-20g load, cantilever acceptable
8. **SolidWorks → CadQuery hybrid pipeline** — SW validates once, CQ scales to many characters
9. **Same 250mm skeleton for Spark and Pro** — Pro adds legs to same frame
10. **One custom PCB** — Pro populates more components (mic, IMU, FSR inputs, camera, battery)
11. **Systems engineering curriculum** — not "learn to code"
12. **Credits model** — Fortnite-style add-ons (movement packs, voice types, characters)
13. **FSRs required for walking** — confirmed from Poppy humanoid research
14. **Pro needs battery** — can't walk tethered to USB cable

---

## Security
- No secrets in code or git
- API keys via environment variables only
- Meshy AI and Anthropic keys in .env (never committed)
- FCC/CE compliance required for production
- CPSIA compliance for ages 12+ (no small parts concerns at this age)
