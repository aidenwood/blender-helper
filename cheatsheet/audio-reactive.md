# Audio-Reactive Animation — VJ / Stage Projection Pipeline

End-to-end audio-reactivity cheatsheet for the SVG → Blender → After Effects → Resolume Arena workflow. The goal: bake one render template that can be re-fired against different tracks per gig with minimal per-track work.

The single most powerful pattern below is **Blender's "control empty" rig** — one empty per frequency band, each baked from `Bake Sound to F-Curve`, then every animatable property in the scene driven off `var.scale.z`. Swap the audio file, rebake the empties, the whole scene reacts. Section 2 + Section 3 together.

---

## 1. Blender — Bake Sound to F-Curve

This is the foundational technique. It takes a `.wav`/`.mp3`/`.flac`, runs an envelope follower over a frequency band, and writes one keyframe per frame onto whatever F-Curve you have selected. Once baked, the animation lives in the file — no audio playback needed at render time.

### Exact workflow

1. Select your target object (or an empty acting as a control).
2. Hover the property you want to animate (e.g. Z scale) and press `I` to insert one keyframe — this creates the F-Curve.
3. Open the **Graph Editor** and click the F-Curve so it's the active channel.
4. With the mouse hovered over the Graph Editor, menu: `Key → Bake Sound to F-Curve` (or `Channel → Bake Sound to F-Curves` in 4.x).
5. Pick your audio file. The bake dialog opens.
6. Set parameters (below), hit `Bake Sound to F-Curve`. Wait — long tracks at 60fps can take 30–60s.

### Bake dialog parameters

| Parameter | What it does | Notes |
|---|---|---|
| **Lowest frequency** | Low cutoff of band-pass filter (Hz) | Default 0 |
| **Highest frequency** | High cutoff (Hz) | Default 100000 |
| **Attack time** | Rise smoothing (seconds) | 0.005–0.05 typical |
| **Release time** | Fall smoothing (seconds) | 0.1–0.3 typical |
| **Threshold** | Noise floor — anything below is zeroed | 0.0 keeps everything |
| **Accumulate** | Each value adds to the previous (monotonic ramp) | For "total energy" counters |
| **Additive** | Adds to existing F-Curve value instead of overwriting | Layering multiple bakes |
| **Square** | Hard-clip to 0 or 1 — turns envelope into a gate | Beat triggers |

### Recommended ranges per drum element

| Element | Low (Hz) | High (Hz) | Attack | Release | Threshold | Square |
|---|---|---|---|---|---|---|
| **Kick** | 40 | 90 | 0.005 | 0.15 | 0.05 | off |
| **Kick (gated trigger)** | 40 | 90 | 0.002 | 0.08 | 0.15 | **on** |
| **Snare body** | 150 | 300 | 0.005 | 0.18 | 0.04 | off |
| **Snare crack** | 1500 | 4000 | 0.005 | 0.12 | 0.03 | off |
| **Hat / cymbals** | 5000 | 12000 | 0.003 | 0.08 | 0.02 | off |
| **Mid (vocals/synth)** | 300 | 2000 | 0.01 | 0.2 | 0.0 | off |
| **Full mix amplitude** | 0 | 22000 | 0.01 | 0.25 | 0.0 | off |
| **Sub bass only** | 20 | 60 | 0.005 | 0.2 | 0.05 | off |

For kick especially, use a narrower band than you think — 40–90Hz cleanly rejects most snare bleed. If your kick has click in the 2–4kHz range, bake a second curve for the click and add them in a driver.

### Frame rate gotcha

The bake runs at the scene's frame rate. Change framerate after baking and your timing drifts — rebake. For 24fps cinematic comps the envelope can feel coarse on fast hats; bump to 60fps for VJ work even if you're rendering 30.

---

## 2. Blender — Audio Drivers

The bake gives you one F-Curve per call, which is fine until you want twelve objects pulsing on the kick. Bake once to a "control empty," then drive every property off that empty's scale.

### Rig setup

