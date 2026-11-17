# Shukhpakhi — Blender 5.3 Guide Reconstruction

This package is a **fresh rebuild of the supplied Python source**, preserving the exact five guide swatches and the bird's visual identity: round cream body, sage-green wings/back, glossy expressive eyes, orange beak/feet and three-part crown tuft.

> **Honesty note:** The supplied ZIP contained 13 Python/README files but no `.blend` project, no rendered PNGs and no `model_report.json`. The prior model's evaluated mesh and its rendered appearance therefore could not be directly inspected. This package builds a revised model from the Python source and the supplied guide image; it is not yet certified as a pixel-perfect match.

## Blender version

Target: **Blender 5.3+**. The authoring environment used for this source revision did not have a Blender executable, so Python syntax and package structure can be checked here, but the `.blend` generation, rendered output and Blender 5.3 API runtime still need to be executed in Blender 5.3.

## Build

1. Extract this entire folder; keep `build_shukhpakhi.py` beside the `shukhpakhi/` folder.
2. Open Blender 5.3 and switch to **Scripting**.
3. In the Text Editor, open this folder's `build_shukhpakhi.py` and click **Run Script**.
4. Save the generated scene as `Shukhpakhi_Master.blend`.
5. Run `render_review.py` to create five turnaround images, three lighting moods and five expression samples inside `Shukhpakhi_Review/`.
6. Run `validate_project.py` if you only need a structural report.

## What changed from the supplied source

- `body.py`: torso and head are now overlapping volumes fused by a Voxel Remesh modifier, followed by smoothing. The old separate belly cushion and separate green cape ellipsoids are removed.
- `feather_engine.py`: adds reusable, actual feather surface meshes (root, tapered vane, camber and thickness). This replaces the former wing-only sinusoidal UV-sphere ripples.
- `body.py`: adds subtle front down-feather overlays, sage back feather overlays and a five-feather tail fan.
- `wings.py`: keeps a smooth wing base but adds distinct covert, secondary and primary feather layers per wing.
- `materials.py`: retains the guide's exact palette and replaces exaggerated shiny/plastic response with rough, soft-sheen feather materials and subtle micro-noise. Bump is explicitly supporting detail, not the feather system.
- `face.py`: replaces static eyelid shells with a real `Blink` shape key on each eyelid surface. Five named expression presets are available in `expressions.py`, but they are static pose helpers, not a complete facial animation system.
- `feet.py` and `config.py`: shorten the old 1.05-unit hip anchor to 0.465 to better match the guide's short chick-like legs.
- `rig.py`: creates a basic rigid-part posing armature for body, wings, legs and tail.
- `render_review.py`: creates five views plus Morning/Evening/Night samples and writes evaluated mesh counts.

## Known gaps — do not treat these as completed

1. **Visual match not yet verified:** actual Blender 5.3 renders must be compared side-by-side with the supplied guide. Shape, eyes, wing position, foot proportions and feather density may need iteration.
2. **Body is fused but not sculpt-perfect:** Voxel Remesh provides a continuous volume; it does not reproduce the guide's exact hand-sculpted contour automatically.
3. **Feather details are procedural approximations:** visible individual feather geometry is now present, but accurate fine barbs, feather edge breakup and natural down-fuzz are not yet equivalent to a high-end sculpt/texture groom.
4. **Rig is not a full deformation rig:** wings/legs/tail are rigid-part parented. The torso/head is not skin-weighted, and toes are not individually articulated by controls.
5. **Expressions are incomplete:** five named presets exist; `Blink` is real, but gaze direction, mouth phonemes, cheek deformation, eye-squint combinations and expression animation are not complete.
6. **Perch grip is only geometry:** the toes do not yet wrap around a curved branch through IK or pose controls.
7. **No mobile export proof:** no GLB export, texture baking, LOD, polygon budget, or Android-device performance test has been performed.
8. **No perceptual similarity metric:** the report gives structural data; it cannot certify that the result visually matches the reference.

## Static expression presets

In Blender's Python Console, with the project folder on `sys.path`:

```python
from shukhpakhi.expressions import set_expression
set_expression("Happy")  # Normal, Happy, Excited, Thinking, Sleepy
```

To return to the base look:

```python
set_expression("Normal")
```

To close one eye manually, select `Eye_L_Eyelid_BlinkShape` or `Eye_R_Eyelid_BlinkShape`, open Object Data Properties > Shape Keys and set `Blink` to 1.0.

## Folder layout

```text
Shukhpakhi_Blender53_GuideReconstruction/
├── build_shukhpakhi.py
├── render_review.py
├── validate_project.py
├── README.md
└── shukhpakhi/
    ├── config.py
    ├── utils.py
    ├── materials.py
    ├── feather_engine.py
    ├── body.py
    ├── wings.py
    ├── face.py
    ├── feet.py
    ├── tuft.py
    ├── rig.py
    ├── expressions.py
    ├── perch.py
    └── assemble.py
```
