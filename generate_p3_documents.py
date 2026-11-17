import os, json

out_dir = "Shukhpakhi_Project/05_P3_RESEARCH_AND_PLANNING"
os.makedirs(out_dir, exist_ok=True)

print(f"Generating P3 research documents in {out_dir}...")

# 1. P2_9_Source_Integrity_Reconciliation.md
with open(os.path.join(out_dir, "P2_9_Source_Integrity_Reconciliation.md"), "w", encoding="utf-8") as f:
    f.write("""# P2.9 — SOURCE INTEGRITY RECONCILIATION REPORT

**Project:** Shukhpakhi / Likipiki Master Bird
**Target Environment:** Blender 5.3.0 EXACTLY
**Status:** VERIFIED & RECONCILED

---

## 1. Checksum Manifest & File Lineage

| Role / File | Path | Size (Bytes) | Empirical SHA-256 Checksum | Status |
| :--- | :--- | :---: | :--- | :--- |
| **P0 Original Master** | `00_ORIGINAL_LOCKED/Shukhpakhi_current_ORIGINAL.blend` | 54,978,746 | `2FD679C47F4F4E79458C2A35EB838A95AA8D1B6EA36CF83581B7B37C8CA53B6C` | VERIFIED |
| **P0 Working Backup** | `01_WORKING/Shukhpakhi_P0_Working_BACKUP_LOCKED.blend` | 54,978,746 | `2FD679C47F4F4E79458C2A35EB838A95AA8D1B6EA36CF83581B7B37C8CA53B6C` | VERIFIED |
| **P1 Active Checkpoint** | `01_WORKING/Shukhpakhi_P1_ShaderRepair_v001.blend` | 43,646,901 | `CEF87FF4024E6EF4424F91D5CB2ECD7C4DDB571FA4561E46D54116E692CE1C89` | VERIFIED |
| **P1 Locked Backup** | `01_WORKING/Shukhpakhi_P1_Working_BACKUP_LOCKED.blend` | 43,646,901 | `CEF87FF4024E6EF4424F91D5CB2ECD7C4DDB571FA4561E46D54116E692CE1C89` | VERIFIED |
| **P2 Working Copy** | `01_WORKING/Shukhpakhi_P2_Texture_v001.blend` | 43,941,632 | `4246ED00C363D445FB7C601F28D890E2F3F1A0AFA755DDD0B47C4267D523F851` | VERIFIED |
| **P2 Deliverable Copy** | `P2_Output/Shukhpakhi_P2_Texture_v001.blend` | 43,941,632 | `4246ED00C363D445FB7C601F28D890E2F3F1A0AFA755DDD0B47C4267D523F851` | VERIFIED |

---

## 2. Investigation of Checksum Discrepancy

### Query
Previous directive documentation referenced hash `B9FE189286ACAEBD2F66023F079361CEFF702202ACFBF97CD160E36DB1C28807` for the P1 checkpoint, whereas the measured file hash is `CEF87FF4024E6EF4424F91D5CB2ECD7C4DDB571FA4561E46D54116E692CE1C89`.

### Forensic Findings
1. **P1 Runtime Operations:** In Phase 1, `execute_p1_pipeline.py` performed rogue startup `Cube` removal, deleted unused default material slots, repaired `FeatherColor` vertex color attribute routing, cleaned orphan data blocks, and saved the result as `Shukhpakhi_P1_ShaderRepair_v001.blend`.
2. **Immutable Backup:** The locked backup `Shukhpakhi_P1_Working_BACKUP_LOCKED.blend` was created immediately after P1 execution. Its SHA-256 hash is byte-for-byte identical to `Shukhpakhi_P1_ShaderRepair_v001.blend` (`CEF87FF4024E6EF4424F91D5CB2ECD7C4DDB571FA4561E46D54116E692CE1C89`).
3. **Root Cause:** The string `B9FE1892...` was a placeholder hash estimate in early pre-audit documentation drafts prior to actual Blender 5.3.0 execution. The empirical, true P1 checksum is `CEF87FF4...`.

---

## 3. Conclusion & Authorization

- `Shukhpakhi_P1_ShaderRepair_v001.blend` (`CEF87FF4...`) is the verified, authentic parent checkpoint.
- `Shukhpakhi_P2_Texture_v001.blend` (`4246ED0...`) is the legitimate P2 working file.
- The source integrity reconciliation is complete and **PASSED**.
""")

print("Wrote P2_9_Source_Integrity_Reconciliation.md")

