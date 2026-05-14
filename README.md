# Blender Helper — VJ / Stage Projection Pipeline

An opinionated toolkit for the stage-projection / VJ pipeline on **Blender 5.x + macOS**:

> **Stage photo → SVG trace → Blender 3D → After Effects comp → Resolume Arena → live gig.**

Built to cut the manual work between the brief and the render so you can run gigs **weekly instead of monthly**. Includes ready-to-paste Blender Python scripts, headless CLI render wrappers, After Effects expression templates, and reference docs covering render-speed cheats, codec selection, audio-reactive rigs, and SVG prep.

Pairs with [Claude Code](https://claude.com/claude-code) (or any AI coding assistant) — the included `CLAUDE.md` briefs the assistant on your setup so you stop re-explaining it every session. Also works fine standalone if you don't use an AI assistant.

## Who this is for

- You're doing VJ / stage-projection work and the render pipeline is your bottleneck.
- You're on macOS (Apple Silicon ideally), using Blender 5.x or 4.x, AE, Resolume.
- You import SVG-traced stage photos and end up with 30+ separate curve objects to wrangle.
- You want one render template that re-fires against different tracks each gig.

## Quick start — weekly gig workflow

```bash
# 1. Scaffold a new gig folder
~/path/to/blender-helper/cli/new-gig.sh 2026-05-22_warehouse_brisbane

# 2. Trace the stage photo to SVG (Illustrator / Inkscape), name layers <category>_<element>_<index>
#    Save into 01_svg/

# 3. In Blender: File → Import → SVG, then run scripts/post_svg_import_cleanup.py
#    Scale, apply, origin, 3D mode, sorted into collections by name prefix.

# 4. Apply a render preset
#    scripts/apply_render_preset.py with PRESET="eevee_fast" (or "cycles_fast")

# 5. Set the loop length for the track's BPM
#    scripts/loop_length_calculator.py with BPM=128, BARS=8

# 6. Bake the audio control rig
#    scripts/setup_audio_control_rig.py with AUDIO_PATH=/path/to/track.wav
#    Drive any property off Ctrl_Kick.scale.z in a driver expression.

# 7. Render layers headlessly overnight
~/path/to/blender-helper/cli/render-layers.sh 02_blender/main.blend 03_renders/layers

# 8. Transcode PNG sequences to HAP Alpha for Resolume
for d in 03_renders/layers/*/; do
  ~/path/to/blender-helper/cli/transcode-to-hap.sh "$d" 50 hap_alpha
done

# 9. Drop the HAP MOVs into Resolume's clip browser, set BPM Sync, gig time.
```

## What's inside

```
.
├── CLAUDE.md                            # AI-assistant context — full pipeline brief
├── MCP_SETUP.md                         # Optional: wire blender-mcp into Claude Code
│
├── scripts/                             # Blender Python (paste into Scripting workspace)
│   ├── apply_render_preset.py           # Cycles/Eevee speed presets + output format
│   ├── batch_render_cameras.py          # Iterate cameras, per-camera output folders
│   ├── batch_render_collections_as_layers.py  # Alpha layers for Resolume comp
│   ├── setup_audio_control_rig.py       # 4 control empties baked to audio bands
│   ├── setup_compositor_glow.py         # Stage-vibe compositor node tree
│   ├── setup_emissive_material.py       # Stage-light glow material
│   ├── post_svg_import_cleanup.py       # Standard cleanup after SVG import
│   ├── loop_length_calculator.py        # BPM + bars + fps → scene end frame
│   ├── copy_active_curve_props_to_selected.py
│   ├── set_extrude_on_selected.py
│   ├── set_bevel_depth_on_selected.py
│   ├── select_all_curves_in_collection.py
│   ├── rename_curves_sequential.py
│   └── apply_material_to_selected.py
│
├── cli/                                 # macOS shell wrappers (caffeinate + notify)
│   ├── new-gig.sh                       # Scaffold the standard gig folder
│   ├── render-cameras.sh                # Headless wrapper around batch_render_cameras.py
│   ├── render-layers.sh                 # Headless wrapper around batch_render_collections_as_layers.py
│   ├── render-overnight.sh              # Batch every .blend in a queue folder
│   └── transcode-to-hap.sh              # PNG sequence → HAP / HAP Alpha via FFmpeg
│
├── templates/
│   └── ae-expressions/                  # One .txt per copy-paste expression
│       ├── README.md
│       ├── beat-pulse-scale.txt
│       ├── audio-mapped-range.txt
│       ├── stagger-by-index.txt
│       ├── smooth-wiggle.txt
│       ├── ctrl-null-slider-link.txt
│       ├── bpm-strobe.txt
│       ├── loop-out-cycle.txt
│       ├── posterize-time-step.txt
│       └── random-color-on-beat.txt
│
├── cheatsheet/                          # Reference docs
│   ├── blender-render-presets.md        # Cycles/Eevee speed cheats
│   ├── ae-expressions.md                # Full expression library + explanations
│   ├── resolume-export.md               # Codecs, BPM math, gig folder structure
│   ├── audio-reactive.md                # Blender bake + AE keyframes + Resolume sync
│   ├── cli-batch-render.md              # Blender CLI flags + automation
│   ├── svg-prep-for-3d.md               # Tracing, layer naming, post-import cleanup
│   ├── svg-curve-workflow.md            # Gotchas of SVG-imported curves
│   ├── batch-operations.md              # Bulk-edit methods, ranked by reliability
│   └── mac-keybinds.md                  # Mac shortcuts + macOS conflicts
│
└── troubleshooting/                     # Common pain points with fixes
    ├── copy-to-selected-greyed-out.md
    ├── option-click-not-working.md
    └── active-vs-selected.md
```

## Using the scripts

**Blender Python (`scripts/`)** — open Blender, switch to the **Scripting** workspace, paste the script, edit the `# === EDIT THESE ===` block at the top, click **Run Script** (or `Option+P`).

**CLI shell scripts (`cli/`)** — run from the terminal. All scripts wrap `caffeinate -i` (Mac stays awake) and ping a notification when done. Make sure they're executable: `chmod +x cli/*.sh`.

**AE expressions (`templates/ae-expressions/`)** — open the `.txt`, edit the variables at the top, copy the whole body, paste into AE's expression editor (Option+click the property's stopwatch).

