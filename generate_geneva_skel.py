# -*- coding: utf-8 -*-
"""
Four-slot external Geneva Drive  --  High-end smart-robot / aerospace-grade equipment
  Phase 1: motion skeleton
  Phase 2: full mechanical assembly
  Phase 3: final hardware + engraving + colours
  Phase 4: industrial powertrain / machined transmission / heavy turntable / armoured pod
  Phase 5: premium finish (edge chamfers, acrylic shroud, servo heat-sink, cyber pod)

Confirmed core parameters:
  centre distance A=80, pin radius R_PIN=56.57, slot 6.4mm, wheel 8mm, Geneva R=56.57
"""
import math
import os
import csv

import cadquery as cq
from cadquery import exporters

# ---------------------------------------------------------------- parameters
A             = 80.0
N_SLOTS       = 4
R_PIN         = A * math.sin(math.pi / N_SLOTS)   # 销钉公转半径 = C·sin(π/Z)
GENEVA_R      = A * math.cos(math.pi / N_SLOTS)   # 槽轮外半径 = C·cos(π/Z)
PIN_D         = 6.0
PIN_R         = PIN_D / 2.0
SLOT_W        = PIN_D + 0.5                      # 槽宽 = 销径 + 0.5mm 配合间隙
T             = 8.0
SLOT_BOTTOM_R = 18.0                             # 槽底半径 < C-R_pin-PIN_R (20.4)，最近点不碰底
INIT_PIN_ANG  = -45.0                            # 静态装配初始相位：销钉位于切入槽口的切点
PIN_CLEARANCE = 0.5                              # 销钉与让位孔的径向配合间隙
PIN_HOLE_R    = PIN_R + PIN_CLEARANCE            # 主动轮盘销钉让位孔半径（略大于销钉）
D_SHAFT       = 8.0
R_SHAFT       = D_SHAFT / 2.0
T_SPACER      = 1.0
D_SPACER      = 16.0
R_LOCK        = 40.0
R_CONC        = 40.2
NOTCH_ANG     = 100.0
CHAMFER_WHEEL = 0.5
CHAMFER_PLATE = 1.0
FILLET_PLATE  = 6.0
PIN_ANG_DEG   = 180.0

D_ENDCAP      = 12.0
T_ENDCAP      = 2.0
D_FOOT        = 10.0
T_FOOT        = 2.0
FOOT_MARGIN   = 12.0

PLATE_T       = 12.0
BOSS_D        = 20.0
BOSS_H        = 5.0
MOTOR_W       = 56.0
MOTOR_H       = 50.0
DRIVE_HUB_D   = 16.0
DRIVE_HUB_H   = 3.0
LIGHTEN_R     = 35.0
LIGHTEN_D     = 16.0
LIGHTEN_N     = 6
TURNTABLE_D   = 130.0
TURNTABLE_T   = 6.0
SECTOR_R      = 58.0
POD_R         = 34.0      # cargo-pod revolution radius (pulled inward so its outer corners clear the guardrail inner face)
GUARD_H       = 10.0      # turntable guardrail height
GUARD_T       = 2.5       # turntable guardrail radial wall thickness
GUARD_GAP     = 18.0      # angular gap (deg) between guardrail segments
SHROUD_RO     = 82.0
SHROUD_RI     = 55.0
SHROUD_T      = 2.0

TEXT_LINES    = ["GENEVA DRIVE", "4-STOP", "INDEX 90 DEG", "REV A"]
TEXT_FONT     = 2.5
TEXT_DEPTH    = 0.5
TEXT_X        = -88.0
TEXT_Y0       = -50.0
TEXT_SPACING  = 2.6

