# HawaBot Strategic Plan

## Vision

Every kid should be able to bring their imagined robot to life — design it, build it, code it, and teach it. HawaBot is the platform that makes that possible.

## Mission

Hawa Labs builds the world's first character-driven physical AI robotics platform for kids aged 12-15. We combine custom 3D-printed robot characters, a progressive Python SDK, structured STEM curriculum, and an AI tutor to create the most engaging path from "I have an idea" to "I built a thinking robot."

---

## Market Opportunity

### Market Size

| Segment | Current Size | CAGR | Projected (2028) |
|---------|-------------|------|-------------------|
| Educational Robotics | $1.8-2.5B | 14-19% | $4.0-5.5B |
| AI in Education | $8.4B | 31% | $25B+ |
| 13-17 STEM Segment | Fastest-growing | 9.96% | Least served |

### Why Now

1. **LEGO Mindstorms discontinued.** SPIKE Prime retiring June 2026. The dominant educational robotics brand is vacating the advanced segment.
2. **AI fluency becoming mandatory.** Boston requires AI fluency for high school graduation starting September 2026. 28 US states have issued AI education guidance. Demand is exploding; supply is not.
3. **Generative AI is mature enough.** Text-to-3D (Meshy 6) and LLM tutoring (Claude) are production-ready. Two years ago this platform was impossible. Today the unit economics work.
4. **Python is the language of AI.** Every competitor still uses block-based visual programming or proprietary languages. The 12-15 demographic is ready for real code, and Python is the gateway to everything they will use in college and careers.

### Target Customer

**Primary (B2C):** Parents of kids aged 12-15 who are interested in STEM, coding, or robotics. Emotional purchase — "my kid designed their own robot and it showed up at our door." Average household income $80K+. Comfortable spending $99-499 on enrichment.

**Secondary (B2B):** Schools, after-school programs, summer camps, makerspaces. Longer sales cycle but higher LTV. Bulk pricing and teacher dashboards in Phase 2.

---

## Competitive Moat

### 1. The Shell Pipeline (Technical Moat)

The core technical differentiator: an automated pipeline that takes any AI-generated 3D mesh, subtracts a standard servo skeleton, and outputs slicer-ready printable shell sections.

- **Proven on real Meshy 6 output** — 500K+ face meshes, arbitrary topology
- **manifold3d** for boolean operations — watertight output guaranteed
- Pipeline: scale -> boolean subtract -> joint clearance cuts -> split into body sections -> validate
- All output sections are watertight and slicer-ready
- PLA material cost per shell: ~$0.60
- Processing time: seconds, not minutes
- **This is hard to replicate.** The intersection of computational geometry, 3D printing constraints, and servo skeleton fitting is a narrow domain. We have working code; competitors would need to build it from scratch.

### 2. Character Attachment (Emotional Moat)

Kids do not bond with generic robots. They bond with *their* robot. The character system — name it, design its appearance, give it expressions — creates an emotional connection that:

- Drives word-of-mouth ("look at my robot FireDrake!")
- Increases engagement with curriculum (missions reference the character by name)
- Creates switching costs (you cannot take your character to a competitor)
- Enables the subscription model (new modules for a character you already love)

### 3. AI-Native Pedagogy (Curriculum Moat)

AI concepts are woven into the curriculum from Month 1 ("What is a robot brain?"), not buried as an advanced topic. The AI tutor (Claude) uses Socratic method, references the student's specific robot and character, and adapts to their progress. No competitor has this.

### 4. Progressive Hardware (Platform Moat)

Three tiers (Spark, Core, Pro) share the same character shell — swap the skeleton internals, keep the character. This means:

- Low entry point ($99 Spark) de-risks the purchase
- Upgrade path is compelling: same beloved character, new capabilities
- Curriculum unlocks naturally with hardware tier

---

## Business Model

### Revenue Streams

