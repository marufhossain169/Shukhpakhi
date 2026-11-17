"""Lightweight rigid-part master rig. This is a posing rig, not a skinned deformation rig."""
import bpy
from mathutils import Vector

COLLECTION = "Shukhpakhi_Rig"


def _parent_to_bone(obj, rig_obj, bone_name):
    world = obj.matrix_world.copy()
    obj.parent = rig_obj
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name
    obj.matrix_world = world


def build_rig():
    old = bpy.data.objects.get("Shukhpakhi_Rig")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    arm_data = bpy.data.armatures.new("Shukhpakhi_ArmatureData")
    rig = bpy.data.objects.new("Shukhpakhi_Rig", arm_data)
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        col = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(col)
    col.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones = {
        "Root": ((0, 0, 0.0), (0, 0, 0.45), None),
        "Body": ((0, 0, 0.45), (0, 0, 1.58), "Root"),
        "Wing.L": ((-0.48, 0, 1.48), (-0.88, 0, 1.04), "Body"),
        "Wing.R": ((0.48, 0, 1.48), (0.88, 0, 1.04), "Body"),
        "Leg.L": ((-0.22, 0, 0.46), (-0.235, 0, 0.08), "Body"),
        "Leg.R": ((0.22, 0, 0.46), (0.235, 0, 0.08), "Body"),
        "Tail": ((0, 0.48, 0.80), (0, 0.88, 0.72), "Body"),
    }
    for name, (head, tail, parent) in bones.items():
        bone = arm_data.edit_bones.new(name)
        bone.head = Vector(head)
        bone.tail = Vector(tail)
        if parent:
            bone.parent = arm_data.edit_bones[parent]
            bone.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    rig.display_type = "WIRE"
    rig["rig_type"] = "Rigid part posing rig; body is not yet skin-weight deformed."

    def objects_in(prefix):
        return [o for o in bpy.data.objects if o.name.startswith(prefix)]

    for prefix in ("Body_", "Head_", "Eye_", "Cheek_", "Beak_"):
        for obj in objects_in(prefix):
            _parent_to_bone(obj, rig, "Body")
    for side in ("L", "R"):
        for obj in objects_in("Wing_" + side + "_"):
            _parent_to_bone(obj, rig, "Wing." + side)
    for side in ("L", "R"):
        for prefix in (f"Leg_{side}", f"Foot_{side}"):
            for obj in objects_in(prefix):
                if obj.parent != rig:
                    _parent_to_bone(obj, rig, f"Leg.{side}")
    for obj in objects_in("Tail_"):
        _parent_to_bone(obj, rig, "Tail")
    # Keep the rig in its own collection and avoid accidental camera/render clutter.
    rig.hide_render = True
    return rig
