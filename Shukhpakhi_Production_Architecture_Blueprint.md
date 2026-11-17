# SHUKHPAKHI — Production Architecture & Engineering Blueprint

**Document date:** 14 November 2026  
**Authoring target:** Blender 5.x (exact runtime build must be recorded before implementation)  
**Primary deliverable:** High-fidelity Blender hero character + deterministic, optimized real-time GLB asset  
**Reference authority:** Likipiki Master Bird Design Guide and `Shukhpakhi_Current_Blend_Audit.zip`

---

## 0. Executive architectural decision

**Do not rebuild the bird from zero. Do not increase feather count first.**

The audit describes an already-developed static character with semantic collections, separate sage/cream body plumage, head plumage, down-like layers, front and rear wing coverts, primaries, secondaries, a tail fan, packed maps, `FeatherUV`, `FeatherColor` and `DownColor` attributes. The dominant confirmed defect is material routing and low-information texture content. The current source also has no Armature, shape keys, skinning or meaningful animation data.

The production strategy is therefore:

1. Freeze and preserve the current source.
2. Correct the P0 shader defects without changing geometry.
3. Replace/repair the texture maps and prove the intended colour under neutral lighting.
4. Inspect the existing groom at macro and full-character scale.
5. Keep, tune or selectively rebuild only the failing geometry layers.
6. Add a hybrid Geometry Nodes + feather-card groom system, initially in a non-destructive collection.
7. Build a deformation rig with corrective shapes and repeatable pose tests.
8. Create a Blender hero shader and a separate export-safe real-time material profile.
9. Bake/realize procedural geometry and produce LODs.
10. Export, re-import and test the GLB in the actual target runtime.

The Master Bird Guide takes precedence over generic realism. It calls for a soft, fluffy cream body, sage/light-green layered feathers, glossy expressive eyes, small orange beak/feet and gentle warm lighting. Do not add strong metallic shine, saturated rainbow iridescence, overlong fur, or a sharper/aggressive bird silhouette merely because those effects look technically sophisticated.

## 1. Evidence ledger: confirmed, inferred and unknown

### 1.1 Confirmed by the supplied audit report

- The audit package reports 48 objects, 44 mesh objects, 20 materials and 5 image datablocks.
- The audited scene totals **1,079,394 vertices and 1,058,554 polygons** across mesh objects. The default `Cube` is included in the inventory.
- The scene is reported as EEVEE, 1920×1080, 24 fps, frame range 1–250, one camera and three area lights.
- Semantic collections already exist for undercoat, body plumage, head plumage, down, wings, tail/crown, face, feet and preview lighting. Preserve and clean this organization.
- Important existing assets include a fused undercoat, separate sage and cream body contour layers, body/head down groom meshes, front/rear wing coverts, primary/secondary feathers and an individual tail-fan mesh.
- Existing meshes contain `FeatherUV`, `FeatherColor` and/or `DownColor` attributes in the places described by the audit.
- The active feather material has two Mix nodes with unlinked Factor = 1.0; those routes discard the intended `FeatherColor` and then discard the prior result for a near-white grayscale noise branch.
- The undercoat material requests `BodyTint`, which the audit did not find on the inspected undercoat mesh; its Mix also selects a noise/ramp branch.
- The packed 1024×1024 albedo is nearly white/achromatic (reported mean ≈248.17/255, identical RGB channels).
- The packed normal is near-flat (reported B mean ≈253.9, R/G near 127) with horizontal wavy bands rather than clear diagonal barb structure.
- The packed roughness map is nearly uniform and very high (reported mean ≈232.9/255, approximately 0.91).
- The audit reports no armature, Armature modifier, shape keys, animation actions or native Hair Curves.
- The three major texture maps are packed, but their recorded paths point to an old absolute Windows/OneDrive location.
- Ten material variants are reported unused; a default `Cube` object remains.

### 1.2 Not established by the supplied package

The ZIP contains the audit report, the read-only Blender audit script, texture images and preview evidence. It does **not** contain `Shukhpakhi_current.blend`. Therefore this blueprint does not claim to have independently opened or evaluated the blend file.

Without running Blender on a copy of the actual file, the following remain unknown:

- Evaluated render appearance at final resolution and current runtime version.
- Feather root embedding, floating, intersections, face winding and normal orientation.
- Whether the UV V axis consistently runs from feather root to tip.
- Whether front/rear covert layers conceal supports in rear/side/banked views.
- The actual appearance of the EEVEE shader and colour management.
- Whether the default Cube is render-visible or an intentional hidden dependency.
- Actual frame time, VRAM, memory use, render time and runtime draw calls.

### 1.3 Blender version discrepancy

The audit says the native blend header contains version code `0503`, interpreted by that audit as a Blender 5.0.3-style identifier, not `0530` for 5.3.0. The stated working version is Blender 5.3. Do not assume these are the same. The first runtime step must record `bpy.app.version_string`, `bpy.app.version` and the version reported by the installed executable; then open a copy and save a new versioned working file only after confirming compatibility.

