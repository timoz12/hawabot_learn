"""
Generate HawaBot Spark skeleton as a high-fidelity STEP file.

Produces a single-body frame with:
- Proper servo-shaped pockets (body + tab slots + turret clearance + shaft holes)
- Screw bosses at all servo mounting points
- 40 magnet pockets (⌀6.1 × 3.1mm) at predefined positions
- Wire channels (vertical + horizontal)
- Pi Pico W pocket with USB access slot and mounting standoffs

Coordinate system: Z-up, origin at center of base plate top surface.
Target height: 200mm.
"""

import cadquery as cq
import os
import math

# ── Global Parameters ─────────────────────────────────────────────────────

C_wall = 0.3        # Servo-to-pocket clearance per side
T_wall = 2.5        # Minimum structural wall
D_wire = 6.0        # Wire channel diameter
D_screw = 2.0       # M2 screw pilot hole diameter
SCREW_BOSS_OD = 5.0 # Screw boss outer diameter

# Base plate
BASE_W = 90.0
BASE_D = 70.0
BASE_H = 20.0
BASE_R = 6.0

# Torso
TORSO_D = 24.0       # Cross-section diameter / side length
TORSO_R = 4.0        # Corner radius for rounded-rect cross-section

# Servo positions
WAIST_Z = 10.0
SHOULDER_Z = 110.0
SHOULDER_X = 40.0
HEAD_PAN_Z = 120.0
HEAD_TILT_Z = 148.0

# SG90 servo dimensions
SG90_L = 22.7       # Body length (front-back)
SG90_W = 12.2       # Body width (side-side)
SG90_H = 27.0       # Body height (bottom to case top)
SG90_H_total = 32.3 # Bottom to spline top
SG90_tab_L = 32.3   # Tab-to-tab length
SG90_tab_T = 2.8    # Tab thickness
SG90_tab_Z = 17.0   # Tab underside height from servo bottom
SG90_turret_D = 11.8
SG90_turret_H = 5.96
SG90_shaft_offset = 6.2
SG90_spline_OD = 4.8
SG90_hole_D = 2.0
SG90_hole_inset = 2.0

# SG90 cavity (body + clearance)
SG90_cav_L = SG90_L + 2 * C_wall
SG90_cav_W = SG90_W + 2 * C_wall
SG90_cav_H = SG90_H + 2 * C_wall

# MG90S servo dimensions
MG90S_L = 22.8
MG90S_W = 12.4
MG90S_H = 28.4
MG90S_H_total = 32.5
MG90S_tab_L = 32.1
MG90S_tab_T = 2.8
MG90S_tab_Z = 18.5
MG90S_spline_OD = 4.8
MG90S_hole_D = 2.0

# MG90S cavity
MG90S_cav_L = MG90S_L + 2 * C_wall
MG90S_cav_W = MG90S_W + 2 * C_wall
MG90S_cav_H = MG90S_H + 2 * C_wall

# Pi Pico W
PICO_L = 51.0
PICO_W = 21.0
PICO_H = 12.0
PICO_cavity_L = PICO_L + 6    # 57
PICO_cavity_W = PICO_W + 4    # 25
PICO_X_OFFSET = 25.0
PICO_hole_L = 47.0            # Mounting hole spacing (length)
PICO_hole_W = 11.4            # Mounting hole spacing (width)
PICO_hole_D = 2.1
PICO_standoff_H = 5.0         # Standoff height
PICO_standoff_OD = 4.5        # Standoff outer diameter

# Magnets
MAG_POCKET_D = 6.1
MAG_POCKET_H = 3.1
MAG_BOSS_OD = 10.0   # Only used on shells, not skeleton

# ── Magnet Positions ──────────────────────────────────────────────────────
# Each tuple: (x, y, z, face_normal_x, face_normal_y, face_normal_z)
# The normal indicates which direction to cut the pocket into the surface.

HEAD_MAGNETS = [
    (0, -14, 125, 0, -1, 0),    # H1 Front
    (0, 14, 125, 0, 1, 0),      # H2 Back
    (-14, 0, 125, -1, 0, 0),    # H3 Left
    (14, 0, 125, 1, 0, 0),      # H4 Right
    (-10, -10, 125, -1, -1, 0), # H5 Front-Left
    (10, -10, 125, 1, -1, 0),   # H6 Front-Right
    (-10, 10, 125, -1, 1, 0),   # H7 Back-Left
    (10, 10, 125, 1, 1, 0),     # H8 Back-Right
]

