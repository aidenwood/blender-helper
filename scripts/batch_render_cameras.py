"""
batch_render_cameras.py
-----------------------
Renders every camera in the scene to its own output folder.

Output structure:
  OUTPUT_ROOT/
    <camera_name>/####.png

How to run:
  1. Edit OUTPUT_ROOT and the optional CAMERA_PREFIX filter.
  2. Scripting workspace → New → paste → Run Script.

The script renders the current frame range (scene.frame_start to scene.frame_end)
for each matching camera. Use the CLI wrapper (cli/render-cameras.sh) for
headless overnight runs.
"""

import os
import bpy

# === EDIT THESE ===
OUTPUT_ROOT = "//renders/cameras"   # // = relative to .blend file
CAMERA_PREFIX = ""                  # "" = render all cameras; "cam_" = only matching
RENDER_ANIMATION = True             # True = full frame range, False = current frame only
# ==================

# CLI wrapper override — cli/render-cameras.sh sets this env var.
OUTPUT_ROOT = os.environ.get("BHELPER_OUTPUT_ROOT", OUTPUT_ROOT)


def find_cameras():
    cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
    if CAMERA_PREFIX:
        cams = [c for c in cams if c.name.startswith(CAMERA_PREFIX)]
    return sorted(cams, key=lambda c: c.name)


def render_camera(scene, cam):
    scene.camera = cam
    out_dir = os.path.join(bpy.path.abspath(OUTPUT_ROOT), cam.name)
    os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.join(out_dir, "")
    print(f"[batch_cameras] rendering '{cam.name}' → {out_dir}")
    if RENDER_ANIMATION:
        bpy.ops.render.render(animation=True)
    else:
        bpy.ops.render.render(write_still=True)


scene = bpy.context.scene
original_camera = scene.camera
original_filepath = scene.render.filepath

cams = find_cameras()
if not cams:
    raise RuntimeError(f"No cameras matched prefix '{CAMERA_PREFIX}'")

print(f"[batch_cameras] will render {len(cams)} camera(s): {[c.name for c in cams]}")

try:
    for cam in cams:
        render_camera(scene, cam)
finally:
    scene.camera = original_camera
    scene.render.filepath = original_filepath

print(f"[batch_cameras] done. {len(cams)} camera(s) rendered.")
