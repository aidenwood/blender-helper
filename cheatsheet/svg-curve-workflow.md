# SVG → Curve Workflow

This is the workflow you'll do most. `File → Import → Scalable Vector Graphics (.svg)` brings the file in as Blender curves. Here's what to expect and the gotchas.

## What you get on import

- **One curve object per path** in the SVG. A logo with 30 paths = 30 objects in the outliner.
- **Each object has its own data block.** Changing extrude on one doesn't affect the others. You'll batch them with Copy to Selected or a script.
- **They're parented to an Empty** named after the SVG file. Useful for moving the whole group; you can unparent (`Option+P → Clear and Keep Transformation`) once placed.
- **Origins at world (0, 0, 0).** Not at each curve's center. If you want each curve to rotate around its own center: select all → `Object → Set Origin → Origin to Geometry`.
- **Scale is tiny.** SVG pixels become roughly millimetres. Result: the whole import is often around 0.05–0.5 metres wide. Resize with `S`, then `Cmd+A → Scale` to apply.
- **Shape is 2D.** Curves come in flat. To extrude/bevel into 3D depth, switch each curve's Shape to 3D (Object Data Properties → Shape → 3D) OR rely on extrude/bevel working on 2D curves (which they do, just along the curve's local Z).
- **Fill is on (mode: Both).** If you want only stroke-like geometry, set Fill to None per curve and use bevel_depth instead.

## The "extrude my whole logo" workflow

Most common goal: SVG comes in flat, I want extruded 3D shapes.

1. Import the SVG.
2. In the outliner, expand the parent Empty. Click the first curve, then `Shift+click` the last one (or just `A` after selecting one with the cursor in the outliner) to select all curves.
3. Click one of them last so it's active.
4. On the active, set:
   - Object Data Properties → Shape → 3D (optional, depends on look you want)
   - Geometry → Extrude → e.g. `0.05`
   - Geometry → Bevel → Depth → e.g. `0.005` (small rounded edge)
5. Right-click each of those values → **Copy to Selected**.

Or, faster: edit `scripts/copy_active_curve_props_to_selected.py` with your values, set the source curve up first, then run it.

## The "they all look weird / inside out" issue

SVG curves sometimes import with reversed normals or with sub-paths that confuse Blender's fill. Symptoms: black patches, missing fill, shading flips.

Fixes in rough order:
- Object Data Properties → Shape → **Fill Mode**: try `Both` / `Front` / `Back`. Often a single click here fixes it.
- Edit Mode → select all (`A`) → `Segments → Switch Direction` (under the Segment menu).
- Recalculate normals: only applies after converting curve → mesh.

## The "scale is wrong / extrude looks huge or invisible" issue

Cause: SVG units came in as ~millimetres but you're working at metre scale.

Two clean fixes:
1. **Scale up the import**: select the parent Empty, `S` → type `1000` → Enter, then `Cmd+A → Scale` (applies the scale so curve data is at the new size). Now extrude=`0.05` looks normal.
2. **Use small values**: leave the scale, use extrude=`0.0001`. Fine, but Cycles/Eevee distance settings and modifier sizes will all need rethinking. Most people prefer fix #1.

After scale-up, **apply transforms** so the curve's local space matches world. Otherwise bevel will look squashed/stretched.

## Joining curves — usually a trap

`Cmd+J` joins all selected curves into one object. Tempting for "tidy up the outliner" but:

- All sub-curves now share **one data block**. You lose the ability to set per-curve extrude.
- The joined object adopts the active's data settings — others lose their individual fills/extrudes.
- Hard to split apart cleanly later (`P → By Loose Parts` in Edit Mode works but tedious).

Better tidy-up: put them in a collection, name the collection something obvious, collapse it in the outliner.

## Converting to mesh (when you need the geometry permanent)

Once you're happy with extrude/bevel: `Object → Convert → Mesh`.

After conversion:
- Curve properties are gone — you can't tweak extrude/bevel any more.
- You can now use mesh modifiers (Bevel, Subdivision Surface, Solidify) and apply them.
- Origins, shading, and UVs are now stable.

Don't convert until you're done iterating on the curve-level look.

## Quick reference: per-curve properties worth knowing

Found in **Properties → Object Data Properties** (the green curve icon) when a curve is the active object:

| Property             | What it does                                            |
|----------------------|---------------------------------------------------------|
| Shape → 2D / 3D      | Restricts how the curve bends in space                  |
| Shape → Fill         | None / Front / Back / Both — controls fill direction    |
| Geometry → Extrude   | Adds depth perpendicular to the curve plane             |
| Geometry → Bevel     | Sweeps a profile (round/object/profile) along the curve |
| Geometry → Taper Obj | Scales bevel along curve based on another curve         |
| Resolution → Preview U | Smoothness along curve length                         |
