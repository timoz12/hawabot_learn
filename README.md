# HawaBot SDK

Physical AI robotics platform for kids. Part of [Hawa Labs](https://hawalabs.com).

## What This Is

An SDK, curriculum engine, and AI tutor — all in one Python package.
Students write real Python code that controls a real robot, guided by an AI tutor
that teaches **robotics concepts first, coding second**.

## Quick Start

```python
from hawabot import Robot

robot = Robot()          # Auto-detects hardware tier
robot.head.pan(45)       # Move head 45° right
robot.arm.left.wave()    # Wave left arm
robot.shutdown()         # Return to rest
```

## Launch the Studio

```bash
pip install -e .
streamlit run hawabot/studio/app.py
```

## Hardware Tiers

| Tier | Servos | Compute | Cost |
|------|--------|---------|------|
| Spark (default) | SG90 / MG90S | Pi Pico W | ~$69 BOM |
| Core | Feetech STS3215 | Pi 5 | ~$200 BOM |
| Studio | Dynamixel XL430/330 | Pi 5 | ~$400 BOM |

The SDK auto-detects tier. Student code never changes between tiers.

## Curriculum Structure

```
missions/
  month_01/  — Joints, DOF, basic motion
  month_02/  — Sensing (ultrasonic, IMU)
  month_03/  — Feedback loops (sensor → motion)
  month_04/  — Computer vision
  month_05+  — Robot brain architecture, LLMs
```

## Safety

The AI tutor has a dedicated child safety layer:
- Every student message is classified before reaching the tutor LLM
- Emotional distress events flag to parent dashboard (no message content stored)
- Tutor stays strictly on robotics/science/math topics
- Uses Claude Haiku for safety classification, Claude Sonnet for tutoring

## Project Structure

```
hawabot/
├── robot.py              # Student entry point
├── joints/               # Head, Arm, Leg body parts
├── drivers/              # Hardware tier abstraction
├── sensors/              # Ultrasonic, IMU, Camera
├── curriculum/           # Mission loader + progress tracker
├── tutor/                # AI tutor + safety filter
└── studio/               # Streamlit IDE
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...   # Required for AI tutor
HAWABOT_MOCK=1             # Force simulation mode (no hardware)
```
