# HawaBot Go-to-Market Strategy

## Market Entry Thesis

HawaBot launches B2C first, selling directly to parents of kids aged 12-15. The design platform (free to use, pay to build) is the primary acquisition funnel. B2B (schools, camps) follows once product-market fit is validated and demand is established from the bottom up.

**Why B2C first:**
- Faster sales cycle (days, not months)
- Emotional purchase ("my kid designed their own robot")
- Direct feedback loop for rapid iteration
- Bottom-up demand makes B2B sales easier later ("our students already want this")

---

## Customer Segments

### Segment 1: STEM-Curious Parents (Primary, B2C)

| Attribute | Detail |
|-----------|--------|
| **Who** | Parents of kids aged 12-15 with interest in coding, robotics, or STEM |
| **Household income** | $80K+ (comfortable spending $99-499 on enrichment) |
| **Motivation** | "I want my kid to learn real skills, not just play games" |
| **Purchase trigger** | Kid designs a character they love; parent sees educational value |
| **Decision maker** | Parent pays; kid drives demand |
| **LTV** | $150-600 (initial kit + potential tier upgrade + subscription premium) |
| **CAC target** | $15-30 (via organic + targeted digital) |

### Segment 2: Gift Buyers (B2C, Seasonal)

| Attribute | Detail |
|-----------|--------|
| **Who** | Grandparents, aunts/uncles, family friends |
| **When** | Holiday season (Nov-Dec), birthdays year-round |
| **Motivation** | "Something educational but exciting" |
| **Purchase trigger** | Gift guides, social proof, unboxing videos |
| **Decision maker** | Gift buyer; recipient is the kid |
| **Key insight** | Spark ($99) is perfectly positioned as a premium gift |

### Segment 3: Educators and Schools (B2B, Phase 2)

| Attribute | Detail |
|-----------|--------|
| **Who** | Middle school STEM teachers, CS teachers, robotics club advisors |
| **Budget** | $2,000-10,000 per classroom set |
| **Motivation** | AI fluency mandates (Boston Sept 2026, 28 states with guidance) |
| **Purchase trigger** | Student demand + admin pressure to teach AI |
| **Decision maker** | Teacher recommends; admin approves budget |
| **LTV** | $5,000-25,000 (class set + annual curriculum license) |
| **CAC target** | $200-500 (trade shows, teacher referrals, direct outreach) |

### Segment 4: Camps and After-School Programs (B2B, Phase 2)

| Attribute | Detail |
|-----------|--------|
| **Who** | Summer camps, after-school STEM programs, makerspaces |
| **Budget** | $1,000-5,000 per program |
| **Motivation** | Differentiated programming that attracts enrollment |
| **Purchase trigger** | "Our parents are asking about AI and robotics" |
| **LTV** | $3,000-15,000 (reusable kits + annual license) |

---

## Acquisition Funnel

```
AWARENESS ──> DESIGN ──> ATTACHMENT ──> PURCHASE ──> ACTIVATE ──> EXPAND
   |             |            |             |            |           |
  Ads,       Free design   "I love my    Buy kit    Unbox,     Upgrade
  social,    platform      character!"   ($99-499)  assemble,  tier,
  content,   (no account               + monthly   start      subscribe,
  PR         required)                  option     curriculum   refer
```

### Stage 1: Awareness

**Channels:**

| Channel | Tactic | Cost | Expected CAC |
|---------|--------|------|--------------|
| TikTok/Instagram Reels | Short-form: "Watch this kid design a robot" (15-30s) | $500-2K/month | $10-20 |
| YouTube | Longer tutorials, unboxing, "build with me" series | $300-1K/month (creator partnerships) | $15-25 |
| Reddit (r/robotics, r/STEM, r/Python) | Organic posts showing the pipeline, SDK, kid builds | $0 (organic) | $0 |
| Parent forums/Facebook groups | Targeted posts in homeschool, STEM parent communities | $200-500/month | $8-15 |
| PR | Launch coverage in EdTech, maker, parenting publications | One-time effort | $0 if earned |
| SEO | "Python robotics for kids", "AI robotics kit", "LEGO alternative" | Content creation cost | $5-10 (long-term) |

