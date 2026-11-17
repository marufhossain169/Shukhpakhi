"""Deterministic builder for the Shukhpakhi Blender 5.3 master source model."""
import bpy
from . import utils, body, face, wings, feet, tuft, rig, expressions


def build_all():
    # Return to Object Mode before deleting/rebuilding datablocks.
    active = bpy.context.object
    if active is not None and active.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    # Remove only previous Shukhpakhi-owned objects/collections; preserve user scene content.
    utils.clear_project_collections()
    body.build()
    face.build()
    wings.build()
    feet.build()
    tuft.build()
    rig.build_rig()
    expressions.build_controller()
    expressions.set_expression("Normal")
    bpy.context.scene["Shukhpakhi_build_version"] = "Guide Reconstruction / Blender 5.3 / v1"
    bpy.context.scene["Shukhpakhi_reference_palette"] = "#A7C49A #D7E8C5 #F8F9E9 #EDE7D9 #F6A623"
    print("Shukhpakhi build complete. IMPORTANT: render comparison and visual QA are still required.")
