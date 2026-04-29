# HawaBot — Pricing & Business Logic

**Last updated:** 2026-04-29

---

## 1. Bill of Materials — Spark Skeleton Kit

### Electronics & Servos

| Component | Qty | Unit Cost (bulk 50+) | Subtotal |
|---|---|---|---|
| Raspberry Pi Pico W | 1 | $4.50 | $4.50 |
| SG90 Micro Servo | 3 | $1.00 | $3.00 |
| MG90S Metal Gear Servo | 2 | $2.00 | $4.00 |
| 6×3mm Neodymium Magnets (N52) | 40 | $0.10 | $4.00 |
| M2×5mm Self-Tapping Screws | 20 | $0.02 | $0.40 |
| Servo wire harness / connectors | 1 | $0.50 | $0.50 |
| **Electronics subtotal** | | | **$16.40** |

### 3D Printed Frame

| Component | Weight | Material Cost | Print Time | Subtotal |
|---|---|---|---|---|
| Skeleton frame (PLA/PETG) | ~60g | $0.90 | ~3 hrs | $0.90 |
| **Frame subtotal** | | | | **$0.90** |

### Skeleton Kit Total

| | Self-printed | Outsourced print |
|---|---|---|
| Electronics + magnets | $16.40 | $16.40 |
| Frame print | $0.90 (material only) | $5.00 (JLC3DP/PCBWay) |
| Assembly labor | — | $3.00 (estimate) |
| **BOM total** | **$17.30** | **$24.40** |

---

## 2. Custom Character Shells — Per Order

### 3D Generation

| Step | Provider | Cost |
|---|---|---|
| 2D preview views (4 views) | Image gen API | ~$0.05 |
| 3D model generation | Tripo3D API | ~$0.20 |
| Fallback / retry | Meshy API | ~$0.05 |
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

### Scenario A: Full Kit (New Customer)

Skeleton kit + first character shell set, shipped.

| Line Item | Self-Print | Outsourced |
|---|---|---|
| Skeleton kit BOM | $17.30 | $24.40 |
| Character generation (3D API) | $0.30 | $0.30 |
| Shell printing (5 parts) | $2.25 | $12.50 |
| Packaging | $1.00 | $1.00 |
| Shipping | $5.00 | $5.00 |
| **Total COGS** | **$25.85** | **$43.20** |

### Scenario B: Additional Character (Existing Customer)

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

### Target Margins

| Product | COGS | Sell Price | Margin | Margin % |
|---|---|---|---|---|
| **Spark Starter Kit** | ~$43 | $79-99 | $36-56 | 45-57% |
| **Additional Character** | ~$20 | $29-39 | $9-19 | 31-49% |
| **AI Tutor (monthly)** | ~$2* | $9.99/mo | ~$8 | 80% |
| **AI Tutor (annual)** | ~$24* | $79.99/yr | ~$56 | 70% |

*AI tutor COGS = Claude API usage per student (~$2/mo estimated at Haiku rates)

### Tier Packaging

#### Spark Starter Kit — $79 (introductory) / $99 (regular)

**Includes:**
- Assembled skeleton (servos installed, magnets pressed, Pico wired)
- 1 custom character shell set (customer designs at purchase)
- Shell magnets (pre-installed)
- USB-C cable
- Quick start card with QR code
- 1 month free AI tutor access

**Does NOT include:**
- Additional character shell sets ($29-39 each)
- Ongoing AI tutor subscription ($9.99/mo)

#### Character Shell Pack — $29 (simple) / $39 (complex)

**Includes:**
- 5 printed shell parts for one custom character
- Shell magnets (pre-installed)
- Snap-on — no tools needed

**Simple vs Complex:**
- Simple: characters with smooth/blocky shapes (chibi, Funko-style)
- Complex: characters with fine details, thin features (spiky hair, weapons, capes)
- Software auto-classifies based on mesh complexity

#### AI Tutor Subscription — $9.99/mo or $79.99/yr

