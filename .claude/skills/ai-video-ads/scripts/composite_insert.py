"""composite_insert.py BASE.mp4 TRACK.npy INSERT.mp4 OUT.mp4 [--mirror] [--crop x,y,w,h] [--audio SRC|silent]
Pastes INSERT frames into tracked boxes of BASE (frame-matched), colour/contrast-matched to the original region,
2px feather. Use for screens (self-view, TV, monitor). --mirror for self-views."""
import sys, subprocess, json, numpy as np
from PIL import Image, ImageFilter
a=sys.argv; base,trk,ins,out=a[1:5]; mirror='--mirror' in a
crop=tuple(map(int,a[a.index('--crop')+1].split(','))) if '--crop' in a else None
audio=a[a.index('--audio')+1] if '--audio' in a else base
def probe(f):
    s=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','json',f],capture_output=True,text=True).stdout)['streams'][0]
    return s['width'],s['height'],s['r_frame_rate']
def dec(f,w,h): return np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout,np.uint8).reshape(-1,h,w,3)
W,H,fps=probe(base); iw,ih,_=probe(ins); F=dec(base,W,H).copy(); C=dec(ins,iw,ih); R=np.load(trk)
for i in range(len(F)):
    x,y,w,h=[int(round(v)) for v in R[i][:4]]
    im=Image.fromarray(C[min(i,len(C)-1)])
    if crop: im=im.crop((crop[0],crop[1],crop[0]+crop[2],crop[1]+crop[3]))
    if mirror: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    c=np.asarray(im.resize((w,h),Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6)),np.float32)
    ref=F[i,y:y+h,x:x+w].astype(np.float32)
    c=(c-c.mean((0,1)))/(c.std((0,1))+1e-6)*ref.std((0,1))+ref.mean((0,1))
    m=np.ones((h,w))
    for k in range(2): v=(k+1)/3; m[k,:]*=v; m[-k-1,:]*=v; m[:,k]*=v; m[:,-k-1]*=v
    F[i,y:y+h,x:x+w]=(c*m[...,None]+ref*(1-m[...,None])).clip(0,255).astype(np.uint8)
cmd=['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fps,'-i','-']
cmd+=(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo'] if audio=='silent' else ['-i',audio])
cmd+=['-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','aac','-shortest',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE); p.stdin.write(F.tobytes()); p.stdin.close(); p.wait(); print(out)
