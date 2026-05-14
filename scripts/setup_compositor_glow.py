"""
setup_compositor_glow.py
------------------------
Builds a stage-vibe compositor node tree on the current scene:

  Render Layers
    → Glare (Fog Glow)
    → Lens Distortion (subtle chromatic aberration)
    → Group Output → Composite
    → Viewer (preview)

Cheap to compute, looks great on a projector. Replaces any existing
node tree on the active scene.

Targets Blender 5.x's new compositor architecture (compositing_node_group
on the scene, NodeGroupOutput instead of CompositorNodeComposite, Glare
properties exposed as node inputs).

How to run:
  Scripting workspace → New → paste → Run Script.
"""

import bpy

# === EDIT THESE ===
GLARE_THRESHOLD = 1.0       # higher = only bright parts glow
GLARE_SIZE = 7              # 5–9 is the sweet spot for projection
GLARE_QUALITY = "High"      # "High" | "Medium" | "Low"
CHROMATIC_DISPERSION = 0.005  # 0.000–0.020. 0.005 = subtle, 0.02 = obvious
# ==================


def ensure_output_socket(ng, name="Image"):
    """Make sure the node group has an Image output socket so Group Output works."""
    for item in ng.interface.items_tree:
        if item.item_type == 'SOCKET' and item.in_out == 'OUTPUT' and item.name == name:
            return item
    return ng.interface.new_socket(name=name, in_out='OUTPUT', socket_type='NodeSocketColor')


def setup(scene):
    # Get or create the scene's compositor node group (5.x architecture).
    tree = scene.compositing_node_group
    if tree is None:
        tree = bpy.data.node_groups.new("Compositor", 'CompositorNodeTree')
        scene.compositing_node_group = tree

    for node in list(tree.nodes):
        tree.nodes.remove(node)

    ensure_output_socket(tree, "Image")

    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = (-600, 0)

    glare = tree.nodes.new('CompositorNodeGlare')
    glare.location = (-300, 0)
    glare.inputs['Type'].default_value = 'Fog Glow'
    glare.inputs['Quality'].default_value = GLARE_QUALITY
    glare.inputs['Threshold'].default_value = GLARE_THRESHOLD
    glare.inputs['Size'].default_value = GLARE_SIZE

    lens = tree.nodes.new('CompositorNodeLensdist')
    lens.location = (0, 0)
    lens.inputs['Distortion'].default_value = 0.0
    lens.inputs['Dispersion'].default_value = CHROMATIC_DISPERSION
    if 'Fit' in lens.inputs:
        lens.inputs['Fit'].default_value = True

    output = tree.nodes.new('NodeGroupOutput')
    output.location = (300, 0)

    viewer = tree.nodes.new('CompositorNodeViewer')
    viewer.location = (300, -200)

    links = tree.links
    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], lens.inputs['Image'])
    links.new(lens.outputs['Image'], output.inputs['Image'])
    links.new(lens.outputs['Image'], viewer.inputs['Image'])


setup(bpy.context.scene)
print("[compositor_glow] stage-glow node tree built. Adjust EDIT THESE values and re-run if needed.")
