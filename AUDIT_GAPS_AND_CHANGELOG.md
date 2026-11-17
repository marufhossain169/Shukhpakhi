# Shukhpakhi source audit — evidence, changes and remaining gaps

## Supplied archive inventory

The uploaded archive `Shukhpakhi_Phase2_3_QualityAndMaterials.zip` contained:
- `build_shukhpakhi.py`, `render_review.py`, `README.md`
- `shukhpakhi/config.py`, `utils.py`, `materials.py`, `body.py`, `face.py`, `wings.py`, `feet.py`, `tuft.py`, `assemble.py`, `__init__.py`

It did **not** contain a `.blend`, source render images, or `model_report.json`.

## Confirmed source-code findings

| Original area | Evidence in supplied source | Consequence | Revised action |
|---|---|---|---|
| Body/head | `body.py` called `_make_sculpted_ellipsoid` separately for body and head; no union/remesh modifier | Separate intersecting shells, not an integrated volume | Joined BMesh source volumes + Voxel Remesh + Smooth modifier |
| Belly/back | Separate `Belly_Cream_Patch` and `Back_Sage_Patch` ellipsoids | Cushion/cape can read as overlays rather than integrated plumage | Removed bulky patches; shader gradient + back feather overlay |
| Wing | `wings.py` built a single UV sphere and displaced its surface with sine/cosine terms | Ridges are not individual feathers | Reusable feather mesh engine + covert/secondary/primary layers |
| Feather detail | Original `materials.py` used Noise and Bump | Surface noise cannot create feather silhouettes or layering | Keep micro-noise subtle; add actual geometry feathers |
| Eyelids | Original `face.py` made clipped UV sphere shells; no shape keys or animation code | “Blinking-ready” claim was unsupported | Front eyelid mesh with a real `Blink` shape key |
| Legs | Original `config.py` set `HIP_Z = 1.05`, while body lower edge is around 0.36 | Visible leg length disproportionate to guide | Lower hip anchor to 0.465; short leg construction |
| Rig | No armature builder in original ZIP | No real posing rig | Added rigid-part armature; not a deformation rig |
| Rendering | Original render script made five views but no mood presets or evaluated geometry counts | Insufficient evidence about material/mood quality and evaluated meshes | Added 5 views + 3 lighting moods + evaluated counts |
| Build path | Original path resolution depends on current `.blend` or Text Editor context | Fragile when starting from an unsaved scene | Use script path and explicit project-folder validation |

## Changes implemented in this revision

- Full replacement of `config.py`, `utils.py`, `materials.py`, `body.py`, `wings.py`, `face.py`, `feet.py`, `tuft.py`, `assemble.py`.
- Added `feather_engine.py`, `rig.py`, `expressions.py`, and optional `perch.py`.
- Added new build, review and validation scripts.
- Preserved guide swatches exactly: `#A7C49A`, `#D7E8C5`, `#F8F9E9`, `#EDE7D9`, `#F6A623`.

## Unverified / remaining critical gaps

- No Blender 5.3 binary available in this authoring runtime: no `.blend` was generated and no actual renders were produced here.
- No visual comparison score is available; human reference review is mandatory.
- Current procedural feather mesh is a structural improvement, not yet high-end feather barbs/fuzz grooming.
- Voxel remesh is a fused base volume, not an exact sculpt of the guide silhouette.
- Rig is rigid-part only; no skin-weight deformation.
- Five expression helpers are not five fully sculpted/animated facial expressions.
- No branch-grip IK, flight/landing animation, GLB optimization, or Android performance verification.

## Release gate

Do not call this final until a Blender 5.3 run produces the review renders, and the front/3-4/side/back views have been compared to the supplied guide. In particular inspect the head/body contour, eye size/placement, wing footprint, individual feather layers, feet scale and tuft silhouette. Record each mismatch and iterate.
