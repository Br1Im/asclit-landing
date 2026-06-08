"""Assemble a segmented heart GLB from BodyParts3D OBJ parts and render clean views."""
import os, sys, zipfile, glob, json
import numpy as np
import trimesh

ZIP = "/work/temp/bp3d/bp3d_obj_99.zip"
WORK = "/work/temp/bp3d/parts"
OUT_GLB = "/work/temp/bp3d/heart_segmented.glb"
os.makedirs(WORK, exist_ok=True)

# id -> (display name, color RGBA) ; grouped colors
PARTS = {
    # muscle / chambers
    "FMA7274": ("Wall of heart", (200,120,110)),
    "FMA9462": ("Myocardium", (190,110,100)),
    "FMA7098": ("Right ventricle", (210,140,120)),
    "FMA7101": ("Left ventricle", (180,90,80)),
    "FMA7096": ("Right atrium", (225,160,140)),
    "FMA7097": ("Left atrium", (200,120,110)),
    "FMA7133": ("Interventricular septum", (170,100,95)),
    # great vessels
    "FMA3736": ("Ascending aorta", (210,70,60)),
    "FMA3768": ("Arch of aorta", (210,70,60)),
    "FMA66326": ("Pulmonary trunk", (90,110,200)),
    "FMA4720": ("Superior vena cava", (80,120,190)),
    "FMA10951": ("Inferior vena cava", (80,120,190)),
    # coronary arteries (bright red)
    "FMA50039": ("Right coronary artery", (200,40,40)),
    "FMA50040": ("Left coronary artery", (200,40,40)),
    "FMA3862": ("Ant. interventricular branch (LAD)", (200,40,40)),
    "FMA3895": ("Circumflex branch", (200,40,40)),
    "FMA3818": ("Marginal branch", (200,40,40)),
    # coronary veins (blue)
    "FMA4706": ("Coronary sinus", (70,90,180)),
    "FMA4707": ("Great cardiac vein", (70,90,180)),
    "FMA4713": ("Middle cardiac vein", (70,90,180)),
    # valves
    "FMA7234": ("Tricuspid valve", (230,220,150)),
    "FMA7235": ("Mitral valve", (230,220,150)),
    "FMA7246": ("Pulmonary valve", (230,220,150)),
}

def find_obj(zf, fid):
    # match names like '.../FMA7274.obj' possibly nested
    for n in zf.namelist():
        base = os.path.basename(n).lower()
        if base == f"{fid.lower()}.obj":
            return n
    return None

def main():
    zf = zipfile.ZipFile(ZIP)
    names = zf.namelist()
    print("zip entries:", len(names), "sample:", names[:3])
    scene = trimesh.Scene()
    found, missing = [], []
    for fid, (label, rgb) in PARTS.items():
        entry = find_obj(zf, fid)
        if not entry:
            missing.append(fid); continue
        data = zf.read(entry)
        p = os.path.join(WORK, f"{fid}.obj")
        open(p, "wb").write(data)
        m = trimesh.load(p, process=False)
        if isinstance(m, trimesh.Scene):
            m = m.dump(concatenate=True)
        color = np.array([*rgb, 255], dtype=np.uint8)
        m.visual = trimesh.visual.ColorVisuals(mesh=m, face_colors=np.tile(color, (len(m.faces),1)))
        scene.add_geometry(m, geom_name=label, node_name=label)
        found.append((fid, label, len(m.vertices), len(m.faces)))
    print("FOUND", len(found), "MISSING", missing)
    for f in found: print("  ", f)
    if not found:
        print("NO PARTS FOUND - check filename convention:", names[:20]); return
    scene.export(OUT_GLB)
    print("exported", OUT_GLB, os.path.getsize(OUT_GLB), "bytes")

if __name__ == "__main__":
    main()
