"""Optional hero-render perch. This is stage geometry, not part of the bird mesh."""
import bpy
from mathutils import Vector
from . import materials

COLLECTION = "Shukhpakhi_Stage"


def add_perch_branch():
    old = bpy.data.collections.get(COLLECTION)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
    col = old or bpy.data.collections.new(COLLECTION)
    if old is None:
        bpy.context.scene.collection.children.link(col)
    mats = materials.create_all()
    curve = bpy.data.curves.new("Perch_Branch_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = 0.064
    curve.bevel_resolution = 5
    spline = curve.splines.new("BEZIER")
    coords = [(-1.35, 0.12, -0.13), (-0.78, 0.045, -0.055), (0.0, 0.0, -0.005),
              (0.72, -0.04, 0.055), (1.35, -0.09, 0.13)]
    spline.bezier_points.add(len(coords) - 1)
    for point, co in zip(spline.bezier_points, coords):
        point.co = Vector(co)
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    branch = bpy.data.objects.new("Stage_Perch_Branch", curve)
    col.objects.link(branch)
    curve.materials.append(mats["wood"])
    branch["stage_only"] = True
    return branch
