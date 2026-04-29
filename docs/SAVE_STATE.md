# HawaBot — Project Save State

**Last updated:** 2026-04-29
**Purpose:** Complete reference of everything implemented, decided, and in-progress. Portable to any platform.

---

## 1. What Is HawaBot

A customizable robotics platform where customers design a character (via photo/text/template), and we produce a 3D-printed shell that snaps onto a standardized robot skeleton. Kids learn to code their robot through an AI-powered tutor.

**Business model:** B2C — sell skeleton kits + custom character shells, with an AI tutoring subscription.

---

## 2. Architecture Overview

```
Customer designs character (web app)
        ↓
2D reference views generated (cheap)
        ↓
Customer confirms → purchases
        ↓
3D model generated (Tripo3D / Meshy API)
        ↓
Shell pipeline: dissect → hollow → magnets → validate → export
        ↓
3D print + ship shells
        ↓
Customer snaps shells onto skeleton, codes robot via AI tutor
```

### System Components

| Component | Location | Status |
|---|---|---|
| **Design Platform** | `web/` | Flask + Three.js scaffold, needs rebuild |
| **Shell Pipeline** | `pipeline/` | Core modules implemented (Apr 2026) |
| **SDK** | `hawabot/` | Python package for controlling robot |
| **PicoDriver** | `hawabot/drivers/pico.py` | Implemented (Apr 2026) |
| **Firmware** | `firmware/pico_w/main.py` | MicroPython, WiFi servo control |
| **AI Tutor** | `hawabot/tutor/` | Not started |
| **Curriculum** | — | Not started |

---

## 3. Hardware — Spark Skeleton (200mm)

### Key Decision: Frame + Shell Model

The skeleton is a **standalone mechanical robot** — it works without shells. Custom character shells snap on via magnets. This replaces the earlier "subtract skeleton from sculpture" approach.

| Parameter | Value |
|---|---|
| **Total height** | 200mm (8-inch action figure scale) |
| **Servos** | 3× SG90 (waist, head pan, head tilt) + 2× MG90S (shoulders) |
| **DOF** | 5 (waist yaw, head pan, head tilt, L/R shoulder pitch) |
| **Controller** | Raspberry Pi Pico W |
| **Magnet seats** | 40 × ⌀6×3mm neodymium disc magnets |
| **Body zones** | Head, torso, left arm, right arm, base |
| **Frame** | Single 3D-printed part (PLA/PETG) |

### Servo Positions (Z-up, origin = base plate top center)

| Servo | Position | Shaft | Joint |
|---|---|---|---|
| Waist | (0, 0, 10) | +Z | Yaw |
| Left shoulder | (-40, 0, 110) | -X | Pitch |
| Right shoulder | (40, 0, 110) | +X | Pitch |
| Head pan | (0, 0, 120) | +Z | Yaw |
| Head tilt | (0, 0, 148) | +Y | Pitch |

### Specification Files

| File | Purpose |
|---|---|
| `pipeline/SKELETON_SPEC.md` | Mechanical frame design (servos, magnets, wiring) |
| `pipeline/INTERFACE_SPEC.md` | Contract between skeleton and shells |
| `pipeline/SHELL_PIPELINE_SPEC.md` | Customer workflow (design → print) |
| `pipeline/SOLIDWORKS_BUILD_GUIDE.md` | Parametric SolidWorks build instructions |
| `pipeline/skeleton_exports/equations.txt` | SolidWorks global equations file |

### Generated CAD Files

| File | Format | Purpose |
|---|---|---|
| `pipeline/skeleton_exports/spark_skeleton_frame.step` | STEP | Frame for SolidWorks import |
| `pipeline/skeleton_exports/spark_skeleton_frame.stl` | STL | For 3D printing |
| `pipeline/skeleton_exports/sg90_reference.step` | STEP | SG90 servo reference model |
| `pipeline/skeleton_exports/mg90s_reference.step` | STEP | MG90S servo reference model |
| `pipeline/skeleton_exports/magnet_6x3_reference.step` | STEP | Magnet reference model |

---

## 4. Shell Pipeline — Code Modules

All in `pipeline/`. Dependencies: `trimesh`, `manifold3d`, `numpy`.

| Module | Purpose | Status |
|---|---|---|
| `skeleton.py` | Central dimensions, magnet grid, cut planes, envelopes | **Done** |
| `dissect.py` | Slice character mesh into 5 body zones | **Done** |
| `hollow.py` | Hollow solid zones into printable shells | **Done** |
| `magnets.py` | Select optimal magnets + generate boss geometry | **Done** |
| `validate.py` | Wall thickness, clearance, weight, watertight checks | **Done** |
| `shell_pipeline.py` | Orchestrator — runs full pipeline end-to-end | **Done** |
| `generate_skeleton_step.py` | CadQuery script to generate skeleton STEP/STL | **Done** |
| `joint_cuts.py` | Joint clearance cuts (legacy, needs update) | Needs rework |

### Pipeline Usage

```bash
python -m pipeline.shell_pipeline path/to/character.stl output/shells/
```

### Pipeline Flow

```
load_and_prepare()     → Scale, center, repair mesh
dissect_character()    → Cut into 5 zones at adjustable planes
hollow_zone()          → Offset inward, boolean subtract, open attachment face
select_magnets()       → Pick optimal magnet positions from skeleton grid
add_magnet_bosses()    → Boolean union boss cylinders onto shell interior
validate_shell()       → Wall thickness, weight, clearance, watertight checks
export STL             → One file per zone
```

