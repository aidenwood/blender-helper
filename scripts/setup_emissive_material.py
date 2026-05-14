"""
setup_emissive_material.py
--------------------------
Creates (or reuses) an emissive "stage glow" material and assigns it to every
selected object. Designed for stage-light curves and projection-ready visuals.

Material structure:
  Principled BSDF with Emission Color + Emission Strength,
  routed to Material Output. Base color matches emission for clean look in
  Eevee. Set use_nodes so you can tweak further in the Shader Editor.

How to run:
  1. Select the target objects (curves, meshes — anything with materials).
  2. Edit the values below.
  3. Scripting workspace → New → paste → Run Script.
"""

import bpy

# === EDIT THESE ===
MATERIAL_NAME = "stage_glow"
EMISSION_COLOR = (1.0, 0.35, 0.8, 1.0)   # RGBA, 0–1. Pink/magenta default.
EMISSION_STRENGTH = 12.0                  # >1 for visible bloom in Eevee; 5–30 normal range
REPLACE_ALL_SLOTS = True
# ==================


def build_material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    for n in list(nodes):
        nodes.remove(n)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    # Match base color to emission for clean look across engines
    bsdf.inputs['Base Color'].default_value = EMISSION_COLOR
    bsdf.inputs['Emission Color'].default_value = EMISSION_COLOR
    bsdf.inputs['Emission Strength'].default_value = EMISSION_STRENGTH
    # Tame specular so curves don't show weird highlights
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.0
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 1.0

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


mat = build_material(MATERIAL_NAME)

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

print(f"[emissive] '{MATERIAL_NAME}' (strength={EMISSION_STRENGTH}) applied to {count} object(s)")
