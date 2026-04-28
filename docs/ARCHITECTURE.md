# HawaBot Technical Architecture

## System Overview

HawaBot is composed of five major subsystems that work together to deliver the full experience: design a character, manufacture the physical robot, code it, learn from it, and grow with it.

```
+---------------------+       +---------------------+       +---------------------+
|  DESIGN PLATFORM    |       |  SHELL PIPELINE     |       |  FULFILLMENT        |
|  (web/)             |  -->  |  (pipeline/)        |  -->  |  3D Print + Ship    |
|  Flask + Three.js   |       |  trimesh+manifold3d |       |  (Manual / Partner) |
+---------------------+       +---------------------+       +---------------------+
                                                                      |
                                                                      v
+---------------------+       +---------------------+       +---------------------+
|  AI TUTOR           |  <->  |  SDK                |  <->  |  HARDWARE           |
|  (hawabot/tutor/)   |       |  (hawabot/)         |       |  Pi Pico W / Pi 5   |
|  Claude Haiku+Sonnet|       |  Python package     |       |  Servos + Sensors   |
+---------------------+       +---------------------+       +---------------------+
```

---

## 1. Design Platform (`web/`)

### Purpose

Customer-facing web application where kids design their robot character, preview it in 3D, and purchase a kit.

### Current Implementation

- **Framework:** Flask (Python) with Jinja2 templates
- **3D Viewer:** Three.js with STL loader for interactive preview
- **API Integration:** Meshy API for text-to-3D and image-to-3D generation
- **Pipeline Integration:** Calls shell pipeline directly for real-time preview

### Architecture

```
Browser (Three.js viewer)
    |
    v
Flask App (web/app.py)
    |
    +-- POST /api/generate
    |       |
    |       +-- Meshy API (text/image -> 3D mesh)    [or mock]
    |       +-- Shell Pipeline (mesh -> printable shell)
    |       +-- Joint Cuts (shell -> body sections)
    |       +-- Return section metadata + 3D URLs
    |
    +-- GET /api/model/<id>/<file>
    |       |
    |       +-- Serve STL/GLB files for viewer
    |
    +-- GET /
            |
            +-- Render index.html (design UI + Three.js)
```

### Data Flow: Character Design to Printable Shell

1. Kid enters text prompt or uploads sketch/photo
2. Platform calls Meshy API (~$0.30/generation, Meshy 6 model)
3. Meshy returns 3D mesh (STL, ~500K faces)
4. Shell pipeline processes mesh (see Section 2)
5. Three.js viewer displays shell sections with exploded view
6. Kid selects tier (Spark/Core/Pro) and plan (full/subscription)
7. Order queued for fulfillment

### Production Architecture (Planned)

```
Next.js Frontend (React + Three.js Fiber)
    |
    v
API Layer (Next.js API routes or FastAPI)
    |
    +-- Auth (Clerk or Auth0)
    +-- Payment (Stripe)
    +-- Meshy API (3D generation)
    +-- Pipeline Worker (async shell processing)
    +-- Order DB (PostgreSQL)
    +-- Fulfillment Queue (webhook to print farm)
```

---

## 2. Shell Pipeline (`pipeline/`)

### Purpose

The core technical moat. Converts any arbitrary 3D sculpture mesh into a set of printable shell sections that fit around a standard servo skeleton.

### Pipeline Stages

