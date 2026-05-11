Update hawabot/config/tiers.py to match current hardware decisions.

Read CLAUDE.md and memory for current decisions, then update tiers.py with:

**Spark (7 DOF, $199):**
- MCU: ESP32-S3 (not Pi Pico W)
- Servos: 5x SG90 + 2x MG90S (production) or 5x SG90 + 1x MG90S + 2x XL330 (prototype)
- Joints: head_pan, head_tilt, l_shoulder_pitch, r_shoulder_pitch, l_shoulder_roll, r_shoulder_roll, waist_yaw
- Audio: speaker only
- Form: tabletop (250mm)

**Core (11 DOF, $299):**
- MCU: ESP32-S3 (same board as Spark, more populated)
- Servos: Spark + 4x SG90 (elbows + hands)
- Additional: IMU, mic, camera
- Form: tabletop (250mm)

**Pro (19 DOF, $599+, future):**
- MCU: CM5 or Pi 5
- Servos: SG90 + MG90S + XL330 (10x XL330 for shoulders+legs)
- Full sensor suite, battery, walking
- Form: bipedal (400-500mm, separate product)

Make sure ServoSpec definitions match actual servo dimensions from hawabot_globals.txt.
Do not change the public API (TierName enum, get_tier() function signature).
