# "Copy to Selected" is greyed out

You right-clicked a property in the Properties panel and "Copy to Selected" is greyed out (or missing entirely). Here's every reason it happens, in order of how often it's the cause.

## 1. Only one object is "really" selected

Copy to Selected requires:
- An **active** object (the source)
- At least one other **selected** object (the target)

If your viewport shows multiple orange outlines but the menu is still greyed out, the selection might not be what you think. The fix that resolves this 80% of the time:

1. `A` to deselect all (or `Option+A`, depending on your keymap).
2. Box-select (`B`, drag) over all the targets you want.
3. Hold `Shift` and **click the source last**. Source now has the lighter outline (active).
4. Right-click the property → Copy to Selected should now work.

## 2. No active object

If you have a selection but **no active**, the menu greys out because there's no source to copy from.

Signs:
- No object has the lighter / pale-yellow outline.
- The Properties panel shows the wrong object's data (or none).

Fix: `Shift+click` an object to make it active without changing the selection.

## 3. You right-clicked the property label, not the value field

The right-click context menu only appears in full form when you click the **input field** (where you'd type a value), not the text label next to it.

Fix: move the cursor onto the actual number / dropdown / checkbox area and right-click there.

## 4. Mixed object types in selection

If your active is a curve and other selected objects are meshes/text/empties, **Copy to Selected** for a curve-specific property is greyed out — there's nowhere on a mesh to put `bevel_depth`.

Fix: select only objects of the same type. Quickest way:
- Right-click an object → `Select → Select All by Type → Curve`.
- Or `Select → All by Type → Curve` from the top of the 3D viewport.

## 5. The property is a sub-property of an unsupported struct

Some properties live inside structs that don't support the operator — typically read-only fields, or fields inside complex modifier internals.

Fix: try copying the **parent** property instead. E.g. you can usually copy the whole modifier rather than one field inside it: right-click the modifier name → `Copy Modifier to Selected`.

## 6. Driver / animation is on the property

If the value is **driven** (purple), **keyframed** (green/yellow), or has any animation data, Copy to Selected may grey out because the operator can't safely overwrite an animated value.

Fix: right-click → Clear Keyframes / Clear Drivers first, or accept that you'll script the change instead.

## 7. Linked / library override

If the data block is linked from another file, properties on it are read-only in your scene. The Copy to Selected target objects must have writable data.

Fix: make local with `Object → Relations → Make Local` (rarely what you actually want — usually means you need to change the original file).

## Failsafe: the script

When none of the above clears it up, run `scripts/copy_active_curve_props_to_selected.py`. It does the same thing programmatically and will print a clear error if your selection state is wrong.
