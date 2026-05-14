"""
rename_curves_sequential.py
---------------------------
Renames every selected curve with a PREFIX and a zero-padded counter.

Example with PREFIX="path", START=1, PAD=3:
  path_001, path_002, path_003, ...

How to run:
  1. Select the curves you want to rename.
  2. Edit the values below.
  3. Scripting workspace → New → paste → Run Script.

Order:
  Curves are sorted by their current name before renaming, so the output is
  stable across runs.
"""

import bpy

# === EDIT THESE ===
PREFIX = "path"
START = 1
PAD = 3                # path_001, path_002, ...
RENAME_DATA_BLOCK = True   # also rename obj.data (the curve data block)
# ==================

curves = [o for o in bpy.context.selected_objects if o.type == 'CURVE']
curves.sort(key=lambda o: o.name)

for i, obj in enumerate(curves, start=START):
    new_name = f"{PREFIX}_{str(i).zfill(PAD)}"
    obj.name = new_name
    if RENAME_DATA_BLOCK:
        obj.data.name = new_name

print(f"[rename] renamed {len(curves)} curve(s) with prefix '{PREFIX}'")
