# P3 — FACE, EYES, BEAK & FEET CORRECTION PLAN

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
* **Forensic Diagnosis:** Protruding mesh geometry ($Z=0.05\,	ext{m}$ thick).
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

* **Current Defect:** Legs slightly long ($0.39\,	ext{m}$).
* **Action:**
  1. Maintain Hip Z anchor at $0.465\,	ext{m}$.
  2. Adjust toe positions to wrap around temporary branch prop (`Perch_Branch_Test_Prop`).