```
INPUT: sculpture.stl (from Meshy or upload)
  |
  v
[1] SCALE ── scale_skeleton_to_sculpture()
  |   - Center both meshes on same origin
  |   - Scale skeleton uniformly to fit inside sculpture
  |   - Maintain padding_mm (default 3mm) for wall thickness
  |   - Clamp scale factor >= 0.5 (never shrink below 50%)
  |
  v
[2] SUBTRACT ── subtract_skeleton()
  |   - Convert trimesh -> manifold3d Manifold objects
  |   - Boolean difference: sculpture - skeleton
  |   - manifold3d guarantees watertight output
  |   - Convert result back to trimesh
  |
  v
[3] TRIM ── trim_shell()
  |   - Remove degenerate and duplicate faces
  |   - Remove unreferenced vertices
  |   - Split into bodies, discard fragments < 10% of largest
  |   - Concatenate remaining bodies
  |
  v
[4] VALIDATE ── validate_shell()
  |   - Check watertightness
  |   - Measure bounding box dimensions
  |   - Ray-cast wall thickness estimation (500 samples)
  |   - Report: min/avg/max wall thickness, volume, face count
  |   - Printability pass/fail (watertight + no degenerate + min wall >= 1mm)
  |
  v
[5] JOINT CUTS ── cut_joint_clearances()
  |   - Define clearance volumes for each joint's range of motion
  |   - Boolean subtract clearance volumes from shell
  |   - Joints: head pan/tilt, shoulder pitch, waist yaw
  |
  v
[6] SPLIT ── split_shell()
  |   - Cut shell into body sections using half-space intersections
  |   - Sections: head, torso, left_arm, right_arm, base
  |   - Each section is independently watertight
  |
  v
OUTPUT: section_head.stl, section_torso.stl, section_left_arm.stl, etc.
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **manifold3d for booleans** | Only library that guarantees watertight output. CGAL is too slow. Trimesh booleans are unreliable on complex meshes. |
| **trimesh for I/O and analysis** | Best Python mesh library for loading, repair, measurement, export. |
| **Scale skeleton, not sculpture** | Preserves character proportions. Skeleton is engineered; sculpture is artistic. |
| **Split into sections** | Required for 3D printing (no support material inside cavities). Also enables magnetic snap-fit assembly. |
| **Magnets for attachment** | 6x2mm N35 neodymium magnets + snap-fit clips. Kid-friendly assembly, no tools required. |

### Skeleton Specification

The skeleton is defined parametrically in `pipeline/skeleton.py` based on the tier's servo dimensions and joint layout.

**Spark Skeleton (5 DOF):**
```
Joint Layout:
  - Head Pan (yaw): SG90, +-90 deg
  - Head Tilt (pitch): SG90, +-45 deg
  - Left Shoulder (pitch): MG90S, +-90 deg
  - Right Shoulder (pitch): MG90S, +-90 deg
  - Waist (yaw): SG90, +-60 deg

Physical Layout:
  [HEAD] ---- head pan servo + tilt servo
    |
  [TORSO] --- shoulder servos (spread = 40mm each side)
    |
  [BASE] ---- waist servo
```

**Core Skeleton (10 DOF):** Adds shoulder roll, elbow pitch, arm rotation per arm.

**Pro Skeleton (21 DOF):** Adds 10-DOF leg assembly (hip pitch/roll/yaw, knee, ankle pitch/roll per leg) plus wrist.

---

## 3. SDK (`hawabot/`)

### Package Structure

```
hawabot/
  __init__.py          # Exports Robot
  robot.py             # Robot class — main entry point
  config/
    tiers.py           # Tier definitions (Spark/Core/Pro), joint specs
  character/
    profile.py         # CharacterProfile (YAML-based)
    profiles/          # Default character YAML files
    animations.py      # Character-specific animations + expressions
  joints/
    head.py            # Head (pan, tilt, nod, shake)
    arm.py             # Arms (wave, reach, elbow bend)
    waist.py           # Waist (turn)
    leg.py             # Legs (Pro only — walk, balance, kick)
  drivers/
    base.py            # BaseDriver ABC
    mock.py            # MockDriver for simulation
    pico.py            # PicoDriver — serial to Pi Pico W (Spark)
    pi5.py             # Pi5Driver — I2C/UART to smart servos (Core/Pro)
  sensors/             # Ultrasonic, IMU, camera abstractions
  sim/
    engine.py          # SimulationEngine — tracks joint state
    visualizer.py      # Matplotlib-based pose visualization
  teach.py             # Teach-by-demo: record() and playback()
  curriculum/          # Mission validation helpers
  tutor/               # AI tutor integration
  studio/              # Streamlit-based visual tool (optional)
```

### Core Abstractions

#### Robot (Entry Point)

```python
from hawabot import Robot

robot = Robot()                    # Auto-detect tier, load character profile
robot = Robot(tier="spark")        # Force tier
robot = Robot(mock=True)           # Force simulation mode
robot = Robot(character_path="my_character.yaml")
```

The `Robot` class:
- Loads the character profile (YAML) or uses defaults
- Detects hardware tier or falls back to simulation
- Instantiates the appropriate driver (MockDriver, PicoDriver, Pi5Driver)
- Creates body part objects (Head, Arms, Waist, optionally Legs)
- Provides high-level methods: `express()`, `teach()`, `play()`, `shutdown()`

#### Driver Abstraction

```
BaseDriver (ABC)
  |
  +-- MockDriver       # Logs commands, simulates joint state
  |
  +-- PicoDriver       # Serial/USB to Pi Pico W (PWM servos)
  |
  +-- Pi5Driver        # I2C/UART to smart servos (STS3215/Dynamixel)
