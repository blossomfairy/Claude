"""track.py CLIP X Y W H OUT.npy : multi-scale template tracking of a region (from frame 0) across a clip.
Writes per-frame (x,y,w,h,err) smoothed, plus OUT.png overlay at 5 frames for visual verification."""
import sys, subprocess, json, numpy as np
from PIL import Image, ImageDraw
clip=sys.argv[1]; x0,y0,w0,h0=map(int,sys.argv[2:6]); out=sys.argv[6]
info=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',clip],capture_output=True,text=True).stdout)['streams'][0]
W,H=info['width'],info['height']
F=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',clip,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout,np.uint8).reshape(-1,H,W,3)
tpl=Image.fromarray(F[0][y0:y0+h0,x0:x0+w0]); cx,cy,s=x0,y0,1.0; res=[]
for f in F:
    g=f.astype(np.float32); best=None
    for sc in s+np.arange(-0.04,0.061,0.01):
        tw,th=round(w0*sc),round(h0*sc); t=np.asarray(tpl.resize((tw,th),Image.BILINEAR),np.float32)
        for dy in range(-8,9):
            for dx in range(-8,9):
                xx,yy=cx+dx,cy+dy
                if xx<0 or yy<0 or xx+tw>W or yy+th>H: continue
                d=((g[yy:yy+th,xx:xx+tw]-t)**2).mean()
                if best is None or d<best[0]: best=(d,xx,yy,sc,tw,th)
    d,cx,cy,s,tw,th=best; res.append((cx,cy,tw,th,d))
res=np.array(res,float); k=np.ones(7)/7
for c in range(4): res[:,c]=np.convolve(np.pad(res[:,c],3,mode='edge'),k,'valid')
np.save(out,res); n=len(F); tiles=[]
for i in np.linspace(0,n-1,5).astype(int):
    x,y,w,h=res[i][:4]; im=Image.fromarray(F[i]); ImageDraw.Draw(im).rectangle([x,y,x+w,y+h],outline=(255,0,0))
    tiles.append(im.crop((max(0,int(x)-90),max(0,int(y)-40),int(x+w)+60,int(y+h)+60)).resize((320,280)))
o=Image.new('RGB',(1600,280)); [o.paste(t,(320*j,0)) for j,t in enumerate(tiles)]; o.save(out.replace('.npy','.png'))
print('frames',n,'max err',round(res[:,4].max(),1),'overlay',out.replace('.npy','.png'))
