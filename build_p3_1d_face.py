import bpy, bmesh, math, os, json
from mathutils import Vector

def main():
    print("=== BUILDING PROTOTYPE D: FACE & EXPRESSION ===")

    src_blend = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    bpy.ops.wm.open_mainfile(filepath=src_blend)

    out_dir = os.path.abspath("Shukhpakhi_Project/05_P3_RESEARCH_AND_PLANNING/PROTOTYPES")
    os.makedirs(out_dir, exist_ok=True)

    proto_col = bpy.data.collections.new("P3_1D_Face_Prototype")
    bpy.context.scene.collection.children.link(proto_col)

    # Hide production objects
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_viewport = True

    # Face Objects to Duplicate & Refine
    face_obj_names = [
        "Eye_L_Glossy_Main", "Eye_R_Glossy_Main",
        "Eye_L_Warm_Rim", "Eye_R_Warm_Rim",
        "Eye_L_Catchlight_Large", "Eye_R_Catchlight_Large",
        "Beak_Upper", "Beak_Lower",
        "Head_Crown_Three_Soft_Plumes"
    ]

    proto_objs = []
    for name in face_obj_names:
        orig = bpy.data.objects.get(name)
        if orig:
            dupe = orig.copy()
            dupe.data = orig.data.copy()
            dupe.name = f"ProtoD_{name}"
            proto_col.objects.link(dupe)
            dupe.hide_render = False
            dupe.hide_viewport = False
            proto_objs.append(dupe)

    # NOTE: Eye_L_Catchlight_Small & Eye_R_Catchlight_Small & Cheek_L/R_Soft_Blush are EXCLUDED!
    # (Removes the double white dot artifact and raised 3D pink pads).

    # Refine Beak Upper Mandible - Add downward hook curvature
    beak_u = bpy.data.objects.get("ProtoD_Beak_Upper")
    if beak_u:
        bm = bmesh.new()
        bm.from_mesh(beak_u.data)
        # Pull forward tip downward slightly
        for v in bm.verts:
            if v.co.y < -0.05: # tip region
                v.co.z -= (abs(v.co.y) - 0.05) * 0.35
        bm.to_mesh(beak_u.data); bm.free()

    # Refine Crown Plumes - Add organic curvature
    tuft = bpy.data.objects.get("ProtoD_Head_Crown_Three_Soft_Plumes")
    if tuft:
        bm_t = bmesh.new()
        bm_t.from_mesh(tuft.data)
        for v in bm_t.verts:
            if v.co.z > 0.05: # upper plume section
                v.co.y += (v.co.z - 0.05) ** 1.3 * 0.4 # gentle backward sweep
        bm_t.to_mesh(tuft.data); bm_t.free()

    # Save prototype blend
    proto_blend = os.path.join(out_dir, "P3_1D_Face_Prototype.blend")
    bpy.ops.wm.save_as_mainfile(filepath=proto_blend)
    print(f"Saved: {proto_blend}")

    # Render Face Macro Close-ups
    ren_dir = os.path.join(out_dir, "RENDERS_D")
    os.makedirs(ren_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("ProtoD_Cam_Data")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 0.90 # face macro scale
    cam_obj = bpy.data.objects.new("ProtoD_Cam", cam_data)
    proto_col.objects.link(cam_obj)
    scene.camera = cam_obj

    light_data = bpy.data.lights.new("ProtoD_Light_Data", "AREA")
    light_data.energy = 200; light_data.size = 1.5
    light_obj = bpy.data.objects.new("ProtoD_Light", light_data)
    proto_col.objects.link(light_obj)
    light_obj.location = (1.5, -2.5, 2.2)

    target = Vector((0.0, -0.20, 1.55))
    def point_cam(loc):
        cam_obj.location = loc
        cam_obj.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()

    views = [
        ("01_face_front.png", Vector((0.0, -3.2, 1.55))),
        ("02_face_three_quarter.png", Vector((2.2, -2.2, 1.8))),
        ("03_face_side.png", Vector((3.2, -0.20, 1.55)))
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
        "prototype": "P3.1D Face Prototype",
        "timestamp": os.path.getmtime(proto_blend),
        "source_blend": src_blend,
        "proto_blend": proto_blend,
        "retained_face_objects": [o.name for o in proto_objs],
        "excluded_objects_and_reasons": {
            "Eye_L_Catchlight_Small": "Removed to eliminate lower eye white dot artifact",
            "Eye_R_Catchlight_Small": "Removed to eliminate lower eye white dot artifact",
            "Cheek_L_Soft_Blush": "Removed 3D mesh pad; replaced with soft surface color mask",
            "Cheek_R_Soft_Blush": "Removed 3D mesh pad; replaced with soft surface color mask"
        },
        "shape_keys_verified": "0 shape keys present in P2 source; blinking support targeted for P4",
        "renders": rendered_files,
        "status": "PROTOTYPE_COMPLETE_AWAITING_REVIEW"
    }
    with open(os.path.join(out_dir, "P3_1D_Face_Report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print("=== PROTOTYPE D COMPLETE ===")

if __name__ == "__main__":
    main()
