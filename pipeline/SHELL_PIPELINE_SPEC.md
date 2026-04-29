# HawaBot Shell Pipeline — Customer Workflow Specification

End-to-end flow from character idea to printable shell parts.

---

## Overview

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. DESIGN   │ →  │  2. PREVIEW  │ →  │  3. PURCHASE │ →  │  4. GENERATE │
│  Upload/draw │    │  2D renders  │    │  Confirm +   │    │  3D model    │
│  character   │    │  (cheap)     │    │  pay         │    │  (expensive) │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                    │
                                                                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  8. PRINT +  │ ←  │  7. EXPORT   │ ←  │  6. FINALIZE │ ←  │  5. DISSECT  │
│  SHIP        │    │  Print-ready │    │  Hollow +    │    │  Guided cuts │
│              │    │  STL files   │    │  magnets     │    │  (customer)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

---

## Step 1: Design — Character Input

**Goal:** Customer provides a character concept.

### Input Methods

| Method | Description | Cost | Quality |
|---|---|---|---|
| Photo upload | Customer uploads photo/drawing of character | Free | Depends on source |
| Text prompt | "A samurai cat with a red cape" | Free | AI-dependent |
| Template | Pick from preset character base + customize | Free | Consistent |

### Output
- Character concept stored as image(s) + text description
- Used as input for preview generation

---

## Step 2: Preview — 2D Reference Views

**Goal:** Show the customer what their character will look like before committing to expensive 3D generation.

### Process
1. Generate **4 reference views** from the concept: front, back, left side, right side
2. Use cheapest available model (image-to-image, ~$0.01-0.05 per set)
3. Overlay skeleton silhouette on the views so customer can see proportions
4. Show cut plane lines on the views (dashed lines where dissection will happen)

### Customer Actions
- Approve the look → proceed to purchase
- Adjust → re-generate views (free, can iterate)
- Abandon → no cost incurred

### Technical Notes
- Skeleton silhouette overlay is a fixed SVG/PNG per view angle
- Cut plane lines are drawn at default positions from INTERFACE_SPEC
- No 3D computation at this stage — purely 2D image work

---

## Step 3: Purchase — Confirmation + Payment

**Goal:** Customer commits and pays.

### What They're Buying
- 3D model generation (compute cost)
- 5 printed shell parts (material + printing + shipping)
- Access to their character in the HawaBot app

### Pricing Model
(Defined elsewhere — this spec just covers the technical pipeline)

---

## Step 4: Generate — 3D Model Creation

**Goal:** Turn the 2D concept into a watertight 3D mesh.

### Process
1. **Enforce T-pose:** All generation prompts include T-pose instructions ("arms straight out to sides, legs shoulder-width apart, facing forward"). This is mandatory for clean zone dissection.
2. Send reference views + text description to 3D generation API (Tripo3D primary, Meshy fallback)
3. Receive raw 3D mesh (GLB/OBJ/STL)
4. **Auto-processing:**
   - Scale to match skeleton height (200mm total)
   - Center on origin
   - Orient: +Z up, +Y forward, character facing -Y
   - Repair mesh: close holes, remove degenerate faces, ensure manifold
   - Validate T-pose: check arm zones are ≥15mm wide at cut planes
   - Remesh to uniform triangle size if needed

### T-Pose Enforcement

All character models must be in **T-pose** for the pipeline to produce clean cuts:

| Input Method | T-Pose Enforcement |
|---|---|
| Text-to-3D | System pre-prompt: "standing in T-pose, arms straight out to sides, legs apart" |
| Image-to-3D | If source image isn't T-pose, regenerate reference views in T-pose first |
| Uploaded STL | Detect arm angle; if not T-pose, flag and offer to regenerate |

### Output
- Watertight 3D mesh in T-pose, correctly scaled and oriented
- Ready for dissection

### Failure Cases
| Issue | Resolution |
|---|---|
| Mesh not watertight | Auto-repair (trimesh.repair) |
| Mesh not in T-pose | Regenerate with T-pose pre-prompt |
| Mesh too thin in places | Flag to customer in dissection step |
| Mesh has internal geometry | Remove internal faces |
| Proportions don't match skeleton | Scale X/Y/Z independently to fit |

