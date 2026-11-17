"""Run inside Blender after build_shukhpakhi.py; writes structural evidence JSON."""
import bpy, os, json

root = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else bpy.path.abspath("//")
if not os.path.isdir(os.path.join(root, "shukhpakhi")):
    try:
        root = os.path.dirname(bpy.path.abspath(bpy.context.space_data.text.filepath))
    except Exception:
        pass
out_dir = os.path.join(root, "Shukhpakhi_Review")
os.makedirs(out_dir, exist_ok=True)
report = {
    "project": "Shukhpakhi Guide Reconstruction",
    "blender_version": bpy.app.version_string,
    "status": "STRUCTURAL_INSPECTION_ONLY; visual guide match not automatically certified",
    "collections": [], "objects": [], "totals": {"vertices": 0, "faces": 0, "triangles_estimate": 0},
    "shape_keys": [], "known_limitations": [
        "No source .blend was included in the supplied ZIP, so the prior model's evaluated topology could not be inspected.",
        "This script creates a fresh model; it does not prove pixel-perfect similarity to the design-guide image.",
        "The armature is a rigid-part posing rig. The unified torso/head is not yet skin-weight deformed.",
        "Five expression labels are static presets; only Blink is a genuine shape key. Full facial animation is not complete.",
        "Rendered visual quality must be reviewed in Blender 5.3; no Blender executable was available in the authoring environment."
    ]
}
for col in bpy.data.collections:
    if col.name.startswith("Shukhpakhi_"):
        cdata = {"name": col.name, "objects": []}
        for obj in col.objects:
            cdata["objects"].append(obj.name)
            entry = {"name": obj.name, "type": obj.type,
                     "dimensions": [round(float(v), 5) for v in obj.dimensions],
                     "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers]}
            if obj.type == "MESH":
                entry["vertices"] = len(obj.data.vertices)
                entry["faces"] = len(obj.data.polygons)
                entry["triangles_estimate"] = sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)
                report["totals"]["vertices"] += entry["vertices"]
                report["totals"]["faces"] += entry["faces"]
                report["totals"]["triangles_estimate"] += entry["triangles_estimate"]
                if obj.data.shape_keys:
                    keys = [k.name for k in obj.data.shape_keys.key_blocks]
                    report["shape_keys"].append({"object": obj.name, "keys": keys})
                    entry["shape_keys"] = keys
            cdata["objects"].append(entry)
        report["collections"].append(cdata)
with open(os.path.join(out_dir, "structural_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("Structural report written:", os.path.join(out_dir, "structural_report.json"))
