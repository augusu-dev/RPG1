#!/usr/bin/env python3
"""Smallest-part kit catalog for Anime Gauntlet Loop Studio.

Each kit is a named assembly of primitive parts (box / cyl / torus / sphere).
Blender (bpy) and the Three.js studio consume the same numbers.

Run:
  python3 kit/catalog.py              # writes kit/catalog.js + kit/catalog.json
  blender --background --python blender/build_kits.py
"""
from __future__ import annotations

import json
import math
import os

# Colors as 0xRRGGBB ints (shared with Three.MeshToonMaterial)
STEEL = 0x3A3A48
STEEL_DK = 0x22222C
CONCRETE = 0x8A8A94
BOLT = 0x2A2A30
LENS = 0xFFE8A0
LENS_E = 0xFFCC66
WOOD = 0x8B5A3A
WOOD_DK = 0x5C3317
CUSHION = 0xC45C5C
GLASS = 0x88C8E8
GLASS_E = 0xFFC878


def P(t, name, p, c, s=None, r=None, r2=None, h=None, e=0, seg=8, rx=0, ry=0, rz=0):
    d = {"t": t, "name": name, "p": list(p), "c": int(c), "e": int(e), "rx": rx, "ry": ry, "rz": rz}
    if s is not None:
        d["s"] = list(s)
    if r is not None:
        d["r"] = r
    if r2 is not None:
        d["r2"] = r2
    if h is not None:
        d["h"] = h
    d["seg"] = seg
    return d


def street_lamp():
    """Cobra-head street lamp from ~14 mechanical parts (footing → lens)."""
    parts = [
        P("cyl", "footing", (0, 0.04, 0), CONCRETE, r=0.22, r2=0.22, h=0.08, seg=10),
        P("cyl", "base_collar", (0, 0.14, 0), STEEL_DK, r=0.11, r2=0.13, h=0.14, seg=8),
        P("cyl", "pole_lower", (0, 1.85, 0), STEEL, r=0.065, r2=0.065, h=3.2, seg=8),
        P("cyl", "mid_ring", (0, 3.48, 0), STEEL_DK, r=0.085, r2=0.085, h=0.07, seg=8),
        P("cyl", "pole_upper", (0, 4.2, 0), STEEL, r=0.05, r2=0.048, h=1.35, seg=8),
        P("box", "arm_bracket", (0, 4.9, 0.02), STEEL_DK, s=(0.14, 0.12, 0.16)),
        P("box", "arm", (0, 4.9, 0.55), STEEL, s=(0.055, 0.055, 1.05)),
        P("box", "conduit", (0.07, 4.62, 0.2), STEEL_DK, s=(0.02, 0.45, 0.02)),
        P("box", "housing", (0, 4.82, 1.12), STEEL_DK, s=(0.32, 0.13, 0.42)),
        P("box", "visor", (0, 4.91, 1.12), STEEL_DK, s=(0.36, 0.03, 0.46)),
        P("box", "lens", (0, 4.74, 1.12), LENS, s=(0.24, 0.04, 0.32), e=LENS_E),
        P("cyl", "bulb", (0, 4.76, 1.12), 0xFFF4C2, r=0.05, r2=0.05, h=0.06, e=0xFFE088, seg=8),
    ]
    for i in range(4):
        a = i * math.pi * 0.5 + 0.4
        parts.append(P("cyl", "bolt_%d" % i, (math.cos(a) * 0.15, 0.09, math.sin(a) * 0.15), BOLT, r=0.018, r2=0.018, h=0.02, seg=6))
    return {"sit": False, "parts": parts}


