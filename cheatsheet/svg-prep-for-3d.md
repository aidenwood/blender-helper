# SVG Prep for 3D — Stage Photo → Blender Pipeline

Tested practices for tracing a stage photo, cleaning the SVG, and getting it into Blender so the curves are script-friendly. Companion doc to `cheatsheet/svg-curve-workflow.md`, which covers what happens *after* the import button. This doc covers everything before that.

The pipeline you're building: **photo → traced SVG with strict layer names → simplified paths → exported clean SVG → Blender import → Python cleanup keyed on layer names**. Get the names right at trace time and the Blender side becomes 90% scripted.

## 1. Tracing tools — what to actually use

Four real options. Different tools win for different photo qualities. Pick one as primary and keep one fallback.

### Adobe Illustrator — Image Trace (recommended primary)

Best for: photos with clear contrast, repeatable batch results, when you already have CC. Open the photo in Illustrator, place as embedded image, then **Window → Image Trace**. The presets are the fastest way in:

- **High Fidelity Photo** — too noisy for stage geometry, skip.
- **6 Colors** or **3 Colors** — good for splitting stage / risers / lights into colour-banded regions you can then ungroup and rename.
- **Black and White Logo** — best for hard-edged stage outlines after contrast prep.
- **Sketched Art** / **Silhouettes** — good for performer silhouettes layer.

