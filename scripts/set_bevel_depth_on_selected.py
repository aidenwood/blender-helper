"""
set_bevel_depth_on_selected.py
------------------------------
Sets Curve > Bevel > Depth (and Resolution) on every selected CURVE object.

How to run:
  Scripting workspace → New → paste → Run Script (or Option+P).

What it changes:
  obj.data.bevel_depth        — radius of the round profile swept along the curve
  obj.data.bevel_resolution   — segments around the profile (higher = smoother)

Notes:
  - Bevel only renders if Bevel Mode is "Round" (the default).
  - For 2D curves with Fill = Both, bevel adds a rim around the fill.
"""

import bpy

# === EDIT THESE ===
BEVEL_DEPTH = 0.01
BEVEL_RESOLUTION = 4
# ==================

count = 0
for obj in bpy.context.selected_objects:
    if obj.type == 'CURVE':
        obj.data.bevel_depth = BEVEL_DEPTH
        obj.data.bevel_resolution = BEVEL_RESOLUTION
        count += 1

print(f"[set_bevel] depth={BEVEL_DEPTH} res={BEVEL_RESOLUTION} on {count} curve(s)")
