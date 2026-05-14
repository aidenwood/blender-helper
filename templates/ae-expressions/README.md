# AE Expressions — copy-paste templates

One file per expression. Each file:
1. Tweakable variables at the top.
2. The expression itself.
3. An `# attach to:` comment showing which property to paste it onto.
4. A `# gotcha:` comment if there's a common mistake.

Workflow: open the file, edit the variables, copy the whole body, paste into AE's expression editor (Option+click the stopwatch on a property to open it).

For the full library with explanations, see `cheatsheet/ae-expressions.md`.

## Files in this folder
- `loop-out-cycle.txt` — auto-loop two keyframes forever
- `beat-pulse-scale.txt` — snap-up-and-decay scale, BPM-locked
- `audio-mapped-range.txt` — audio amplitude (Slider) → property with min/max
- `stagger-by-index.txt` — same animation delayed per layer
- `smooth-wiggle.txt` — multi-octave wiggle, lower frequency, controlled
- `ctrl-null-slider-link.txt` — read any property off a master CTRL null
- `bpm-strobe.txt` — hard on/off at a BPM subdivision
- `posterize-time-step.txt` — chunky stepped motion (12fps look at 50fps)
- `random-color-on-beat.txt` — colour cycles on every beat, repeatable seed

## The CTRL null rig

Before pasting any of these: create a null layer named `CTRL` in your comp. Add Slider Controls (Effect → Expression Controls → Slider Control) for BPM, AudioAmp, Intensity. Drive everything off these so swapping a track or tweaking intensity at gig time is one slider, not 40.