---

## 2. Target architecture and non-destructive project layout

Retain the existing semantic collections as the source layer. Add versioned collections rather than overwriting the original meshes.

```text
SHUKHPAKHI_PROJECT/
├── 00_REFERENCE_LOCKED/
│   ├── Master_Bird_Guide
│   └── reference_crops_front_3q_side_back
├── 01_SOURCE_AUDIT_LOCKED/
│   ├── original_objects
│   └── original_materials
├── 02_HERO_BODY/
│   ├── Undercoat
│   ├── Sage_Body_Plumage
│   ├── Cream_Breast_Plumage
│   └── Head_Plumage
├── 03_HERO_GROOM/
│   ├── GN_Down_Guides
│   ├── GN_Down_Evaluated
│   ├── Wing_Primaries
│   ├── Wing_Secondaries
│   ├── Wing_Coverts_Front
│   ├── Wing_Coverts_Back
│   └── Tail_Fan
├── 04_RIG_AND_CORRECTIVES/
│   ├── Armature
│   ├── Corrective_Shape_Keys
│   └── Animation_Test_Actions
├── 05_MATERIALS_AND_TEXTURES/
│   ├── Hero_Cycles
│   ├── Preview_EEVEE
│   └── Runtime_GLTF
├── 06_LIGHTING_TESTS/
│   ├── Neutral_Studio
│   ├── Morning
│   ├── Evening
│   └── Night
├── 07_RUNTIME_LODS/
│   ├── LOD0_Hero_Runtime
│   ├── LOD1_Default_UI
│   ├── LOD2_Low_Power
│   └── LOD3_Impostor
└── 08_EXPORT/
    ├── GLB
    ├── FBX
    ├── Textures
    └── Validation_Reports
```

**Non-destructive rule:** source meshes, materials and textures remain unchanged in `01_SOURCE_AUDIT_LOCKED`. Each repair is made in a working copy or versioned collection. Keep a dated `.blend` checkpoint before every destructive apply, remesh, join, decimate, UV repack or bake operation.

## 3. Phase 0 — Freeze, baseline and runtime truth

### Execution

1. Obtain the actual `.blend` file and make two copies: immutable backup and working copy.
2. Open the working copy using the intended Blender executable.
3. Run `runtime_audit_in_blender.py` from the audit ZIP.
4. Save the exact Blender version, scene engine, mesh totals, collection list, image packing, UV maps, attributes, shader links, object visibility, armatures, shape keys, actions and modifier inventory.
5. Render a baseline set without editing: front, 3/4, side, back, top, plus macro crops of breast down, body contour feathers, wing front/rear and tail.
6. Use neutral grey/white studio lighting, neutral world, fixed exposure and orthographic cameras for structural comparisons. Keep cinematic mood renders separate.

### Gate 0 — must pass before repair

- The original file opens without missing data or recovery prompts.
- Audit report and baseline render set are saved beside the working copy.
- Blender runtime version is recorded unambiguously.
- Original file remains untouched.

---

## 4. Phase 1 — P0 shader repair (first implementation priority)

### 4.1 Feather base-colour diagnostic

For the first test only, bypass both faulty Mix nodes:

```text
Color Attribute: FeatherColor ───────────────> Principled BSDF: Base Color
Principled BSDF ─────────────────────────────> Material Output
```

Do not add noise, albedo, bump or normal nodes in this first test. Render the sage/cream feather regions under neutral light. This isolates whether the attribute exists, has the correct domain and contains the expected values.

If this diagnostic fails, inspect:

- Exact attribute spelling and case: `FeatherColor`.
- Attribute data type: colour, not float/vector.
- Domain: point or corner; choose one deliberately and use it consistently.
- Whether values are populated rather than default white/black.
- Whether every assigned feather mesh has the attribute.
- Whether the shader is sampling the intended object/mesh and not a stale material variant.

### 4.2 Undercoat tint repair

The audit reports that the undercoat shader requests `BodyTint`, but the undercoat mesh does not expose it. Choose one explicit approach:

**Preferred:** add a real `BodyTint` colour attribute with a documented domain and paint/derive the cream breast vs sage back/crown mask.  
**Alternative:** use explicitly assigned region materials if the body regions are already separate, well-defined mesh regions.

Do not keep a dangling/missing attribute node in the final material. Do not let a noise ramp become the main pigment source.

### 4.3 Final hero material graph

After the diagnostic works, introduce details gradually:

```text
FeatherColor attribute (linear) ───────────────┐
                                                ├─ controlled pigment multiply ─ Base Color
FeatherAlbedo image (sRGB, subtle variation) ──┘

FeatherRoughness (Non-Color) ───────────────────────────────────────────────> Roughness
FeatherNormal (Non-Color) -> Normal Map (Tangent Space) -> Normal ──────────> Normal
FeatherUV -> UV Map -> Image Texture / Tangent basis
FeatherUV -> Tangent node (where supported) ───────────────────────────────> Tangent
```

