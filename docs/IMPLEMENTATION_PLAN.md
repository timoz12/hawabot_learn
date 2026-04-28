# HawaBot Implementation Plan

## Current State Assessment

### What Is Built (Working Code)

| Component | Path | Status | Notes |
|-----------|------|--------|-------|
| SDK core (`Robot` class) | `hawabot/robot.py` | Functional | Entry point, tier detection, body parts, teach-by-demo |
| Character profile system | `hawabot/character/` | Functional | YAML profiles, animations, expressions |
| Joint abstractions | `hawabot/joints/` | Functional | Head, Arms, Waist, Leg modules |
| Driver abstraction | `hawabot/drivers/` | Functional (mock) | MockDriver complete; Pico/Pi5 scaffolded |
| Simulation engine | `hawabot/sim/` | Functional | Joint state tracking, matplotlib visualizer |
| Tier config | `hawabot/config/tiers.py` | Functional | Spark/Core/Pro definitions, joint specs |
| Shell pipeline | `pipeline/shell_pipeline.py` | Functional | Scale, subtract, trim, validate — tested on real meshes |
| Joint clearance cuts | `pipeline/joint_cuts.py` | Functional | Clearance volumes, section splitting |
| Skeleton builder | `pipeline/skeleton.py` | Functional | Parametric skeleton generation per tier |
| Web prototype | `web/app.py` | Functional | Flask + Three.js, Meshy API integration, pipeline integration |
| Curriculum structure | `missions/` | Scaffolded | 5-month directory structure, month_01 prompts started |
| AI tutor | `hawabot/tutor/` | Scaffolded | Module structure in place, prompts directory |
| Teach-by-demo | `hawabot/teach.py` | Functional | Record/playback with JSON serialization |

### What Remains

| Component | Priority | Effort | Dependency |
|-----------|----------|--------|------------|
| Hardware drivers (Pico, Pi5) | P0 | 3-4 weeks | Physical hardware in hand |
| AI tutor implementation | P0 | 2-3 weeks | Anthropic API key, prompt engineering |
| Curriculum content (25 missions) | P0 | 6-8 weeks | SDK stable, tutor working |
| Production web platform | P1 | 8-12 weeks | Design finalized, Stripe integration |
| Skeleton physical prototyping | P0 | 4-6 weeks | 3D printer, servo stock |
| Assembly instructions | P1 | 2 weeks | Physical prototype complete |
| COPPA compliance review | P0 | 2-4 weeks | Legal counsel |
| Payment + fulfillment system | P1 | 4-6 weeks | Web platform, Stripe |
| Core tier skeleton + drivers | P2 | 4-6 weeks | Spark shipped, STS3215 servos |
| Pro tier skeleton + drivers | P3 | 6-8 weeks | Core validated, Dynamixel servos |

---

## Phased Build Plan

### Phase 0: Foundation (Weeks 1-4) -- IN PROGRESS

**Goal:** Validate the full pipeline end-to-end with a physical Spark prototype.

| Task | Owner | Duration | Status |
|------|-------|----------|--------|
| Order Spark hardware (5x SG90/MG90S, Pi Pico W, sensors) | Hardware | Week 1 | TODO |
| 3D print first skeleton from `pipeline/skeleton.py` output | Hardware | Week 1-2 | TODO |
| Implement PicoDriver (serial protocol for PWM servos) | Firmware | Week 1-3 | Scaffolded |
| Test SDK -> PicoDriver -> physical servo movement | Integration | Week 3 | TODO |
| Print first character shell using pipeline output | Pipeline | Week 2-3 | Pipeline proven on meshes |
| Validate shell fits skeleton, magnets hold, joints clear | Hardware | Week 3-4 | TODO |
| Film first "kid unboxes and builds" prototype session | Validation | Week 4 | TODO |

**Critical path:** Physical hardware must be in hand by Week 1. PicoDriver must work by Week 3. First assembled robot by Week 4.

**Exit criteria:**
- [ ] Physical Spark robot assembled and working
- [ ] SDK controls real servos via PicoDriver
- [ ] Character shell fits and sections snap together
- [ ] At least one complete teach/play cycle on real hardware

---

### Phase 1: Spark MVP (Weeks 5-12)

**Goal:** Shippable Spark product with curriculum, tutor, and purchase flow.

#### 1A: AI Tutor (Weeks 5-7)

| Task | Duration | Dependency |
|------|----------|------------|
| Implement safety layer (Claude Haiku pre-classifier) | 1 week | Anthropic API access |
| Implement tutor layer (Claude Sonnet, system prompt + context injection) | 1 week | Safety layer |
| Character-aware prompt templates (inject name, tier, current mission) | 3 days | Character profile system |
| Test with 5-10 representative student interactions | 1 week | Tutor working |
| COPPA compliance review with legal counsel | 2-4 weeks (parallel) | Tutor design finalized |

#### 1B: Curriculum Content (Weeks 5-10)

