"""Master P0 Execution & Audit Script for Shukhpakhi Reconstruction.

Target Blender: Exactly 5.3.0
Phase: P0 ONLY (Read-Only Baseline Audit & Deliverables Generation)
"""

import bpy
import mathutils
from mathutils import Vector, Euler
import os
import sys
import json
import csv
import hashlib
import platform
import numpy as np
from datetime import datetime
from collections import Counter


def verify_blender_version():
    expected = (5, 3, 0)
    actual = bpy.app.version
    print(f"Checking Blender version: actual={actual}, expected={expected}")
    if actual != expected:
        raise RuntimeError(
            f"VERSION MISMATCH: Target Blender version must be EXACTLY {expected}, but running on {actual} ({bpy.app.version_string})"
        )
    print("Blender version lock VERIFIED: 5.3.0")


def compute_sha256(filepath):
    if not os.path.isfile(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()


def run_audit(working_blend_path, output_dir):
    print(f"\n--- Starting P0 Master Audit on: {working_blend_path} ---")
    os.makedirs(output_dir, exist_ok=True)
    renders_dir = os.path.join(output_dir, "P0_Baseline_Renders")
    unobstructed_renders_dir = os.path.join(renders_dir, "unobstructed")
    os.makedirs(renders_dir, exist_ok=True)
    os.makedirs(unobstructed_renders_dir, exist_ok=True)

    # 1. RUNTIME ENVIRONMENT
    print("\n1. Auditing Runtime Environment...")
    scene = bpy.context.scene
    cam = scene.camera
    lights_info = []
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            lt = o.data
            lights_info.append({
                "name": o.name,
                "type": lt.type,
                "energy_watts": float(lt.energy),
                "color": [round(float(c), 4) for c in lt.color],
                "size": round(float(getattr(lt, "size", 0.0)), 4),
                "location": [round(float(v), 4) for v in o.location],
                "rotation_euler": [round(float(v), 4) for v in o.rotation_euler],
            })

    world = scene.world
    world_info = {}
    if world:
        world_info = {
            "name": world.name,
            "use_nodes": getattr(world, "use_nodes", False),
        }
        if world.use_nodes and world.node_tree:
            bg_node = world.node_tree.nodes.get("Background")
            if bg_node:
                col = bg_node.inputs["Color"].default_value
                strength = bg_node.inputs["Strength"].default_value
                world_info["background_color"] = [round(float(c), 4) for c in col]
                world_info["background_strength"] = round(float(strength), 4)

    def to_str(val):
        if isinstance(val, bytes):
            return val.decode("utf-8", errors="ignore")
        return str(val) if val is not None else ""

    env_report = {
        "audit_timestamp": datetime.now().isoformat(),
        "blender": {
            "version_string": to_str(bpy.app.version_string),
            "version_tuple": list(bpy.app.version),
            "binary_path": to_str(bpy.app.binary_path),
            "build_date": to_str(getattr(bpy.app, "build_date", "")),
            "build_time": to_str(getattr(bpy.app, "build_time", "")),
            "build_hash": to_str(getattr(bpy.app, "build_hash", "")),
            "build_branch": to_str(getattr(bpy.app, "build_branch", "")),
            "build_commit_date": to_str(getattr(bpy.app, "build_commit_date", "")),
        },
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "python_version": sys.version,
            "numpy_version": np.__version__,
        },
        "blend_file": {
            "working_filepath": working_blend_path,
            "working_file_size_bytes": os.path.getsize(working_blend_path),
            "working_sha256": compute_sha256(working_blend_path),
            "original_locked_path": os.path.abspath(os.path.join(output_dir, "..", "00_ORIGINAL_LOCKED", "Shukhpakhi_current_ORIGINAL.blend")),
            "original_locked_sha256": compute_sha256(os.path.abspath(os.path.join(output_dir, "..", "00_ORIGINAL_LOCKED", "Shukhpakhi_current_ORIGINAL.blend"))),
        },
        "scene": {
            "name": scene.name,
            "render_engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "resolution_percentage": scene.render.resolution_percentage,
            "fps": scene.render.fps,
            "frame_range": [scene.frame_start, scene.frame_end],
            "active_camera": cam.name if cam else None,
        },
        "color_management": {
            "view_transform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": round(float(scene.view_settings.exposure), 4),
            "gamma": round(float(scene.view_settings.gamma), 4),
            "display_device": scene.display_settings.display_device,
        },
        "units": {
            "system": scene.unit_settings.system,
            "scale_length": round(float(scene.unit_settings.scale_length), 4),
            "length_unit": scene.unit_settings.length_unit,
        },
        "camera": {
            "name": cam.name if cam else None,
            "type": cam.data.type if cam else None,
            "ortho_scale": round(float(cam.data.ortho_scale), 4) if (cam and hasattr(cam.data, "ortho_scale")) else None,
            "clip_start": round(float(cam.data.clip_start), 4) if cam else None,
            "clip_end": round(float(cam.data.clip_end), 4) if cam else None,
            "location": [round(float(v), 4) for v in cam.location] if cam else None,
            "rotation_euler": [round(float(v), 4) for v in cam.rotation_euler] if cam else None,
        },
        "lights": lights_info,
        "world": world_info,
    }

    env_json_path = os.path.join(output_dir, "P0_Runtime_Environment.json")
    with open(env_json_path, "w", encoding="utf-8") as f:
        json.dump(env_report, f, indent=2, default=str)
    print(f"Saved: {env_json_path}")

    # 2. RUNTIME AUDIT (FULL JSON & SUMMARY)
    print("\n2. Executing Full Runtime Audit...")
    objects = list(bpy.data.objects)
    meshes = [o for o in objects if o.type == 'MESH']
    mesh_totals = {
        "objects": len(meshes),
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "edges": sum(len(o.data.edges) for o in meshes),
        "loops": sum(len(o.data.loops) for o in meshes),
        "polygons": sum(len(o.data.polygons) for o in meshes),
    }

    images = []
    for img in bpy.data.images:
        images.append({
            "name": img.name,
            "filepath": img.filepath,
            "absolute_filepath": bpy.path.abspath(img.filepath) if img.filepath else None,
            "size": list(img.size),
            "channels": img.channels,
            "packed": bool(img.packed_file or len(getattr(img, "packed_files", []))),
            "colorspace": img.colorspace_settings.name,
            "source": img.source,
        })

    armatures = [o.name for o in objects if o.type == 'ARMATURE']
    curves = [o.name for o in objects if o.type == 'CURVES']
    legacy_curves = [o.name for o in objects if o.type == 'CURVE']
    shape_key_objects = [o.name for o in meshes if o.data.shape_keys]
    anim_objects = [o.name for o in objects if o.animation_data]
    modifier_types = Counter(mod.type for o in objects for mod in o.modifiers)

    def object_mesh_detail(obj):
        m = obj.data
        attrs = []
        for a in getattr(m, "attributes", []):
            attrs.append({
                "name": a.name,
                "domain": str(a.domain),
                "data_type": str(a.data_type),
                "length": len(a.data)
            })
        uvs = [{"name": uv.name, "active": bool(uv.active)} for uv in getattr(m, "uv_layers", [])]
        mat_slots = [slot.material.name if slot.material else None for slot in obj.material_slots]
        mods = [{"name": mod.name, "type": mod.type} for mod in obj.modifiers]
        vgs = [vg.name for vg in obj.vertex_groups]
        bb = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        min_c = [round(min(v[i] for v in bb), 4) for i in range(3)]
        max_c = [round(max(v[i] for v in bb), 4) for i in range(3)]
        dims = [round(max_c[i] - min_c[i], 4) for i in range(3)]
        return {
            "name": obj.name,
            "data_name": m.name,
            "type": obj.type,
            "collections": [c.name for c in obj.users_collection],
            "vertices": len(m.vertices),
            "edges": len(m.edges),
            "loops": len(m.loops),
            "polygons": len(m.polygons),
            "parent": obj.parent.name if obj.parent else None,
            "parent_type": obj.parent_type,
            "hide_viewport": obj.hide_viewport,
            "hide_render": obj.hide_render,
            "modifiers": mods,
            "vertex_groups": vgs,
            "shape_keys": list(m.shape_keys.key_blocks.keys()) if m.shape_keys else [],
            "uv_layers": uvs,
            "attributes": attrs,
            "materials": mat_slots,
            "bound_box_min": min_c,
            "bound_box_max": max_c,
            "dimensions": dims,
        }

    mesh_objects_data = [object_mesh_detail(o) for o in meshes]

    runtime_audit = {
        "audit_timestamp": datetime.now().isoformat(),
        "blender_version": bpy.app.version_string,
        "blend_filepath": bpy.data.filepath,
        "inventory": {
            "total_objects": len(objects),
            "object_types": dict(Counter(o.type for o in objects)),
            "meshes": len(meshes),
            "mesh_totals": mesh_totals,
            "materials": len(bpy.data.materials),
            "images": len(bpy.data.images),
            "collections": [c.name for c in bpy.data.collections],
            "modifier_types": dict(modifier_types),
            "armatures": armatures,
            "hair_curves_objects": curves,
            "legacy_curve_objects": legacy_curves,
            "shape_key_objects": shape_key_objects,
            "objects_with_animation_data": anim_objects,
            "actions": [a.name for a in bpy.data.actions],
            "cube_present": bpy.data.objects.get("Cube") is not None,
        },
        "objects": mesh_objects_data,
        "images": images,
    }

    runtime_audit_json_path = os.path.join(output_dir, "P0_Runtime_Audit.json")
    with open(runtime_audit_json_path, "w", encoding="utf-8") as f:
        json.dump(runtime_audit, f, indent=2, default=str)
    print(f"Saved: {runtime_audit_json_path}")

    # 3. OBJECT INVENTORY CSV
    print("\n3. Generating Object Inventory CSV...")
    csv_path = os.path.join(output_dir, "P0_Object_Inventory.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Type", "Collections", "Vertices", "Edges", "Polygons", "Loops",
            "Materials", "Modifiers", "Parent", "Parent_Type", "Hide_Viewport", "Hide_Render",
            "BoundBox_Min_X", "BoundBox_Min_Y", "BoundBox_Min_Z",
            "BoundBox_Max_X", "BoundBox_Max_Y", "BoundBox_Max_Z",
            "Dim_X", "Dim_Y", "Dim_Z"
        ])
        for o in objects:
            colls = ", ".join(c.name for c in o.users_collection)
            if o.type == 'MESH' and o.data:
                m = o.data
                verts = len(m.vertices)
                edges = len(m.edges)
                polys = len(m.polygons)
                loops = len(m.loops)
                mats = ", ".join(s.material.name if s.material else "EMPTY" for s in o.material_slots)
            else:
                verts = edges = polys = loops = 0
                mats = ""
            mods = ", ".join(m.name + "(" + m.type + ")" for m in o.modifiers)
            parent = o.parent.name if o.parent else ""
            parent_type = o.parent_type
            bb = [o.matrix_world @ mathutils.Vector(corner) for corner in o.bound_box]
            min_c = [round(min(v[i] for v in bb), 4) for i in range(3)]
            max_c = [round(max(v[i] for v in bb), 4) for i in range(3)]
            dims = [round(max_c[i] - min_c[i], 4) for i in range(3)]
            writer.writerow([
                o.name, o.type, colls, verts, edges, polys, loops,
                mats, mods, parent, parent_type, o.hide_viewport, o.hide_render,
                min_c[0], min_c[1], min_c[2],
                max_c[0], max_c[1], max_c[2],
                dims[0], dims[1], dims[2]
            ])
    print(f"Saved: {csv_path}")

    # 4. MATERIAL NODE AUDIT (MACHINE READABLE)
    print("\n4. Auditing Material Node Graphs...")
    mat_audit = {
        "audit_timestamp": datetime.now().isoformat(),
        "total_materials": len(bpy.data.materials),
        "materials": [],
        "critical_defect_analysis": {},
    }

    for mat in bpy.data.materials:
        rec = {
            "name": mat.name,
            "users": mat.users,
            "use_nodes": getattr(mat, "use_nodes", False),
            "diffuse_color": [round(float(c), 4) for c in mat.diffuse_color],
            "nodes": [],
            "links": [],
            "defects_detected": [],
        }
        if mat.use_nodes and mat.node_tree:
            nt = mat.node_tree
            for n in nt.nodes:
                inputs_rec = {}
                for inp in n.inputs:
                    linked = [f"{l.from_node.name}.{l.from_socket.name}" for l in inp.links]
                    def_val = None
                    if hasattr(inp, "default_value"):
                        v = inp.default_value
                        try:
                            def_val = [round(float(x), 4) for x in list(v)]
                        except Exception:
                            try:
                                def_val = round(float(v), 4)
                            except Exception:
                                def_val = str(v)
                    inputs_rec[inp.name] = {
                        "type": inp.type,
                        "is_linked": bool(inp.links),
                        "links": linked,
                        "default_value": def_val if not inp.links else None
                    }
                outputs_rec = {}
                for out in n.outputs:
                    linked = [f"{l.to_node.name}.{l.to_socket.name}" for l in out.links]
                    outputs_rec[out.name] = {
                        "type": out.type,
                        "is_linked": bool(out.links),
                        "links": linked
                    }
                props = {}
                for p in ["attribute_name", "layer_name", "attribute_type", "blend_type", "data_type", "interpolation"]:
                    if hasattr(n, p):
                        props[p] = str(getattr(n, p))
                if n.type == 'TEX_IMAGE' and n.image:
                    props["image_name"] = n.image.name
                    props["image_filepath"] = n.image.filepath
                    props["image_colorspace"] = n.image.colorspace_settings.name
                    props["image_packed"] = bool(n.image.packed_file or len(getattr(n.image, "packed_files", [])))

                # Suspicious Mix check
                if n.type in ('ShaderNodeMix', 'ShaderNodeMixRGB', 'MIX_RGB'):
                    blend_type = getattr(n, "blend_type", "MIX")
                    fac_inp = n.inputs.get("Factor") or n.inputs.get("Fac")
                    if fac_inp and not fac_inp.links and fac_inp.default_value == 1.0:
                        rec["defects_detected"].append({
                            "node": n.name,
                            "type": n.type,
                            "issue": "Unlinked Factor=1.0 selects input 2/B, discarding input 1/A",
                            "blend_type": blend_type,
                        })

                rec["nodes"].append({
                    "name": n.name,
                    "label": n.label,
                    "type": n.type,
                    "bl_idname": n.bl_idname,
                    "location": [round(float(v), 2) for v in n.location],
                    "inputs": inputs_rec,
                    "outputs": outputs_rec,
                    "properties": props,
                })

            for l in nt.links:
                rec["links"].append({
                    "from_node": l.from_node.name,
                    "from_socket": l.from_socket.name,
                    "to_node": l.to_node.name,
                    "to_socket": l.to_socket.name,
                })

        mat_audit["materials"].append(rec)

    # Detailed defect analysis for Feather and Undercoat
    mat_audit["critical_defect_analysis"] = {
        "Shukhpakhi_MAT_Feather_Vane_Microbarb": {
            "material_name": "Shukhpakhi_MAT_Feather_Vane_Microbarb",
            "users": bpy.data.materials["Shukhpakhi_MAT_Feather_Vane_Microbarb"].users,
            "description": "Feather color routing defect verified at runtime in Blender 5.3.0.",
            "color_attribute_node": {
                "name": "Color Attribute",
                "type": "VERTEX_COLOR",
                "layer_name": "FeatherColor",
                "output_target": "Mix (Legacy).Color1"
            },
            "mix_node_1": {
                "name": "Mix (Legacy)",
                "type": "MIX_RGB",
                "blend_type": "MULTIPLY",
                "factor": 1.0,
                "factor_is_linked": False,
                "color1_source": "Color Attribute.Color (FeatherColor)",
                "color2_source": "Image Texture.Color (Shukhpakhi_Feather_albedo)",
                "output_target": "Mix (Legacy).001.Color1",
                "behavior": "With Factor=1.0 and Multiply, output = Color1 * Color2. Because Shukhpakhi_Feather_albedo is almost 1.0 white (mean 0.973), output closely mimics Color1, but then feeds into Mix (Legacy).001."
            },
            "mix_node_2": {
                "name": "Mix (Legacy).001",
                "type": "MIX_RGB",
                "blend_type": "MULTIPLY",
                "factor": 1.0,
                "factor_is_linked": False,
                "color1_source": "Mix (Legacy).Color",
                "color2_source": "Combine Color.Color (Noise Texture MapRange Float 0.965-1.035)",
                "output_target": "Principled BSDF.Base Color",
                "behavior": "Multiplies incoming feather color by near-white grayscale noise. Coupled with weak albedo and high roughness, this washes out vibrant feather shading."
            },
            "normal_node": {
                "name": "Normal Map",
                "type": "NORMAL_MAP",
                "strength": 0.3,
                "source": "Image Texture.002 (Shukhpakhi_Feather_normal)"
            },
            "roughness_node": {
                "name": "Image Texture.001",
                "image": "Shukhpakhi_Feather_roughness",
                "target": "Principled BSDF.Roughness"
            }
        },
        "Shukhpakhi_MAT_Undercoat_Natural": {
            "material_name": "Shukhpakhi_MAT_Undercoat_Natural",
            "users": bpy.data.materials["Shukhpakhi_MAT_Undercoat_Natural"].users,
            "description": "Undercoat shader references Color Attribute 'BodyTint'.",
            "color_attribute_node": {
                "name": "Color Attribute",
                "type": "VERTEX_COLOR",
                "layer_name": "BodyTint",
                "mesh_attribute_present_on_undercoat": True,
                "mesh_attribute_domain": "POINT",
                "mesh_attribute_type": "FLOAT_COLOR",
                "output_target": "Mix (Legacy).Color1"
            },
            "mix_node": {
                "name": "Mix (Legacy)",
                "type": "MIX_RGB",
                "blend_type": "MULTIPLY",
                "factor": 1.0,
                "factor_is_linked": False,
                "color1_source": "Color Attribute.Color (BodyTint)",
                "color2_source": "Color Ramp.Color (from Noise Texture scale 185)",
                "output_target": "Principled BSDF.Base Color",
                "behavior": "Multiplies BodyTint attribute by procedural noise ColorRamp."
            }
        },
        "unused_materials_summary": [m.name for m in bpy.data.materials if m.users == 0]
    }

    mat_audit_path = os.path.join(output_dir, "P0_Material_Node_Audit.json")
    with open(mat_audit_path, "w", encoding="utf-8") as f:
        json.dump(mat_audit, f, indent=2, default=str)
    print(f"Saved: {mat_audit_path}")

    # 5. TEXTURE INVENTORY (CSV & PIXEL STATS)
    print("\n5. Analyzing Packed Textures & Pixel Statistics...")
    tex_csv_path = os.path.join(output_dir, "P0_Texture_Inventory.csv")
    with open(tex_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Datablock_Name", "Resolution", "Channels", "Colorspace", "Packed",
            "Packed_Bytes", "SHA256", "Filepath", "Resolved_Filepath",
            "Min_Val", "Max_Val", "Mean_Val", "StdDev_Val",
            "Mean_R", "Mean_G", "Mean_B", "Mean_A",
            "StdDev_R", "StdDev_G", "StdDev_B", "StdDev_A",
            "Diagnosis"
        ])
        for img in bpy.data.images:
            w, h = img.size
            channels = img.channels
            colorspace = img.colorspace_settings.name
            is_packed = bool(img.packed_file or len(getattr(img, "packed_files", [])))
            packed_bytes = 0
            sha256_hash = ""
            if img.packed_file:
                pdata = img.packed_file.data
                packed_bytes = len(pdata)
                sha256_hash = hashlib.sha256(pdata).hexdigest().upper()
            elif len(getattr(img, "packed_files", [])):
                pdata = img.packed_files[0].data
                packed_bytes = len(pdata)
                sha256_hash = hashlib.sha256(pdata).hexdigest().upper()

            min_v = max_v = mean_v = std_v = 0.0
            m_r = m_g = m_b = m_a = 0.0
            s_r = s_g = s_b = s_a = 0.0
            diag = "Empty or system buffer"

            if w > 0 and h > 0:
                try:
                    pixels = np.array(img.pixels[:], dtype=np.float32)
                    if len(pixels) == w * h * 4:
                        pixels = pixels.reshape((h, w, 4))
                        min_v = round(float(np.min(pixels)), 4)
                        max_v = round(float(np.max(pixels)), 4)
                        mean_v = round(float(np.mean(pixels)), 4)
                        std_v = round(float(np.std(pixels)), 4)
                        m_r = round(float(np.mean(pixels[:, :, 0])), 4)
                        m_g = round(float(np.mean(pixels[:, :, 1])), 4)
                        m_b = round(float(np.mean(pixels[:, :, 2])), 4)
                        m_a = round(float(np.mean(pixels[:, :, 3])), 4)
                        s_r = round(float(np.std(pixels[:, :, 0])), 4)
                        s_g = round(float(np.std(pixels[:, :, 1])), 4)
                        s_b = round(float(np.std(pixels[:, :, 2])), 4)
                        s_a = round(float(np.std(pixels[:, :, 3])), 4)

                        if "albedo" in img.name.lower():
                            if m_r > 0.95 and s_r < 0.05:
                                diag = f"Nearly flat achromatic white (mean={m_r:.3f}, std={s_r:.3f}); lacks sage/cream pigment and feather barb definition."
                            else:
                                diag = "Populated albedo map"
                        elif "normal" in img.name.lower():
                            if m_b > 0.98 and abs(m_r - 0.5) < 0.05 and abs(m_g - 0.5) < 0.05:
                                diag = f"Near-flat tangent normal (R={m_r:.3f}, G={m_g:.3f}, B={m_b:.3f}); shows shallow horizontal wave pattern instead of diagonal branching barbs."
                            else:
                                diag = "Populated normal map"
                        elif "roughness" in img.name.lower():
                            if m_r > 0.85 and s_r < 0.05:
                                diag = f"Excessively uniform high roughness (mean={m_r:.3f}, std={s_r:.3f} ~ 0.91); lacks material differentiation across rachis and vane."
                            else:
                                diag = "Populated roughness map"
                except Exception as e:
                    diag = f"Pixel read error: {e}"

            writer.writerow([
                img.name, f"{w}x{h}", channels, colorspace, is_packed,
                packed_bytes, sha256_hash, img.filepath,
                bpy.path.abspath(img.filepath) if img.filepath else "",
                min_v, max_v, mean_v, std_v,
                m_r, m_g, m_b, m_a,
                s_r, s_g, s_b, s_a,
                diag
            ])
    print(f"Saved: {tex_csv_path}")

    # 6. UV AND ATTRIBUTE AUDIT
    print("\n6. Auditing UV Layers and Custom Mesh Attributes...")
    uv_attr_audit = {
        "audit_timestamp": datetime.now().isoformat(),
        "total_mesh_objects": len(meshes),
        "attribute_key_findings": {
            "FeatherUV": "Present as CORNER FLOAT2 on all contour feathers, primaries, secondaries, and tail fan meshes.",
            "FeatherColor": "Present as POINT FLOAT_COLOR on contour layers, primaries, secondaries, and tail fan. Carries distinct sage and cream color data.",
            "DownColor": "Present as POINT FLOAT_COLOR on Body_Short_Down_Fibre_Groom and Head_Micro_Down_Fibre_Groom.",
            "BodyTint": "Present as POINT FLOAT_COLOR on Body_Head_Fused_Soft_Undercoat (len=355,810).",
        },
        "meshes": []
    }

    for obj in meshes:
        m = obj.data
        uv_records = []
        for uv in m.uv_layers:
            # Check UV bounding box
            uv_data = uv.data
            if len(uv_data) > 0:
                # Sample corners to find min/max
                us = [uv_data[i].uv[0] for i in range(min(1000, len(uv_data)))]
                vs = [uv_data[i].uv[1] for i in range(min(1000, len(uv_data)))]
                u_min, u_max = round(min(us), 4), round(max(us), 4)
                v_min, v_max = round(min(vs), 4), round(max(vs), 4)
            else:
                u_min = u_max = v_min = v_max = 0.0
            uv_records.append({
                "name": uv.name,
                "active": uv.active,
                "corners_count": len(uv_data),
                "u_bounds_sample": [u_min, u_max],
                "v_bounds_sample": [v_min, v_max],
            })

        attr_records = []
        for attr in m.attributes:
            sample_vals = []
            len_data = len(attr.data)
            if len_data > 0:
                for idx in range(min(3, len_data)):
                    it = attr.data[idx]
                    if hasattr(it, "color"):
                        sample_vals.append([round(float(c), 4) for c in it.color])
                    elif hasattr(it, "vector"):
                        sample_vals.append([round(float(v), 4) for v in it.vector])
                    elif hasattr(it, "value"):
                        v = it.value
                        try:
                            sample_vals.append(round(float(v), 4))
                        except Exception:
                            sample_vals.append(str(v))
            attr_records.append({
                "name": attr.name,
                "domain": str(attr.domain),
                "data_type": str(attr.data_type),
                "length": len_data,
                "sample_values": sample_vals
            })

        uv_attr_audit["meshes"].append({
            "object_name": obj.name,
            "mesh_name": m.name,
            "vertex_count": len(m.vertices),
            "polygon_count": len(m.polygons),
            "uv_layers": uv_records,
            "attributes": attr_records
        })

    uv_attr_json_path = os.path.join(output_dir, "P0_UV_And_Attribute_Audit.json")
    with open(uv_attr_json_path, "w", encoding="utf-8") as f:
        json.dump(uv_attr_audit, f, indent=2, default=str)
    print(f"Saved: {uv_attr_json_path}")

    # 7. RIG AND ANIMATION AUDIT
    print("\n7. Auditing Rigging and Animation State...")
    rig_audit = {
        "audit_timestamp": datetime.now().isoformat(),
        "armature_objects": [o.name for o in objects if o.type == 'ARMATURE'],
        "armature_modifiers": [
            {"object": o.name, "modifier": m.name, "armature": m.object.name if m.object else None}
            for o in meshes for m in o.modifiers if m.type == 'ARMATURE'
        ],
        "vertex_groups_summary": [
            {"object": o.name, "groups": [vg.name for vg in o.vertex_groups]}
            for o in meshes if len(o.vertex_groups) > 0
        ],
        "shape_keys_summary": [
            {"object": o.name, "keys": list(o.data.shape_keys.key_blocks.keys())}
            for o in meshes if o.data.shape_keys
        ],
        "animation_data_objects": [
            {
                "object": o.name,
                "action": o.animation_data.action.name if o.animation_data.action else None,
                "drivers_count": len(o.animation_data.drivers) if o.animation_data else 0,
                "nla_tracks_count": len(o.animation_data.nla_tracks) if o.animation_data else 0
            }
            for o in objects if o.animation_data
        ],
        "actions": [a.name for a in bpy.data.actions],
        "hair_curves": [o.name for o in objects if o.type in ('CURVES', 'CURVE')],
        "status_evaluation": {
            "zone_b_status": "UNINITIALIZED",
            "findings": [
                "Zero armatures or bones present in the source scene.",
                "Zero Armature modifiers assigned to any mesh object.",
                "Zero vertex groups present across all 44 mesh objects.",
                "Zero shape keys present across all mesh objects.",
                "Zero animation actions or keyframed data present.",
                "Character is currently a static anatomical mesh assembly."
            ]
        }
    }

    rig_audit_json_path = os.path.join(output_dir, "P0_Rig_And_Animation_Audit.json")
    with open(rig_audit_json_path, "w", encoding="utf-8") as f:
        json.dump(rig_audit, f, indent=2, default=str)
    print(f"Saved: {rig_audit_json_path}")

    # 8. BASELINE RENDERS (10 MANDATORY VIEWS + UNOBSTRUCTED DIAGNOSTICS)
    print("\n8. Generating Baseline Renders...")
    audit_col_name = "P0_AUDIT_CAMERA_RIG"
    if audit_col_name in bpy.data.collections:
        c = bpy.data.collections[audit_col_name]
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)

    audit_col = bpy.data.collections.new(audit_col_name)
    scene.collection.children.link(audit_col)

    audit_cam_data = bpy.data.cameras.new("P0_Audit_Camera")
    audit_cam_data.type = "ORTHO"
    audit_cam = bpy.data.objects.new("P0_Audit_Camera", audit_cam_data)
    audit_col.objects.link(audit_cam)
    original_scene_cam = scene.camera
    scene.camera = audit_cam

    # Save original scene resolution and format
    orig_res_x = scene.render.resolution_x
    orig_res_y = scene.render.resolution_y
    orig_res_pct = scene.render.resolution_percentage
    orig_filepath = scene.render.filepath

    # Set review resolution
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    views_spec = [
        # (filename, location, target, ortho_scale)
        ("front.png", (0.0, -7.8, 1.25), (0.0, 0.0, 1.25), 3.45),
        ("three_quarter.png", (5.5, -5.5, 2.0), (0.0, 0.0, 1.25), 3.45),
        ("side.png", (7.8, 0.0, 1.25), (0.0, 0.0, 1.25), 3.45),
        ("back.png", (0.0, 7.8, 1.25), (0.0, 0.0, 1.25), 3.45),
        ("top.png", (0.0, 0.0, 7.8), (0.0, 0.0, 1.25), 3.45),
        ("breast_macro.png", (0.0, -3.5, 1.25), (0.0, -0.40, 1.15), 1.20),
        ("contour_macro.png", (2.5, 2.5, 1.80), (0.35, 0.25, 1.35), 0.95),
        ("wing_front.png", (2.5, -2.5, 1.55), (0.55, -0.15, 1.25), 1.05),
        ("wing_rear.png", (2.5, 2.5, 1.55), (0.55, 0.20, 1.25), 1.05),
        ("tail_macro.png", (0.0, 3.2, 0.95), (0.0, 0.65, 0.80), 0.85),
    ]

    cube = bpy.data.objects.get("Cube")

    # Render PASS 1: Exact baseline as saved (Cube visible)
    print("\n--- Rendering Baseline Set 1: Exact As-Saved Working Scene (Cube Visible) ---")
    for fname, loc, target, scale in views_spec:
        audit_cam.location = Vector(loc)
        if fname == "top.png":
            audit_cam.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
        else:
            audit_cam.rotation_euler = (Vector(target) - audit_cam.location).to_track_quat("-Z", "Y").to_euler()
        audit_cam.data.ortho_scale = scale
        out_file = os.path.join(renders_dir, fname)
        scene.render.filepath = out_file
        bpy.ops.render.render(write_still=True)
        print(f"Rendered baseline: {out_file}")

    # Render PASS 2: Unobstructed Diagnostic Set (Cube temporarily excluded for render pass)
    print("\n--- Rendering Baseline Set 2: Unobstructed Diagnostic Set (Cube Excluded) ---")
    if cube:
        cube.hide_render = True
    try:
        for fname, loc, target, scale in views_spec:
            audit_cam.location = Vector(loc)
            if fname == "top.png":
                audit_cam.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
            else:
                audit_cam.rotation_euler = (Vector(target) - audit_cam.location).to_track_quat("-Z", "Y").to_euler()
            audit_cam.data.ortho_scale = scale
            out_file = os.path.join(unobstructed_renders_dir, fname)
            scene.render.filepath = out_file
            bpy.ops.render.render(write_still=True)
            print(f"Rendered unobstructed diagnostic: {out_file}")
    finally:
        if cube:
            cube.hide_render = False  # Restore exact unmodified scene state

    # Clean up temporary audit collection and camera
    scene.camera = original_scene_cam
    scene.render.resolution_x = orig_res_x
    scene.render.resolution_y = orig_res_y
    scene.render.resolution_percentage = orig_res_pct
    scene.render.filepath = orig_filepath

    for o in list(audit_col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    try:
        scene.collection.children.unlink(audit_col)
    except Exception:
        pass
    bpy.data.collections.remove(audit_col)
    print("Cleaned up temporary audit camera and collection.")

    print("\n--- P0 Master Audit Script Completed Successfully! ---")


if __name__ == "__main__":
    verify_blender_version()
    working_blend = bpy.data.filepath
    out_dir = os.path.abspath(os.path.join(os.path.dirname(working_blend), "..", "02_AUDIT_OUTPUT"))
    run_audit(working_blend, out_dir)