TORSO_MAGNETS = [
    # Z=30 ring
    (0, -14, 30, 0, -1, 0),     # T1
    (0, 14, 30, 0, 1, 0),       # T2
    (-14, 0, 30, -1, 0, 0),     # T7
    (14, 0, 30, 1, 0, 0),       # T8
    # Z=70 ring
    (0, -14, 70, 0, -1, 0),     # T3
    (0, 14, 70, 0, 1, 0),       # T4
    (-14, 0, 70, -1, 0, 0),     # T9
    (14, 0, 70, 1, 0, 0),       # T10
    # Z=100 ring
    (0, -14, 100, 0, -1, 0),    # T5
    (0, 14, 100, 0, 1, 0),      # T6
    (-14, 0, 100, -1, 0, 0),    # T11
    (14, 0, 100, 1, 0, 0),      # T12
]

LEFT_ARM_MAGNETS = [
    (-40, -10, 110, 0, -1, 0),  # LA1 Front
    (-40, 10, 110, 0, 1, 0),    # LA2 Back
    (-40, 0, 100, 0, 0, -1),    # LA3 Bottom
    (-40, 0, 120, 0, 0, 1),     # LA4 Top
    (-52, -8, 110, -1, 0, 0),   # LA5 Outer front
    (-52, 8, 110, -1, 0, 0),    # LA6 Outer back
]

RIGHT_ARM_MAGNETS = [
    (40, -10, 110, 0, -1, 0),   # RA1
    (40, 10, 110, 0, 1, 0),     # RA2
    (40, 0, 100, 0, 0, -1),     # RA3
    (40, 0, 120, 0, 0, 1),      # RA4
    (52, -8, 110, 1, 0, 0),     # RA5
    (52, 8, 110, 1, 0, 0),      # RA6
]

BASE_MAGNETS = [
    (-35, -28, -10, 0, -1, 0),  # B1 Front-left
    (35, -28, -10, 0, -1, 0),   # B2 Front-right
    (-35, 28, -10, 0, 1, 0),    # B3 Back-left
    (35, 28, -10, 0, 1, 0),     # B4 Back-right
    (0, -28, -10, 0, -1, 0),    # B5 Front-center
    (0, 28, -10, 0, 1, 0),      # B6 Back-center
    (-40, 0, -10, -1, 0, 0),    # B7 Left-center
    (40, 0, -10, 1, 0, 0),      # B8 Right-center
]


# ── Helper Functions ──────────────────────────────────────────────────────

