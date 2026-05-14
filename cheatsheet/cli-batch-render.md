# Blender CLI & Batch Rendering — VJ / Stage Projection Cheatsheet

Render once, render overnight, render to multiple targets. This guide covers everything you need to drive Blender 5.1.1 from the macOS terminal on Apple Silicon — single frames, full ranges, multi-camera passes, multi-collection layer exports, overnight batch jobs across folders, and headless Python overrides. Built for a weekly VJ gig cadence: SVG-traced photos → Blender → After Effects → Resolume Arena.

---

## 1. The Blender CLI on macOS

### Binary location

The Blender executable on macOS lives inside the `.app` bundle. The actual binary path is:

```bash
/Applications/Blender.app/Contents/MacOS/Blender
```

Anything you can do in Blender's GUI render pipeline you can do from this binary. No GUI required — `-b` (background) mode is the foundation of every batch workflow below.

### Clean zsh alias

Add this to `~/.zshrc` so you can type `blender` anywhere. Sourcing once means every new terminal tab picks it up.

```bash
echo 'alias blender="/Applications/Blender.app/Contents/MacOS/Blender"' >> ~/.zshrc
source ~/.zshrc
```

Verify it works:

```bash
blender --version
```

### Flag overview — the ones you'll actually use

These are the flags that matter for batch VJ work. Order matters in Blender CLI: **the `.blend` file must come before render flags**, otherwise overrides apply to the default startup scene instead of your file.

| Flag | What it does |
|---|---|
| `-b <file.blend>` | Background mode — load `.blend`, no GUI, run, exit |
| `-a` | Render the full animation range set in the `.blend` |
| `-f <frame>` | Render a single frame number |
| `-s <start>` | Override start frame |
| `-e <end>` | Override end frame |
| `-o <path>` | Output path. `#` chars become zero-padded frame numbers |
| `-x 1` | Use the file extension from the format (`.png`, `.exr`, etc.) |
| `-F <FORMAT>` | Output format: `PNG`, `OPEN_EXR`, `OPEN_EXR_MULTILAYER`, `FFMPEG`, `JPEG`, `TIFF` |
| `-E <ENGINE>` | Render engine: `CYCLES`, `BLENDER_EEVEE_NEXT`, `BLENDER_WORKBENCH` |
| `-P <script.py>` | Run a Python script after the file loads, before render |
| `--python-expr "<code>"` | Run an inline Python expression |
| `--cycles-device METAL+CPU` | Force Metal GPU + CPU on Apple Silicon |
| `--` | Everything after this is passed to your Python script as `sys.argv` |

---

## 2. Render a single frame / range from CLI

### Render frames 1–250 of `scene.blend`

This renders the full 250-frame range to a folder, using the file's existing format settings. The `####` in the output path becomes `0001`, `0002`, etc.

```bash
# === EDIT THIS ===
BLEND="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend"
OUT="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/frame_####"

/Applications/Blender.app/Contents/MacOS/Blender -b "$BLEND" -o "$OUT" -s 1 -e 250 -a
```

### Render only frame 120

Single-frame renders are the fastest way to verify lighting or camera framing without committing to a full sequence. Same pattern, `-f` instead of `-a`.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/preview_####" \
  -f 120
```

### Override output path and format from CLI

Force PNG output regardless of what's saved in the `.blend`. `-x 1` ensures the extension is appended so Resolume and AE both pick the sequence up cleanly.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -F PNG \
  -x 1 \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/png_####" \
  -s 1 -e 250 -a
```

For multilayer EXR (useful when you want depth + alpha + cryptomatte going into After Effects), swap the format:

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -F OPEN_EXR_MULTILAYER \
  -x 1 \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/exr_####" \
  -s 1 -e 250 -a
```

### Override the render engine from CLI

EEVEE Next is your VJ workhorse — fast, looks good, motion blur and bloom for free. Override the engine without touching the `.blend`.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -E BLENDER_EEVEE_NEXT \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/eevee_####" \
  -s 1 -e 250 -a
```

### Override the camera from CLI (via `--python-expr`)

There's no built-in `-camera` flag, so we set the scene's active camera via a one-liner Python expression. The expression runs after the file loads, before render starts.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  --python-expr "import bpy; bpy.context.scene.camera = bpy.data.objects['Camera_StageWide']" \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/wide_####" \
  -s 1 -e 250 -a
