# HawaBot — Next Tasks

**Last updated:** 2026-04-29

---

## In Progress

### 1. SolidWorks Parametric Skeleton Build
**Owner:** Tim
**Status:** Starting — reviewing generated STEP file
**Guide:** `pipeline/SOLIDWORKS_BUILD_GUIDE.md`

- [ ] Import `spark_skeleton_frame.step` into SolidWorks
- [ ] Verify servo pockets, magnet holes, wire channels via section views
- [ ] Download real servo STEPs (SG90, MG90S) from GrabCAD
- [ ] Download Pi Pico W STEP from raspberrypi.com
- [ ] Rebuild frame parametrically using `equations.txt` global variables
- [ ] Create assembly with real servo + Pico STEP files
- [ ] Run interference check
- [ ] Export final frame STL for printing

---

## Upcoming (Ordered)

### 2. Shell Pipeline End-to-End Test
**Blocked by:** Need a test character mesh (STL/OBJ)
**Effort:** ~2 hours

- [ ] Generate or download a test character mesh (e.g., Naruto figurine STL from Printables)
- [ ] Run full pipeline: `python -m pipeline.shell_pipeline test_character.stl output/`
- [ ] Verify all 5 zone shells are produced
- [ ] Inspect shell quality (wall thickness, magnet bosses, openings)
- [ ] Fix any issues found
- [ ] Add unit tests for each pipeline module

### 3. 3D Generation API Integration
**Effort:** ~1 day

- [ ] Set up Tripo3D API account and get API key
- [ ] Write `pipeline/generate_3d.py` — wrapper for Tripo3D image-to-3D API
- [ ] Handle response → download mesh → feed into shell pipeline
- [ ] Add Meshy API as fallback option
- [ ] Test with sample character images
- [ ] Measure quality + cost per generation

### 4. Pricing & Business Logic
**Effort:** ~1 day

- [ ] Define cost structure:
  - Skeleton kit (BOM cost + margin)
  - 3D generation compute cost per character
  - 3D printing cost per shell set (material + time + shipping)
  - AI tutor subscription pricing
- [ ] Build pricing calculator (given character complexity → total price)
- [ ] Define tier packaging (what's included at each price point)
- [ ] Document in `docs/PRICING.md`

### 5. Web App — 3D Preview Viewer
**Effort:** ~2 days
**Reference:** Printables.com-style dark viewer (see memory)

- [ ] Rebuild `web/` with new workflow (design → preview → purchase → shells)
- [ ] Three.js STL viewer with dark background
- [ ] Top-left orbit/pan/zoom controls
- [ ] Cut plane visualization (colored lines on model)
- [ ] Cut plane adjustment sliders
- [ ] Exploded view of 5 zones
- [ ] Before/after: solid character → shell pieces on skeleton

### 6. Web App — Customer Flow
**Effort:** ~3 days

- [ ] Photo upload / text prompt input
- [ ] 2D reference view generation (cheap — 4 views)
- [ ] Character confirmation screen
- [ ] Purchase flow (Stripe integration)
- [ ] Guided dissection walkthrough (step through each cut)
- [ ] Order status tracking

### 7. AI Tutor — Curriculum Design
**Effort:** ~1 week

- [ ] Define learning objectives per age group
- [ ] Design lesson sequence (move servos → sequences → sensors → logic)
- [ ] Write lesson content / prompts
- [ ] Define exercise types (code challenges, creative projects)
- [ ] Map to HawaBot SDK API (which methods for which lessons)

### 8. AI Tutor — Implementation
**Effort:** ~1 week
**Blocked by:** Curriculum design

- [ ] Design tutor agent architecture (Claude Haiku for speed, Sonnet for complex help)
- [ ] Build `hawabot/tutor/` module
- [ ] Context-aware help (knows which lesson, which robot, what code they wrote)
- [ ] Code validation (check student code before running on robot)
- [ ] Progressive hints (don't give answer immediately)
- [ ] Safety guardrails (prevent harmful servo commands)

### 9. Physical Prototype
**Blocked by:** SolidWorks skeleton finalized

- [ ] 3D print skeleton frame
- [ ] Install servos, Pico W, magnets
- [ ] Flash firmware
- [ ] Test SDK connectivity + servo control
- [ ] Generate and print a test character shell set
- [ ] Validate magnet snap-on fit
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

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-28 | 200mm skeleton height | SG90s need room; 150mm too cramped |
| 2026-04-28 | Frame + magnetic shell model | Cleaner than boolean subtraction, swappable characters |
| 2026-04-28 | 40 magnet seats, software selects | Universal skeleton, per-character optimization |
| 2026-04-28 | Single-part frame (not sectioned) | Skeleton doesn't split; only shells do |
| 2026-04-29 | Tripo3D as primary 3D gen | Best value: $0.01/credit, <10s, guaranteed watertight |
| 2026-04-29 | Meshy as fallback | Better docs, good for fine detail |
| 2026-04-29 | Spark tier only for launch | Ship one thing well, expand later |
