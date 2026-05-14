"""
copy_active_curve_props_to_selected.py
--------------------------------------
Copies the most-used curve properties from the ACTIVE curve to every other
selected curve.

  Active   = the last-clicked object (lighter outline in the viewport).
  Selected = every orange-outlined object.

How to set this up before running:
  1. Box-select all the target curves.
  2. Click the SOURCE curve last (Shift+click if already selected) so it
     becomes active. You'll see a lighter outline on it.
  3. Scripting workspace → New → paste → Run Script.

Properties copied:
  - extrude
  - bevel_depth
  - bevel_resolution
  - resolution_u            (curve smoothness along its length)
  - use_fill_caps           (cap the ends of extruded curves)
  - fill_mode               ('FULL', 'BACK', 'FRONT', 'HALF')

If you need more props copied, add to the list at the bottom of this file.
"""

import bpy

PROPS_TO_COPY = (
    "extrude",
    "bevel_depth",
    "bevel_resolution",
    "resolution_u",
    "use_fill_caps",
    "fill_mode",
)

active = bpy.context.active_object
if active is None or active.type != 'CURVE':
    raise RuntimeError(
        "Active object must be a curve. Click the source curve last so it's active."
    )

src = active.data
count = 0
for obj in bpy.context.selected_objects:
    if obj == active or obj.type != 'CURVE':
        continue
    for prop in PROPS_TO_COPY:
        setattr(obj.data, prop, getattr(src, prop))
    count += 1

print(f"[copy_props] copied {len(PROPS_TO_COPY)} props from '{active.name}' to {count} curve(s)")