```

---

## 3. Render multiple cameras to separate folders

For VJ work you often want the same scene from 3–4 angles (wide, close, top-down, performer POV) as separate sequences that Resolume can crossfade between. This script iterates camera names and renders each to its own folder. Paste-and-go — edit the `CAMERAS` array and paths at the top.

```bash
#!/usr/bin/env bash
set -euo pipefail

# === EDIT THIS ===
BLEND="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend"
OUT_ROOT="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/cameras"
START=1
END=250
CAMERAS=("Camera_StageWide" "Camera_Close" "Camera_TopDown" "Camera_POV")
# === END EDIT ===

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"

for CAM in "${CAMERAS[@]}"; do
  OUT_DIR="${OUT_ROOT}/${CAM}"
  mkdir -p "$OUT_DIR"
  echo "▶ Rendering camera: ${CAM} → ${OUT_DIR}"

  "$BLENDER" -b "$BLEND" \
    --python-expr "import bpy; bpy.context.scene.camera = bpy.data.objects['${CAM}']" \
    -F PNG -x 1 \
    -o "${OUT_DIR}/${CAM}_####" \
    -s "$START" -e "$END" -a
done

echo "✓ All camera passes done"
osascript -e 'display notification "All camera passes rendered" with title "Blender Batch"'
```

Save as `~/Desktop/00 - Aidxn/blender-helper/scripts/render-cameras.sh`, then `chmod +x` and run it.

```bash
chmod +x "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/scripts/render-cameras.sh"
"/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/scripts/render-cameras.sh"
```

---

## 4. Render multiple collections as separate "layer" passes

This is the VJ layer-export pattern. Each top-level collection in your `.blend` (e.g. `Stage_Bones`, `Performers`, `Particles`, `Backdrop`) gets rendered alone with alpha enabled, so you can stack and blend them in After Effects or Resolume independently.

The script hides every collection, un-hides one, renders, moves to the next. It also flips the film transparency on so backgrounds come through as alpha.

```bash
#!/usr/bin/env bash
set -euo pipefail

# === EDIT THIS ===
BLEND="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend"
OUT_ROOT="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/layers"
START=1
END=250
COLLECTIONS=("Stage_Bones" "Performers" "Particles" "Backdrop")
# === END EDIT ===

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"

for COL in "${COLLECTIONS[@]}"; do
  OUT_DIR="${OUT_ROOT}/${COL}"
  mkdir -p "$OUT_DIR"
  echo "▶ Rendering layer: ${COL} → ${OUT_DIR}"

  "$BLENDER" -b "$BLEND" --python-expr "
import bpy
scene = bpy.context.scene
scene.render.film_transparent = True
target = '${COL}'
for col in bpy.data.collections:
    hide = (col.name != target)
    for vl in scene.view_layers:
        layer_col = vl.layer_collection.children.get(col.name)
        if layer_col:
            layer_col.exclude = hide
" \
    -F PNG -x 1 \
    -o "${OUT_DIR}/${COL}_####" \
    -s "$START" -e "$END" -a
done

echo "✓ All layer passes done"
osascript -e 'display notification "All layer passes rendered" with title "Blender Batch"'
```

The `film_transparent = True` line is the magic — without it your background colour bleeds into the alpha channel and breaks compositing in AE.

---

## 5. Render multiple `.blend` files in a folder

Overnight batch: every `.blend` in a directory gets rendered using its own internal frame range and output path. Perfect when you've prepped 5–6 scenes during the day and want to wake up to finished sequences.

```bash
#!/usr/bin/env bash
set -euo pipefail

# === EDIT THIS ===
BLEND_DIR="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/queue"
LOG_DIR="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/logs"
# === END EDIT ===

BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
mkdir -p "$LOG_DIR"

