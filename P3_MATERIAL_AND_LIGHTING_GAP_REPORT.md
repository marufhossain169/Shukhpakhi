# P3 — MATERIAL, SHADING & LIGHTING GAP REPORT

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
* `SP_Feather_ORM_2048.png`: Non-Color, $R=	ext{AO}(1.0), G=	ext{Roughness}, B=	ext{Metallic}(0.0)$.