---

## Step 5: Dissect — Guided Body Zone Cutting

**Goal:** Customer walks through cutting the character into 5 body zones, confirming each cut.

This is the **interactive, customer-facing step**. The software proposes cuts; the customer adjusts and confirms.

### Process

#### 5a. Auto-propose cut planes

Software analyzes the mesh and proposes initial cut positions using defaults from INTERFACE_SPEC:

```python
cuts = {
    "head_torso": {"type": "horizontal", "z": 115, "range": (105, 130)},
    "torso_base": {"type": "horizontal", "z": 10, "range": (0, 20)},
    "left_arm":   {"type": "vertical",   "x": -28, "range": (-35, -24)},
    "right_arm":  {"type": "vertical",   "x": 28, "range": (24, 35)},
}
```

Smart defaults: if the mesh has a visible neck narrowing, snap head cut to narrowest point. If arms are clearly separated from torso, snap arm cuts to the gap.

#### 5b. Customer walks through each cut

For each cut, the UI shows:

1. **3D view** of the character with the cut plane highlighted
2. **Slider** to move the cut plane up/down (or left/right for arms)
3. **Preview** of the two resulting pieces (above/below the cut)
4. **Warnings** if the cut:
   - Intersects a servo position (blocked — can't cut there)
   - Creates a zone smaller than 15mm (warning)
   - Creates a zone that won't clear a joint (warning)
5. **Confirm** button to lock the cut and move to the next one

#### Cut sequence
1. Head / Torso (horizontal) — most intuitive, start here
2. Left arm (vertical)
3. Right arm (vertical)
4. Torso / Base (horizontal)

After all 4 cuts: customer sees the **exploded view** — all 6 pieces separated, colored by zone (torso = front + back clamshell). Confirm to proceed.

#### 5c. Validation

After all cuts are confirmed, validate:
- [ ] Every zone has minimum dimensions (15mm in any axis)
- [ ] No servo position falls inside a shell zone (servos stay in skeleton)
- [ ] Magnet positions are reachable (not cut through)
- [ ] Each zone can physically slide onto/off the skeleton (no undercuts that trap it)

### Output
- 5 separate mesh pieces (raw, not yet hollowed)
- Cut plane positions recorded for this character

---

## Step 6: Finalize — Hollow + Magnet Bosses

**Goal:** Turn each solid zone piece into a printable hollow shell with magnet attachment features.

### Process per Zone

#### 6a. Hollow the shell (Skeleton Subtraction Method)

1. **Build clearance volume** for this zone — the skeleton geometry (servos, brackets, column) expanded by 1.5mm clearance per side, plus joint rotation sweep volumes
2. **Apply draft taper** along the removal direction (1.5-2° angle so shell slides on/off easily)
3. **Boolean subtract** clearance volume from the solid zone piece → shell with exact skeleton-shaped cavity
4. **Torso special case:** Split into front/back clamshell halves along the XZ plane (Y=0), since the torso can't slide over shoulder brackets as one piece
5. **Validate wall thickness** — scan for any region thinner than 2mm after subtraction. Flag thin spots to customer or auto-thicken.

**Shell removal directions:**

| Zone | Removal | Draft Angle | Notes |
|---|---|---|---|
| Head | Lifts up (+Z) | 2° | Neck opening must clear magnet ring |
| Torso | Clamshell front/back | 1° | Each half pulls away along ±Y |
| Arms | Slide outward (±X) | 2° | Inboard face is open |
| Base | Lifts off (-Z) | 1.5° | Top face is open |

#### 6b. Select magnet positions

For each zone, run the magnet selection algorithm (defined in INTERFACE_SPEC):

1. Get all candidate magnet positions for this zone from skeleton spec
2. Check which ones the shell has enough wall thickness for (≥6mm at that point)
3. Score by distribution balance + edge distance
4. Select minimum required count (or more if shell geometry supports it)

#### 6c. Merge magnet bosses

For each selected magnet position:

1. Create a boss cylinder (⌀10mm × 4mm tall) on the shell's inner surface
2. Orient boss so pocket faces toward skeleton magnet
3. **Boolean union** boss with shell
4. **Cut** magnet pocket (⌀6.1mm × 3.1mm) into boss
5. Verify boss doesn't punch through shell outer surface

#### 6d. Joint clearance trimming

Check each joint's range of motion. If the shell would collide with an adjacent shell during movement:

1. Simulate the joint rotation at 5° increments through full ROM
2. Find any intersection between this shell and adjacent shells
3. **Trim** the interfering region with a swept boolean cut
4. Re-validate wall thickness after trimming

### Output per Zone
- Hollow shell mesh with magnet bosses
- Magnet position list (which skeleton magnets this shell uses)
- Validation report (wall thickness, clearance, magnet count)

---

## Step 7: Export — Print-Ready Files

**Goal:** Generate final STL files ready for 3D printing.

### Process

1. **Orient for printing** — lay each shell in optimal print orientation:
   - Head: upside down (opening up), minimizes supports
   - Torso: on its back or upright depending on geometry
   - Arms: on flat side
   - Base: upside down (opening up)

2. **Generate supports** (or mark support-free orientation)

3. **Export STL** per zone (6 files — torso is 2 pieces):
   ```
   character_shells/
   ├── head_shell.stl
   ├── torso_front_shell.stl
   ├── torso_back_shell.stl
   ├── left_arm_shell.stl
   ├── right_arm_shell.stl
   └── base_shell.stl
   ```

4. **Export assembly preview** — combined STL/3MF with all shells + skeleton for visual verification

### Quality Checks
- [ ] All meshes manifold (watertight)
- [ ] No degenerate triangles
- [ ] File size reasonable (< 50MB per piece)
- [ ] Fits printer bed (max 220×220×250mm — standard Ender 3)

---

## Step 8: Print + Ship

**Goal:** Physical shells arrive at customer's door.

### Fulfillment Options
| Option | Description |
|---|---|
| Partner print farm | Send STLs to print service → ship to customer |
| In-house printing | Print at HawaBot facility |
| Customer prints | Provide STL files for home printing (future) |

### Kit Contents
- 5 shell parts (labeled)
- Bag of 6×3mm magnets (count matches shell requirements)
- Instruction card (snap magnets into pockets, place shells on skeleton)
- QR code → setup guide in HawaBot app

---

## Pipeline Code Architecture

```
pipeline/
├── SKELETON_SPEC.md          # Skeleton frame design (fixed)
├── INTERFACE_SPEC.md         # Shell↔skeleton contract (fixed)
├── SHELL_PIPELINE_SPEC.md    # This document
│
├── skeleton.py               # Skeleton geometry + magnet positions
├── generate_skeleton_step.py # CadQuery STEP export for skeleton
│
├── dissect.py                # Step 5: Cut mesh into zones
├── hollow.py                 # Step 6a: Shell hollowing
├── magnets.py                # Step 6b-c: Magnet selection + boss merge
├── clearance.py              # Step 6d: Joint clearance trimming
├── validate.py               # Validation checks across all steps
├── export.py                 # Step 7: Print-ready STL generation
│
├── shell_pipeline.py         # Orchestrator: runs steps 4-7 end to end
└── skeleton_exports/         # Generated skeleton files
```

### Key Dependencies
- `trimesh` — mesh loading, manipulation, boolean ops
- `manifold3d` — robust boolean operations (subtract, union)
- `cadquery` — parametric CAD for skeleton STEP generation
- `numpy` — geometry math
- `Meshy API` (or equivalent) — 3D model generation (Step 4)

---

## Data Flow Summary

```
Photo/Text ──→ 2D Views ──→ 3D Mesh ──→ 5 Solid Zones ──→ 5 Hollow Shells ──→ 5 STL Files
                  │              │              │                  │
                  │         Scale + Orient   Cut planes      Magnet bosses
                  │         Repair mesh     (customer        (auto-selected)
                  │                          adjusts)       Joint trimming
                  │
            Skeleton silhouette
            overlay (fixed)
```
