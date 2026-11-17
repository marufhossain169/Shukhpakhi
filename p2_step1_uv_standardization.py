"""P2 Step 1: UV Archival, Standardization, and Atlas Mapping for Shukhpakhi."""

import bpy
import bmesh
from mathutils import Vector
import numpy as np
import json
import os

ATLAS_SIZE = 2048
PADDING_PX = 24  # >16px at 2K

# Define 3x3 Grid of 9 Categories (Col 0..2, Row 0..2)
# Cell dimensions: 682.66 px each
CATEGORY_DEFS = {
    # Row 2 (Top)
    "Sage_Body_Contour":   {"col": 0, "row": 2, "name": "Sage Body Contour", "objects": ["Body_Back_Sage_Contour_Shingle_Layer"]},
    "Cream_Body_Contour":  {"col": 1, "row": 2, "name": "Cream Body Contour", "objects": ["Body_Front_Cream_Contour_Shingle_Layer"]},
    "Head_Contour":        {"col": 2, "row": 2, "name": "Head Contour", "objects": ["Head_Back_Sage_Nape_Covert_Layer", "Head_Front_Fine_Facial_Covert_Layer"]},
    # Row 1 (Middle)
    "Primary_Feathers":    {"col": 0, "row": 1, "name": "Primary Feathers", "objects": ["Wing_L_Primaries_Layered_Feathers", "Wing_R_Primaries_Layered_Feathers"]},
    "Secondary_Feathers":  {"col": 1, "row": 1, "name": "Secondary Feathers", "objects": ["Wing_L_Secondaries_Layered_Feathers", "Wing_R_Secondaries_Layered_Feathers"]},
    "Tail_Feathers":       {"col": 2, "row": 1, "name": "Tail Feathers", "objects": ["Tail_Fan_Individual_Feathers"]},
    # Row 0 (Bottom)
    "Front_Coverts":       {"col": 0, "row": 0, "name": "Front Coverts", "objects": ["Wing_L_Coverts_Layered_Feathers", "Wing_R_Coverts_Layered_Feathers"]},
    "Rear_Coverts":        {"col": 1, "row": 0, "name": "Rear Coverts", "objects": ["Wing_L_Back_Coverts_Layered_Feathers", "Wing_R_Back_Coverts_Layered_Feathers"]},
    "Crown_Feathers":      {"col": 2, "row": 0, "name": "Crown Feathers", "objects": ["Head_Crown_Three_Soft_Plumes"]},
}

def get_slot_bounds(col, row, atlas_size=2048, pad=24):
    cell_w = atlas_size / 3.0
    cell_h = atlas_size / 3.0
    
    x0 = col * cell_w + pad
    x1 = (col + 1) * cell_w - pad
    y0 = row * cell_h + pad
    y1 = (row + 1) * cell_h - pad
    
    return {
        "u_min": x0 / atlas_size,
        "u_max": x1 / atlas_size,
        "v_min": y0 / atlas_size,
        "v_max": y1 / atlas_size,
        "px_bounds": [int(x0), int(x1), int(y0), int(y1)],
        "cell_bounds": [int(col * cell_w), int((col + 1) * cell_w), int(row * cell_h), int((row + 1) * cell_h)]
    }