Suggested starting ranges for look-development, not final locked values:

| Parameter | Starting range | Notes |
|---|---:|---|
| Metallic | 0.0 | Bird feathers are dielectric, not metal. |
| Body/contour roughness | 0.72–0.90 | Tune by scale and lighting; avoid a plastic hotspot. |
| Down roughness | 0.82–0.96 | Soft, diffuse, broad response. |
| Specular IOR | physically plausible dielectric | Do not raise specular to fake wet plastic. |
| Sheen | subtle, 0.15–0.35 starting point | Use only to recover soft edge response. |
| Subsurface | low, restrained | Mostly for thin down/edge backlighting, not a waxy whole-body effect. |
| Anisotropy | subtle, tangent-aligned | Direction follows feather rachis; use only in render paths that support it. |

**Important renderer limitation:** Blender 5.3 EEVEE documents Principled anisotropy as unsupported; its sheen is only an approximation. Therefore anisotropic feather highlights must be validated in Cycles for the hero render. For EEVEE/mobile, use a compatible fallback (baked normal/roughness directionality or a tested custom runtime shader), not an assumption that the same node graph will behave identically. See Blender's EEVEE node limitations and Principled documentation.

### 4.4 OSL decision

Do not make OSL a required production material dependency. Blender OSL is a Cycles scripting path, not a portable EEVEE/glTF runtime material. Use ordinary Blender nodes for the authoritative hero shader and a separately validated PBR-compatible runtime graph. OSL may be used for offline research/look development only, with its result baked into supported maps before export.

---

## 5. Phase 2 — Rebuild the feather texture set

The existing maps are not suitable as final feather anatomy maps. Preserve them as audit evidence, then generate a versioned replacement set.

### 5.1 Feather UV convention

- Standardize `FeatherUV` on every feather mesh.
- `U` runs across the feather width; `V=0` at root and `V=1` at tip (or choose the reverse, but document it and keep it identical everywhere).
- Confirm orientation on at least 10 representative feathers: primary, secondary, covert, tail and body contour.
- Use a tangent basis derived from the same UV map used for the normal texture.
- Avoid mirrored UVs for baked tangent-space normal maps unless the mirrored tangent handedness is verified. Mirroring is acceptable for simple colour-only cards that share the same symmetric atlas region.

### 5.2 New map specifications

| Map | Requirements | Colour space |
|---|---|---|
| Feather albedo | Sage/cream pigment variation, subtle shaft/barb colour, no baked lighting or shadow | sRGB |
| Feather tangent normal | Central rachis ridge and fine diagonal barbs branching from shaft; restrained amplitude | Non-Color / linear |
| Roughness | Meaningful but subtle variation; not almost constant 0.91 | Non-Color / linear |
| AO | Contact/overlap occlusion only; avoid dark painted fake shadows | Non-Color / linear |
| Alpha mask (where used) | Clean feather silhouette and limited edge fringe; no fuzzy semi-transparent halo | Linear alpha |

Use a compact ORM map for runtime where appropriate:

```text
ORM.R = Ambient Occlusion
ORM.G = Roughness
ORM.B = Metallic (0 for the bird)
```

The glTF metallic-roughness convention uses G for roughness and B for metallic, while occlusion reads R. The same packed image can be referenced through the corresponding material slots if the target importer handles it correctly. Validate this by re-importing the final GLB.

### 5.3 Normal map acceptance

- The map must be a tangent-space normal map, not a height image mistakenly plugged into Normal.
- The blue channel should remain near the expected tangent-space normal range, with controlled R/G perturbations.
- Confirm the green/Y convention with a known test card and the actual runtime; do not blindly flip it.
- Inspect grazing light from at least four directions.
- Check seams at feather roots and tips.

### 5.4 Texture packing and resolution

- Hero source: keep high-quality source maps, normally 2K for the main feather atlas unless close-up render tests demand more.
- Runtime default: 1K atlas; 512px for low LOD.
- Keep atlas padding for mipmaps (initial target: 8–16 px at 2K, adjusted after mip-chain testing).
- Albedo RGB is sRGB; normal, roughness, metallic and AO are linear/Non-Color.
- Do not bake light direction into albedo.
- Pack texture files into the `.blend` and also ship clean relative paths in the release folder.

### Gate 2

A neutral render must show the correct sage/cream regions before geometry changes. A macro render must show plausible feather direction and micro-relief without obvious horizontal striping, plastic specular bands or noisy stippling.

---

## 6. Phase 3 — Hybrid groom and feather architecture

### 6.1 First rule: inspect current geometry before generating more

The project already has large body/head contour layers, down meshes and wing feather layers. Render existing geometry at:

- Full character scale (guide-style character height).
- 100%, 200% and 400% crops of breast, cheek and back.
- Wing front, wing rear and 90-degree bank.
- Tail fan from rear and three-quarter views.

Classify each asset as **KEEP**, **TUNE**, **REBUILD** or **REMOVE**. Only a failed category is rebuilt. A high polygon count does not prove visual quality, and a low-resolution preview does not prove geometry defects.