def _sg90_pocket(workplane, x, y, z, shaft_axis="Z"):
    """
    Cut an SG90 servo pocket into a solid.
    shaft_axis: "Z" (shaft up), "Y" (shaft forward), "X" (shaft sideways)

    Cuts: body cavity + tab slot + turret clearance + shaft hole.
    Returns the workplane with cuts applied.
    """
    wp = workplane

    if shaft_axis == "Z":
        # Servo body pocket: centered at (x, y), bottom at z
        body = (
            cq.Workplane("XY")
            .workplane(offset=z + SG90_cav_H / 2)
            .center(x, y)
            .rect(SG90_cav_L, SG90_cav_W)
            .extrude(SG90_cav_H / 2, both=True)
        )
        wp = wp.cut(body)

        # Tab slot: wider, at tab height
        tab_z = z + SG90_tab_Z
        tab = (
            cq.Workplane("XY")
            .workplane(offset=tab_z + (SG90_tab_T + 2 * C_wall) / 2)
            .center(x, y)
            .rect(SG90_tab_L + 2 * C_wall, SG90_cav_W)
            .extrude((SG90_tab_T + 2 * C_wall) / 2, both=True)
        )
        wp = wp.cut(tab)

        # Turret clearance above body
        turret_bottom = z + SG90_cav_H
        turret_h = SG90_turret_H + 2 * C_wall
        turret = (
            cq.Workplane("XY")
            .workplane(offset=turret_bottom)
            .center(x, y)
            .circle((SG90_turret_D + 2 * C_wall) / 2)
            .extrude(turret_h)
        )
        wp = wp.cut(turret)

        # Shaft hole above turret
        shaft_bottom = turret_bottom + turret_h
        shaft_clearance_h = 10  # Extra space for horn rotation
        shaft = (
            cq.Workplane("XY")
            .workplane(offset=shaft_bottom)
            .center(x, y)
            .circle((SG90_spline_OD + 4) / 2)  # Horn clearance
            .extrude(shaft_clearance_h)
        )
        wp = wp.cut(shaft)

    elif shaft_axis == "Y":
        # Rotated 90°: servo body L along X, servo body W along Z,
        # servo body H along Y. Shaft points +Y.
        body = (
            cq.Workplane("XZ")
            .workplane(offset=y)
            .center(x, z)
            .rect(SG90_cav_W, SG90_cav_L)  # W along X, L along Z (in XZ plane)
            .extrude(SG90_cav_H / 2, both=True)
        )
        wp = wp.cut(body)

        # Tab slot (wider along the long axis, which is now Z)
        tab_offset_y = y + SG90_tab_Z - SG90_H / 2
        tab = (
            cq.Workplane("XZ")
            .workplane(offset=tab_offset_y)
            .center(x, z)
            .rect(SG90_cav_W, SG90_tab_L + 2 * C_wall)
            .extrude((SG90_tab_T + 2 * C_wall) / 2, both=True)
        )
        wp = wp.cut(tab)

        # Turret clearance (extends in +Y)
        turret_y = y + SG90_cav_H / 2
        turret = (
            cq.Workplane("XZ")
            .workplane(offset=turret_y)
            .center(x, z)
            .circle((SG90_turret_D + 2 * C_wall) / 2)
            .extrude(SG90_turret_H + 2 * C_wall)
        )
        wp = wp.cut(turret)

        # Shaft hole (+Y direction)
        shaft_y = turret_y + SG90_turret_H + 2 * C_wall
        shaft = (
            cq.Workplane("XZ")
            .workplane(offset=shaft_y)
            .center(x, z)
            .circle((SG90_spline_OD + 4) / 2)
            .extrude(10)
        )
        wp = wp.cut(shaft)

    return wp


def _mg90s_pocket(workplane, x, y, z, shaft_axis="X", shaft_sign=-1):
    """
    Cut an MG90S servo pocket for shoulder mount.
    Servo oriented with shaft pointing along X axis (outward from body).
    shaft_sign: -1 for left (shaft -X), +1 for right (shaft +X).

    Servo body H dimension runs along X (the shaft axis).
    Servo body L dimension runs along Y.
    Servo body W dimension runs along Z.
    """
    wp = workplane

    # Body pocket centered at (x, y, z)
    body = (
        cq.Workplane("YZ")
        .workplane(offset=x)
        .center(y, z)
        .rect(MG90S_cav_L, MG90S_cav_W)
        .extrude(MG90S_cav_H / 2, both=True)
    )
    wp = wp.cut(body)

    # Tab slot: extends wider along Y at tab height
    # Tab Z position relative to servo bottom: MG90S_tab_Z
    # Servo bottom is at x - shaft_sign * MG90S_cav_H/2 (opposite side from shaft)
    tab_x = x  # Tabs are at a fixed height up the servo body
    tab = (
        cq.Workplane("YZ")
        .workplane(offset=tab_x)
        .center(y, z)
        .rect(MG90S_tab_L + 2 * C_wall, MG90S_cav_W)
        .extrude((MG90S_tab_T + 2 * C_wall) / 2, both=True)
    )
    wp = wp.cut(tab)

    # Shaft hole: extends outward from servo in shaft direction
    shaft_start_x = x + shaft_sign * MG90S_cav_H / 2
    shaft = (
        cq.Workplane("YZ")
        .workplane(offset=shaft_start_x)
        .center(y, z)
        .circle((MG90S_spline_OD + 4) / 2)
        .extrude(shaft_sign * 20)  # Through the bracket and out
    )
    wp = wp.cut(shaft)

    return wp


