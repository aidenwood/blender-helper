# Resolume Export Cheatsheet — Blender / AE → Resolume Arena

Pipeline target: SVG-traced stage photos → Blender → After Effects → **Resolume Arena** for live VJ. Goal is to render every stage element as its own layered loop so you can mix on the fly. Weekly gig cadence means prep has to be repeatable, not bespoke.

---

## 1. Codec Selection for Resolume

Resolume plays anything QuickTime/Media Foundation can open, but "plays" and "plays at 60fps with 12 layers stacked" are different things. For live VJ work you only ever pick from this shortlist: **DXV3, HAP, HAP Alpha, HAP Q, HAP Q Alpha**. NotchLC is in the "would be nice" pile — see note below.

### The shortlist

| Codec          | Alpha | Quality      | File size (relative) | Decode load            | Use when                                                        |
| -------------- | ----- | ------------ | -------------------- | ---------------------- | --------------------------------------------------------------- |
| **DXV3**       | No    | Good         | ~1.0x                | GPU, very low CPU      | Resolume native, default for solid clips with no transparency   |
| **DXV3 Alpha** | Yes   | Good         | ~1.3x                | GPU, very low CPU      | Layered stage elements (what you want most of the time)         |
| **HAP**        | No    | Good         | ~0.7x (smallest)     | GPU, low CPU           | When disk space matters more than absolute quality              |
| **HAP Alpha**  | Yes   | Good         | ~2.0x of DXV alpha   | GPU, low CPU           | Cross-platform projects (TouchDesigner / disguise / VDMX share) |
| **HAP Q**      | No    | Better       | ~2x of HAP           | GPU, slightly more CPU | Gradients, soft shadows, hero clips                             |
| **HAP Q Alpha**| Yes   | Better       | ~2.5–3x of HAP       | GPU, slightly more CPU | Hero layered clips with gradients (foggy beams, soft particles) |

DXV uses DXT compression + LZF; HAP uses DXT + Snappy. Functionally near-identical. Resolume is built around DXV so it's the safest default; HAP/HAP Q is the right pick when you also need the files to play in TouchDesigner, disguise, MadMapper, or VDMX.

### Apple Silicon notes

- DXV3 and HAP all decode on the GPU via Metal on M1/M2/M3/M4. Decode is extremely cheap — the bottleneck is disk I/O, not CPU.
- Tested ceiling: a 14" M1 Pro will run ~26 layers of 4K HAP at 60fps in Arena 7.13+, an M1 Max 32-core GPU runs ~40 layers of 4K at ~58fps (Resolume forum benchmarks).
- HAP `-chunks` flag splits a frame across CPU threads for decompression. On Apple Silicon, set `-chunks 8` for 8/10-core machines, `-chunks 4` on a base M1. Never exceed your physical core count.
- **NotchLC is NOT natively supported in Resolume Arena (as of Arena 7.x — still a feature request on the Resolume forum).** It plays in disguise / TouchDesigner / VDMX / Pixera, but in Resolume you have to transcode it to DXV/HAP. Skip it for this pipeline.

### Why ProRes and H.264 are wrong

**H.264** is a *delivery* codec, not a *playback* codec. It's long-GOP (only every 30th frame is a keyframe), so jumping to a random position forces the decoder to walk back to the last keyframe and reconstruct intermediate frames. Single clip = fine. Twelve stacked, scrubbed, beat-snapped clips = stutter, dropped frames, melted CPU.

**ProRes 4444** is gorgeous and supports alpha, but it's CPU-decoded, intra-frame, and gigantic (~5–10x DXV file size at the same res). One ProRes 4K clip will hammer a CPU core; six will tank the framerate. Use ProRes as a **master/intermediate** out of Blender or AE — never as the final clip Resolume plays.

Rule of thumb: ProRes 4444 between tools, DXV3/HAP into Resolume.

---

## 2. Render-out Formats from Blender that Work in Resolume

The cleanest path is **image sequence → transcode to DXV3 (or HAP Q Alpha)**. Direct video out of Blender adds a re-encode step you didn't ask for and locks you in if you want to re-comp.

### Recommended Blender output

- **For alpha-layered stage elements (most of your work):** PNG sequence, RGBA, 16-bit, transparent background (set `Film → Transparent` to On).
- **For HDR / glow / heavy comp passes:** OpenEXR (Multilayer) Half Float (16-bit). DWA or ZIP compression. Smaller than you'd expect, lossless for practical purposes, and stores values above 1.0 for bloom passes.
- **Avoid 8-bit PNG with alpha** for soft edges — it bands. Use 16-bit PNG or EXR Half.
- **TIFF** is fine but no upside over PNG for VJ work — skip it.

