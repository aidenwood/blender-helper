"""
setup_compositor_glow.py
------------------------
Builds a stage-vibe compositor node tree on the current scene:

  Render Layers
    → Glare (Fog Glow)
    → Lens Distortion (subtle chromatic aberration)
    → Vignette (multiply with radial mask)
    → Composite + Viewer

Cheap to compute, looks great on a projector. Replaces any existing
node tree on the active scene.

How to run:
  Scripting workspace → New → paste → Run Script.
"""

import bpy

# === EDIT THESE ===
GLARE_THRESHOLD = 1.0       # higher = only bright parts glow
GLARE_SIZE = 7              # 5–9 is the sweet spot for projection
CHROMATIC_DISPERSION = 0.005  # 0.000–0.020. 0.005 = subtle, 0.02 = obvious
VIGNETTE_AMOUNT = 0.6       # 0 = no vignette, 1 = strong
# ==================


def setup(scene):
    scene.use_nodes = True
    tree = scene.node_tree
    for node in list(tree.nodes):
        tree.nodes.remove(node)

    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = (-600, 0)

    glare = tree.nodes.new('CompositorNodeGlare')
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.threshold = GLARE_THRESHOLD
    glare.size = GLARE_SIZE
    glare.location = (-350, 0)

    lens = tree.nodes.new('CompositorNodeLensdist')
    lens.use_projector = False
    lens.use_fit = True
    lens.inputs['Distort'].default_value = 0.0
    lens.inputs['Dispersion'].default_value = CHROMATIC_DISPERSION
    lens.location = (-100, 0)

    # Vignette: ellipse mask → blur → multiply
    ellipse = tree.nodes.new('CompositorNodeEllipseMask')
    ellipse.width = 0.95
    ellipse.height = 0.95
    ellipse.location = (-100, -300)

    blur = tree.nodes.new('CompositorNodeBlur')
    blur.filter_type = 'GAUSS'
    blur.size_x = 200
    blur.size_y = 200
    blur.location = (150, -300)

    # Mix: scale vignette by VIGNETTE_AMOUNT
    mix_vig = tree.nodes.new('CompositorNodeMixRGB')
    mix_vig.blend_type = 'MIX'
    mix_vig.inputs['Fac'].default_value = VIGNETTE_AMOUNT
    mix_vig.inputs[1].default_value = (1, 1, 1, 1)  # full bright when fac=0
    mix_vig.location = (400, -300)

    multiply = tree.nodes.new('CompositorNodeMixRGB')
    multiply.blend_type = 'MULTIPLY'
    multiply.inputs['Fac'].default_value = 1.0
    multiply.location = (200, 0)

    comp = tree.nodes.new('CompositorNodeComposite')
    comp.location = (500, 0)

    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = (500, -150)

    links = tree.links
    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], lens.inputs['Image'])
    links.new(lens.outputs['Image'], multiply.inputs[1])
    links.new(ellipse.outputs['Mask'], blur.inputs['Image'])
    links.new(blur.outputs['Image'], mix_vig.inputs[2])
    links.new(mix_vig.outputs['Image'], multiply.inputs[2])
    links.new(multiply.outputs['Image'], comp.inputs['Image'])
    links.new(multiply.outputs['Image'], viewer.inputs['Image'])


setup(bpy.context.scene)
print("[compositor_glow] stage-glow node tree built. Adjust EDIT THESE values and re-run if needed.")