def _screw_holes_sg90(workplane, x, y, z, shaft_axis="Z"):
    """Add M2 screw pilot holes at SG90 tab mounting positions."""
    wp = workplane

    if shaft_axis == "Z":
        # Tab holes are along the long axis (X direction), at tab height
        tab_z = z + SG90_tab_Z
        # 4 holes: 2 on each tab end
        # Tab extends ±SG90_tab_L/2 from center along X
        # Holes are inset from tab edge by SG90_hole_inset
        hole_x_offset = SG90_tab_L / 2 - SG90_hole_inset
        for dx_sign in [-1, 1]:
            for dy_sign in [-1, 1]:
                hx = x + dx_sign * hole_x_offset
                hy = y + dy_sign * (SG90_W / 2 - 1)  # Near tab edges
                hole = (
                    cq.Workplane("XY")
                    .workplane(offset=tab_z - 4)
                    .center(hx, hy)
                    .circle(D_screw / 2)
                    .extrude(8)
                )
                wp = wp.cut(hole)
    elif shaft_axis == "Y":
        tab_offset_y = y + SG90_tab_Z - SG90_H / 2
        hole_z_offset = SG90_tab_L / 2 - SG90_hole_inset
        for dz_sign in [-1, 1]:
            for dx_sign in [-1, 1]:
                hz = z + dz_sign * hole_z_offset
                hx = x + dx_sign * (SG90_W / 2 - 1)
                hole = (
                    cq.Workplane("XZ")
                    .workplane(offset=tab_offset_y - 4)
                    .center(hx, hz)
                    .circle(D_screw / 2)
                    .extrude(8)
                )
                wp = wp.cut(hole)

    return wp


def _screw_holes_mg90s(workplane, x, y, z, shaft_sign=-1):
    """Add M2 screw pilot holes at MG90S tab mounting positions."""
    wp = workplane

    hole_y_offset = MG90S_tab_L / 2 - 2.0  # Inset from tab edge
    for dy_sign in [-1, 1]:
        for dz_sign in [-1, 1]:
            hy = y + dy_sign * hole_y_offset
            hz = z + dz_sign * (MG90S_W / 2 - 1)
            hole = (
                cq.Workplane("YZ")
                .workplane(offset=x - 4)
                .center(hy, hz)
                .circle(D_screw / 2)
                .extrude(8)
            )
            wp = wp.cut(hole)

    return wp


def _cut_magnet_pockets(workplane, magnet_list):
    """Cut magnet pockets into the solid at each position."""
    wp = workplane

    for mx, my, mz, nx, ny, nz in magnet_list:
        # Normalize the normal vector
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length == 0:
            continue
        nx, ny, nz = nx / length, ny / length, nz / length

        # Determine which workplane to use based on dominant normal direction
        if abs(nz) > abs(nx) and abs(nz) > abs(ny):
            # Normal is mostly Z — cut from top or bottom face
            direction = 1 if nz > 0 else -1
            pocket = (
                cq.Workplane("XY")
                .workplane(offset=mz)
                .center(mx, my)
                .circle(MAG_POCKET_D / 2)
                .extrude(direction * MAG_POCKET_H)
            )
        elif abs(ny) > abs(nx):
            # Normal is mostly Y — cut from front or back face
            direction = 1 if ny > 0 else -1
            pocket = (
                cq.Workplane("XZ")
                .workplane(offset=my)
                .center(mx, mz)
                .circle(MAG_POCKET_D / 2)
                .extrude(direction * MAG_POCKET_H)
            )
        else:
            # Normal is mostly X — cut from left or right face
            direction = 1 if nx > 0 else -1
            pocket = (
                cq.Workplane("YZ")
                .workplane(offset=mx)
                .center(my, mz)
                .circle(MAG_POCKET_D / 2)
                .extrude(direction * MAG_POCKET_H)
            )

        wp = wp.cut(pocket)

    return wp


# ── Main Build ────────────────────────────────────────────────────────────