def chair():
    """Cafe chair: 4 legs, stretchers, seat board, cushion, back posts, slats, top rail."""
    parts = []
    for nx, nz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        parts.append(P("cyl", "leg_%d%d" % (nx, nz), (nx * 0.18, 0.23, nz * 0.18), WOOD_DK, r=0.022, r2=0.02, h=0.46, seg=6))
    parts += [
        P("box", "stretcher_w", (0, 0.14, 0), WOOD_DK, s=(0.34, 0.02, 0.02)),
        P("box", "stretcher_d", (0, 0.14, 0), WOOD_DK, s=(0.02, 0.02, 0.34)),
        P("box", "seat_board", (0, 0.47, 0), WOOD, s=(0.42, 0.04, 0.42)),
        P("box", "cushion", (0, 0.52, 0), CUSHION, s=(0.4, 0.05, 0.4)),
        P("cyl", "back_L", (-0.18, 0.78, -0.18), WOOD_DK, r=0.018, r2=0.018, h=0.64, seg=6),
        P("cyl", "back_R", (0.18, 0.78, -0.18), WOOD_DK, r=0.018, r2=0.018, h=0.64, seg=6),
        P("box", "slat_1", (0, 0.72, -0.18), WOOD, s=(0.34, 0.04, 0.02)),
        P("box", "slat_2", (0, 0.86, -0.18), WOOD, s=(0.34, 0.04, 0.02)),
        P("box", "slat_3", (0, 1.0, -0.18), WOOD, s=(0.34, 0.04, 0.02)),
        P("box", "top_rail", (0, 1.12, -0.18), WOOD, s=(0.4, 0.04, 0.03)),
        P("box", "back_pad", (0, 0.88, -0.15), CUSHION, s=(0.32, 0.28, 0.03)),
    ]
    return {"sit": True, "sitOffset": [0, 0.52, 0.02], "parts": parts}


def sofa():
    parts = [
        P("box", "plinth", (0, 0.12, 0), WOOD_DK, s=(1.42, 0.1, 0.62)),
        P("box", "seat", (0, 0.32, 0.04), 0x4A6FA5, s=(1.36, 0.16, 0.5)),
        P("box", "back", (0, 0.55, -0.24), 0x3D5A86, s=(1.36, 0.42, 0.14)),
        P("box", "arm_L", (-0.68, 0.42, 0), 0x3D5A86, s=(0.1, 0.28, 0.58)),
        P("box", "arm_R", (0.68, 0.42, 0), 0x3D5A86, s=(0.1, 0.28, 0.58)),
        P("box", "pillow_L", (-0.38, 0.48, -0.08), 0xE8D5A3, s=(0.28, 0.16, 0.18)),
        P("box", "pillow_R", (0.38, 0.48, -0.08), 0xE8D5A3, s=(0.28, 0.16, 0.18)),
    ]
    return {"sit": True, "sitOffset": [0, 0.42, 0.06], "parts": parts}


def desk():
    return {"sit": False, "parts": [
        P("box", "top", (0, 0.74, 0), 0xD4C4A8, s=(1.2, 0.05, 0.6)),
        P("box", "leg_L", (-0.52, 0.36, 0), WOOD_DK, s=(0.06, 0.72, 0.54)),
        P("box", "leg_R", (0.52, 0.36, 0), WOOD_DK, s=(0.06, 0.72, 0.54)),
        P("box", "drawer", (0.2, 0.58, 0.22), WOOD, s=(0.4, 0.12, 0.18)),
        P("cyl", "knob", (0.2, 0.58, 0.32), 0xC0A060, r=0.02, r2=0.02, h=0.03, seg=6),
        P("box", "monitor", (0, 0.98, -0.12), 0x222, s=(0.46, 0.28, 0.04), e=0x446688),
        P("box", "stand", (0, 0.8, -0.12), 0x333, s=(0.1, 0.08, 0.08)),
    ]}


def vending():
    return {"kind": "vend", "parts": [
        P("box", "cabinet", (0, 1.05, 0), 0x1A4AA8, s=(1.05, 2.1, 0.78), e=0x2266CC),
        P("box", "bezel", (0, 1.2, 0.4), STEEL_DK, s=(0.92, 1.5, 0.04)),
        P("box", "glass", (0, 1.25, 0.43), 0xFF6699, s=(0.82, 1.32, 0.03), e=0xFF88AA),
        P("box", "can_1", (-0.2, 1.35, 0.38), 0xFF3344, s=(0.12, 0.22, 0.12), e=0xFF5566),
        P("box", "can_2", (0.05, 1.35, 0.38), 0x33CCFF, s=(0.12, 0.22, 0.12), e=0x66DDFF),
        P("box", "can_3", (0.28, 1.35, 0.38), 0xFFE066, s=(0.12, 0.22, 0.12), e=0xFFEE88),
        P("box", "coin_slot", (0.32, 0.55, 0.41), 0xDDD, s=(0.1, 0.04, 0.02)),
        P("box", "dispense", (0, 0.22, 0.42), STEEL_DK, s=(0.7, 0.16, 0.06)),
        P("box", "logo", (0, 1.95, 0.41), 0xFFFFFF, s=(0.7, 0.12, 0.02), e=0x88DDFF),
    ]}


