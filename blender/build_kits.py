#!/usr/bin/env python3
"""Assemble kits from kit/catalog.py into Blender objects (smallest parts).

  blender --background --python blender/build_kits.py

If bpy is missing, this still validates the catalog and prints the part tree.
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from kit.catalog import KITS, emit  # noqa: E402

try:
    import bpy
    from mathutils import Euler, Vector
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def hex_color(n):
    r = ((n >> 16) & 255) / 255.0
    g = ((n >> 8) & 255) / 255.0
    b = (n & 255) / 255.0
    return (r, g, b, 1.0)


def build_kit_bpy(name, kit, origin):
    col = bpy.data.collections.new("KIT_" + name)
    bpy.context.scene.collection.children.link(col)
    empty = bpy.data.objects.new(name, None)
    empty.location = origin
    col.objects.link(empty)
    for i, p in enumerate(kit["parts"]):
        t = p["t"]
        mesh_name = "%s_%s" % (name, p["name"])
        if t == "box":
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
            obj = bpy.context.active_object
            sx, sy, sz = p["s"]
            # Blender Z-up vs Three Y-up: catalog is Three.js Y-up (x,y,z).
            # Map (x, y, z) Three -> (x, z, y) Blender.
            obj.scale = (sx, sz, sy)
        elif t == "cyl":
            r = p.get("r") or 0.1
            r2 = p.get("r2", r)
            h = p.get("h") or 0.1
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=p.get("seg") or 8)
            obj = bpy.context.active_object
            if abs(r2 - r) > 1e-6:
                obj.scale.x = 1
        elif t == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=p.get("r") or 0.2, segments=p.get("seg") or 8, ring_count=6)
            obj = bpy.context.active_object
        elif t == "torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=p.get("r") or 0.3, minor_radius=0.04)
            obj = bpy.context.active_object
        else:
            continue
        obj.name = mesh_name
        px, py, pz = p["p"]
        obj.location = (origin[0] + px, origin[1] + pz, origin[2] + py)
        obj.rotation_euler = Euler((p.get("rx") or 0, p.get("rz") or 0, p.get("ry") or 0))
        mat = bpy.data.materials.new(mesh_name + "_MAT")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = hex_color(p["c"])
            if p.get("e"):
                bsdf.inputs["Emission Color"].default_value = hex_color(p["e"])
                bsdf.inputs["Emission Strength"].default_value = 4.0
        obj.data.materials.append(mat)
        obj.parent = empty
        try:
            col.objects.link(obj)
        except RuntimeError:
            pass
        # remove from scene collection default
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)
    return empty


def build_spire_tower_bpy(h=300.0, footprint=24.0):
    """300m slender glass tower + spire, floors as repeating curtain-wall parts."""
    if not HAS_BPY:
        return
    col = bpy.data.collections.new("TOWER_300")
    bpy.context.scene.collection.children.link(col)
    bpy.ops.mesh.primitive_cube_add(size=1)
    core = bpy.context.active_object
    core.name = "spire_core"
    body_h = h - 22.0
    core.scale = (footprint, footprint, body_h)
    core.location = (0, 0, body_h * 0.5)
    # spire
    bpy.ops.mesh.primitive_cone_add(radius1=1.8, depth=22.0, vertices=6)
    spire = bpy.context.active_object
    spire.name = "spire_needle"
    spire.location = (0, 0, body_h + 11.0)
    floors = int(body_h / 3.5)
    # sample one floor of window frames as separate cubes (kit idea)
    for side in range(4):
        ang = side * math.pi * 0.5
        for i in range(6):
            bpy.ops.mesh.primitive_cube_add(size=1)
            w = bpy.context.active_object
            w.name = "win_f0_s%d_%d" % (side, i)
            w.scale = (1.4, 0.08, 1.3)
            off = (i - 2.5) * 3.2
            x = math.sin(ang) * (footprint * 0.5 + 0.06) + math.cos(ang) * off
            y = math.cos(ang) * (footprint * 0.5 + 0.06) - math.sin(ang) * off
            w.location = (x, y, 1.7)
            w.rotation_euler = Euler((0, 0, ang))


def main():
    emit(os.path.join(ROOT, "kit"))
    print("catalog kits:", ", ".join(KITS.keys()))
    for name, kit in KITS.items():
        print("  %s  parts=%d  sit=%s" % (name, len(kit["parts"]), kit.get("sit")))
    if not HAS_BPY:
        print("bpy not found — catalog emitted. Run inside Blender to mesh the kits.")
        return
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    x = 0.0
    for name, kit in KITS.items():
        build_kit_bpy(name, kit, (x, 0.0, 0.0))
        x += 4.0
    build_spire_tower_bpy()
    out = os.path.join(ROOT, "kit", "kits.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
    print("exported", out)


if __name__ == "__main__":
    main()