| Task | Duration | Dependency |
|------|----------|------------|
| Month 1 missions (5 missions): Joints, DOF, basic motion | 2 weeks | SDK stable |
| Month 2 missions (5 missions): Sensing, ultrasonic, reactions | 2 weeks | Month 1 complete |
| Tutor prompt files for each mission | 1 week per month | Missions written |
| Starter code templates for each mission | Parallel with missions | SDK API finalized |
| Mission validation logic (event log checks) | 1 week | Missions designed |
| Beta test with 3-5 kids (ages 12-15) | 2 weeks | Month 1-2 content ready |

#### 1C: Production Platform (Weeks 6-12)

| Task | Duration | Dependency |
|------|----------|------------|
| Design UI/UX for design platform (Figma) | 2 weeks | None |
| Next.js frontend: character design flow | 3 weeks | UI design |
| Three.js Fiber 3D viewer (interactive preview) | 2 weeks | Parallel with frontend |
| Stripe payment integration (one-time + subscription) | 1 week | Frontend |
| User accounts (Clerk/Auth0) | 1 week | Frontend |
| Meshy API production integration (rate limits, error handling, queue) | 1 week | API key + account |
| Order management + fulfillment queue | 2 weeks | Payment working |
| Deploy to Vercel + set up CI/CD | 1 week | All above |

#### 1D: Manufacturing Pipeline (Weeks 8-12)

| Task | Duration | Dependency |
|------|----------|------------|
| Source servos, sensors, Pico W in bulk (100-unit MOQ) | 2 weeks | Phase 0 validated |
| Design PCB carrier board (Pico W + servo headers + sensor connectors) | 3 weeks | Schematic finalized |
| Establish 3D print workflow (in-house Bambu Lab or partner) | 2 weeks | Shell pipeline proven |
| Design packaging (box, foam inserts, instruction card) | 2 weeks | Parallel |
| Assembly documentation (photo + video) | 1 week | Physical prototype |
| Assemble 10 beta kits | 1 week | All components in hand |
| Ship beta kits to testers | Week 12 | Kits assembled |

**Phase 1 exit criteria:**
- [ ] 10 beta kits shipped and tested by real kids
- [ ] AI tutor functional with safety layer passing COPPA review
- [ ] Month 1-2 curriculum complete and tested
- [ ] Production web platform deployed with payment flow
- [ ] Manufacturing process documented and repeatable

---

### Phase 2: Spark Launch + Core Development (Weeks 13-20)

**Goal:** Public Spark launch. Begin Core tier development.

#### 2A: Spark Public Launch (Weeks 13-15)

| Task | Duration | Dependency |
|------|----------|------------|
| Incorporate beta tester feedback | 1 week | Beta results |
| Fix critical bugs from beta | 1-2 weeks | Beta results |
| Launch landing page + purchase flow | 1 week | Platform ready |
| Launch marketing campaign (see GO_TO_MARKET.md) | Ongoing | Platform live |
| First 50 customer orders fulfilled | Weeks 14-15 | Launch |
| Customer support process established | Week 13 | Launch |

#### 2B: Core Tier Development (Weeks 13-20)

| Task | Duration | Dependency |
|------|----------|------------|
| Order Core hardware (STS3215 servos, Pi 5, mic, speaker, IMU) | Week 13 | Budget approved |
| Design Core skeleton (10 DOF, STS3215 mounting) | 3 weeks | Servos in hand |
| Implement Pi5Driver (UART/TTL bus for smart servos) | 3 weeks | Pi 5 + servos |
| Implement compliance mode for teach-by-demo on real hardware | 2 weeks | Pi5Driver working |
| Extend shell pipeline for Core skeleton | 1 week | Core skeleton designed |
| Month 3 curriculum: Feedback loops, IMU balance | 2 weeks | Core hardware working |
| Voice AI integration (microphone -> Claude -> speaker) | 2 weeks | Pi5Driver + mic |
| Core beta test (5 users) | 2 weeks | All above |

**Phase 2 exit criteria:**
- [ ] 50+ Spark kits sold and delivered
- [ ] Customer feedback incorporated, NPS measured
- [ ] Core tier prototype working end-to-end
- [ ] Month 3 curriculum written and tested
- [ ] Manufacturing process handling 20+ kits/week

---

### Phase 3: Core Launch + Pro Development (Weeks 21-30)

**Goal:** Core tier public launch. Begin Pro tier and B2B.

| Task | Duration |
|------|----------|
| Core public launch | Week 21 |
| Upgrade path tested (Spark customer -> Core, same character) | Week 21-22 |
| Pro skeleton design (21 DOF, Dynamixel) | Weeks 21-26 |
| Dynamixel driver implementation | Weeks 22-26 |
| Camera + computer vision integration | Weeks 24-28 |
| Month 4-5 curriculum | Weeks 23-28 |
| B2B pilot outreach (3-5 schools/camps) | Weeks 21-24 |
| Teacher dashboard (class management, progress tracking) | Weeks 25-30 |
| Pro beta test | Weeks 28-30 |

---

### Phase 4: Full Platform (Weeks 31-40)

**Goal:** All three tiers live. B2B channel active. Fundraise.