**Includes:**
- Interactive coding lessons (progressive difficulty)
- AI-powered hints and explanations
- Code validation before running on robot
- Creative project prompts
- Progress tracking

---

## 5. Unit Economics

### At 100 units/month (early stage, outsourced printing)

| Metric | Value |
|---|---|
| Revenue per Starter Kit | $89 (avg) |
| COGS per Starter Kit | $43 |
| **Gross profit per kit** | **$46** |
| Monthly kit revenue | $8,900 |
| Monthly kit gross profit | $4,600 |
| | |
| Additional characters/mo (estimate 0.5 per customer) | 50 |
| Revenue per character | $34 (avg) |
| Monthly character revenue | $1,700 |
| Monthly character gross profit | $700 |
| | |
| Tutor subscribers (30% convert after free month) | 30 |
| Monthly tutor revenue | $300 |
| Monthly tutor gross profit | $240 |
| | |
| **Total monthly revenue** | **$10,900** |
| **Total monthly gross profit** | **$5,540** |
| **Blended gross margin** | **51%** |

### At 1,000 units/month (growth, in-house printing)

| Metric | Value |
|---|---|
| Revenue per Starter Kit | $89 |
| COGS per Starter Kit (in-house) | $28 |
| **Gross profit per kit** | **$61** |
| Monthly kit revenue | $89,000 |
| Monthly kit gross profit | $61,000 |
| | |
| Additional characters (1 per customer) | 1,000 |
| Monthly character revenue | $34,000 |
| Monthly character gross profit | $24,500 |
| | |
| Tutor subscribers (50% conversion) | 500 |
| Monthly tutor revenue | $5,000 |
| Monthly tutor gross profit | $4,000 |
| | |
| **Total monthly revenue** | **$128,000** |
| **Total monthly gross profit** | **$89,500** |
| **Blended gross margin** | **70%** |

---

## 6. Cost Reduction Levers

| Lever | Impact | When |
|---|---|---|
| In-house print farm (3-5 Bambu printers) | -$10/kit COGS | At ~200 units/mo |
| Bulk component sourcing (AliExpress, direct) | -$3/kit on servos + magnets | At ~500 units/mo |
| Volume 3D gen API pricing | -30% on generation costs | At ~1000 gen/mo |
| Multi-color printing (Bambu AMS) | Charge premium for painted shells | Immediate upsell |
| Customer self-print option | $0 print cost, charge for STL files only | From launch |

### Customer Self-Print Option

Offer shell STL files as a download ($14.99 per character) instead of printing + shipping. Margin is ~95% since COGS is just the $0.30 3D generation.

---

## 7. Competitive Pricing Reference

| Competitor | Product | Price |
|---|---|---|
| Sphero BOLT | Programmable robot ball | $149 |
| LEGO Mindstorms | Robotics kit | $359 |
| Botley 2.0 | Coding robot (younger kids) | $79 |
| littleBits | Electronics kit | $99-199 |
| Funko Pop | Collectible figure (non-robotic) | $12-15 |
| Hot Toys | Premium action figure (non-robotic) | $250-400 |

**HawaBot positioning:** Cheaper than LEGO Mindstorms / Sphero, but with custom character appeal. The character customization is the differentiator no competitor offers.

---

## 8. Revenue Model Summary

```
┌─────────────────────────────────┐
│         HARDWARE SALE           │  One-time
│  Skeleton Kit: $79-99           │
│  Character Shells: $29-39 each  │
│  STL Download: $14.99 each      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      RECURRING SUBSCRIPTION     │  Monthly/Annual
│  AI Tutor: $9.99/mo             │
│  (or $79.99/yr)                 │
│  ~80% gross margin              │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│       FUTURE EXPANSION          │
│  Character marketplace (%)      │
│  Classroom licenses             │
│  Core/Pro tier upgrades         │
│  Sensor add-on packs            │
└─────────────────────────────────┘
```