def tree():
    return {"parts": [
        P("cyl", "trunk", (0, 0.7, 0), 0x5C3317, r=0.12, r2=0.16, h=1.4, seg=7),
        P("sphere", "crown_a", (0, 1.85, 0), 0x3D8C4A, r=0.7, seg=8),
        P("sphere", "crown_b", (0.25, 2.05, 0.1), 0x4CA05A, r=0.5, seg=8),
        P("sphere", "crown_c", (-0.2, 2.15, -0.15), 0x2E7A3C, r=0.45, seg=8),
    ]}


def elevator_door():
    return {"kind": "elev", "parts": [
        P("box", "frame", (0, 1.2, 0), 0x8899AA, s=(1.7, 2.45, 0.12)),
        P("box", "leaf_L", (-0.35, 1.15, 0.04), 0xC0CAD4, s=(0.62, 2.2, 0.06)),
        P("box", "leaf_R", (0.35, 1.15, 0.04), 0xC0CAD4, s=(0.62, 2.2, 0.06)),
        P("box", "sill", (0, 0.04, 0.08), STEEL, s=(1.5, 0.06, 0.2)),
        P("box", "display", (0, 2.28, 0.08), 0x111, s=(0.35, 0.12, 0.04), e=0x66FF99),
        P("box", "btn_up", (0.78, 1.35, 0.06), 0xEEE, s=(0.08, 0.08, 0.04)),
        P("box", "btn_dn", (0.78, 1.18, 0.06), 0xEEE, s=(0.08, 0.08, 0.04)),
    ]}


def railing():
    return {"parts": [
        P("cyl", "post", (0, 0.55, 0), STEEL, r=0.03, r2=0.03, h=1.1, seg=6),
        P("box", "rail_top", (0.5, 1.08, 0), STEEL, s=(1.02, 0.04, 0.04)),
        P("box", "rail_mid", (0.5, 0.62, 0), STEEL, s=(1.02, 0.025, 0.025)),
    ]}


def car_kei():
    return {"parts": [
        P("box", "body", (0, 0.55, 0), 0xFF6688, s=(1.55, 0.7, 2.9)),
        P("box", "cabin", (0, 1.12, -0.15), 0x88D0FF, s=(1.4, 0.5, 1.4)),
        P("cyl", "wheel_fl", (0.72, 0.28, 0.85), STEEL_DK, r=0.28, r2=0.28, h=0.18, seg=8, rz=1.57),
        P("cyl", "wheel_fr", (-0.72, 0.28, 0.85), STEEL_DK, r=0.28, r2=0.28, h=0.18, seg=8, rz=1.57),
        P("cyl", "wheel_rl", (0.72, 0.28, -0.85), STEEL_DK, r=0.28, r2=0.28, h=0.18, seg=8, rz=1.57),
        P("cyl", "wheel_rr", (-0.72, 0.28, -0.85), STEEL_DK, r=0.28, r2=0.28, h=0.18, seg=8, rz=1.57),
        P("box", "head_L", (0.45, 0.55, 1.46), 0xFFFFCC, s=(0.22, 0.1, 0.06), e=0xFFE088),
        P("box", "head_R", (-0.45, 0.55, 1.46), 0xFFFFCC, s=(0.22, 0.1, 0.06), e=0xFFE088),
        P("box", "tail_L", (0.45, 0.58, -1.46), 0xFF3344, s=(0.22, 0.08, 0.05), e=0xFF2244),
        P("box", "tail_R", (-0.45, 0.58, -1.46), 0xFF3344, s=(0.22, 0.08, 0.05), e=0xFF2244),
        P("box", "mirror_L", (0.82, 1.05, 0.5), STEEL, s=(0.08, 0.08, 0.14)),
        P("box", "mirror_R", (-0.82, 1.05, 0.5), STEEL, s=(0.08, 0.08, 0.14)),
    ]}


KITS = {
    "street_lamp": street_lamp(),
    "chair": chair(),
    "sofa": sofa(),
    "desk": desk(),
    "vending": vending(),
    "tree": tree(),
    "elevator_door": elevator_door(),
    "railing": railing(),
    "car_kei": car_kei(),
}


def emit(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "catalog.json")
    js_path = os.path.join(out_dir, "catalog.js")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(KITS, f, ensure_ascii=False)
    # No template braces-in-strings issues: JSON dump is a single assignment.
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.KITS = ")
        json.dump(KITS, f, ensure_ascii=False)
        f.write(";\n")
    n = sum(len(k["parts"]) for k in KITS.values())
    print("kits=%d parts=%d -> %s %s" % (len(KITS), n, json_path, js_path))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    emit(here)