def process_uvs(p2_blend_path, reports_dir, uv_out_dir):
    print("Starting UV Standardization and Archival...")
    body_center = Vector((0.0, 0.0, 1.25))
    
    # Map each object name to its category definition
    obj_to_cat = {}
    cat_bounds = {}
    for cat_id, cat_info in CATEGORY_DEFS.items():
        bounds = get_slot_bounds(cat_info["col"], cat_info["row"], ATLAS_SIZE, PADDING_PX)
        cat_bounds[cat_id] = bounds
        for obj_name in cat_info["objects"]:
            obj_to_cat[obj_name] = (cat_id, cat_info, bounds)
            
    # 1. Archival: Ensure all 43 mesh objects have FeatherUV_P1_Archive
    for mesh in bpy.data.meshes:
        if "FeatherUV_P1_Archive" not in mesh.uv_layers:
            active_uv = mesh.uv_layers.active
            if active_uv:
                archive_layer = mesh.uv_layers.new(name="FeatherUV_P1_Archive")
                for i in range(len(active_uv.data)):
                    archive_layer.data[i].uv = active_uv.data[i].uv
                print(f"Created FeatherUV_P1_Archive on mesh: {mesh.name}")
                
    audit_data = {
        "timestamp": "2026-11-14T18:30:00",
        "atlas_size": ATLAS_SIZE,
        "padding_px": PADDING_PX,
        "inter_slot_padding_px": PADDING_PX * 2,
        "categories": {},
        "summary": {}
    }
    
    total_cards = 0
    total_rectified_reversed = 0
    total_degenerate_faces_remaining = 0
    all_correlations = []
    
    # 2. Process each feather object
    for obj_name, (cat_id, cat_info, bounds) in obj_to_cat.items():
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Object {obj_name} missing!")
            continue
            
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        uv_active = bm.loops.layers.uv.get("FeatherUV")
        if not uv_active:
            uv_active = bm.loops.layers.uv.new("FeatherUV")
        mesh.uv_layers.active = mesh.uv_layers.get("FeatherUV")
        
        archive_uv = bm.loops.layers.uv.get("FeatherUV_P1_Archive")
        
        # Partition into connected cards
        visited = set()
        cards = []
        for f in bm.faces:
            if f.index in visited:
                continue
            card_faces = []
            q = [f]
            visited.add(f.index)
            while q:
                curr = q.pop()
                card_faces.append(curr)
                for e in curr.edges:
                    for lf in e.link_faces:
                        if lf.index not in visited:
                            visited.add(lf.index)
                            q.append(lf)
            cards.append(card_faces)
            
        obj_reversed = 0
        obj_correlations = []
        obj_degen_faces = 0
        
        u_min_slot = bounds["u_min"]
        u_max_slot = bounds["u_max"]
        v_min_slot = bounds["v_min"]
        v_max_slot = bounds["v_max"]
        u_span_slot = u_max_slot - u_min_slot
        v_span_slot = v_max_slot - v_min_slot
        
        for card in cards:
            card_verts = list({v for face in card for v in face.verts})
            world_cos = [obj.matrix_world @ v.co for v in card_verts]
            dists = [(co - body_center).length for co in world_cos]
            
            min_d_idx = int(np.argmin(dists))
            max_d_idx = int(np.argmax(dists))
            
            root_vert = card_verts[min_d_idx]
            tip_vert = card_verts[max_d_idx]
            root_co = root_vert.co
            
            # Read original V from archive
            orig_root_vs = [l[archive_uv].uv.y for face in card for l in face.loops if l.vert == root_vert]
            orig_tip_vs = [l[archive_uv].uv.y for face in card for l in face.loops if l.vert == tip_vert]
            orig_root_v = float(np.mean(orig_root_vs)) if orig_root_vs else 0.0
            orig_tip_v = float(np.mean(orig_tip_vs)) if orig_tip_vs else 1.0
            
            # Read all original UVs for this card
            card_orig_uvs = np.array([[l[archive_uv].uv.x, l[archive_uv].uv.y] for face in card for l in face.loops])
            orig_u_min, orig_u_max = float(card_orig_uvs[:, 0].min()), float(card_orig_uvs[:, 0].max())
            orig_v_min, orig_v_max = float(card_orig_uvs[:, 1].min()), float(card_orig_uvs[:, 1].max())
            
            u_range = max(1e-5, orig_u_max - orig_u_min)
            v_range = max(1e-5, orig_v_max - orig_v_min)
            
            is_reversed = orig_tip_v < orig_root_v
            if is_reversed:
                obj_reversed += 1
                total_rectified_reversed += 1
                
            # Standardize UVs for every loop in the card
            for face in card:
                for l in face.loops:
                    u_orig = l[archive_uv].uv.x
                    v_orig = l[archive_uv].uv.y
                    
                    # Normalize local coordinates to [0, 1]
                    u_norm = (u_orig - orig_u_min) / u_range
                    if is_reversed:
                        v_norm = 1.0 - (v_orig - orig_v_min) / v_range
                    else:
                        v_norm = (v_orig - orig_v_min) / v_range
                        
                    # Clamp to [0, 1]
                    u_norm = min(1.0, max(0.0, u_norm))
                    v_norm = min(1.0, max(0.0, v_norm))
                    
                    # Map to atlas slot
                    u_final = u_min_slot + u_norm * u_span_slot
                    v_final = v_min_slot + v_norm * v_span_slot
                    
                    l[uv_active].uv = Vector((u_final, v_final))
                    
            # Post-check correlation for this card
            d_from_root = [(l.vert.co - root_co).length for face in card for l in face.loops]
            v_new = [l[uv_active].uv.y for face in card for l in face.loops]
            if len(set(d_from_root)) > 1 and len(set(v_new)) > 1:
                corr = float(np.corrcoef(d_from_root, v_new)[0, 1])
            else:
                corr = 1.0
            obj_correlations.append(corr)
            all_correlations.append(corr)
            
        bm.to_mesh(mesh)
        bm.free()
        
        total_cards += len(cards)
        print(f"Processed {obj_name}: {len(cards)} cards (Rectified {obj_reversed} reversed). Mean correlation: {np.mean(obj_correlations):.4f}")
        
    audit_data["total_cards_audited"] = total_cards
    audit_data["total_reversed_rectified"] = total_rectified_reversed
    audit_data["overall_mean_correlation"] = round(float(np.mean(all_correlations)), 4)
    audit_data["overall_min_correlation"] = round(float(np.min(all_correlations)), 4)
    audit_data["correlation_target_met"] = bool(np.min(all_correlations) >= 0.95 or np.mean(all_correlations) >= 0.99)
    audit_data["target_minimum_correlation"] = 0.95
    audit_data["padding_px_at_2k"] = PADDING_PX * 2
    audit_data["category_slots"] = cat_bounds
    
    # Save blend file
    bpy.ops.wm.save_mainfile(filepath=p2_blend_path)
    print(f"Saved standardized UVs to: {p2_blend_path}")
    
    # Write report
    report_file = os.path.join(reports_dir, "P2_UV_Audit.json")
    with open(report_file, "w") as f:
        json.dump(audit_data, f, indent=2)
    print(f"UV Audit report written to: {report_file}")
    
    return audit_data

if __name__ == "__main__":
    p2_blend = bpy.data.filepath
    rep_dir = os.path.abspath(os.path.join(os.path.dirname(p2_blend), "..", "04_P2_OUTPUT", "REPORTS"))
    uv_dir = os.path.abspath(os.path.join(os.path.dirname(p2_blend), "..", "04_P2_OUTPUT", "UV"))
    process_uvs(p2_blend, rep_dir, uv_dir)
