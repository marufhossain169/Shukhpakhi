import bpy, bmesh, math, os, json, numpy as np
from mathutils import Vector

def main():
    print("=== BUILDING PROTOTYPE C: WING ASSEMBLY ===")

    src_blend = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    bpy.ops.wm.open_mainfile(filepath=src_blend)

    out_dir = os.path.abspath("Shukhpakhi_Project/05_P3_RESEARCH_AND_PLANNING/PROTOTYPES")
    os.makedirs(out_dir, exist_ok=True)

    proto_col = bpy.data.collections.new("P3_1C_Wing_Assembly_Prototype")
    bpy.context.scene.collection.children.link(proto_col)

    # Hide all production objects
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_viewport = True

    # Materials
    sage_mat = bpy.data.materials.get("Shukhpakhi_MAT_Feather_Vane_Microbarb")
    undercoat_mat = bpy.data.materials.get("Shukhpakhi_MAT_Wing_Undercoat")

    # 1. Layer 0 — Low-Profile Anatomical Base Proxy
    bm_base = bmesh.new()
    bmesh.ops.create_uvsphere(bm_base, u_segments=12, v_segments=8, radius=0.15)
    # Scale into low-profile wing shape: X=0.25m, Y=0.35m, Z=0.12m
    for v in bm_base.verts:
        v.co.x *= (0.25 / 0.30)
        v.co.y *= (0.35 / 0.30)
        v.co.z *= (0.12 / 0.30)
    base_mesh = bpy.data.meshes.new("P3_1C_Wing_Base_Proxy_Mesh")
    bm_base.to_mesh(base_mesh); bm_base.free()

    base_obj = bpy.data.objects.new("P3_1C_Wing_L_Base_Proxy", base_mesh)
    proto_col.objects.link(base_obj)
    base_obj.location = Vector((0.52, -0.05, 1.25)) # Shoulder anchor
    base_obj.hide_render = False; base_obj.hide_viewport = False
    if undercoat_mat: base_mesh.materials.append(undercoat_mat)

    # Helper to generate a feather vane mesh
    def create_vane_mesh(name, length, width, u_slot_min, v_slot_min):
        bm_v = bmesh.new()
        bmesh.ops.create_grid(bm_v, x_segments=2, y_segments=4, size=1.0)
        for v in bm_v.verts:
            u_norm = (v.co.x + 1.0) / 2.0
            v_norm = (v.co.y + 1.0) / 2.0
            w_factor = math.sin(v_norm * math.pi) ** 0.6
            v.co.x *= (width * 0.5) * w_factor
            v.co.y = (v_norm * length)
            v.co.z = math.sin(v_norm * math.pi) * 0.003
        mesh = bpy.data.meshes.new(name)
        bm_v.to_mesh(mesh); bm_v.free()

        uv_layer = mesh.uv_layers.new(name="FeatherUV")
        for idx, ld in enumerate(uv_layer.data):
            ld.uv = (u_slot_min + (idx % 3)*0.1, v_slot_min + (idx // 3)*0.08)
        if sage_mat: mesh.materials.append(sage_mat)
        return mesh

    # Layers & Counts
    layer_counts = {
        "Layer_1_Scapulars": {"count": 8, "len": 0.09, "wid": 0.032, "uv": (0.012, 0.012)},
        "Layer_2_Lesser_Coverts": {"count": 18, "len": 0.055, "wid": 0.024, "uv": (0.012, 0.012)},
        "Layer_3_Median_Coverts": {"count": 14, "len": 0.070, "wid": 0.028, "uv": (0.345, 0.012)},
        "Layer_4_Greater_Coverts": {"count": 12, "len": 0.095, "wid": 0.030, "uv": (0.345, 0.012)},
        "Layer_5_Secondaries": {"count": 10, "len": 0.140, "wid": 0.032, "uv": (0.345, 0.345)},
        "Layer_6_Primaries": {"count": 8, "len": 0.180, "wid": 0.035, "uv": (0.012, 0.345)},
        "Layer_7_Alula": {"count": 3, "len": 0.045, "wid": 0.018, "uv": (0.678, 0.012)}
    }

    total_wing_feathers = sum(v["count"] for v in layer_counts.values()) # 73
    rng = np.random.default_rng(101)

    layer_objects = {}
    for lname, linfo in layer_counts.items():
        objs = []
        mesh = create_vane_mesh(f"{lname}_Mesh", linfo["len"], linfo["wid"], linfo["uv"][0], linfo["uv"][1])
        for i in range(linfo["count"]):
            f_obj = bpy.data.objects.new(f"Wing_L_{lname}_{i}", mesh)
            proto_col.objects.link(f_obj)

            # Position along wing span/depth
            t = (i + 0.5) / linfo["count"]
            rx = 0.42 + t * 0.22
            ry = -0.15 + (t - 0.5)*0.10
            rz = 1.25 + (0.5 - abs(t - 0.5))*0.10 - (list(layer_counts.keys()).index(lname))*0.012

            f_obj.location = Vector((rx, ry, rz))
            f_obj.rotation_euler = (math.radians(15 + rng.uniform(-5, 5)),
                                    math.radians(-20 + rng.uniform(-5, 5)),
                                    math.radians(rng.uniform(-10, 10)))
            f_obj.hide_render = False; f_obj.hide_viewport = False
            objs.append(f_obj.name)
        layer_objects[lname] = objs

    # Save prototype blend
    proto_blend = os.path.join(out_dir, "P3_1C_Wing_Assembly_Prototype.blend")
    bpy.ops.wm.save_as_mainfile(filepath=proto_blend)
    print(f"Saved: {proto_blend}")

    # Render Turnarounds
    ren_dir = os.path.join(out_dir, "RENDERS_C")
    os.makedirs(ren_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("ProtoC_Cam_Data")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 1.2 # wing macro view
    cam_obj = bpy.data.objects.new("ProtoC_Cam", cam_data)
    proto_col.objects.link(cam_obj)
    scene.camera = cam_obj

    light_data = bpy.data.lights.new("ProtoC_Light_Data", "AREA")
    light_data.energy = 250; light_data.size = 2.0
    light_obj = bpy.data.objects.new("ProtoC_Light", light_data)
    proto_col.objects.link(light_obj)
    light_obj.location = (2.0, -2.5, 2.5)

    target = base_obj.location
    def point_cam(loc):
        cam_obj.location = loc
        cam_obj.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()

    views = [
        ("01_wing_dorsal_front.png", Vector((0.52, -2.5, 1.25))),
        ("02_wing_three_quarter.png", Vector((2.2, -2.2, 2.0))),
        ("03_wing_side.png", Vector((2.8, -0.05, 1.25)))
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
        "prototype": "P3.1C Wing Assembly",
        "timestamp": os.path.getmtime(proto_blend),
        "source_blend": src_blend,
        "proto_blend": proto_blend,
        "base_proxy_dimensions": [0.25, 0.35, 0.12],
        "total_wing_feathers": total_wing_feathers,
        "layer_feather_counts": {k: v["count"] for k, v in layer_counts.items()},
        "renders": rendered_files,
        "status": "PROTOTYPE_COMPLETE_AWAITING_REVIEW"
    }
    with open(os.path.join(out_dir, "P3_1C_Wing_Report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print("=== PROTOTYPE C COMPLETE ===")

if __name__ == "__main__":
    main()
