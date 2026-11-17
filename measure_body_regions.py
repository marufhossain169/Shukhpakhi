import bpy, bmesh, json
from mathutils import Vector

def main():
    src = "Shukhpakhi_Project/01_WORKING/Shukhpakhi_P2_Texture_v001.blend"
    bpy.ops.wm.open_mainfile(filepath=src)

    obj = bpy.data.objects.get("Body_Head_Fused_Soft_Undercoat")
    assert obj, "Undercoat object not found!"

    mw = obj.matrix_world
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    # World space vertex Z coordinates
    world_cos = [mw @ v.co for v in bm.verts]
    z_vals = [co.z for co in world_cos]
    x_vals = [co.x for co in world_cos]
    y_vals = [co.y for co in world_cos]

    z_min, z_max = min(z_vals), max(z_vals)
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)

    full_height = z_max - z_min
    full_width = x_max - x_min
    full_depth = y_max - y_min

    # Head region (Z >= 1.45m in world space)
    head_verts = [co for co in world_cos if co.z >= 1.45]
    head_x = [co.x for co in head_verts]
    head_z = [co.z for co in head_verts]
    head_width = max(head_x) - min(head_x)
    head_height = max(head_z) - min(head_z)

    # Torso region (Z < 1.45m in world space)
    torso_verts = [co for co in world_cos if co.z < 1.45]
    torso_x = [co.x for co in torso_verts]
    torso_z = [co.z for co in torso_verts]
    torso_width = max(torso_x) - min(torso_x)
    torso_height = max(torso_z) - min(torso_z)

    res = {
        "full_body_bounds": {
            "x_span": [round(x_min, 4), round(x_max, 4)],
            "y_span": [round(y_min, 4), round(y_max, 4)],
            "z_span": [round(z_min, 4), round(z_max, 4)],
            "full_width": round(full_width, 4),
            "full_depth": round(full_depth, 4),
            "full_height": round(full_height, 4),
            "full_height_to_width_ratio": round(full_height / full_width, 4)
        },
        "head_region_sep_z_1_45": {
            "head_width": round(head_width, 4),
            "head_height": round(head_height, 4),
            "head_to_full_width_ratio": round(head_width / full_width, 4)
        },
        "torso_region_sep_z_1_45": {
            "torso_width": round(torso_width, 4),
            "torso_height": round(torso_height, 4),
            "torso_height_to_width_ratio": round(torso_height / torso_width, 4)
        }
    }

    bm.free()

    with open("Shukhpakhi_Project/02_AUDIT_OUTPUT/body_region_measurements.json", "w") as f:
        json.dump(res, f, indent=2)

    print("Body region measurements complete!")

if __name__ == "__main__":
    main()