Blender settings:

```
Output Properties → Output
  File Format: PNG
  Color: RGBA
  Color Depth: 16
  Compression: 15%

Output Properties → Format
  Resolution: match your projection (see §7)
  Frame Rate: 60 (or 30 for archival masters)

Render Properties → Film
  Transparent: ON   ← critical for alpha
```

### FFmpeg one-liners (run as pasted; assume `cd` into the sequence folder)

PNG sequence → **DXV3 with alpha** (the Resolume native default for layered work) requires Resolume Alley because FFmpeg doesn't ship a DXV encoder. Drop the folder onto Alley, pick "DXV3", done. If you need a command-line route, see HAP options below.

PNG sequence → **HAP Q Alpha** (best-quality alpha, cross-platform). Note: FFmpeg's HAP encoder does NOT support `hap_q_alpha` directly as of mainline — use `hap_alpha` and accept slightly lower quality, or use [HAPpy](https://github.com/Tedcharlesbrown/HAPpy) / [AfterCodecs](https://aaeplugins.com/plugins/aftercodecs/) / Jokyo for true Q Alpha. **Flagged uncertainty:** verify your FFmpeg build's HAP support with `ffmpeg -h encoder=hap`.

```bash
# PNG sequence → HAP Alpha (works in FFmpeg today)
ffmpeg -framerate 60 -i frame_%04d.png \
  -c:v hap -format hap_alpha -chunks 8 \
  -pix_fmt rgba \
  out_hap_alpha.mov

# PNG sequence → HAP Q (no alpha, best quality colour)
ffmpeg -framerate 60 -i frame_%04d.png \
  -c:v hap -format hap_q -chunks 8 \
  out_hap_q.mov

# PNG sequence → HAP (smallest, no alpha)
ffmpeg -framerate 60 -i frame_%04d.png \
  -c:v hap -chunks 8 \
  out_hap.mov

# EXR sequence → ProRes 4444 master (intermediate, NOT for Resolume direct)
ffmpeg -framerate 60 -i frame_%04d.exr \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le \
  -vendor apl0 \
  master_prores4444.mov

# ProRes 4444 → HAP Q Alpha via FFmpeg (uses hap_alpha — HAP-Q-Alpha needs Alley/HAPpy)
ffmpeg -i master_prores4444.mov \
  -c:v hap -format hap_alpha -chunks 8 \
  out_hap_alpha.mov

# ProRes 4444 → DXV3 → use Resolume Alley GUI, not FFmpeg
# (DXV is closed-source; no FFmpeg encoder exists)
```

**HAP hard requirements:** width and height must both be multiples of 4 (1920×1080 ✅, 1366×768 ❌ — round up). Resolume will reject misaligned dimensions.

### Direct Blender → video?

Skip it for layered work. Blender's built-in MPEG-4 output is fine for previews; for final clips, render to PNG/EXR and transcode. This also gives you a free "re-render the last 200 frames" safety net if Blender crashes mid-render.

---

## 3. Render-out Formats from After Effects that Work in Resolume

AE doesn't natively write HAP or DXV. You have three paths:

1. **AfterCodecs (Autokroma)** — direct HAP/HAP Alpha/HAP Q/HAP Q Alpha export from the AE render queue. Paid (~€95). Worth it if you render multiple HAP clips per week.
2. **Jokyo HAP AeEncoder** — paid, AE-only, supports all HAP variants.
3. **AE → ProRes 4444 → Resolume Alley (or FFmpeg) → DXV3/HAP**. Free, two steps, but it's the safest fallback and the one you should reach for if you don't own AfterCodecs.

The often-cited "Renderheads HAP plugin" is from the Fnordware/Renderheads era and is **discontinued / unmaintained on Apple Silicon**. Don't rely on it for new builds — use AfterCodecs or the ProRes intermediate route.

### Recommended AE render settings

```
Format: QuickTime
Codec: Apple ProRes 4444 (with alpha)
Channels: RGB + Alpha
Depth: Trillions of Colors+ (16 bpc)
Color: Premultiplied (Matted)   ← if compositing on black
       OR Straight (Unmatted)   ← if Resolume will composite further
Resolution: Full (1.0)
```

Premultiplied vs Straight matters: Resolume expects straight (unpremultiplied) alpha for clean edges over arbitrary backgrounds. If your stage element will composite over varying content downstream, render **Straight** out of AE. If it always composites over black (e.g. a beam over a dark stage photo), Premultiplied is fine and slightly smaller.

Then transcode:

