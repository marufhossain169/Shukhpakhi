"""Wing base forms plus real overlapping covert, secondary and primary feathers."""
import math
from . import config, utils, materials
from . import feather_engine

COLLECTION = config.COLLECTION_PREFIX + "Wings"


def _wing_feathers(sign):
    covert, secondary, primary = [], [], []
    normal = (sign * 0.58, -0.80, 0.08)
    # Three offset covert rows, roots at the upper/leading edge and tips swept down/back.
    for row, z in enumerate((1.48, 1.34, 1.20)):
        for col in range(4):
            x = sign * (0.52 + col * 0.066)
            root = (x, -0.287 - 0.012 * row, z - col * 0.018)
            covert.append({"root": root, "direction": (sign * 0.06, 0.10, -0.16),
                          "normal": normal, "length": 0.145, "width": 0.048,
                          "height": 0.006, "offset": 0.006})
    # Longer secondaries along the trailing lower edge.
    for i in range(5):
        x = sign * (0.59 + i * 0.045)
        root = (x, -0.258 + i * 0.012, 1.18 - i * 0.095)
        secondary.append({"root": root, "direction": (sign * 0.12, 0.15, -0.23),
                      "normal": normal, "length": 0.20, "width": 0.052,
                      "height": 0.007, "offset": 0.008})
    # Distinct tapered primary tips.
    for i in range(4):
        x = sign * (0.70 + i * 0.028)
        root = (x, -0.235 + i * 0.016, 0.88 - i * 0.075)
        primary.append({"root": root, "direction": (sign * 0.08, 0.18, -0.26),
                      "normal": normal, "length": 0.23, "width": 0.047,
                      "height": 0.007, "offset": 0.009})
    return {"covert": covert, "secondary": secondary, "primary": primary}


def build():
    utils.clear_collection(COLLECTION)
    mats = materials.create_all()
    made = []
    for side, sign in (("L", -1), ("R", 1)):
        wing = utils.create_ellipsoid(
            f"Wing_{side}_Soft_Base", (sign * config.WING_X, config.WING_Y, config.WING_Z),
            config.WING_RADII, COLLECTION, mats["sage"], segments=48, rings=36, subsurf=1
        )
        wing.rotation_euler = (0.0, 0.0, 0.0)  # feather roots are placed against this unrotated base
        made.append(wing)
        if config.ENABLE_WING_FEATHERS:
            groups = _wing_feathers(sign)
            for layer, material_key in (("covert", "light_green"),
                                        ("secondary", "sage"), ("primary", "sage")):
                feather_obj = feather_engine.create_feather_cluster(
                    f"Wing_{side}_{layer.title()}_Feathers", groups[layer],
                    mats[material_key], thickness=0.0032, bevel=0.0010
                )
                if feather_obj: made.append(feather_obj)
    return made
