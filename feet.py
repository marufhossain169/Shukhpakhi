"""Short orange legs and rounded articulated toe geometry."""
import bpy
import bmesh
import math
from mathutils import Vector
from . import config, utils, materials

COLLECTION = config.COLLECTION_PREFIX + "Feet"


def build():
    utils.clear_collection(COLLECTION)
    mats = materials.create_all()
    made = []
    for side, sign in (("L", -1), ("R", 1)):
        x, y = sign * config.LEG_X, config.LEG_Y
        ankle = Vector((x, y, config.FOOT_Z + 0.025))
        hip = Vector((x * 0.88, y + 0.012, config.HIP_Z))
        bm = bmesh.new()
        utils.add_tapered_limb(bm, ankle, hip, config.LEG_RADIUS * 0.78,
                               config.LEG_RADIUS * 1.18, segments=18)
        mesh = bpy.data.meshes.new(f"Leg_{side}_Mesh")
        bm.to_mesh(mesh); bm.free()
        leg = bpy.data.objects.new(f"Leg_{side}_Short_Stalk", mesh)
        utils.link_object(leg, COLLECTION); mesh.materials.append(mats["orange"])
        utils.smooth_mesh(leg)
        made.append(leg)

        bm = bmesh.new()
        utils.add_uv_sphere_to_bmesh(bm, (x, y, config.FOOT_Z + 0.025),
                                     (0.046, 0.052, 0.035), 20, 14)
        mesh = bpy.data.meshes.new(f"Ankle_{side}_Mesh")
        bm.to_mesh(mesh); bm.free()
        ankle_obj = bpy.data.objects.new(f"Foot_{side}_Rounded_Ankle", mesh)
        utils.link_object(ankle_obj, COLLECTION); mesh.materials.append(mats["orange"])
        utils.smooth_mesh(ankle_obj); made.append(ankle_obj)

        toe_specs = [("Inner", -sign * 0.28, 0.92), ("Center", 0.0, 1.06),
                     ("Outer", sign * 0.28, 0.90)]
        for toe_name, yaw, factor in toe_specs:
            length = config.TOE_LENGTH * factor
            tip = Vector((x + math.sin(yaw) * length, y - math.cos(yaw) * length,
                          config.FOOT_Z + config.TOE_RADIUS * 0.55))
            bm = bmesh.new()
            utils.add_tapered_limb(bm, ankle, tip, config.TOE_RADIUS * 1.35,
                                   config.TOE_RADIUS * 0.78, segments=18)
            mesh = bpy.data.meshes.new(f"Toe_{side}_{toe_name}_Mesh")
            bm.to_mesh(mesh); bm.free()
            toe = bpy.data.objects.new(f"Foot_{side}_Toe_{toe_name}", mesh)
            utils.link_object(toe, COLLECTION); mesh.materials.append(mats["orange"])
            utils.smooth_mesh(toe); made.append(toe)

        # Rear hallux points backwards (positive Y) for believable perching anatomy.
        back_tip = Vector((x, y + config.TOE_LENGTH * 0.55,
                           config.FOOT_Z + config.TOE_RADIUS * 0.55))
        bm = bmesh.new()
        utils.add_tapered_limb(bm, ankle, back_tip, config.TOE_RADIUS * 1.25,
                               config.TOE_RADIUS * 0.75, segments=18)
        mesh = bpy.data.meshes.new(f"Hallux_{side}_Mesh")
        bm.to_mesh(mesh); bm.free()
        toe = bpy.data.objects.new(f"Foot_{side}_Rear_Hallux", mesh)
        utils.link_object(toe, COLLECTION); mesh.materials.append(mats["orange"])
        utils.smooth_mesh(toe); made.append(toe)
    return made
