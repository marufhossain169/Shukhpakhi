# P3 — WING ARCHITECTURE & 7-LAYER FEATHER BLUEPRINT

**Project:** Shukhpakhi / Likipiki Master Bird

---

## 1. Wing Local Coordinate System

Define local wing frame $(X_w, Y_w, Z_w)$ for Left Wing (mirrored for Right):
* **$X_w$ (Proximal $ightarrow$ Distal):** Along wing span, pointing outward from shoulder to wingtip.
* **$Y_w$ (Leading Edge $ightarrow$ Trailing Edge):** Pointing rearward along flight direction.
* **$Z_w$ (Ventral $ightarrow$ Dorsal):** Pointing outward perpendicular to wing upper surface.

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
   - Compact, low-profile volume ($X=0.25\,	ext{m}, Y=0.35\,	ext{m}, Z=0.12\,	ext{m}$). Replaces oversized $0.81\,	ext{m}$ capsule.
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
* **Root Embedding:** Every feather root must be embedded $\ge 8\,	ext{mm}$ inside `Wing_Base_Proxy`. Zero floating roots.
* **Staggered Overlap:** Adjacent covert rows offset by $50\%$ width step to prevent vertical alignment seams.