```

All drivers implement the `BaseDriver` ABC (`hawabot/drivers/base.py`):
- `set_angle(joint_name, angle)` — command a joint to a target angle (degrees)
- `get_angle(joint_name)` — read current angle (degrees)
- `get_temperature(joint_name)` — actuator temperature in °C, or None if unsupported
- `get_voltage()` — supply voltage, or None if unsupported
- `wait(seconds)` — block for animation timing
- `get_event_log()` — ordered list of events for curriculum validation
- `shutdown()` — return all joints to rest and release resources

#### Character Profile System

```yaml
# character.yaml
name: "FireDrake"
tier: "spark"
personality: "brave and curious"
animations:
  happy:
    - {head_tilt: 15, duration: 0.3}
    - {left_shoulder: 45, right_shoulder: 45, duration: 0.5}
  greeting:
    - {head_pan: -30, duration: 0.3}
    - {head_pan: 30, duration: 0.3}
    - {head_pan: 0, left_shoulder: 90, duration: 0.5}
expressions:
  happy: "happy"
  sad: "thinking"
  excited: "greeting"
```

Loaded by `CharacterProfile.load()` using Pydantic for validation. Falls back to default profile if no custom file exists.

#### Teach-by-Demo

```python
# Record
recording = robot.teach(duration=5, sample_rate_hz=20)

# On real hardware (Core/Pro): servos enter compliance mode,
# kid physically moves the robot's arms/head,
# positions are sampled at 20 Hz.

# On simulation: gentle random motion is simulated.

# Playback
robot.play(recording, speed=1.0)

# Save/Load
recording.save("my_dance.json")
loaded = Recording.load("my_dance.json")
robot.play(loaded)
```

The Recording object stores timestamped joint positions as a list of frames. Serialized as JSON with character name and tier metadata.

### Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| pyyaml | Character profile loading | Yes |
| pydantic | Config validation | Yes |
| matplotlib | Simulation visualization | Optional (`[sim]`) |
| anthropic | AI tutor | Optional (`[tutor]`) |
| streamlit | Visual studio tool | Optional (`[studio]`) |

---

## 4. AI Tutor (`hawabot/tutor/`)

### Architecture

```
Student Input (text)
    |
    v
[SAFETY LAYER] ── Claude Haiku (fast, cheap)
    |   - COPPA compliance check
    |   - PII detection and rejection
    |   - Content appropriateness filter
    |   - No child messages stored
    |
    v  (passes safety check)
[TUTOR LAYER] ── Claude Sonnet (capable, pedagogical)
    |   - System prompt: robotics educator persona
    |   - Mission context injection (current lesson objectives)
    |   - Character-aware ("Let's make FireDrake wave!")
    |   - Socratic method (questions, not answers)
    |   - Code suggestions scoped to SDK
    |
    v
Tutor Response (text + optional code)
```

### V1 Implementation

- **No RAG** — system prompt + mission context injection is sufficient for V1
- **Stateless** — each request includes system prompt + current mission + recent conversation (last 5 turns)
- **Character injection** — tutor references the kid's character name and tier capabilities
- **Guardrails** — tutor only suggests code using the hawabot SDK; does not generate arbitrary Python

### System Prompt Structure (V1)

```
[Role] You are a robotics tutor for a kid using HawaBot.
[Character] The student's robot is named {name}, a {personality} character.
[Tier] The robot is a {tier} with {dof} degrees of freedom.
[Mission] Current mission: {mission_title}. Objectives: {objectives}.
[Pedagogy] Use Socratic method. Ask questions before giving answers.
           Relate concepts to the physical robot. Use the character's name.
[Safety] Never store or request personal information. Keep responses
         age-appropriate. If unsure, redirect to the mission topic.
