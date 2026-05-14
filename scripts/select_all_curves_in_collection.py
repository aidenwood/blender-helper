"""
select_all_curves_in_collection.py
----------------------------------
Selects every CURVE object inside a named collection, including curves in
child collections (recursive).

How to run:
  1. Edit COLLECTION_NAME below to match your collection in the outliner.
  2. Scripting workspace → New → paste → Run Script.

After running, all curves in that collection will be selected (orange outline)
and the last one walked becomes active. You can then run any of the other
batch scripts.
"""

import bpy

# === EDIT THESE ===
COLLECTION_NAME = "Collection"
DESELECT_OTHERS_FIRST = True
# ==================

coll = bpy.data.collections.get(COLLECTION_NAME)
if coll is None:
    raise RuntimeError(
        f"Collection '{COLLECTION_NAME}' not found. "
        f"Available: {[c.name for c in bpy.data.collections]}"
    )

if DESELECT_OTHERS_FIRST:
    bpy.ops.object.select_all(action='DESELECT')

selected = 0
last = None

def walk(c):
    global selected, last
    for o in c.objects:
        if o.type == 'CURVE':
            o.select_set(True)
            last = o
            selected += 1
    for child in c.children:
        walk(child)

walk(coll)

if last is not None:
    bpy.context.view_layer.objects.active = last

print(f"[select_curves] selected {selected} curve(s) in '{COLLECTION_NAME}'")