```bash
# AE ProRes 4444 (straight alpha) → HAP Alpha for Resolume
ffmpeg -i ae_render_prores4444.mov \
  -c:v hap -format hap_alpha -chunks 8 \
  -pix_fmt rgba \
  out_hap_alpha.mov
```

For DXV3 Alpha, drop the ProRes into **Resolume Alley** (free) and export as DXV3 with alpha. Alley is multi-threaded and uses the GPU — it's faster than the FFmpeg HAP route for big batches.

---

## 4. Folder Structure for a Gig

The folder is the source of truth — Resolume's clip browser reads from disk, so a tidy folder = a tidy panel. Use the same structure every gig and your muscle memory transfers.

```
/Gigs/
└── 2026-05-23_ClubName_Headliner/
    ├── _comp/                      # Resolume comp + saved decks
    │   ├── ClubName_2026-05-23.avc
    │   └── backups/
    ├── _project/                   # Blender/AE source (NOT loaded by Resolume)
    │   ├── blender/
    │   └── ae/
    ├── _masters/                   # ProRes / EXR intermediates (archive)
    │   └── ProRes4444/
    ├── clips/                      # The only folder Resolume actually loads
    │   ├── 01_backdrop/            # Layer 1 — static / slow plate
    │   │   ├── city_skyline_120bpm_8bar.mov
    │   │   └── city_skyline_140bpm_8bar.mov
    │   ├── 02_midground/           # Layer 2 — building silhouettes / structures
    │   ├── 03_beams/               # Layer 3 — light beams, additive
    │   │   ├── beam_sweep_L_120bpm_4bar.mov
    │   │   └── beam_sweep_R_120bpm_4bar.mov
    │   ├── 04_particles/           # Layer 4 — sparks, embers, additive
    │   ├── 05_flash/               # Layer 5 — strobes, hits, 1-bar stabs
    │   └── 06_overlay/             # Layer 6 — text, logos, overlays
    ├── audio/                      # Reference tracks for BPM checks
    └── README.md                   # Gig-specific notes (BPM, deck order, MIDI)
```

Naming convention: `element_descriptor_BPM_BARS.mov`. The BPM in the filename means future-you doesn't have to open every clip to remember it. **Folders 01–06 map directly to layers 1–6 in Resolume** — when you drag-import a folder, Resolume creates one column per file, so each column is a variant of that layer.

---

## 5. Resolume Composition Setup for Layered Blender Renders

### Composition basics

- **Composition → Settings:** Resolution = native projection size (see §7). FPS = 60.
- **Set composition BPM** to the gig's headline tempo (e.g. 128). Tap it in during soundcheck against the DJ's first track.
- **Layer order (bottom → top):** Backdrop → Midground → Beams → Particles → Flash → Overlay. Resolume composites bottom-up, so your backdrop is layer 1.

### Clip transport modes (per clip, in the Transport panel)

- **Play Mode = Loop** for everything. (Other options: Ping Pong, Play Once, Random.)
- **Transport = BPM Sync** for beat-locked clips (beams, flashes, particles). This stretches the clip to fit the composition BPM.
- **Transport = Timeline** for slow plates / backdrops that should play at their rendered speed regardless of BPM.
- **Transport = Hold** for static-feel clips you want frozen until manually triggered.
- **Beat Snap** (toolbar): set to **1 Beat** or **1 Bar** — the next clip you trigger waits until the next beat/bar to fire, so manual triggers stay tight.

### Layer blend modes for additive stage-light feel

