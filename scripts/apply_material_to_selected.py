"""
apply_material_to_selected.py
-----------------------------
Assigns a named material to every selected object that supports materials
(meshes, curves, surfaces, text, metaballs).

If the material doesn't exist yet, it's created with nodes enabled so you
can tweak shading in the Shader Editor straight away.

How to run:
  1. Select the target objects.
  2. Edit MATERIAL_NAME below.
  3. Scripting workspace → New → paste → Run Script.

Notes:
  - REPLACE_ALL_SLOTS=True wipes existing material slots and adds the new one
    as slot 0. Set False to only overwrite slot 0 (or append if empty).
"""

import bpy

# === EDIT THESE ===
MATERIAL_NAME = "Main"
REPLACE_ALL_SLOTS = True
# ==================

mat = bpy.data.materials.get(MATERIAL_NAME)
if mat is None:
    mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.use_nodes = True

count = 0
for obj in bpy.context.selected_objects:
    if not hasattr(obj.data, "materials"):
        continue
    if REPLACE_ALL_SLOTS:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    else:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
    count += 1

print(f"[apply_material] '{MATERIAL_NAME}' applied to {count} object(s)")
