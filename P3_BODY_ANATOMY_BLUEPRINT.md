# P3 — BODY ANATOMY & BASE GEOMETRY BLUEPRINT

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
                     /-----------------                    |   Head Mass (R)   |  <- Width = 1.20m
                    |  Eye Center: Z=1.6|
                     \-----------------/
                              |  <- Seamless Neck Transition (No constriction)
                     /-----------------                    |   Upper Chest     |
                    |   Breast Fullness |  <- Max Torso Width = 1.40m
                    |  Belly Bottom: Z=0.5|
                     \-----------------/
                              |
                     [ Legs: Hip Z=0.465 ]
                              |
                     [ Branch: Z=0.0 ]
```

### Key Target Dimensions
* **Total Height (Head to Feet):** $1.65\,	ext{m}$ (reduced from $2.21\,	ext{m}$).
* **Max Body Width:** $1.40\,	ext{m}$.
* **Height-to-Width Ratio:** $1.15$ (plump chick proportion matching Master Guide).
* **Head-to-Body Width Ratio:** $0.85$ (large, cute head proportion).
* **Hip Anchor Height:** $0.465\,	ext{m}$.

---

## 2. Anatomical Base Reconstruction Strategy

1. **Unified Torso Volume:** Fuse head and body volumes into a continuous organic mass using Voxel Remesh ($0.008\,	ext{m}$ voxel size) followed by explicit Laplacian Smoothing ($20$ iterations).
2. **Elimination of Neck Constriction:** Remove the artificial waist/neck dip between head and body so the head merges smoothly into the upper chest.
3. **Ventral Belly Fullness:** Expand the lower ventral belly volume to create the rounded, chick-like pouch shown in the guide.
