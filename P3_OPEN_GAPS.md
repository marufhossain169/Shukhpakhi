# P3 — OPEN GAPS & DEFECT TRACKING MANIFEST

**Project:** Shukhpakhi / Likipiki Master Bird
**Status:** ACTIVE TRACKING

---

## Live Gap Tracking Table

| Gap ID | Description | Severity | Evidence | Status | Required Action |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **P3-GAP-01** | Torso height ratio ($1.545$) exceeds guide ($1.15$) | HIGH | Audit JSON / Renders | OPEN | Reshape base torso mesh |
| **P3-GAP-02** | Body shingles look like hard scales | HIGH | `01_front.png` render | OPEN | Implement 3-family feather system |
| **P3-GAP-03** | Oversized wing base capsule ($Z=0.81\,	ext{m}$) | HIGH | Mesh audit JSON | OPEN | Replace with low-profile 7-layer wing |
| **P3-GAP-04** | Lower eye white dot artifact | HIGH | Eye render close-up | OPEN | Remove `Eye_L/R_Catchlight_Small` |
| **P3-GAP-05** | Raised pink 3D cheek pads | MEDIUM | Object inventory CSV | OPEN | Replace mesh pads with vertex blush |
| **P3-GAP-06** | Flat elongated beak | MEDIUM | `03_side.png` render | OPEN | Reshape upper mandible curve |
| **P3-GAP-07** | Rigid spiky crown plumes | MEDIUM | `01_front.png` render | OPEN | Add organic plume curvature |
| **P3-GAP-08** | Wing covert UV correlation below $0.95$ | LOW | `P2_UV_Audit.json` | OPEN | Documented; procedural grooming in P3 |
