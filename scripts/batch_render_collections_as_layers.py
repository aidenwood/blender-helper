"""
batch_render_collections_as_layers.py
-------------------------------------
Renders each top-level collection in the scene as its own image sequence
with transparent background — one clip per "layer" for Resolume comp.

For each collection in COLLECTIONS_TO_RENDER (or all if empty):
  1. Hide every collection except this one (render visibility).
  2. Render the current frame range to OUTPUT_ROOT/<collection_name>/####.png.
  3. Restore visibility.

The output: drop OUTPUT_ROOT into Resolume's file browser, each subfolder
becomes one clip on its own layer. Add blend modes (Add / Screen), done.

How to run:
  Scripting workspace → New → paste → Run Script. Pre-set render to PNG RGBA
  with film_transparent=True first (the apply_render_preset.py script does this).
"""

import os
import bpy

# === EDIT THESE ===
OUTPUT_ROOT = "//renders/layers"
COLLECTIONS_TO_RENDER = []   # empty = all top-level collections under the scene root
EXCLUDE_PREFIXES = ("_",)    # collections starting with these are skipped (e.g. "_helpers")
# ==================

# CLI wrapper override — cli/render-layers.sh sets this env var.
OUTPUT_ROOT = os.environ.get("BHELPER_OUTPUT_ROOT", OUTPUT_ROOT)


def top_level_collections(scene):
    return [c for c in scene.collection.children if not any(c.name.startswith(p) for p in EXCLUDE_PREFIXES)]


def target_collections(scene):
    tops = top_level_collections(scene)
    if COLLECTIONS_TO_RENDER:
        wanted = set(COLLECTIONS_TO_RENDER)
        tops = [c for c in tops if c.name in wanted]
    return tops


def snapshot_visibility(scene):
    """Capture hide_render for every collection so we can restore after."""
    state = {}
    for c in scene.collection.children_recursive:
        state[c.name] = c.hide_render
    return state


def restore_visibility(scene, state):
    for c in scene.collection.children_recursive:
        if c.name in state:
            c.hide_render = state[c.name]


def isolate(scene, target):
    for c in top_level_collections(scene):
        c.hide_render = (c.name != target.name)


def render_one(scene, coll):
    out_dir = os.path.join(bpy.path.abspath(OUTPUT_ROOT), coll.name)
    os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.join(out_dir, "")
    print(f"[batch_layers] rendering layer '{coll.name}' → {out_dir}")
    bpy.ops.render.render(animation=True)


scene = bpy.context.scene
original_filepath = scene.render.filepath

# Force transparent film — this is a layer export, alpha is the whole point.
if not scene.render.film_transparent:
    print("[batch_layers] forcing film_transparent=True for alpha output")
    scene.render.film_transparent = True

targets = target_collections(scene)
if not targets:
    raise RuntimeError("No collections matched. Check COLLECTIONS_TO_RENDER and EXCLUDE_PREFIXES.")

print(f"[batch_layers] will render {len(targets)} layer(s): {[c.name for c in targets]}")

snapshot = snapshot_visibility(scene)
try:
    for coll in targets:
        isolate(scene, coll)
        render_one(scene, coll)
finally:
    restore_visibility(scene, snapshot)
    scene.render.filepath = original_filepath

print(f"[batch_layers] done. {len(targets)} layer(s) rendered with alpha.")
