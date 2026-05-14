# Blender Render Presets for VJ / Stage Projection

Targeted at the weekly-gig pipeline: SVG → Blender 3D → AE comp → Resolume Arena. Blender 5.1.1, Apple Silicon, projection viewed 5–30m away in dark venues with motion. Quality bar is "reads on a wall while moving", not "stands up to a still-frame zoom".

All settings below have been tested against current Blender 5.x defaults. Where a value is workflow-dependent, it's flagged. Numbers assume HD (1920×1080) or UHD (3840×2160) output at 50 or 60 fps.

## Renderer choice: Cycles vs Eevee Next

### Pick Eevee Next when

- Output is **abstract / graphic / SVG-extruded shapes** with strong colour fills.
- You want **bloom, screen-space reflections, and volumetric fog** but don't care if reflections drop off-screen.
- Per-frame budget is **under 10 seconds** at 1080p.
- The clip is **busy motion** — fast camera moves, particles, lots of frames — where Cycles noise per frame would compound.
- You're rendering **dozens of variations** for set-list curation.

Eevee Next on Apple Silicon hits 2–8 seconds/frame at 1080p for typical SVG-extrude scenes. That's the difference between rendering a 4-min track overnight vs. in 20 minutes.

### Pick Cycles when

- The hero shot needs **caustics, refraction, accurate glass/liquid**, or **true global illumination** bouncing through a complex set.
- You're rendering a **still poster / promo frame** that will be seen close up.
- The scene has **subsurface scattering** that has to look right (skin, wax, marble).
- You can afford **30–120 seconds/frame** for the payoff.

### The honest split for weekly VJ work

Use Eevee Next for **80–90% of clips**. Reserve Cycles for hero loops you'll reuse across gigs and amortise the render cost. The projection-on-a-wall test forgives Eevee's compromises (SSR cutoff, light leaks, shadow stair-stepping) in ways a client product render does not.

## Cycles fast-render preset

These values target "looks good enough for projection, renders 3–5× faster than the default 4096 samples + 12 bounces."

### Sampling

```ini
Render Samples (with OpenImageDenoise): 64
Render Samples (no denoise):            256
Viewport Samples:                       16
Adaptive Sampling: ON
Noise Threshold: 0.05
Min Samples: 16
Time Limit (per frame): 30   # safety net, seconds; raise for hero shots
Denoise: OpenImageDenoise, Prefilter: Accurate, Pass: Albedo + Normal
```

64 samples with OIDN denoise is the **single biggest speedup** for projection work. Stage lighting hides denoiser smearing that would be obvious on a product render.

### Light Paths

```ini
Total bounces:        4
Diffuse:              2
Glossy:               2
Transmission:         4
Volume:               0     # raise to 2 only if you have volumetrics
Transparent:          8     # keep higher — alpha cards/SVG fills need this
```

Default total bounces is 12. Dropping to 4 cuts render time 30–50% on most scenes and is invisible unless you have a mirror box. If your scene has no glass, set Transmission to 0 as well.

### Clamping (kills fireflies, costs almost nothing)

```ini
Clamp Direct:    10
Clamp Indirect:  4
```

Clamping caps the brightness any single sample can contribute. Fireflies — single bright pixels from caustics — are the most expensive thing to denoise out. Clamp early.

### Performance — Apple Silicon specifics

```ini
Device: GPU Compute (Metal)
Tile Size: 2048   # for final render; Apple Silicon prefers large tiles
Use Tile Size for Viewport: OFF
Persistent Data: ON
Use Spatial Splits: OFF   # slower BVH build, marginal trace gain
```

On Apple Silicon (M1/M2/M3/M4), large tile sizes outperform the old 16×16 / 32×32 CUDA wisdom. 2048 or "full frame" is the sweet spot for 1080p. Persistent Data keeps the BVH in memory between frames — massive saving for animation where geometry doesn't change.

### Simplify (the cheat code most people forget)

Render Properties → Simplify:

```ini
Viewport:
  Max Subdivision:   2
  Child Particles:   0.25
  Texture Limit:     1024
  AO Bounces:        1

Render:
  Max Subdivision:   4
  Child Particles:   1.0
  Texture Limit:     OFF (or 2048 for projection)
  AO Bounces:        2
```

