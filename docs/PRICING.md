# HawaBot — Pricing & Business Logic

**Last updated:** 2026-05-03

---

## 1. Bill of Materials — Spark Kit (7 DOF, 250mm)

### Electronics & Servos

| Component | Qty | Unit Cost (bulk 50+) | Subtotal |
|---|---|---|---|
| ESP32-S3 custom PCB (assembled) | 1 | $10.00 | $10.00 |
| SG90 Micro Servo | 5 | $1.50 | $7.50 |
| MG90S Metal Gear Servo | 2 | $2.50 | $5.00 |
| Speaker (28mm) + MAX98357A (on PCB) | 1 | $2.00 | $2.00 |
| 6×3mm Neodymium Magnets (N52) | 20 | $0.10 | $2.00 |
| M2×5mm Self-Tapping Screws | 10 | $0.02 | $0.20 |
| Servo wire harness / JST connectors | 1 | $0.50 | $0.50 |
| USB-C cable | 1 | $1.00 | $1.00 |
| **Electronics subtotal** | | | **$28.20** |

Note: PCA9685 PWM driver, MAX98357A amp, and power regulation are integrated on the custom PCB (~55×35mm, 2-layer). Same PCB for Spark and Pro (Pro populates additional mic, IMU, camera connector).

### 3D Printed Frame

| Component | Weight | Material Cost | Print Time | Subtotal |
|---|---|---|---|---|
| Skeleton frame (PLA/PETG) | ~60g | $0.90 | ~3 hrs | $0.90 |
| **Frame subtotal** | | | | **$0.90** |

### Spark Kit Total

| | Self-printed | Outsourced print |
|---|---|---|
| Electronics + magnets | $28.20 | $28.20 |
| Frame print | $0.90 (material only) | $5.00 (JLC3DP/PCBWay) |
| Assembly labor | — | $5.00 (estimate) |
| **BOM total** | **$29.10** | **$38.20** |

---

## 2. Custom Character Shells — Per Order

### 3D Generation

| Step | Provider | Cost |
|---|---|---|
| 2D preview views (4 views) | Image gen API | ~$0.05 |
| 3D model generation | Meshy API | ~$0.20-0.30 |
| **Generation subtotal** | | **~$0.30** |

### Shell Printing (5 parts)

| Part | Estimated Weight | Material Cost | Print Time |
|---|---|---|---|
| Head shell | 8-12g | $0.12 | 25 min |
| Torso shell | 15-25g | $0.30 | 50 min |
| Left arm shell | 5-10g | $0.08 | 20 min |
| Right arm shell | 5-10g | $0.08 | 20 min |
| Base shell | 10-15g | $0.15 | 30 min |
| **Total** | **43-72g** | **$0.73** | **~2.5 hrs** |

| | Self-printed | Print farm |
|---|---|---|
| Material | $0.73 | — |
| Print service fee | — | $8-15 (5 parts) |
| Shell magnets (10-15 pcs) | $1.00-1.50 | $1.00-1.50 |
| **Shell subtotal** | **~$2.25** | **~$12.50** |

### Shipping (US Domestic)

| Method | Cost | Delivery |
|---|---|---|
| USPS First Class Package | $4.63-5.50 | 1-3 days |
| USPS Ground Advantage | $4.50-6.00 | 2-5 days |

---

## 3. Full Cost Stack — Per Customer Order

### Scenario A: Spark Kit (New Customer)

Skeleton kit + first character shell set, shipped.

| Line Item | Self-Print | Outsourced |
|---|---|---|
| Skeleton kit BOM | $29.10 | $38.20 |
| Character generation (3D API) | $0.30 | $0.30 |
| Shell printing (5 parts) | $2.25 | $12.50 |
| Packaging | $1.00 | $1.00 |
| Shipping | $5.00 | $5.00 |
| **Total COGS** | **$37.65** | **$57.00** |

### Scenario B: Pro Upgrade (Existing Spark Customer)

Full leg system + shoulder upgrades + sensors + battery, shipped.