def build_skeleton_frame():
    """
    Build the complete skeleton frame as a single solid body.
    This is the 3D-printed structural part — everything mounts to this.
    """

    # ── 1. Base Plate ─────────────────────────────────────────────────────
    # Z = -BASE_H to Z = 0
    frame = (
        cq.Workplane("XY")
        .workplane(offset=-BASE_H / 2)
        .rect(BASE_W, BASE_D)
        .extrude(BASE_H / 2, both=True)
    )
    frame = frame.edges("|Z and (not >Z)").fillet(BASE_R)

    # ── 2. Waist Servo Column ─────────────────────────────────────────────
    # Solid block rising from base surface to house the waist servo
    # Outer dimensions: servo + walls on each side
    waist_outer_l = SG90_tab_L + 2 * C_wall + 2 * T_wall  # ~37.3mm
    waist_outer_w = SG90_cav_W + 2 * T_wall                # ~17.8mm
    waist_outer_h = SG90_cav_H + SG90_turret_H + 4         # ~37.6mm

    waist_block = (
        cq.Workplane("XY")
        .workplane(offset=waist_outer_h / 2)
        .rect(waist_outer_l, waist_outer_w)
        .extrude(waist_outer_h / 2, both=True)
    )
    frame = frame.union(waist_block)

    # ── 3. Torso Column ──────────────────────────────────────────────────
    # Rounded rectangle from Z=0 up to HEAD_PAN_Z
    torso = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .rect(TORSO_D, TORSO_D)
        .extrude(HEAD_PAN_Z)
    )
    # Round the vertical edges
    torso = torso.edges("|Z").fillet(TORSO_R)
    frame = frame.union(torso)

    # ── 4. Shoulder Brackets ──────────────────────────────────────────────
    # Each bracket extends from torso column out to the shoulder position
    bracket_depth = MG90S_cav_L + 2 * T_wall    # Y dimension (~28.4mm)
    bracket_height = MG90S_cav_W + 2 * T_wall   # Z dimension (~17.4mm)

    for sign in [-1, 1]:  # -1 = left, +1 = right
        # Bracket extends from torso edge to shoulder position + some overhang
        inner_x = sign * (TORSO_D / 2 - 2)  # Start 2mm inside torso for overlap
        outer_x = sign * (SHOULDER_X + 15)   # Extend 15mm past servo center
        mid_x = (inner_x + outer_x) / 2
        width = abs(outer_x - inner_x)

        bracket = (
            cq.Workplane("XY")
            .workplane(offset=SHOULDER_Z)
            .center(mid_x, 0)
            .rect(width, bracket_depth)
            .extrude(bracket_height / 2, both=True)
        )
        # Round the ends
        bracket = bracket.edges("|X").fillet(min(2.0, bracket_height / 4))
        frame = frame.union(bracket)

    # ── 5. Head Pan Mount ─────────────────────────────────────────────────
    # Platform at top of torso for pan servo
    pan_mount_l = SG90_tab_L + 2 * C_wall + 2 * T_wall
    pan_mount_w = SG90_cav_W + 2 * T_wall
    pan_mount_h = SG90_cav_H + SG90_turret_H + 4

    pan_mount = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_PAN_Z)
        .rect(pan_mount_l, pan_mount_w)
        .extrude(pan_mount_h)
    )
    frame = frame.union(pan_mount)

    # ── 6. Head Tilt Mount ────────────────────────────────────────────────
    # Bracket above pan servo for tilt servo (rotated 90°: shaft → +Y)
    # Tilt servo body: W along X, L along Z, H along Y
    tilt_mount_x = SG90_cav_W + 2 * T_wall   # ~17.8mm (X)
    tilt_mount_z = SG90_cav_L + 2 * T_wall   # ~28.3mm (Z)
    tilt_mount_y = SG90_cav_H + 2 * T_wall   # ~32.6mm (Y)

    tilt_mount = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_TILT_Z)
        .rect(tilt_mount_x, tilt_mount_y)
        .extrude(tilt_mount_z / 2, both=True)
    )
    frame = frame.union(tilt_mount)

    # Connecting bridge from pan mount top to tilt mount
    bridge_bottom = HEAD_PAN_Z + pan_mount_h
    bridge_top = HEAD_TILT_Z - tilt_mount_z / 2
    if bridge_top > bridge_bottom:
        bridge = (
            cq.Workplane("XY")
            .workplane(offset=bridge_bottom)
            .rect(min(pan_mount_l, tilt_mount_x), min(pan_mount_w, tilt_mount_y))
            .extrude(bridge_top - bridge_bottom)
        )
        frame = frame.union(bridge)

    # ── 7. Head Magnet Ring ───────────────────────────────────────────────
    # Cylindrical ring around the neck area for head shell magnets to grab
    ring_r = 16.0   # Outer radius of the ring
    ring_h = 8.0    # Height of the ring
    ring_z = 122.0  # Just above pan servo
    ring = (
        cq.Workplane("XY")
        .workplane(offset=ring_z)
        .circle(ring_r)
        .extrude(ring_h)
    )
    frame = frame.union(ring)

    # ══════════════════════════════════════════════════════════════════════
    # CUT OPERATIONS — servo pockets, wire channels, magnet pockets, etc.
    # ══════════════════════════════════════════════════════════════════════

    # ── 8. Waist Servo Pocket ─────────────────────────────────────────────
    frame = _sg90_pocket(frame, 0, 0, WAIST_Z - C_wall, shaft_axis="Z")
    frame = _screw_holes_sg90(frame, 0, 0, WAIST_Z - C_wall, shaft_axis="Z")

    # Cable exit slot on the side of waist column
    cable_exit = (
        cq.Workplane("XZ")
        .workplane(offset=-waist_outer_w / 2 - 1)
        .center(waist_outer_l / 2 - 3, WAIST_Z + 5)
        .rect(6, 4)
        .extrude(waist_outer_w + 2)
    )
    frame = frame.cut(cable_exit)

    # ── 9. Shoulder Servo Pockets ─────────────────────────────────────────
    # Left shoulder: shaft points -X
    frame = _mg90s_pocket(frame, -SHOULDER_X, 0, SHOULDER_Z,
                          shaft_axis="X", shaft_sign=-1)
    frame = _screw_holes_mg90s(frame, -SHOULDER_X, 0, SHOULDER_Z, shaft_sign=-1)

    # Right shoulder: shaft points +X
    frame = _mg90s_pocket(frame, SHOULDER_X, 0, SHOULDER_Z,
                          shaft_axis="X", shaft_sign=1)
    frame = _screw_holes_mg90s(frame, SHOULDER_X, 0, SHOULDER_Z, shaft_sign=1)

    # ── 10. Head Pan Servo Pocket ─────────────────────────────────────────
    frame = _sg90_pocket(frame, 0, 0, HEAD_PAN_Z, shaft_axis="Z")
    frame = _screw_holes_sg90(frame, 0, 0, HEAD_PAN_Z, shaft_axis="Z")

    # ── 11. Head Tilt Servo Pocket ────────────────────────────────────────
    frame = _sg90_pocket(frame, 0, 0, HEAD_TILT_Z, shaft_axis="Y")
    frame = _screw_holes_sg90(frame, 0, 0, HEAD_TILT_Z, shaft_axis="Y")

    # ── 12. Pi Pico W Pocket ──────────────────────────────────────────────
    # Cut from bottom face of base plate, centered at X=PICO_X_OFFSET
    pico_pocket = (
        cq.Workplane("XY")
        .workplane(offset=-BASE_H + PICO_H / 2)
        .center(PICO_X_OFFSET, 0)
        .rect(PICO_cavity_L, PICO_cavity_W)
        .extrude(PICO_H / 2, both=True)
    )
    frame = frame.cut(pico_pocket)

    # USB access slot: from Pico pocket right edge to base +X edge
    usb_slot_w = 14.0
    pico_right_edge = PICO_X_OFFSET + PICO_cavity_L / 2
    base_right_edge = BASE_W / 2
    usb_slot_l = base_right_edge - pico_right_edge + 2  # +2 to punch through
    usb_slot = (
        cq.Workplane("XY")
        .workplane(offset=-BASE_H + PICO_H / 2)
        .center(pico_right_edge + usb_slot_l / 2 - 1, 0)
        .rect(usb_slot_l, usb_slot_w)
        .extrude(PICO_H / 2, both=True)
    )
    frame = frame.cut(usb_slot)

    # Pico mounting standoffs (4 posts rising from pocket floor)
    for dx_sign in [-1, 1]:
        for dy_sign in [-1, 1]:
            sx = PICO_X_OFFSET + dx_sign * PICO_hole_L / 2
            sy = dy_sign * PICO_hole_W / 2
            standoff = (
                cq.Workplane("XY")
                .workplane(offset=-BASE_H)
                .center(sx, sy)
                .circle(PICO_standoff_OD / 2)
                .extrude(PICO_standoff_H)
            )
            frame = frame.union(standoff)

            # Pilot hole through standoff
            pilot = (
                cq.Workplane("XY")
                .workplane(offset=-BASE_H)
                .center(sx, sy)
                .circle(PICO_hole_D / 2)
                .extrude(PICO_standoff_H + 1)
            )
            frame = frame.cut(pilot)

    # ── 13. Wire Channels ─────────────────────────────────────────────────
    # Vertical: through torso column, offset from center
    wire_x = TORSO_D / 2 - D_wire / 2 - 1  # Near the surface but inside
    vert_wire = (
        cq.Workplane("XY")
        .workplane(offset=-BASE_H)
        .center(wire_x, 0)
        .circle(D_wire / 2)
        .extrude(BASE_H + HEAD_PAN_Z + 5)
    )
    frame = frame.cut(vert_wire)

    # Horizontal: from torso center to each shoulder at SHOULDER_Z
    for sign in [-1, 1]:
        h_wire = (
            cq.Workplane("YZ")
            .workplane(offset=0)
            .center(0, SHOULDER_Z)
            .circle(D_wire / 2)
            .extrude(sign * (SHOULDER_X + 10))
        )
        frame = frame.cut(h_wire)

    # Pan-to-tilt short wire run
    pan_tilt_wire = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_PAN_Z + SG90_cav_H)
        .center(SG90_cav_L / 2 + 1, 0)
        .circle(2)  # 4mm channel
        .extrude(HEAD_TILT_Z - HEAD_PAN_Z - SG90_cav_H + 5)
    )
    frame = frame.cut(pan_tilt_wire)

    # ── 14. Magnet Pockets ────────────────────────────────────────────────
    all_magnets = (
        HEAD_MAGNETS + TORSO_MAGNETS +
        LEFT_ARM_MAGNETS + RIGHT_ARM_MAGNETS +
        BASE_MAGNETS
    )
    frame = _cut_magnet_pockets(frame, all_magnets)

    # ── 15. Cosmetic Fillets ──────────────────────────────────────────────
    # Add small fillets to major external edges for print quality
    try:
        frame = frame.edges("|Z and (>Z)").fillet(1.5)
    except Exception:
        pass  # Some edges may not be filletable — skip gracefully

    return frame