### 6.2 Underbelly/chest down: procedural Geometry Nodes

Use a dedicated Geometry Nodes group such as `GN_Shukhpakhi_DownGroom` for short, soft down. The down system must not resemble long mammal fur.

**Inputs**

- Undercoat surface.
- `DownDensity` float mask.
- `DownLength` float mask.
- `DownColor` colour attribute.
- `FeatherFlow` vector/rotation field.
- Seed and density controls.

**Node logic**

```text
Undercoat Mesh
   ├─ Named Attribute: DownDensity ──> density field
   ├─ Named Attribute: DownLength  ──> scale/length field
   ├─ Named Attribute: DownColor   ──> instance colour
   └─ Distribute Points on Faces (Poisson Disk)
          └─ Align to surface normal + local FeatherFlow
                 └─ Instance on Points (3–5 short clump variants)
                        └─ deterministic random rotation/scale/length
                               └─ Join Geometry with undercoat
```

Use `Distribute Points on Faces` with Poisson Disk spacing for controlled density and stable point IDs. Use `Instance on Points` to reuse small geometry rather than making every clump a unique mesh. Blender 5.3 documents stable IDs and attribute transfer for point distribution, and shared geometry instances rather than duplicated underlying geometry.

**Groom constraints**

- Dense but short down on breast/underbelly and cheek transition; sparse around eyes, beak, nostrils and toe joints.
- Root must be embedded in the undercoat; tips should break the silhouette only subtly.
- Use multiple small clump variants and deterministic per-point random values.
- Avoid uniform spacing, identical yaw, identical length or identical direction.
- Control density with a painted mask, not global density alone.
- Do not cover the clean eye/face silhouette or change the round body proportions.

For hero grooming, a small guide-curve setup may be used to author flow, then converted to short tapered clumps. Native Hair Curves can be useful for guide/interpolation and trimming, but do not ship a large live hair simulation as the mobile asset. Blender 5.3 Hair Curves includes guide interpolation, attachment and curve-profile controls; use those only where they improve the groom and bake the evaluated result for delivery.

### 6.3 Primary and secondary flight feathers: card + geometry hybrid

Use individually shaped feather meshes/cards for primaries and secondaries, grouped by their anatomical attachment regions.

**Do not make every major feather a transparent, alpha-blended plane.** That would retain sorting instability at shallow viewing angles. Default architecture:

1. Model the main feather blade silhouette as actual tapered geometry with a subtle thickness/rounded edge.
2. Use an opaque material for the main blade wherever possible.
3. Use alpha masking (`MASK`/alpha clip) only for very fine barbed/fringe edges or small wisps.
4. Reserve true alpha blending for rare, intentionally translucent wisps and test them independently.
5. Avoid coplanar overlapping feather cards; use anatomical layering and embedded roots.
6. Give every feather a stable pivot at its root and an orientation derived from local wing flow.
7. Use feather-specific colour variation from `FeatherColor`, not a large material-per-feather count.

The glTF specification explicitly distinguishes `MASK` (cutout/depth-safe for real-time sorting) from `BLEND` (composited transparency whose sorting has implementation-specific limitations). This is why masked geometry is the preferred default for flight feathers.

### 6.4 Layer stack

| Layer | Geometry | Runtime treatment |
|---|---|---|
| Undercoat | Fused body/head base | One skinned mesh where practical |
| Short down | GN-generated clumps | Baked/realized and merged by material for runtime |
| Body contour plumage | Shingle/contour feathers | Keep only if silhouette and overlap tests pass |
| Wing primaries | Individual tapered cards/meshes | Parent/weight to hand/wrist region |
| Wing secondaries | Individual tapered cards/meshes | Parent/weight to forearm/ulna region |
| Wing coverts | Front/rear layered feathers | Separate front/rear groups; preserve overlap order |
| Tail fan | Individual feathers | Bone/shape-key fan controller |
| Facial micro-covert | Very short fine feather forms | Low density, avoid facial silhouette damage |

### 6.5 Reducing sorting, floating and z-fighting

- Use `MASK` rather than `BLEND` for major feather card alpha.
- Keep depth-writing opaque blade regions.
- Embed feather roots into the body/wing support; do not simply float cards a fixed large distance above the surface.
- Use tiny intentional layer offsets only when measured; avoid arbitrary offsets that change across scale.
- Validate front/rear coverts at 0°, 30°, 60° and near-grazing camera angles.
- Verify face normals, tangent basis, double-sided state and back-face lighting.
- Test with a moving camera, not a single frontal still.

---

## 7. Phase 4 — Rig, skinning and corrective deformation

### 7.1 Skeleton hierarchy

Use one root armature with semantic bone names and explicit pivots. Suggested hierarchy:

```text
root_master
└── body_root
    ├── pelvis
    ├── torso
    │   └── neck
    │       └── head
    │           ├── eye_L_aim
    │           ├── eye_R_aim
    │           ├── eyelid_L_ctrl
    │           └── eyelid_R_ctrl
    ├── wing_L_shoulder
    │   └── wing_L_humerus
    │       └── wing_L_ulna
    │           └── wing_L_wrist
    │               ├── wing_L_hand
    │               └── wing_L_alula
    ├── wing_R_shoulder
    │   └── wing_R_humerus
    │       └── wing_R_ulna
    │           └── wing_R_wrist
    │               ├── wing_R_hand
    │               └── wing_R_alula
    ├── tail_root
    │   ├── tail_fan_center
    │   ├── tail_fan_L_group
    │   └── tail_fan_R_group
    ├── leg_L_root -> leg_L_ankle -> toe_L_front/rear
    └── leg_R_root -> leg_R_ankle -> toe_R_front/rear
```

Add per-feather bones only where the feather needs independent articulation. Avoid one bone per tiny down clump. The primary/secondary feather groups should follow the anatomy and attach to the nearest hand/wrist or ulna segment.

### 7.2 Deformation strategy

- Skin the undercoat and anatomical wing support.
- Use rigid or near-rigid attachment for most contour/flight feather cards to avoid rubber-like feather bending.
- Keep primaries attached near their roots; their tips should follow the hand/wrist fan.
- Keep secondaries attached to the ulna/forearm region.
- Keep alula as a separate small articulated element driven from the wrist.
- Tail fan feathers should spread from the tail base rather than stretch as one wide sheet.
- Avoid putting feather tips under full influence of two distant bones.

### 7.3 Weight-paint standards

All deforming vertices must have normalized weights. Enforce at most four non-zero influences per vertex in the runtime export.

| Region | Weighting target | Rule |
|---|---|---|
| Rigid feather root | 0.90–1.00 nearest bone | Minimal influence from adjacent bone |
| Shoulder blend | gradual two-bone blend | 2–3 edge loops across shoulder transition |
| Elbow/ulna transition | gradual two-bone blend | Avoid sudden 1.0/0.0 transition on deforming support |
| Wrist transition | mostly wrist/hand | Corrective shape addresses fold volume |
| Alula | 0.95–1.00 alula bone | Keep independent from primary fan |
| Tail feather roots | 0.90–1.00 assigned tail group | Fan spread driven from bases, not tip weights |

**Heat-map convention:** blue = 0.0, cyan ≈0.25, green ≈0.50, yellow ≈0.75, red = 1.0. The map is a visualization, not a substitute for inspecting numerical weights. Normalize sum to 1.0; flag vertices with no weights, non-normalized sums, or more than four influences. Treat Auto Weights as an initial guess only; manually clean shoulder, elbow, wrist and tail roots.

### 7.4 Corrective shape keys

Create corrective shapes after the base rig weights are stable. Minimum set:

- `WingShoulder_Up_Corrective_L/R`
- `WingShoulder_Down_Corrective_L/R`
- `WingElbow_Fold_Corrective_L/R`
- `WingWrist_Twist_Corrective_L/R`
- `Alula_Raise_L/R`
- `TailFan_Spread`
- `TailFan_Fold`
- `Chest_Compress` (only if the body visibly collapses under pose)

Correctives must be sculpted at defined test poses, not guessed from arbitrary offsets.

**Driver response logic**

Let `θ` be the relevant local bone rotation, `θ0` the start threshold and `θ1` the full-correction threshold:

```python
t = clamp((abs(theta) - theta0) / (theta1 - theta0), 0.0, 1.0)
weight = t * t * (3.0 - 2.0 * t)  # smoothstep
```

This provides a smooth onset rather than an abrupt corrective switch. Use separate correctives for opposing bend directions where necessary. Blender drivers may drive shape keys for authoring, but the runtime export must not depend on Blender driver logic: bake the resulting bone and shape-key channels into animation clips before GLB/FBX export.

### 7.5 Required deformation test matrix

For each wing, render and inspect:

- Shoulder: neutral, +30°, +60°, +90° raise and corresponding down/fold pose.
- Elbow: neutral, 30°, 60°, 90° fold.
- Wrist: neutral, inward twist, outward twist and full flight extension.
- Alula: neutral, raised and folded.
- Tail: closed, 25%, 50%, 75%, 100% spread.
- Combined: full upstroke, full downstroke, gliding extension, landing flare and banked turn.

Reject pinching, visible gaps, feather-root detachment, card interpenetration, flipped normals, or abrupt volume collapse. Corrective shapes should fix a defined failure, not conceal bad base weights.

---

## 8. Phase 5 — Material architecture: hero render vs runtime

### 8.1 Hero Blender shader

Use a node-based Principled shader as the production standard. Use Cycles for final look-development and macro inspection when testing anisotropy/subtle thin-feather scattering. Keep a matching EEVEE preview shader, but document the differences.

Recommended logical layers:

