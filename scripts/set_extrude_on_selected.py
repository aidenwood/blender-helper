"""
set_extrude_on_selected.py
--------------------------
Sets Curve > Extrude on every selected CURVE object.

How to run:
  1. Open Blender, switch to the Scripting workspace (top tab).
  2. In the text editor pane: New → paste this file.
  3. Edit the value in the EDIT THESE block below.
  4. Run Script (the play icon) or press Option+P with the cursor in the editor.

What it changes:
  obj.data.extrude   — adds depth along the curve normal (the "thickness")

Notes:
  - Only affects objects of type CURVE. Mesh/text/empty are skipped.
  - Curves in 2D shape mode will extrude flat; for 3D depth, set Shape to 3D
    first (Object Data Properties > Shape > 3D) or run the props-copy script.
"""

import bpy

# === EDIT THESE ===
EXTRUDE_VALUE = 0.05   # in metres (or your scene unit)
# ==================

count = 0
for obj in bpy.context.selected_objects:
    if obj.type == 'CURVE':
        obj.data.extrude = EXTRUDE_VALUE
        count += 1

print(f"[set_extrude] extrude={EXTRUDE_VALUE} on {count} curve(s)")
