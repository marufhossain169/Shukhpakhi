"""Three soft feather-like crown plumes (not botanical leaf blades)."""
from . import config, utils, materials
from . import feather_engine

COLLECTION = config.COLLECTION_PREFIX + "Tuft"


def build():
    utils.clear_collection(COLLECTION)
    mats = materials.create_all()
    bx, by, bz = config.TUFT_BASE
    specs = [
        {"root": (bx, by, bz), "direction": (0.00, 0.055, 0.235), "normal": (0, -1, 0.2),
         "length": 0.235, "width": 0.060, "height": 0.009, "offset": 0.0},
        {"root": (bx - 0.035, by + 0.006, bz - 0.025), "direction": (-0.075, 0.035, 0.175),
         "normal": (-0.15, -1, 0.1), "length": 0.185, "width": 0.052, "height": 0.007, "offset": 0.0},
        {"root": (bx + 0.035, by + 0.006, bz - 0.025), "direction": (0.075, 0.035, 0.175),
         "normal": (0.15, -1, 0.1), "length": 0.185, "width": 0.052, "height": 0.007, "offset": 0.0},
    ]
    return [feather_engine.create_feather_cluster("Head_Tuft_Three_Soft_Feathers", specs,
                                                   mats["light_green"], thickness=0.003,
                                                   bevel=0.001)]
