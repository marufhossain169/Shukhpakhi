"""Named static expression presets. Blink is an actual mesh shape key; this is not an animation engine."""
import bpy

PRESETS = {"Normal", "Happy", "Excited", "Thinking", "Sleepy"}


def build_controller():
    old = bpy.data.objects.get("Shukhpakhi_Expression_Controller")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    controller = bpy.data.objects.new("Shukhpakhi_Expression_Controller", None)
    col = bpy.data.collections.get("Shukhpakhi_Rig")
    if col is None:
        col = bpy.data.collections.new("Shukhpakhi_Rig")
        bpy.context.scene.collection.children.link(col)
    col.objects.link(controller)
    controller.empty_display_type = "CIRCLE"
    controller.empty_display_size = 0.12
    controller.hide_render = True
    controller["available_presets"] = "Normal, Happy, Excited, Thinking, Sleepy"
    controller["note"] = "Run expressions.set_expression('Happy') from Blender Python to apply a static preset."
    return controller


def set_expression(name):
    if name not in PRESETS:
        raise ValueError(f"Unknown expression {name!r}; choose one of {sorted(PRESETS)}")
    blink_by_preset = {"Normal": 0.0, "Happy": 0.96, "Excited": 0.0,
                       "Thinking": 0.12, "Sleepy": 0.64}
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.data.shape_keys:
            key = obj.data.shape_keys.key_blocks.get("Blink")
            if key:
                key.value = blink_by_preset[name]
        if obj.name.startswith("Eye_") and obj.name.endswith("Glossy_Main"):
            factor = 1.045 if name == "Excited" else 1.0
            obj.scale = (factor, factor, factor)
        if obj.name.startswith("Eye_") and obj.name.endswith("Closed_Lid_Line"):
            show_line = name in ("Happy", "Sleepy")
            obj.hide_render = not show_line
            obj.hide_viewport = not show_line
        if obj.name.startswith("Eye_") and ("Catchlight" in obj.name):
            hide_glints = name in ("Happy", "Sleepy")
            obj.hide_render = hide_glints
            obj.hide_viewport = hide_glints
    controller = bpy.data.objects.get("Shukhpakhi_Expression_Controller")
    if controller:
        controller["current_expression"] = name
    return name
