"""Guide-calibrated soft feather, skin, beak and eye materials for Blender 5.3."""
import bpy
from . import config


def _input(node, candidates, value):
    for name in candidates:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return True
    return False


def get_material(name):
    key = "Shukhpakhi_MAT_" + name
    mat = bpy.data.materials.get(key) or bpy.data.materials.new(key)
    mat.diffuse_color = config.PALETTE.get(name, (0.8, 0.8, 0.8, 1.0))
    mat.use_nodes = True
    return mat


def _principled(mat, color, roughness, specular=0.22, sheen=0.0, sss=0.0, coat=0.0):
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 40)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (340, 40)
    _input(bsdf, ["Base Color"], color)
    _input(bsdf, ["Roughness"], roughness)
    _input(bsdf, ["Metallic"], 0.0)
    _input(bsdf, ["Specular IOR Level", "Specular"], specular)
    _input(bsdf, ["Sheen Weight", "Sheen"], sheen)
    _input(bsdf, ["Sheen Roughness"], 0.72)
    _input(bsdf, ["Subsurface Weight", "Subsurface"], sss)
    _input(bsdf, ["Subsurface Scale"], 0.035)
    _input(bsdf, ["Coat Weight", "Clearcoat"], coat)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return bsdf


def _make_feather_material(mat, base_color, accent_color=None, body_back_gradient=False):
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (780, 40)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (520, 40)
    _input(bsdf, ["Roughness"], 0.82)
    _input(bsdf, ["Metallic"], 0.0)
    _input(bsdf, ["Specular IOR Level", "Specular"], 0.18)
    _input(bsdf, ["Sheen Weight", "Sheen"], 0.28)
    _input(bsdf, ["Sheen Roughness"], 0.78)
    _input(bsdf, ["Subsurface Weight", "Subsurface"], 0.055)
    _input(bsdf, ["Subsurface Scale"], 0.025)

    tex = nodes.new("ShaderNodeTexCoord")
    tex.location = (-800, 100)
    if body_back_gradient:
        sep = nodes.new("ShaderNodeSeparateXYZ")
        sep.location = (-610, 250)
        links.new(tex.outputs["Generated"], sep.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.location = (-390, 250)
        cr = ramp.color_ramp
        cr.elements[0].position = 0.0
        cr.elements[0].color = config.PALETTE["cream"]
        cr.elements[1].position = 1.0
        cr.elements[1].color = config.PALETTE["sage"]
        mid1 = cr.elements.new(0.42)
        mid1.color = config.PALETTE["cream"]
        mid2 = cr.elements.new(0.60)
        mid2.color = config.PALETTE["light_green"]
        links.new(sep.outputs["Y"], ramp.inputs["Fac"])
        # Gentle warm-beige belly shading at the lowest body region, fading to guide cream.
        z_ramp = nodes.new("ShaderNodeValToRGB")
        z_ramp.location = (-390, -30)
        z_ramp.color_ramp.elements[0].position = 0.02
        z_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        z_ramp.color_ramp.elements[1].position = 0.32
        z_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
        links.new(sep.outputs["Z"], z_ramp.inputs["Fac"])
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MIX"
        mix.location = (80, 160)
        mix.inputs["Color1"].default_value = config.PALETTE["warm_beige"]
        links.new(z_ramp.outputs["Color"], mix.inputs["Fac"])
        links.new(ramp.outputs["Color"], mix.inputs["Color2"])
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        _input(bsdf, ["Base Color"], base_color)
        if accent_color:
            sep = nodes.new("ShaderNodeSeparateXYZ")
            sep.location = (-570, 220)
            links.new(tex.outputs["Generated"], sep.inputs["Vector"])
            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.location = (-350, 220)
            ramp.color_ramp.elements[0].position = 0.15
            ramp.color_ramp.elements[0].color = accent_color
            ramp.color_ramp.elements[1].position = 0.88
            ramp.color_ramp.elements[1].color = base_color
            links.new(sep.outputs["Z"], ramp.inputs["Fac"])
            links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # Fine micro-variation only. This is intentionally subtle; it does NOT replace geometry feathers.
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-560, -130)
    noise.inputs["Scale"].default_value = 175.0
    noise.inputs["Detail"].default_value = 2.2
    noise.inputs["Roughness"].default_value = 0.62
    links.new(tex.outputs["Object"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.location = (260, -130)
    bump.inputs["Strength"].default_value = 0.018
    bump.inputs["Distance"].default_value = 0.004
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])


def create_all():
    mats = {}
    for name, accent in (("cream", "warm_beige"), ("sage", "light_green"),
                         ("light_green", "cream"), ("warm_beige", "cream")):
        mat = get_material(name)
        _make_feather_material(mat, config.PALETTE[name], config.PALETTE[accent],
                               body_back_gradient=(name == "cream"))
        mats[name] = mat

    # Dedicated body shader: cream on the front, a soft transition, sage across the back.
    mats["body"] = get_material("body")
    mats["body"].diffuse_color = config.PALETTE["cream"]
    _make_feather_material(mats["body"], config.PALETTE["cream"],
                           config.PALETTE["warm_beige"], body_back_gradient=True)
    mats["orange"] = get_material("orange")
    _principled(mats["orange"], config.PALETTE["orange"], 0.36, 0.30, 0.06, 0.015, 0.05)
    mats["eye_dark"] = get_material("eye_dark")
    _principled(mats["eye_dark"], config.PALETTE["eye_dark"], 0.075, 0.72, 0.0, 0.0, 0.32)
    mats["eye_rim"] = get_material("eye_rim")
    _principled(mats["eye_rim"], config.PALETTE["eye_rim"], 0.28, 0.30)
    mats["white"] = get_material("white")
    _principled(mats["white"], config.PALETTE["white"], 0.06, 0.65, 0.0, 0.0, 0.12)
    mats["blush"] = get_material("blush")
    _principled(mats["blush"], config.PALETTE["blush"], 0.88, 0.08, 0.0, 0.02)
    mats["eyelid"] = get_material("eyelid")
    _make_feather_material(mats["eyelid"], config.PALETTE["cream"], config.PALETTE["warm_beige"])
    mats["wood"] = get_material("wood")
    _principled(mats["wood"], config.PALETTE["wood"], 0.88, 0.16)
    return mats