1. **Pigment layer:** `FeatherColor` attribute as the stable sage/cream region colour.
2. **Micro-albedo layer:** subtle fibre/pigment variation; never near-white noise as the sole base colour.
3. **Roughness layer:** high but differentiated values across down, contour and flight feathers.
4. **Tangent-normal layer:** rachis and diagonal barbs, rooted in local feather UV.
5. **Sheen layer:** restrained broad sheen, not a clear-coat plastic shell.
6. **Thin-edge/backlight response:** low, controlled translucency/SSS for fine down in hero rendering only.
7. **Optional anisotropy:** tangent-aligned to the feather shaft, only where the renderer actually supports it.

### 8.2 Structural colour / iridescence policy

The guide does not show strong rainbow iridescence. Therefore do not implement visible peacock-like spectral colour as a default. The target is soft sage/cream plumage with directional, low-intensity highlights. If a subtle angle-dependent green shift is explored, it must be approved against the guide and disabled in the default runtime material unless it survives device tests.

### 8.3 Runtime-safe shader

Use a separate export material profile built from the subset the target importer actually supports:

- Base color map + vertex/mesh pigment baked into the map or supported vertex colours.
- Tangent-space normal map.
- ORM metallic-roughness map.
- Alpha mask where required.
- Metallic = 0.
- No reliance on OSL, live Geometry Nodes, unsupported Eevee features or Blender-only shader nodes.

Standard glTF core includes metallic-roughness, normal and occlusion textures. Do not assume Blender-specific SSS, arbitrary shader graphs or Cycles-only effects will transfer unchanged.

---

## 9. Phase 6 — Runtime optimization and LOD policy

The audit's ~1.06M polygon count is a high-detail source model, not an acceptable default budget for a small mobile UI mascot. Keep it as the authoring/hero source until geometry is proven, then build independent runtime LODs. Do not decimate the source file in place.

### 9.1 Provisional runtime budgets

These are **initial engineering budgets**, not verified performance results. Profile on the actual target phone and actual renderer before locking them.

| Asset tier | Triangle target | Texture target | Use |
|---|---:|---:|---|
| Hero source | Existing high-detail source; optimize only after macro review | 2K source maps as needed | Blender close-up / master asset |
| LOD0 | 20k–30k | 2K atlas | Full-screen companion / close view |
| LOD1 | 8k–12k | 1K atlas | Default 120–150px UI character |
| LOD2 | 2k–4k | 512px–1K | Low-power / small screen size |
| LOD3 | 2D impostor or baked pose set | sprite atlas | Tiny icon-scale display |

At the guide's approximate 120–150px character display size, LOD1 should be the initial default. LOD0 can be selected for a full-screen interaction or close-up.

### 9.2 Screen-space LOD selection

Use projected character height, not a fixed world-distance threshold:

- LOD0: projected height >300px.
- LOD1: 96–300px.
- LOD2: 40–96px.
- LOD3/impostor: <40px.

Add 10–15% hysteresis around switch thresholds to prevent flicker when the character scale changes slightly. Tune thresholds from actual device screenshots.

### 9.3 LOD reduction rules

- LOD0: retain major individual wing/tail feathers and enough body contour geometry for close silhouettes; reduce hidden internal layers.
- LOD1: remove much of the individual micro-down geometry and let normal/roughness maps carry fine surface detail; retain only visible silhouette-critical contour feathers and wing layers.
- LOD2: use fewer feather cards; preserve head tuft, wing silhouette, tail contour, eyes and beak proportions.
- LOD3: use a small baked pose/expression sprite set if the app does not need true 3D interaction at that size.

### 9.4 Draw calls and materials

- Target **4–6 material batches**, hard ceiling 8 for the bird in the default UI scene.
- Use shared feather atlas/material across sage and cream feathers; drive region colour through vertex/mesh attributes or baked atlas regions.
- Combine geometry by material and compatible rig segment, not blindly into one mesh that loses useful skinning.
- Use instancing in the Blender authoring groom; bake/realize and merge for runtime where the target renderer cannot preserve Geometry Nodes instances.
- Avoid one unique material per feather.
- Keep eyes, beak/feet and feather/body groups separate only where it provides necessary material or deformation control.
- Use a single consistent skeleton and avoid redundant mesh objects at runtime.

### 9.5 Profiling metrics

Capture at minimum:

- Triangles and vertices per LOD.
- Number of mesh primitives and material batches.
- Number of bones and maximum influences per vertex.
- Texture dimensions and compressed memory size.
- GPU frame time for the bird alone and the full Likipiki scene.
- CPU update time for animation/pose logic.
- Memory/VRAM on low- and mid-range Android hardware.

Use the app's total frame budget as the actual constraint. At 60 fps the total frame interval is 16.67 ms; do not spend that entire budget on the bird. A bird-specific GPU budget can be set after the target phone and rendering implementation are measured.

---

## 10. Phase 7 — UV, bake and export pipeline

### 10.1 GLB is the primary runtime deliverable

