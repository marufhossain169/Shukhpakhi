# P3 — MASTER GUIDE COMPARISON & VISUAL GAP ANALYSIS

**Project:** Shukhpakhi / Likipiki Master Bird
**Visual Authority:** `reference/Likipiki_Master_Bird_Design_Guide.png`

---

## 1. Landmark & Proportional Audit

| Region | Master Guide Landmark | Current Model Render | Visual Discrepancy | Gap Severity |
| :--- | :--- | :--- | :--- | :---: |
| **Overall Silhouette** | Compact, round, chick-like ($H/W pprox 1.15$) | Elongated egg shape ($H/W pprox 1.55$) | Body is vertically stretched by ~35% | **HIGH** |
| **Head & Torso Seam** | Fused, continuous volume | Visually separated head mass | Visible neck indentation line | **HIGH** |
| **Chest & Belly** | Soft cream downy fullness | Scaled shingle cards | Look like hard armor scales | **HIGH** |
| **Wings** | Soft, compact sage wing flush to body | Oversized capsule pushing feathers out | Wing looks like a separate bulbous mass | **HIGH** |
| **Wing Layering** | Continuous covert rows into soft primaries | Sparse, separated feather plates | Visible gaps and unnatural feather angles | **HIGH** |
| **Eyes** | Large glossy black with single crisp top highlight | Multiple white dots (upper + lower) | Lower white dot ruins eye expression | **HIGH** |
| **Cheeks** | Soft, blended pink blush | Raised 3D pink pads | Look like attached rubber patches | **MEDIUM** |
| **Beak** | Short, curved orange beak (#F6A623) | Overly flat/oval orange beak | Lacks subtle downward hook | **MEDIUM** |
| **Crown Tuft** | Three soft, flowing plumes | Three rigid pointed spikes | Spiky appearance | **MEDIUM** |
| **Feet & Legs** | Short orange chick feet wrapping branch | Long stalk legs, yellow-orange tint | Legs too long ($0.39\,	ext{m}$) | **MEDIUM** |

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
