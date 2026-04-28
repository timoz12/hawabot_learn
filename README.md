# HawaBot

Physical AI robotics platform for kids. Part of [Hawa Labs](https://hawalabs.com).

Kids design a custom robot character, Hawa Labs 3D prints and ships it, then kids code and teach their robot using Python + an AI tutor.

## What's Here

### 1. HawaBot SDK (`hawabot/`)
Python package that ships with every kit. Controls the robot, runs the curriculum, powers the AI tutor.

```python
from hawabot import Robot

robot = Robot()              # Loads character profile, simulation mode
robot.head.pan(45)           # Turn head right
robot.arm.left.wave()        # Wave animation
robot.waist.turn(-20)        # Turn upper body
robot.express("happy")       # Character-specific expression

recording = robot.teach(5)   # Record 5 seconds of motion (teach-by-demo)
robot.play(recording)        # Play it back

robot.shutdown()             # Return to rest
```

### 2. Shell Pipeline (`pipeline/`)
The moat: takes any 3D sculpture (from AI generation), subtracts the standard servo skeleton, and outputs printable shell sections.

```bash
python -m pipeline.shell_pipeline sculpture.stl skeleton.stl output_shell.stl
python -m pipeline.joint_cuts output_shell.stl
```

Pipeline: **Scale** skeleton to fit → **Subtract** from sculpture → **Cut** joint clearances → **Split** into printable sections → **Validate** watertightness.

### 3. Design Platform (`web/`)
Web prototype for the customer-facing design platform. Three.js 3D viewer, Meshy API integration (mock or real), tier/plan selection.

```bash
python web/app.py
# Open http://localhost:5001
```

## Hardware Tiers

| Tier | Form | DOF | Servos | Compute | BOM |
|------|------|-----|--------|---------|-----|
| **Spark** | Tabletop companion | 5 | SG90/MG90S | Pi Pico W | ~$69 |
| **Core** | Enhanced upper body | 10 | Feetech STS3215 | Pi 5 | ~$200 |
| **Pro** | Full bipedal | 21 | Dynamixel XL430/330 | Pi 5 | ~$400 |

Spark is a desk companion (head + arms + waist). Core adds elbows and teach-by-demo. Pro adds legs for walking.

## Curriculum (5 months)

| Month | Topic | Tier Required |
|-------|-------|---------------|
| 1 | Joints, DOF, basic motion | Spark+ |
| 2 | Sensing: ultrasonic, reactions | Spark+ |
| 3 | Feedback loops, IMU balance | Core+ |
| 4 | Computer vision | Pro |
| 5 | Robot brain: RL, LLM integration | Pro |

## Reference (`hawabot_reference/`)
Specs and engineering lessons from the full-scale development robot (Poppy-based, 20 DOF, 913mm). Used to derive joint limits, servo specs, and curriculum content for the educational versions.

## Environment Variables

```bash
HAWABOT_MOCK=1             # Force simulation mode (default)
ANTHROPIC_API_KEY=sk-...   # Required for AI tutor
MESHY_API_KEY=...          # Required for real 3D generation
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[sim]"
pip install flask trimesh manifold3d scipy shapely rtree
```