shopt -s nullglob
for BLEND in "$BLEND_DIR"/*.blend; do
  NAME="$(basename "$BLEND" .blend)"
  LOG="${LOG_DIR}/${NAME}.log"
  echo "▶ Rendering: ${NAME}"
  echo "  Log: ${LOG}"

  caffeinate -i "$BLENDER" -b "$BLEND" -a > "$LOG" 2>&1 \
    && echo "✓ ${NAME} done" \
    || echo "✗ ${NAME} FAILED — check ${LOG}"
done

osascript -e 'display notification "Overnight batch complete" with title "Blender Batch"'
```

The `caffeinate -i` keeps the Mac awake during the render. Each render's stdout/stderr goes to its own log file so you can debug failures in the morning without scrolling through a single 50MB log.

---

## 6. Headless Python: render with custom settings applied from CLI

When you want to enforce a consistent render config across many `.blend` files — same samples, same codec, same output naming — write a Python file and pass it with `-P`. The script runs after the `.blend` loads, mutates settings, then triggers render.

### The Python file (`render-config.py`)

Save this at `/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/scripts/render-config.py`. It reads CLI args passed after `--`, applies VJ-friendly settings, and renders.

```python
import bpy
import sys
import os

# Parse args passed after `--`
argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

# Defaults — override via CLI
out_path = argv[0] if len(argv) > 0 else "/tmp/render_####"
start    = int(argv[1]) if len(argv) > 1 else 1
end      = int(argv[2]) if len(argv) > 2 else 250
samples  = int(argv[3]) if len(argv) > 3 else 64

scene = bpy.context.scene
r = scene.render

# Output
r.filepath = out_path
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGBA'
r.film_transparent = True
r.use_file_extension = True

# Resolution — VJ delivery is typically 1920x1080 or 1080x1920 portrait
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = 100
r.fps = 30

# Frame range
scene.frame_start = start
scene.frame_end = end

# Engine settings — assumes Cycles. Swap for EEVEE if needed.
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = samples
scene.cycles.use_denoising = True

# Trigger render
bpy.ops.render.render(animation=True)

print(f"✓ Rendered {start}-{end} @ {samples} samples → {out_path}")
```

### Call it from CLI

Everything after `--` flows into the Python script's `sys.argv`. This lets one Python file drive many renders with different output paths and ranges.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -P "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/scripts/render-config.py" \
  -- "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/gig01_####" 1 250 64
```

For an EEVEE Next variant, change `scene.render.engine = 'BLENDER_EEVEE_NEXT'` and replace the Cycles block with `scene.eevee.taa_render_samples = samples`.

---

## 7. Apple Silicon performance flags

### Metal GPU + CPU

On M1/M2/M3/M4 Macs, Cycles renders via Metal. The CLI flag forces Metal GPU plus CPU as combined render devices — usually the fastest config for stage-projection scenes that aren't memory-bound. Always pair this with `-b` background mode for batch jobs.

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  --cycles-device METAL+CPU \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/metal_####" \
  -s 1 -e 250 -a
```

You can also hard-set the device inside your Python script (`scene.cycles.device = 'GPU'`), which is more portable across machines but less explicit at the call site.

### Memory considerations

Unified memory on Apple Silicon means GPU and CPU share the same pool — an M2 Pro with 16GB has roughly 11–12GB usable for renders before macOS starts paging. Heavy SVG-traced geometry (curves with thousands of control points) and 8K textures will tip you over fast. Convert curves to mesh, decimate where you can, and bake high-res displacement to normal maps before overnight runs.

### Thermal throttling on long renders

Macs with passive cooling (MacBook Air) will throttle hard after 20–30 minutes of sustained Cycles renders, dropping render speed by 30–50%. Mitigations: render on AC power not battery, lift the laptop off the desk for airflow, keep ambient cool, and prefer EEVEE Next for long sequences where speed beats absolute quality. For a weekly gig cadence, a MacBook Pro or Mac Studio is the right call.

### `caffeinate -i` for overnight jobs

macOS will sleep mid-render if power settings aren't right, killing your batch. Prefix any long render with `caffeinate -i` to block idle sleep for the lifetime of that process. When the render finishes the caffeinate dies with it — no manual cleanup.

```bash
caffeinate -i /Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/overnight_####" \
  -s 1 -e 250 -a
```

---

## 8. Progress monitoring and notifications

### Pipe output to log files

Blender prints frame-by-frame progress to stdout. Redirect to a timestamped log so you can `tail -f` it from another terminal tab and check progress without interrupting the render.

```bash
LOG="/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/logs/render-$(date +%Y%m%d-%H%M%S).log"

/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/scene.blend" \
  -o "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/job_####" \
  -s 1 -e 250 -a > "$LOG" 2>&1

echo "Log: $LOG"
```

In another tab, watch it live:

```bash
tail -f "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/logs/render-20260514-211530.log"
```

### macOS notifications with `osascript`

`osascript` is built into macOS — zero install. Drop this line after any render command to fire a Notification Centre banner.

```bash
osascript -e 'display notification "Render finished" with title "Blender" sound name "Glass"'
```

Chain it onto a render with `&&` so it only fires on success, or use `;` to fire either way:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b "/path/to/scene.blend" -a \
  && osascript -e 'display notification "Render done ✓" with title "Blender"' \
  || osascript -e 'display notification "Render FAILED ✗" with title "Blender"'
```

### terminal-notifier alternative

`terminal-notifier` is the third-party tool with more control — custom icons, click actions to open Finder at the output folder, sounds. Install via Homebrew, then use in place of `osascript`.

```bash
brew install terminal-notifier

terminal-notifier \
  -title "Blender" \
  -message "Render finished" \
  -sound Glass \
  -open "file:///Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/out/"
```

The `-open` flag is the killer feature — click the notification, Finder jumps straight to the output folder. Worth installing for a weekly gig workflow.

---

## 9. Render farm / cloud options (brief overview)

### Sheep It (free, community-powered)

Free distributed render farm where users earn credits by lending their machines to other people's renders. Quality is fine but queue times are unpredictable (sometimes minutes, sometimes hours depending on credit balance and queue position). Setup is moderate — install their Java client, upload `.blend` with packed textures. Honest take: great for non-urgent personal projects or one-offs, **not reliable for a weekly gig** where you need a deadline guarantee.

### Rebusfarm (commercial, mature)

Pay-per-render service that's been around forever, slick plugin integration with Blender via their "Farminizer" plugin. Pricing is roughly USD $0.01–$0.03 per GhzHr — a 250-frame Cycles sequence might land at $20–$80 depending on complexity. Setup is easy, support is solid, output quality matches local. Worth it for a VJ who's hit a deadline wall on a complex scene, **overkill for weekly EEVEE-based stage projections** that render in 2–3 hours locally.

### Garage Farm (commercial, friendly)

Similar pricing model to Rebus (around $0.012/GhzHr base, often cheaper in practice), with a more startup-feel UX and decent free trial credits. Their CLI uploader is good if you want to script submissions. Honest take: **the best balance of cost and ease for a solo VJ** who occasionally needs to offload — try it before Rebus, the trial credits will cover a small gig.

### Flamenco (free, self-hosted)

Free open-source farm from the Blender Foundation. Self-hosted means you set up a manager on one Mac and workers on others (or cloud VMs). Setup pain is real — networking, shared storage, worker config. Honest take: **only worth it if you already have 2–3 spare Macs or a homelab**. For a solo VJ on one machine, the setup time exceeds the time saved.

### TL;DR for a solo VJ doing weekly gigs

Render locally with the scripts in this doc 90% of the time. Keep a Garage Farm account warm for the 10% of weeks where a complex Cycles scene blows past your deadline. Skip Sheep It (unreliable) and Flamenco (overhead).

---

## 10. Reusable scripts to build next

These three shell scripts cover 90% of the friction points in a weekly VJ render workflow. They're the next thing to build out in `~/Desktop/00 - Aidxn/blender-helper/scripts/`.

### `render-cameras.sh`
Takes a `.blend` path and a list of camera names, renders each camera to its own subfolder with PNG sequence and alpha, fires a macOS notification on completion. Wraps the multi-camera pattern from section 3 into a CLI tool with proper arg parsing. Worth it: every gig has 3–4 camera angles, and clicking through the Blender GUI to swap active cameras eats 5+ minutes per pass.

### `render-layers.sh`
Takes a `.blend` and a list of collection names, exports each as a transparent PNG sequence for AE/Resolume layer compositing. Wraps the multi-collection pattern from section 4. Worth it: this is the single most-repeated VJ task — "give me each element as its own video layer" — and doing it by hand in the Blender outliner is the most error-prone step in the entire pipeline.

### `render-overnight.sh`
Scans a queue folder for `.blend` files, renders each one under `caffeinate -i` with per-file logging, pipes output to timestamped logs, fires a single summary notification at the end with success/fail counts. Wraps section 5 with better reporting. Worth it: drop 5 scenes in the queue folder before bed, wake up to finished sequences and a clean summary of what worked and what didn't.

---

## Quick reference — commands you'll paste weekly

```bash
# Full animation render with notification
caffeinate -i /Applications/Blender.app/Contents/MacOS/Blender \
  -b "/path/to/scene.blend" \
  --cycles-device METAL+CPU \
  -F PNG -x 1 \
  -o "/path/to/out/frame_####" \
  -s 1 -e 250 -a \
  && osascript -e 'display notification "Done" with title "Blender"'

# Single preview frame
/Applications/Blender.app/Contents/MacOS/Blender \
  -b "/path/to/scene.blend" \
  -o "/path/to/out/preview_####" \
  -f 120

# Watch render progress in another tab
tail -f "/Users/aidenwood/Desktop/00 - Aidxn/blender-helper/render/logs/"*.log
```