1. Add an empty named `Ctrl_Kick`. Add empties `Ctrl_Snare`, `Ctrl_Mid`, `Ctrl_Hat` too.
2. Select `Ctrl_Kick`, in N-panel set Z scale to 1, press `I` over the Z scale field.
3. In the Graph Editor, isolate that Z scale F-Curve. `Key → Bake Sound to F-Curve` with kick settings (Section 1).
4. Repeat for each empty with its band's settings.
5. Now anywhere in the scene: right-click any property → `Add Driver` → expression below.

### Driver variable setup (every driver below uses this)

In the driver panel:
- Variable name: `kick`
- Type: `Single Property`
- Object: `Ctrl_Kick`
- Path: `scale.z`

Repeat for `snare`, `mid`, `hat` as needed.

### Clamped pulse (most common)

Maps audio amplitude into a controlled property range. Use for scale, emission strength, bloom intensity.

```python
# Driver expression — scale property pulsing 1.0 → 1.5
1.0 + min(kick, 1.0) * 0.5
```

```python
# Emission strength pulsing 2.0 → 12.0
2.0 + min(max(kick, 0.0), 1.0) * 10.0
```

### Smoothed pulse (low-pass / inertia)

Raw bakes can jitter on transient-heavy material. Blender drivers can't hold state between frames natively, so smooth at bake time (longer Release) OR use a second control empty baked with a slow Release as your "smooth" channel:

```python
# Blend raw kick with smooth kick — 30% snappy, 70% smoothed
kick * 0.3 + kick_smooth * 0.7
```

Bake `kick_smooth` with Release = 0.5 and Attack = 0.05 for that lazy follow.

### Threshold trigger (kick-only, ignore everything below)

```python
# Outputs 1.0 if kick fires above 0.35, else 0.0
1.0 if kick > 0.35 else 0.0
```

For a softer trigger with a falloff envelope, bake the kick channel with **Square** on — the envelope becomes a clean 0/1 gate at the bake stage and you don't need driver logic.

### Hold-and-decay (peak follower in driver)

True peak-and-decay needs state. Easiest path: bake a second channel with a very long Release (1.5–3s), then read that. Or bake with `Accumulate` on for a true running maximum.

### Beat counter (integer increments)

Bake the kick channel with **Square** + **Accumulate**. Each kick adds 1 to the running total. Then in a driver:

```python
# Rotate 30 degrees per kick
kick_count * 0.5236   # 30 degrees in radians
```

```python
# Cycle through 4 colour states
kick_count % 4
```

This is the killer feature for stage work — predictable, beat-locked counters baked into the file.

---

## 3. Blender — Python: bake multiple bands at once

Drop this into the Scripting workspace, edit `AUDIO_PATH`, run. Creates four control empties at the origin, each baked to its frequency band. Then drive everything off `bpy.data.objects["Ctrl_Kick"].scale.z` etc.

