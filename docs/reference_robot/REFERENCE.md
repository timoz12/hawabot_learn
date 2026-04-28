# Hawabot — Reference Document for the Mini Educational Robot Program

This folder is a self-contained snapshot of the **Hawabot** project, a custom humanoid being built solo by Dean (timoz12). It is intended as a reference for designing a smaller, simpler educational robot for teenagers — what to keep, what to simplify, and the engineering lessons learned along the way.

**Snapshot date**: 2026-04-27
**Status**: Hardware fully assembled, software in active development. Stand-up reliable with assist; closed-loop balance and walking are next.

---

## Files in this folder

| File | What it is | Use it for |
|---|---|---|
| `REFERENCE.md` | This document | High-level overview |
| `robot_description.json` | Custom Hawabot dimensions + masses (torso, head, simplifications vs Poppy) | Component sizing reference |
| `servo_mapping.json` | All 20 servo IDs → joint names, Dynamixel models, masses, stall torques | Servo selection and joint layout |
| `dynamixel_limits.json` | Per-servo position limits (calibrated min/max), groups (upper/lower bus) | Safety bounds |
| `standing_pose.json` | Calibrated standing pose — joint position targets for all 20 servos | Working pose example |
| `Poppy_Humanoid.URDF` | Full Poppy Humanoid URDF (legs + arms inherited unchanged) | Link lengths, masses, inertias, collision meshes |
| `poppy_humanoid.json` | Poppy Humanoid metadata (joint definitions, limits) | Joint convention reference |

**Coordinate convention everywhere: ROS FLU** — `+X forward, +Y left, +Z up`.
Poppy joint axis suffixes: `_x` = roll, `_y` = pitch, `_z` = yaw.

---

## What Hawabot is

| Property | Value |
|---|---|
| Form factor | Bipedal humanoid |
| Standing height | 913 mm (≈ 3 ft) |
| Mass (current estimate) | 3–4 kg (will be measured precisely tomorrow) |
| Degrees of freedom | 20 (10 leg + 8 arm + 1 waist + 1 head) |
| Mechanical base | Poppy Humanoid (Inria), simplified torso/head |
| Smart servos | 20× Dynamixel X-series (mix of XH/XM 540 + 430 classes) |
| IMU | HWT906 9-DOF (chest, ROS-FLU calibrated) |
| Cameras | Intel RealSense D455 (depth) + Livox MID360 (lidar) |
| Compute | 2× NVIDIA Jetson Thor (brain + actuation, dual ROS 2 nodes) |
| Bus | 2× U2D2 USB-TTL adapters @ 1 Mbps, daisy-chain protocol 2.0 |

