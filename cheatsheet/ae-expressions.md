# After Effects Expressions — VJ / Stage Visuals Library

Copy-paste expression library for the SVG → Blender → AE → Resolume pipeline. Every block is gig-tested on AE 2024+. Goal: cut manual keyframing so a comp goes from "monthly build" to "weekly turnaround".

**How to apply an expression:** Alt-click (Option-click on Mac) the stopwatch next to a property in the Timeline panel. Paste the code. Click outside the box to commit.

**Pickwhip basics:** the spiral icon next to the expression editor lets you drag-link to other properties — use it instead of typing `thisComp.layer("...").effect("...")` chains by hand.

---

## 1. Loop / Cycle Expressions

The `loopOut()` family extends keyframes beyond the last one without manually duplicating them. Apply to any animated property; you must have at least two keyframes for it to do anything.

### Loop — Cycle (seamless repeat)
Plays keyframes start-to-end, then jumps back to the first keyframe and repeats. Best for: rotating logos, spinning loaders, anything that returns to its start value.

```js
loopOut("cycle")
```

**Attach to:** any keyframed property (Position, Rotation, Scale, Opacity, slider values).
**Tweakables:** none — controlled by your keyframe timing.
**Gotcha:** if your first and last keyframe values don't match, you'll get a visible "snap" on the loop. Either match them, or use `pingpong`.

### Loop — Pingpong (back and forth)
Plays keyframes forward, then reverses, forever. Best for: breathing scale, sway, idle motion that should never snap.

```js
loopOut("pingpong")
```

**Attach to:** any keyframed property.
**Tweakables:** none.
**Gotcha:** doubles your effective cycle length — a 1s forward animation becomes a 2s pingpong.

### Loop — Offset (additive repeat)
Repeats keyframes but adds the total delta to the start each cycle. Best for: continuous travel (a layer scrolling forever in X), endless rotation that doesn't reset to 0.

```js
loopOut("offset")
```

**Attach to:** Position (for endless scroll), Rotation (for accelerating spin), any numeric property.
**Gotcha:** values can grow huge over a long timeline — fine in AE, but if you're sending Position to Resolume via a render, watch for off-screen drift.

### Loop In counterparts
All three have `loopIn()` versions that extend keyframes *before* the first one. Useful when you want a layer that fades in mid-comp to look like it's been going forever.

```js
loopIn("cycle")
```

---

## 2. Wiggle and Controlled Randomness

`wiggle(freq, amp)` is the workhorse. Smooth wiggle layers multiple octaves at low frequency; `seedRandom` lets you nail down a "good" random pass so it doesn't change every render.

### Basic Wiggle
Random shake every frame. Great for handheld camera fake, jittery text.

```js
freq = 3;
amp = 20;
wiggle(freq, amp)
```

**Attach to:** Position (2D or 3D), Rotation, Scale, any numeric/array property.
**Tweakables:** `freq` (wiggles per second), `amp` (max deviation from base value, in property units).
**Gotcha:** on Scale, `amp = 20` means ±20% — easy to blow past 100% and clip. On Position, `amp` is pixels.

### Smooth Wiggle (low freq, multiple octaves)
Slower, more organic motion — drifts instead of jitters. Use for floating logos, ambient camera moves on a still photo composite.

```js
freq = 0.5;
amp = 60;
octaves = 3;
amp_mult = 0.4;
wiggle(freq, amp, octaves, amp_mult)
```