| Stream | Description | Margin |
|--------|-------------|--------|
| Kit Sales (Full) | One-time purchase: shell + skeleton + SDK + curriculum access | 55-65% |
| Kit Sales (Subscription) | Monthly subscription over 5 months, new module each month | 60-70% |
| Shell Reprints | New character designs for existing skeletons | 80%+ |
| B2B Licensing | School/camp site licenses, bulk kits, teacher dashboard | 70%+ |
| Character Marketplace | Community-designed characters (future) | 90%+ |

### Pricing

| Tier | Full Kit Price | Monthly (5mo) | BOM Cost | Gross Margin (Full) |
|------|---------------|---------------|----------|---------------------|
| Spark | $99 | $25/mo ($125 total) | $69 | 30% |
| Core | $249 | $55/mo ($275 total) | $200 | 20% |
| Pro | $499 | $110/mo ($550 total) | $400 | 20% |

Note: Spark is the volume leader and loss-leader. At scale, BOM drops 15-25% through volume purchasing. Core and Pro margins improve significantly at 1,000+ unit runs.

### Unit Economics (Spark, at scale)

| Item | Cost |
|------|------|
| Servo kit (5x SG90/MG90S) | $12 |
| Pi Pico W | $6 |
| Ultrasonic sensor + buzzer | $4 |
| PLA shell (3D printed) | $0.60 |
| PCB + wiring + magnets | $8 |
| Packaging + shipping | $15 |
| Assembly labor | $10 |
| Meshy API (3D generation) | $0.30 |
| **Total COGS** | **~$56** |
| **Retail price** | **$99** |
| **Gross margin** | **43%** |

### Revenue Projection Framework

| Milestone | Monthly Revenue | Assumptions |
|-----------|----------------|-------------|
| Month 6 (post-launch) | $15K | 150 Spark kits/month, early adopters |
| Month 12 | $50K | Mix of tiers, 300 kits/month, 20% subscription |
| Month 18 | $150K | B2B pilot revenue begins, 600 kits/month |
| Month 24 | $400K | B2B at scale, 1,200 kits/month, reprints revenue |

These are conservative estimates assuming organic growth + targeted digital marketing. Subscription revenue compounds: by Month 12, recurring subscribers from previous months add $10-15K/month on top of new sales.

---

## Key Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| 3D printing does not scale | High | Partner with on-demand print farms (Shapeways, Xometry) for overflow. Long-term: in-house print farm with 20+ Bambu Lab printers. |
| Meshy API pricing/reliability | Medium | Shell pipeline is API-agnostic. Can swap to Tripo3D, OpenAI 3D, or other providers. Mesh input is a standard STL. |
| COPPA compliance complexity | High | No child data stored. Claude Haiku pre-classifier rejects PII. Legal review before launch. |
| Competitor copies character concept | Medium | 12-18 month head start on pipeline + curriculum. Network effects from character library. Patent shell pipeline process. |
| Hardware QA at scale | Medium | Spark tier uses commodity servos with known failure modes. Pre-assembly testing protocol. 30-day replacement warranty. |
| AI tutor produces wrong content | Low | Claude Sonnet with constrained system prompt + mission context. No open-ended generation. Haiku safety layer pre-classifies all inputs. |

---

## Strategic Priorities (Next 12 Months)

1. **Ship Spark MVP** — Complete SDK, finalize shell pipeline, launch design platform
2. **Validate B2C** — 500 paid customers in first 6 months
3. **Prove subscription** — 30%+ of customers choose monthly plan
4. **Core tier launch** — Month 4-5 post-Spark, validates upgrade path
5. **B2B pilot** — 3-5 schools/camps by Month 9
6. **Fundraise** — Seed round ($1.5-2.5M) at Month 6-9, armed with customer data

---

## Long-Term Vision (3-5 Years)

- **Year 1:** Spark + Core launch, 2,000+ customers, B2C validated
- **Year 2:** Pro launch, B2B at scale, character marketplace, 10,000+ customers
- **Year 3:** International expansion, teacher certification program, API platform for third-party curricula
- **Year 5:** The default platform for AI + robotics education. 100K+ active robots. Community-driven curriculum and character ecosystem.

The endgame: HawaBot becomes to physical AI education what Arduino became to maker electronics — the platform everyone starts with.
