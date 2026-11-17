"""Inspect attachment points and physical root vs tip evidence for feather cards."""

import bpy
import bmesh
from mathutils import Vector
import numpy as np

def inspect_object(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object {obj_name} not found")
        return
        
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    uv_layer = bm.loops.layers.uv.get("FeatherUV") or bm.loops.layers.uv.active
    
    # Partition into cards
    visited = set()
    components = []
    for f in bm.faces:
        if f.index in visited:
            continue
        comp = []
        q = [f]
        visited.add(f.index)
        while q:
            curr = q.pop()
            comp.append(curr)
            for e in curr.edges:
                for lf in e.link_faces:
                    if lf.index not in visited:
                        visited.add(lf.index)
                        q.append(lf)
        components.append(comp)
        
    print(f"\n=======================================================")
    print(f"OBJECT: {obj_name} (Total cards: {len(components)})")
    print(f"=======================================================")
    
    # Inspect first 3 cards in detail
    body_center = Vector((0.0, 0.0, 1.25)) # Bird body center in world coordinates
    
    for c_idx in range(min(5, len(components))):
        card = components[c_idx]
        card_verts = list({v for face in card for v in face.verts})
        
        # World positions
        world_cos = [obj.matrix_world @ v.co for v in card_verts]
        # Distances to body center
        dists_to_body = [(co - body_center).length for co in world_cos]
        
        min_d_idx = int(np.argmin(dists_to_body))
        max_d_idx = int(np.argmax(dists_to_body))
        
        root_vert = card_verts[min_d_idx] # Closest to body center = ROOT
        tip_vert = card_verts[max_d_idx]  # Farthest from body center = TIP
        
        # Find UV values associated with root and tip
        root_uvs = [l[uv_layer].uv for face in card for l in face.loops if l.vert == root_vert]
        tip_uvs = [l[uv_layer].uv for face in card for l in face.loops if l.vert == tip_vert]
        
        root_v = np.mean([uv.y for uv in root_uvs]) if root_uvs else None
        tip_v = np.mean([uv.y for uv in tip_uvs]) if tip_uvs else None
        
        # All V values
        all_vs = [l[uv_layer].uv.y for face in card for l in face.loops]
        v_min, v_max = min(all_vs), max(all_vs)
        
        is_reversed = (tip_v < root_v) if (tip_v is not None and root_v is not None) else None
        
        print(f"Card {c_idx}: {len(card_verts)} verts, {len(card)} faces")
        print(f"  Root (dist to body {dists_to_body[min_d_idx]:.3f}m) -> UV V: {root_v:.4f}")
        print(f"  Tip  (dist to body {dists_to_body[max_d_idx]:.3f}m) -> UV V: {tip_v:.4f}")
        print(f"  V Range: [{v_min:.4f}, {v_max:.4f}], V Span: {v_max - v_min:.4f}")
        print(f"  Orientation: {'REVERSED (V_root > V_tip)' if is_reversed else 'NORMAL (V_root < V_tip)'}")

    bm.free()

if __name__ == "__main__":
    for name in [
        "Head_Crown_Three_Soft_Plumes",
        "Tail_Fan_Individual_Feathers",
        "Wing_L_Primaries_Layered_Feathers",
        "Wing_L_Coverts_Layered_Feathers",
        "Body_Back_Sage_Contour_Shingle_Layer",
        "Body_Front_Cream_Contour_Shingle_Layer"
    ]:
        inspect_object(name)