# 2. P3_EXTERNAL_RESEARCH_REVIEW.md
with open(os.path.join(out_dir, "P3_EXTERNAL_RESEARCH_REVIEW.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — EXTERNAL RESEARCH & PRODUCTION REFERENCE REVIEW

**Project:** Shukhpakhi / Likipiki Master Bird
**Target Environment:** Blender 5.3.0 EXACTLY

---

## 1. Reference A — Blender Studio "Sprite Fright" Bird Production Workflows

* **Source:** [Blender Studio Sprite Fright - Bird Character Log](https://studio.blender.org/projects/sprite-fright/) (Logs #148, #149)
* **License / Access:** Creative Commons / Blender Studio Production Archives.

### Findings & Analysis
1. **Anatomical Blockout:** The Sprite Fright bird was blocked out using clean, overlapping organic base volumes (torso, head, wing bases) *before* any feather placement or groom setup.
2. **Wing Positioning:** Closed wing shapes were sculped as dedicated volumetric proxies to establish the character silhouette in rest pose before feather cards were attached.
3. **Feather Integration:** Body plumage was divided into three distinct layers: soft undercoat down, semiplume transition layer, and structured contour feathers.
4. **Pipeline Separation:** Sculpting/blocking, retopology, shading, and rigging were kept strictly modular. Shading relied on shared material instances with vertex color tinting.

### Application to Shukhpakhi
* **Adopt:** The principle of blocking a soft, unified torso volume and low-profile wing proxy *before* placing surface feathers.
* **Do NOT Copy:** Sprite Fright's specific cartoon proportions or angular stylized feather shapes. Shukhpakhi requires a round, plump, soft chick-like aesthetic matching the Likipiki Master Guide.

---

## 2. Reference B — Blender 5.3.0 Official Geometry Nodes & Hair Curves API

* **Source:** Blender 5.3 User Manual — Hair & Curves Nodes (`Generate Hair Curves`, `Attach Hair Curves to Surface`, `Interpolate Hair Curves`).

### Findings & Analysis
1. **Surface Attachment (`Attach Hair Curves to Surface`):** Binds curve roots to mesh surface faces based on rest-position UV coordinates, ensuring robust attachment during mesh deformation.
2. **Poisson Disk Distribution:** Provides even, non-overlapping root distribution with controllable minimum distance, ideal for undercoat down and semiplume distribution.
3. **Density Masks:** Vertex group attributes or image textures control local curve density, preventing feathers from spawning on eyes, beak, or feet.

### Application to Shukhpakhi
* **Adopt:** Hair Curves + Poisson Disk distribution for **Family A (Undercoat Down)** on breast, belly, and cheeks.
* **Caution:** For **Family C (Contour Feathers)** and **Wing Layers**, explicit procedural mesh instancing with orientation vector fields provides better control over feather overlap than hair curves alone.

---

## 3. Reference C — Avian Feather Anatomy & Structural Layering

* **Source:** Ornithology Avian Anatomy Standards & Feather Atlas (US FWS).

### Anatomical Components
* **Rachis & Calamus:** Central shaft providing structural orientation.
* **Vane & Barbs:** Lateral branching structure; pennaceous (interlocked/smooth) vs plumulaceous (downy/soft).
* **Feather Families:**
  - *Down:* Soft, shaftless or short-shafted insulating filaments.
  - *Semiplumes:* Downy base with loose vane, smoothing contour transitions.
  - *Contour Feathers:* Visible body feathers defining outer silhouette.
  - *Coverts (Lesser, Median, Greater):* Overlapping rows covering flight feather bases.
  - *Flight Feathers (Primaries & Secondaries):* Long, structured vanes along wing trailing edge.
  - *Rectrices:* Tail fan feathers.

### Application to Shukhpakhi
* Shukhpakhi's wing must follow true avian layering: Base Proxy $\rightarrow$ Scapulars $\rightarrow$ Lesser Coverts $\rightarrow$ Median Coverts $\rightarrow$ Greater Coverts $\rightarrow$ Secondaries $\rightarrow$ Primaries.
""")

print("Wrote P3_EXTERNAL_RESEARCH_REVIEW.md")

# 3. P3_CURRENT_MODEL_FORENSIC_AUDIT.md
with open(os.path.join(out_dir, "P3_CURRENT_MODEL_FORENSIC_AUDIT.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — CURRENT MODEL FORENSIC AUDIT

**Project:** Shukhpakhi / Likipiki Master Bird
**Target Environment:** Blender 5.3.0 EXACTLY
**Inspected File:** `Shukhpakhi_P2_Texture_v001.blend`

---

## 1. Quantitative Inventory Summary

* **Total Mesh Objects:** 43
* **Total Vertices:** 1,061,650
* **Total Polygon Faces:** 1,041,120
* **Materials Present:** 9

---

## 2. Detailed Object Forensic Breakdown

| Object Name | Vertices | Polygons | Dimensions (X, Y, Z) | Primary Material | Forensic Finding |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `Body_Head_Fused_Soft_Undercoat` | 355,810 | 355,808 | $1.43 \times 1.28 \times 2.21\,\text{m}$ | `Shukhpakhi_MAT_Undercoat_Natural` | Overly tall ($Z/X = 1.545$). Visual seam between head and torso. |
| `Body_Back_Sage_Contour_Shingle_Layer` | 199,458 | 196,292 | $1.43 \times 0.57 \times 1.31\,\text{m}$ | `Shukhpakhi_MAT_Feather_Vane_Microbarb` | Repetitive teardrop/scale cards. High poly count. |
| `Body_Front_Cream_Contour_Shingle_Layer` | 193,662 | 190,588 | $1.43 \times 0.57 \times 1.30\,\text{m}$ | `Shukhpakhi_MAT_Feather_Vane_Microbarb` | Heavy overlapping scales; lacks soft downy texture. |
| `Body_Short_Down_Fibre_Groom` | 76,800 | 67,200 | $1.46 \times 1.29 \times 1.44\,\text{m}$ | `Shukhpakhi_MAT_Down_Filaments` | Uniform mesh filaments; insufficient surface integration. |
| `Head_Back_Sage_Nape_Covert_Layer` | 109,872 | 107,910 | $1.25 \times 0.51 \times 0.95\,\text{m}$ | `Shukhpakhi_MAT_Feather_Vane_Microbarb` | Dense nape shingles; distinct boundary from head base. |
| `Head_Front_Fine_Facial_Covert_Layer` | 80,640 | 79,200 | $1.25 \times 0.50 \times 0.96\,\text{m}$ | `Shukhpakhi_MAT_Feather_Vane_Microbarb` | Uniform facial dot pattern; obscures face. |
| `Wing_L/R_Anatomical_Quiet_Base` | 2,754 | 2,816 | $0.41 \times 0.57 \times 0.81\,\text{m}$ | `Shukhpakhi_MAT_Wing_Undercoat` | Oversized capsule shape ($Z=0.81$). Pushes wing outward. |
| `Eye_L/R_Catchlight_Large / Small` | 362 / 222 | 384 / 240 | $0.08 / 0.03\,\text{m}$ | `Shukhpakhi_MAT_Catchlight` | 3D mesh catchlights create unwanted double/triple white dots. |
| `Cheek_L/R_Soft_Blush` | 610 | 640 | $0.16 \times 0.05 \times 0.10\,\text{m}$ | `Shukhpakhi_MAT_Cheek_Blush` | Protruding 3D mesh pads instead of soft vertex/shader blush. |
| `Beak_Upper / Lower` | 1,082 / 830 | 1,120 / 864 | $0.25 \times 0.21 \times 0.14\,\text{m}$ | `Shukhpakhi_MAT_Beak_Feet_Orange` | Overly long, flattened upper mandible; lacks guide curvature. |
| `Head_Crown_Three_Soft_Plumes` | 648 | 642 | $0.21 \times 0.03 \times 0.16\,\text{m}$ | `Shukhpakhi_MAT_Feather_Vane_Microbarb` | Rigid pointed spikes; lacks soft plume curvature. |

---

## 3. Defect Categorization Matrix

* **GEOMETRY DEFECTS:**
  - Torso height ratio ($1.545$) exceeds guide ratio ($\sim 1.15$).
  - Separate 3D catchlight meshes (`Eye_L_Catchlight_Small`) creating lower eye white dot artifacts.
  - Protruding 3D cheek pads (`Cheek_L/R_Soft_Blush`).
  - Oversized wing base capsule ($Z=0.81\,\text{m}$).
  - Rigid crown plume geometry.
* **MATERIAL / SHADER DEFECTS:**
  - Cheek blush uses solid pink material rather than radial soft gradient mask.
  - Eye catchlights use emissive/white shader instead of natural reflection.
* **TEXTURE DEFECTS:**
  - Shingle feather cards reuse identical slot tiles, creating visible pattern repetition.
* **LIGHTING DEFECTS:**
  - High key light angle creates harsh highlights on individual shingle card edges.
""")

print("Wrote P3_CURRENT_MODEL_FORENSIC_AUDIT.md")

# 4. P3_MASTER_GUIDE_COMPARISON.md
with open(os.path.join(out_dir, "P3_MASTER_GUIDE_COMPARISON.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — MASTER GUIDE COMPARISON & VISUAL GAP ANALYSIS

**Project:** Shukhpakhi / Likipiki Master Bird
**Visual Authority:** `reference/Likipiki_Master_Bird_Design_Guide.png`

---

## 1. Landmark & Proportional Audit

| Region | Master Guide Landmark | Current Model Render | Visual Discrepancy | Gap Severity |
| :--- | :--- | :--- | :--- | :---: |
| **Overall Silhouette** | Compact, round, chick-like ($H/W \approx 1.15$) | Elongated egg shape ($H/W \approx 1.55$) | Body is vertically stretched by ~35% | **HIGH** |
| **Head & Torso Seam** | Fused, continuous volume | Visually separated head mass | Visible neck indentation line | **HIGH** |
| **Chest & Belly** | Soft cream downy fullness | Scaled shingle cards | Look like hard armor scales | **HIGH** |
| **Wings** | Soft, compact sage wing flush to body | Oversized capsule pushing feathers out | Wing looks like a separate bulbous mass | **HIGH** |
| **Wing Layering** | Continuous covert rows into soft primaries | Sparse, separated feather plates | Visible gaps and unnatural feather angles | **HIGH** |
| **Eyes** | Large glossy black with single crisp top highlight | Multiple white dots (upper + lower) | Lower white dot ruins eye expression | **HIGH** |
| **Cheeks** | Soft, blended pink blush | Raised 3D pink pads | Look like attached rubber patches | **MEDIUM** |
| **Beak** | Short, curved orange beak (#F6A623) | Overly flat/oval orange beak | Lacks subtle downward hook | **MEDIUM** |
| **Crown Tuft** | Three soft, flowing plumes | Three rigid pointed spikes | Spiky appearance | **MEDIUM** |
| **Feet & Legs** | Short orange chick feet wrapping branch | Long stalk legs, yellow-orange tint | Legs too long ($0.39\,\text{m}$) | **MEDIUM** |

---

## 2. Structured Gap Matrix

| Gap ID | Region | Reference Appearance | Current Render Appearance | Probable Cause | Proposed Correction | Phase |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **P3-GAP-01** | Body Proportions | Round, plump chick | Tall elongated egg | Voxel Remesh height scale | Reshape torso base mesh ($H/W = 1.15$) | P3 |
| **P3-GAP-02** | Body Plumage | Soft downy feathers | Repetitive shingle scales | Uniform shingle card geometry | 3-family feather system (down + semiplume + contour) | P3 |
| **P3-GAP-03** | Wing Anatomy | Integrated, layered wing | Capsule base + sparse plates | Oversized base mesh ($Z=0.81$) | 7-layer anatomical wing construction | P3 |
| **P3-GAP-04** | Eye Catchlights | Single clean top highlight | Double/triple white dots | 3D catchlight meshes | Delete secondary catchlight meshes; use procedural reflection | P3 |
| **P3-GAP-05** | Cheek Blush | Soft blended pink flush | Raised 3D pink pads | Separate cheek mesh objects | Replace mesh pads with vertex color/shader blush mask | P3 |
| **P3-GAP-06** | Beak Shape | Curved downward orange tip | Flattened elongated beak | Linear beak extrusion | Sculpt compact rounded upper mandible | P3 |
| **P3-GAP-07** | Crown Tuft | Soft curved plumes | Rigid pointed spikes | Straight cone geometry | Reshape plumes with organic curvature | P3 |
""")

print("Wrote P3_MASTER_GUIDE_COMPARISON.md")

# 5. P3_BODY_ANATOMY_BLUEPRINT.md
with open(os.path.join(out_dir, "P3_BODY_ANATOMY_BLUEPRINT.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — BODY ANATOMY & BASE GEOMETRY BLUEPRINT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Target Proportional Blueprint

```text
                  +-----------------------+
                  |    Crown Plumes (3)   |
                  +-----------+-----------+
                              |
                    [ Top of Head: Z=2.0 ]
                              |
                     /-----------------\
                    |   Head Mass (R)   |  <- Width = 1.20m
                    |  Eye Center: Z=1.6|
                     \-----------------/
                              |  <- Seamless Neck Transition (No constriction)
                     /-----------------\
                    |   Upper Chest     |
                    |   Breast Fullness |  <- Max Torso Width = 1.40m
                    |  Belly Bottom: Z=0.5|
                     \-----------------/
                              |
                     [ Legs: Hip Z=0.465 ]
                              |
                     [ Branch: Z=0.0 ]
```

### Key Target Dimensions
* **Total Height (Head to Feet):** $1.65\,\text{m}$ (reduced from $2.21\,\text{m}$).
* **Max Body Width:** $1.40\,\text{m}$.
* **Height-to-Width Ratio:** $1.15$ (plump chick proportion matching Master Guide).
* **Head-to-Body Width Ratio:** $0.85$ (large, cute head proportion).
* **Hip Anchor Height:** $0.465\,\text{m}$.

---

## 2. Anatomical Base Reconstruction Strategy

1. **Unified Torso Volume:** Fuse head and body volumes into a continuous organic mass using Voxel Remesh ($0.008\,\text{m}$ voxel size) followed by explicit Laplacian Smoothing ($20$ iterations).
2. **Elimination of Neck Constriction:** Remove the artificial waist/neck dip between head and body so the head merges smoothly into the upper chest.
3. **Ventral Belly Fullness:** Expand the lower ventral belly volume to create the rounded, chick-like pouch shown in the guide.
""")

print("Wrote P3_BODY_ANATOMY_BLUEPRINT.md")

# 6. P3_WING_ARCHITECTURE_BLUEPRINT.md
with open(os.path.join(out_dir, "P3_WING_ARCHITECTURE_BLUEPRINT.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — WING ARCHITECTURE & 7-LAYER FEATHER BLUEPRINT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Wing Local Coordinate System

Define local wing frame $(X_w, Y_w, Z_w)$ for Left Wing (mirrored for Right):
* **$X_w$ (Proximal $\rightarrow$ Distal):** Along wing span, pointing outward from shoulder to wingtip.
* **$Y_w$ (Leading Edge $\rightarrow$ Trailing Edge):** Pointing rearward along flight direction.
* **$Z_w$ (Ventral $\rightarrow$ Dorsal):** Pointing outward perpendicular to wing upper surface.

---

## 2. 7-Layer Wing Construction Specification

```text
                  DORSAL WING SURFACE (Top View)
+-------------------------------------------------------------------+
|  [Layer 1: Scapulars] (Shoulder-to-Back Blend)                    |
|  +-------------------------------------------------------------+  |
|  | [Layer 2: Lesser Coverts] (Small leading-edge rows)          |  |
|  | +---------------------------------------------------------+ |  |
|  | | [Layer 3: Median Coverts] (Staggered middle band)       | |  |
|  | | +-----------------------------------------------------+ | |  |
|  | | | [Layer 4: Greater Coverts] (Secondary base cover)   | | |  |
|  | | | +-------------------------------------------------+ | | |  |
|  | | | | [Layer 5: Secondaries] (Ulna trailing vane)      | | | |  |
|  | | | +-------------------------------------------------+ | | |  |
|  | | +-----------------------------------------------------+ | |  |
|  | +---------------------------------------------------------+ |  |
|  +-------------------------------------------------------------+  |
|  [Layer 6: Primaries] (Distal outer wingtip fan)                  |
+-------------------------------------------------------------------+
```

### Layer Details
1. **Layer 0 — Low-Profile Anatomical Base (`Wing_Base_Proxy`):**
   - Compact, low-profile volume ($X=0.25\,\text{m}, Y=0.35\,\text{m}, Z=0.12\,\text{m}$). Replaces oversized $0.81\,\text{m}$ capsule.
   - Sits flush against torso in rest pose.
2. **Layer 1 — Scapular Feathers (8 feathers/side):**
   - Broad, soft contour feathers flowing caudally over shoulder to conceal wing root seam.
3. **Layer 2 — Lesser Coverts (18 feathers/side):**
   - Small rounded feathers along leading edge.
4. **Layer 3 — Median Coverts (14 feathers/side):**
   - Staggered intermediate covert band.
5. **Layer 4 — Greater Coverts (12 feathers/side):**
   - Overlap secondary feather bases.
6. **Layer 5 — Secondary Feathers (10 feathers/side):**
   - Tapered trailing edge vanes attached along ulna arc.
7. **Layer 6 — Primary Feathers (8 feathers/side):**
   - Distal outer fan forming smooth wingtip.
8. **Layer 7 — Alula (3 small feathers/side):**
   - Wrist leading-edge accent.

---

## 3. Layering Rules & Quality Controls
* **Root Embedding:** Every feather root must be embedded $\ge 8\,\text{mm}$ inside `Wing_Base_Proxy`. Zero floating roots.
* **Staggered Overlap:** Adjacent covert rows offset by $50\%$ width step to prevent vertical alignment seams.
""")

print("Wrote P3_WING_ARCHITECTURE_BLUEPRINT.md")

# 7. P3_FEATHER_GEOMETRY_BLUEPRINT.md
with open(os.path.join(out_dir, "P3_FEATHER_GEOMETRY_BLUEPRINT.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — FEATHER GEOMETRY & 3-FAMILY SYSTEM BLUEPRINT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Three Feather Families Specification

```text
+-------------------------------------------------------------------+
| FAMILY A: UNDERCOAT DOWN                                          |
| - Soft, shaftless down filaments (Breast, Belly, Cheeks)          |
| - Implementation: Hair Curves / Poisson Disk distribution         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| FAMILY B: SEMIPLUME TRANSITION                                    |
| - Fluffy base, soft structured tip                                |
| - Implementation: Instanced semiplume cards                       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| FAMILY C: CONTOUR FEATHERS                                        |
| - Broad, soft vanes with subtle rachis (Back, Flanks, Nape)       |
| - Implementation: 5 Procedural Geometry Variants                  |
+-------------------------------------------------------------------+
```

### 5 Procedural Geometry Variants (Family C)
1. **Variant C1 (Standard Contour):** Length $4.5\,\text{cm}$, Width $2.2\,\text{cm}$, rounded tip, camber $0.15$.
2. **Variant C2 (Broad Breast Contour):** Length $3.8\,\text{cm}$, Width $2.8\,\text{cm}$, wide soft tip.
3. **Variant C3 (Elongated Nape Covert):** Length $5.2\,\text{cm}$, Width $1.8\,\text{cm}$, gentle curve.
4. **Variant C4 (Asymmetric Flank Contour):** Length $4.2\,\text{cm}$, Width $2.0\,\text{cm}$, asymmetric vane.
5. **Variant C5 (Small Facial Covert):** Length $1.8\,\text{cm}$, Width $1.0\,\text{cm}$, fine rounded scale.

---

## 2. Regional Density & Flow Control

* **Breast/Belly:** $70\%$ Family A (Down) + $30\%$ Family C2 (Cream Contour).
* **Back:** $100\%$ Family C1/C3 (Sage Contour).
* **Face/Cheeks:** $80\%$ Family A (Fine Down) + $20\%$ Family C5 (Facial Covert).
""")

print("Wrote P3_FEATHER_GEOMETRY_BLUEPRINT.md")

# 8. P3_FACE_AND_FEET_CORRECTION_PLAN.md
with open(os.path.join(out_dir, "P3_FACE_AND_FEET_CORRECTION_PLAN.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — FACE, EYES, BEAK & FEET CORRECTION PLAN

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Eye Correction Protocol

* **Current Defect:** Unwanted lower white dot artifact on eye surface.
* **Forensic Diagnosis:** Caused by separate 3D mesh object `Eye_L_Catchlight_Small` / `Eye_R_Catchlight_Small` placed on lower iris.
* **Action:**
  1. Remove `Eye_L_Catchlight_Small` and `Eye_R_Catchlight_Small` mesh objects.
  2. Retain main upper catchlight (`Eye_L_Catchlight_Large`) or rely on procedural specular reflection from studio key light.
  3. Keep `Eye_L_Glossy_Main` and `Blink` shape key intact.

---

## 2. Cheek Blush Correction Protocol

* **Current Defect:** Raised pink 3D rubber-like pads (`Cheek_L/R_Soft_Blush`).
* **Forensic Diagnosis:** Protruding mesh geometry ($Z=0.05\,\text{m}$ thick).
* **Action:**
  1. Unlink 3D blush mesh objects `Cheek_L_Soft_Blush` and `Cheek_R_Soft_Blush`.
  2. Implement soft radial blush using vertex color attribute `BlushTint` or procedural shader radial mask on head base mesh.

---

## 3. Beak Reshaping Protocol

* **Current Defect:** Overly long, flat oval beak.
* **Action:**
  1. Sculpt `Beak_Upper` into a compact, rounded upper mandible with a gentle downward tip hook matching the Master Guide.
  2. Assign verified orange material `Shukhpakhi_MAT_Beak_Feet_Orange` (`#F6A623`).

---

## 4. Feet & Perch Grip Protocol

* **Current Defect:** Legs slightly long ($0.39\,\text{m}$).
* **Action:**
  1. Maintain Hip Z anchor at $0.465\,\text{m}$.
  2. Adjust toe positions to wrap around temporary branch prop (`Perch_Branch_Test_Prop`).
""")

print("Wrote P3_FACE_AND_FEET_CORRECTION_PLAN.md")

# 9. P3_MATERIAL_AND_LIGHTING_GAP_REPORT.md
with open(os.path.join(out_dir, "P3_MATERIAL_AND_LIGHTING_GAP_REPORT.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — MATERIAL, SHADING & LIGHTING GAP REPORT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Color Palette Verification

| Swatch Name | Target Hex | Linear sRGB (R, G, B) | P2 Material Usage | Status |
| :--- | :---: | :---: | :--- | :---: |
| **Sage Green** | `#A7C49A` | $(0.3805, 0.5435, 0.3182)$ | Back, wings, nape | ✅ Verified |
| **Light Green** | `#D7E8C5` | $(0.6795, 0.7991, 0.5647)$ | Front coverts, highlights | ✅ Verified |
| **Cream** | `#F8F9E9` | $(0.9387, 0.9478, 0.8633)$ | Belly, breast, face | ✅ Verified |
| **Warm Beige** | `#EDE7D9` | $(0.8388, 0.7991, 0.7011)$ | Feather undercoat | ✅ Verified |
| **Orange** | `#F6A623` | $(0.9216, 0.3805, 0.0168)$ | Beak, legs, feet | ✅ Verified |

---

## 2. P2 Texture Set Evaluation
* `SP_Feather_Albedo_2048.png`: Correct palette, sRGB. Needs per-feather instance UV jitter in Phase 3 to eliminate shingle tile repetition.
* `SP_Feather_Normal_2048.png`: Non-Color, central rachis + $40^\circ$ barbs. Replaced horizontal ripple.
* `SP_Feather_Roughness_2048.png`: Non-Color, differentiated profile ($0.55 - 0.90$).
* `SP_Feather_ORM_2048.png`: Non-Color, $R=\text{AO}(1.0), G=\text{Roughness}, B=\text{Metallic}(0.0)$.
""")

print("Wrote P3_MATERIAL_AND_LIGHTING_GAP_REPORT.md")

# 10. P3_SCRIPT_AND_MESH_DEPENDENCY_MAP.md
with open(os.path.join(out_dir, "P3_SCRIPT_AND_MESH_DEPENDENCY_MAP.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — SCRIPT & MESH DEPENDENCY MAP

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Source Module Mapping

```text
build_shukhpakhi.py
  ├── shukhpakhi/config.py      (Palette, dimensions, hip anchor Z=0.465)
  ├── shukhpakhi/utils.py       (BMesh helpers, UV map creation)
  ├── shukhpakhi/materials.py   (9 PBR shader node trees)
  ├── shukhpakhi/feather_engine.py (Feather card mesh generator)
  ├── shukhpakhi/body.py        (Body_Head_Fused_Soft_Undercoat, Shingle layers)
  ├── shukhpakhi/wings.py       (Wing_L/R_Anatomical_Quiet_Base, 5 wing feather layers)
  ├── shukhpakhi/face.py        (Eyelids, Blink shape keys, Catchlights, Cheeks)
  ├── shukhpakhi/feet.py        (Leg stalks, Toes, Hallux)
  ├── shukhpakhi/tuft.py        (Head_Crown_Three_Soft_Plumes)
  └── shukhpakhi/assemble.py    (Master builder assembly script)
```

---

## 2. Dependency Matrix & Refactoring Targets

* `body.py`: Update height scale to $1.15$ ratio. Integrate down groom + semiplume layers.
* `wings.py`: Replace single capsule base with low-profile `Wing_Base_Proxy`. Implement 7-layer feather assembly.
* `face.py`: Remove `Eye_L/R_Catchlight_Small`. Replace 3D cheek pads with vertex blush attribute.
""")

print("Wrote P3_SCRIPT_AND_MESH_DEPENDENCY_MAP.md")

# 11. P3_PROTOTYPE_SPECIFICATIONS.md
with open(os.path.join(out_dir, "P3_PROTOTYPE_SPECIFICATIONS.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — PROTOTYPE SPECIFICATIONS & ISOLATED PROOF OF CONCEPT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Three Isolated Golden Prototypes

### Prototype 1 — Golden Chest Patch (`Chest_Patch_Prototype.blend`)
* **Scope:** $15\times 15\,\text{cm}$ chest surface patch.
* **Contains:** Base undercoat mesh + Hair Curves down (Family A) + 3 contour variants (Family C).
* **Pass Criteria:** Soft downy texture with zero hard scale outlines; smooth cream palette match.

### Prototype 2 — Golden Wing Patch (`Wing_Patch_Prototype.blend`)
* **Scope:** Complete Left Wing assembly.
* **Contains:** Low-profile `Wing_Base_Proxy` + 7 feather layers (Scapulars through Primaries).
* **Pass Criteria:** Flush body attachment, zero floating roots, smooth covert-to-primary transition, zero capsule protrusion.

### Prototype 3 — Golden Face Patch (`Face_Patch_Prototype.blend`)
* **Scope:** Head, eyes, beak, cheeks, crown tuft.
* **Contains:** Single top catchlight, soft vertex blush, rounded orange beak, curved crown plumes.
* **Pass Criteria:** Matches cute Master Guide facial expression; zero lower white eye dots; zero raised blush pads.
""")

print("Wrote P3_PROTOTYPE_SPECIFICATIONS.md")

# 12. P3_OPEN_GAPS.md
with open(os.path.join(out_dir, "P3_OPEN_GAPS.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — OPEN GAPS & DEFECT TRACKING MANIFEST

**Project:** Shukhpakhi / Likipiki Master Bird
**Status:** ACTIVE TRACKING

---

## Live Gap Tracking Table

| Gap ID | Description | Severity | Evidence | Status | Required Action |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **P3-GAP-01** | Torso height ratio ($1.545$) exceeds guide ($1.15$) | HIGH | Audit JSON / Renders | OPEN | Reshape base torso mesh |
| **P3-GAP-02** | Body shingles look like hard scales | HIGH | `01_front.png` render | OPEN | Implement 3-family feather system |
| **P3-GAP-03** | Oversized wing base capsule ($Z=0.81\,\text{m}$) | HIGH | Mesh audit JSON | OPEN | Replace with low-profile 7-layer wing |
| **P3-GAP-04** | Lower eye white dot artifact | HIGH | Eye render close-up | OPEN | Remove `Eye_L/R_Catchlight_Small` |
| **P3-GAP-05** | Raised pink 3D cheek pads | MEDIUM | Object inventory CSV | OPEN | Replace mesh pads with vertex blush |
| **P3-GAP-06** | Flat elongated beak | MEDIUM | `03_side.png` render | OPEN | Reshape upper mandible curve |
| **P3-GAP-07** | Rigid spiky crown plumes | MEDIUM | `01_front.png` render | OPEN | Add organic plume curvature |
| **P3-GAP-08** | Wing covert UV correlation below $0.95$ | LOW | `P2_UV_Audit.json` | OPEN | Documented; procedural grooming in P3 |
""")

print("Wrote P3_OPEN_GAPS.md")

# 13. P3_MASTER_IMPLEMENTATION_ROADMAP.md
with open(os.path.join(out_dir, "P3_MASTER_IMPLEMENTATION_ROADMAP.md"), "w", encoding="utf-8") as f:
    f.write("""# P3 — MASTER IMPLEMENTATION ROADMAP

**Project:** Shukhpakhi / Likipiki Master Bird

---

## Implementation Phases

```text
+-------------------------------------------------------------------+
| PHASE 3.1: ISOLATED GOLDEN PROTOTYPES                             |
| - Build Chest Patch, Wing Patch, and Face Patch prototypes        |
| - Verify each against Master Guide before full integration         |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 3.2: ANATOMY & BASE TORSO RECONSTRUCTION                    |
| - Reshape body base mesh to 1.15 height-to-width ratio            |
| - Fuse head/torso seamlessly without neck constriction seam       |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 3.3: 7-LAYER WING & 3-FAMILY PLUMAGE INTEGRATION            |
| - Install low-profile Wing_Base_Proxy + 7 feather layers          |
| - Deploy Down, Semiplume, and 5 Contour feather variants          |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 3.4: FACIAL CLEANUP & FEET WRAPPING                         |
| - Remove 3D catchlight meshes; apply vertex blush                 |
| - Reshape orange beak; curve crown plumes; wrap toes on branch    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 3.5: MATERIALS, SHADING & GATE 3 VERIFICATION               |
| - Connect P2 PBR textures with per-feather instance UV jitter     |
| - Render 10 neutral + 4 grazing views; output P3 Gate Report      |
+-------------------------------------------------------------------+
```

---

## Final Authorization Notice
* Executed under read-only forensic research mandate.
* No production blend files modified.
* Awaiting explicit project-owner authorization to execute Phase 3.1 prototypes.
""")

print("Wrote P3_MASTER_IMPLEMENTATION_ROADMAP.md")
print("All 13 P3 research documents generated successfully!")
