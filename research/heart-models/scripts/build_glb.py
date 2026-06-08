"""Build a clean, grouped, web-ready segmented heart GLB from BodyParts3D.
Trims vessels to the heart vicinity, groups parts into educational categories,
smooths normals, assigns anatomical colors. Each category = one named mesh so the
web viewer can highlight it. Heart muscle (wall) kept as one piece (dataset limit)."""
import zipfile, numpy as np, trimesh

ZIP = "/work/temp/bp3d/bp3d_obj_99.zip"
OUT = "/work/temp/bp3d/heart_web.glb"

# category -> (list of FMA ids, color RGB, slug)
GROUPS = {
    "Myocardium":          (["FMA7274"], (181, 88, 78), "myocardium"),
    "Aorta":               (["FMA3736","FMA3768"], (197, 58, 50), "aorta"),
    "Pulmonary trunk":     (["FMA66326"], (74, 105, 196), "pulm_trunk"),
    "Superior vena cava":  (["FMA4720"], (88, 130, 190), "svc"),
    "Inferior vena cava":  (["FMA10951"], (88, 130, 190), "ivc"),
    "Coronary arteries":   (["FMA3802","FMA4685","FMA3895","FMA3818"], (199, 42, 42), "cor_art"),
    "Coronary veins":      (["FMA4706","FMA4707","FMA4713"], (64, 92, 176), "cor_vein"),
    "Heart valves":        (["FMA7234","FMA7235","FMA7246"], (226, 214, 150), "valves"),
}

def entry_for(zf, fid):
    for n in zf.namelist():
        if n.replace("\\","/").split("/")[-1].lower() == f"{fid.lower()}.obj":
            return n
    return None

def load(zf, fid):
    e = entry_for(zf, fid)
    if not e: return None
    p = f"/work/temp/bp3d/{fid}.obj"
    open(p,"wb").write(zf.read(e))
    m = trimesh.load(p, process=True)
    if isinstance(m, trimesh.Scene): m = m.dump(concatenate=True)
    return m

def clip(mesh, lo, hi):
    v = mesh.vertices
    inside = np.all((v>=lo)&(v<=hi), axis=1)
    fmask = inside[mesh.faces].all(axis=1)
    if fmask.sum() < 4: return None
    m = mesh.submesh([np.where(fmask)[0]], append=True)
    # drop tiny disconnected shards left by clipping
    comps = m.split(only_watertight=False)
    comps = [c for c in comps if len(c.faces) >= 60]
    if not comps:
        return m
    return trimesh.util.concatenate(comps)

def main():
    zf = zipfile.ZipFile(ZIP)
    wall = load(zf, "FMA7274")
    lo = wall.bounds[0] - 6
    hi = wall.bounds[1] + 6
    hi[2] = wall.bounds[1][2] + 24  # short superior stumps
    scene = trimesh.Scene()
    for name,(ids,rgb,slug) in GROUPS.items():
        parts=[]
        for fid in ids:
            m = load(zf, fid)
            if m is None: continue
            if name != "Myocardium":
                m = clip(m, lo, hi)
            if m is None or len(m.faces)==0: continue
            parts.append(m)
        if not parts: continue
        merged = trimesh.util.concatenate(parts) if len(parts)>1 else parts[0]
        try: merged.fix_normals()
        except Exception: pass
        merged.visual = trimesh.visual.ColorVisuals(mesh=merged,
            face_colors=np.tile(np.array([*rgb,255],np.uint8),(len(merged.faces),1)))
        scene.add_geometry(merged, geom_name=name, node_name=name)
        print(f"{name:22s} {len(merged.vertices):7d}v {len(merged.faces):7d}f")
    scene.export(OUT)
    import os
    print("WROTE", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    main()
