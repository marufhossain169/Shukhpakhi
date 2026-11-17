"""Blender 5.3 review renders: 5 neutral views + Morning/Evening/Night front and 3/4."""
import bpy, os, json, sys
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else bpy.path.abspath("//")
if not os.path.isdir(os.path.join(ROOT, "shukhpakhi")):
    try:
        ROOT = os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath))
    except Exception:
        pass
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from shukhpakhi import materials, perch, expressions

OUT = os.path.join(ROOT, "Shukhpakhi_Review")
os.makedirs(OUT, exist_ok=True)

if bpy.app.version < (5, 3, 0):
    raise RuntimeError("render_review.py targets Blender 5.3+")

# Remove only the previous review-stage collection.
COL_NAME = "Shukhpakhi_ReviewRig"
old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    try:
        bpy.context.scene.collection.children.unlink(old)
    except Exception:
        pass
    bpy.data.collections.remove(old)
rig = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(rig)


def link_rig(obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    rig.objects.link(obj)
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 96
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"
# Keep the look conservative to avoid washing out the pale cream body.
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0

world = scene.world or bpy.data.worlds.new("Shukhpakhi_ReviewWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42

# Neutral floor for the turnaround.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0.040))
floor = link_rig(bpy.context.object)
floor.name = "Review_Neutral_Floor"
floor_mat = bpy.data.materials.get("Shukhpakhi_Review_Floor") or bpy.data.materials.new("Shukhpakhi_Review_Floor")
floor_mat.diffuse_color = (0.22, 0.25, 0.20, 1)
floor_mat.use_nodes = True
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.22, 0.25, 0.20, 1)
floor_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.92
floor.data.materials.clear(); floor.data.materials.append(floor_mat)


def area_light(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    rig.objects.link(ob)
    ob.location = location
    aim(ob, (0, 0, 1.35))
    return ob

key = area_light("Review_Key", (3.2, -4.5, 5.3), 480, 4.0, (1.0, 0.91, 0.78))
fill = area_light("Review_Fill", (-3.8, -3.0, 3.5), 235, 4.5, (0.83, 0.91, 1.0))
rim = area_light("Review_Rim", (0.3, 3.5, 4.5), 420, 3.0, (1.0, 0.93, 0.78))

cam_data = bpy.data.cameras.new("Shukhpakhi_ReviewCamera")
cam = bpy.data.objects.new("Shukhpakhi_ReviewCamera", cam_data)
rig.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = 3.25
scene.camera = cam

target = (0.0, 0.0, 1.32)
views = [
    ("01_front", (0, -8, 1.36)),
    ("02_three_quarter", (5.6, -6.7, 1.78)),
    ("03_side", (8, 0, 1.34)),
    ("04_back", (0, 8, 1.34)),
    ("05_top", (0, -0.15, 8.4)),
]


def set_mood(name):
    if name == "Morning":
        key.data.energy, key.data.color = 620, (1.0, 0.82, 0.58)
        fill.data.energy, fill.data.color = 255, (0.84, 0.94, 0.82)
        rim.data.energy, rim.data.color = 420, (1.0, 0.90, 0.68)
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.42, 0.48, 0.34, 1)
    elif name == "Evening":
        key.data.energy, key.data.color = 530, (1.0, 0.62, 0.43)
        fill.data.energy, fill.data.color = 210, (0.78, 0.72, 0.88)
        rim.data.energy, rim.data.color = 380, (1.0, 0.73, 0.52)
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.30, 0.25, 0.34, 1)
    else:
        key.data.energy, key.data.color = 300, (0.55, 0.68, 1.0)
        fill.data.energy, fill.data.color = 155, (0.70, 0.79, 1.0)
        rim.data.energy, rim.data.color = 310, (0.78, 0.84, 1.0)
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.085, 0.15, 1)

# Five neutral turnaround images.
set_mood("Morning")
for name, pos in views:
    cam.location = pos
    aim(cam, target)
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)

# Mood samples are staged on a small curved perch to match the guide's hero composition.
floor.hide_render = True
perch.add_perch_branch()

# Mood samples: front and 3/4 for each canonical lighting setup.
for mood in ("Morning", "Evening", "Night"):
    set_mood(mood)
    for name, pos in views[:2]:
        cam.location = pos
        aim(cam, target)
        scene.render.filepath = os.path.join(OUT, f"{mood.lower()}_{name}.png")
        bpy.ops.render.render(write_still=True)

# Expression samples are intentionally rendered so incomplete expressions remain visible to review.
set_mood("Morning")
cam.location = views[0][1]
aim(cam, target)
for expression in ("Normal", "Happy", "Excited", "Thinking", "Sleepy"):
    expressions.set_expression(expression)
    scene.render.filepath = os.path.join(OUT, f"expression_{expression.lower()}.png")
    bpy.ops.render.render(write_still=True)
expressions.set_expression("Normal")

# Structural report includes evaluated mesh counts (not only pre-modifier source meshes).
report = {
    "project": "Shukhpakhi Guide Reconstruction",
    "blender_version": bpy.app.version_string,
    "status": "RENDERED; visual match still requires human comparison against the supplied guide",
    "render_files": [f for f in os.listdir(OUT) if f.lower().endswith(".png")],
    "collections": [], "objects": [],
    "totals": {"source_vertices": 0, "source_faces": 0, "evaluated_vertices": 0,
                "evaluated_faces": 0, "evaluated_triangles_estimate": 0},
    "shape_keys": [],
    "known_gaps": [
        "Rigid-part posing rig only; unified torso/head is not weight-skinned for deformation.",
        "Expression presets are static; Blink is a shape key, but eye gaze, beak speech and full facial animation are not built.",
        "No automated perceptual image similarity score is produced; reference comparison remains a visual QA step.",
        "No mobile GLB optimization or Android runtime test has been performed."
    ]
}
depsgraph = bpy.context.evaluated_depsgraph_get()
for col in bpy.data.collections:
    if col.name.startswith("Shukhpakhi_") and col.name != COL_NAME:
        cdata = {"name": col.name, "objects": []}
        for obj in col.objects:
            cdata["objects"].append(obj.name)
            entry = {"name": obj.name, "type": obj.type,
                     "dimensions": [round(float(v), 5) for v in obj.dimensions],
                     "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers]}
            if obj.type == "MESH":
                entry["source_vertices"] = len(obj.data.vertices)
                entry["source_faces"] = len(obj.data.polygons)
                report["totals"]["source_vertices"] += entry["source_vertices"]
                report["totals"]["source_faces"] += entry["source_faces"]
                evaluated = obj.evaluated_get(depsgraph)
                eval_mesh = evaluated.to_mesh()
                try:
                    vcount, fcount = len(eval_mesh.vertices), len(eval_mesh.polygons)
                    tri_count = sum(max(0, len(p.vertices) - 2) for p in eval_mesh.polygons)
                    entry["evaluated_vertices"] = vcount
                    entry["evaluated_faces"] = fcount
                    entry["evaluated_triangles_estimate"] = tri_count
                    report["totals"]["evaluated_vertices"] += vcount
                    report["totals"]["evaluated_faces"] += fcount
                    report["totals"]["evaluated_triangles_estimate"] += tri_count
                finally:
                    evaluated.to_mesh_clear()
                if obj.data.shape_keys:
                    keys = [k.name for k in obj.data.shape_keys.key_blocks]
                    report["shape_keys"].append({"object": obj.name, "keys": keys})
                    entry["shape_keys"] = keys
            cdata["objects"].append(entry)
        report["collections"].append(cdata)
with open(os.path.join(OUT, "model_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("Shukhpakhi review renders and report complete:", OUT)
