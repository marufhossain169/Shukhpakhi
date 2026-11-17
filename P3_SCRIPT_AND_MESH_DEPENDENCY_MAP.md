# P3 — SCRIPT & MESH DEPENDENCY MAP

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
