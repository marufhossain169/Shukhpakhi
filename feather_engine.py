"""Reusable actual feather-mesh generator (not a wavy UV sphere approximation)."""
import math
from mathutils import Vector
from . import utils

COLLECTION = "Shukhpakhi_Feathers"


def _safe_basis(direction, normal):
    d = Vector(direction).normalized()
    n = Vector(normal).normalized()
    side = d.cross(n)
    if side.length < 1e-5:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    n = side.cross(d).normalized()
    return d, side, n


def _one_feather(root, direction, normal, length, width, height, sides=6, rows=7, offset=0.0):
    root = Vector(root)
    d, side, n = _safe_basis(direction, normal)
    verts, faces = [], []
    for ri in range(rows):
        t = ri / (rows - 1)
        # Narrow root, rounded shoulder, soft pointed/rounded tip.
        profile = max(0.0, math.sin(math.pi * (0.04 + 0.92 * t))) ** 0.72
        profile *= (1.0 - 0.18 * t)
        for ci in range(sides):
            u = -1.0 + 2.0 * ci / (sides - 1)
            w = width * profile * u
            camber = height * profile * (1.0 - abs(u) ** 1.4) * (0.55 + 0.45 * math.sin(math.pi * t))
            # Slight backward sweep and gentle curvature are built into the feather mesh.
            p = root + d * (length * t) + side * w + n * (offset + camber)
            p += side * (0.10 * width * math.sin(math.pi * t) * (t - 0.35))
            verts.append(tuple(p))
    for r in range(rows - 1):
        for c in range(sides - 1):
            a = r * sides + c
            faces.append((a, a + 1, a + sides + 1, a + sides))
    return verts, faces


def create_feather_cluster(name, specs, material, collection=COLLECTION,
                           thickness=0.0022, bevel=0.0010):
    verts, faces = [], []
    for spec in specs:
        fv, ff = _one_feather(
            spec["root"], spec["direction"], spec["normal"],
            spec["length"], spec["width"], spec.get("height", 0.004),
            sides=spec.get("sides", 7), rows=spec.get("rows", 8),
            offset=spec.get("offset", 0.002)
        )
        base = len(verts)
        verts.extend(fv)
        faces.extend([tuple(base + i for i in face) for face in ff])
    if not verts:
        return None
    obj = utils.create_mesh_object(name, verts, faces, collection, material, smooth=True)
    if thickness > 0:
        utils.add_bevel_and_solidify(obj, thickness=thickness, bevel=bevel)
    return obj


def ellipsoid_surface(center, radii, unit_direction):
    """Returns exact point and outward normal on an axis-aligned ellipsoid."""
    c = Vector(center)
    rx, ry, rz = radii
    q = Vector(unit_direction).normalized()
    point = c + Vector((q.x * rx, q.y * ry, q.z * rz))
    normal = Vector((q.x / rx, q.y / ry, q.z / rz)).normalized()
    return point, normal


def tangent_direction(preferred, normal):
    v = Vector(preferred)
    n = Vector(normal).normalized()
    t = v - n * v.dot(n)
    if t.length < 1e-5:
        t = Vector((1, 0, 0)) - n * n.x
    return t.normalized()
