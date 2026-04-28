# HawaBot Shell Interface Specification

This document defines the **contract between the skeleton and the shell parts**. It specifies where shells attach, how they're oriented, what clearance they need, and where cut planes divide a character into body zones.

The skeleton team owns this spec. The shell pipeline must conform to it. If you change a magnet position here, both the skeleton CAD and the shell pipeline must update.

---

## Body Zones

A character model gets dissected into **5 zones**. Each zone becomes a separate hollow shell that snaps onto the skeleton via magnets.

```
    ┌─────────────┐
    │             │
    │    HEAD     │  Zone 1
    │             │
    ├──┬──────┬───┤  ← Head cut plane
    │  │      │   │
 ┌──┤  │TORSO │  ├──┐
 │L │  │      │  │R │
 │ARM│ │      │  │ARM│  Zone 3 (L), Zone 4 (R)
 │  │  │      │  │  │
 └──┤  │      │  ├──┘
    │  │      │   │  Zone 2
    ├──┴──────┴───┤  ← Base cut plane
    │    BASE     │  Zone 5
    └─────────────┘
```

| Zone | Name | What it covers | Attaches to |
|---|---|---|---|
| 1 | Head | Head + neck | Head magnet ring on skeleton |
| 2 | Torso | Chest, back, waist | Torso magnet grid on skeleton |
| 3 | Left Arm | Left shoulder + arm | Left arm magnets on skeleton |
| 4 | Right Arm | Right shoulder + arm | Right arm magnets on skeleton |
| 5 | Base | Feet, base cover | Base rim magnets on skeleton |

---

## Cut Planes

Cut planes define where the character model gets sliced into zones. The customer can **adjust these up/down** during the guided dissection step to match their character's proportions.

### Default Cut Plane Positions

| Cut Plane | Z Position | Adjustable Range | Divides |
|---|---|---|---|
| Head / Torso | Z = 115 mm | 105–130 mm | Head zone from torso zone |
| Torso / Base | Z = 10 mm | 0–20 mm | Torso zone from base zone |
| Left arm | X = -28 mm | -24 to -35 mm | Left arm from torso |
| Right arm | X = +28 mm | +24 to +35 mm | Right arm from torso |

### Cut Plane Rules

1. **Head/Torso cut** must be **below** the head pan servo (Z=120) so the pan/tilt stack stays inside the head shell. Default Z=115 is at the neck area — the head shell drops over the pan/tilt servo stack.
2. **Arm cuts** are vertical planes. They must be **inboard of the shoulder servo** (X=±40) so the servo housing stays with the skeleton.
3. **Torso/Base cut** must be **above the base plate top surface** (Z=0). The base shell wraps around the base plate sides and bottom.
4. All cuts produce **overlapping edges** — each shell extends 1mm past the cut plane to avoid visible gaps when assembled.

### Customer Adjustment UI

The customer sees the character model with colored cut lines. They can drag each line:

- **Head cut:** Slide up/down to adjust where the neck meets the body. Higher = more neck on the torso piece. Lower = more neck on the head piece.
- **Arm cuts:** Slide in/out to adjust how much shoulder is on the arm vs torso piece.
- **Base cut:** Slide up/down to control how much of the lower body is torso vs base.

Software validates after each adjustment that:
- No cut plane intersects a servo location
- Each zone has minimum 15mm height/width (printability)
- Magnet positions fall within the correct zone

---

## Clearance Envelopes

Each zone shell must maintain **minimum clearance** from the skeleton so it can be placed/removed and joints can move.

### Head Zone Clearance

```
Shell inner surface must clear:
- Head pan servo body by ≥ 2mm radially
- Head tilt servo body by ≥ 2mm radially  
- Head pan rotation: ±90° yaw → shell must not collide with torso shell
  → minimum inner radius of 18mm around Z axis at cut plane
- Head tilt rotation: ±30° pitch → clearance arc in +Y/-Y direction
  → 5mm gap between tilt servo horn and shell inner wall
```

| Constraint | Value | Why |
|---|---|---|
| Min inner radius at neck | 18 mm | Pan rotation clearance |
| Min gap from tilt servo | 5 mm | Nod range of motion |
| Min shell wall thickness | 2.0 mm | Printability |
| Opening diameter (bottom) | ≥ 36 mm | Must fit over head magnet ring |

### Torso Zone Clearance

```
Shell inner surface must clear:
- Torso column by ≥ 3mm radially (wire routing space)
- Waist rotation: ±90° → the entire torso shell rotates with the waist servo
  → at the base cut plane, shell must clear base shell by ≥ 2mm through full rotation
- Shoulder servo housing by ≥ 2mm
```

| Constraint | Value | Why |
|---|---|---|
| Min gap from torso column | 3 mm | Wire routing + tolerance |
| Min gap at waist rotation | 2 mm | Shell-to-shell clearance during rotation |
| Min shell wall thickness | 2.0 mm | Printability |

### Arm Zone Clearance

```
Shell inner surface must clear:
- Shoulder servo housing by ≥ 2mm
- Shoulder pitch rotation: ±90° → arm shell rotates around X axis
  → at the shoulder cut, shell must clear torso shell through full rotation
- Servo horn + arm shaft by ≥ 2mm
```