Manual tuning after picking a preset:
- **Threshold** (B&W modes): 128 default. Drop to 80–100 if the photo is dark, raise to 150–180 for bright stages.
- **Paths**: 50–70% — controls how tightly paths hug the source. Lower = simpler.
- **Corners**: 75% — higher means more sharp corners preserved (good for trusses).
- **Noise**: 25–50px — anything smaller than this gets dropped. Crank for noisy photos.
- **Method**: choose **Overlapping** (Abutting leaves gaps between regions; Overlapping makes layered shapes that map well to Blender's per-curve workflow).
- **Ignore White**: ON — drops the background blank.

After tuning, hit **Expand** in the top bar. This commits the trace to editable vector paths. Without Expand you can't rename, simplify, or export cleanly.

### Inkscape — Trace Bitmap (recommended free option)

Best for: free workflow, layered-output control. `Path → Trace Bitmap` (`Shift+Cmd+B`). Three modes worth knowing:

- **Brightness Cutoff** — single-pass, one threshold (0.45 is a good start for stage photos). Fast, good for silhouette layer.
- **Edge Detection** — uses an edge filter (default threshold 0.65). Gives outline-only paths. Great for truss/lighting positions where you want strokes not fills.
- **Multiple Scans → Brightness Steps** — set scans to **4–6**. Inkscape outputs that many stacked paths from dark to light. This is the magic mode for layered stage SVGs because each brightness band can be renamed and treated as its own Blender layer.

Tick **Stack Scans** so paths overlap correctly. Tick **Remove Background** to drop the white. Untick **Smooth** if you want sharp truss edges; tick it for performer silhouettes.

### Vectorizer.AI (paid, web)

$9–18/month. Output quality is genuinely better than Illustrator on noisy phone photos — its corner detection is sharper and it produces fewer redundant anchors out of the gate. Worth it if you're tracing weekly and shooting handheld. Export as **SVG → Cleaner** (drops decorative metadata) and pick **Curves: Cubic Bezier**, **Stroke style: Filled shapes**.

### Adobe Capture (mobile)

Useful only for on-site capture at the venue. Shape mode → trace live → send to CC Library → opens in Illustrator with paths ready. Lower quality than desktop Image Trace but you skip the photo-transfer step. Treat output as a sketch — re-trace properly back at the desk.

### Recommendation

**Primary: Illustrator Image Trace** with the **3 Colors** or **Black and White Logo** preset after photo prep (next section). It's the fastest path to a layered, named, exportable SVG. **Fallback: Inkscape Multiple Scans → Brightness Steps** when you need the layered output for free, or when Illustrator over-smooths a sharp-edged stage.

## 2. Photo prep before tracing

Tracing quality is bounded by photo quality. 2 minutes of prep in Photoshop / Affinity / Preview saves 20 minutes of anchor cleanup.

Do these in order:

1. **Crop tight** to the stage. Drop everything outside the proscenium — audience, ceiling, exit signs.
2. **Levels / Curves** — crush the blacks (input black to ~30) and lift the whites (input white to ~225). This separates stage geometry from ambient stage haze.
3. **Desaturate** to greyscale unless you're tracing colour-banded regions (in which case keep saturated and bump it +30).
4. **High-pass sharpen** at radius 2–4px, blend mode Overlay, opacity 60%. Sharpens edges without amplifying noise.
5. **Export as PNG** at 2000–3000px on the long edge. Higher = unnecessarily slow trace. Lower = lost detail on trusses.

### Splitting into layers before trace

When you want **background / stage / foreground performers** as separate Blender objects, don't trace the whole photo once and try to split after. Instead:

1. Duplicate the prepped photo into 3 documents.
2. Mask each one to a single depth band — paint out everything not in that band.
3. Trace each separately with appropriate settings (performers benefit from lower threshold + smoothing; trusses benefit from higher threshold + sharp corners).
4. Combine into one SVG in Illustrator/Inkscape by copying each layer into a single doc with named layers.

This is slower per stage but the layered output is what makes the Blender side scriptable.

## 3. Layer naming convention — the load-bearing decision

**Get this right and the Blender side writes itself.** Every Python script in `scripts/` can target curves by name prefix. Sloppy names mean manual selection forever.

### The convention

```
<category>_<element>_<index>
```

All lowercase, underscores only, two-digit zero-padded index. Categories:

| Prefix              | What it is                                  | Blender treatment           |
|---------------------|---------------------------------------------|-----------------------------|
| `bg_`               | Anything behind the stage (screens, backdrops, video walls) | Flat or slight extrude, dark material |
| `stage_riser_`      | Floor risers, stages, platforms             | Heavy extrude, matte material |
| `stage_floor_`      | Main stage floor outline                    | Single extrude, anchor object |
| `truss_main_`       | Primary horizontal trusses                  | Bevel + metal material |
| `truss_vertical_`   | Vertical truss towers                       | Bevel + metal material |
| `lights_par_`       | PAR can lighting positions                  | Emissive material, audio-bake driver |
| `lights_moving_`    | Moving head positions                       | Emissive + animatable rotation |
| `lights_strip_`     | LED strip / batten positions                | Emissive, longer thin geometry |
| `screen_`           | LED video screens, projection surfaces      | Flat with image texture |
| `performer_silhouette_` | Performer rough silhouettes             | Wiggle modifier, soft material |
| `prop_`             | Set pieces, scenic elements                 | Per-prop treatment |

### Examples for one stage

```
bg_screen_01
bg_screen_02
stage_riser_01
stage_riser_02
stage_floor_01
truss_main_01
truss_main_02
truss_vertical_01
lights_par_01
lights_par_02
lights_par_03
lights_moving_01
performer_silhouette_01
performer_silhouette_02
```

### Where to set the names

- **Illustrator**: Layers panel → double-click layer name → rename. After **Expand**, each sub-path becomes a `<Path>` inside its layer. Don't rename every path — name the **layer** and use the layer name as the Blender collection name (the SVG importer creates one curve object per path, but layer info is preserved in the SVG `<g id="...">` group attribute, which Blender exposes).
- **Inkscape**: Object → Objects panel (`Object → Objects...`). Double-click to rename layers and individual paths. Inkscape SVG preserves both `inkscape:label` and `id` — Blender reads `id`.

If you only name layers (not individual paths), Blender groups them by layer on import via the Empty parent. If you also name individual paths, scripts can target single elements (`lights_par_07`) instead of whole groups.

## 4. Path simplification — before export, not after

Too many anchor points wreck Blender bevel: the bevel profile gets stretched between dense anchors and produces visible ripples on what should be a smooth edge. Aim for the **minimum anchors needed to read the shape** at your final render resolution.

### Target anchor counts

| Element                  | Target anchors |
|--------------------------|----------------|
| Stage floor outline      | 8–20           |
| Riser (rectangular-ish)  | 4–8            |
| Truss (straight bar)     | 4–6            |
| PAR light (small circle) | 4–6            |
| Moving head (rounded)    | 6–10           |
| Performer silhouette     | 30–80          |
| Background screen        | 4–8            |

If a trace gives you 200 anchors for a simple riser, simplify before export. 200 anchors × 60 curves = Blender chugs on viewport redraw.

### Illustrator — Simplify

`Object → Path → Simplify`. The dialog has two key sliders:

- **Curve Precision**: 90–95% is a good start. Drop to 70–80% for aggressive cleanup on noisy traces.
- **Angle Threshold**: 30–45°. Higher = preserves sharp corners (truss joints), rounds gentler curves.

Tick **Show Original** to compare. Run twice if needed but watch for the shape distorting.

### Inkscape — Simplify

Select all paths, then `Path → Simplify` (`Cmd+L`). Each press simplifies further — 2–3 presses is usually right. The simplification threshold lives in `Inkscape → Preferences → Behavior → Simplification threshold` (default 0.002; raise to 0.005 for more aggressive).

Inkscape's Simplify is more destructive than Illustrator's per press. Save before, undo if it goes too far.

### Vectorizer.AI

Path reduction is built into the trace settings — set **Detail** to **Medium** or **Low** for stage geometry. The output is already optimised; rarely needs further simplification.

## 5. Joining paths vs leaving separate

This decision determines whether you can animate elements independently in Blender. Default to **leave separate**.

### Compound (single path with holes)

Use compound paths for: **a single visual shape that happens to have holes in it.** E.g. a truss frame outline where you want the outer rectangle and the inner cutouts as one curve so Blender fills the metal but leaves the holes hollow.

- Illustrator: select shapes → `Object → Compound Path → Make` (`Cmd+8`).
- Inkscape: select paths → `Path → Combine` (`Cmd+K`).

In Blender these come in as one curve with multiple sub-curves and the fill correctly skips the holes.

### Separate paths

Use separate paths for: **anything you want to animate, material-swap, or trigger independently.** Individual PAR lights, individual letters of a logo, each performer silhouette, each lighting position.

- Illustrator: don't `Compound Path → Make` them. Don't `Object → Group` them either if you want individual SVG paths (group is fine, it survives to SVG `<g>` and doesn't merge geometry).
- Inkscape: `Path → Break Apart` (`Shift+Cmd+K`) if a previous Combine merged things you wanted separate.

### Trade-off

| Approach        | Pro                                                        | Con                                                          |
|-----------------|------------------------------------------------------------|--------------------------------------------------------------|
| Compound        | One Blender object, fill respects holes, clean outliner   | Can't animate sub-elements independently                     |
| Separate        | Each path = one Blender curve object, script-targetable   | Outliner gets crowded; use collections to manage             |

For stage lighting positions specifically: **always separate**. You'll want to drive emission per-light from audio bakes.

## 6. Fill vs stroke — convert before export

Blender's SVG importer treats fills and strokes very differently and the result surprises most people.

### What Blender does

- **Filled paths** → closed curves with `Fill Mode: Both`. Ready for extrude, looks like solid geometry.
- **Stroked paths (no fill)** → open curves with `Fill Mode: None`. **They have zero thickness.** You'd need to add `Geometry → Bevel → Depth` per curve to give them visible thickness, and it'll be a round tube — not a flat ribbon.

This is fine for some cases (lighting cables as tubes) but wrong for most (a stroked rectangle becomes a hollow wireframe, not a solid panel).

### The rule

If you want **solid 3D geometry**, convert strokes to outlines/fills before SVG export.

- **Illustrator**: select all stroked paths → `Object → Path → Outline Stroke`. The stroke becomes a filled shape with the stroke's thickness as fill width.
- **Inkscape**: select → `Path → Stroke to Path` (`Cmd+Alt+C`). Same result.

### When to keep strokes

Keep stroked paths (don't outline) when:

- You want tube-like geometry in Blender (cables, wires, light beams).
- You'll set `Geometry → Bevel → Depth` to a small value in Blender to give them thickness uniformly.
- You want to animate the curve as a path (Follow Path constraint, Array along curve).

For 99% of stage geometry — risers, screens, truss profiles, light fixture outlines — **outline the strokes first**.

## 7. SVG export settings — per tool

### Illustrator → File → Export → Export As → SVG

Critical settings:
- **Styling**: `Presentation Attributes` (not Inline CSS — Blender ignores CSS).
- **Font**: `Convert to Outline` (Blender doesn't read SVG font references).
- **Images**: `Embed` (Link breaks if Blender can't resolve the path).
- **Object IDs**: `Layer Names` — this is the one that maps your layer names into the SVG `id` attribute that Blender picks up.
- **Decimal**: `2` — enough precision for stage work, smaller file.
- **Minify**: OFF (makes the file uneditable if you need to hand-fix something).
- **Responsive**: OFF (adds `viewBox`-only sizing which can confuse Blender's import scale).

### Inkscape → File → Save As → Plain SVG

- Use **Plain SVG (*.svg)**, not **Inkscape SVG**. Inkscape SVG includes `sodipodi:` and `inkscape:` namespace metadata that Blender ignores but bloats the file.
- `Inkscape → Preferences → SVG output → Numeric precision`: 3 decimal places.
- `Inkscape → Preferences → SVG output → Path data`: `Absolute` (Blender handles both but absolute is more predictable).
- Make sure `viewBox` is set (it is by default if you set a document size).

### Figma — caution

Figma's SVG export is the most lossy of the three. Specific gotchas:

- **Masks** export as clip paths; Blender ignores clips. Flatten masks to paths before export (`Object → Flatten`).
- **Gradients** export as `linearGradient` / `radialGradient` defs. Blender drops these entirely — you get a solid fill of the first stop's colour. Bake gradients into raster or replace with solid colours before tracing.
- **Effects** (drop shadow, layer blur, inner shadow) don't survive at all. Strip them.
- **Boolean operations** export correctly if you `Flatten Selection` first; otherwise Figma can export the source components and the boolean separately, doubling geometry.
- **Strokes** export as strokes, not outlines. **Outline them first** (`Object → Outline Stroke` equivalent: select → `Shift+Cmd+O`).

Figma is fine as a source if you flatten aggressively before export. Illustrator and Inkscape are more reliable for trace-from-photo work.

## 8. Importing into Blender — quick recap

`File → Import → Scalable Vector Graphics (.svg)`. Full details in `cheatsheet/svg-curve-workflow.md`. The short version:

- **One curve object per path** in the SVG.
- **Parented to an Empty** named after the SVG file.
- **Tiny scale** — SVG pixels become roughly millimetres, so the import is usually 0.05–0.5m wide.
- **2D shape mode**, **fill on** (`Fill Mode: Both`).
- **Origins at world origin**, not per-curve.

Don't fix any of this manually. Run the post-import cleanup script next.

## 9. Post-import cleanup — script this

A consistent sequence of operations runs after every import. UI version first, then the script template.

### Manual sequence (one-time, to verify)

1. Select the parent Empty in the outliner.
2. `Object → Select → Select Children` (or `Shift+G → Children`).
3. `S` → type `1000` → Enter to scale up.
4. `Cmd+A → Scale` to apply.
5. `Object → Set Origin → Origin to Geometry`.
6. Select all curves, one as active. Properties → Object Data → Shape → 3D.
7. Move each curve into a collection by name prefix (`bg_*` → "Background" collection, `truss_*` → "Trusses" collection, etc.).

### Script template — drop into `scripts/post_svg_import_cleanup.py`

```python
"""
post_svg_import_cleanup.py
--------------------------
Runs after File → Import → SVG to:
  1. Scale up the parent Empty.
  2. Apply scale.
  3. Set origin to geometry on every imported curve.
  4. Switch curves to 3D shape mode.
  5. Sort curves into collections by name prefix.

How to run:
  1. Import the SVG. Note the Empty's name (matches the file).
  2. Edit EMPTY_NAME below.
  3. Scripting workspace → New → paste → Run Script.
"""

import bpy

# === EDIT THESE ===
EMPTY_NAME = "MyStage.svg"   # the parent empty Blender creates on import
SCALE_FACTOR = 1000          # SVG mm → metres
PREFIX_TO_COLLECTION = {
    "bg_":        "Background",
    "stage_":     "Stage",
    "truss_":     "Trusses",
    "lights_":    "Lights",
    "screen_":    "Screens",
    "performer_": "Performers",
    "prop_":      "Props",
}
# ==================

empty = bpy.data.objects.get(EMPTY_NAME)
if empty is None:
    raise RuntimeError(f"Empty '{EMPTY_NAME}' not found.")

# 1. Scale up
empty.scale = (SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR)

# 2. Apply scale recursively
bpy.ops.object.select_all(action='DESELECT')
empty.select_set(True)
for child in empty.children_recursive:
    child.select_set(True)
bpy.context.view_layer.objects.active = empty
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3 + 4. Per-curve cleanup
for obj in empty.children_recursive:
    if obj.type != 'CURVE':
        continue
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    obj.data.dimensions = '3D'

# 5. Sort into collections
for prefix, coll_name in PREFIX_TO_COLLECTION.items():
    coll = bpy.data.collections.get(coll_name)
    if coll is None:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)
    for obj in empty.children_recursive:
        if obj.type == 'CURVE' and obj.name.startswith(prefix):
            for c in obj.users_collection:
                c.objects.unlink(obj)
            coll.objects.link(obj)

print("[post_svg_import_cleanup] done")
```

This is the single biggest time-saver in the whole pipeline. Every weekly stage runs through this script untouched.

## 10. Naming-convention payoff — three real use cases

Once the SVG has clean `<prefix>_<element>_<index>` names and the curves are sorted into collections, each of these is a 10-line script.

### Use case 1 — apply metal material to all trusses

```python
import bpy

# === EDIT THESE ===
PREFIX = "truss_"
MATERIAL_NAME = "Metal_Brushed"
# ==================

mat = bpy.data.materials.get(MATERIAL_NAME)
if mat is None:
    mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.6, 0.6, 0.62, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.35

for obj in bpy.data.objects:
    if obj.type == 'CURVE' and obj.name.startswith(PREFIX):
        obj.data.materials.clear()
        obj.data.materials.append(mat)
```

### Use case 2 — emissive lights driven off an audio bake

Assumes you've baked an audio f-curve onto a custom property `["audio"]` on a controller empty. Each light's emission strength reads that value via a driver.

```python
import bpy

# === EDIT THESE ===
PREFIX = "lights_"
DRIVER_TARGET = "AudioController"   # an Empty with ["audio"] custom prop
EMISSION_BASE_COLOR = (1.0, 0.6, 0.2, 1)
EMISSION_MULTIPLIER = 50.0
# ==================

mat = bpy.data.materials.new(f"Emissive_{PREFIX}")
mat.use_nodes = True
nt = mat.node_tree
out = nt.nodes["Material Output"]
for n in list(nt.nodes):
    if n != out:
        nt.nodes.remove(n)
emit = nt.nodes.new("ShaderNodeEmission")
emit.inputs["Color"].default_value = EMISSION_BASE_COLOR
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

# Driver on emission strength
fcurve = emit.inputs["Strength"].driver_add("default_value")
drv = fcurve.driver
drv.type = 'SCRIPTED'
var = drv.variables.new()
var.name = "a"
var.targets[0].id_type = 'OBJECT'
var.targets[0].id = bpy.data.objects[DRIVER_TARGET]
var.targets[0].data_path = '["audio"]'
drv.expression = f"a * {EMISSION_MULTIPLIER}"

for obj in bpy.data.objects:
    if obj.type == 'CURVE' and obj.name.startswith(PREFIX):
        obj.data.materials.clear()
        obj.data.materials.append(mat)
```

### Use case 3 — wiggle every performer silhouette

Adds a Noise modifier to the location of each performer curve so they sway slightly. Subtle motion sells a static silhouette as a live performer.

```python
import bpy
import random

# === EDIT THESE ===
PREFIX = "performer_"
WIGGLE_STRENGTH = 0.05   # metres
WIGGLE_SPEED = 0.5
# ==================

for obj in bpy.data.objects:
    if obj.type != 'CURVE' or not obj.name.startswith(PREFIX):
        continue
    # Insert a keyframe so we have an f-curve to modify
    obj.keyframe_insert(data_path="location", frame=1)
    action = obj.animation_data.action
    for fc in action.fcurves:
        mod = fc.modifiers.new(type='NOISE')
        mod.strength = WIGGLE_STRENGTH
        mod.scale = 50 / WIGGLE_SPEED
        mod.phase = random.uniform(0, 100)
```

Run all three after the post-import cleanup and the stage is materialed, audio-reactive, and animated in under a minute.

## Pipeline summary — weekly gig checklist

```
[1] Shoot stage photo at venue.
[2] Photo prep: crop, levels, sharpen, export 2500px PNG.
[3] (Optional) Split into bg / stage / performers layers.
[4] Illustrator Image Trace → 3 Colors or B&W Logo → Expand.
[5] Outline all strokes (Object → Path → Outline Stroke).
[6] Simplify (Object → Path → Simplify @ 90% / 35°).
[7] Rename layers + paths using <category>_<element>_<index>.
[8] Export SVG: Presentation Attributes, Layer Names IDs, decimal 2.
[9] Blender: File → Import → SVG.
[10] Run scripts/post_svg_import_cleanup.py.
[11] Run material / emission / wiggle scripts.
[12] Animate, render, AE, Resolume.
```

Steps 9–11 are the same every week. Steps 1–8 take 15–25 minutes once the convention is muscle memory.