| Line Item | Cost |
|---|---|
| 4× SG90 servos (elbows + hands) | $8.00 |
| 2× XL330 servos (shoulder upgrade) | $54.00 |
| 8× XL330 servos (legs) | $216.00 |
| FSRs (4×) | $8.00 |
| Battery + TP4056 | $12.00 |
| IMU + mic + camera | $8.00 |
| Leg frame + feet (3D printed) | $10.00 |
| Packaging + shipping | $10.00 |
| **Total COGS** | **~$326.00** |

Retail: **$399 upgrade** (from Spark to Pro).

### Scenario C: Additional Character (Existing Customer)

New shell set only, shipped.

| Line Item | Self-Print | Outsourced |
|---|---|---|
| Character generation | $0.30 | $0.30 |
| Shell printing (5 parts) | $2.25 | $12.50 |
| Shell magnets | $1.25 | $1.25 |
| Packaging | $0.50 | $0.50 |
| Shipping | $5.00 | $5.00 |
| **Total COGS** | **$9.30** | **$19.55** |

---

## 4. Pricing Strategy

### Tier Pricing

| Tier | All-In Price | Upgrade Price | BOM Cost | Margin |
|---|---|---|---|---|
| **Spark** (7 DOF, 250mm) | $199 | — | ~$57 (outsourced) | 71% |
| **Pro** (19 DOF) | $599 all-in | $399 (from Spark) | ~$326 (upgrade COGS) | 18% upgrade / 36% all-in |
| **Max** (future) | $999+ | TBD | TBD | TBD |

Pro upgrades Spark with XL330 serial bus servos for legs and shoulders, full sensor suite (IMU, mic, camera), battery system, and walking capability. Max is a future tier with advanced compute and on-board AI.

### Credits Model (Fortnite-Style Add-Ons)

Credits buy robot capabilities — not just tutor access. Kids spend credits to make their character DO things.

| Add-On Type | Price | Examples |
|---|---|---|
| Movement pack | $5-10 | Dance routine, martial arts moves, wave patterns |
| Voice type | $5 | New TTS personality for speaker output |
| Animation | $5-10 | Choreographed sequence, reaction animations |
| New character shell | $15-25 | Different character appearance (printed + shipped) |
| Shell STL download | $14.99 | Self-print option (~95% margin) |

**Credits power the robot, not just the tutor.** This is the Fortnite model: the base game (robot) is the platform, credits buy emotes (movement packs, voice types, animations, personality).

### Build-As-You-Go Subscription ($39/mo × 6)

Each month ships a portion of the Spark kit + curriculum:

| Month | What Ships | What They Learn |
|---|---|---|
| 1 | ESP32-S3 PCB + base frame + waist servo | Electronics, first servo, serial bus |
| 2 | Head pan + tilt servos + head frame | Sensor input, pan/tilt control |
| 3 | R shoulder pitch + roll + arm frame | Kinematics, joint coordination |
| 4 | L shoulder pitch + roll + arm frame | Symmetry, mirroring, calibration |
| 5 | Shell kit (magnetic snap-on pieces) + speaker | Character design, personality, voice |
| 6 | AI tutor unlock + credits + graduation | Full system integration, challenges |

$39/mo × 6 = $234 total (slight premium over $199 one-time, justified by curriculum pacing).

---

## 5. Unit Economics

### At 100 units/month (early stage, outsourced printing)

| Metric | Value |
|---|---|
| Revenue per Spark Kit | $199 |
| COGS per Spark Kit | $57 |
| **Gross profit per kit** | **$142** |
| Monthly kit revenue | $19,900 |
| Monthly kit gross profit | $14,200 |
| | |
| Additional characters/mo (0.3 per customer avg) | 30 |
| Revenue per character | $20 (avg, mix of printed + STL) |
| Monthly character revenue | $600 |
| | |
| Credit purchases (25% of customers) | 25 |
| Avg credit purchase | $8 |
| Monthly credit revenue | $200 |
| | |
| **Total monthly revenue** | **$20,700** |
| **Total monthly gross profit** | **$15,000+** |
| **Blended gross margin** | **~72%** |

