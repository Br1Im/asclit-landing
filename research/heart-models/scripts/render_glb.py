import os
os.environ["PYOPENGL_PLATFORM"]="egl"
import numpy as np, trimesh, pyrender
from PIL import Image
GLB="/work/temp/asclit-landing/heart_new.glb"
OUT="/work/temp/heartgen/glbshots"; os.makedirs(OUT,exist_ok=True)
tm=trimesh.load(GLB, process=False)
scene=pyrender.Scene.from_trimesh_scene(tm, bg_color=[255,255,255,255], ambient_light=[0.5,0.5,0.5]) if isinstance(tm,trimesh.Scene) else None
# get bounds/center
if isinstance(tm,trimesh.Scene):
    allv=np.vstack([g.vertices for g in tm.geometry.values()])
else:
    allv=tm.vertices
center=(allv.min(0)+allv.max(0))/2
radius=np.linalg.norm(allv-center,axis=1).max()
print("center",center,"radius",radius,"bounds",allv.min(0),allv.max(0))
# rebuild scene centered
pscene=pyrender.Scene(bg_color=[255,255,255,255], ambient_light=[0.55,0.55,0.55])
T=np.eye(4); T[:3,3]=-center
if isinstance(tm,trimesh.Scene):
    for name,g in tm.geometry.items():
        m=pyrender.Mesh.from_trimesh(g, smooth=True)
        pscene.add(m, pose=T)
else:
    pscene.add(pyrender.Mesh.from_trimesh(tm,smooth=True),pose=T)
cam=pyrender.PerspectiveCamera(yfov=np.pi/5.0)
d=radius/np.tan(np.pi/10)*1.3
# figure vertical axis: assume Y up (glTF convention)
UP=np.array([0,1.0,0])
import math
def eye_at(angle_deg, elev=0.12):
    a=math.radians(angle_deg)
    return np.array([math.sin(a)*d, elev*d, math.cos(a)*d])
def look_at(eye,up=UP,target=np.zeros(3)):
    eye=np.array(eye,float);f=target-eye;f/=np.linalg.norm(f)
    s=np.cross(f,up);s/=np.linalg.norm(s);u=np.cross(s,f)
    M=np.eye(4);M[:3,0]=s;M[:3,1]=u;M[:3,2]=-f;M[:3,3]=eye;return M
r=pyrender.OffscreenRenderer(900,1050)
angles={"0_front":0,"1_frontright":45,"2_right":90,"3_back":180,"4_left":270,"5_frontleft":315}
paths=[]
for name,ang in angles.items():
    for n in list(pscene.nodes):
        if n.camera or n.light: pscene.remove_node(n)
    eye=eye_at(ang); pose=look_at(eye)
    pscene.add(cam,pose=pose)
    pscene.add(pyrender.DirectionalLight(color=[255,255,255],intensity=3.0),pose=pose)
    kp=look_at(eye_at(ang+40,0.5)); pscene.add(pyrender.DirectionalLight(intensity=2.0),pose=kp)
    color,_=r.render(pscene); p=f"{OUT}/{name}.png"; Image.fromarray(color).save(p); paths.append(p); print("saved",p)
r.delete()
imgs=[Image.open(p) for p in paths]; w,h=imgs[0].size
sheet=Image.new("RGB",(w*3,h*2),(255,255,255))
for i,im in enumerate(imgs): sheet.paste(im,((i%3)*w,(i//3)*h))
sheet.save(f"{OUT}/contact.png"); print("contact ok")