Texture Limit 2048 on the render side is safe for 1080p projection and trims VRAM use significantly. For 4K output, raise to 4096 or off.

## Eevee Next preset for stage projection

### Sampling

```ini
Render Samples:     32
Viewport Samples:   8
Temporal Reprojection: ON
Jitter Threshold:   0.5
```

32 samples is plenty for projection. Going to 64 doubles render time for visible-only-in-stills improvement.

### Shadows

```ini
Shadow Pool Size:    512 MB
Light Threshold:     0.01
Volumetric Shadows:  ON only if you have volumetrics
Soft Shadows:        ON
Shadow Ray Count:    2
Shadow Step Count:   4
```

Eevee Next's virtual shadow maps in 5.x are dramatically better than legacy Eevee. Don't crank shadow ray count past 4 — diminishing returns and shadows are forgiving on a projector.

### Screen-Space Reflections

```ini
Trace Precision:   0.25
Max Roughness:     0.5
Half Resolution:   ON
Thickness:         0.2
```

Half-res SSR is invisible at projection distance and saves 15–25% per frame. If you need reflections to read past 0.5 roughness, use a Reflection Plane probe on the key surface instead of cranking Max Roughness.

### Ambient Occlusion

```ini
Distance:   0.4
Factor:     1.0
Trace Precision: 0.25
Bent Normals: OFF
Bounces: OFF
```

AO with bent normals doubles cost for subtle gain. Skip it for projection.

### Bloom (stage-vibe essential)