- Beams, particles, flashes: **Add** or **Lighten** blend mode. This is the "light through fog" look — bright pixels add together, dark pixels stay dark. No haloing.
- Overlays/text: **Screen** for a softer additive, or **Normal** with the alpha channel doing the work.
- Backdrop layer 1: **Normal** (it's the base).

### A/B deck for live mixing

Arena's Deck panel lets you save multiple "stage layouts" — one deck per song section, or per gig. For live mixing:

- **Deck A**: clips loaded, intro/build energy.
- **Deck B**: clips loaded, drop/climax energy.
- Use the **Crossfader** at the bottom to A/B between two clips on the same layer. Assign the crossfader to a MIDI fader on your controller.
- Save each gig's deck as a separate `.avc` so you can hot-swap between sets.

---

## 6. Loop Points and Beat-Aligned Clips

### Render-time math (do this in Blender BEFORE you hit render)

Frame count for a perfect beat-locked loop:

```
frames = bars × beats_per_bar × fps × 60 / bpm
```

Common 60fps loops at 128 BPM (4/4):

| Bars | Beats | Frames @ 60fps |
| ---- | ----- | -------------- |
| 1    | 4     | 112.5 → 113    |
| 2    | 8     | 225            |
| 4    | 16    | 450            |
| 8    | 32    | 900            |
| 16   | 64    | 1800           |

Worked example: 8 bars × 4 beats × 60fps × 60/128 = **900 frames** exactly. Set Blender's End Frame to 900 (not 901 — see loop trick below).

For **30fps**: divide all frame counts by 2. For non-128 BPM (e.g. 140), recalculate — the formula always works.

### The last-frame-equals-first-frame trick

A clean loop means frame `N+1` should be identical to frame `1`. Render frames `1` through `N`, NOT `1` through `N+1` — Resolume loops by jumping from the last rendered frame back to the first. If you render the duplicate frame, you get a perceptible hitch.

In Blender: animate from frame 1 to frame 901, but set End Frame = 900. The animation should be designed so that the *state* at frame 901 matches frame 1 (e.g. rotation = 360°, position back to start). Same logic in AE — work to N+1 in your timeline, render to N.

### Resolume BPM sync settings

- **Composition BPM** set to the gig BPM.
- Per-clip: **Transport = BPM Sync**, then set **BPM** = the BPM you rendered the clip at, and **Beats** = the number of beats in the loop (e.g. 32 for an 8-bar clip).
- Resolume will time-stretch on playback if the comp BPM differs from the clip BPM. Stretching faster is fine; stretching slower (e.g. clip rendered at 140, played at 120) shows frame doubling on motion-heavy content. **Render at the slowest BPM you expect to play at, then let Resolume speed it up.**

---

## 7. Resolution and Resampling

Render at the **native projector output resolution** wherever possible. Resolume will upscale and downscale on the fly via the GPU, but you pay for it in softness (upscale) or wasted decode bandwidth (downscale).

### Common projection canvases

| Setup                            | Resolution     | Notes                                                                                 |
| -------------------------------- | -------------- | ------------------------------------------------------------------------------------- |
| Single 1080p projector           | 1920×1080      | The bread and butter. Render here.                                                    |
| Ultrawide / two stitched 1080p   | 3840×1080      | One side-by-side canvas. Use Slice Mapping to split to two outputs.                   |
| 4× 1080p grid (LED wall)         | 3840×2160 (4K) | Same as UHD. Render once, slice to 4 outputs.                                         |
| 3× 1080p horizontal              | 5760×1080      | Common for stage wings + centre.                                                      |
| Custom irregular surfaces        | Variable       | Render to a rectangular bounding box, then slice/warp in Advanced Output.             |

**HAP/DXV require multiples of 4.** 5760×1080 ✅. Anything weird, round up and crop in Advanced Output.

How Resolume handles mismatches: Composition resolution is the working canvas. Clips smaller than the canvas are placed at native size (with Size/Position you control). Clips larger are scaled down on the GPU — cheap but blurry if downscale ratio is severe. **Render clips at canvas resolution or an exact integer fraction of it (1/2, 1/4) for clean scaling.**

---

## 8. Slice Mapping — One-Paragraph Crash Course

Resolume's **Advanced Output** (Output menu → Advanced) is the projection-mapping engine. Your composition is a flat canvas; **Slices** are rectangular (or warped) regions you carve out and assign to physical projector outputs. Each slice has an **Input Selection** (which part of the comp it pulls from) and an **Output Transformation** (where it lands on which projector, with corner-pin warp and edge blending for irregular surfaces — stage edges, set pieces, multiple screens). For your photo-traced stage, each traced surface becomes a slice with a corner-pin warp matched to the real-world geometry. You don't need to master this on week one — just know that Advanced Output is where you go when "the projection doesn't line up with the stage". Save the slice map as part of the comp `.avc` so it travels with the gig.

---

## 9. Live Performance Gotchas

- **Pre-load clips before doors.** Trigger every clip you plan to use once in soundcheck — Resolume caches the first chunk in RAM, so the second trigger is instant. Cold clips can stutter on first play.
- **RAM Mode** (right-click clip → Memory → RAM): forces the entire clip into memory. Use sparingly — only for hero short loops on big shows where disk I/O is suspect. Eats RAM fast on 4K HAP Q.
- **Dropped frames on long clips**: long means anything over ~30s at 4K. Decode buffers can stall on slow SSDs. **Keep clips short: 4–16 bar loops, not 2-minute renders.** If you need a 2-minute build, layer multiple short loops with fades and clip triggers rather than one long render.
- **Short loops > long renders** for live use. A 4-bar loop you trigger and layer is infinitely more useful than a fixed 64-bar narrative — you can't beat-match a narrative to a DJ's actual mix.
- **Disable preview rendering** on the engine output during gigs (the small preview window is decoded again — kills perf on multi-projector setups).
- **Lock GPU to high performance** in macOS Energy Saver and Activity Monitor. On Intel Macs use `pmset`; on Apple Silicon, plug in mains and keep the lid open.
- **Audio in Resolume**: bring DJ feed in via the audio input for FFT-driven effects, but don't route house audio THROUGH Resolume. Audio path: DJ → mixer → PA; Resolume just listens.
- **Save every 5 minutes during build.** Resolume crashes are rare but the recovery is a pain.

---

## 10. Pre-Gig Checklist (run 1 hour before doors)

1. [ ] **Composition opens cleanly** from `_comp/` folder — no missing media warnings.
2. [ ] **All clips have correct codec** — spot-check 3 clips: `right-click → File Info`, confirm DXV3 / HAP variant, no stray H.264.
3. [ ] **Composition BPM set** to gig headline tempo (tap against the DJ's first track if known).
4. [ ] **Layer order correct**: Backdrop (L1) → Overlay (L6). Blend modes assigned (Normal / Add / Add / Add / Screen / Normal).
5. [ ] **All clips pre-loaded** — trigger each column once, watch for stutter on first play, retrigger to confirm cached.
6. [ ] **Beat Snap = 1 Beat or 1 Bar**, BPM Sync enabled on beat-locked clips.
7. [ ] **Output resolution matches projector(s)** — confirm in Advanced Output and on the projector OSD.
8. [ ] **Slice Map aligned** — walk the stage, check the projection lines up with the physical surfaces. Re-corner-pin if it shifted in transit.
9. [ ] **MIDI / OSC controller mapped** — test crossfader, layer faders, clip triggers, BPM tap. Mappings saved with the comp.
10. [ ] **Crossfader assigned** and snapped to centre.
11. [ ] **Activity Monitor open on second screen** — eyeball GPU and disk I/O during a full deck rehearsal pass.
12. [ ] **Saved deck snapshot** as `gigname_doors.avc` so a crash recovery returns you to the prepped state.

---

## Quick reference — codec decision tree

```
Need alpha for layered stage element?
├── Yes → DXV3 Alpha (Resolume-only) OR HAP Alpha / HAP Q Alpha (cross-platform)
└── No  → DXV3 (Resolume-only) OR HAP / HAP Q (cross-platform, smaller files)

Need best gradient/colour quality (hero clip)?
└── HAP Q (Alpha) — accept 2x file size

Need maximum number of layers / smallest files?
└── DXV3 or HAP — saves disk and decode budget

Coming from After Effects?
├── Own AfterCodecs → render HAP/HAP Alpha direct from AE queue
└── No plugin → AE → ProRes 4444 → Alley/FFmpeg → DXV3/HAP

Coming from Blender?
└── PNG seq (RGBA 16-bit) or EXR Half → FFmpeg → HAP Alpha (or Alley → DXV3)
```

---

## Sources & further reading

- [Resolume DXV3 Codec](https://resolume.com/software/codec)
- [HAP codec official site (variants + FFmpeg commands)](https://hap.video/using-hap)
- [HAPpy encoder (GUI for HAP including HAP Q Alpha)](https://github.com/Tedcharlesbrown/HAPpy)
- [NotchLC codec specs](https://notchlc.notch.one/) — informational; not natively supported in Resolume
- [Resolume BPM sync docs](https://resolume.com/support/en/bpm)
- [Resolume Advanced Output docs](https://www.resolume.com/support/en/advanced-output)
- [Resolume Output Transformation docs](https://resolume.com/support/en/output-transformation)
- [AfterCodecs (paid AE HAP exporter)](https://aaeplugins.com/plugins/aftercodecs/)
- [Jokyo HAP AeEncoder](https://jokyohapencoder.com/jokyo-hap-aeencoder-hap-encoder-plugin-for-adobe-after-effects/)
- [Apple Silicon performance benchmarks (Resolume forum)](https://resolume.com/forum/viewtopic.php?t=11093&start=90)

### Flagged uncertainties

- **HAP Q Alpha via FFmpeg**: mainline FFmpeg's HAP encoder does not expose `hap_q_alpha`. Use HAPpy, AfterCodecs, or Jokyo for true HAP Q Alpha. Verify your local build with `ffmpeg -h encoder=hap` before assuming it works.
- **NotchLC in Resolume**: not natively supported as of Arena 7.x. Transcode to DXV3/HAP if a NotchLC asset arrives from a collaborator.
- **Exact file-size multipliers** in §1 are typical-content rules-of-thumb; ratios shift with motion complexity and gradient density. Benchmark on your own footage if precise budgets matter.
