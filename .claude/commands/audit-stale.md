Audit all documentation and code for staleness against current decisions.

Read CLAUDE.md for the current state of decisions, then check each file below for conflicts:

**Documentation:**
- docs/ARCHITECTURE.md — check MCU references, tier DOF counts, driver references
- docs/STRATEGY.md — check pricing, tier definitions, target audience
- docs/PRICING.md — check against current $199/$299/$599 tier pricing
- docs/IMPLEMENTATION_PLAN.md — check against current phase status
- pipeline/SKELETON_SPEC.md — check dimensions, DOF, servo references
- pipeline/SHELL_PIPELINE_SPEC.md — check skeleton model references
- pipeline/INTERFACE_SPEC.md — check component dimensions

**Code:**
- hawabot/config/tiers.py — check DOF counts, servo types, MCU assignments, pricing
- hawabot/drivers/pico.py — check if ESP32 driver exists or is needed
- hawabot/drivers/pi5.py — check if still relevant
- firmware/pico_w/main.py — check if ESP32 port exists

For each file, report:
- Current state (what it says)
- Correct state (what it should say based on current decisions)
- Priority (high = blocks SolidWorks or firmware work, medium = misleading, low = cosmetic)
