"""Run from Blender 5.3 Text Editor. Open this file from the extracted project folder."""
import bpy
import os
import sys
import importlib

if bpy.app.version < (5, 3, 0):
    raise RuntimeError(f"This project targets Blender 5.3+. Current: {bpy.app.version_string}")

PROJECT_DIR = ""
try:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    pass
if not os.path.isdir(os.path.join(PROJECT_DIR, "shukhpakhi")):
    try:
        active_text = bpy.context.space_data.text
        if active_text and active_text.filepath:
            PROJECT_DIR = os.path.dirname(bpy.path.abspath(active_text.filepath))
    except Exception:
        pass
if not os.path.isdir(os.path.join(PROJECT_DIR, "shukhpakhi")):
    for text_block in bpy.data.texts:
        if text_block.filepath and os.path.basename(text_block.filepath) == "build_shukhpakhi.py":
            PROJECT_DIR = os.path.dirname(bpy.path.abspath(text_block.filepath))
            break

if not os.path.isdir(os.path.join(PROJECT_DIR, "shukhpakhi")):
    raise RuntimeError(
        "Cannot find the 'shukhpakhi' folder. Extract the complete project ZIP, "
        "then open build_shukhpakhi.py from that folder in Blender's Text Editor."
    )

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import shukhpakhi.config as config
import shukhpakhi.utils as utils
import shukhpakhi.materials as materials
import shukhpakhi.feather_engine as feather_engine
import shukhpakhi.body as body
import shukhpakhi.face as face
import shukhpakhi.wings as wings
import shukhpakhi.feet as feet
import shukhpakhi.tuft as tuft
import shukhpakhi.rig as rig
import shukhpakhi.expressions as expressions
import shukhpakhi.assemble as assemble

# Reload in dependency order so repeated Script runs do not mix old module versions.
for module in (config, utils, materials, feather_engine, body, face, wings, feet,
               tuft, rig, expressions, assemble):
    importlib.reload(module)

assemble.build_all()