**Attach to:** Position, Rotation, Camera position.
**Tweakables:** `octaves` (how many wiggle layers — higher = more detail), `amp_mult` (each octave's strength relative to the last; <1 = smoother).
**Gotcha:** `octaves > 5` rarely adds visible detail and just costs render time.

### Seeded Random Wiggle (repeatable)
Locks the random seed so the wiggle is identical every time. Critical when you're rendering multiple passes that need to match.

```js
freq = 2;
amp = 30;
seed = 4;
seedRandom(seed, true);
wiggle(freq, amp)
```

**Attach to:** anything wiggled.
**Tweakables:** `seed` (change the number to roll a new random pass and keep the one you like).
**Gotcha:** the `true` flag is "timeless" — without it, `seedRandom` only affects calls *after* it, and `wiggle` won't be seeded. Always include it.

### Posterized / Stepped Wiggle (glitch feel)
Wiggle that updates at a chosen FPS instead of every frame — gives a stuttery, robotic, glitch-loop feel that reads well on stage LED walls.

```js
fps = 8;
freq = 5;
amp = 40;
posterizeTime(fps);
wiggle(freq, amp)
```

**Attach to:** Position, Rotation, Source Text colour fill, any property.
**Tweakables:** `fps` (lower = chunkier glitch).
**Gotcha:** `posterizeTime(0)` disables it entirely — useful for A/B comparing on the fly.

### Wiggle One Axis Only
Stock wiggle moves all dimensions. To shake X only on Position, split the value array.

```js
freq = 4;
amp = 30;
w = wiggle(freq, amp);
[w[0], value[1]]
```

**Attach to:** Position.
**Tweakables:** swap `w[0], value[1]` for `value[0], w[1]` to wiggle Y only.

---

## 3. Audio-Reactive Expressions

Workflow: select your audio layer → **Animation > Keyframe Assistant > Convert Audio to Keyframes**. This creates an "Audio Amplitude" null with Slider Controls for Left/Right/Both channels. Then drive properties off that slider.

### Audio-Driven Scale (pulse with the music)
Scales a layer up when audio amplitude rises. Drop on logos, light beams, anything you want to thump.

```js
audioLayer = thisComp.layer("Audio Amplitude");
amp = audioLayer.effect("Both Channels")("Slider");
baseScale = 100;
sensitivity = 2;
s = baseScale + amp * sensitivity;
[s, s]
```

**Attach to:** Scale.
**Tweakables:** `baseScale` (rest size %), `sensitivity` (how hard it reacts — higher = bigger pumps).
**Gotcha:** if you renamed the audio null, update the `"Audio Amplitude"` string. Channel names are literally `"Left Channel"`, `"Right Channel"`, `"Both Channels"`.

### Audio-Mapped to Range (linear)
Maps raw amplitude (0–30ish, depends on source) into a clean output range. Far more controllable than raw multiplication.

```js
audioLayer = thisComp.layer("Audio Amplitude");
amp = audioLayer.effect("Both Channels")("Slider");
inMin = 0;
inMax = 25;
outMin = 80;
outMax = 140;
s = linear(amp, inMin, inMax, outMin, outMax);
[s, s]
```

**Attach to:** Scale, Opacity, Rotation, any single-value or array property.
**Tweakables:** `inMin/inMax` (clip the audio range — find these by scrubbing the slider keyframes), `outMin/outMax` (what you want to drive).
**Gotcha:** `linear()` clamps outside the input range — values above `inMax` won't push higher. Use `ease()` for smoother S-curves between the same points.

### Audio-Driven Opacity Flicker
Layer only shows when audio is loud. Great for flash frames on snares, strobing on bass hits.

```js
audioLayer = thisComp.layer("Audio Amplitude");
amp = audioLayer.effect("Both Channels")("Slider");
threshold = 15;
amp > threshold ? 100 : 0
```

**Attach to:** Opacity.
**Tweakables:** `threshold` (amplitude that triggers the flash).
**Gotcha:** ternary on Opacity will snap hard. For a softer feel use `linear(amp, threshold, threshold + 5, 0, 100)`.

### Audio-Driven Rotation Kick
Adds a small rotational hit on each transient.

```js
audioLayer = thisComp.layer("Audio Amplitude");
amp = audioLayer.effect("Both Channels")("Slider");
maxKick = 8;
value + linear(amp, 0, 30, 0, maxKick)
```

**Attach to:** Rotation (note: `value +` lets you keep manual keyframes on top of the audio response).
**Tweakables:** `maxKick` (degrees).

---

## 4. BPM-Locked Animation

For when you have a known tempo and want hands-off sync. Set `bpm` once and reuse the helper math everywhere. These don't need keyframes — they run off `time`.

### Beat Pulse (snap up, decay)
Property snaps to peak on each beat then eases back. The bedrock VJ pump.

```js
bpm = 128;
peak = 130;
rest = 100;
decay = 4;
beatDur = 60 / bpm;
phase = (time % beatDur) / beatDur;
s = rest + (peak - rest) * Math.exp(-phase * decay);
[s, s]
```

**Attach to:** Scale.
**Tweakables:** `bpm`, `peak` (size at impact), `rest` (size between beats), `decay` (higher = snappier falloff).
**Gotcha:** `time` is comp time. If you need to offset (e.g. first beat lands at 0.5s), subtract: `(time - 0.5) % beatDur`.

### 16th-Note Flicker
Toggles opacity on every 16th note. Perfect for hi-hat-rate flashes.

```js
bpm = 128;
subdiv = 4;
on = 100;
off = 0;
beatDur = 60 / bpm;
stepDur = beatDur / subdiv;
step = Math.floor(time / stepDur);
step % 2 == 0 ? on : off
```

**Attach to:** Opacity.
**Tweakables:** `bpm`, `subdiv` (4 = 16ths, 2 = 8ths, 1 = quarter notes), `on/off` values.
**Gotcha:** at high BPM and `subdiv = 4` you can alias on 30fps comp output — bump comp frame rate to 60 for clean reads on LED.

### Bar-Aligned Hard Cut (4-bar phrase)
Cycles a property through N states, one per bar. Use to swap source text, switch between colour controls, fire a different animation each bar of a phrase.

```js
bpm = 128;
beatsPerBar = 4;
states = 4;
barDur = (60 / bpm) * beatsPerBar;
currentBar = Math.floor(time / barDur) % states;
currentBar
```

**Attach to:** a Slider Control on a CTRL null — then use the slider value to switch behaviour elsewhere via `if/else` or `linear()`.
**Tweakables:** `states` (how many bars before the pattern repeats).

### Sine Wave Locked to BPM
Smooth in-out following the beat, no keyframes. Different feel from the pulse — more breathing, less hitting.

```js
bpm = 128;
amp = 30;
base = 100;
beatDur = 60 / bpm;
base + Math.sin((time / beatDur) * Math.PI * 2) * amp
```

**Attach to:** Scale (wrap in `[v, v]`), Rotation, Position offset.
**Tweakables:** `amp`, `base`, multiply `beatDur` by 0.5 for half-time or 2 for double-time feel.

---

## 5. Stagger / Sequencer Expressions

When you have an array of layers (e.g. 30 SVG-traced stage panels) and want them all to run the same animation offset in time. Apply the same expression to all layers — `index` makes each one unique.

### Delay by Layer Index
Each layer plays the layer-above's value, but `n` seconds later. Cascades animation down a stack.

```js
delayPerLayer = 0.1;
if (index > 1) {
  thisComp.layer(index - 1).transform.position.valueAtTime(time - delayPerLayer)
} else {
  value
}
```

**Attach to:** Position (or any property — change `transform.position` to match).
**Tweakables:** `delayPerLayer` (seconds between each layer's start).
**Gotcha:** the top layer (`index == 1`) falls back to `value` so it still animates from its own keyframes. Don't apply to all layers and then animate none — nothing will move.

### Index-Based Time Offset
All layers run the same expression but each one is shifted in time. Cleaner than chaining valueAtTime when you don't need a follow-the-leader effect.

```js
bpm = 128;
offsetPerLayer = 0.05;
beatDur = 60 / bpm;
t = time - (index - 1) * offsetPerLayer;
phase = (t % beatDur) / beatDur;
100 + (130 - 100) * Math.exp(-phase * 4)
```

**Attach to:** Scale (wrap), Opacity, anything.
**Tweakables:** `offsetPerLayer` (delay between each layer in the stack).

### Index-Based Position (auto grid)
Auto-arranges layers into a grid by index without manual positioning. Useful for sequencer-style "panels of stuff".

```js
cols = 6;
spacingX = 200;
spacingY = 200;
startX = 200;
startY = 200;
col = (index - 1) % cols;
row = Math.floor((index - 1) / cols);
[startX + col * spacingX, startY + row * spacingY]
```

**Attach to:** Position.
**Tweakables:** `cols`, `spacingX/Y`, `startX/Y`.
**Gotcha:** `index` starts at 1, not 0 — that's why we subtract 1.

---

## 6. Easing Utilities

`linear()` and `ease()` remap one value range to another. `ease()` is the same shape as the F9 easy ease keyframes. Use these instead of fiddly keyframe handles when you can.

### linear() — straight-line remap
Map an input range to an output range with no curve. Cleanest tool for connecting one property to another.

```js
ctrl = thisComp.layer("CTRL").effect("Slider Control")("Slider");
inMin = 0;
inMax = 100;
outMin = 50;
outMax = 200;
linear(ctrl, inMin, inMax, outMin, outMax)
```

**Attach to:** any numeric property.
**Gotcha:** `linear()` clamps — outside the input range, output is held at the nearest endpoint.

### ease() — S-curve remap
Same as linear but with ease-in-out built in. Use for transitions where a straight ramp feels mechanical.

```js
t = time;
startT = 2;
endT = 4;
startVal = 0;
endVal = 100;
ease(t, startT, endT, startVal, endVal)
```

**Attach to:** Opacity (e.g. fade between t=2s and t=4s), Position, anything.
**Tweakables:** the input range (`startT/endT`) and output (`startVal/endVal`).
**Gotcha:** `easeIn()` and `easeOut()` exist as one-sided variants. Use them when only one end needs the curve.

### Custom Bezier Ease
For when stock `ease()` isn't punchy enough. Power curves give you control over the snap.

```js
t = time;
startT = 0;
endT = 1;
startVal = 0;
endVal = 100;
power = 3;
p = ease(t, startT, endT, 0, 1);
startVal + (endVal - startVal) * Math.pow(p, power)
```

**Attach to:** any numeric property.
**Tweakables:** `power` (>1 = ease-in heavier, <1 = ease-out heavier).

### Snap-to-Grid Position
Forces Position onto a grid — handy when you wiggle inside a tile system and don't want soft drift.

```js
gridSize = 50;
x = Math.round(value[0] / gridSize) * gridSize;
y = Math.round(value[1] / gridSize) * gridSize;
[x, y]
```

**Attach to:** Position (after a wiggle, or below other position math).
**Tweakables:** `gridSize` (in pixels).
**Gotcha:** if `value` is already a clean integer, you'll see no change — apply this *after* a wiggle or animation.

---

## 7. Time-Based Effects

Manipulate the comp's `time` value to retime, freeze, stutter, or loop within a nested comp.

### posterizeTime — stepped motion
Freezes time at the chosen FPS so every subsequent expression evaluates in steps. Great for stop-motion, glitch, or low-frame-rate stylisation.

```js
fps = 12;
posterizeTime(fps);
value
```

**Attach to:** Position, Scale, or any animated property — applies to everything that reads `time` *after* this line.
**Tweakables:** `fps`.
**Gotcha:** affects only the expression on this property, not the layer's source footage. To posterise source, use the **Posterize Time** effect from the Effects panel.

### Freeze at Time
Locks a property's value to whatever it was at a specific time, forever. Like a permanent freeze frame for one property.

```js
freezeTime = 1.5;
value.valueAtTime(freezeTime)
```

**Attach to:** any keyframed property.
**Tweakables:** `freezeTime` (seconds).
**Gotcha:** the property must have keyframes — otherwise `valueAtTime` returns the static value and the expression does nothing.

### Time Remap Loop (in nested comps)
Loops a pre-comp's playback without using `loopOut` on Time Remap keyframes. Useful when you want clean infinite loops of a nested animation.

```js
loopDur = 2;
time % loopDur
```

**Attach to:** Time Remap (enable via `Layer > Time > Enable Time Remapping`).
**Tweakables:** `loopDur` (length of the loop in seconds — should match your nested comp duration).
**Gotcha:** the nested comp's duration must be at least `loopDur` long, or you'll loop past its end and see blank frames.

### Time Reversal at a Threshold
Plays time-remapped layer forward, then reverses past a point. Pingpong without keyframes.

```js
loopDur = 4;
half = loopDur / 2;
t = time % loopDur;
t < half ? t : loopDur - t
```

**Attach to:** Time Remap.

### Speed Ramp via Slider
Lets a CTRL slider control playback speed of a nested comp.

```js
ctrl = thisComp.layer("CTRL").effect("Speed")("Slider");
speed = ctrl / 100;
timeToFrames(time * speed) / 1.0 / thisComp.frameRate
```

**Attach to:** Time Remap.
**Tweakables:** `ctrl` value at 100 = real speed, 200 = 2x, 50 = half.

---

## 8. Pseudo-3D / Parallax

Drive 2D layer offsets from a fake Z value so a flat composite reads as depth. Pairs perfectly with SVG-traced stage panels at different "depths".

### Z-Driven Parallax (X / Y offset from camera move)
A "depth" slider on each layer; a CTRL slider drives a virtual camera pan. Layers closer to camera move more.

```js
camX = thisComp.layer("CTRL").effect("CamX")("Slider");
camY = thisComp.layer("CTRL").effect("CamY")("Slider");
depth = effect("Depth")("Slider");
basePos = [thisComp.width / 2, thisComp.height / 2];
parallaxScale = 1 / Math.max(depth, 0.01);
[basePos[0] + camX * parallaxScale, basePos[1] + camY * parallaxScale]
```

**Attach to:** Position. Each layer needs its own `Depth` slider effect (Effect > Expression Controls > Slider Control, rename to "Depth").
**Tweakables:** layer-level `Depth` (low = close to camera, high = far away), CTRL `CamX/CamY` for pan.
**Gotcha:** `Math.max(depth, 0.01)` prevents division by zero — if Depth is 0, you get NaN and the layer disappears.

### Distance-Based Scale
Layers scale according to their Depth slider so far things are visibly smaller.

```js
depth = effect("Depth")("Slider");
nearScale = 100;
farScale = 30;
maxDepth = 10;
s = linear(depth, 0, maxDepth, nearScale, farScale);
[s, s]
```

**Attach to:** Scale.

### Perspective Fake (rotate on Y from CTRL)
Approximates 3D rotation in 2D by squashing X scale as a fake-Y-rotation slider moves.

```js
yRot = thisComp.layer("CTRL").effect("YRot")("Slider");
sx = Math.cos(degreesToRadians(yRot)) * 100;
sy = 100;
[sx, sy]
```

**Attach to:** Scale.
**Tweakables:** YRot slider in degrees.
**Gotcha:** this only fakes rotation — there's no actual depth so edges won't foreshorten. For real 3D, switch the layer to 3D and use the camera.

---

## 9. Source Text Expressions

Apply these by Alt-clicking the **Source Text** property of a Text layer. They return a string. Great for lyric-driven stage visuals, live clocks, frame counters on debug overlays.

### Running Clock (HH:MM:SS)
Shows the current comp time as a live clock — perfect for "tour show clock" displays.

```js
t = time;
h = Math.floor(t / 3600);
m = Math.floor((t % 3600) / 60);
s = Math.floor(t % 60);
function pad(n) { return (n < 10 ? "0" : "") + n; }
pad(h) + ":" + pad(m) + ":" + pad(s)
```

**Attach to:** Source Text.
**Gotcha:** this is comp time, not wall-clock time. For real-time-of-day you need a separate utility (AE has no live system clock natively).

### Frame Counter
Outputs the current frame number — useful as a debug HUD or as a stylised counter on a loading screen.

```js
fps = 1.0 / thisComp.frameDuration;
"F " + Math.floor(time * fps)
```

**Attach to:** Source Text.

### Text from Comp Markers
Reads the comment of the nearest preceding comp marker. Drop comp markers (numpad * on macOS) on a music bar's downbeats, type the lyric in the marker comment, and your text layer plays the lyrics automatically.

```js
markers = thisComp.marker;
out = "";
if (markers.numKeys > 0) {
  for (i = 1; i <= markers.numKeys; i++) {
    if (markers.key(i).time <= time) {
      out = markers.key(i).comment;
    }
  }
}
out
```

**Attach to:** Source Text.
**Gotcha:** uses **comp** markers (top of timeline panel), not **layer** markers. Layer markers would be `thisLayer.marker`.

### Beat-Switched Text (locked to BPM)
Cycles through an array of strings, one per beat. Quick way to make text "perform" without keyframes.

```js
bpm = 128;
lines = ["UP", "DOWN", "LEFT", "RIGHT"];
beatDur = 60 / bpm;
i = Math.floor(time / beatDur) % lines.length;
lines[i]
```

**Attach to:** Source Text.
**Tweakables:** `bpm`, `lines` array.

### Audio-Triggered Text Swap
Swap text on each amplitude transient. Reads "live" on bass hits.

```js
audioLayer = thisComp.layer("Audio Amplitude");
amp = audioLayer.effect("Both Channels")("Slider");
threshold = 18;
amp > threshold ? "HIT" : "..."
```

**Attach to:** Source Text.
**Gotcha:** strobes hard if the audio sits near the threshold — add a small ease window with two thresholds if it flickers too much.

---

## 10. One-Liner Utilities

Short expressions that earn their keep. Keep these in muscle memory.

### CTRL Slider Multiplier
The fastest way to make any property remote-controllable.

```js
value * thisComp.layer("CTRL").effect("Master")("Slider") / 100
```

**Attach to:** Scale, Opacity, anything multiplicative. Slider at 100 = original, 200 = doubled.

### Opacity Linked to Scale
Layer fades as it shrinks. Cheap "distance" feel.

```js
transform.scale[0]
```

**Attach to:** Opacity.
**Gotcha:** Opacity range is 0–100, Scale typically also 0–100, so they match directly. If Scale goes above 100, Opacity clamps at 100 anyway.

### Conditional Show/Hide via Slider
Slider acts as a master visibility switch.

```js
thisComp.layer("CTRL").effect("Show")("Slider") > 0 ? 100 : 0
```

**Attach to:** Opacity.

### Inverse of Another Property
Mirror a value — when one is high the other is low.

```js
100 - thisComp.layer("CTRL").effect("A")("Slider")
```

**Attach to:** Opacity, any property that needs to crossfade with another.

### Random Pick from Array
Picks a random element once. Good for randomising layer behaviour across an array of duplicated layers.

```js
seedRandom(index, true);
options = [0, 90, 180, 270];
options[Math.floor(random(options.length))]
```

**Attach to:** Rotation (e.g. random orientation per layer).

### Clamp a Value
Forces a value to stay within bounds — useful when wiggle or audio can push past sensible limits.

```js
minV = 50;
maxV = 150;
Math.min(Math.max(value, minV), maxV)
```

**Attach to:** any numeric property.

### Distance Between Two Layers
Returns pixel distance from this layer to another. Great for trigger logic (fade in when close to another layer).

```js
other = thisComp.layer("Target").transform.position;
length(transform.position, other)
```

**Attach to:** any property where you want proximity to drive a value — usually fed into `linear()` for a soft trigger.

---

## Setup Pattern — The "CTRL Null" Rig

The single most important habit in this library. Every gig-ready comp has a master null called **CTRL** at the top of the layer stack with a handful of slider/angle/color controls. Every other layer reads from it via expressions. This is the difference between a "I built this comp once" file and one you can re-skin in 5 minutes for a new show.

### How to build it

1. **Create the null.** `Layer > New > Null Object`. Rename it `CTRL`. Move it to the top of the stack and lock its transforms so you don't accidentally move it.
2. **Add controls.** With CTRL selected, go to `Effect > Expression Controls` and add:
   - **Slider Control** — for any numeric value (rename: `Master`, `BPM`, `CamX`, `CamY`, `Intensity`, `Speed`).
   - **Angle Control** — for rotation values (rename: `GlobalRotation`).
   - **Color Control** — for tinting layers from a single source (rename: `Accent`, `BG`).
   - **Checkbox Control** — for boolean switches (rename: `ShowGrid`, `BeatSync`).
3. **Wire everything to it.** Use the pickwhip from each property's expression editor to point at the CTRL effect. AE writes the path for you, then you wrap it in math.
4. **Animate the CTRL, not the layers.** Now your timeline has a few CTRL keyframes instead of dozens per layer.

### Example: BPM-driven comp with master intensity

CTRL has two slider effects: `BPM` (set to 128) and `Intensity` (0–100, animated).

On any layer's Scale:

```js
ctrl = thisComp.layer("CTRL");
bpm = ctrl.effect("BPM")("Slider");
intensity = ctrl.effect("Intensity")("Slider") / 100;
peak = 100 + 30 * intensity;
rest = 100;
decay = 4;
beatDur = 60 / bpm;
phase = (time % beatDur) / beatDur;
s = rest + (peak - rest) * Math.exp(-phase * decay);
[s, s]
```

Crank Intensity to 100 for the drop, drag it to 0 for a breakdown. One slider, the whole comp responds.

### Why this matters for the SVG → Blender → AE → Resolume pipeline

- **Re-skinnable comps.** Same CTRL rig + different SVG-traced panels = new gig content in an hour.
- **Resolume-friendly stems.** Render layer groups in passes, each pass already synced to the master CTRL — Resolume just crossfades between renders without you keyframing again.
- **Show-day tweaks.** A venue wants the visuals 20% punchier? Bump `Intensity` keyframes. Done. No layer-by-layer surgery.

### Naming conventions worth committing to
- CTRL null: always `CTRL` (uppercase) so it's findable in expressions.
- Effect names: PascalCase, no spaces (`CamX`, not `Cam X`). Spaces in effect names are legal but make expression strings ugly.
- Duplicate CTRL nulls per section (`CTRL_LIGHTS`, `CTRL_TEXT`) when one comp has very different content groups.

### Compatibility notes
- Tested on **AE 2024+** (24.0 onward). All syntax above works on the legacy expression engine and the new JavaScript engine.
- If you're stuck on **AE CC 2018 or earlier**, the legacy ExtendScript engine doesn't support `let`/`const` consistently — stick with `var` or omit declarations entirely (every variable above will still work without keywords).
- `posterizeTime()` has existed since AE 6 — safe everywhere.
- `valueAtTime()` is universal.
