# P3 — FEATHER GEOMETRY & 3-FAMILY SYSTEM BLUEPRINT

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
1. **Variant C1 (Standard Contour):** Length $4.5\,	ext{cm}$, Width $2.2\,	ext{cm}$, rounded tip, camber $0.15$.
2. **Variant C2 (Broad Breast Contour):** Length $3.8\,	ext{cm}$, Width $2.8\,	ext{cm}$, wide soft tip.
3. **Variant C3 (Elongated Nape Covert):** Length $5.2\,	ext{cm}$, Width $1.8\,	ext{cm}$, gentle curve.
4. **Variant C4 (Asymmetric Flank Contour):** Length $4.2\,	ext{cm}$, Width $2.0\,	ext{cm}$, asymmetric vane.
5. **Variant C5 (Small Facial Covert):** Length $1.8\,	ext{cm}$, Width $1.0\,	ext{cm}$, fine rounded scale.

---

## 2. Regional Density & Flow Control

* **Breast/Belly:** $70\%$ Family A (Down) + $30\%$ Family C2 (Cream Contour).
* **Back:** $100\%$ Family C1/C3 (Sage Contour).
* **Face/Cheeks:** $80\%$ Family A (Fine Down) + $20\%$ Family C5 (Facial Covert).
