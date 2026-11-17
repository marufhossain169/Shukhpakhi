"""Unified torso/head volume plus separately modeled down-feather overlays."""
import bpy
import bmesh
import math
from . import config, utils, materials
from . import feather_engine

COLLECTION = config.COLLECTION_PREFIX + "Body"


def _make_unified_body(mat):
    bm = bmesh.new()
    utils.add_uv_sphere_bmesh(bm, config.BODY_CENTER, config.BODY_RADII, 64, 44)
    utils.add_uv_sphere_bmesh(bm, config.HEAD_CENTER, config.HEAD_RADII, 64, 44)
    bm.normal_update()
    mesh = bpy.data.meshes.new("Body_Unified_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Body_Unified_Sculpt_Base", mesh)
    utils.link_object(obj, COLLECTION)
    mesh.materials.append(mat)
    utils.smooth_mesh(obj)

    # Voxel remesh fuses overlapping volumes; this is the actual union step missing in the old source.
    remesh = obj.modifiers.new("UNION_Torso_Head_VoxelRemesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = config.BODY_VOXEL_SIZE
    if hasattr(remesh, "use_smooth_shade"):
        remesh.use_smooth_shade = True
    smooth = obj.modifiers.new("Sculpt_Soften", "SMOOTH")
    smooth.factor = config.BODY_SMOOTH_FACTOR
    smooth.iterations = config.BODY_SMOOTH_ITERATIONS
    sub = obj.modifiers.new("Silhouette_Polish", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return obj


def _body_down_specs():
    specs = []
    cx, cy, cz = config.BODY_CENTER
    rx, ry, rz = config.BODY_RADII
    # Sparse, staggered front chest feathers: visible texture without a spiky outline.
    for row, v in enumerate((-0.70, -0.51, -0.32, -0.13, 0.06, 0.25)):
        for col in range(11):
            u = -0.72 + col * 0.144 + (0.055 if row % 2 else 0.0)
            r2 = u * u + v * v
            if r2 > 0.78:
                continue
            q = (u, -math.sqrt(max(0.02, 1.0 - r2)), v)
            point, normal = feather_engine.ellipsoid_surface((cx, cy, cz), (rx, ry, rz), q)
            direction = feather_engine.tangent_direction((0.0, 0.0, -1.0), normal)
            specs.append({"root": point + normal * 0.004, "direction": direction,
                          "normal": normal, "length": 0.078, "width": 0.025,
                          "height": 0.0022, "offset": 0.0})
    return specs


def _back_feather_specs():
    specs = []
    cx, cy, cz = config.BODY_CENTER
    rx, ry, rz = config.BODY_RADII
    for row, v in enumerate((-0.62, -0.46, -0.30, -0.14, 0.02, 0.18, 0.34, 0.50)):
        for col in range(13):
            u = -0.70 + col * 0.115 + (0.035 if row % 2 else 0.0)
            r2 = u * u + v * v
            if r2 > 0.78:
                continue
            q = (u, math.sqrt(max(0.02, 1.0 - r2)), v)
            point, normal = feather_engine.ellipsoid_surface((cx, cy, cz), (rx, ry, rz), q)
            direction = feather_engine.tangent_direction((0.0, 0.0, -1.0), normal)
            specs.append({"root": point + normal * 0.005, "direction": direction,
                          "normal": normal, "length": 0.155, "width": 0.052,
                          "height": 0.005, "offset": 0.0})
    return specs


def _tail_specs():
    specs = []
    root = (0.0, 0.54, 0.78)
    for i, x in enumerate((-0.16, -0.08, 0.0, 0.08, 0.16)):
        specs.append({"root": (x, root[1], root[2] + (0.02 if i in (1, 3) else 0.0)),
                      "direction": (x * 0.22, 1.0, -0.20), "normal": (0.0, 0.0, 1.0),
                      "length": 0.31 if i == 2 else 0.28, "width": 0.075,
                      "height": 0.009, "offset": 0.0})
    return specs


def build():
    utils.clear_collection(COLLECTION)
    mats = materials.create_all()
    made = [_make_unified_body(mats["body"])]
    if config.ENABLE_BODY_DOWN_FEATHERS:
        obj = feather_engine.create_feather_cluster("Body_Front_Down_Feather_Layer", _body_down_specs(),
                                                    mats["cream"], thickness=0.0014, bevel=0.0006)
        if obj: made.append(obj)
    if config.ENABLE_BACK_FEATHERS:
        obj = feather_engine.create_feather_cluster("Body_Back_Sage_Feather_Mantle", _back_feather_specs(),
                                                    mats["sage"], thickness=0.0022, bevel=0.0008)
        if obj: made.append(obj)
    if config.ENABLE_TAIL_FEATHERS:
        obj = feather_engine.create_feather_cluster("Tail_Individual_Feather_Fan", _tail_specs(),
                                                    mats["sage"], thickness=0.003, bevel=0.001)
        if obj: made.append(obj)
    return made


# bpy imported after declarations to keep helper functions easy to inspect.
import bpy
