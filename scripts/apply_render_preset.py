"""
apply_render_preset.py
----------------------
Applies a named render preset to the current scene. Three presets for VJ work:

  cycles_fast       — 64 samples + OIDN, low bounces, large tiles, persistent data.
                      Use for: most stage clips. 3–5× faster than defaults.
  cycles_balanced   — 128 samples + OIDN, slightly more bounces.
                      Use for: hero shots, close-ups, reflective surfaces.
  eevee_fast        — 32 samples, bloom, basic SSR.
                      Use for: 80–90% of VJ output. Fastest path.

How to run:
  1. Open the .blend you want to render.
  2. Scripting workspace → New → paste this file.
  3. Edit PRESET at the top.
  4. Run Script (Option+P).

The script also sets output format defaults appropriate for VJ work
(PNG RGBA 16-bit image sequence, ready to transcode to HAP/DXV3 later).
"""

import bpy

# === EDIT THESE ===
PRESET = "eevee_fast"   # "cycles_fast" | "cycles_balanced" | "eevee_fast"
RESOLUTION = (1920, 1080)
FPS = 50                # 50 for European/AU gigs, 60 for US
SET_OUTPUT_FORMAT = True  # False = leave format alone
# ==================


def apply_cycles_fast(scene):
    scene.render.engine = 'CYCLES'
    cy = scene.cycles
    cy.device = 'GPU'
    cy.samples = 64
    cy.use_denoising = True
    cy.denoiser = 'OPENIMAGEDENOISE'
    cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    cy.denoising_prefilter = 'ACCURATE'
    cy.max_bounces = 4
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 2
    cy.transmission_bounces = 4
    cy.volume_bounces = 0
    cy.transparent_max_bounces = 4
    cy.sample_clamp_direct = 10.0
    cy.sample_clamp_indirect = 4.0
    cy.use_persistent_data = True
    cy.tile_size = 2048


def apply_cycles_balanced(scene):
    apply_cycles_fast(scene)
    scene.cycles.samples = 128
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 3


def apply_eevee_fast(scene):
    # Blender 4.2+ uses 'BLENDER_EEVEE_NEXT'; 4.1 and earlier use 'BLENDER_EEVEE'.
    engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    ee = scene.eevee
    ee.taa_render_samples = 32
    ee.taa_samples = 8
    if hasattr(ee, 'use_bloom'):
        ee.use_bloom = True
    if hasattr(ee, 'use_ssr'):
        ee.use_ssr = True
        ee.use_ssr_halfres = True
    if hasattr(ee, 'use_gtao'):
        ee.use_gtao = True
    if hasattr(ee, 'use_motion_blur'):
        ee.use_motion_blur = False  # toggle on per-scene if you want it


def set_output(scene):
    scene.render.resolution_x = RESOLUTION[0]
    scene.render.resolution_y = RESOLUTION[1]
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    if SET_OUTPUT_FORMAT:
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 15
        scene.render.film_transparent = True


PRESETS = {
    "cycles_fast": apply_cycles_fast,
    "cycles_balanced": apply_cycles_balanced,
    "eevee_fast": apply_eevee_fast,
}

scene = bpy.context.scene
if PRESET not in PRESETS:
    raise RuntimeError(f"Unknown preset '{PRESET}'. Options: {list(PRESETS)}")

PRESETS[PRESET](scene)
set_output(scene)

print(f"[render_preset] applied '{PRESET}' at {RESOLUTION[0]}x{RESOLUTION[1]}@{FPS}fps")
