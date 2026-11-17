"""Blender mesh/collection helpers. Avoids destructive scene-wide cleanup."""
import bpy
import bmesh
from mathutils import Vector


def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection(name):
    col = get_collection(name)
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    return col


def clear_project_collections():
    for col in list(bpy.data.collections):
        if col.name.startswith("Shukhpakhi_"):
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            if col.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(col)
            bpy.data.collections.remove(col)


def link_object(obj, collection_name):
    col = get_collection(collection_name)
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def smooth_mesh(obj):
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def create_mesh_object(name, verts, faces, collection_name, material=None, smooth=True):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, collection_name)
    if material:
        mesh.materials.append(material)
    if smooth:
        smooth_mesh(obj)
    return obj


def add_uv_sphere_bmesh(bm, center, radii, segments=48, rings=32):
    result = bmesh.ops.create_uvsphere(
        bm, u_segments=segments, v_segments=rings, radius=1.0
    )
    verts = result.get("verts", [])
    center = Vector(center)
    rx, ry, rz = radii
    for vert in verts:
        vert.co = Vector((vert.co.x * rx, vert.co.y * ry, vert.co.z * rz)) + center
    return verts


def create_ellipsoid(name, location, radii, collection_name, material,
                     segments=40, rings=28, subsurf=1):
    bm = bmesh.new()
    add_uv_sphere_bmesh(bm, (0, 0, 0), radii, segments, rings)
    bm.normal_update()
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    link_object(obj, collection_name)
    mesh.materials.append(material)
    smooth_mesh(obj)
    if subsurf:
        mod = obj.modifiers.new("Soft_Surface_Subdivision", "SUBSURF")
        mod.levels = subsurf
        mod.render_levels = subsurf
    return obj


def add_bevel_and_solidify(obj, thickness=0.003, bevel=0.0015):
    solid = obj.modifiers.new("Feather_Thickness", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = -0.25
    bev = obj.modifiers.new("Feather_Edge_Soften", "BEVEL")
    bev.width = bevel
    bev.segments = 2
    return obj


def apply_object_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def add_tapered_limb(bm, start, end, r_start, r_end, segments=16):
    start, end = Vector(start), Vector(end)
    delta = end - start
    length = delta.length
    if length < 1e-6:
        return
    quat = delta.normalized().to_track_quat("Z", "Y")
    temp = bmesh.new()
    bmesh.ops.create_cone(temp, cap_ends=True, cap_tris=False,
                          segments=segments, radius1=r_start,
                          radius2=r_end, depth=length)
    mapping = {}
    for v in temp.verts:
        mapping[v] = bm.verts.new((quat @ v.co) + (start + end) * 0.5)
    for face in temp.faces:
        try:
            bm.faces.new([mapping[v] for v in face.verts])
        except ValueError:
            pass
    temp.free()


def add_uv_sphere_to_bmesh(bm, center, radii, segments=24, rings=16):
    add_uv_sphere_bmesh(bm, center, radii, segments, rings)