```python
import bpy

AUDIO_PATH = "/Users/aidenwood/Desktop/track.wav"

BANDS = [
    # (name, low_hz, high_hz, attack, release, threshold, accumulate, additive, square)
    ("Ctrl_Kick",   40,    90,    0.005, 0.15, 0.05, False, False, False),
    ("Ctrl_Snare",  150,   400,   0.005, 0.18, 0.04, False, False, False),
    ("Ctrl_Mid",    300,   2000,  0.01,  0.20, 0.00, False, False, False),
    ("Ctrl_Hat",    5000,  12000, 0.003, 0.08, 0.02, False, False, False),
]

scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base
print(f"Baking at {fps} fps, range {scene.frame_start}-{scene.frame_end}")

for i, (name, lo, hi, atk, rel, thr, accum, add, sq) in enumerate(BANDS):
    # Create or reuse empty
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
    else:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(i * 2, 0, 0))
        obj = bpy.context.active_object
        obj.name = name

    # Clear existing animation
    if obj.animation_data and obj.animation_data.action:
        bpy.data.actions.remove(obj.animation_data.action, do_unlink=True)

    # Seed the F-Curve with a keyframe on scale Z
    obj.scale.z = 1.0
    obj.keyframe_insert(data_path="scale", index=2, frame=scene.frame_start)

    fcurve = obj.animation_data.action.fcurves.find("scale", index=2)

    # Bake — needs a Graph Editor area context override
    area = next((a for a in bpy.context.screen.areas if a.type == 'GRAPH_EDITOR'), None)
    if area is None:
        # Hijack the current area temporarily
        old_type = bpy.context.area.type
        bpy.context.area.type = 'GRAPH_EDITOR'
        area = bpy.context.area
    else:
        old_type = None

    # Select only this fcurve
    for fc in obj.animation_data.action.fcurves:
        fc.select = False
    fcurve.select = True

    with bpy.context.temp_override(area=area):
        bpy.ops.graph.sound_bake(
            filepath=AUDIO_PATH,
            low=lo,
            high=hi,
            attack=atk,
            release=rel,
            threshold=thr,
            use_accumulate=accum,
            use_additive=add,
            use_square=sq,
        )

    if old_type is not None:
        bpy.context.area.type = old_type

    print(f"Baked {name}: {lo}-{hi}Hz")

print("Done. Drive properties off ObjectName.scale.z")
```

### Using the rig

After running, any property in the scene can pull from these. Right-click → Add Driver → Single Property → Object `Ctrl_Kick` → Path `scale.z`. Repeat for the others. Section 2 has the working expressions.

### Re-baking for a new track

Change `AUDIO_PATH`, re-run. The script clears existing animation on each empty first, so it's idempotent. Every driver in the scene picks up the new bake automatically — that's the whole win.

---

## 4. After Effects — Convert Audio to Keyframes

The AE equivalent of Blender's sound bake. Drops a stack of Slider Control keyframes onto a null, one per frame, for Left / Right / Both channels.

### Workflow

1. Drag audio into the comp. Make sure it covers the full timeline.
2. Select the audio layer.
3. `Animation → Keyframe Assistant → Convert Audio to Keyframes`.
4. AE creates a layer called `Audio Amplitude` with three Slider Controls: Left Channel, Right Channel, Both Channels.
5. The sliders are keyframed every frame with raw audio amplitude in arbitrary units (typically 0–30 range, can spike higher on loud masters).

### Settings to check first

- The audio layer's **Audio Levels** (volume) is sampled — if you've turned the layer down, the bake is quieter. Reset to 0dB before baking.
- AE bakes at the comp frame rate. Same gotcha as Blender — change frame rate, rebake.
- Long comps (10min+) can take 10–30s; AE freezes during the bake.

### What the keyframes look like

Each frame is an independent keyframe with a numeric value. No interpolation, no smoothing. On a typical loud track expect Both Channels to swing between 0 and 25–40. You'll almost always remap with `linear()` before using.

### Smoothing and scaling expression

Pick-whip a property to `Both Channels`, then wrap the expression:

```javascript
// Scale 0-50 range of audio amplitude onto a 100-150 scale
amp = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");
s = linear(amp, 0, 50, 100, 150);
[s, s]
```

For temporal smoothing (low-pass), sample the previous N frames:

```javascript
// 5-frame moving average — kills the jitter
src = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");
n = 5;
total = 0;
for (i = 0; i < n; i++) {
  total += src.valueAtTime(time - i * thisComp.frameDuration);
}
total / n
```

Drop that on a separate Slider Control called "Smoothed" and pick-whip from there.

---

## 5. After Effects — FFT / Spectrum Analysers

`Convert Audio to Keyframes` only gives you amplitude — total loudness. For frequency-specific reactivity (kick vs snare vs hat) you need FFT.

### Trapcode Sound Keys (paid, the standard)

Part of Red Giant Trapcode Suite. Apply to an audio layer, opens a spectrum view, you draw frequency band selections directly on the spectrum. Each band becomes a keyframed slider you can pick-whip.

- Up to 8 simultaneous bands in one instance.
- Real-time spectrum preview — scrub the track and watch which bands light up.
- Outputs already smoothed, attack/release built-in.
- About $200 standalone or as part of Suite.

