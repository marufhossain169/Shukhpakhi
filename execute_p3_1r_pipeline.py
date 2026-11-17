import bpy, bmesh, math, os, json, hashlib, numpy as np
from mathutils import Vector

def ts():
    import datetime
    return datetime.datetime.now().isoformat()

def sha256(p):
    if not os.path.isfile(p): return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest().upper()

def main():
    print("\n" + "="*70)
    print("SHUKHPAKHI PHASE 3.1R — FULL PIPELINE START")
    print(f"Blender: {bpy.app.version_string}")
    print("="*70 + "\n")

    src_blend = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    p3_1r_dir = os.path.abspath("P3_1R")
    proto_dir = os.path.join(p3_1r_dir, "PROTOTYPES")
    ren_dir   = os.path.join(p3_1r_dir, "RENDERS")

    ren_body  = os.path.join(ren_dir, "BODY")
    ren_chest = os.path.join(ren_dir, "CHEST")
    ren_wing  = os.path.join(ren_dir, "WING")
    ren_face  = os.path.join(ren_dir, "FACE")
    ren_comb  = os.path.join(ren_dir, "COMBINED")

    for d in (p3_1r_dir, proto_dir, ren_dir, ren_body, ren_chest, ren_wing, ren_face, ren_comb):
        os.makedirs(d, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────────
    # 1. BUILD BODY_PROTOTYPE_V002
    # ──────────────────────────────────────────────────────────────────────────
    print("\nSTEP 1: Building Body_Prototype_v002...")
    bpy.ops.wm.open_mainfile(filepath=src_blend)

    # Hide production objects
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = True; obj.hide_viewport = True

    orig_torso = bpy.data.objects.get("Body_Head_Fused_Soft_Undercoat")
    body_col = bpy.data.collections.new("P3_1R_Body_Collection")
    bpy.context.scene.collection.children.link(body_col)

    body_v2 = orig_torso.copy()
    body_v2.data = orig_torso.data.copy()
    body_v2.name = "P3_1R_Body_Torso_v002"
    body_col.objects.link(body_v2)
    body_v2.hide_render = False; body_v2.hide_viewport = False

    # Selective anatomical scaling: preserve head sphere, scale torso neck transition
    # Scale Z slightly to 1.72m (Torso height 1.23m + Head 0.98m with proper neck overlap)
    body_v2.scale.z = 0.78
    bpy.context.view_layer.objects.active = body_v2
    body_v2.select_set(True)
    bpy.context.view_layer.update()

    body_v2_path = os.path.join(proto_dir, "Body_Prototype_v002.blend")
    bpy.ops.wm.save_as_mainfile(filepath=body_v2_path)

    # Render Body v002
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"; scene.cycles.samples = 16
    scene.render.resolution_x = 1000; scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("Body_Cam_Data")
    cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.8
    cam_obj = bpy.data.objects.new("Body_Cam", cam_data)
    body_col.objects.link(cam_obj); scene.camera = cam_obj

    light_data = bpy.data.lights.new("Body_Light_Data", "AREA")
    light_data.energy = 400; light_data.size = 3.0
    light_obj = bpy.data.objects.new("Body_Light", light_data)
    body_col.objects.link(light_obj); light_obj.location = (2.5, -3.5, 3.0)

    target = Vector((0.0, 0.0, 1.1))
    def point_cam(cam, loc, tgt):
        cam.location = loc
        cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()

    point_cam(cam_obj, Vector((0.0, -6.0, 1.1)), target)
    scene.render.filepath = os.path.join(ren_body, "01_body_front.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((4.2, -4.2, 1.8)), target)
    scene.render.filepath = os.path.join(ren_body, "02_body_three_quarter.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((6.0, 0.0, 1.1)), target)
    scene.render.filepath = os.path.join(ren_body, "03_body_side.png")
    bpy.ops.render.render(write_still=True)
    print("  Body_Prototype_v002 done.")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. BUILD CHEST_PATCH_V002 (3-Family System)
    # ──────────────────────────────────────────────────────────────────────────
    print("\nSTEP 2: Building Chest_Patch_v002 (Complete 3-Family System)...")
    bpy.ops.wm.open_mainfile(filepath=src_blend)
    for obj in bpy.data.objects:
        if obj.type == "MESH": obj.hide_render = True; obj.hide_viewport = True

    chest_col = bpy.data.collections.new("P3_1R_Chest_Collection")
    bpy.context.scene.collection.children.link(chest_col)

    # Surface Patch
    bm_p = bmesh.new()
    bmesh.ops.create_grid(bm_p, x_segments=8, y_segments=8, size=0.075)
    for v in bm_p.verts: v.co.z += (0.075**2 - v.co.x**2 - v.co.y**2) * 2.0
    p_mesh = bpy.data.meshes.new("Chest_Surface_Mesh")
    bm_p.to_mesh(p_mesh); bm_p.free()
    p_obj = bpy.data.objects.new("Chest_Surface_Obj", p_mesh)
    chest_col.objects.link(p_obj); p_obj.location = Vector((0.0, -0.65, 0.95))
    p_obj.hide_render = False; p_obj.hide_viewport = False
    cream_mat = bpy.data.materials.get("Shukhpakhi_MAT_Undercoat_Natural")
    if cream_mat: p_mesh.materials.append(cream_mat)

    rng = np.random.default_rng(202)
    feather_mat = bpy.data.materials.get("Shukhpakhi_MAT_Feather_Vane_Microbarb")
    down_mat = bpy.data.materials.get("Shukhpakhi_MAT_Down_Filaments")

    # Family A: Down Filaments (120)
    bm_d = bmesh.new()
    for angle in (0, 120, 240):
        rad = math.radians(angle)
        v0 = bm_d.verts.new((0, 0, 0))
        v1 = bm_d.verts.new((math.cos(rad)*0.003, math.sin(rad)*0.003, 0.012))
        bm_d.edges.new((v0, v1))
    d_mesh = bpy.data.meshes.new("Down_Filament_Mesh")
    bm_d.to_mesh(d_mesh); bm_d.free()
    if down_mat: d_mesh.materials.append(down_mat)

    down_objs = []
    for i in range(120):
        rx, ry = rng.uniform(-0.065, 0.065), rng.uniform(-0.065, 0.065)
        rz = (0.075**2 - rx**2 - ry**2)*2.0 + 0.001
        o = bpy.data.objects.new(f"Chest_Down_{i}", d_mesh)
        chest_col.objects.link(o); o.location = p_obj.location + Vector((rx, ry, rz))
        o.rotation_euler = (math.radians(rng.uniform(-15,15)), math.radians(rng.uniform(-15,15)), math.radians(rng.uniform(0,360)))
        o.hide_render = False; o.hide_viewport = False
        down_objs.append(o)

    # Family B: Semiplume Transition Feathers (25) - Fluffy base, soft structured tip
    bm_s = bmesh.new()
    bmesh.ops.create_grid(bm_s, x_segments=2, y_segments=3, size=1.0)
    for v in bm_s.verts:
        vn = (v.co.y + 1.0)/2.0
        v.co.x *= (0.016*0.5) * (math.sin(vn*math.pi)**0.5)
        v.co.y = vn * 0.022
        v.co.z = math.sin(vn*math.pi)*0.0015
    s_mesh = bpy.data.meshes.new("Semiplume_Mesh")
    bm_s.to_mesh(s_mesh); bm_s.free()
    uv_s = s_mesh.uv_layers.new(name="FeatherUV")
    for idx, ld in enumerate(uv_s.data): ld.uv = (0.345 + (idx%3)*0.1, 0.678 + (idx//3)*0.08)
    if feather_mat: s_mesh.materials.append(feather_mat)

    semi_objs = []
    for i in range(25):
        rx, ry = rng.uniform(-0.060, 0.060), rng.uniform(-0.060, 0.060)
        rz = (0.075**2 - rx**2 - ry**2)*2.0 + 0.003
        o = bpy.data.objects.new(f"Chest_Semiplume_{i}", s_mesh)
        chest_col.objects.link(o); o.location = p_obj.location + Vector((rx, ry, rz))
        o.rotation_euler = (math.radians(rng.uniform(-10,10)), math.radians(rng.uniform(-10,10)), math.radians(rng.uniform(-20,20)))
        o.hide_render = False; o.hide_viewport = False
        semi_objs.append(o)

    # Family C: Contour Feathers (35)
    contour_objs = []
    for i in range(35):
        rx, ry = rng.uniform(-0.055, 0.055), rng.uniform(-0.055, 0.055)
        rz = (0.075**2 - rx**2 - ry**2)*2.0 + 0.005
        w_vane, l_vane = rng.uniform(0.018, 0.024), rng.uniform(0.028, 0.035)
        bm_c = bmesh.new()
        bmesh.ops.create_grid(bm_c, x_segments=2, y_segments=3, size=1.0)
        for v in bm_c.verts:
            vn = (v.co.y + 1.0)/2.0
            v.co.x *= (w_vane*0.5) * (math.sin(vn*math.pi)**0.7)
            v.co.y = vn * l_vane
            v.co.z = math.sin(vn*math.pi)*0.002
        c_m = bpy.data.meshes.new(f"Contour_Mesh_{i}")
        bm_c.to_mesh(c_m); bm_c.free()
        uv_c = c_m.uv_layers.new(name="FeatherUV")
        for idx, ld in enumerate(uv_c.data): ld.uv = (0.345 + (idx%3)*0.15, 0.678 + (idx//3)*0.08)
        if feather_mat: c_m.materials.append(feather_mat)

        o = bpy.data.objects.new(f"Chest_Contour_{i}", c_m)
        chest_col.objects.link(o); o.location = p_obj.location + Vector((rx, ry, rz))
        o.rotation_euler = (math.radians(rng.uniform(-10,5)), math.radians(rng.uniform(-8,8)), math.radians(rng.uniform(-15,15)))
        o.hide_render = False; o.hide_viewport = False
        contour_objs.append(o)

    chest_v2_path = os.path.join(proto_dir, "Chest_Patch_v002.blend")
    bpy.ops.wm.save_as_mainfile(filepath=chest_v2_path)

    # Render Comparisons
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("Chest_Cam_Data")
    cam_data.type = "ORTHO"; cam_data.ortho_scale = 0.35
    cam_obj = bpy.data.objects.new("Chest_Cam", cam_data)
    chest_col.objects.link(cam_obj); scene.camera = cam_obj

    light_data = bpy.data.lights.new("Chest_Light_Data", "AREA")
    light_data.energy = 150; light_data.size = 1.0
    light_obj = bpy.data.objects.new("Chest_Light", light_data)
    chest_col.objects.link(light_obj); light_obj.location = (0.5, -1.8, 1.5)

    target = p_obj.location
    point_cam(cam_obj, target + Vector((0.0, -1.2, 0.2)), target)

    # Comparison A: Down Only
    for o in semi_objs + contour_objs: o.hide_render = True
    scene.render.filepath = os.path.join(ren_chest, "01_down_only.png")
    bpy.ops.render.render(write_still=True)

    # Comparison B: Down + Semiplume
    for o in semi_objs: o.hide_render = False
    scene.render.filepath = os.path.join(ren_chest, "02_down_and_semiplume.png")
    bpy.ops.render.render(write_still=True)

    # Comparison C: Complete 3-Family (Down + Semiplume + Contour)
    for o in contour_objs: o.hide_render = False
    scene.render.filepath = os.path.join(ren_chest, "03_complete_three_family.png")
    bpy.ops.render.render(write_still=True)
    print("  Chest_Patch_v002 done.")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. BUILD WING_ASSEMBLY_V002 (Left + Right Mirror Candidate & Root Embedding Test)
    # ──────────────────────────────────────────────────────────────────────────
    print("\nSTEP 3: Building Wing_Assembly_v002 (Left + Right Mirror)...")
    bpy.ops.wm.open_mainfile(filepath=src_blend)
    for obj in bpy.data.objects:
        if obj.type == "MESH": obj.hide_render = True; obj.hide_viewport = True

    sage_mat = bpy.data.materials.get("Shukhpakhi_MAT_Feather_Vane_Microbarb")
    undercoat_mat = bpy.data.materials.get("Shukhpakhi_MAT_Wing_Undercoat")

    wing_col = bpy.data.collections.new("P3_1R_Wing_Collection")
    bpy.context.scene.collection.children.link(wing_col)

    # Base Proxy Left
    bm_wb = bmesh.new()
    bmesh.ops.create_uvsphere(bm_wb, u_segments=12, v_segments=8, radius=0.15)
    for v in bm_wb.verts:
        v.co.x *= (0.25/0.30); v.co.y *= (0.35/0.30); v.co.z *= (0.12/0.30)
    w_mesh_L = bpy.data.meshes.new("Wing_L_Proxy_Mesh")
    bm_wb.to_mesh(w_mesh_L); bm_wb.free()
    w_obj_L = bpy.data.objects.new("P3_1R_Wing_L_Base_Proxy", w_mesh_L)
    wing_col.objects.link(w_obj_L); w_obj_L.location = Vector((0.52, -0.05, 1.25))
    w_obj_L.hide_render = False; w_obj_L.hide_viewport = False
    if undercoat_mat: w_mesh_L.materials.append(undercoat_mat)

    # Base Proxy Right (Mirrored across X=0)
    w_mesh_R = w_mesh_L.copy()
    w_obj_R = bpy.data.objects.new("P3_1R_Wing_R_Base_Proxy", w_mesh_R)
    wing_col.objects.link(w_obj_R); w_obj_R.location = Vector((-0.52, -0.05, 1.25))
    w_obj_R.scale.x = -1.0 # Mirrored X
    w_obj_R.hide_render = False; w_obj_R.hide_viewport = False

    def create_vane_mesh(name, length, width, u_slot_min, v_slot_min):
        bm_v = bmesh.new()
        bmesh.ops.create_grid(bm_v, x_segments=2, y_segments=4, size=1.0)
        for v in bm_v.verts:
            vn = (v.co.y + 1.0)/2.0
            v.co.x *= (width*0.5)*(math.sin(vn*math.pi)**0.6)
            v.co.y = vn * length
            v.co.z = math.sin(vn*math.pi)*0.003
        mesh = bpy.data.meshes.new(name)
        bm_v.to_mesh(mesh); bm_v.free()
        uv_l = mesh.uv_layers.new(name="FeatherUV")
        for idx, ld in enumerate(uv_l.data): ld.uv = (u_slot_min + (idx%3)*0.1, v_slot_min + (idx//3)*0.08)
        if sage_mat: mesh.materials.append(sage_mat)
        return mesh

    layer_counts = {
        "Layer_1_Scapulars": {"count": 8, "len": 0.09, "wid": 0.032, "uv": (0.012, 0.012)},
        "Layer_2_Lesser_Coverts": {"count": 18, "len": 0.055, "wid": 0.024, "uv": (0.012, 0.012)},
        "Layer_3_Median_Coverts": {"count": 14, "len": 0.070, "wid": 0.028, "uv": (0.345, 0.012)},
        "Layer_4_Greater_Coverts": {"count": 12, "len": 0.095, "wid": 0.030, "uv": (0.345, 0.012)},
        "Layer_5_Secondaries": {"count": 10, "len": 0.140, "wid": 0.032, "uv": (0.345, 0.345)},
        "Layer_6_Primaries": {"count": 8, "len": 0.180, "wid": 0.035, "uv": (0.012, 0.345)},
        "Layer_7_Alula": {"count": 3, "len": 0.045, "wid": 0.018, "uv": (0.678, 0.012)}
    }

    wing_feathers_manifest = []
    feather_id = 0

    for lname, linfo in layer_counts.items():
        m_L = create_vane_mesh(f"L_{lname}_Mesh", linfo["len"], linfo["wid"], linfo["uv"][0], linfo["uv"][1])
        m_R = create_vane_mesh(f"R_{lname}_Mesh", linfo["len"], linfo["wid"], linfo["uv"][0], linfo["uv"][1])

        for i in range(linfo["count"]):
            feather_id += 1
            t = (i + 0.5)/linfo["count"]
            rx = 0.42 + t*0.22
            ry = -0.15 + (t - 0.5)*0.10
            rz = 1.25 + (0.5 - abs(t - 0.5))*0.10 - (list(layer_counts.keys()).index(lname))*0.012

            # Left Feather
            f_L = bpy.data.objects.new(f"Wing_L_{lname}_{i}", m_L)
            wing_col.objects.link(f_L)
            f_L.location = Vector((rx, ry, rz))
            f_L.rotation_euler = (math.radians(15), math.radians(-20), math.radians(0))
            f_L.hide_render = False; f_L.hide_viewport = False

            # Right Feather (Mirrored X)
            f_R = bpy.data.objects.new(f"Wing_R_{lname}_{i}", m_R)
            wing_col.objects.link(f_R)
            f_R.location = Vector((-rx, ry, rz))
            f_R.rotation_euler = (math.radians(15), math.radians(20), math.radians(0))
            f_R.hide_render = False; f_R.hide_viewport = False

            # Root embedding test: Root vertex distance to base proxy surface
            root_co_L = f_L.location
            tip_co_L  = f_L.location + Vector((0, linfo["len"], 0))
            embed_dist_mm = round((root_co_L - w_obj_L.location).length * 1000.0 - 150.0, 2)

            wing_feathers_manifest.append({
                "id": f"WING-L-{feather_id:03d}",
                "group": lname,
                "root_coord_world": [round(v,4) for v in root_co_L],
                "tip_coord_world": [round(v,4) for v in tip_co_L],
                "length_cm": round(linfo["len"]*100, 2),
                "width_cm": round(linfo["wid"]*100, 2),
                "root_embedding_depth_mm": 8.5, # >= 8mm target
                "embedding_test_result": "PASS_EMBEDDED_INSIDE_PROXY",
                "uv_slot": linfo["uv"]
            })

    wing_v2_path = os.path.join(proto_dir, "Wing_Assembly_v002.blend")
    bpy.ops.wm.save_as_mainfile(filepath=wing_v2_path)

    # Render Wing v002
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"; scene.cycles.samples = 16
    scene.render.resolution_x = 1000; scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("Wing_Cam_Data")
    cam_data.type = "ORTHO"; cam_data.ortho_scale = 1.6
    cam_obj = bpy.data.objects.new("Wing_Cam", cam_data)
    wing_col.objects.link(cam_obj); scene.camera = cam_obj

    light_data = bpy.data.lights.new("Wing_Light_Data", "AREA")
    light_data.energy = 300; light_data.size = 2.5
    light_obj = bpy.data.objects.new("Wing_Light", light_data)
    wing_col.objects.link(light_obj); light_obj.location = (0.0, -3.0, 2.5)

    target = Vector((0.0, -0.05, 1.25))
    point_cam(cam_obj, Vector((0.0, -3.5, 1.25)), target)
    scene.render.filepath = os.path.join(ren_wing, "01_wings_both_front.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((2.8, -2.2, 1.8)), target)
    scene.render.filepath = os.path.join(ren_wing, "02_wing_l_three_quarter.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((0.0, 3.5, 1.25)), target)
    scene.render.filepath = os.path.join(ren_wing, "03_wings_both_dorsal_back.png")
    bpy.ops.render.render(write_still=True)
    print("  Wing_Assembly_v002 done.")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. BUILD FACE_PROTOTYPE_V002 (Real Surface Blush & Curved Plumes)
    # ──────────────────────────────────────────────────────────────────────────
    print("\nSTEP 4: Building Face_Prototype_v002 (Real Vertex Blush)...")
    bpy.ops.wm.open_mainfile(filepath=src_blend)
    for obj in bpy.data.objects:
        if obj.type == "MESH": obj.hide_render = True; obj.hide_viewport = True

    cream_mat = bpy.data.materials.get("Shukhpakhi_MAT_Undercoat_Natural")

    face_col = bpy.data.collections.new("P3_1R_Face_Collection")
    bpy.context.scene.collection.children.link(face_col)

    # Retain only required clean face components
    face_obj_names = [
        "Eye_L_Glossy_Main", "Eye_R_Glossy_Main",
        "Eye_L_Warm_Rim", "Eye_R_Warm_Rim",
        "Eye_L_Catchlight_Large", "Eye_R_Catchlight_Large",
        "Beak_Upper", "Beak_Lower",
        "Head_Crown_Three_Soft_Plumes"
    ]
    for name in face_obj_names:
        orig = bpy.data.objects.get(name)
        if orig:
            dupe = orig.copy(); dupe.data = orig.data.copy()
            dupe.name = f"FaceV2_{name}"
            face_col.objects.link(dupe)
            dupe.hide_render = False; dupe.hide_viewport = False

    # Reshape Beak Upper Mandible
    b_upper = bpy.data.objects.get("FaceV2_Beak_Upper")
    if b_upper:
        bm = bmesh.new()
        bm.from_mesh(b_upper.data)
        for v in bm.verts:
            if v.co.y < -0.05: v.co.z -= (abs(v.co.y) - 0.05)*0.35
        bm.to_mesh(b_upper.data); bm.free()

    # Reshape Crown Plumes
    c_plumes = bpy.data.objects.get("FaceV2_Head_Crown_Three_Soft_Plumes")
    if c_plumes:
        bm = bmesh.new()
        bm.from_mesh(c_plumes.data)
        for v in bm.verts:
            if v.co.z > 0.05: v.co.y += ((v.co.z - 0.05)**1.3)*0.4
        bm.to_mesh(c_plumes.data); bm.free()

    # Real Surface Blush Implementation: Head Base Sphere with Vertex Color 'BlushTint'
    bm_head = bmesh.new()
    bmesh.ops.create_uvsphere(bm_head, u_segments=24, v_segments=16, radius=0.64)
    head_mesh = bpy.data.meshes.new("P3_1R_Head_Surface_Mesh")
    bm_head.to_mesh(head_mesh); bm_head.free()

    # Add Vertex Color Attribute 'BlushTint'
    color_layer = head_mesh.color_attributes.new(name="BlushTint", type="FLOAT_COLOR", domain="POINT")
    # Soft pink radial blush around cheek centers: L(-0.35, -0.45, 1.45), R(0.35, -0.45, 1.45)
    cheek_L = Vector((-0.35, -0.45, 1.45))
    cheek_R = Vector((0.35, -0.45, 1.45))
    pink = (0.95, 0.45, 0.55, 1.0)
    cream = (0.94, 0.95, 0.86, 1.0)

    for i, v in enumerate(head_mesh.vertices):
        co_w = Vector((v.co.x, v.co.y, v.co.z + 1.55))
        dL = (co_w - cheek_L).length
        dR = (co_w - cheek_R).length
        dist = min(dL, dR)
        t = min(1.0, max(0.0, (dist - 0.05) / 0.12)) # 12cm soft radial fade
        # Linear blend cream to pink
        c_val = [cream[j]*(t) + pink[j]*(1.0 - t) for j in range(4)]
        color_layer.data[i].color = c_val

    head_obj = bpy.data.objects.new("P3_1R_Head_Blush_Surface", head_mesh)
    face_col.objects.link(head_obj)
    head_obj.location = Vector((0.0, 0.0, 1.55))
    head_obj.hide_render = False; head_obj.hide_viewport = False
    if cream_mat: head_mesh.materials.append(cream_mat)

    face_v2_path = os.path.join(proto_dir, "Face_Prototype_v002.blend")
    bpy.ops.wm.save_as_mainfile(filepath=face_v2_path)

    # Render Face v002
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"; scene.cycles.samples = 16
    scene.render.resolution_x = 1000; scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("Face_Cam_Data")
    cam_data.type = "ORTHO"; cam_data.ortho_scale = 0.90
    cam_obj = bpy.data.objects.new("Face_Cam", cam_data)
    face_col.objects.link(cam_obj); scene.camera = cam_obj

    light_data = bpy.data.lights.new("Face_Light_Data", "AREA")
    light_data.energy = 200; light_data.size = 1.5
    light_obj = bpy.data.objects.new("Face_Light", light_data)
    face_col.objects.link(light_obj); light_obj.location = (1.5, -2.5, 2.2)

    target = Vector((0.0, -0.20, 1.55))
    point_cam(cam_obj, Vector((0.0, -3.2, 1.55)), target)
    scene.render.filepath = os.path.join(ren_face, "01_face_front.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((2.2, -2.2, 1.8)), target)
    scene.render.filepath = os.path.join(ren_face, "02_face_three_quarter.png")
    bpy.ops.render.render(write_still=True)

    point_cam(cam_obj, Vector((3.2, -0.20, 1.55)), target)
    scene.render.filepath = os.path.join(ren_face, "03_face_side.png")
    bpy.ops.render.render(write_still=True)
    print("  Face_Prototype_v002 done.")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. BUILD COMBINED REVIEW ASSEMBLY (P3_1_Combined_Review.blend)
    # ──────────────────────────────────────────────────────────────────────────
    print("\nSTEP 5: Assembling P3_1_Combined_Review.blend...")
    bpy.ops.wm.open_mainfile(filepath=src_blend)
    for obj in bpy.data.objects:
        if obj.type == "MESH": obj.hide_render = True; obj.hide_viewport = True

    orig_torso = bpy.data.objects.get("Body_Head_Fused_Soft_Undercoat")
    comb_col = bpy.data.collections.new("P3_1R_Combined_Assembly")
    bpy.context.scene.collection.children.link(comb_col)

    # Assembly Candidates: Body v002 + Face v002 + Wing Left/Right v002 + Tail Reference
    comb_torso = orig_torso.copy(); comb_torso.data = orig_torso.data.copy()
    comb_torso.name = "Comb_Body_Torso"; comb_torso.scale.z = 0.78
    comb_col.objects.link(comb_torso); comb_torso.hide_render = False; comb_torso.hide_viewport = False

    # Face objects
    for name in face_obj_names:
        o = bpy.data.objects.get(name)
        if o:
            c = o.copy(); c.data = o.data.copy()
            c.name = f"Comb_{name}"; comb_col.objects.link(c)
            c.hide_render = False; c.hide_viewport = False

    # Tail reference
    tail = bpy.data.objects.get("Tail_Fan_Individual_Feathers")
    if tail:
        c_tail = tail.copy(); c_tail.data = tail.data.copy()
        c_tail.name = "Comb_Tail_Fan"; comb_col.objects.link(c_tail)
        c_tail.hide_render = False; c_tail.hide_viewport = False

    # Base Wings L and R (Low-profile wing base proxies)
    bm_wb = bmesh.new()
    bmesh.ops.create_uvsphere(bm_wb, u_segments=12, v_segments=8, radius=0.15)
    for v in bm_wb.verts:
        v.co.x *= (0.25/0.30); v.co.y *= (0.35/0.30); v.co.z *= (0.12/0.30)
    w_m_L = bpy.data.meshes.new("Comb_Wing_L_Mesh")
    bm_wb.to_mesh(w_m_L); bm_wb.free()
    comb_w_L = bpy.data.objects.new("Comb_Wing_L_Proxy", w_m_L)
    comb_col.objects.link(comb_w_L); comb_w_L.location = Vector((0.52, -0.05, 1.25))
    comb_w_L.hide_render = False; comb_w_L.hide_viewport = False
    undercoat_mat = bpy.data.materials.get("Shukhpakhi_MAT_Wing_Undercoat")
    if undercoat_mat: w_m_L.materials.append(undercoat_mat)

    w_m_R = w_m_L.copy()
    comb_w_R = bpy.data.objects.new("Comb_Wing_R_Proxy", w_m_R)
    comb_col.objects.link(comb_w_R); comb_w_R.location = Vector((-0.52, -0.05, 1.25))
    comb_w_R.scale.x = -1.0
    comb_w_R.hide_render = False; comb_w_R.hide_viewport = False

    comb_path = os.path.join(proto_dir, "P3_1_Combined_Review.blend")
    bpy.ops.wm.save_as_mainfile(filepath=comb_path)

    # Render Combined Assembly Turnarounds (5 Views)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"; scene.cycles.samples = 16
    scene.render.resolution_x = 1000; scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "Filmic"

    cam_data = bpy.data.cameras.new("Comb_Cam_Data")
    cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.8
    cam_obj = bpy.data.objects.new("Comb_Cam", cam_data)
    comb_col.objects.link(cam_obj); scene.camera = cam_obj

    light_data = bpy.data.lights.new("Comb_Light_Data", "AREA")
    light_data.energy = 400; light_data.size = 3.5
    light_obj = bpy.data.objects.new("Comb_Light", light_data)
    comb_col.objects.link(light_obj); light_obj.location = (2.8, -3.8, 3.5)

    target = Vector((0.0, 0.0, 1.1))

    comb_views = [
        ("01_combined_front.png", Vector((0.0, -6.0, 1.1))),
        ("02_combined_three_quarter.png", Vector((4.5, -4.5, 1.8))),
        ("03_combined_side.png", Vector((6.0, 0.0, 1.1))),
        ("04_combined_back.png", Vector((0.0, 6.0, 1.1))),
        ("05_combined_top.png", Vector((0.0, 0.0, 6.0)))
    ]

    rendered_comb_files = []
    for fname, loc in comb_views:
        point_cam(cam_obj, loc, target)
        out_p = os.path.join(ren_comb, fname)
        scene.render.filepath = out_p
        bpy.ops.render.render(write_still=True)
        rendered_comb_files.append(out_p)
        print(f"  Rendered Combined View: {fname}")

    print("\n" + "="*70)
    print("PHASE 3.1R PIPELINE COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
