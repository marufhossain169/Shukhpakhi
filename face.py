"""Expressive glossy eyes, shape-key eyelids, cheeks and rounded two-part beak."""
import math
import bpy
import bmesh
from . import config, utils, materials

COLLECTION = config.COLLECTION_PREFIX + "Face"


def _add_bmesh_ellipsoid(name, loc, radii, material, subsurf=1, rotation=(0, 0, 0)):
    bm = bmesh.new()
    utils.add_uv_sphere_bmesh(bm, (0, 0, 0), radii, 40, 28)
    bm.normal_update()
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rotation
    utils.link_object(obj, COLLECTION)
    mesh.materials.append(material)
    utils.smooth_mesh(obj)
    if subsurf:
        mod = obj.modifiers.new("Polished_Round_Form", "SUBSURF")
        mod.levels = subsurf
        mod.render_levels = subsurf
    return obj


def _make_blink_lid(name, loc, eye_radii, eye_rotation, material):
    rx, ry, rz = eye_radii
    rows, cols = 9, 17
    closed = []
    for r in range(rows):
        theta = math.pi * r / (rows - 1)
        for c in range(cols):
            phi = -math.pi / 2 + math.pi * c / (cols - 1)
            x = rx * math.sin(theta) * math.sin(phi) * 1.015
            z = rz * math.cos(theta) * 1.015
            inside = max(0.0, 1.0 - (x / (rx * 1.08)) ** 2 - (z / (rz * 1.08)) ** 2)
            y = -ry * math.sqrt(inside) - 0.010
            closed.append((x, y, z))
    faces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * cols + c
            faces.append((a, a + cols, a + cols + 1, a + 1))
    obj = utils.create_mesh_object(name, closed, faces, COLLECTION, material, smooth=True)
    obj.location = loc
    obj.rotation_euler = eye_rotation
    basis = obj.shape_key_add(name="Basis")
    blink = obj.shape_key_add(name="Blink")
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            x, y, z = closed[idx]
            # Open state collapses the lid into a narrow upper rim; Blink=1 restores the full cover.
            blink.data[idx].co = (x, y, z)
            open_z = rz * (0.995 - 0.018 * (c / (cols - 1) - 0.5) ** 2)
            basis.data[idx].co = (x * 0.035, y, open_z)
    blink.value = 0.0
    obj["control_hint"] = "Set shape key 'Blink' to 1.0 to close the eye."
    return obj



def _make_closed_lid_line(name, side_sign, loc, material):
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = 0.0045
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    count = 9
    spline.points.add(count - 1)
    for i, point in enumerate(spline.points):
        t = -1.0 + 2.0 * i / (count - 1)
        x = loc[0] + side_sign * 0.112 * t
        y = loc[1] - 0.108
        z = loc[2] - 0.018 + 0.027 * (abs(t) ** 1.7)
        point.co = (x, y, z, 1.0)
    obj = bpy.data.objects.new(name, curve)
    utils.link_object(obj, COLLECTION)
    curve.materials.append(material)
    obj.hide_render = True
    obj.hide_viewport = True
    obj["visibility_hint"] = "Enabled by the Happy/Sleepy static expression preset."
    return obj

def _make_beak_half(name, loc, radii, upper, material):
    bm = bmesh.new()
    result = bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=24, radius=1.0)
    rx, ry, rz = radii
    for v in result["verts"]:
        x, y, z = v.co
        if upper and z < 0:
            z *= 0.22
        elif not upper and z > 0:
            z *= 0.22
        forward = max(0.0, -y)
        taper = 1.0 - (forward ** 1.35) * 0.46
        v.co = (x * rx * taper, y * ry, z * rz * (1.0 - forward * 0.24))
    bm.normal_update()
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    utils.link_object(obj, COLLECTION)
    mesh.materials.append(material)
    utils.smooth_mesh(obj)
    mod = obj.modifiers.new("Beak_Soften", "SUBSURF")
    mod.levels = 1
    mod.render_levels = 1
    return obj


def build():
    utils.clear_collection(COLLECTION)
    mats = materials.create_all()
    made = []
    for side, sign in (("L", -1), ("R", 1)):
        loc = (sign * config.EYE_X, config.EYE_Y, config.EYE_Z)
        rot = (0.035, 0.0, -sign * 0.16)
        # Soft warm iris rim sits behind the glossy dark eye and remains narrow.
        rim_loc = (loc[0], loc[1] + 0.020, loc[2])  # slightly behind the dark eye, so it reads as a ring
        rim = _add_bmesh_ellipsoid(f"Eye_{side}_Warm_Rim", rim_loc,
                                   tuple(v * 1.10 for v in config.EYE_RADII), mats["eye_rim"], 1, rot)
        eye = _add_bmesh_ellipsoid(f"Eye_{side}_Glossy_Main", loc,
                                   config.EYE_RADII, mats["eye_dark"], 1, rot)
        made.extend((rim, eye))
        # Large and small catchlights placed on the camera-facing (-Y) surface.
        made.append(_add_bmesh_ellipsoid(
            f"Eye_{side}_Catchlight_Large",
            (loc[0] - 0.041, loc[1] - 0.091, loc[2] + 0.054),
            (0.041, 0.016, 0.049), mats["white"], 0, rot))
        made.append(_add_bmesh_ellipsoid(
            f"Eye_{side}_Catchlight_Small",
            (loc[0] + 0.043, loc[1] - 0.091, loc[2] - 0.049),
            (0.017, 0.010, 0.019), mats["white"], 0, rot))
        made.append(_make_blink_lid(f"Eye_{side}_Eyelid_BlinkShape", loc,
                                    config.EYE_RADII, rot, mats["eyelid"]))
        made.append(_make_closed_lid_line(f"Eye_{side}_Closed_Lid_Line", sign, loc, mats["eye_rim"]))
        made.append(_add_bmesh_ellipsoid(
            f"Cheek_{side}_Soft_Blush",
            (sign * config.CHEEK_X, config.CHEEK_Y, config.CHEEK_Z),
            config.CHEEK_RADII, mats["blush"], 1, (0, 0, -sign * 0.25)))

    made.append(_make_beak_half("Beak_Upper", config.BEAK_CENTER, config.BEAK_UPPER,
                                True, mats["orange"]))
    lower_loc = (config.BEAK_CENTER[0], config.BEAK_CENTER[1] + 0.018,
                 config.BEAK_CENTER[2] - 0.035)
    made.append(_make_beak_half("Beak_Lower", lower_loc, config.BEAK_LOWER,
                                False, mats["orange"]))
    return made