If the project budget supports it, Sound Keys is the path. It's the AE equivalent of running Blender's sound bake four times with different frequency ranges, except interactive.

### Free alternative — Audio Spectrum effect trick

`Effect → Generate → Audio Spectrum` is designed for visualisation but you can sample its output. Set Start Frequency and End Frequency to bracket your band (e.g. 40–90 for kick), set Frequency Bands to 1, and the effect's "Maximum Height" parameter ends up driven by that band's energy.

Then sample the rendered pixel brightness via a layer reference, or — easier — use it as a visualisation while you eyeball where to set thresholds in Sound Keys / your driver.

### Free alternative — pre-bake in Blender, export to AE

Honestly the cleanest free path: bake your four bands in Blender (Section 3), export the F-Curve values as a CSV, import into AE as keyframes on a null. Tedious but free, and you keep one source of truth between the two apps.

### When you actually need FFT

- Multiple elements reacting to different drums independently.
- Vocal-driven mouth animation or lyrics overlays (1–4kHz band).
- Track has a distinct lead synth you want to highlight (depends on the track — find it on a spectrum view).

For full-mix amplitude pulsing, the free Convert Audio to Keyframes is fine.

---

## 6. The "Audio Amplitude → Controlled Animation" Expression

The canonical AE pattern. Memorise this — every other audio-reactive expression is a variant.

```javascript
// === AUDIO-REACTIVE CONTROLLED ANIMATION ===
// Maps audio amplitude onto a property with min/max range and easing

amp = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");

// Input range — what raw amplitude values to expect from the track
inMin = 5;     // Floor — below this, output sits at outMin
inMax = 40;    // Ceiling — above this, output clamps at outMax

// Output range — the property's resting and peak values
outMin = 100;  // Resting (silence)
outMax = 130;  // Peak (loudest)

// Optional ease curve — 1 is linear, >1 emphasises peaks, <1 emphasises quiet
easeExp = 1.5;

// Clamp + normalise
t = linear(amp, inMin, inMax, 0, 1);

// Apply ease
t = Math.pow(t, easeExp);

// Map to output
v = linear(t, 0, 1, outMin, outMax);

[v, v]   // for scale; use just `v` for opacity, rotation, single-value props
```

### Variants

**Opacity flash on loud beats:**

```javascript
amp = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");
linear(amp, 10, 35, 20, 100)
```

**Position bounce (Y-axis kick):**

```javascript
amp = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");
y = transform.position[1] - linear(amp, 8, 30, 0, 40);
[transform.position[0], y]
```

**Smoothed (kills jitter — combine with Section 4 smoother on a separate slider):**

```javascript
amp = thisComp.layer("Audio Amplitude").effect("Smoothed")("Slider");
s = linear(amp, 3, 25, 1.0, 1.4);
[s * 100, s * 100]
```

### Calibrating inMin / inMax

Park the playhead on a loud section. Note the Slider value (e.g. 38). Park on a quiet section (e.g. 6). Use those as `inMax` and `inMin`. Wrong calibration is why audio-reactive AE comps look dead or maxed-out — it's never the expression, it's the range.

---

## 7. Beat-Locked vs Amplitude-Driven

Two philosophies, both valid, hybrid is best for gigs.

### Amplitude-driven

Property follows audio amplitude in real time. Reactive, alive, but messy — quiet sections drop out, ghost notes wobble things, mastering changes between tracks break your range calibration. **Good for: organic looks, smoke, particles, glow.** Bad for: anything that needs to land on the 1.

### Beat-locked

Property animates on a fixed BPM grid regardless of what the audio is doing. Predictable, snappy, reliable across tracks of the same BPM. But ignores dynamics — your visual hits the beat in a drop and in a breakdown identically. **Good for: hard cuts, strobes, geometric pattern switches, text reveals.** Bad for: feeling responsive to the music's actual energy.

### Hybrid pattern — amplitude within beat windows

