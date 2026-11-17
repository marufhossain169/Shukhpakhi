import json

d = json.load(open('Shukhpakhi_Project/02_AUDIT_OUTPUT/p3_forensic_mesh_audit.json'))
print(f"Total Objects: {len(d['objects'])}")
print("="*100)
for o in d['objects']:
    if o['type'] == 'MESH':
        dims = f"({o['dimensions'][0]:.2f}, {o['dimensions'][1]:.2f}, {o['dimensions'][2]:.2f})"
        mats = ", ".join(o['materials']) if o['materials'] else "None"
        print(f"{o['name']:42s} | V:{o['verts']:6d} | F:{o['faces']:6d} | Dim:{dims:22s} | Mat:{mats}")
