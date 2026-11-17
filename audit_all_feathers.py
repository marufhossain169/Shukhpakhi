"""Complete audit of all 5,129 feather cards across all 14 feather objects."""

import bpy
import bmesh
from mathutils import Vector
import numpy as np
import json
import os

FEATHER_OBJECT_NAMES = [
    "Head_Crown_Three_Soft_Plumes",
    "Tail_Fan_Individual_Feathers",
    "Wing_L_Primaries_Layered_Feathers",
    "Wing_R_Primaries_Layered_Feathers",
    "Wing_L_Secondaries_Layered_Feathers",
    "Wing_R_Secondaries_Layered_Feathers",
    "Wing_L_Coverts_Layered_Feathers",
    "Wing_R_Coverts_Layered_Feathers",
    "Wing_L_Back_Coverts_Layered_Feathers",
    "Wing_R_Back_Coverts_Layered_Feathers",
    "Body_Front_Cream_Contour_Shingle_Layer",
    "Body_Back_Sage_Contour_Shingle_Layer",
    "Head_Front_Fine_Facial_Covert_Layer",
    "Head_Back_Sage_Nape_Covert_Layer",
]

def audit_all_feathers():
    body_center = Vector((0.0, 0.0, 1.25))
    total_cards_audited = 0
    total_reversed_cards = 0
    total_normal_cards = 0
    total_degenerate_faces = 0
    
    object_summaries = {}
    
    for obj_name in FEATHER_OBJECT_NAMES:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Skipping missing: {obj_name}")
            continue
            
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        uv_layer = bm.loops.layers.uv.get("FeatherUV") or bm.loops.layers.uv.active
        
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
            
        reversed_in_obj = []
        normal_in_obj = []
        card_v_spans = []
        correlations = []
        degen_faces_in_obj = 0
        
        for c_idx, card in enumerate(cards):
            card_verts = list({v for face in card for v in face.verts})
            world_cos = [obj.matrix_world @ v.co for v in card_verts]
            dists = [(co - body_center).length for co in world_cos]
            
            min_d_idx = int(np.argmin(dists))
            max_d_idx = int(np.argmax(dists))
            
            root_vert = card_verts[min_d_idx]
            tip_vert = card_verts[max_d_idx]
            
            # Root & tip UV V values
            root_vs = [l[uv_layer].uv.y for face in card for l in face.loops if l.vert == root_vert]
            tip_vs = [l[uv_layer].uv.y for face in card for l in face.loops if l.vert == tip_vert]
            
            root_v = float(np.mean(root_vs)) if root_vs else 0.0
            tip_v = float(np.mean(tip_vs)) if tip_vs else 1.0
            
            all_vs = [l[uv_layer].uv.y for face in card for l in face.loops]
            v_min, v_max = min(all_vs), max(all_vs)
            v_span = v_max - v_min
            card_v_spans.append(v_span)
            
            # Correlation between physical distance to root and UV V
            root_co = root_vert.co
            d_from_root = [(l.vert.co - root_co).length for face in card for l in face.loops]
            v_vals = [l[uv_layer].uv.y for face in card for l in face.loops]
            if len(set(d_from_root)) > 1 and len(set(v_vals)) > 1:
                c = float(np.corrcoef(d_from_root, v_vals)[0, 1])
            else:
                c = 1.0
            correlations.append(c)
            
            # Degenerate UV faces check
            for face in card:
                loop_uvs = [l[uv_layer].uv for l in face.loops]
                # Area of UV polygon using shoelace
                n = len(loop_uvs)
                area = 0.5 * abs(sum(loop_uvs[i].x * loop_uvs[(i+1)%n].y - loop_uvs[(i+1)%n].x * loop_uvs[i].y for i in range(n)))
                if area < 1e-7:
                    degen_faces_in_obj += 1
            
            if tip_v < root_v:
                reversed_in_obj.append(c_idx)
            else:
                normal_in_obj.append(c_idx)
                
        total_cards_audited += len(cards)
        total_reversed_cards += len(reversed_in_obj)
        total_normal_cards += len(normal_in_obj)
        total_degenerate_faces += degen_faces_in_obj
        
        summary = {
            "object_name": obj_name,
            "total_cards": len(cards),
            "normal_cards_count": len(normal_in_obj),
            "reversed_cards_count": len(reversed_in_obj),
            "reversed_card_indices": reversed_in_obj[:20], # show sample
            "degenerate_uv_faces": degen_faces_in_obj,
            "mean_v_span": round(float(np.mean(card_v_spans)), 4),
            "min_v_span": round(float(np.min(card_v_spans)), 4),
            "mean_correlation": round(float(np.mean(correlations)), 4),
            "min_correlation": round(float(np.min(correlations)), 4),
        }
        object_summaries[obj_name] = summary
        print(f"[{obj_name}] Cards: {len(cards)}, Normal: {len(normal_in_obj)}, Reversed: {len(reversed_in_obj)}, DegenFaces: {degen_faces_in_obj}, MeanCorr: {summary['mean_correlation']:.4f}, MeanVspan: {summary['mean_v_span']:.4f}")
        
        bm.free()
        
    full_report = {
        "total_cards_audited": total_cards_audited,
        "total_normal_cards": total_normal_cards,
        "total_reversed_cards": total_reversed_cards,
        "total_degenerate_faces": total_degenerate_faces,
        "object_summaries": object_summaries
    }
    
    out_path = os.path.join(os.path.dirname(bpy.data.filepath), "..", "04_P2_OUTPUT", "REPORTS", "P2_UV_Audit.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nAudit complete. Written to: {out_path}")
    print(f"Total cards audited: {total_cards_audited}")
    print(f"Total reversed cards: {total_reversed_cards}")
    print(f"Total normal cards: {total_normal_cards}")
    print(f"Total degenerate faces: {total_degenerate_faces}")

if __name__ == "__main__":
    audit_all_feathers()