The gig-reliable approach: beat-locked timing for *when* things happen, amplitude for *how much*. Example: a logo pulses on every beat (beat-locked) but the pulse amount scales with the kick's amplitude that frame (amplitude-driven).

```javascript
// AE — beat-locked pulse with amplitude-driven intensity
bpm = 128;
beatDur = 60 / bpm;
phase = (time % beatDur) / beatDur;     // 0-1 across each beat
beatEnvelope = Math.pow(1 - phase, 4);  // sharp decay from 1 to 0

amp = thisComp.layer("Audio Amplitude").effect("Both Channels")("Slider");
intensity = linear(amp, 5, 35, 0.3, 1.0);

s = 100 + beatEnvelope * intensity * 30;
[s, s]
```

The beat envelope guarantees the visual hits the 1, 2, 3, 4. The amplitude scales each hit so quiet sections pulse subtly and drops smash.

### Blender equivalent

Drive a beat-locked F-Curve (manually keyframed or driven off frame number) and multiply by the kick control empty:

```python
# Driver — scale property
beat_phase = (frame % (24 * 60 / 128)) / (24 * 60 / 128)  # at 24fps, 128 BPM
beat_env = pow(1 - beat_phase, 4)
1.0 + beat_env * min(kick, 1.0) * 0.3
```

---

## 8. Pre-Gig Audio Prep

A 30-min prep pass per track makes the difference between a tight set and a sloppy one.

### Get the BPM

Drag the track into Ableton Live, Logic, or Mixxx — they'll detect BPM automatically. Cross-check by tapping along to be sure. Write the BPM in the project file name: `track_128bpm.wav`.

For variable-tempo tracks (live drums, classical) you can't lock to one BPM — fall back to pure amplitude-driven.

### Isolate kick / snare / hat

Three options, in order of quality:

1. **iZotope RX 11 Music Rebalance** — drag track in, pull vocals/bass/percussion/other independently. Best quality, $300+.
2. **Logic Pro Stem Splitter** (built into 10.8+) — free if you have Logic, four-stem split, near-RX quality.
3. **Free: Spleeter or Demucs** — open-source CLI tools, run via Python. Solid quality for free.

You don't need surgical isolation — even 70% clean stems give you way better Blender bakes than baking against the full mix. The kick band at 40–90Hz on an isolated drum stem is nearly perfect.

### Render audio-reactive baselines at the track's BPM

Before the gig, render every audio-reactive comp / Blender scene against the actual track at the actual BPM. Don't trust that the 128 BPM template will look right on a 127.5 BPM track — render and check. Compounding drift over a 5-minute clip is audible.

### Prep "amplitude follow" templates

Have one Blender file and one AE comp set up as **template projects**: empty scene, four control empties already created with drivers wired up, just needs a new audio file dragged in and the bake script re-run. Same for AE — Audio Amplitude null in place, expressions wired, just swap the audio layer.

This is the entire workflow win. New track for a gig becomes: drop audio, run bake script, re-render. Twenty minutes instead of three hours.

---

## 9. Resolume Arena — Audio Reactivity at Performance Time

Resolume is the live layer where pre-rendered comps meet the actual gig. Three audio-reactive systems to know.

### BPM Sync

Set the master BPM (tap-tempo button, MIDI clock from a DJ deck, or Ableton Link). Any clip can be set to play in sync with the BPM grid — 1/4 note, 1/8, full bar, two bars. Triggering a clip waits for the next beat.

Critical for swap-friendly templates: render your audio-reactive Blender exports as one-bar or four-bar loops at the track's BPM, set Resolume's BPM to match, and clips will retrigger cleanly on the beat regardless of when you fire them.

### Audio Analysis input

`Preferences → Audio → Audio Input` — pick your interface. Then `Preferences → Audio Analysis` gives you Low / Mid / High envelopes + BPM detection from incoming audio.

These envelopes show up as automation sources. Right-click any clip parameter (opacity, speed, X position, FX intensity) → "Shortcut..." → pick "Audio Low" / "Audio Mid" / "Audio High". Now that parameter pulses with that frequency band from the live audio feed.

