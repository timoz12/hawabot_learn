# Documentation Staleness Audit

_Last audit: 2026-05-24. All HIGH and MEDIUM items resolved._

All documentation now reflects the two-tier strategy:
- **Spark** ($199, 7 DOF, desk companion)
- **Pro** ($599, 19 DOF, walking humanoid, same 250mm skeleton)
- **Max** ($999+, future flagship, 400-500mm, on-board AI)

---

## Resolved (2026-05-24)

| File | What Was Fixed |
|---|---|
| `pipeline/COMPONENT_REFERENCE.md` | Removed all Core references, updated MCU to ESP32-S3, fixed servo counts (SG90×4/MG90S×3 Spark, SG90×8/XL330×11 Pro), removed waist roll/LEDs/ultrasonic, updated compute board sections |
| `pipeline/SOLIDWORKS_BUILD_GUIDE.md` | Replaced Pi 5 with ESP32-S3 PCB, removed waist roll, added shoulder roll, removed LEDs/ultrasonic, updated assembly tree, fixed joint positions |
| `hawabot/drivers/pi5.py` | Changed "Pro tier" → "Max tier", removed Core (11 DOF) references |
| `pipeline/INTERFACE_SPEC.md` | Updated Pico USB → ESP32-S3 USB-C in clearance specs and assembly sequence |
| `pipeline/SKELETON_SPEC.md` | Changed "Core Humanoid" variant → "Max Humanoid", "Spark/Core" → "Spark/Pro" |
| `docs/IMPLEMENTATION_PLAN.md` | Struck through resolved Core tier tech debt item |
| `docs/GO_TO_MARKET.md` | Updated partnership from "Pi Pico W / Pi 5" → "ESP32-S3 (Spark/Pro), Pi 5 (Max future)" |
| `docs/ARCHITECTURE.md` | Added ESP32Driver to driver instantiation list |

## Resolved (2026-05-12)

| File | What Was Fixed |
|---|---|
| `CLAUDE.md` | Created from scratch with full current state |
| `hawabot/config/tiers.py` | Two tiers (Spark+Pro+Max), correct DOF/servos/MCU/pricing, Core removed |
| `docs/ARCHITECTURE.md` | ESP32-S3, correct DOFs, ESP32Driver added, PicoDriver marked legacy, shoulder roll corrected to SG90 |
| `docs/STRATEGY.md` | $199/$599/$999+ pricing, two tiers, systems engineering positioning |
| `docs/PRICING.md` | Complete rewrite with current BOM, credits model, competitive analysis |
| `docs/IMPLEMENTATION_PLAN.md` | Full rewrite: ESP32-S3, two tiers, correct phases, updated hardware budget |
| `docs/GO_TO_MARKET.md` | Updated pricing ($199/$599), removed Core tier, $39/mo subscription, updated revenue targets |
| `docs/COMPETITIVE_ANALYSIS.md` | Updated pricing ($199/$599), added TonyPi competitor, two tiers, systems engineering positioning |
| `docs/TIER_COMPONENTS.md` | New — full component tables for Spark, Pro, Max with interfaces and intent |
| `hawabot/drivers/pi5.py` | Docstring updated — Max tier only |
| `pipeline/SKELETON_SPEC.md` | Staleness banner + redirect to PARAMETRIC_PIPELINE_PLAN.md |
| `solidworks_package/PARAMETRIC_PIPELINE_PLAN.md` | All Core→Pro, two-tier architecture, correct MCU table |
| `solidworks_package/SOLIDWORKS_CONTEXT.md` | New — cowork reference with full hardware context |
| `docs/PROTOTYPE_BOM_CHECKLIST.md` | Phase 1 ordered ($56), no breadboard (soldered), custom PCB reference |

## Still Pending (Low Priority)

| File | Issue | When to Fix |
|---|---|---|
| `pipeline/SHELL_PIPELINE_SPEC.md` | May reference old skeleton model | When pipeline code is modified |
| `pipeline/COMPONENT_REFERENCE.md` | Partially duplicated in solidworks_package/ | Consolidate when convenient |
| `firmware/pico_w/main.py` | Legacy — needs ESP32-S3 port | When starting firmware development |
| `hawabot/drivers/pico.py` | Legacy — needs ESP32Driver equivalent | When ESP32 firmware is ready |
