import bpy, math, os, json
from mathutils import Vector

def main():
    print("=== BUILDING PROTOTYPE A: BODY SILHOUETTE ===")

    # Load P2 blend
    src_blend = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    bpy.ops.wm.open_mainfile(filepath=src_blend)

    # Create isolated collection for Prototype A
    proto_col = bpy.data.collections.new("P3_1A_Body_Silhouette_Prototype")
    bpy.context.scene.collection.children.link(proto_col)

    # Duplicate base torso object
    orig_torso = bpy.data.objects.get("Body_Head_Fused_Soft_Undercoat")
    assert orig_torso, "Original torso not found!"

    # Hide original torso and production layers from render for prototype evaluation
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_viewport = True

    # Create prototype duplicate
    proto_torso = orig_torso.copy()
    proto_torso.data = orig_torso.data.copy()
    proto_torso.name = "P3_1A_Torso_Reshaped_Prototype"
    proto_col.objects.link(proto_torso)
    proto_torso.hide_render = False
    proto_torso.hide_viewport = False

    # Record original dimensions
    orig_dims = list(orig_torso.dimensions)
    orig_height_width_ratio = orig_dims[2] / orig_dims[0]

    # Adjust prototype scale along Z to achieve target plump chick ratio (~1.15)
    # Original: X=1.43, Y=1.28, Z=2.21 (Z/X = 1.545)
    # Target height = 1.43 * 1.15 = 1.6445m
    scale_factor_z = (orig_dims[0] * 1.15) / orig_dims[2]  # ~0.744
    proto_torso.scale.z *= scale_factor_z
    bpy.context.view_layer.objects.active = proto_torso
    proto_torso.select_set(True)

    # Record reshaped dimensions
    bpy.context.view_layer.update()
    new_dims = list(proto_torso.dimensions)
    new_height_width_ratio = new_dims[2] / new_dims[0]

    # Landmarks
    landmarks = {
        "crown_top_z": round(proto_torso.location.z + new_dims[2] / 2.0, 4),
        "eye_center_z": 1.40,
        "widest_torso_width_x": round(new_dims[0], 4),
        "torso_depth_y": round(new_dims[1], 4),
        "belly_bottom_z": round(proto_torso.location.z - new_dims[2] / 2.0, 4),
        "hip_anchor_z": 0.465,
        "orig_height_width_ratio": round(orig_height_width_ratio, 4),
        "target_height_width_ratio": 1.15,
        "new_height_width_ratio": round(new_height_width_ratio, 4)
    }

    # Save prototype blend
    out_dir = os.path.abspath("Shukhpakhi_Project/05_P3_RESEARCH_AND_PLANNING/PROTOTYPES")
    os.makedirs(out_dir, exist_ok=True)
    proto_blend = os.path.join(out_dir, "P3_1A_Body_Silhouette_Prototype.blend")
    bpy.ops.wm.save_as_mainfile(filepath=proto_blend)
    print(f"Saved: {proto_blend}")

    # Render turnaround comparisons
    ren_dir = os.path.join(out_dir, "RENDERS_A")
    os.makedirs(ren_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    # Setup Camera
    cam_data = bpy.data.cameras.new("ProtoA_Cam_Data")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.8
    cam_obj = bpy.data.objects.new("ProtoA_Cam", cam_data)
    proto_col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Setup Light
    light_data = bpy.data.lights.new("ProtoA_Light_Data", "AREA")
    light_data.energy = 400; light_data.size = 3.0
    light_obj = bpy.data.objects.new("ProtoA_Light", light_data)
    proto_col.objects.link(light_obj)
    light_obj.location = (2.5, -3.5, 3.0)

    target = Vector((0.0, 0.0, 1.1))

    def point_cam(loc):
        cam_obj.location = loc
        cam_obj.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()

    views = [
        ("01_front.png", Vector((0.0, -6.0, 1.1))),
        ("02_three_quarter.png", Vector((4.2, -4.2, 1.8))),
        ("03_side.png", Vector((6.0, 0.0, 1.1)))
    ]

    rendered_files = []
    for fname, loc in views:
        point_cam(loc)
        out_path = os.path.join(ren_dir, fname)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        rendered_files.append(out_path)
        print(f"Rendered: {fname}")

    # Write Report JSON
    report = {
        "prototype": "P3.1A Body Silhouette",
        "timestamp": os.path.getmtime(proto_blend),
        "source_blend": src_blend,
        "proto_blend": proto_blend,
        "original_dimensions": [round(v, 4) for v in orig_dims],
        "reshaped_dimensions": [round(v, 4) for v in new_dims],
        "landmarks": landmarks,
        "renders": rendered_files,
        "status": "PROTOTYPE_COMPLETE_AWAITING_REVIEW"
    }
    with open(os.path.join(out_dir, "P3_1A_Body_Report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print("=== PROTOTYPE A COMPLETE ===")

if __name__ == "__main__":
    main()
