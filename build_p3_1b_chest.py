import bpy, bmesh, math, os, json, numpy as np
from mathutils import Vector

def main():
    print("=== BUILDING PROTOTYPE B: CHEST PATCH ===")

    src_blend = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    bpy.ops.wm.open_mainfile(filepath=src_blend)

    out_dir = os.path.abspath("Shukhpakhi_Project/05_P3_RESEARCH_AND_PLANNING/PROTOTYPES")
    os.makedirs(out_dir, exist_ok=True)

    proto_col = bpy.data.collections.new("P3_1B_Chest_Patch_Prototype")
    bpy.context.scene.collection.children.link(proto_col)

    # Hide all production objects
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_viewport = True

    # 1. Create a 15x15 cm Chest Patch Base surface
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=0.075) # 15cm x 15cm
    # Give slight curvature matching breast
    for v in bm.verts:
        v.co.z += (0.075**2 - v.co.x**2 - v.co.y**2) * 2.0
    patch_mesh = bpy.data.meshes.new("P3_1B_Chest_Base_Mesh")
    bm.to_mesh(patch_mesh); bm.free()

    patch_obj = bpy.data.objects.new("P3_1B_Chest_Base_Surface", patch_mesh)
    proto_col.objects.link(patch_obj)
    patch_obj.location = Vector((0.0, -0.65, 0.95))
    patch_obj.hide_render = False; patch_obj.hide_viewport = False

    # Assign Cream undercoat material
    cream_mat = bpy.data.materials.get("Shukhpakhi_MAT_Undercoat_Natural")
    if cream_mat: patch_mesh.materials.append(cream_mat)

    # 2. Family A: Soft Down Filaments (Instanced down-clump mesh with Poisson distribution)
    bm_down = bmesh.new()
    # Create 3-prong soft filament clump
    for angle in (0, 120, 240):
        rad = math.radians(angle)
        dx, dy = math.cos(rad)*0.003, math.sin(rad)*0.003
        v0 = bm_down.verts.new((0, 0, 0))
        v1 = bm_down.verts.new((dx, dy, 0.012))
        bm_down.edges.new((v0, v1))
    down_mesh = bpy.data.meshes.new("P3_1B_Down_Filament_Mesh")
    bm_down.to_mesh(down_mesh); bm_down.free()

    down_mat = bpy.data.materials.get("Shukhpakhi_MAT_Down_Filaments")
    if down_mat: down_mesh.materials.append(down_mat)

    # Distribute 120 down clumps across surface
    rng = np.random.default_rng(42)
    down_count = 120
    for i in range(down_count):
        rx = (rng.uniform(-0.065, 0.065))
        ry = (rng.uniform(-0.065, 0.065))
        rz = (0.075**2 - rx**2 - ry**2) * 2.0 + 0.001

        clump = bpy.data.objects.new(f"Down_Clump_{i}", down_mesh)
        proto_col.objects.link(clump)
        clump.location = patch_obj.location + Vector((rx, ry, rz))
        clump.rotation_euler = (math.radians(rng.uniform(-15, 15)),
                                math.radians(rng.uniform(-15, 15)),
                                math.radians(rng.uniform(0, 360)))
        clump.hide_render = False; clump.hide_viewport = False

    # 3. Family C: Soft Cream Contour Feathers (5 Procedural Variants)
    feather_mat = bpy.data.materials.get("Shukhpakhi_MAT_Feather_Vane_Microbarb")
    contour_count = 35
    for i in range(contour_count):
        rx = (rng.uniform(-0.055, 0.055))
        ry = (rng.uniform(-0.055, 0.055))
        rz = (0.075**2 - rx**2 - ry**2) * 2.0 + 0.004

        # Soft rounded contour vane (Variant C2 - Broad Breast)
        w_vane = rng.uniform(0.018, 0.024)
        l_vane = rng.uniform(0.028, 0.035)

        bm_c = bmesh.new()
        bmesh.ops.create_grid(bm_c, x_segments=2, y_segments=3, size=1.0)
        # Reshape grid into rounded leaf contour
        for v in bm_c.verts:
            # v.co ranges [-1, 1]
            u_norm = (v.co.x + 1.0) / 2.0
            v_norm = (v.co.y + 1.0) / 2.0
            width_factor = math.sin(v_norm * math.pi) ** 0.7
            v.co.x *= (w_vane * 0.5) * width_factor
            v.co.y = (v_norm * l_vane)
            v.co.z = math.sin(v_norm * math.pi) * 0.002 # camber

        c_mesh = bpy.data.meshes.new(f"Contour_Vane_Mesh_{i}")
        bm_c.to_mesh(c_mesh); bm_c.free()

        # Add FeatherUV
        uv_layer = c_mesh.uv_layers.new(name="FeatherUV")
        for idx, ld in enumerate(uv_layer.data):
            # Cream body contour slot in P2 atlas: U ~ [0.345, 0.655], V ~ [0.678, 0.988]
            u_slot = 0.345 + (idx % 3) * 0.15
            v_slot = 0.678 + (idx // 3) * 0.08
            ld.uv = (u_slot, v_slot)

        if feather_mat: c_mesh.materials.append(feather_mat)

        c_obj = bpy.data.objects.new(f"Chest_Contour_{i}", c_mesh)
        proto_col.objects.link(c_obj)
        c_obj.location = patch_obj.location + Vector((rx, ry, rz))
        # Flow downward & slightly outward
        c_obj.rotation_euler = (math.radians(rng.uniform(-10, 5)),
                                math.radians(rng.uniform(-8, 8)),
                                math.radians(rng.uniform(-15, 15)))
        c_obj.hide_render = False; c_obj.hide_viewport = False

    # Save prototype blend
    proto_blend = os.path.join(out_dir, "P3_1B_Chest_Patch_Prototype.blend")
    bpy.ops.wm.save_as_mainfile(filepath=proto_blend)
    print(f"Saved: {proto_blend}")

    # Render Patch Close-up & Wireframe
    ren_dir = os.path.join(out_dir, "RENDERS_B")
    os.makedirs(ren_dir, exist_ok=True)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("ProtoB_Cam_Data")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 0.35 # close-up macro scale
    cam_obj = bpy.data.objects.new("ProtoB_Cam", cam_data)
    proto_col.objects.link(cam_obj)
    scene.camera = cam_obj

    light_data = bpy.data.lights.new("ProtoB_Light_Data", "AREA")
    light_data.energy = 150; light_data.size = 1.0
    light_obj = bpy.data.objects.new("ProtoB_Light", light_data)
    proto_col.objects.link(light_obj)
    light_obj.location = (0.5, -1.8, 1.5)

    target = patch_obj.location
    cam_obj.location = target + Vector((0.0, -1.2, 0.2))
    cam_obj.rotation_euler = (target - cam_obj.location).to_track_quat("-Z", "Y").to_euler()

    # Render 1: Shaded Macro
    out_shaded = os.path.join(ren_dir, "01_chest_macro_shaded.png")
    scene.render.filepath = out_shaded
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {out_shaded}")

    # Write Report JSON
    report = {
        "prototype": "P3.1B Chest Patch",
        "timestamp": os.path.getmtime(proto_blend),
        "source_blend": src_blend,
        "proto_blend": proto_blend,
        "patch_dimensions": "15cm x 15cm",
        "feather_counts": {
            "family_a_down_clumps": down_count,
            "family_c_contour_vanes": contour_count
        },
        "renders": [out_shaded],
        "status": "PROTOTYPE_COMPLETE_AWAITING_REVIEW"
    }
    with open(os.path.join(out_dir, "P3_1B_Chest_Report.json"), "w") as f:
        json.dump(report, f, indent=2)

    print("=== PROTOTYPE B COMPLETE ===")

if __name__ == "__main__":
    main()
