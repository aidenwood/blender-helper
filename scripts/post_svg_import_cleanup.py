"""
post_svg_import_cleanup.py
--------------------------
The standard cleanup pass after `File → Import → SVG`.

In order:
  1. Selects all curves under the imported parent Empty (if you give its name).
     Falls back to "all curves in scene" if no parent given.
  2. Scales them up by SCALE_FACTOR and applies the scale.
  3. Sets origin → geometry on each curve.
  4. Switches each curve to 3D Shape mode.
  5. Sorts curves into collections by name prefix (split on first underscore).

Naming convention this script expects:
  `<category>_<element>_<index>` — e.g. `truss_main_01`, `lights_par_03`, `stage_riser_02`.
  Curves are moved to a collection named after `<category>` (created if missing).

How to run:
  1. Import your SVG.
  2. Edit PARENT_EMPTY_NAME and SCALE_FACTOR.
  3. Scripting workspace → New → paste → Run Script.
"""

import bpy

# === EDIT THESE ===
PARENT_EMPTY_NAME = ""      # "" = process every curve in the scene; otherwise the SVG's parent Empty
SCALE_FACTOR = 1000.0       # SVG comes in tiny; 1000 takes mm → m. Use 100 if it's already roughly cm-scale.
SET_3D_SHAPE = True
SORT_INTO_COLLECTIONS = True
SORT_SEPARATOR = "_"        # split layer name on this; first chunk = collection name
DEFAULT_COLLECTION = "_unsorted"
# ==================


def get_curves():
    if PARENT_EMPTY_NAME:
        parent = bpy.data.objects.get(PARENT_EMPTY_NAME)
        if parent is None:
            raise RuntimeError(f"Parent Empty '{PARENT_EMPTY_NAME}' not found")
        return [o for o in parent.children_recursive if o.type == 'CURVE']
    return [o for o in bpy.data.objects if o.type == 'CURVE']


def ensure_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def move_to_collection(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)


curves = get_curves()
if not curves:
    raise RuntimeError("No curves found. Check PARENT_EMPTY_NAME or import an SVG first.")

print(f"[svg_cleanup] processing {len(curves)} curve(s)")

# Step 1+2: select + scale + apply scale
bpy.ops.object.select_all(action='DESELECT')
for c in curves:
    c.select_set(True)
bpy.context.view_layer.objects.active = curves[0]
bpy.ops.transform.resize(value=(SCALE_FACTOR,) * 3)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Step 3: origin → geometry per curve
for c in curves:
    bpy.ops.object.select_all(action='DESELECT')
    c.select_set(True)
    bpy.context.view_layer.objects.active = c
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

# Step 4: 3D shape mode
if SET_3D_SHAPE:
    for c in curves:
        c.data.dimensions = '3D'

# Step 5: sort into collections by name prefix
if SORT_INTO_COLLECTIONS:
    sorted_count = 0
    for c in curves:
        chunks = c.name.split(SORT_SEPARATOR, 1)
        coll_name = chunks[0] if len(chunks) > 1 and chunks[0] else DEFAULT_COLLECTION
        coll = ensure_collection(coll_name)
        move_to_collection(c, coll)
        sorted_count += 1
    print(f"[svg_cleanup] sorted {sorted_count} curves into collections by name prefix")

print(f"[svg_cleanup] done.")