### Sidechain from USB audio input

The cleanest setup: USB-C audio interface fed off the DJ mixer's booth or master out. Resolume sees that as Audio Input, runs analysis on it, and your visuals react to whatever the DJ is actually playing — not what's coming out of the laptop speakers.

A cheap 2-channel USB interface (Focusrite Scarlett Solo, Behringer UMC22) is enough. Make sure to disable any input monitoring or you'll get feedback through the venue PA.

### Mapping audio params to clip params

Common mappings for stage work:

- Audio Low → clip opacity (kick brings the layer up)
- Audio High → strobe FX intensity (hat-driven shimmer)
- BPM → clip playback speed (clip plays at gig tempo regardless of render BPM)
- Audio Low (gated, threshold 0.4) → trigger next clip on column (auto-switch on big drops)

Resolume's audio analysis is good but not great. Pre-bake the heavy stuff in Blender/AE; use Resolume's reactivity for live-feel touches like opacity and FX intensity.

---

## 10. Latency and Sync

The three tools have very different sync characteristics. Knowing the failure modes saves the gig.

### Blender — perfect sync

Sound Bake reads the audio file directly and writes keyframes at exact frame positions. Sync is sample-accurate. No drift, no latency, period.

**Gotcha:** The audio file you bake against must be the same file the DJ plays at the gig. A different mastering pass, a different sample rate, even re-encoded MP3 vs WAV can shift the kick by a few ms. Lock your audio source early and don't re-export.

### After Effects — small drift on long comps

Convert Audio to Keyframes is generally tight but can drift up to one frame on comps over 5 minutes. Cause: AE's audio engine sample-rate-converts on the fly and the conversion isn't always frame-perfect.

**Workaround 1:** Split long comps into 60–90s pre-comps and re-bake audio per pre-comp. Drift resets at each boundary.

**Workaround 2:** Bake amplitude in Blender (Section 3), export keyframes as CSV, paste into AE Slider Control. Tedious but bit-exact.

**Workaround 3:** Render the AE comp with its embedded audio. Resolume then plays the pre-baked visual + audio together, sync is perfect on playback regardless of any AE drift during editing.

### Resolume — 50–200ms audio analysis latency

Real-time FFT and envelope detection introduce latency — the visual reacts a chunk of a beat after the audio. Fine for slow pads, terrible for kick-locked strobes.

**Workaround 1:** Don't use live audio analysis for tight beat-locked elements. Use it for slow envelopes (opacity, glow). Beat-locked stuff goes through BPM Sync, not audio analysis.

**Workaround 2:** Manually offset the audio analysis output. Resolume has a Smoothness setting on each analysis band — counterintuitively, lower Smoothness can reduce perceived latency at the cost of jitter.

**Workaround 3:** For the tightest reactivity, send MIDI from a DJ deck or Ableton Link. MIDI clock has microsecond latency vs audio analysis's 50–200ms. If the DJ can provide a clock feed, take it.

### Audio interface buffer

Don't forget the obvious one: your audio interface's buffer size adds latency too. Drop it to 128 or 64 samples in Resolume's audio preferences (lower = less latency but more CPU). 64 samples at 48kHz is 1.3ms — basically zero.

---

## Quick reference — the gig-day checklist

1. Get the BPM, write it in the file name.
2. Isolate drums (Logic Stem Splitter or Spleeter).
3. Drop audio into the Blender template, run the bake script (Section 3).
4. Render the four control empties driving the scene.
5. Drop render + audio into the AE template, hit Convert Audio to Keyframes (Section 4).
6. Export from AE as a one-bar or four-bar loop at the track's BPM.
7. Load into Resolume, set master BPM, enable BPM Sync on the clip.
8. Patch USB audio in from the booth feed (Section 9).
9. Map Audio Low to clip opacity, Audio High to a strobe FX (Section 9).
10. Soundcheck — verify nothing drifts, no feedback, latency feels right.

End to end on a familiar track: 30 minutes from new audio file to gig-ready clip.