## Using with Claude Code

```bash
cd blender-helper
claude
```

`CLAUDE.md` is read automatically. It tells the assistant:

- Your Blender version (5.x) and OS (macOS).
- The full VJ pipeline you're working in.
- The naming convention scripts rely on (`<category>_<element>_<index>`).
- To prefer one-shot UI actions over Python when the UI works reliably.
- To prefer Python when the UI is genuinely slow or flaky.
- To flag Mac-specific keybind conflicts upfront.
- Which words are banned ("easy", "simple", "just" — show the steps instead).

It also points Claude at the cheatsheet and troubleshooting docs so it doesn't reinvent answers.

You can use this folder without Claude Code — the scripts and docs stand on their own — but the AI experience is better with `CLAUDE.md` in place.

### Optional: blender-mcp integration

If you want Claude Code to drive Blender directly (query scene, run operators, set properties without copy-pasting), see `MCP_SETUP.md`. This is a "later" upgrade and not required.

## What this is NOT

- **Not a tutorial.** Assumes you know Object Mode, Properties panel, basic selection, and the rough shape of an AE/Resolume workflow.
- **Not Windows/Linux-tested.** Mac-focused throughout (caffeinate, osascript, the Blender app path). Most Python is portable; the shell scripts and keybind doc aren't.
- **Not a modelling guide.** It's a batch + render-automation toolkit for an existing pipeline.
- **Not maintained for older Blender versions.** Built against 5.x. Should work on most 4.x but not tested.

## Contributing

PRs welcome if:

- You hit a Mac-specific Blender quirk and you've documented the fix.
- You have a render-time speedup or workflow shortcut that fits the same shape (header docstring, `# === EDIT THESE ===` block, single concern).
- A doc is wrong or outdated for current Blender / AE / Resolume.

PRs less welcome:

- Windows-specific content (this is intentionally Mac-focused — fork for Windows).
- "Do everything" mega-scripts (split into focused single-purpose scripts).

## License

MIT. Use it, fork it, paste any of these scripts into your own projects without attribution.