Use GLB/glTF 2.0 as the primary asset for real-time/mobile integration. Blender's glTF 2.0 exporter supports meshes, Principled-based materials, textures, skinning and animation (including shape-key animation). FBX is a secondary interchange format if a downstream DCC or engine specifically requires it.

### 10.2 Geometry Nodes and Hair Curves export rule

Do not rely on live Blender Geometry Nodes or unbaked grooming logic in the target runtime. Evaluate the final GN modifier, realize instances and bake the resulting mesh into named runtime collections. Convert any final Hair Curves groom that must ship into an exportable mesh/card representation. Keep the live guide/groom graph only in the `.blend` authoring file.

### 10.3 UV requirements

- Keep one UV set for material sampling (`UV_Feather` or the retained `FeatherUV`).
- Create a distinct bake UV set where needed (`UV_Bake`).
- Bake UV islands must be non-overlapping unless the overlap is intentional and identical across all baked details; unique normal/AO bake islands must not overlap.
- Maintain adequate padding for mipmaps and texture filtering.
- Confirm no inverted/degenerate UV islands and no tangent discontinuities at critical seams.
- Preserve atlas reuse only when it does not corrupt unique baked normal data.

### 10.4 Normal-map bake checklist

1. Freeze the high-resolution hero geometry.
2. Generate the low-resolution runtime LOD.
3. Unwrap its unique bake UVs.
4. Triangulate or lock the final triangulation before baking.
5. Bake tangent-space normal using the same tangent convention expected by the engine.
6. Bake AO separately or into the ORM red channel.
7. Verify the green/Y direction with a known test mesh.
8. Test the bake on the actual runtime LOD, not only in Blender.

### 10.5 Transform and skeleton checklist

- Use one documented scene unit scale; keep the bird's world dimensions consistent.
- Choose a single forward/up convention and test it in the target runtime.
- Put the root origin/pivot at the agreed character root (normally ground/perch reference), not at an arbitrary mesh centroid.
- Apply mesh object rotation/scale and establish bone roll/rest pose before skinning and animation.
- Do not casually apply transforms to a finished armature after rigging; Blender documents that transform application to armatures does not alter pose locations/animation curves in the same way as a simple mesh transform.
- Set every export mesh to clean object transforms as designed; ensure armature rest pose and inverse bind matrices are correct.
- Remove non-deforming/helper bones from the runtime skeleton unless needed by the engine.
- Enforce maximum four skin influences at export.

### 10.6 Animation export

- Create named actions/clips: `Idle`, `Blink`, `Happy`, `Excited`, `Thinking`, `Sleepy`, `Perch`, `Takeoff`, `Flight`, `Landing`, `JoyfulJump`.
- Keep one consistent rest pose and action naming convention.
- Bake driver-driven correctives and shape-key channels to keyframes before export; do not expect Blender driver expressions to execute inside the game engine.
- Export the armature, skinned meshes and animation clips together in a test GLB.
- Re-import the GLB into a clean Blender file and into the actual app runtime. Check orientation, scale, bone hierarchy, weights, materials, alpha mode and animation timing.

### 10.7 FBX secondary export

Use FBX only when required by a downstream tool. Verify forward/up axes and unit scaling explicitly. Blender's FBX documentation notes its Y-forward/Z-up convention and provides export axis conversions and Apply Transform options. Do not select Apply Transform/scale settings by habit; run a round-trip import test into the exact destination application.

---

## 11. Phase 8 — Quality gates and measurable acceptance

### Gate A — identity and static form

- Front, 3/4, side, back and top views retain the Master Bird identity.
- Head/body proportions, eye placement, beak size, tuft and wing coverage are judged against aligned reference crops.
- No visible head/body seam, detached feather roots or broken breast contour.
- As a proposed comparison target, aim for silhouette IoU ≥0.90 on aligned clean reference crops and major landmark placement within 2–3% of bird height. These are project acceptance targets, not measurements already achieved.

### Gate B — colour/material

- Sage/cream colour regions match the guide under neutral studio lighting.
- The shader no longer discards `FeatherColor` or references missing `BodyTint`.
- Albedo is not a near-white substitute for pigment.
- Normal map shows coherent root-to-tip shaft and diagonal barb direction.
- Roughness separates down, contour and flight feathers without broad plastic hotspots.
- No strong rainbow iridescence unless separately approved.

### Gate C — feather geometry

- Breast down reads as short soft plumage, not fur or a spiky hedgehog.
- Contour feathers overlap in a coherent flow.
- Primary/secondary feathers do not produce alpha sorting artifacts at grazing views.
- Front/rear coverts cover the wing support through the full bank/flight range.
- Tail fan opens without visible gaps or root separation.

### Gate D — deformation

- Normalized weights sum to 1.0 (tolerance 0.99–1.01 after export normalization).
- No more than four non-zero influences per vertex in the runtime mesh.
- No shoulder, elbow, wrist, alula or tail-base pinching in the required pose matrix.
- Corrective shapes activate smoothly and do not pop.
- Driver logic is baked into exported animation curves.

### Gate E — runtime/export

