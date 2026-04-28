# HawaBot Spark Skeleton — SolidWorks Build Guide

Step-by-step instructions to build the complete 200mm skeleton assembly in SolidWorks using real servo STEP files, parametric frame geometry, magnet pockets, and wire channels.

---

## Prerequisites

### Download Component STEP Files

Before starting, download these and save to a local folder (e.g., `C:\HawaBot\components\`):

| Component | Source | File |
|---|---|---|
| Pi Pico W | [raspberrypi.com](https://datasheets.raspberrypi.com/picow/PicoW-step.zip) | `PicoW.step` |
| SG90 Servo | [GrabCAD](https://grabcad.com/library/sg90-micro-servo-9g-tower-pro-1) | `SG90.step` |
| MG90S Servo | [GrabCAD](https://grabcad.com/library/mg90s-servo-high-detail-1) | `MG90S.step` |

GrabCAD requires a free account. The Pi Pico W STEP is a direct download (no account).

### Verify Servo Dimensions

After importing each servo STEP, measure it against our spec. Community models may differ slightly:

| Check | SG90 Expected | MG90S Expected |
|---|---|---|
| Body L×W×H | 22.7 × 12.2 × 27.0 mm | 22.8 × 12.4 × 28.4 mm |
| Tab-to-tab L | 32.3 mm | 32.1 mm |
| Overall H (with shaft) | 32.3 mm | 32.5 mm |

If the STEP dimensions don't match, adjust your `C_wall` clearance to compensate.

---

## Part 1: Frame Part (`frame.sldprt`)

This is the 3D-printed structural frame — the backbone that everything mounts to.

### Step 1.1: Create Part and Set Up Equations

1. **File → New → Part** (millimeters template)
2. **Tools → Equations** → click **Import** → select `pipeline/skeleton_exports/equations.txt`
   - All global variables are now available in any sketch dimension
3. Alternatively, manually enter the key variables:

```
"BASE_W" = 90          "SHOULDER_Z" = 110
"BASE_D" = 70          "SHOULDER_X" = 40
"BASE_H" = 20          "HEAD_PAN_Z" = 120
"BASE_R" = 6           "HEAD_TILT_Z" = 148
"TORSO_D" = 24         "C_wall" = 0.3
"WAIST_Z" = 10         "D_wire" = 6
"MAG_POCKET_D" = 6.1   "MAG_POCKET_H" = 3.1
"D_screw" = 2.0
```

### Step 1.2: Build the Base Plate

**Sketch on Top Plane** (this is Z=0, the base plate top surface):

1. Draw a **Center Rectangle**: width = `"BASE_W"` (90), height = `"BASE_D"` (70)
2. **Sketch Fillet** all 4 corners: radius = `"BASE_R"` (6)
3. **Exit Sketch** → **Boss-Extrude**: Direction = **Blind, downward** (check "Reverse Direction"), depth = `"BASE_H"` (20)
4. Name the feature: `Base Plate`

**Result:** A 90×70×20mm rounded-rect plate sitting below the origin, from Z=0 down to Z=-20.

### Step 1.3: Pi Pico W Pocket (cut from bottom)

1. **Select the bottom face** of the base plate (Z=-20) → **Insert Sketch**
2. Draw a rectangle: 57mm × 25mm (`"PICO_cavity_L"` × `"PICO_cavity_W"`)
3. **Position:** Dimension the rectangle center to X=+25mm from origin (`"PICO_X_OFFSET"`), Y=0
4. **Exit Sketch** → **Cut-Extrude**: Direction = **Blind, upward** (into the plate), depth = 12mm (`"PICO_cavity_H"`)
   - This leaves 8mm of solid above the pocket (20-12=8mm floor)
5. Name: `Pico Pocket`

**USB Access Slot:**

6. **Select the bottom face** again → **Insert Sketch**
7. Draw a rectangle: 14mm tall × spans from Pico pocket right edge to +X base edge
   - Width = (90/2) - (25 + 57/2) + 1mm overlap ≈ 17.5mm
   - Height = 12mm (same as Pico pocket depth)
8. Center vertically (Y=0)
9. **Cut-Extrude**: depth = 12mm (same as pocket)
10. Name: `USB Slot`

**Pico Mounting Bosses:**

11. **Select the floor** of the Pico pocket → **Insert Sketch**
12. Draw 4 circles at Pico mounting hole positions:
    - Hole spacing: 47mm × 11.4mm, centered on the Pico pocket center
    - Boss OD = 4.5mm, hole = 2.1mm
13. **Boss-Extrude**: upward 5mm (standoffs for the board to sit on)
14. **Hole Wizard**: M2 through holes through each boss
15. Name: `Pico Standoffs`

### Step 1.4: Waist Servo Pocket (on top face)

1. **Select Top Plane** → **Insert Sketch** at Z=0
2. Draw the servo body pocket outline, centered at origin:
   - Rectangle: 23.3mm × 12.8mm (`"SG90_L" + 2*"C_wall"` × `"SG90_W" + 2*"C_wall"`)
3. **Exit Sketch** → **Boss-Extrude**: upward, depth = 27.6mm (`"SG90_H" + 2*"C_wall"`)
   - ✅ **Merge result = CHECKED** (part of the frame)
4. Name: `Waist Servo Column`

**Tab Ledges:**

5. Create a **new sketch** on the front face of the waist column, at Z = `"SG90_tab_Z"` (17mm above base surface)
6. Draw a horizontal shelf profile: extends out to tab length each side
   - Total shelf width = 32.9mm (`"SG90_tab_L" + 2*"C_wall"`)
   - Shelf depth = 3.4mm (`"SG90_tab_T" + 2*"C_wall"`)
   - Shelf is a U-shaped pocket: the servo body sits in the middle, tabs rest on ledges
7. **Cut-Extrude**: through the column at tab height to create the slot
8. Name: `Waist Tab Slot`

**Screw Bosses at Tab Holes:**

9. Use **Hole Wizard** → Straight Tap, M2 × 8mm deep
10. Position at each tab mounting hole:
    - 2 holes per tab, inset 2mm from tab edge
    - Total 4 holes (2 per side)
11. Name: `Waist Screw Holes`

**Turret + Shaft Clearance:**

12. **New sketch** on top of waist column (Z = 27.6mm)
13. Draw a circle: ⌀12.4mm (`"SG90_turret_D" + 2*"C_wall"`)
14. **Cut-Extrude**: upward through remaining material, or add a cylindrical void rising above the column
15. Name: `Waist Turret Clearance`

**Cable Exit:**

16. **New sketch** on the side face of the waist column
17. Draw a slot/rectangle: 4mm × 6mm, positioned at Z ≈ 5mm (bottom of servo)
18. **Cut-Extrude**: through the wall
19. Name: `Waist Cable Exit`

### Step 1.5: Torso Column

1. **New sketch on Top Plane** at Z=0
2. Draw a rounded rectangle centered at origin: 24mm × 24mm with 4mm corner fillets
   - Or draw a circle ⌀24mm — either works
3. **Boss-Extrude**: upward from Z=0 to Z=120mm (`"HEAD_PAN_Z"`)
   - Merge result = CHECKED
4. Name: `Torso Column`

> **Note:** The torso column merges into the waist servo column below. SolidWorks will union them automatically since Merge is checked.

**Vertical Wire Channel:**

5. **New sketch on Top Plane**
6. Draw a circle: ⌀6mm (`"D_wire"`), centered at X = +14mm, Y = 0 (offset from torso center, along the back side)
7. **Cut-Extrude**: from Z=0 upward through full torso height (120mm)
   - Use "Through All" or "Up To Surface" of the torso top face
8. Name: `Vertical Wire Channel`

### Step 1.6: Shoulder Servo Mounts

Each shoulder is a mounting bracket that extends outward from the torso column. The MG90S servo is oriented with its shaft pointing outward (±X).

**Left Shoulder:**

1. **New sketch** on the **Front Plane** (or a plane at Z = `"SHOULDER_Z"` = 110mm)
2. Draw the shoulder mount bracket profile:
   - Start from torso column outer edge (X = -12mm)
   - Extend to X = -40mm (`-"SHOULDER_X"`)
   - Width (Z direction) = MG90S body width + walls = 12.4 + 2×0.3 + 2×2.5 = 17.6mm
   - Depth (Y direction) = MG90S body length + walls = 22.8 + 2×0.3 + 2×2.5 = 28.2mm
3. **Boss-Extrude**: depth = bracket Y dimension (centered on Y=0)
   - Merge result = CHECKED
4. Name: `Left Shoulder Bracket`

**Left Shoulder Servo Pocket:**

5. **New sketch** on the outer face of the left bracket (X = -40mm face)
6. Draw servo body pocket: 23.4mm × 13.0mm (`"MG90S_L"+2*"C_wall"` × `"MG90S_W"+2*"C_wall"`)
7. **Cut-Extrude**: inward (toward +X) by full servo height: 29.0mm (`"MG90S_H"+2*"C_wall"`)
   - This hollows out the bracket to accept the servo
8. Name: `Left Servo Pocket`

**Left Shoulder Tab Slot:**

9. At Z = `SHOULDER_Z` + `MG90S_tab_Z` - `MG90S_H`/2 (tab height from bottom of servo), cut a wider slot for the mounting tabs
10. Slot dimensions: 32.7mm × 3.4mm (`"MG90S_tab_L"+2*"C_wall"` × `"MG90S_tab_T"+2*"C_wall"`)
11. Name: `Left Tab Slot`

**Left Shoulder Screw Holes:**

12. **Hole Wizard**: M2 × 6mm at each tab mounting hole position (4 holes total)
13. Name: `Left Screw Holes`

**Left Shaft Hole:**

14. **New sketch** on the outer face of left bracket
15. Draw circle at servo shaft position: ⌀8mm (shaft + horn clearance)
16. **Cut-Extrude**: Through All (so the shaft/horn can extend outward)
17. Name: `Left Shaft Hole`

**Right Shoulder:**

18. Select all left shoulder features → **Insert → Mirror → Mirror Feature**
19. Mirror plane = **Right Plane** (YZ plane)
20. This creates the right shoulder as an exact mirror
21. Rename mirrored features with `Right` prefix

**Horizontal Wire Channels:**

22. For each shoulder: **New sketch** at Z = 110mm
23. Draw ⌀6mm circle at Y=0, X = ±14mm (where torso wire channel is)
24. **Cut-Extrude**: horizontally from torso center to shoulder bracket
25. Name: `Left Wire Channel`, `Right Wire Channel`

### Step 1.7: Head Pan Servo Mount

The head pan servo sits at the top of the torso column, shaft pointing up (+Z).

1. **New sketch** at Z = `"HEAD_PAN_Z"` = 120mm (top of torso column)
2. Draw a mounting platform profile:
   - Outer: 34mm × 20mm rounded rect (servo tab length + walls)
   - This extends the torso column top to support the pan servo
3. **Boss-Extrude**: upward by SG90 full height = 32.9mm (`"SG90_H_total" + 2*"C_wall"`)
   - Merge = CHECKED
4. Name: `Head Pan Mount`

**Pan Servo Pocket:**

5. **New sketch** on top of head pan mount
6. Draw SG90 body pocket: 23.3mm × 12.8mm, centered
7. **Cut-Extrude**: downward into the mount by 27.6mm (`"SG90_cav_H"`)
8. Name: `Pan Servo Pocket`

**Pan Tab Slot:**

9. Cut wider slot at tab height (Z = 120 + 17 = 137mm)
10. Slot: 32.9mm × 3.4mm
11. Name: `Pan Tab Slot`

**Pan Screw Holes:**

12. Hole Wizard: M2 at tab hole positions
13. Name: `Pan Screw Holes`

**Pan Turret Clearance:**

14. Cut a ⌀12.4mm hole through the top of the mount for turret + shaft
15. Name: `Pan Turret Clearance`

### Step 1.8: Head Tilt Servo Mount

The tilt servo stacks above the pan servo, rotated 90° so its shaft points forward (+Y).

1. **New sketch** at Z = `"HEAD_TILT_Z"` = 148mm
2. Draw a mounting bracket profile:
   - The tilt servo is rotated: body dimensions are now W×L×H = 12.8 × 23.3 × 27.6mm (swapped L and W because it's rotated)
   - Bracket outer: 18mm × 28mm (servo dims + walls)
3. **Boss-Extrude**: upward by servo width dimension (12.8 + walls)
   - Or extrude a bracket shape that connects down to the pan mount
   - Merge = CHECKED
4. Name: `Head Tilt Mount`

**Tilt Servo Pocket:**

5. Cut pocket into the bracket: 12.8mm × 23.3mm × 27.6mm, oriented with long axis along Y
6. Name: `Tilt Servo Pocket`

**Tilt Tab Slot + Screw Holes:**

7. Cut tab slot at the appropriate rotation
8. Add M2 holes
9. Name: `Tilt Tab Slot`, `Tilt Screw Holes`

**Tilt Shaft Hole:**

10. ⌀8mm hole through the +Y face for shaft/horn to extend forward
11. Name: `Tilt Shaft Hole`

**Head Pan → Tilt Wire Channel:**

12. ⌀4mm channel from pan servo area up through tilt mount
13. Name: `Pan-Tilt Wire Channel`

### Step 1.9: Magnet Pockets

All 40 magnet pockets are cut into the frame's outer surfaces. Each pocket is ⌀6.1mm × 3.1mm deep.

**Recommended approach:** Use a **Hole Wizard** counterbore (⌀6.1mm, depth 3.1mm, no through-hole) placed at each magnet position. Or use a simple Cut-Extrude with a ⌀6.1mm circle.

#### Head Zone (8 pockets)

Create on the head pan mount outer surface, at Z=125mm (ring around the neck):

| ID | X | Y | Z | Face |
|---|---|---|---|---|
| H1 | 0 | -14 | 125 | Front |
| H2 | 0 | +14 | 125 | Back |
| H3 | -14 | 0 | 125 | Left |
| H4 | +14 | 0 | 125 | Right |
| H5 | -10 | -10 | 125 | Front-Left |
| H6 | +10 | -10 | 125 | Front-Right |
| H7 | -10 | +10 | 125 | Back-Left |
| H8 | +10 | +10 | 125 | Back-Right |

1. For each position: sketch a ⌀6.1mm circle on the appropriate face
2. **Cut-Extrude**: 3.1mm into the surface
3. Name each: `Mag_H1` through `Mag_H8`

> **Tip:** Create one pocket as a feature, then use **Linear Pattern** or **Sketch Driven Pattern** to place the rest. For the ring, use **Circular Pattern** around the Z axis with 8 instances.

#### Torso Zone (12 pockets)

On the torso column outer surface at 3 heights (Z=30, 70, 100), 4 positions per ring:

| Ring Z | Front (Y-) | Back (Y+) | Left (X-) | Right (X+) |
|---|---|---|---|---|
| 30 | T1 | T2 | T7 | T8 |
| 70 | T3 | T4 | T9 | T10 |
| 100 | T5 | T6 | T11 | T12 |

1. Create one pocket on the front face at Z=30
2. **Circular Pattern** around Z axis: 4 instances (0°, 90°, 180°, 270°)
3. **Linear Pattern** along Z: 3 instances, spacing = 35mm (Z=30, 65, 100)
4. Name: `Mag_Torso_Pattern`

#### Arm Zone (6 pockets per arm, 12 total)

On each shoulder bracket outer surface:

1. Create pockets at LA1–LA6 positions (see SKELETON_SPEC.md)
2. Mirror to right arm
3. Name: `Mag_Left_Arm`, `Mag_Right_Arm`

#### Base Zone (8 pockets)

On the base plate side faces at Z=-10mm:

1. Create pockets at B1–B8 positions around the base perimeter
2. Name: `Mag_Base_Pattern`

### Step 1.10: Final Frame Touches

**Fillets:**
1. Add 1mm fillets to all sharp internal edges (printability)
2. Add 2mm fillets to external edges where frame sections meet (strength)

**Weight Reduction (optional):**
1. **Shell** command on the torso column interior: 3mm wall, leaving it partially hollow
2. Only if the frame is too heavy — solid is stronger

---

## Part 2: Assembly (`hawabot_spark_skeleton.sldasm`)

### Step 2.1: Create Assembly

1. **File → New → Assembly**
2. **Insert Component** → select `frame.sldprt` → place at origin (fixed)

### Step 2.2: Insert Servo Components

**Waist Servo (SG90 #1):**

1. **Insert Component** → `SG90.sldprt`
2. **Mate:**
   - Coincident: servo bottom face → frame waist pocket bottom face
   - Coincident: servo centerline → frame waist pocket centerline
   - Coincident: servo front face → frame waist pocket front face
3. Verify servo drops into pocket with ~0.3mm gap on each side

**Left Shoulder Servo (MG90S #1):**

1. **Insert Component** → `MG90S.sldprt`
2. **Mate:**
   - Coincident: servo body → left shoulder pocket (rotated so shaft points -X)
   - Align tab holes with frame screw holes
3. Verify fit

**Right Shoulder Servo (MG90S #2):**

1. Insert MG90S, mate into right pocket (shaft points +X)

**Head Pan Servo (SG90 #2):**

1. Insert SG90, mate into pan pocket (shaft points +Z)

**Head Tilt Servo (SG90 #3):**

1. Insert SG90, mate into tilt pocket (shaft points +Y)
2. Verify it clears the pan servo below

### Step 2.3: Insert Pi Pico W

1. **Insert Component** → `PicoW.sldprt`
2. **Mate:**
   - Coincident: board bottom → Pico pocket standoff tops
   - Centered in pocket (X = +25mm from origin)
   - USB port aligned with USB slot opening

### Step 2.4: Insert Magnets (Reference)

1. Create a simple part: cylinder ⌀6mm × 3mm → `magnet_6x3.sldprt`
2. Insert into each magnet pocket (40 instances)
3. These are **reference only** — they show where magnets go but aren't part of the printed frame

> **Shortcut:** Use **Component Pattern** referencing the magnet pocket features to auto-place all 40 magnets.

### Step 2.5: Interference Check

1. **Tools → Evaluate → Interference Detection**
2. **Expected interferences:** None (all components should have clearance)
3. **Check for:**
   - Servo bodies fitting in pockets (0.3mm gap)
   - Servo tabs resting on ledges
   - Shaft/horn clearing holes
   - Pico fitting in pocket with USB access
   - No magnet-to-servo collisions

### Step 2.6: Section Views

Verify internal geometry with section views:

1. **Insert → Reference Geometry → Section View** through Front Plane
   - Check: servo pockets properly shaped, wire channels visible, magnet pockets correct depth
2. Section through Right Plane
   - Check: shoulder servo pocket, horizontal wire channel, arm shaft hole
3. Section through a horizontal plane at Z=110
   - Check: shoulder bracket cross-section, servo clearance

---

## Part 3: Export

### Frame STL for 3D Printing

1. In `frame.sldprt`: **File → Save As → STL**
2. Settings:
   - Resolution: **Fine** (deviation 0.01mm, angle 5°)
   - Units: Millimeters
   - Save as: `frame_spark_v1.stl`

### Assembly STEP for Reference

1. In the assembly: **File → Save As → STEP (.step)**
2. This exports all components positioned correctly
3. Save as: `hawabot_spark_skeleton_assembly.step`

### Individual Section STEPs

Not needed anymore — the frame is one piece. Only the cosmetic shells get split into sections.

---

## Parametric Adjustments

To modify the skeleton, change variables in **Tools → Equations**:

| Want to... | Change | Effect |
|---|---|---|
| Wider shoulders | `SHOULDER_X` from 40 → 45 | Brackets extend further, arm shells wider |
| Taller figure | `HEAD_PAN_Z`, `HEAD_TILT_Z` | Torso column grows, head moves up |
| Thicker torso | `TORSO_D` from 24 → 28 | More room for wires, bulkier look |
| More magnet clearance | `MAG_POCKET_D` from 6.1 → 6.2 | Looser magnet fit |
| Tighter servo fit | `C_wall` from 0.3 → 0.2 | Less gap around servos |

All features referencing these variables rebuild automatically.