**Key content assets:**
- 30-second "design to delivery" video (text prompt -> 3D model -> printed robot -> kid codes it)
- Side-by-side: HawaBot character vs. generic robot (emotional hook)
- "LEGO retired. Here's what's next." article targeting parent search queries
- Student project showcases (once beta users have builds)

### Stage 2: Design (The Free Funnel)

The design platform is free to use. No account required. This is the most critical funnel innovation.

**Flow:**
1. Kid lands on hawabot.com
2. Types a character description or uploads a sketch
3. AI generates a 3D model in ~30 seconds
4. Interactive Three.js viewer: rotate, zoom, exploded view
5. "Want to build this? Choose your tier."
6. Account creation + payment only at checkout

**Why this works:**
- Zero friction to emotional attachment (kid sees *their* character in 3D)
- Free design = viral sharing ("look what I made")
- Design gallery becomes social proof and content engine
- Platform generates leads even from non-buyers (retarget later)

**Metrics to track:**
- Designs created / day
- Design-to-checkout conversion rate (target: 5-10%)
- Average designs per user before purchase
- Social shares of designs

### Stage 3: Attachment

Between design and purchase, the kid has already named their character and iterated on the design. The emotional investment is real. This is the moment the parent sees the kid genuinely excited and decides to buy.

**Tactics:**
- Email the design to the kid ("Your robot is ready to be built!")
- Show the character in a mockup scene (on a desk, in a kid's room)
- Preview character-specific animations ("Here's how FireDrake waves")
- Social sharing: "Share your design" button with character image

### Stage 4: Purchase

**Two options at checkout:**

| Option | Spark | Core | Pro |
|--------|-------|------|-----|
| **Full Kit (one-time)** | $99 | $249 | $499 |
| **Monthly (5 months)** | $25/mo | $55/mo | $110/mo |

**Monthly subscription value prop:**
- Lower commitment: "Try it for $25"
- New module each month (unboxing excitement 5x)
- Matches curriculum pacing (new hardware for new lessons)
- Higher total revenue ($125 vs. $99 for Spark)

**Checkout optimizations:**
- Default to monthly option (lower barrier)
- Show "most popular" badge on Core tier
- Countdown: "Your design is saved for 7 days"
- Trust signals: 30-day guarantee, COPPA compliant, real photos of kits

### Stage 5: Activate

First 48 hours after delivery determine long-term engagement.

**Activation sequence:**
1. Unboxing experience (quality packaging, clear "start here" card)
2. Assembly guide (15-30 minutes, magnets + snap-fit, no tools)
3. First code: `from hawabot import Robot; robot = Robot(); robot.wave()`
4. AI tutor introduces itself using the character's name
5. Mission 1.1 begins: "Make [CharacterName] look around"

**Target activation metrics:**
- Kit assembled within 24 hours of delivery: 80%
- First code executed within 48 hours: 70%
- Mission 1.1 completed within 1 week: 60%

### Stage 6: Expand

**Expansion revenue streams:**

| Opportunity | Trigger | Revenue |
|-------------|---------|---------|
| Tier upgrade (Spark -> Core) | Kid completes Month 2, wants teach-by-demo | $150-200 |
| New character shell | Kid wants a different character for same skeleton | $20-40 |
| Subscription upsell | Full-kit buyer wants monthly modules | $25-110/mo |
| Referral | Kid shows friend; friend designs own character | Referral bonus |
| B2B lead | Teacher sees student's robot; contacts Hawa Labs | $2,000-10,000 |

---

## Pricing Strategy

### Principles

1. **Spark is the gateway.** $99 is impulse-buy territory for target demographic. Optimize for volume, not margin.
2. **Monthly lowers the bar.** $25/month is Netflix pricing. Parents say yes easily.
3. **Core is the sweet spot.** Best margin-to-value ratio. "Most popular" positioning.
4. **Pro is aspirational.** Not everyone needs it. Creates ceiling for the most engaged.

### Price Anchoring

```
On the pricing page:

  Pro $499        <-- Anchor (makes Core look reasonable)
  Core $249       <-- "Most Popular" badge
  Spark $99       <-- "Start Here" badge
```

### Subscription Economics

| Tier | Monthly Price | Months | Total | vs. Full Kit | Premium |
|------|-------------|--------|-------|--------------|---------|
| Spark | $25 | 5 | $125 | $99 | +26% |
| Core | $55 | 5 | $275 | $249 | +10% |
| Pro | $110 | 5 | $550 | $499 | +10% |

Subscribers pay a premium for the monthly unboxing experience and lower upfront commitment. This premium funds the additional shipping costs (5 shipments vs. 1).

---

## Launch Plan

### Pre-Launch (8 weeks before)

| Week | Activity |
|------|----------|
| -8 | Landing page live with email waitlist |
| -7 | Design platform open (free, no purchase yet) |
| -6 | Begin posting design showcase content on social media |
| -5 | Influencer/creator outreach (send 5-10 free beta kits) |
| -4 | Press kit distributed to EdTech, maker, parenting publications |
| -3 | Email waitlist: "Launching in 3 weeks. Design your robot now." |
| -2 | Early access for waitlist (limited quantity, 20% discount) |
| -1 | Final pre-launch social push: user-generated designs, countdown |

### Launch Week

| Day | Activity |
|-----|----------|
| Day 0 | Public launch. Platform open for orders. |
| Day 0 | Launch post on Product Hunt |
| Day 0 | Reddit posts: r/robotics, r/Python, r/STEM, r/edtech |
| Day 0 | Email blast to full waitlist |
| Day 1-2 | Respond to all social media engagement |
| Day 3 | First customer unboxing video (from early access) shared |
| Day 5 | "First week" metrics review. Adjust ad spend. |
| Day 7 | Thank-you email to first customers. Request reviews. |

### Post-Launch (Weeks 1-12)

| Week | Focus |
|------|-------|
| 1-2 | Customer support, fulfill initial orders, gather feedback |
| 3-4 | Iterate on design platform based on user behavior data |
| 5-6 | Launch referral program (design credit for referrals) |
| 7-8 | Content series: "Student of the week" showcasing builds |
| 9-10 | Retarget design-only users (designed but did not purchase) |
| 11-12 | Core tier announcement + pre-orders |

---

## Channel Strategy

### Direct (Primary)

| Channel | Role | Investment |
|---------|------|-----------|
| hawabot.com | Primary sales channel, design platform | $500/month hosting + tools |
| Email marketing | Nurture leads, announce launches, curriculum updates | $50-100/month (Resend/Loops) |
| Social media (owned) | Brand building, community, student showcases | Time + $200/month content tools |

### Paid (Scale)

| Channel | Audience | Budget | Expected ROAS |
|---------|----------|--------|---------------|
| Meta (Instagram/Facebook) | Parents of teens, STEM interests | $1,000-3,000/month | 3-5x |
| TikTok Ads | Teens 13-17, tech/maker interests | $500-1,500/month | 2-4x |
| Google Ads | "robotics kit for kids", "Python for kids", "LEGO alternative" | $500-1,000/month | 4-6x |
| YouTube Ads | Pre-roll on STEM/coding/maker channels | $500-1,000/month | 3-5x |

**Total paid budget:** $2,500-6,500/month (scale up with validated ROAS)

### Earned/Organic (Leverage)

| Channel | Tactic |
|---------|--------|
| Product Hunt | Launch day listing |
| Hacker News | "Show HN: We built a pipeline that turns any AI-generated 3D model into a printable robot shell" |
| Reddit | Organic posts in relevant communities (not ads) |
| Teacher word-of-mouth | Free design platform access for educators |
| Student word-of-mouth | "Share your robot" social features |
| Press | EdTech, maker, parenting publications |

---

## Partnership Opportunities

### Tier 1 (Pursue Immediately)

| Partner | Type | Value |
|---------|------|-------|
| **Code.org / CS Teachers Association** | Curriculum alignment | Credibility with educators, B2B pipeline |
| **Raspberry Pi Foundation** | Hardware ecosystem | Pi Pico W / Pi 5 are our compute platforms |
| **Anthropic** | AI partner | Claude powers the tutor; co-marketing opportunity |
| **Bambu Lab / Prusa** | 3D printing | Volume printing partnership, co-brand "printed on Bambu Lab" |

### Tier 2 (Pursue at Scale)

| Partner | Type | Value |
|---------|------|-------|
| **Amazon** | Retail channel | Spark kit on Amazon for discoverability |
| **Micro Center** | Retail channel | In-store demos, maker audience |
| **FIRST Robotics** | Competition ecosystem | Bridge from educational to competitive robotics |
| **Public libraries** | Community access | Maker programs, equalizer for lower-income access |
| **After-school networks (Boys & Girls Club, 4-H)** | B2B channel | Volume, reach underserved communities |

---

## Metrics and KPIs

### North Star Metric

**Active Robots:** Number of robots that have executed SDK code in the last 30 days.

This metric captures acquisition (someone bought a kit), activation (they built it and coded it), and retention (they are still using it). Everything else ladders up to this.

### Funnel Metrics

| Stage | Metric | Target (Month 3) | Target (Month 12) |
|-------|--------|-------------------|---------------------|
| Awareness | Monthly unique visitors | 5,000 | 50,000 |
| Design | Designs created / month | 500 | 5,000 |
| Conversion | Design-to-purchase rate | 5% | 8% |
| Purchase | Kits sold / month | 25 | 300 |
| Activation | Kit assembled < 48 hours | 80% | 85% |
| Activation | First code < 1 week | 70% | 80% |
| Retention | Active at 30 days | 60% | 70% |
| Retention | Active at 90 days | 40% | 55% |
| Expansion | Tier upgrade rate | 5% | 15% |
| Referral | Referral rate | 10% | 20% |

### Revenue Metrics

| Metric | Target (Month 6) | Target (Month 12) |
|--------|-------------------|---------------------|
| Monthly revenue | $15,000 | $50,000 |
| Monthly recurring (subscriptions) | $3,000 | $15,000 |
| Average order value | $120 | $150 |
| Customer acquisition cost | $25 | $20 |
| Gross margin | 35% | 45% |
| LTV:CAC ratio | 4:1 | 8:1 |

### Product Metrics

| Metric | Target |
|--------|--------|
| Missions completed per active user/month | 3+ |
| AI tutor interactions per session | 5+ |
| Teach-by-demo recordings per user/month | 2+ (Core/Pro) |
| Character designs shared socially | 15% of all designs |
| NPS (Net Promoter Score) | 50+ |

### B2B Metrics (Phase 2+)

| Metric | Target (Month 18) |
|--------|-------------------|
| School pilots active | 5 |
| Kits deployed in schools | 100 |
| Teacher satisfaction score | 4.5/5 |
| B2B revenue / month | $10,000 |
| Inbound B2B leads / month | 20 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Low design-to-purchase conversion | A/B test design flow, add "virtual robot" free tier to build habit before purchase |
| High CAC on paid channels | Double down on organic/viral (design sharing, student showcases), reduce paid spend |
| Fulfillment bottleneck (3D printing) | Partner with print farm for overflow; pre-print popular designs; batch printing |
| Subscription churn after Month 1 | Strong Month 2 preview in Month 1 curriculum; "what's coming next" teasers |
| B2B sales cycle too long | Start with after-school programs (faster decision) before schools (budget cycles) |
| Seasonal demand concentration (holidays) | Year-round content marketing; birthday gift positioning; camp partnerships for summer |

---

## Summary: First 12 Months

| Quarter | Focus | Revenue Target |
|---------|-------|----------------|
| Q1 | Pre-launch: build waitlist, beta test, design platform live | $0 (pre-revenue) |
| Q2 | Spark launch, first 200 customers, validate funnel | $20,000 |
| Q3 | Scale Spark, launch Core, begin B2B pilots | $50,000 |
| Q4 | Holiday push, Core at scale, 500+ total customers | $100,000 |

**Year 1 revenue target: $170,000-250,000**

This is achievable with ~1,500 kits sold at an average order value of $130, requiring ~125 kits/month by Q4. With a 6% design-to-purchase conversion rate and 25,000 monthly visitors, this is within reach through organic growth plus modest paid spend.
