"""
setup_audio_control_rig.py
--------------------------
Creates four control Empties (Kick / Snare / Mid / Hat) and bakes each one's
Z-scale to a frequency band of the given audio file using Blender's
"Bake Sound to F-Curve" operator.

After running, drive any scene property off a control's scale with a driver:

  Right-click any property → Add Driver → in the Driver editor:
    var = bpy.data.objects["Ctrl_Kick"].scale.z
    expression: var          (raw)
    expression: max(0, var - 0.05)   (threshold)
    expression: var * 5      (scaled up for emission strength)

Re-running this script with a new audio file is idempotent — the empties
are reused and their bakes overwritten.

How to run:
  1. Edit AUDIO_PATH (must be a real file on disk — wav/mp3/aiff).
  2. Edit BANDS to taste.
  3. Scripting workspace → New → paste → Run Script.

NOTE: 'bake_sound' is a Graph Editor operator. The script switches a temporary
area to Graph Editor to run it. Keep Blender focused while it runs.
"""

import bpy

# === EDIT THESE ===
AUDIO_PATH = "/Users/aidenwood/Desktop/track.wav"   # absolute path; must exist
BANDS = [
    # name,        lowest_hz, highest_hz, attack, release, threshold, accumulate, additive, square
    ("Ctrl_Kick",      40,       100,     0.005,   0.20,    0.0,       False,      False,    False),
    ("Ctrl_Snare",    200,       500,     0.005,   0.10,    0.0,       False,      False,    False),
    ("Ctrl_Mid",      500,      2000,     0.005,   0.10,    0.0,       False,      False,    False),
    ("Ctrl_Hat",     5000,     12000,     0.005,   0.05,    0.0,       False,      False,    False),
]
EMPTY_LOCATION_STEP = 2.0   # space the empties along X so they don't overlap
# ==================


import os

if not os.path.isfile(AUDIO_PATH):
    raise RuntimeError(f"AUDIO_PATH not found: {AUDIO_PATH}")


def ensure_empty(name, idx):
    obj = bpy.data.objects.get(name)
    if obj is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(idx * EMPTY_LOCATION_STEP, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
    return obj


def bake_band_to_z_scale(obj, audio_path, low, high, attack, release, threshold, accumulate, additive, square):
    """Run bake_sound on the Z-scale F-curve of obj."""
    # Keyframe scale.z so an F-curve exists, then we bake over it.
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", index=2, frame=bpy.context.scene.frame_start)
    obj.keyframe_insert(data_path="scale", index=2, frame=bpy.context.scene.frame_end)

    # Find a window we can flip to Graph Editor.
    area = next((a for a in bpy.context.screen.areas if a.type != 'PROPERTIES'), None)
    if area is None:
        raise RuntimeError("No usable area to switch to Graph Editor. Run from the default workspace.")
    original_type = area.type
    area.type = 'GRAPH_EDITOR'

    # Select only this object so bake_sound knows which F-curve to target.
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # The F-curve we want is scale[2]. Select only that channel.
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            fc.select = (fc.data_path == "scale" and fc.array_index == 2)

    with bpy.context.temp_override(area=area):
        bpy.ops.graph.sound_bake(
            filepath=audio_path,
            low=low,
            high=high,
            attack=attack,
            release=release,
            threshold=threshold,
            use_accumulate=accumulate,
            use_additive=additive,
            use_square=square,
        )

    area.type = original_type


for i, band in enumerate(BANDS):
    name, low, high, atk, rel, thr, acc, add, sq = band
    obj = ensure_empty(name, i)
    print(f"[audio_rig] baking '{name}' {low}–{high}Hz from {os.path.basename(AUDIO_PATH)}")
    bake_band_to_z_scale(obj, AUDIO_PATH, low, high, atk, rel, thr, acc, add, sq)

print(f"[audio_rig] done. {len(BANDS)} control empties baked.")
print("           Drive any property with `bpy.data.objects[\"Ctrl_Kick\"].scale.z` in a driver expression.")