[SDK] Only suggest code using the hawabot package. Available APIs: {api_list}
```

### Cost Model

| Component | Model | Cost per 1K tokens | Avg tokens/interaction | Cost/interaction |
|-----------|-------|--------------------|-----------------------|-----------------|
| Safety | Claude Haiku | $0.25/1M input | ~200 input | $0.00005 |
| Tutor | Claude Sonnet | $3/1M input | ~500 input + 300 output | $0.0024 |
| **Total** | | | | **~$0.003** |

At 50 interactions/student/month: ~$0.15/student/month. Negligible relative to kit price.

---

## 5. Curriculum System (`missions/`)

### Structure

```
missions/
  month_01/           # Joints, DOF, basic motion (Spark+)
  month_02/           # Sensing: ultrasonic, reactions (Spark+)
  month_03/           # Feedback loops, IMU balance (Core+)
  month_04/           # Computer vision, object tracking (Pro)
  month_05/           # Robot brain: RL, LLM integration (Pro)
```

Each month contains 5 missions. Each mission includes:
- **Prompt file** for the AI tutor (mission context, objectives, hints)
- **Starter code** for the student
- **Validation logic** (checks robot event log for expected behaviors)
- **Extension challenges** for advanced students

### Mission Validation

The SDK's event log system allows missions to programmatically verify that a student completed objectives:

```python
# Student code
robot.head.pan(45)
robot.arm.left.wave()

# Validation (run by curriculum system)
log = robot.event_log()
assert any(e["joint"] == "head_pan" and e["angle"] == 45 for e in log)
assert any(e["action"] == "wave" and e["side"] == "left" for e in log)
```

---

## 6. Hardware Abstraction

### Tier Definitions (`hawabot/config/tiers.py`)

Each tier defines:
- Joint names and limits (min/max angle, default speed)
- Servo type per joint
- Compute platform
- Available sensors
- Form factor (tabletop / upper_body / bipedal)

### Communication Protocols

| Tier | Compute | Protocol | Servos | Connection |
|------|---------|----------|--------|------------|
| Spark | Pi Pico W | USB Serial (115200 baud) | PWM (SG90/MG90S) | Direct GPIO (GP0-GP4) |
| Core | Pi 5 | Local | UART/TTL bus (STS3215) | Feetech bus adapter |
| Pro | Pi 5 | Local | UART/TTL bus (Dynamixel) | U2D2 adapter |

### PicoDriver — Spark Tier Hardware (`hawabot/drivers/pico.py`)

The PicoDriver enables the Spark tier by communicating with a Raspberry Pi Pico W over USB serial. The Pico W runs MicroPython firmware that drives PWM signals to 5 hobby servos.

**Architecture:**

```
Host (laptop)                          Pi Pico W (MicroPython)
  PicoDriver  ─── USB serial ───►  firmware/pico_w/main.py
              ◄── responses ────         │
                                         ├─ GP0  → waist_yaw (SG90)
                                         ├─ GP1  → left_shoulder_pitch (MG90S)
                                         ├─ GP2  → right_shoulder_pitch (MG90S)
                                         ├─ GP3  → head_pan (SG90)
                                         ├─ GP4  → head_tilt (SG90)
                                         └─ GP26 → VSYS ADC (battery voltage, optional)
```

**Serial Protocol (115200 baud, newline-terminated text):**

| Command | Response | Description |
|---------|----------|-------------|
| `S <pin> <pulse_us>` | `OK` | Set servo PWM pulse width |
| `V` | `V <float>` or `V NONE` | Read supply voltage via ADC |
| `P` | `PONG` | Ping / health check |

**PWM Calibration:**

Hobby servos (SG90/MG90S) accept 500–2500 µs pulses at 50 Hz:
- -90° → 500 µs
- 0° (centre) → 1500 µs
- +90° → 2500 µs
- Linear mapping: `pulse_us = 1500 + (angle / 90) * 1000`

**Key Design Decisions:**

| Decision | Rationale |
|----------|-----------|
| Track angles locally (no servo feedback) | SG90/MG90S have no position readback; store last-commanded angle |
| Simple text protocol | Easy to debug via serial monitor; MicroPython-friendly |
| Ping handshake on connect | Detects firmware issues immediately rather than failing on first command |
| Configurable pin map | Same driver works with alternative wiring; defaults match reference design |

**Firmware Installation:**

1. Flash MicroPython onto Pi Pico W (hold BOOTSEL, drag `.uf2` file)
2. Copy `firmware/pico_w/main.py` as `main.py` on the Pico W filesystem (via Thonny, mpremote, or rshell)
3. Power-cycle — firmware starts listening on USB serial immediately

### Sensor Abstraction

```
sensors/
  ultrasonic.py    # HC-SR04 (Spark+): distance measurement
  imu.py           # MPU6050 (Core+): orientation, acceleration
  camera.py        # Pi Camera (Pro): image capture, video stream
  microphone.py    # USB mic (Core+): audio capture for voice AI