- GLB imports into a clean scene with no missing textures.
- All expected materials, normal maps and alpha modes survive.
- No unsupported Blender nodes are required at runtime.
- No live GN/Hair system is required to generate the shipped mesh.
- LOD switching is stable, with no visible popping at the chosen thresholds.
- Target device performance is measured and accepted; no performance claim is made from polygon count alone.

---

## 12. Prioritized implementation schedule

| Order | Work item | Dependency | Deliverable | Gate |
|---|---|---|---|---|
| P0 | Obtain/open source `.blend`, version check, read-only runtime audit | Actual `.blend` | Baseline audit + renders | Gate 0 |
| P1 | Repair feather and undercoat colour routing | P0 | Diagnostic material renders | Gate B initial |
| P2 | Replace albedo, normal and roughness maps | P1 | Packed, validated texture set | Gate B |
| P3 | Macro-inspect existing groom and classify KEEP/TUNE/REBUILD | P2 | Geometry change list | Gate A/C |
| P4 | Build selective GN down system and feather-card fixes | P3 | Hero groom v2 | Gate C |
| P5 | Create wing/tail skeleton, weights and correctives | Stable geometry | Rigged master | Gate D |
| P6 | Create hero and runtime material profiles | P1/P2 | Cycle/EEVEE/GLTF material variants | Gate B/E |
| P7 | Bake LOD0/LOD1/LOD2 and merge by material/rig segment | P4/P5 | Runtime meshes | Gate E |
| P8 | GLB export, round-trip import and device profile | P6/P7 | Tested GLB + report | Gate E |

**Recommended order is intentionally not “rig first” or “LOD first.”** Rigging unstable feather geometry produces expensive rework. Optimizing broken materials makes it difficult to judge what geometry should be retained. Repair the known material defects, inspect the groom, then commit to geometry and rigging.

---

## 13. Risks and explicit non-promises

1. **No visual-match guarantee yet:** there is no current full-resolution Blender render set in the supplied ZIP. A guide match can only be approved after repeatable render comparison.
2. **No mesh-topology verdict:** the audit report includes counts and datablock information, but does not prove the feather roots, intersections, normals or UV orientations are correct.
3. **No runtime performance claim:** a 1M-polygon Blender source does not directly predict final runtime performance; the runtime LOD must be measured on the target Android device.
4. **No OSL portability:** OSL is not a glTF runtime shader dependency.
5. **No guaranteed anisotropy in EEVEE:** Blender 5.3 EEVEE documents anisotropy limitations. Validate in Cycles and provide a real-time fallback.
6. **No guaranteed live Geometry Nodes export:** bake/realize the final generated geometry for the runtime artifact.
7. **No promise that all existing feather layers should remain:** the current model is dense; any layer that fails macro/full-character inspection should be tuned or removed, not automatically preserved.
8. **No claim that the current `.blend` was repaired:** the supplied package is an audit evidence package, not a modified Blender project.

---

## 14. Official technical references

- Blender 5.3 — Distribute Points on Faces: https://docs.blender.org/manual/en/5.3/modeling/geometry_nodes/point/distribute_points_on_faces.html
- Blender 5.3 — Instance on Points: https://docs.blender.org/manual/en/5.3/modeling/geometry_nodes/instances/instance_on_points.html
- Blender 5.3 — Hair Curves Interpolation: https://docs.blender.org/manual/en/5.3/modeling/geometry_nodes/hair/generation/interpolate_hair_curves.html
- Blender 5.3 — Hair Curve Attachment: https://docs.blender.org/manual/en/5.3/modeling/geometry_nodes/hair/utility/attach_hair_curves_to_surface.html
- Blender 5.3 — EEVEE supported-node limitations: https://docs.blender.org/manual/en/5.3/render/eevee/limitations/nodes_support.html
- Blender 5.3 — Principled BSDF: https://docs.blender.org/manual/en/5.3/render/shader_nodes/shader/principled.html
- Blender 5.3 — Open Shading Language: https://docs.blender.org/manual/en/5.3/render/cycles/osl/index.html
- Blender 5.3 — glTF 2.0 exporter: https://docs.blender.org/manual/en/5.3/addons/scene_gltf2.html
- Blender 5.3 — FBX exporter: https://docs.blender.org/manual/en/5.3/files/import_export/fbx_legacy.html
- Khronos — glTF 2.0 material, metallic-roughness, normal, AO and alpha-mode specification: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

---

## Final architecture decision

**Repair colour routing and textures first. Reuse what is already good. Rebuild only the geometry that fails controlled inspection. Use Geometry Nodes for short undercoat down, physically shaped/masked feather meshes for major flight feathers, a semantic armature with corrective shapes for deformation, a Cycles hero material plus a restricted runtime PBR material, and a separately optimized GLB LOD family.**

The Master Bird Guide remains the visual authority at every gate. Production approval is withheld until the source `.blend` is opened in the confirmed Blender runtime, the fixes are rendered, the rig passes the pose matrix and the exported asset passes a real-device test.