---

## 5. PicoDriver — Firmware & SDK

### Firmware (`firmware/pico_w/main.py`)

MicroPython running on Pi Pico W. Starts a WiFi access point, listens for JSON commands over TCP socket. Controls up to 8 PWM servo channels.

### Driver (`hawabot/drivers/pico.py`)

Python class `PicoDriver` that connects to the Pico W over WiFi and sends servo angle commands. Used by `hawabot/robot.py` to expose a high-level API.

### Robot API (`hawabot/robot.py`)

```python
from hawabot import Robot
robot = Robot(driver="pico", host="192.168.4.1")
robot.move("head_pan", 45)
robot.wave()
```

---

## 6. 3D Generation Platform — Recommendation

**Primary: Tripo3D** — best value for 3D-printable action figures.

| Metric | Tripo3D | Meshy (fallback) |
|---|---|---|
| Cost per model | ~$0.01/credit via API | ~$0.03-0.06/model |
| Speed | <10 seconds | 30-60 seconds |
| Watertight output | Yes (guaranteed manifold) | Yes |
| Export formats | GLB, OBJ, STL, FBX, USD, 3MF | GLB, OBJ, STL, FBX, USDZ |
| API | REST, independent billing | REST, Pro+ tier |
| 3D print features | Pre-hollowed, multi-part assembly | Standard |

**Strategy:** Start with Tripo3D API. Fall back to Meshy for models needing finer detail (faces, hands). Test both via fal.ai ($0.20-0.40/model) before committing to direct subscriptions.

---

## 7. Key Design Decisions Made

| Decision | Choice | Why |
|---|---|---|
| Skeleton height | 200mm | SG90 servos need room; 150mm too cramped for aesthetics |
| Skeleton approach | Standalone frame + magnetic snap-on shells | Cleaner separation, swappable characters, simpler manufacturing |
| Shell attachment | 6×3mm neodymium disc magnets | No tools, instant snap-on/off, works with any character |
| Magnet strategy | 40 predefined seats, software selects subset | One skeleton design, infinite shell compatibility |
| Frame printing | Single part, not sectioned | Only shells get split into body zones |
| Cut planes | Customer-adjustable during guided dissection | Different characters have different proportions |
| 3D gen platform | Tripo3D (primary), Meshy (fallback) | Best value watertight mesh for 3D printing |
| Tier strategy | Spark only for now; Core/Pro later | Ship one thing well first |
| Skeleton variant | Humanoid only for now; stumpy/creature later | Focus on action figure market first |

---

## 8. File Inventory

```
hawabot_learn/
├── hawabot/                    # Python SDK
│   ├── __init__.py
│   ├── robot.py                # High-level robot API
│   ├── drivers/
│   │   └── pico.py             # PicoDriver (WiFi servo control)
│   └── tutor/                  # AI tutor (not started)
│
├── firmware/
│   └── pico_w/
│       └── main.py             # MicroPython firmware
│
├── pipeline/                   # Shell manufacturing pipeline
│   ├── SKELETON_SPEC.md        # Frame design spec
│   ├── INTERFACE_SPEC.md       # Shell↔skeleton contract
│   ├── SHELL_PIPELINE_SPEC.md  # Customer workflow spec
│   ├── SOLIDWORKS_BUILD_GUIDE.md
│   ├── skeleton.py             # Dimensions & magnet grid (data module)
│   ├── dissect.py              # Mesh → 5 zones
│   ├── hollow.py               # Solid → hollow shell
│   ├── magnets.py              # Magnet selection + boss gen
│   ├── validate.py             # Quality checks
│   ├── shell_pipeline.py       # Orchestrator
│   ├── generate_skeleton_step.py  # CadQuery STEP generator
│   ├── joint_cuts.py           # Legacy — needs rework
│   ├── skeleton_exports/       # Generated CAD files
│   │   ├── spark_skeleton_frame.step
│   │   ├── spark_skeleton_frame.stl
│   │   ├── sg90_reference.step
│   │   ├── mg90s_reference.step
│   │   ├── magnet_6x3_reference.step
│   │   └── equations.txt
│   └── preview.py              # 3D preview (legacy)
│
├── web/                        # Design platform (Flask + Three.js)
│   └── app.py                  # Needs rebuild for new workflow
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── STRATEGY.md
│   ├── COMPETITIVE_ANALYSIS.md
│   ├── GO_TO_MARKET.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── SAVE_STATE.md           # This file
│   ├── NEXT_TASK.md            # Upcoming work
│   └── reference_robot/
│
└── tests/                      # Not yet created
```

---

## 9. Dependencies

### Python (SDK + Pipeline)

```
trimesh          # Mesh loading, manipulation
manifold3d       # Robust boolean operations
numpy            # Geometry math
cadquery          # Parametric CAD (STEP generation) — Python 3.13 required
flask            # Web app
```

### Firmware

```
MicroPython      # Running on Pi Pico W
```

### External APIs

```
Tripo3D API      # Primary 3D model generation
Meshy API        # Fallback 3D generation
Claude API       # AI tutor (planned)
```

---

## 10. Git Info

- **Remote:** `https://github.com/timoz12/hawabot_learn.git` (remote name: `hawabot_learn`)
- **Main branch:** `main`
- **Working branch:** `master`
- **CadQuery venv:** `/tmp/cad_env` (Python 3.13 — CadQuery doesn't work on 3.14)