| Task | Duration |
|------|----------|
| Pro public launch | Week 31 |
| All 25 missions complete and tested | Week 32 |
| B2B pricing and contracts finalized | Week 31-33 |
| First school deployments (10-30 kit orders) | Week 33-36 |
| Character marketplace v1 (community sharing) | Week 34-38 |
| Fundraising materials prepared | Week 35-36 |
| Seed round conversations begin | Week 36+ |

---

## Dependency Graph

```
Phase 0: Physical Prototype
    |
    +---> PicoDriver works --------+
    |                              |
    +---> Shell fits skeleton -----+---> Phase 1: Spark MVP
                                   |
                      AI Tutor ----+
                      Curriculum --+
                      Web Platform +
                      Manufacturing+
                                   |
                                   +---> Phase 2: Spark Launch
                                   |         + Core Dev
                                   |
                                   +---> Phase 3: Core Launch
                                   |         + Pro Dev + B2B
                                   |
                                   +---> Phase 4: Full Platform
```

**Single biggest risk:** Physical prototype (Phase 0). If the shell does not fit the skeleton reliably, or the PicoDriver has latency issues, everything downstream is delayed. This is why Phase 0 is 4 weeks of focused hardware work before anything else.

---

## Milestones and Success Metrics

| Milestone | Target Date | Success Metric |
|-----------|-------------|----------------|
| First physical Spark robot assembled | Phase 0, Week 4 | Robot moves all 5 DOF via SDK |
| AI tutor passes COPPA review | Phase 1, Week 8 | Legal sign-off |
| 10 beta kits shipped | Phase 1, Week 12 | Kids complete Month 1 missions |
| Spark public launch | Phase 2, Week 13 | Platform live, accepting orders |
| 50 Spark kits sold | Phase 2, Week 16 | Revenue: ~$5,000 |
| 200 Spark kits sold | Phase 2, Week 20 | Revenue: ~$20,000 |
| Core tier launched | Phase 3, Week 21 | Core kits shipping |
| First B2B sale | Phase 3, Week 24 | School/camp pilot signed |
| 500 total kits sold | Phase 3, Week 28 | Validates product-market fit |
| All 3 tiers live | Phase 4, Week 31 | Full product line |
| 1,000 total kits sold | Phase 4, Week 36 | Seed round ready |

---

## Resource Requirements

### Team (Minimum Viable)

| Role | Responsibility | Phase Needed |
|------|---------------|--------------|
| Founder/Engineer | SDK, pipeline, architecture, everything | Phase 0+ |
| Firmware Engineer (part-time/contract) | PicoDriver, Pi5Driver, PCB design | Phase 0-2 |
| Curriculum Designer (part-time) | Mission content, pedagogy, beta testing | Phase 1+ |
| Frontend Developer (contract) | Next.js platform, Three.js viewer | Phase 1 |
| 3D Print Operator (part-time) | Shell printing, assembly, QA | Phase 1+ |

### Hardware Budget (Phase 0-1)

| Item | Quantity | Unit Cost | Total |
|------|----------|-----------|-------|
| SG90 servos | 50 | $1.50 | $75 |
| MG90S servos | 20 | $3.50 | $70 |
| Pi Pico W | 15 | $6 | $90 |
| HC-SR04 ultrasonic | 15 | $2 | $30 |
| Passive buzzer | 15 | $0.50 | $8 |
| PLA filament (5 rolls) | 5 | $20 | $100 |
| 3D printer (Bambu Lab A1 Mini) | 1 | $300 | $300 |
| Neodymium magnets (6x2mm, bulk) | 200 | $0.10 | $20 |
| PCB prototyping | 1 run | $150 | $150 |
| Misc (wires, connectors, tools) | - | - | $100 |
| **Total** | | | **~$943** |

### Software/Service Budget (Monthly)

| Service | Cost/Month | Notes |
|---------|-----------|-------|
| Anthropic API (Claude) | $50-200 | Scales with users; ~$0.15/student/month |
| Meshy API | $30-100 | ~$0.30/generation; batch pricing available |
| Vercel (hosting) | $20-50 | Pro plan for production |
| Domain + email | $15 | hawalabs.com |
| Stripe | 2.9% + $0.30/txn | Per transaction |
| **Total (pre-launch)** | **~$120/month** | |

---

## Technical Debt and Known Issues

| Issue | Severity | Plan |
|-------|----------|------|
| Web prototype is Flask, not production-ready | Medium | Rewrite to Next.js in Phase 1C |
| No automated tests for shell pipeline | Medium | Add pytest suite in Phase 1 |
| MockDriver does not simulate servo latency | Low | Add configurable delay in Phase 1 |
| Curriculum validation is basic (event log only) | Low | Sufficient for V1; enhance in Phase 3 |
| No CI/CD pipeline | Medium | GitHub Actions in Phase 1 |
| Character animations are hardcoded per profile | Low | Animation editor tool in Phase 3 |
| Shell pipeline does not handle non-manifold input gracefully | Medium | Add mesh repair stage with manifold3d.repair in Phase 1 |