### At 1,000 units/month (growth, in-house printing)

| Metric | Value |
|---|---|
| Revenue per Spark Kit | $199 |
| COGS per Spark Kit (in-house) | $40 |
| **Gross profit per Spark kit** | **$159** |
| Monthly kit revenue (mix: 700 Spark, 200 Pro all-in, 100 Pro upgrade) | $259,300 |
| Monthly kit gross profit | $195,000 |
| | |
| Credits + characters (recurring) | $25,000 |
| | |
| **Total monthly revenue** | **$284,300** |
| **Total monthly gross profit** | **$220,000** |
| **Blended gross margin** | **~77%** |

---

## 6. Cost Reduction Levers

| Lever | Impact | When |
|---|---|---|
| In-house print farm (3-5 Bambu printers) | -$10/kit COGS | At ~200 units/mo |
| Bulk servo + PCB sourcing (Feetech direct, JLCPCB volume) | -$5/kit | At ~500 units/mo |
| Volume 3D gen API pricing | -30% on generation costs | At ~1000 gen/mo |
| Multi-color printing (Bambu AMS) | Charge premium for painted shells | Immediate upsell |
| Customer self-print option | $0 print cost, charge for STL files only | From launch |
| Upgrade to serial bus servos (SCS0009) for production | Eliminates PCA9685, simplifies wiring | After Feetech volume pricing confirmed |

---

## 7. Competitive Pricing Reference

| Competitor | Product | Price | Humanoid? | DOF |
|---|---|---|---|---|
| Sphero BOLT+ | Programmable ball | $199 | No | 0 |
| Wonder Workshop Dash | Wheeled robot | $159 | No | 0 |
| Makeblock mBot Neo | Wheeled robot | $155 | No | 0 |
| SunFounder PiDog | Quadruped (no Pi) | $180 | No | 12 |
| UBTECH Alpha 1 Pro | Humanoid | $350 | Yes | 16 |
| Robotis Mini | Humanoid | $539 | Yes | 16 |
| Hiwonder TonyPi | Walking humanoid + Pi 5 | $570 | Yes | 18 |
| **HawaBot Spark** | **Humanoid + AI tutor** | **$199** | **Yes** | **7** |
| **HawaBot Pro** | **Humanoid + walking + full sensor suite** | **$599** | **Yes** | **19** |

**HawaBot Spark is the only humanoid robot under $350.** At $199, it sits in the Sphero BOLT+ price bracket but offers a physical humanoid body, character customization, and systems engineering curriculum that no competitor has. HawaBot Pro at $599 competes directly with Robotis Mini and Hiwonder TonyPi but includes AI tutoring, character customization, and a full walking platform.

---

## 8. Revenue Model Summary

```
┌──────────────────────────────────────────┐
│            SPARK KIT                     │  One-time ($199) or subscription ($39/mo×6)
│  Skeleton + 1st character + PCB + SDK    │
│  + curriculum access + speaker           │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         PRO UPGRADE                      │  $399 upgrade (or $599 all-in)
│  +10 XL330 servos (shoulders + legs)     │
│  +4 SG90 (elbows + hands)               │
│  +IMU + mic + camera + FSRs             │
│  +battery + leg frame + feet            │
│  +advanced curriculum modules            │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         CREDITS (Fortnite model)         │  Recurring (organic demand)
│  Movement packs: $5-10                   │
│  Voice types: $5                         │
│  Animations: $5-10                       │
│  Character shells: $15-25 (printed)      │
│  Shell STL download: $14.99              │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         MAX (Future)                     │  $999+
│  Advanced compute, on-board AI           │
│  Character marketplace (% cut)           │
│  Classroom licenses (bulk pricing)       │
│  Sensor/peripheral add-on packs          │
└──────────────────────────────────────────┘
```

**Key insight:** Credits ARE the recurring revenue. Like Fortnite emotes for physical robots — kids naturally want new movement packs, voice types, and character shells. No subscription fatigue.
