"""In-depth inspection of feather cards: islands, root-to-tip geometric orientation, and UV correlation."""

import bpy
import bmesh
import numpy as np
import json
import os

def analyze_feather_mesh(obj):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    uv_layer = bm.loops.layers.uv.get("FeatherUV")
    if not uv_layer:
        uv_layer = bm.loops.layers.uv.active

    # Find connected components (individual feather cards)
    visited = set()
    components = []
    
    for f in bm.faces:
        if f.index in visited:
            continue
        comp_faces = []
        queue = [f]
        visited.add(f.index)
        while queue:
            curr = queue.pop()
            comp_faces.append(curr)
            for edge in curr.edges:
                for linked in edge.link_faces:
                    if linked.index not in visited:
                        visited.add(linked.index)
                        queue.append(linked)
        components.append(comp_faces)
        
    num_cards = len(components)
    
    # Analyze a representative sample of cards (or all if <= 50)
    card_samples = components if num_cards <= 50 else [components[i] for i in np.linspace(0, num_cards - 1, 20, dtype=int)]
    
    card_metrics = []
    for idx, card in enumerate(card_samples):
        verts = list({v for face in card for v in face.verts})
        co_3d = np.array([v.co for v in verts])
        
        # In UV space:
        uvs = np.array([[l[uv_layer].uv.x, l[uv_layer].uv.y] for face in card for l in face.loops])
        u_min, u_max = float(uvs[:, 0].min()), float(uvs[:, 0].max())
        v_min, v_max = float(uvs[:, 1].min()), float(uvs[:, 1].max())
        
        # Check geometric principal axis
        # Center of geometry
        center = co_3d.mean(axis=0)
        cov = np.cov(co_3d - center, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        major_axis = eigenvectors[:, -1] # longest 3D direction (length of feather)
        
        # Project 3D verts along major axis
        t_proj = np.dot(co_3d - center, major_axis)
        v_loop_vals = [l[uv_layer].uv.y for face in card for l in face.loops]
        t_loop_vals = [np.dot(np.array(l.vert.co) - center, major_axis) for face in card for l in face.loops]
        
        # Correlation between 3D longitudinal axis and UV V
        corr = float(np.corrcoef(t_loop_vals, v_loop_vals)[0, 1])
        
        # Check root vs tip based on distance to object center or bounding box
        card_metrics.append({
            "card_index": idx,
            "face_count": len(card),
            "vert_count": len(verts),
            "u_range": [round(u_min, 4), round(u_max, 4)],
            "v_range": [round(v_min, 4), round(v_max, 4)],
            "v_span": round(v_max - v_min, 4),
            "correlation_t_v": round(corr, 4),
            "abs_corr": round(abs(corr), 4)
        })
        
    bm.free()
    
    avg_v_span = np.mean([m["v_span"] for m in card_metrics])
    avg_corr = np.mean([m["abs_corr"] for m in card_metrics])
    
    return {
        "object_name": obj.name,
        "total_cards": num_cards,
        "sample_count": len(card_metrics),
        "avg_v_span": round(float(avg_v_span), 4),
        "avg_abs_correlation": round(float(avg_corr), 4),
        "card_samples": card_metrics[:5] # show first 5
    }

def run_audit():
    feather_objects = [
        "Head_Crown_Three_Soft_Plumes",
        "Tail_Fan_Individual_Feathers",
        "Wing_L_Primaries_Layered_Feathers",
        "Wing_L_Secondaries_Layered_Feathers",
        "Wing_L_Coverts_Layered_Feathers",
        "Wing_L_Back_Coverts_Layered_Feathers",
        "Body_Front_Cream_Contour_Shingle_Layer",
        "Body_Back_Sage_Contour_Shingle_Layer",
        "Head_Front_Fine_Facial_Covert_Layer",
        "Head_Back_Sage_Nape_Covert_Layer",
    ]
    
    results = {}
    for name in feather_objects:
        obj = bpy.data.objects.get(name)
        if obj:
            print(f"Auditing {name}...")
            res = analyze_feather_mesh(obj)
            results[name] = res
            print(f"  Total cards: {res['total_cards']}, Avg V span: {res['avg_v_span']}, Avg Correlation: {res['avg_abs_correlation']}")
            for s in res['card_samples']:
                print(f"    Card {s['card_index']}: U={s['u_range']} V={s['v_range']} Span={s['v_span']} Corr={s['correlation_t_v']}")

    out_file = os.path.join(os.path.dirname(bpy.data.filepath), "..", "04_P2_OUTPUT", "REPORTS", "feather_cards_audit.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Audit completed: {out_file}")

if __name__ == "__main__":
    run_audit()
