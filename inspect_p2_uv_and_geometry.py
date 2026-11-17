"""Audit of mesh objects, materials, UV layers, and island topologies in Shukhpakhi P2."""

import bpy
import json
import os
import numpy as np

def audit_p2_scene():
    report = {}
    
    # Categorize objects
    mesh_objects = [o for o in bpy.data.objects if o.type == 'MESH']
    report["total_mesh_objects"] = len(mesh_objects)
    
    feather_mat = bpy.data.materials.get("Shukhpakhi_MAT_Feather_Vane_Microbarb")
    feather_objects = []
    other_objects = []
    
    for obj in mesh_objects:
        mat_names = [s.material.name for s in obj.material_slots if s.material]
        uv_layers = [uv.name for uv in obj.data.uv_layers]
        color_attrs = [ca.name for ca in obj.data.color_attributes]
        
        info = {
            "name": obj.name,
            "mesh_name": obj.data.name,
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "materials": mat_names,
            "uv_layers": uv_layers,
            "color_attributes": color_attrs,
        }
        
        if "Shukhpakhi_MAT_Feather_Vane_Microbarb" in mat_names:
            # Analyze UV details for feather objects
            mesh = obj.data
            uv_layer = mesh.uv_layers.active
            if uv_layer:
                uv_data = uv_layer.data
                uv_coords = [list(loop.uv) for loop in uv_data]
                if uv_coords:
                    uv_arr = np.array(uv_coords)
                    info["uv_min"] = [float(uv_arr[:, 0].min()), float(uv_arr[:, 1].min())]
                    info["uv_max"] = [float(uv_arr[:, 0].max()), float(uv_arr[:, 1].max())]
                    info["uv_mean"] = [float(uv_arr[:, 0].mean()), float(uv_arr[:, 1].mean())]
            feather_objects.append(info)
        else:
            other_objects.append(info)
            
    report["feather_objects_count"] = len(feather_objects)
    report["other_objects_count"] = len(other_objects)
    report["feather_objects"] = feather_objects
    report["other_objects"] = other_objects
    
    print(f"Total mesh objects: {len(mesh_objects)}")
    print(f"Feather objects: {len(feather_objects)}")
    for fo in feather_objects:
        uv_range = f"min={fo.get('uv_min')} max={fo.get('uv_max')}"
        print(f"  - {fo['name']}: {fo['polygons']} polys, UVs: {fo['uv_layers']}, UV range: {uv_range}")
        
    out_path = os.path.join(os.path.dirname(bpy.data.filepath), "..", "04_P2_OUTPUT", "REPORTS", "p2_initial_mesh_audit.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Audit written to: {out_path}")

if __name__ == "__main__":
    audit_p2_scene()
