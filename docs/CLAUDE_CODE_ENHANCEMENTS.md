# Future .claude/ Enhancements

Recommendations based on the Claude Code Project Structure Reference guide, tailored to HawaBot's multi-domain workflow (hardware + firmware + pipeline + web + curriculum).

---

## Skills (Auto-activate on task match)

Skills are reusable Claude Code capabilities with instructions, scripts, and reference materials. Each lives in `.claude/skills/<name>/`.

### Recommended Skills

#### `pcb-review`
Auto-activates when working on custom PCB design or KiCad files.
```
.claude/skills/pcb-review/
├── SKILL.md          # Instructions: check pin conflicts, antenna keep-out, power rail separation
├── references/
│   └── esp32s3_pin_allocation.md  # From project_custom_pcb.md memory
└── assets/
    └── pcb_checklist.md           # DFM checklist for JLCPCB
```

#### `servo-engineering`
Auto-activates when discussing servo selection, joint design, or torque analysis.
```
.claude/skills/servo-engineering/
├── SKILL.md          # Instructions: check cantilever loads, verify pocket dimensions, reference servo survey
├── references/
│   └── servo_survey.md            # Full servo comparison table
│   └── pocket_dimensions.md       # Clearances per servo type
```

#### `solidworks-sync`
Auto-activates when preparing files for the SolidWorks machine.
```
.claude/skills/solidworks-sync/
├── SKILL.md          # Instructions: verify mate table, check for stale data, list STEP files needed
├── references/
│   └── v17_axis_architecture.md   # Plane/axis naming and architecture
```

#### `curriculum-design`
Auto-activates when writing mission content or lesson plans.
```
.claude/skills/curriculum-design/
├── SKILL.md          # Instructions: systems engineering focus, NOT coding focus, Socratic method
├── references/
│   └── curriculum_positioning.md  # From memory
│   └── learning_layers.md         # 7 system layers (mechanical → AI)
```

---

## Agents (Isolated parallel work)

Agents are subagent definitions for complex, multi-step tasks that benefit from isolation.

### Recommended Agents

#### `bom-optimizer`
Researches component pricing, checks availability, suggests alternatives.
```yaml
# .claude/agents/bom-optimizer.yml
name: BOM Optimizer
description: Research current pricing and availability for robot components
tools: [WebSearch, WebFetch, Read, Write]
instructions: |
  Search reliable suppliers (RobotShop, Adafruit, DigiKey, Mouser) for current
  pricing. Flag out-of-stock items. Suggest alternatives within spec. Never
  trust AliExpress pricing without verification. Report in table format.
```

#### `compliance-checker`
Reviews design decisions against FCC/CE/safety requirements.
```yaml
# .claude/agents/compliance-checker.yml
name: Compliance Checker
description: Check hardware design decisions against regulatory requirements
tools: [WebSearch, WebFetch, Read]
instructions: |
  Verify FCC modular certification status of RF modules. Check age-appropriate
  safety requirements (CPSIA, ASTM F963 for 12+ products). Flag any component
  that may need additional certification.
```

#### `doc-updater`
Systematically updates stale documentation to match current decisions.
```yaml
# .claude/agents/doc-updater.yml
name: Documentation Updater
description: Update stale docs to match CLAUDE.md and memory
tools: [Read, Edit, Write, Glob, Grep]
instructions: |
  Read CLAUDE.md for current decisions. Read the target file. Identify
  all discrepancies. Make minimal edits to bring the file current.
  Do not rewrite sections that are already correct.
```

---

## Hooks (Lifecycle event scripts)

Hooks run automatically on Claude Code events. These prevent common mistakes.

### Recommended Hooks

#### PreToolUse: Protect golden files
Block edits to validated SolidWorks files without explicit confirmation.
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "command": "check-golden-files.sh"
    }]
  }
}
```
`check-golden-files.sh` would warn if editing:
- `solidworks_package/hawabot_ssp_macro_v17.bas`
- `solidworks_package/hawabot_skeleton_sketch.SLDPRT`
- Any `.step` reference files

#### PostToolUse: Lint Python after edits
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "command": "python -m ruff check --fix"
    }]
  }
}
```

#### SessionEnd: Save conversation summary
Auto-save key decisions from each session to a log.
```json
{
  "hooks": {
    "SessionEnd": [{
      "command": "save-session-summary.sh"
    }]
  }
}
```

---

## Commands (Slash commands already created)

| Command | Purpose | Created |
|---|---|---|
| `/review-bom` | Generate full BOM table for all tiers | Yes |
| `/sync-solidworks` | Prepare SolidWorks package, check for drift | Yes |
| `/audit-stale` | Find all stale docs and code | Yes |
| `/update-tiers` | Update hawabot/config/tiers.py to match current decisions | Yes |

### Future Commands to Add

| Command | Purpose | When to Add |
|---|---|---|
| `/design-pcb` | Guide custom PCB schematic design in KiCad | When starting PCB design |
| `/test-firmware` | Flash and test ESP32-S3 firmware | When firmware is ready |
| `/generate-skeleton` | Run CadQuery pipeline for a character | When pipeline is automated |
| `/prep-release` | Checklist for preparing a tier release | Before first production run |
| `/cost-analysis` | Full cost analysis including shipping, labor, margin | Before pricing finalization |

---

## Implementation Priority

| Enhancement | Effort | Impact | When |
|---|---|---|---|
| **CLAUDE.md** | Done | High | Now |
| **Slash commands (4)** | Done | High | Now |
| **Stale audit** | Done | High | Now |
| Skills (pcb-review) | 30 min | Medium | When starting PCB design |
| Skills (servo-engineering) | 30 min | Medium | When revisiting servo selection |
| Skills (curriculum-design) | 30 min | Medium | When writing mission content |
| Agent (bom-optimizer) | 15 min | Medium | Before next sourcing round |
| Agent (compliance-checker) | 15 min | High | Before production |
| Hooks (golden file protection) | 15 min | Low | When multiple people edit |
| Hooks (lint) | 5 min | Low | When code quality matters |