### Simplifications vs. stock Poppy
Poppy has 25 DOF; Hawabot has 20. The legs and arms are mechanically identical to Poppy (we use Poppy's URDF directly). The simplifications are:
- **Torso**: 1 servo (`abs_z` waist yaw only) instead of Poppy's 5 (`abs_y/x/z`, `bust_y/x`)
- **Head**: 1 servo (`head_z` yaw only) instead of Poppy's 2 (`head_z`, `head_y`)
- This removes 5 DOF but keeps the locomotion-critical legs unchanged. Tradeoff: less expressive upper body, easier control, lighter, cheaper.

### Why Poppy?
Open-source URDF, well-documented kinematics, large user community, parts available, mechanically printable on a desktop FDM printer. The full URDF (`Poppy_Humanoid.URDF`) is the source of truth for leg/arm link lengths, masses, and inertias.

---

## Hardware breakdown

### Servos (20 total) — see `servo_mapping.json`
**Two classes used:**

| Class | Models | Mass | Stall torque | No-load speed | Where used |
|---|---|---|---|---|---|
| **Large (165 g)** | XH/XM 540-W150, W270 | 165 g | 7.3–10.6 Nm | 33–60 rpm | Legs (gravity load) + waist + ankle/knee/hip |
| **Small (82 g)** | XH/XM 430-W210, W350 | 82 g | 3.0–4.1 Nm | 46–77 rpm | Arms + head + hip yaw |

**Key Dynamixel features used:**
- Operating mode 3 (position control, default)
- Operating mode 5 (current-based position — torque-limited, "compliant")
- Goal Current cap (RAM register 102) — clips PWM so the servo gives up gracefully under overload instead of tripping HW error 0x20
- Built-in current/temperature/HW-error registers for every servo
- GroupSyncWrite / GroupSyncRead for atomic per-bus broadcast

### Bus topology
- **Upper bus** (`/dev/ttyDXL_upper`): IDs 11–18 (arms), 30 (head) — 9 servos
- **Lower bus** (`/dev/ttyDXL_lower`): IDs 1–10 (legs), 22 (waist) — 11 servos
- Stable symlinks via udev rule (`99-u2d2.rules`) keyed on FTDI serial numbers
- USB latency_timer set to 1 ms (default 16 ms) for fast register reads — critical for >50 Hz control loops

### IMU: HWT906
- 9-DOF (gyro + accel + mag), 100 Hz, USB-CDC binary protocol
- Calibrated axes to robot frame (FLU)
- Used for pitch/roll feedback during balance
- Cheap (~$50) and reliable

### Compute (Dual Jetson Thor)
- **Thor 1 (brain)**: LLM, perception, high-level planning
- **Thor 2 (sensors/actuation)**: real-time IMU + servo control loops
- ROS 2 over Cyclone DDS, Ethernet between nodes
- Power: 12 V rail to servos, separate 5 V to Jetsons, battery in backpack (planned)

### Mechanical structure
- Aluminum extrusion central column for torso
- 3D-printed shells (head ≈ 500 g, torso shells ≈ 200 g estimated)
- Poppy printed components for legs/arms

---

## Software architecture

### Repository layout (key directories)
```
~/dynamixel_setup/         servo control scripts, poses, limits, motions
~/balance/                 IMU-based balance controller + logs
~/imu/                     HWT906 reader, calibration, udev rules
~/ros2_ws/src/             main ROS 2 workspace
~/llm_ws/src/              LLM integration workspace
~/perception_yolo/ros2_ws/ perception pipeline
~/robotics paratmeters/    robot_description.json, servo_mapping.json, Poppy URDF
```

### Key scripts (Python, no compilation)
| Script | Purpose |
|---|---|
| `move_to_standing.py` | Synchronized stand-up via GroupSyncWrite + smoothstep waypoints. Reaches ~80% before ankle saturates. |
| `move_to_standing_v3_mode5.py` | Same + ankle Mode 5 compliance. Reliable stand-up with operator assist. |
| `teach_and_play.py` | Kinesthetic teach-by-demo. Records joint positions while operator moves the robot, plays them back. |
| `teach_compliant_stand.py` | Extended teach-by-demo with all-leg Mode 5 follower (in development). |
| `calibrate_leg_holding_current.py` | Measures per-joint holding current, finds Goal Current sweet spot per joint. |
| `phase_a_dry_run.py` | Open-loop balance controller (100 Hz IMU read, computes deltas, no servo writes yet). |
| `setup_ftdi_latency.sh` | Sets USB latency_timer=1 ms for fast servo reads. |

### Control patterns (all proven)
1. **Position mode (default)**: write `goal_position`, servo tracks with PD loop, full torque available.
2. **Current-based position (mode 5)**: same tracking but PWM clipped at `goal_current` cap. Servo can't trip HW overload — just gives up residual position error.
3. **Synchronized waypoint interpolation**: smoothstep-eased trajectory broadcast as a stream of `goal_position` updates via GroupSyncWrite. All servos on a bus advance in lockstep.
4. **Follower mode (compliant teaching)**: at 50 Hz, write `goal_position = present_position` for joints in mode 5 with low Goal Current. Joint stays where the operator's hand puts it.

---

## What's been built

### Milestones complete (chronological)
1. **IMU integration** — HWT906 streaming at 100 Hz, axes calibrated to robot frame
2. **Servo identity + calibration** — all 20 servos enumerated, position limits calibrated and stored in `dynamixel_limits.json`, joint names mapped to Poppy convention
3. **Standing pose** — captured manually + saved to `standing_pose.json`
4. **First stand-up** — `move_to_standing.py` with synchronized waypoint interpolation
5. **Ankle saturation diagnosed + solved** — Mode 5 compliance via `move_to_standing_v3_mode5.py`. No more HW 0x20 trips.
6. **Teach-by-demo** — `teach_and_play.py`. First motion recorded: a wave (right arm, 15 s).
7. **Phase A balance dry-run** — open-loop IMU reader at 100 Hz, sign math verified.

### Verified control achievements
- **Mode 5 compliance works under real load**: ankle current capped at 837 units / 1000 cap, residual position error 3.87° / 4.22° (matches Disney Olaf paper's reported standing tracking error of 3.87°)
- **Reliable stand-up with operator assist** — no hardware faults, repeatable
- **Standing pose is self-stable** — once the robot reaches standing, it holds without help. Failure mode is *only* during the rising transient.

---

## What's planned

### Near-term (Stand-up + balance)
1. **FTDI latency fix** — drop register-read time from 16 ms to 1 ms. Brings v3 stand-up from 33 s back to 6 s.
2. **Compliant-leg teach demo (Option C)** — record a stand-up with all leg joints back-drivable, then play back
3. **v4 phased stand-up (Option B)** — hand-engineered Schenkman-style trunk-lean-before-leg-drive trajectory (alternative to C)
4. **Closed-loop balance**:
   - Phase B: pitch-only PID via `ankle_y`
   - Phase C: add roll via `hip_x`
   - Phase D: multi-joint pitch (hip_y + knee_y)
5. **Freestanding test off harness** — only after Phase D is reliable

### Long-term (Walking + AI)
1. **Animation-reference RL imitation** — Disney Olaf-style PPO policy in Isaac Sim that imitates a recorded demo, with thermal CBF, joint-limit CBF, and impact-reduction rewards. Path from teach-by-demo → robust walking.
2. **Two-policy split** — separate standing and walking policies, conditioned on a high-level command (path-frame velocity, pose target, etc.)
3. **Perception integration** — YOLO on RealSense + lidar SLAM, fused into a world model on Thor 1
4. **LLM brain** — Thor 1 hosts an LLM that takes natural language commands, decomposes them into motion library calls (`wave`, `walk-to-X`, `look-at-Y`)

---

## Key engineering decisions and lessons (most relevant for the mini version)

### 1. Geometric problems vs. force problems
**Lesson**: When a servo overloads, ask first whether it's a *placement* problem before raising current limits.
- **Story**: Hawabot's ankle was tripping HW overload at mid-extension during stand-up. We measured peak current = 837 units (~2.25 A) — well under the servo's 4.4 A stall.
- The actual problem (per Schenkman 1990 sit-to-stand biomechanics): the CoM hadn't moved over the feet yet when the legs pushed. Geometry, not torque.
- Yoshioka 2009: minimum ankle torque for sit-to-stand is ~0.3 Nm/kg. Hawabot at 3–4 kg needs ~1 Nm/ankle. Our XM540-W150 stall is 7.3 Nm. We have **7× headroom** — the servo isn't the bottleneck.
- **Mini-version takeaway**: teach kids to debug *behavior*, not just specs. A small-error overload often reveals a kinematic mistake.

### 2. Compliance via current-based position (Mode 5)
**Lesson**: Smart servos can be made "soft" without losing position tracking.
- Set Goal Current low → servo tries to track goal but caps PWM. If load exceeds the cap, position error grows but the servo doesn't fault.
- Used for two purposes: (a) safe stand-up (ankle gives up gracefully), (b) compliant teach-by-demo (operator can move the joint by hand because it can't push hard).
- **Mini-version takeaway**: any mid-tier smart servo (Dynamixel, Feetech STS, etc.) supports this. It's a *killer feature* for educational robots — same hardware does both "drive accurately" and "be moved by the kid."

### 3. The animation-reference paradigm (Disney Olaf, Dec 2025)
**Lesson**: Demonstrate the motion, don't design it.
- Hand-designing trajectories (Schenkman phases, min-jerk per joint, etc.) is hard and brittle. The artist authors a kinematic motion, then RL trains a policy that imitates it under physics.
- Hawabot's `teach_and_play.py` is the front-end of this: each recording is an "animation reference."
- **Mini-version takeaway**: kinesthetic teaching is the most direct, intuitive interface for kids. They move the robot; it remembers; it plays back. Then you can layer "smarter playback" (smoothing, scaling, conditioning on context) on top — without ever forcing them to write trajectory math.

### 4. Synchronized writes matter
**Lesson**: When you have N joints driving a coordinated motion, they must all step in lockstep.
- Early Hawabot stand-ups failed because each servo received its `goal_position` at a slightly different time. Strong servos overshot; weak servos got stuck holding partial-pose load alone.
- Fix: GroupSyncWrite — one packet per bus broadcasts goal_position to all servos. Atomic on that bus.
- **Mini-version takeaway**: any multi-DOF educational robot needs sync writes. Most servo SDKs (Dynamixel, microROS, even Arduino libraries) support it.

### 5. USB-TTL latency is a silent bottleneck
**Lesson**: Default FTDI latency is 16 ms, which kills high-rate sensor loops.
- Reading 4 registers × 20 servos = 80 reads × 16 ms = ~1.3 s per status poll on Hawabot
- Setting `latency_timer=1` via udev → ~80 ms per poll, 16× faster
- **Mini-version takeaway**: kids' robots will hit this too. Bake it into the boot/setup script; don't expect them to know.

### 6. Standing pose vs. rising transient
**Lesson**: A stable static pose is much easier than a stable transition.
- Once Hawabot is standing, it holds itself without help. The challenge is the *rising motion* — dynamic CoM placement, momentum transfer, ankle/knee coordination.
- **Mini-version takeaway**: don't promise teenagers a "walking robot" on day one. Promise an *expressive* robot (waves, gestures, headlooks, balance demos) and let walking be the optional graduate-level capstone.

---

## Designing a mini educational version — recommendations

### Form factor options (in order of cost/complexity)
1. **Tabletop articulated companion** (cheapest, easiest) — 4–6 servos, 2 arms + base + head, no legs. Like an InMoov bust on a desk. Total mass ~1 kg, runs on a USB power supply.
2. **Wheeled mobile humanoid** — 4–6 servos for arms/head + 2 wheels for mobility. Avoids bipedal balance entirely.
3. **Self-balancing two-wheeled "humanoid"** — 4–6 arm/head servos + Segway-style two-wheel base with IMU PID. Teaches closed-loop balance without bipedal complexity.
4. **Bipedal mini** (hardest) — 12–14 servos, 50 cm tall, ~1.5 kg. This is real engineering for teenagers; expect 6–12 months of work.

I'd recommend **option 1 or 2 for a first product**, with option 3 as an "advanced track."

### What to keep from Hawabot
| Feature | Why teenagers benefit |
|---|---|
| **Smart servos with current/temp/position feedback** | Teaches closed-loop control, debugging, hardware safety |
| **Open mechanical design (visible joints)** | Kids can see the robot work, intuit the kinematics |
| **Teach-by-demo workflow** | Immediate feedback loop, no math required to start |
| **Per-servo soft limits + watchdog** | Defensive programming as a habit |
| **IMU as a "tilt sense"** | Concrete intro to sensor fusion |
| **LLM-as-brain via API** | The exciting AI part, no GPU needed |
| **Python-only stack** | Lowest barrier to entry |

### What to simplify or drop
| Feature | Why drop |
|---|---|
| **ROS 2** | Steep learning curve; Python + simple message bus is plenty for a teenager |
| **Dual-Jetson architecture** | One Raspberry Pi 5 / Jetson Nano is fine |
| **Lidar + depth camera** | One USB webcam + YOLO via cloud API teaches the same lessons cheaper |
| **Custom kernel modules / udev / RT-Linux** | Use plug-and-play USB; pre-flash an SD card |
| **Bipedal walking** | Save for "advanced module"; not needed to teach AI-on-robot |
| **Battery + power management** | Wall-powered for a workshop kit avoids fire risk |
| **Force-torque sensors** | Use servo current as the "force" signal — already built in |

### Cost trajectory (rough)
| Component | Hawabot | Mini target |
|---|---|---|
| Servos | $2,800 (20 × $140 avg) | $300 (6 × $50, e.g., Feetech STS3215 / lower-end Dynamixel) |
| Compute | $4,000 (2× Jetson Thor) | $80 (RPi 5) |
| Sensors | $1,500 (D455 + Livox + IMU) | $30 (USB webcam + cheap IMU) |
| Frame + 3D prints | $200 | $40 |
| Power | $300 (battery + regulators) | $20 (wall PSU) |
| **Total** | **~$8,800** | **~$470** |

### Pedagogical structure (suggested 8-week curriculum)
1. **Week 1**: Servo basics — ID, position, torque. Move one joint, read its state.
2. **Week 2**: Multi-servo coordination — sync writes, smoothstep trajectories.
3. **Week 3**: Soft limits, current monitoring, watchdogs — defensive coding.
4. **Week 4**: IMU + tilt — intro to sensors, gravity, axis conventions.
5. **Week 5**: Teach-by-demo — record a wave, play it back. Mode 5 compliance.
6. **Week 6**: Closed-loop control — wobble platform PID balance demo.
7. **Week 7**: AI integration — LLM API takes "say hello and wave" → executes recorded motions.
8. **Week 8**: Capstone — kids design and demo their own robot behavior.

### Hard things to avoid for safety / pedagogy
- Hot servos (high stall current → burn risk). Use lower-spec servos with thermal limits.
- Heavy parts that can fall. Keep mass <1.5 kg.
- Pinch points in joint envelopes. Add hard mechanical stops.
- "Magic" abstractions — kids should be able to read every line of code that moves the robot.

---

## How to use this folder in another chat

1. Drop `REFERENCE.md` (this file) plus the JSON/URDF files into the chat as attachments or paste them.
2. Ask the chat to:
   - Propose a 6-DOF tabletop variant based on this design
   - Estimate a BOM cost for a target price point
   - Generate a curriculum that builds toward Hawabot's capabilities at a teenager's pace
   - Adapt specific Hawabot scripts (e.g., `teach_and_play.py`) for a smaller bus + servo class
3. The Poppy URDF is the most mechanically detailed file (29 KB) — useful for any "how big should the joints be" question.
4. The `servo_mapping.json` has the most reusable spec data: every Dynamixel model used, with masses and stall torques. Good for answering "which class of servo for joint X."

---

## Contact / source of truth
This snapshot is a *point-in-time* description. Active development happens in `~/dynamixel_setup/`, `~/balance/`, and the ROS 2 workspaces in `~/`. The GitHub repo is `timoz12/hawabot` (private).

For an exact reproduction or follow-up questions, the original project lead is Dean (timoz12).