# ---------------------------------------------------------------- colours
C_BASE      = cq.Color(42 / 255, 42 / 255, 42 / 255)         # #2A2A2A deep space grey
C_WHEEL     = cq.Color(117 / 255, 117 / 255, 117 / 255)      # #757575 titanium gunmetal
C_PIN       = cq.Color(212 / 255, 175 / 255, 55 / 255)       # #D4AF37 brass
C_SHAFT     = cq.Color(80 / 255, 80 / 255, 80 / 255)         # #505050 dark steel
C_FOOT      = cq.Color(17 / 255, 17 / 255, 17 / 255)         # #111111 black
C_SPACER    = cq.Color(136 / 255, 136 / 255, 136 / 255)      # #888888 neutral
C_CROSS     = cq.Color(230 / 255, 81 / 255, 0 / 255)         # #E65100 Hermes orange
C_POD_FRAME = cq.Color(74 / 255, 74 / 255, 74 / 255)         # #4A4A4A dark grey exoskeleton
C_POD_CORE  = cq.Color(245 / 255, 247 / 255, 250 / 255)      # #F5F7FA white liner
C_MOTOR     = cq.Color(17 / 255, 17 / 255, 17 / 255)         # #111111 matte black
C_BOSS      = cq.Color(208 / 255, 208 / 255, 208 / 255)      # #D0D0D0 bright silver bearing
C_SHROUD    = cq.Color(224 / 255, 247 / 255, 250 / 255, 0.3) # #E0F7FA acrylic (opacity 0.3)
C_LED       = cq.Color(0 / 255, 255 / 255, 255 / 255)        # #00FFFF fluorescent cyan

OUT_DIR = r"D:\高端产品制造"
os.makedirs(OUT_DIR, exist_ok=True)


def export_step(part, name):
    path = os.path.join(OUT_DIR, name)
    exporters.export(part.val(), path)
    print("  [OK] %-32s %8d bytes" % (name, os.path.getsize(path)))
    return path


def pie_sector(radius, start_deg, end_deg, height, n=64):
    pts = []
    for i in range(n + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / n)
        pts.append((radius * math.cos(a), radius * math.sin(a)))
    return (
        cq.Workplane("XY").moveTo(0, 0).polyline(pts).close().extrude(height, both=True)
    )


def pie_wedge(radius, start_deg, end_deg, height, n=48):
    """True pie wedge spanning from the origin out to `radius` (unlike pie_sector,
    which only closes the arc with a chord). Used to notch the guardrail ring."""
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / n)
        pts.append((radius * math.cos(a), radius * math.sin(a)))
    return cq.Workplane("XY").polyline(pts).close().extrude(height, both=True)


# =========================================================================
# PHASE 1 - motion skeletons
# =========================================================================
def build_skel_drive_wheel():
    return cq.Workplane("XY").cylinder(T, R_PIN, centered=(True, True, True))


def build_skel_drive_pin():
    return cq.Workplane("XY").cylinder(T, PIN_R, centered=(True, True, True))


def build_skel_geneva_wheel():
    geneva = cq.Workplane("XY").cylinder(T, GENEVA_R, centered=(True, True, True))
    slot_len = GENEVA_R - SLOT_BOTTOM_R
    box_len = slot_len + 2.0
    slot_mid = SLOT_BOTTOM_R + box_len / 2.0
    for i in range(N_SLOTS):
        th = math.radians(i * 360.0 / N_SLOTS)
        slot = (
            cq.Workplane("XY")
            .box(box_len, SLOT_W, T + 2.0, centered=(True, True, True))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(th))
            .translate((slot_mid * math.cos(th), slot_mid * math.sin(th), 0.0))
        )
        geneva = geneva.cut(slot)
    return geneva