| Constraint | Value | Why |
|---|---|---|
| Min gap from servo housing | 2 mm | Assembly tolerance |
| Min inner radius at shoulder | 20 mm | Rotation clearance |
| Min shell wall thickness | 2.0 mm | Printability |
| Max arm shell weight | 15 g | Servo torque limit (MG90S: 1.8 kg·cm) |

### Base Zone Clearance

```
Shell covers the base plate sides and bottom.
- Must clear Pico USB port (slot in +X side)
- Must not block base plate top surface (waist servo mounts here)
- Battery compartment access (future)
```

| Constraint | Value | Why |
|---|---|---|
| USB port clearance | 14×8 mm opening on +X face | Pico W USB access |
| Min shell wall thickness | 2.0 mm | Printability |
| Max overhang past base | 5 mm | Stability — shell shouldn't make it tippy |

---

## Magnet Interface Contract

### How It Works

1. **Skeleton** has magnet pockets at all predefined positions (see SKELETON_SPEC.md § Magnet Grid)
2. **Software** analyzes the shell geometry and selects which magnet positions to use
3. **Shell** gets magnet boss features merged onto its inner surface at the selected positions
4. **Assembly:** magnets press-fit into both skeleton and shell pockets. User drops shell onto skeleton — magnets snap it into place.

### Magnet Boss Geometry (Shell Side)

Each magnet boss is a small cylindrical protrusion on the shell's inner surface:

```
        ┌─────────┐  Shell outer wall
        │         │
        │  ┌───┐  │  Magnet boss: ⌀10mm base, ⌀6.1mm pocket
        │  │ M │  │  M = magnet pocket (⌀6.1 × 3.1mm deep)
        │  └───┘  │
        │         │
        └─────────┘

Side view:
        Shell wall (2mm)
        ├──┤
             Boss (4mm tall, ⌀10mm)
             ├────┤
                   Pocket (⌀6.1, 3.1mm deep)
                   ├───┤
```

| Parameter | Value | Notes |
|---|---|---|
| Boss outer ⌀ | 10 mm | Structural base |
| Boss height | 4 mm | Extends inward from shell wall |
| Pocket ⌀ | 6.1 mm | Press-fit for 6mm magnet |
| Pocket depth | 3.1 mm | Flush or 0.1mm recessed |
| Min shell wall behind boss | 1.5 mm | Don't punch through |

### Magnet Selection Algorithm

For each body zone, the software:

1. **Filters** magnet positions to those where the shell has ≥ 6mm wall thickness (boss needs 4mm + 2mm wall behind it)
2. **Scores** each position by:
   - Distance from shell center of mass (favor positions that create balanced pull)
   - Angular distribution (favor even spacing, penalize clustering)
   - Proximity to shell edge (penalize positions too close to zone boundary)
3. **Selects** minimum required magnets per zone:

| Zone | Min Magnets | Max Magnets | Required Pattern |
|---|---|---|---|
| Head | 3 | 8 | At least 3, evenly distributed around ring |
| Torso | 4 | 10 | At least 2 front + 2 back for rotational stability |
| Left Arm | 2 | 6 | At least 1 near shoulder + 1 toward hand |
| Right Arm | 2 | 6 | Mirror of left |
| Base | 3 | 8 | At least 3 corners for stability |

4. **Validates** that selected magnets provide:
   - Pull force ≥ 2× shell weight (each magnet ~0.5kg, so 3 magnets hold 1.5kg — plenty for ~15g shells)
   - No single-axis alignment (magnets can't all be in a line)
   - Stable seating (shell doesn't rock when placed)

### Polarity Convention

| Side | Polarity Facing Out |
|---|---|
| Skeleton | North |
| Shell | South |

All magnets in a zone face the same direction. This means any shell fits any skeleton — no per-character polarity matching needed.

---

## Assembly Sequence (End User)

1. Skeleton ships assembled — servos installed, magnets press-fit, Pico wired
2. Customer receives 5 printed shell parts (head, torso, L arm, R arm, base)
3. Customer presses magnets into shell boss pockets (or pre-installed at fulfillment)
4. **Base shell:** Slide onto base plate bottom → magnets snap
5. **Torso shell:** Lower over torso column → magnets snap to column surface
6. **Arm shells:** Slide over shoulder housings → magnets snap
7. **Head shell:** Drop over head servo stack → magnets snap to neck ring
8. Power on, code, play

No tools required. All connections are magnetic snap-fit.

---

## Validation Checks (Shell Pipeline Must Pass)

Before a shell set is approved for printing:

| Check | Criteria | Fail Action |
|---|---|---|
| Wall thickness | ≥ 2mm everywhere | Flag thin spots, suggest thickening |
| Clearance | Meets envelope constraints above | Flag interference, suggest hollowing more |
| Magnet bosses | ≥ min count per zone, all have wall behind them | Adjust selection or flag to customer |
| Joint motion | No shell-to-shell collision through full ROM | Trim interfering regions |
| Watertight | Each shell is manifold (printable) | Auto-repair or flag |
| Weight | Each zone ≤ max weight for its servo | Suggest thinner walls or smaller design |
| Opening size | Shell can physically fit over skeleton features | Flag if opening too narrow |
