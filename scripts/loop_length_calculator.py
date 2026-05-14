"""
loop_length_calculator.py
-------------------------
Sets the scene's End Frame so the render loops perfectly at a given BPM.

Math: frames = bars × beats_per_bar × fps × 60 / bpm

Uses the "render to N, not N+1" trick so the last frame's value is the same
as frame 1's — clip loops seamlessly in Resolume's BPM Sync mode.

How to run:
  1. Edit BPM, BARS, BEATS_PER_BAR below.
  2. Scripting workspace → New → paste → Run Script.

The script prints the resulting frame count and seconds so you can sanity-check.
"""

import bpy

# === EDIT THESE ===
BPM = 128
BARS = 8
BEATS_PER_BAR = 4   # 4 for almost all dance music; 3 for waltz/3-time
SET_START_FRAME_TO_1 = True
# ==================

scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base

total_beats = BARS * BEATS_PER_BAR
seconds = total_beats * 60 / BPM
frames = round(seconds * fps)

# "Render to N, not N+1" — last frame = first frame on loop.
end_frame = frames

if SET_START_FRAME_TO_1:
    scene.frame_start = 1
    scene.frame_end = scene.frame_start + end_frame - 1
else:
    scene.frame_end = scene.frame_start + end_frame - 1

print(
    f"[loop_length] {BARS} bars × {BEATS_PER_BAR} beats @ {BPM} BPM, {fps:g} fps"
    f"  →  {frames} frames ({seconds:.3f}s)"
)
print(f"               scene.frame_start = {scene.frame_start}")
print(f"               scene.frame_end   = {scene.frame_end}")

# Quick sanity warning if BPM/fps don't divide evenly
if abs(seconds * fps - frames) > 0.01:
    print(
        "[loop_length] WARNING: this BPM/bars/fps combo doesn't land on a whole frame. "
        "Loop will drift slightly. Try BARS as a multiple of 2 or change fps to 60/30."
    )