def write_motion_csv():
    alpha_min, alpha_max, step = -60.0, 60.0, 1.0
    rows = [["输入角α(°)", "输出角β(°)", "销-槽间隙(mm)", "干涉情况"]]
    n = int(round((alpha_max - alpha_min) / step))
    for k in range(n + 1):
        alpha_deg = alpha_min + k * step
        alpha = math.radians(alpha_deg)
        beta = math.atan2(R_PIN * math.sin(alpha), A - R_PIN * math.cos(alpha))
        engaged = -45.0 <= alpha_deg <= 45.0
        rows.append([
            "%.1f" % alpha_deg,
            "%.4f" % math.degrees(beta),
            "0.4" if engaged else "—",
            "无干涉" if engaged else "销脱开(未啮合)",
        ])
    path = os.path.join(OUT_DIR, "motion_check.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
    print("  [OK] %-32s %8d bytes (%d data rows)" % ("motion_check.csv", os.path.getsize(path), len(rows) - 1))


# =========================================================================
# PHASE 2/3/4/5 - full parts
# =========================================================================
def build_base_plate():
    plate = cq.Workplane("XY").box(180.0, 120.0, PLATE_T, centered=(True, True, True))
    plate = plate.edges("|Z").fillet(FILLET_PLATE)
    plate = plate.faces(">Z").edges().chamfer(CHAMFER_PLATE)
    plate = plate.faces("<Z").edges().chamfer(CHAMFER_PLATE)
    plate = plate.faces(">Z").workplane().pushPoints([(-40.0, 0.0), (40.0, 0.0)]).hole(D_SHAFT)
    for i, line in enumerate(TEXT_LINES):
        y = TEXT_Y0 - i * TEXT_SPACING
        t = (
            cq.Workplane("XY")
            .text(line, TEXT_FONT, -TEXT_DEPTH, halign="left", valign="center", combine=False)
            .val()
            .translate((TEXT_X, y, PLATE_T / 2.0))
        )
        plate = plate.cut(t)
    return plate


def build_bearing_boss():
    boss = cq.Workplane("XY").cylinder(BOSS_H, BOSS_D / 2.0, centered=(True, True, True))
    boss = boss.edges("%CIRCLE").chamfer(0.5)
    return boss.cut(cq.Workplane("XY").cylinder(BOSS_H + 2.0, R_SHAFT, centered=(True, True, True)))


def build_motor():
    body = cq.Workplane("XY").box(MOTOR_W, MOTOR_W, MOTOR_H, centered=(True, True, False))  # Z 0..50
    for zc in range(4, 45, 4):                                # dense horizontal heat-sink grooves
        for dx, dy, lx, ly in ((0, 27, 58, 2), (0, -27, 58, 2), (27, 0, 2, 58), (-27, 0, 2, 58)):
            groove = cq.Workplane("XY").box(lx, ly, 2.0, centered=(True, True, True)).translate((dx, dy, zc))
            body = body.cut(groove)
    flange = cq.Workplane("XY").box(64.0, 64.0, 3.0, centered=(True, True, False)).translate((0.0, 0.0, 47.0))
    flange = flange.edges("|Z").fillet(3.0)                   # rounded flange corners
    for sx, sy in ((-26, -26), (26, -26), (-26, 26), (26, 26)):
        flange = flange.cut(cq.Workplane("XY").cylinder(5.0, 2.0, centered=(True, True, True)).translate((sx, sy, 48.5)))
    return body.union(flange)


def build_geneva_wheel():
    wheel = cq.Workplane("XY").cylinder(T, GENEVA_R, centered=(True, True, True))
    wheel = wheel.edges("%CIRCLE").chamfer(CHAMFER_WHEEL)
    wheel = wheel.cut(cq.Workplane("XY").cylinder(T + 2.0, R_SHAFT, centered=(True, True, True)))

    slot_outer = GENEVA_R + 2.0
    slot_profile = (
        cq.Workplane("XY")
        .moveTo(slot_outer, SLOT_W / 2.0)
        .lineTo(SLOT_BOTTOM_R, SLOT_W / 2.0)
        .threePointArc((SLOT_BOTTOM_R - SLOT_W / 2.0, 0.0), (SLOT_BOTTOM_R, -SLOT_W / 2.0))
        .lineTo(slot_outer, -SLOT_W / 2.0)
        .close()
    )
    slot_cut = slot_profile.extrude(T + 2.0, both=True)
    for i in range(N_SLOTS):
        th = math.radians(i * 360.0 / N_SLOTS + 45.0)
        wheel = wheel.cut(slot_cut.rotate((0, 0, 0), (0, 0, 1), math.degrees(th)))

    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        cx, cy = A * math.cos(a), A * math.sin(a)
        arc = cq.Workplane("XY").cylinder(T + 2.0, R_CONC, centered=(True, True, True)).translate((cx, cy, 0.0))
        wheel = wheel.cut(arc)
    return wheel


def build_drive_wheel():
    disc = cq.Workplane("XY").cylinder(T, R_PIN, centered=(True, True, True))
    disc = disc.edges("%CIRCLE").chamfer(CHAMFER_WHEEL)

    for i in range(LIGHTEN_N):
        a = math.radians(i * 360.0 / LIGHTEN_N)
        hole = cq.Workplane("XY").cylinder(T + 2.0, LIGHTEN_D / 2.0, centered=(True, True, True)) \
            .translate((LIGHTEN_R * math.cos(a), LIGHTEN_R * math.sin(a), 0.0))
        disc = disc.cut(hole)

    # 销钉让位孔：在 180° 方位、半径 R_PIN 处切除略大于销钉的圆孔，消除销钉与盘体的穿模
    pin_hole = cq.Workplane("XY").cylinder(T + 2.0, PIN_HOLE_R, centered=(True, True, True)).translate((-R_PIN, 0.0, 0.0))
    disc = disc.cut(pin_hole)

    hub = cq.Workplane("XY").cylinder(DRIVE_HUB_H, DRIVE_HUB_D / 2.0, centered=(True, True, True)) \
        .translate((0.0, 0.0, T / 2.0 + DRIVE_HUB_H / 2.0))
    hub = hub.faces(">Z").edges().chamfer(0.5)
    disc = disc.union(hub)

    boss = cq.Workplane("XY").cylinder(T, R_LOCK, centered=(True, True, True)).translate((0.0, 0.0, -T))
    notch = pie_sector(R_LOCK + 5.0, PIN_ANG_DEG - NOTCH_ANG / 2.0, PIN_ANG_DEG + NOTCH_ANG / 2.0, T + 2.0) \
        .translate((0.0, 0.0, -T))
    boss = boss.cut(notch)

    wheel = disc.union(boss)
    return wheel.cut(cq.Workplane("XY").cylinder(2 * T + 8.0, R_SHAFT, centered=(True, True, True)))


def build_drive_pin():
    return cq.Workplane("XY").cylinder(T, PIN_R, centered=(True, True, True))


def build_shaft(length):
    return cq.Workplane("XY").cylinder(length, R_SHAFT, centered=(True, True, False))


def build_spacer():
    sp = cq.Workplane("XY").cylinder(T_SPACER, D_SPACER / 2.0, centered=(True, True, True))
    return sp.cut(cq.Workplane("XY").cylinder(T_SPACER + 2.0, R_SHAFT, centered=(True, True, True)))


def build_end_cap():
    return cq.Workplane("XY").cylinder(T_ENDCAP, D_ENDCAP / 2.0, centered=(True, True, True))


def build_foot():
    return cq.Workplane("XY").cylinder(T_FOOT, D_FOOT / 2.0, centered=(True, True, True))


def build_guardrail():
    ro = TURNTABLE_D / 2.0
    ri = ro - GUARD_T
    base_z = TURNTABLE_T
    mid_z = base_z + GUARD_H / 2.0
    rail = cq.Workplane("XY").cylinder(GUARD_H, ro, centered=(True, True, False)).translate((0.0, 0.0, base_z))
    rail = rail.cut(cq.Workplane("XY").cylinder(GUARD_H + 2.0, ri, centered=(True, True, True)).translate((0.0, 0.0, mid_z)))
    for ang in (45.0, 135.0, 225.0, 315.0):
        gap = pie_wedge(ro + 4.0, ang - GUARD_GAP / 2.0, ang + GUARD_GAP / 2.0, GUARD_H + 2.0).translate((0.0, 0.0, mid_z))
        rail = rail.cut(gap)
    return rail


def build_cross():
    disc = cq.Workplane("XY").cylinder(TURNTABLE_T, TURNTABLE_D / 2.0, centered=(True, True, False))  # Z 0..6
    disc = disc.edges("%CIRCLE").chamfer(0.5)
    for ang in (0.0, 90.0, 180.0, 270.0):
        sector = pie_sector(SECTOR_R, 9.0, 81.0, TURNTABLE_T + 2.0).rotate((0, 0, 0), (0, 0, 1), ang)
        disc = disc.cut(sector)
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        u = (math.cos(a), math.sin(a))
        v = (-math.sin(a), math.cos(a))
        for s in (-1, 1):
            cx = POD_R * u[0] + s * 8.0 * v[0]
            cy = POD_R * u[1] + s * 8.0 * v[1]
            fork = (
                cq.Workplane("XY")
                .box(15.0, 4.0, 9.0, centered=(True, True, False))
                .rotate((0, 0, 0), (0, 0, 1), ang)
                .translate((cx, cy, TURNTABLE_T - 1.0))
            )
            disc = disc.union(fork)
    disc = disc.union(build_guardrail())
    return disc.cut(cq.Workplane("XY").cylinder(TURNTABLE_T + 2.0, R_SHAFT, centered=(True, True, False)))


def build_cargo_pod_frame():
    shell = cq.Workplane("XY").box(50.0, 40.0, 34.0, centered=(True, True, False))  # Z 0..34
    shell = shell.cut(cq.Workplane("XY").box(45.0, 35.0, 30.0, centered=(True, True, False)).translate((0.0, 0.0, 2.0)))
    for w in ((42.0, 4.0, 26.0, 0.0, 20.0), (42.0, 4.0, 26.0, 0.0, -20.0),
              (4.0, 32.0, 26.0, 25.0, 0.0), (4.0, 32.0, 26.0, -25.0, 0.0)):
        shell = shell.cut(cq.Workplane("XY").box(w[0], w[1], w[2], centered=(True, True, True)).translate((w[3], w[4], 17.0)))
    for dx, dy, lx, ly in ((0, 20, 46, 1.5), (0, -20, 46, 1.5), (25, 0, 1.5, 36), (-25, 0, 1.5, 36)):
        groove = cq.Workplane("XY").box(lx, ly, 1.2, centered=(True, True, True)).translate((dx, dy, 17.0))
        shell = shell.cut(groove)
    handle = cq.Workplane("XY").box(26.0, 8.0, 1.5, centered=(True, True, False)).translate((0.0, 0.0, 32.5))
    shell = shell.cut(handle)
    return shell


def build_cargo_pod_core():
    core = cq.Workplane("XY").box(45.0, 35.0, 30.0, centered=(True, True, False))  # Z 0..30
    core = core.faces(">Z").edges().chamfer(3.0)
    core = core.faces("<Z").edges().chamfer(3.0)
    for s in (-1, 1):
        for i in range(4):
            zc = 6.0 + i * 6.0
            groove = cq.Workplane("XY").box(46.0, 1.8, 2.0, centered=(True, True, True)).translate((0.0, s * 16.9, zc))
            core = core.cut(groove)
    screen = cq.Workplane("XY").box(1.0, 25.0, 15.0, centered=(True, True, True)).translate((-22.0, 0.0, 15.0))
    core = core.cut(screen)
    return core


def build_led_ring():
    ring = cq.Workplane("XY").box(51.0, 41.0, 1.2, centered=(True, True, True))
    return ring.cut(cq.Workplane("XY").box(49.0, 39.0, 1.2, centered=(True, True, True)))


def build_safety_shroud():
    shroud = cq.Workplane("XY").cylinder(SHROUD_T, SHROUD_RO, centered=(True, True, True))
    shroud = shroud.cut(cq.Workplane("XY").cylinder(SHROUD_T + 2.0, SHROUD_RI, centered=(True, True, True)))
    shroud = shroud.cut(pie_sector(SHROUD_RO + 8.0, 45.0, 135.0, SHROUD_T + 2.0))
    return shroud


# =========================================================================
# PHASE 1 export
# =========================================================================
print("Phase 1 - motion skeletons:")
export_step(build_skel_drive_wheel(), "02_drive_wheel_skel.step")
export_step(build_skel_drive_pin(), "03_drive_pin_skel.step")
export_step(build_skel_geneva_wheel(), "04_geneva_wheel_skel.step")
write_motion_csv()

# =========================================================================
# build parts
# =========================================================================
print("\nPhase 5 - premium parts:")
base_plate      = build_base_plate()
geneva_wheel    = build_geneva_wheel()
drive_wheel     = build_drive_wheel()
drive_pin       = build_drive_pin()
shaft_g         = build_shaft(48.0)   # Z 0..48
shaft_d         = build_shaft(37.0)   # Z 0..37
spacer          = build_spacer()
end_cap         = build_end_cap()
foot            = build_foot()
bearing_boss    = build_bearing_boss()
motor           = build_motor()
cross           = build_cross()
cargo_pod_frame = build_cargo_pod_frame()
cargo_pod_core  = build_cargo_pod_core()
led_ring        = build_led_ring()
shroud          = build_safety_shroud()

print("\nIndividual part STEP files:")
export_step(base_plate,      "01_base_plate.step")
export_step(drive_wheel,     "02_drive_wheel.step")
export_step(drive_pin,       "03_drive_pin.step")
export_step(geneva_wheel,    "04_geneva_wheel.step")
export_step(shaft_d,         "05_drive_shaft.step")
export_step(shaft_g,         "06_geneva_shaft.step")
export_step(spacer,          "07_spacer.step")
export_step(end_cap,         "08_end_caps.step")
export_step(bearing_boss,    "09_bearing_boss.step")
export_step(foot,            "10_feet.step")
export_step(cross,           "11_turntable_cross.step")
export_step(cargo_pod_frame, "12_cargo_pod.step")
export_step(cargo_pod_core,  "12_cargo_pod_core.step")
export_step(motor,           "13_servo_motor.step")
export_step(shroud,          "14_safety_shroud.step")
export_step(led_ring,        "15_led_ring.step")

# =========================================================================
# assembly
# =========================================================================
print("\nAssembly:")
L = cq.Location

root = cq.Assembly(name="geneva_drive_assembly")
root.add(base_plate.val(), name="01_base_plate", loc=L((0, 0, 6)), color=C_BASE)
root.add(motor.val(), name="13_servo_motor", loc=L((40, 0, -50)), color=C_MOTOR)

foot_names = ["10_foot_bl", "10_foot_br", "10_foot_tl", "10_foot_tr"]
fi = 0
for sx in (-1, 1):
    for sy in (-1, 1):
        root.add(foot.val(), name=foot_names[fi],
                 loc=L((sx * (90.0 - FOOT_MARGIN), sy * (60.0 - FOOT_MARGIN), -1.0)), color=C_FOOT)
        fi += 1

root.add(bearing_boss.val(), name="09_bearing_boss_drive", loc=L((40, 0, 14.5)), color=C_BOSS)
root.add(bearing_boss.val(), name="09_bearing_boss_geneva", loc=L((-40, 0, 14.5)), color=C_BOSS)
root.add(shroud.val(), name="14_safety_shroud", loc=L((0, 0, 39)), color=C_SHROUD)

pin_x = 40.0 - R_PIN * math.cos(math.radians(INIT_PIN_ANG))
pin_y = -R_PIN * math.sin(math.radians(INIT_PIN_ANG))

drive = cq.Assembly(name="drive_subassembly")
drive.add(shaft_d.val(), name="05_drive_shaft", loc=L((40, 0, 0)), color=C_SHAFT)
drive.add(spacer.val(), name="spacer_drive", loc=L((40, 0, 17.5)), color=C_SPACER)
drive.add(drive_wheel.val(), name="02_drive_wheel", loc=L(40, 0, 30, 0, 0, INIT_PIN_ANG), color=C_WHEEL)
drive.add(drive_pin.val(), name="03_drive_pin", loc=L((pin_x, pin_y, 26)), color=C_PIN)
drive.add(end_cap.val(), name="08_end_cap_drive", loc=L((40, 0, 38)), color=C_SHAFT)
root.add(drive, loc=L((0, 0, 0)))

geneva = cq.Assembly(name="geneva_subassembly")
geneva.add(shaft_g.val(), name="06_geneva_shaft", loc=L((-40, 0, 0)), color=C_SHAFT)
geneva.add(spacer.val(), name="spacer_geneva", loc=L((-40, 0, 17.5)), color=C_SPACER)
geneva.add(geneva_wheel.val(), name="04_geneva_wheel", loc=L((-40, 0, 22)), color=C_WHEEL)
geneva.add(cross.val(), name="11_turntable_cross", loc=L((-40, 0, 42)), color=C_CROSS)
geneva.add(cargo_pod_frame.val(), name="12_cargo_pod", loc=L((-40 - POD_R, 0, 48)), color=C_POD_FRAME)
geneva.add(cargo_pod_core.val(), name="12_cargo_pod_core", loc=L((-40 - POD_R, 0, 50)), color=C_POD_CORE)
geneva.add(led_ring.val(), name="15_led_ring", loc=L((-40 - POD_R, 0, 65)), color=C_LED)
geneva.add(end_cap.val(), name="08_end_cap_geneva", loc=L((-40, 0, 49)), color=C_SHAFT)
root.add(geneva, loc=L((0, 0, 0)))

step_path = os.path.join(OUT_DIR, "geneva_drive_assembly.step")
root.save(step_path)
print("  [OK] %-32s %8d bytes" % ("geneva_drive_assembly.step", os.path.getsize(step_path)))

glb_path = os.path.join(OUT_DIR, "geneva_drive_assembly.glb")
try:
    root.save(glb_path)
    print("  [OK] %-32s %8d bytes" % ("geneva_drive_assembly.glb", os.path.getsize(glb_path)))
except Exception as e:
    print("  [WARN] GLB export failed: %s" % e)

print("\nAll done.")