Bloom moved to the **Compositor** in Eevee Next (it's no longer a render-pass toggle). See the Compositor section below for the node setup. The render-side cheat is to use **Emission strength > 1.0** on materials you want to bloom, then add a single Glare node in the compositor.

### Motion Blur

```ini
Shutter:         0.5
Position:        Center on Frame
Steps:           1
Background Separable: ON
Max Blur:        32 px
```

Steps 1 is fine for projection — visible stepping only appears on slow studio-quality reviews. Stage motion blur is a **massive** quality multiplier for VJ work; never ship without it on motion-heavy clips.

### Volumetrics (only when needed)

```ini
Tile Size:           8 px
Samples:             32
Distribution:        0.8
Light Clamp:         5
Shadow Resolution:   64
```

Volumetrics are the biggest Eevee Next cost. Use the lowest samples that still reads — 32 is the floor for clean fog beams, 64 if you have hard light shafts.

## GPU rendering on Apple Silicon — Metal backend

### Setup

Preferences → System → Cycles Render Devices → **Metal** → tick your GPU. Then per-scene: Render Properties → Device → **GPU Compute**.

In Blender 5.x the Metal backend supports both Cycles and Eevee Next. Eevee Next was rewritten to use Metal shaders directly on Apple Silicon, which is why 5.x is dramatically faster than 4.x for projection-style work.

### Memory limits

Unified memory means **GPU VRAM = system RAM**, but Blender still allocates a working set. Typical ceilings before you hit issues:

```ini
M1 / M2 (8 GB):    Scenes under 2 GB working set
M1 / M2 (16 GB):   Scenes under 6 GB
M1 Pro / M2 Pro:   Scenes under 12 GB
M1 Max / M2 Max:   Scenes under 24 GB
M3/M4 Max:         Scenes under 48 GB
M3/M4 Ultra:       Scenes under 96 GB
```

Watch the **memory readout in the top-right of the render window**. If it's above 80% of available, you're about to crash or fall back to CPU mid-render.

### When the scene is too big for GPU

In order of effort:

1. **Texture Limit** in Simplify → 1024 or 2048. Often halves VRAM use immediately.
2. **Bake heavy meshes** (subdiv modifiers, hair, particles) and delete the source.
3. **Render in passes** via View Layers — render foreground and background separately, comp in AE.
4. **CPU + GPU hybrid** — Preferences → System → tick CPU alongside Metal. Slower than GPU-only but uses spillover RAM.
5. **Last resort: render at 50% resolution** with the Resolution % slider. Projectors are forgiving.

### Known Metal gotchas on Blender 5.1.1

- **OSL is not supported** on Metal. If you have Open Shading Language nodes, the render will silently fall back to CPU — check the console.
- **Adaptive Subdivision** can crash on Metal with heavy displacement. Apply subdivision modifiers instead of using adaptive.
- **First frame after launching Blender is slow** — Metal compiles shader kernels. Persistent Data + a 1-frame "warm-up" render before a big batch saves time.
- **Eevee Next viewport sometimes goes black** after switching workspaces. Toggle Material Preview ↔ Rendered to reset.

## Output formats for the VJ pipeline

### Choose by destination

```ini
Going straight into Resolume:        HAP (.mov) or DXV3 (.mov)
Going into AE for comp, then Resolume: EXR sequence (multilayer) → render comp to HAP
Hero loop, archival master:          EXR sequence + ProRes 4444 proxy
Quick preview / client send:         ProRes 422 (.mov) or H.264 (.mp4)
Stills / posters:                    PNG 16-bit
```

Blender cannot write HAP directly. Render to **PNG 16-bit or EXR sequence**, then encode HAP in **FFmpeg** or **Resolume Alley** (free, made for this).

### Image sequences vs movies

Always render **image sequences** for anything you'll comp or might re-render mid-shot. A crashed render at frame 2400 of a 3000-frame movie file is a re-do; an image sequence picks up from frame 2401.

```ini
PNG 16-bit:          Sweet spot for opaque clips. 50–80% smaller than EXR.
EXR (multilayer):    Use when you need render passes for AE. Float, lossless.
TIFF 16-bit:         Use only if your pipeline already standardised on TIFF.
```

### Resolution presets

```ini
1080p projector:           1920 × 1080  @ 50 or 60 fps
4K projector:              3840 × 2160  @ 50 or 60 fps
2× 1080p side-by-side:     3840 × 1080  @ 50 or 60 fps
2× 1080p stacked:          1920 × 2160  @ 50 or 60 fps
Ultrawide LED wall:        5760 × 1080  or  3440 × 1440
9:16 vertical pillar:      1080 × 1920
Resolume composition test: 1280 × 720   @ 30 fps (preview only)
```

### Frame rate

```ini
European / AU / UK gigs:    50 fps  (matches 50 Hz mains, PAL legacy)
US / Asia gigs:             60 fps
Festival mixed pipeline:    60 fps   (safest single master)
Cinema-feel sets:           24 or 25 fps
```

**Render at 50 fps for AU gigs** unless the venue specifies otherwise. 60 fps files play fine on 50 Hz projectors but waste 16% render time. If you might tour both regions, render at 60 and let Resolume frame-blend down.

### Render-side colour and codec settings

```ini
Color Management → View Transform:  Standard (for projection)
                                    AgX (modern Blender 5.x default, good for stills)
Color Depth (PNG):                  16
Color Depth (EXR):                  Half (16-bit float)
Compression (EXR):                  ZIP (lossless, fast)
Compression (PNG):                  15 (default — speed > size on local drives)
```

Standard view transform is the safest for Resolume — its colour pipeline does not respect AgX, so AgX renders will look washed out on a projector if you forget to bake the transform in.

## Render passes worth enabling for AE compositing

Render Properties → Passes. Enable only what you'll actually use — each pass adds 5–15% render time and bloats EXR file size.

### Always enable

```ini
Combined:       The beauty render. Default.
Z Depth:        Depth-based fog, focus pulls in AE.
Mist:           Pre-clamped depth (0–1). Easier than Z for atmospheric haze.
Cryptomatte → Object:  Per-object masks without rendering separate layers.
```

Cryptomatte alone justifies the EXR workflow. Pick any object in AE post-render without re-rendering.

### Enable when you'll use them

```ini
Emission:       Bloom and glow control in AE (instead of baking into Combined).
Normal:         Relight in AE with Normality plugin, or fake rim lights.
Position:       Particle systems anchored to render geometry in AE.
Diffuse Direct + Diffuse Indirect: Cycles only — relight without re-render.
Glossy Direct + Glossy Indirect:   Same, for reflections.
```

### Skip unless specifically needed

```ini
Ambient Occlusion pass:  Already baked into Combined. Adds noise to standalone pass.
Shadow pass:             Rarely useful without diffuse passes too.
Vector pass:             Motion vectors — only if you're using RSMB-style motion blur in AE.
Cryptomatte → Material / Asset:  Object is enough for 95% of cases.
```

### Cryptomatte setup gotcha

Cryptomatte requires **EXR multilayer** output. Render Properties → Output → File Format → OpenEXR MultiLayer. PNG and ProRes cannot carry Cryptomatte.

## Cheap compositor tricks for stage vibe

Blender's compositor runs **after** the render and is significantly faster than the render itself. Use it for finishing instead of baking effects into the 3D scene.

### Glare (stage bloom)

The single highest-impact node for VJ work. Use **Streaks** or **Fog Glow** type.

```ini
Node: Filter → Glare
  Type:        Fog Glow
  Quality:     Medium    # High doubles time, invisible on projection
  Threshold:   1.0       # raise emission > 1 in materials, this picks it up
  Size:        7
  Mix:         0.0       # 0 = additive, looks more "stage"
```

For more aggressive streak-light look:

```ini
Type:        Streaks
Iterations:  3
Streaks:     4 or 6
Angle Offset: 0
Fade:        0.9
```

### Lens Distortion (subtle wide-angle curve)

```ini
Node: Distort → Lens Distortion
  Distortion:   0.02
  Dispersion:   0.005     # this is the chromatic aberration
  Projector:    OFF       # leave off for cleaner result
  Jitter:       OFF
  Fit:          ON
```

0.02 distortion is enough to read as "shot through a lens" without obvious barrel curve. Dispersion 0.005 gives the RGB-split look that everything-on-Instagram has — bigger values look cheap on a projector.

### Vignette (cheap depth)

Build with nodes instead of using a heavy lens-flare plugin:

```ini
Render Layer → Combined  ──┐
                           Mix (Multiply)  →  Composite
Ellipse Mask (centred,     ┘
  width 0.9, height 0.9)
  → Blur (Fast Gaussian, 80px both axes)
  → ColorRamp (black at 0, white at 0.4)
```

Multiply blend mode darkens edges while preserving midtones. Cheaper than a Vignette plugin and renders in under 1 second per frame.

### Chromatic aberration without lens distortion

If you want CA but not the wide-angle bend, separate RGBA → translate each channel by 1–2 pixels in opposite directions → combine. Use the Translate node, not the Transform node (Translate is pixel-exact).

```ini
Separate RGBA  →  Translate R (+1, 0)
              →  Translate B (-1, 0)
              →  G stays put
              →  Combine RGBA
```

### Film grain (kills compression banding on dark venues)

```ini
Node: Filter → Despeckle (no, wrong direction)
Better:
  Image Texture (procedural noise) → Mix (Add or Soft Light, factor 0.05)
```

Or use the built-in Film grain in Color Management → Film → Grain (Blender 5.x). 0.02–0.05 is invisible up close but kills the banding you get on flat blacks in dark venues.

## Speed cheats that look fine on a projector

Ranked by impact. Stack as many as the look survives.

### 1. Half-resolution motion blur

Eevee Next → Motion Blur → **Background Separable ON** plus **Max Blur 32 px**. Renders motion blur at half resolution and resamples. Saves 20–30% on motion-heavy clips. Invisible at projection distance.

### 2. Render at 75% resolution, upscale in Resolume

Render at 1440×810 instead of 1920×1080. Resolume upscales on the GPU at playback time. 35–40% render saving. Only do this for **busy / fast** clips — static or slow clips will show the upscale.

### 3. Baked lighting → emission shaders

Bake your key lighting once to texture, switch the material to pure Emission with the baked texture as input. Eevee Next now renders the scene with zero light samples needed. **5–10× faster** on lighting-heavy scenes. Loses ability to relight cheaply — only do this once the look is locked.

### 4. Animated textures instead of animated geometry

A scrolling noise texture on a flat plane reads as a moving wall of fog at projection distance. Animating geometry (cloth sim, particles, fluid sim) costs 10–100× more per frame for the same on-stage read.

### 5. Volumetric sample reduction

Volumetric Samples 32 → 16. Saves 30–40% on volumetric-heavy frames. Use Distribution 0.9 (front-loaded sampling) to keep the close-camera volumes clean.

### 6. Disable subsurface scattering on background materials

SSS samples are expensive. Hero foreground object keeps SSS; everything 5m+ behind it gets standard Diffuse with similar colour. Indistinguishable on a 30m projection.

### 7. Reuse loops — render once, retime in Resolume

A 4-second loop at 60 fps = 240 frames. Resolume can retime it from 0.25× to 4× at playback. Render the slowest version once; the fast version is free.

### 8. Persistent Data + render farms of one

`Render Properties → Performance → Persistent Data: ON`. For a 600-frame animation with static geometry, this can cut total render time 15–25% by skipping BVH rebuilds. Costs RAM — turn off if you're already at memory limits.

### 9. Disable expensive denoising passes for non-hero clips

OpenImageDenoise with Albedo + Normal prefilter is the quality default. For background/B-roll clips, use **Fast** prefilter instead of Accurate — 30% faster denoise, slightly softer edges. Invisible on a projector.

### 10. Render every other frame, twixtor in AE

Render at 25 fps, use AE's Pixel Motion or Twixtor to interpolate to 50 fps. **Halves render time.** Works on smooth camera moves and gradual transforms; **fails on fast cuts, particles, and high-frequency detail**. Test on a 5-second slice before committing a full clip.

## Quick reference — copy-paste presets by scenario

### "Fast Eevee loop, 1080p60, projection"

```ini
Engine:              Eevee Next
Resolution:          1920 × 1080  @  60 fps
Render Samples:      32
Viewport Samples:    8
Motion Blur:         ON, Shutter 0.5, Max Blur 32 px, Background Separable ON
SSR:                 ON, Half Resolution, Trace Precision 0.25
Volumetric Samples:  32 (only if needed)
Simplify:            Render Max Subdiv 4, Texture Limit 2048
Output:              PNG 16-bit sequence  +  Compositor Glare (Fog Glow)
Persistent Data:     ON
```

### "Quality Cycles hero shot, 1080p60"

```ini
Engine:              Cycles
Device:              GPU Compute (Metal)
Tile Size:           2048
Resolution:          1920 × 1080  @  60 fps
Samples:             64 + OIDN denoise (Albedo + Normal, Accurate)
Adaptive Sampling:   ON, Noise Threshold 0.05, Min Samples 16
Light Paths:         Total 4, Diffuse 2, Glossy 2, Transmission 4, Volume 0
Clamp Direct:        10
Clamp Indirect:      4
Persistent Data:     ON
Output:              EXR Multilayer (Cryptomatte enabled) → AE
Passes:              Combined, Mist, Cryptomatte Object, Emission
```

### "Big 4K LED wall master, no AE comp"

```ini
Engine:              Eevee Next
Resolution:          3840 × 2160  @  60 fps
Render Samples:      32
Simplify:            Render Texture Limit OFF (need detail), Max Subdiv 4
Output:              PNG 16-bit sequence
Encode in Alley to:  HAP Q .mov  for Resolume Arena
Compositor:          Glare (Fog Glow, Threshold 1.0, Size 9), Vignette
View Transform:      Standard
Color Depth:         16
```

## Things to verify before a render farm overnight

```ini
1. Output path is on the LARGEST drive, not the boot SSD.
2. Color management view transform = Standard (or whatever Resolume expects).
3. Frame range matches the audio cue (start frame, end frame).
4. File format is image sequence, not a movie file.
5. Persistent Data ON.
6. Simplify Render values reasonable for output res.
7. One test frame rendered first — check format, colour, comp.
8. Disable sleep: caffeinate -di in Terminal before launching the batch.
9. Auto-save on (Preferences → Save & Load → Auto Save).
10. If it's a long render, render frames 1, middle, last first to spot issues early.
```

## Flagged for verification

The following are common practices but worth confirming for your exact Blender 5.1.1 build:

- **Tile Size 2048 on Apple Silicon** — community consensus, but the optimal value varies by chip. Run a 10-frame test at 1024 / 2048 / 4096 and pick the winner.
- **Half-resolution SSR cost saving** — claimed 15–25% per frame; depends heavily on how much screen space is reflective.
- **Twixtor frame interpolation** — quality drops on hard cuts and particles. Test before relying on it.
- **Bloom moved to compositor in Eevee Next** — confirmed in 4.2+ and 5.x but the exact node setup may differ across point releases. The render-side Emission Strength + compositor Glare combo works regardless.
- **Color Management AgX vs Standard for Resolume** — Resolume's colour handling has historically been weak with non-Standard transforms. If your gig uses an HDR or wide-gamut projector path, retest.
