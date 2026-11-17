"""Canonical dimensions, palette and build controls for Shukhpakhi (Blender 5.3)."""

COLLECTION_PREFIX = "Shukhpakhi_"
BIRD_FACES = "-Y"


def srgb_to_linear(c):
    c = max(0.0, min(1.0, c))
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_rgba(value, alpha=1.0):
    value = value.lstrip("#")
    rgb = [srgb_to_linear(int(value[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    return (*rgb, alpha)


# Exact guide swatches are preserved. Additional colours are supporting accents only.
PALETTE_HEX = {
    "sage": "#A7C49A",
    "light_green": "#D7E8C5",
    "cream": "#F8F9E9",
    "warm_beige": "#EDE7D9",
    "orange": "#F6A623",
    "orange_shadow": "#D98218",
    "eye_dark": "#21150F",
    "eye_rim": "#69452B",
    "blush": "#E99A87",
    "white": "#FFFDF7",
    "wood": "#765335",
    "wood_light": "#A77A4D",
}
PALETTE = {k: hex_to_rgba(v) for k, v in PALETTE_HEX.items()}

# Canonical character proportions, world units. Z=0 is the foot contact plane.
BODY_CENTER = (0.0, 0.025, 1.20)
BODY_RADII = (0.73, 0.64, 0.82)
HEAD_CENTER = (0.0, -0.075, 1.88)
HEAD_RADII = (0.625, 0.565, 0.565)

# Face: front is negative Y.
EYE_X = 0.247
EYE_Y = -0.535
EYE_Z = 1.925
EYE_RADII = (0.148, 0.098, 0.169)
BEAK_CENTER = (0.0, -0.645, 1.775)
BEAK_UPPER = (0.125, 0.105, 0.071)
BEAK_LOWER = (0.091, 0.084, 0.043)
CHEEK_X = 0.365
CHEEK_Y = -0.530
CHEEK_Z = 1.755
CHEEK_RADII = (0.082, 0.026, 0.050)

# Short, chick-like legs: deliberately much shorter than the old 1.05-unit hip anchor.
FOOT_Z = 0.055
HIP_Z = 0.465
LEG_X = 0.235
LEG_Y = -0.005
LEG_RADIUS = 0.034
TOE_LENGTH = 0.155
TOE_RADIUS = 0.027

# Wing base anchors; individual feathers are generated separately.
WING_X = 0.615
WING_Y = -0.015
WING_Z = 1.285
WING_RADII = (0.175, 0.345, 0.455)

TUFT_BASE = (0.0, -0.045, 2.405)

# Master-build controls: high-quality source model, not a mobile polygon budget.
BODY_VOXEL_SIZE = 0.022
BODY_SMOOTH_FACTOR = 0.55
BODY_SMOOTH_ITERATIONS = 3
BODY_FEATHER_SEED = 23
ENABLE_BODY_DOWN_FEATHERS = True
ENABLE_WING_FEATHERS = True
ENABLE_BACK_FEATHERS = True
ENABLE_TAIL_FEATHERS = True