```

---

## 7. Data Flow Diagrams

### End-to-End: Design to Learning

```
[Kid designs character] --> [Meshy API generates 3D] --> [Shell pipeline processes]
         |                                                        |
         v                                                        v
[Preview in browser]                                [STL files queued for printing]
         |                                                        |
         v                                                        v
[Select tier + purchase]                            [3D print + assemble + ship]
         |                                                        |
         v                                                        v
[Character profile YAML]  <----  [Kit arrives]  ---->  [Install SDK: pip install hawabot]
         |                            |                           |
         v                            v                           v
[AI tutor loaded with      [Physical robot assembled]    [from hawabot import Robot]
 character context]                   |                           |
         |                            v                           v
         +----------->  [Curriculum missions begin]  <-----------+
```

### Runtime: Student Coding Session

```
Student Python Script
    |
    +-- import hawabot
    |
    +-- Robot() instantiation
    |       +-- Load character profile (YAML)
    |       +-- Detect/select tier
    |       +-- Initialize driver (Mock/Pico/Pi5)
    |       +-- Build body parts (Head, Arms, Waist, Legs)
    |
    +-- robot.head.pan(45)
    |       +-- Driver.set_angle("head_pan", 45)
    |       +-- [Mock]: clamp angle, update state dict, log event
    |       +-- [Pico]: clamp angle → pulse_us → serial "S <pin> <us>" → PWM → servo moves
    |       +-- [Pi5]: clamp angle → UART packet → smart servo moves
    |
    +-- robot.express("happy")
    |       +-- Look up animation in character profile
    |       +-- Play sequence of joint movements
    |
    +-- robot.teach(5)
            +-- [Real]: enable compliance mode on smart servos
            +-- Record joint positions at 20 Hz for 5 seconds
            +-- Return Recording object
```

---

## 8. Deployment Architecture

### Current (Prototype)

- SDK: `pip install -e ".[sim]"` from local clone
- Web: `python web/app.py` on localhost
- Pipeline: CLI invocation
- AI Tutor: requires `ANTHROPIC_API_KEY` env var

### Production (Planned)

```
                    +-------------------+
                    |   CDN (Vercel)    |
                    |   Next.js SSR     |
                    +--------+----------+
                             |
                    +--------v----------+
                    |   API Gateway     |
                    |   (Vercel/AWS)    |
                    +--------+----------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+   +-------v-------+   +-------v-------+
| Meshy Worker  |   | Auth + Payment|   | Tutor API     |
| (async queue) |   | (Stripe/Clerk)|   | (Claude API)  |
+-------+-------+   +---------------+   +---------------+
        |
+-------v-------+
| Shell Pipeline |
| (compute node) |
+-------+-------+
        |
+-------v-------+
| Order + Print  |
| Queue (DB)     |
+----------------+
```

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `HAWABOT_MOCK` | Force simulation mode (default: "1") | No |
| `ANTHROPIC_API_KEY` | Claude API for AI tutor | For tutor features |
| `MESHY_API_KEY` | Meshy API for 3D generation | For design platform |

---

## 9. Technology Stack Summary

| Layer | Technology | Status |
|-------|-----------|--------|
| SDK Core | Python 3.10+, PyYAML, Pydantic | Built |
| SDK Simulation | matplotlib | Built |
| Shell Pipeline | trimesh, manifold3d, scipy, numpy | Built |
| Joint Cuts | trimesh, manifold3d | Built |
| Web Prototype | Flask, Three.js, Jinja2 | Built |
| AI Tutor | Anthropic Claude API (Haiku + Sonnet) | Scaffolded |
| Curriculum | YAML mission definitions + Python validation | Scaffolded |
| PicoDriver (Spark) | pyserial, MicroPython PWM firmware | Built |
| Pi5Driver (Core/Pro) | Pi 5 UART/TTL for smart servos | Scaffolded |
| Production Web | Next.js, React, Three.js Fiber | Planned |
| Payment | Stripe | Planned |
| Auth | Clerk or Auth0 | Planned |
| Database | PostgreSQL | Planned |
| Hosting | Vercel + AWS Lambda | Planned |