# ── Export ────────────────────────────────────────────────────────────────

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "skeleton_exports")
    os.makedirs(out_dir, exist_ok=True)

    print("Building skeleton frame...")
    frame = build_skeleton_frame()

    # Export STEP (for SolidWorks / CAD import)
    step_path = os.path.join(out_dir, "spark_skeleton_frame.step")
    cq.exporters.export(frame, step_path)
    print(f"  STEP → {step_path}")

    # Export STL (for 3D printing / pipeline use)
    stl_path = os.path.join(out_dir, "spark_skeleton_frame.stl")
    cq.exporters.export(frame, stl_path, tolerance=0.01, angularTolerance=0.1)
    print(f"  STL  → {stl_path}")

    # Also export a "reference servo" STEP — simple SG90 block for
    # people who don't have the GrabCAD files
    print("\nBuilding reference servo models...")

    sg90_ref = (
        cq.Workplane("XY")
        .box(SG90_L, SG90_W, SG90_H)
        .faces(">Z").workplane()
        .rect(SG90_tab_L, SG90_W)
        .extrude(-(SG90_H - SG90_tab_Z))
        .faces(">Z").workplane()
        .center(SG90_shaft_offset - SG90_L / 2, 0)
        .circle(SG90_turret_D / 2)
        .extrude(SG90_turret_H)
    )
    sg90_path = os.path.join(out_dir, "sg90_reference.step")
    cq.exporters.export(sg90_ref, sg90_path)
    print(f"  SG90  → {sg90_path}")

    mg90s_ref = (
        cq.Workplane("XY")
        .box(MG90S_L, MG90S_W, MG90S_H)
    )
    mg90s_path = os.path.join(out_dir, "mg90s_reference.step")
    cq.exporters.export(mg90s_ref, mg90s_path)
    print(f"  MG90S → {mg90s_path}")

    # Simple magnet cylinder
    magnet_ref = (
        cq.Workplane("XY")
        .circle(3.0)
        .extrude(3.0)
    )
    magnet_path = os.path.join(out_dir, "magnet_6x3_reference.step")
    cq.exporters.export(magnet_ref, magnet_path)
    print(f"  Magnet → {magnet_path}")

    print("\nDone!")
    print(f"Import {step_path} into SolidWorks.")
    print("Reference servo/magnet STEPs can be placed in an assembly for visual check.")


if __name__ == "__main__":
    main()
