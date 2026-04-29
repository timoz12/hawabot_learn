# HawaBot — Next Tasks

**Last updated:** 2026-04-29 (evening)

---

## Completed Recently

| Task | Status | Notes |
|---|---|---|
| Shell pipeline modules (dissect, hollow, magnets, validate) | **Done** | All modules implemented |
| Skeleton subtraction hollowing | **Done** | Replaces vertex-offset; all shells watertight |
| Torso clamshell split | **Done** | Front/back halves for removal |
| 3D gen API wrapper (Tripo3D + Meshy) | **Done** | `pipeline/generate_3d.py` |
| Pricing & business logic | **Done** | `docs/PRICING.md` — bundled model, no subscription |
| E2E pipeline test (Naruto mesh) | **Done** | 6 shells exported, all watertight |

---

## In Progress

### 1. SolidWorks Parametric Skeleton Build
**Owner:** Tim
**Status:** Building in SolidWorks
**Guide:** `pipeline/SOLIDWORKS_BUILD_GUIDE.md`

- [ ] Import `spark_skeleton_frame.step` into SolidWorks
- [ ] Verify servo pockets, magnet holes, wire channels via section views
- [ ] Download real servo STEPs (SG90, MG90S) from GrabCAD
- [ ] Download Pi Pico W STEP from raspberrypi.com
- [ ] Rebuild frame parametrically using `equations.txt` global variables
- [ ] Create assembly with real servo + Pico STEP files
- [ ] Run interference check
- [ ] Export final frame STL for printing
- [ ] **Re-run pipeline** with finalized skeleton geometry

---

## Upcoming (Ordered)

### 2. Pipeline Tuning
**Blocked by:** Finalized SolidWorks skeleton
**Effort:** ~1 day

- [ ] Update `skeleton.py` clearance volumes to match final SolidWorks geometry
- [ ] Tune magnet selection algorithm (currently too conservative on thin shells)
- [ ] Add auto-thickening for thin wall regions (customer confirmation step)
- [ ] Test with a proper **T-pose character mesh** (Naruto was hands-in-pockets)
- [ ] Add T-pose enforcement to `generate_3d.py` via prompt injection
- [ ] Add T-pose detection to `dissect.py` (validate arm zones > 15mm width)

### 3. T-Pose Enforcement in 3D Generation
**Effort:** ~half day

- [ ] Add T-pose pre-prompt to `generate_3d.py` for text-to-3D calls
- [ ] For image-to-3D: detect if source is T-pose, regenerate reference views if not
- [ ] Add arm-spread validation in `dissect.py` (sanity check before cutting)
- [ ] Document T-pose requirement in `SHELL_PIPELINE_SPEC.md`

### 4. Web App — 3D Preview Viewer
**Effort:** ~2 days
**Reference:** Printables.com-style dark viewer (see memory)

- [ ] Rebuild `web/` with new workflow (design → preview → purchase → shells)
- [ ] Three.js STL viewer with dark background
- [ ] Top-left orbit/pan/zoom controls
- [ ] Cut plane visualization (colored lines on model)
- [ ] Cut plane adjustment sliders
- [ ] Exploded view of 6 zones (torso = 2 pieces)
- [ ] Before/after: solid character → shell pieces on skeleton

### 5. Web App — Customer Flow
**Effort:** ~3 days

- [ ] Photo upload / text prompt input
- [ ] 2D reference view generation (cheap — 4 views)
- [ ] T-pose regeneration step (if needed)
- [ ] Character confirmation screen
- [ ] Purchase flow (Stripe integration)
- [ ] Guided dissection walkthrough (step through each cut)
- [ ] Order status tracking

### 6. Credit Store & Skill Packs
**Effort:** ~2 days

- [ ] Design credit pack UI (browse by character, preview before buying)
- [ ] Implement credit balance system (purchase, consume, track)
- [ ] Movement pack format (servo keyframes + timing)
- [ ] AI-generated custom animations (text prompt → movement sequence)
- [ ] Character-specific skill packs (tied to character design)
- [ ] Voice types (Core/Pro tier only — requires speaker hardware)
- [ ] Credit consumption tracking + low-balance alerts

### 7. AI Tutor — Curriculum Design
**Effort:** ~1 week

- [ ] Define learning objectives per age group
- [ ] Design lesson sequence (move servos → sequences → sensors → logic)
- [ ] Write lesson content / prompts
- [ ] Define exercise types (code challenges, creative projects)
- [ ] Map to HawaBot SDK API (which methods for which lessons)
- [ ] Character-specific lesson content (unlocked per character purchase)

### 8. AI Tutor — Implementation
**Effort:** ~1 week
**Blocked by:** Curriculum design

- [ ] Design tutor agent architecture (Claude Haiku for speed, Sonnet for complex help)
- [ ] Build `hawabot/tutor/` module
- [ ] Context-aware help (knows which lesson, which robot, what code they wrote)
- [ ] Code validation (check student code before running on robot)
- [ ] Progressive hints (don't give answer immediately)
- [ ] Safety guardrails (prevent harmful servo commands)
- [ ] Credit consumption per interaction

### 9. Physical Prototype
**Blocked by:** SolidWorks skeleton finalized

- [ ] 3D print skeleton frame
- [ ] Install servos, Pico W, magnets
- [ ] Flash firmware
- [ ] Test SDK connectivity + servo control
- [ ] Generate T-pose test character via Tripo3D API
- [ ] Print shell set, validate magnet snap-on fit
- [ ] Full demo: code robot, snap on character, show off

---

## Future / Backlog

| Task | Notes |
|---|---|
| Stumpy skeleton variant | For dragons, animals — different proportions |
| Core tier skeleton | STS3215 servos, elbows, Pi 5, 250mm |
| Sensor add-ons | Ultrasonic, touch, light sensors |
| Mobile app | Companion app for robot control |
| Classroom mode | Teacher dashboard, class management |
| Print farm integration | Auto-submit STLs to print service API |
| Character marketplace | Community-shared character designs |
| Multi-robot coordination | Pro tier — robots interact with each other |

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-28 | 200mm skeleton height | SG90s need room; 150mm too cramped |
| 2026-04-28 | Frame + magnetic shell model | Cleaner than boolean subtraction of shells, swappable characters |
| 2026-04-28 | 40 magnet seats, software selects | Universal skeleton, per-character optimization |
| 2026-04-28 | Single-part frame (not sectioned) | Skeleton doesn't split; only shells do |
| 2026-04-29 | Skeleton subtraction for hollowing | Exact fit, watertight results; vertex-offset was fragile |
| 2026-04-29 | Torso clamshell (front/back split) | Can't slide over shoulder brackets as one piece |
| 2026-04-29 | Draft taper on all shells | Easy removal — 1.5-2° taper along removal direction |
| 2026-04-29 | T-pose standard for all character models | Clean arm zone separation; enforced via pre-prompts |
| 2026-04-29 | Tripo3D as primary 3D gen | Best value: $0.01/credit, <10s, guaranteed watertight |
| 2026-04-29 | Bundled pricing, no separate AI subscription | Kit = 6mo tutor; characters extend +6mo; credits for extras |
| 2026-04-29 | Credits = Fortnite-style add-ons | Movement packs, voice types, animations — not just tutoring |
| 2026-04-29 | Voice types gated to Core/Pro tier | Requires speaker hardware not in Spark |
