# HawaBot

Physical AI robotics platform for kids. Part of [Hawa Labs](https://hawalabs.com).

Kids design a custom robot character, Hawa Labs 3D prints and ships it, then kids code and teach their robot using Python + an AI tutor.

## Project Structure

```
hawabot/                      SDK — Python package shipped with every kit
├── robot.py                  Student entry point
├── character/                Character profiles + animations
├── config/                   Hardware tier definitions (Spark/Core/Pro)
├── joints/                   Body parts (head, arm, waist, leg)
├── drivers/                  Hardware abstraction (mock, pico, pi5)
├── sensors/                  Sensor abstractions
├── sim/                      Simulation engine + 2D visualizer
├── teach.py                  Teach-by-demo (record + playback)
├── curriculum/               Mission loader + progress tracker
├── tutor/                    AI tutor + safety filter
└── studio/                   Streamlit IDE

pipeline/                     Shell pipeline — the moat
├── skeleton.py               Spark skeleton geometry generator
├── shell_pipeline.py         Scale → Subtract → Trim → Validate
├── joint_cuts.py             Joint clearance cuts + section splitting
├── preview.py                3D preview renderer (matplotlib)
├── SKELETON_SPEC.md          Parametric SolidWorks reference
└── skeleton_exports/         SolidWorks parameter files + exported STLs

web/                          Design platform prototype
├── app.py                    Flask backend (Meshy API + pipeline)
└── templates/index.html      Three.js frontend

missions/                     Curriculum content (5 months)
├── month_01/ ... month_05/

docs/                         Documentation
├── STRATEGY.md               Vision, moat, business model
├── COMPETITIVE_ANALYSIS.md   Feature matrix vs competitors
├── ARCHITECTURE.md           Technical architecture
├── IMPLEMENTATION_PLAN.md    Phased build plan
├── GO_TO_MARKET.md           GTM strategy
├── research/                 Original inspiration (slides, papers)
└── reference_robot/          Full-scale Hawabot specs (Poppy URDF, servos)
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[sim]"
pip install flask trimesh manifold3d scipy shapely rtree
```

### Run the SDK
```python
from hawabot import Robot

robot = Robot()
robot.head.pan(45)
robot.arm.left.wave()
robot.express("happy")

recording = robot.teach(5)
robot.play(recording)
robot.shutdown()
```

### Run the Design Platform
```bash
python web/app.py
# Open http://localhost:5001
```

### Run the Shell Pipeline
```bash
python -m pipeline.shell_pipeline sculpture.stl skeleton.stl output_shell.stl
```

## Hardware Tiers

| Tier | Form | DOF | Voice | BOM | Price |
|------|------|-----|-------|-----|-------|
| **Spark** | Tabletop companion | 5 | Buzzer | ~$69 | $99 / $25mo |
| **Core** | Enhanced upper body | 10 | Mic + speaker | ~$200 | $249 / $55mo |
| **Pro** | Full bipedal | 21 | HQ mic + speaker | ~$400 | $499 / $110mo |

## Environment Variables

```bash
HAWABOT_MOCK=1             # Force simulation mode (default)
ANTHROPIC_API_KEY=sk-...   # Required for AI tutor
MESHY_API_KEY=...          # Required for real 3D generation
```
