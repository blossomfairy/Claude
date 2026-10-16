"""paintout.py CLIP TRACK.npy OUT.mp4 SAMPLE_DX SAMPLE_DY SAMPLE_W SAMPLE_H
Fills tracked boxes with the mean colour of a clean area at (box_x+DX, box_y+DY, W, H), temporally smoothed, with grain
and feathered edges. Only for tiny UI/sign removal; verify at native res - a visible patch is a fail."""
import sys, subprocess, json, numpy as np
clip,trk,out=sys.argv[1:4]; dx,dy,sw,sh=map(int,sys.argv[4:8])
s=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','json',clip],capture_output=True,text=True).stdout)['streams'][0]
W,H,fps=s['width'],s['height'],s['r_frame_rate']
F=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i',clip,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout,np.uint8).reshape(-1,H,W,3).copy()
R=np.load(trk); rng=np.random.default_rng(0)
cols=np.array([F[i,int(R[i][1])+dy:int(R[i][1])+dy+sh,int(R[i][0])+dx:int(R[i][0])+dx+sw].reshape(-1,3).mean(0) for i in range(len(F))])
cols=np.stack([np.convolve(np.pad(cols[:,c],4,mode='edge'),np.ones(9)/9,'valid') for c in range(3)],1)
for i in range(len(F)):
    x,y,w,h=[int(round(v)) for v in R[i][:4]]
    blk=cols[i][None,None,:]*np.linspace(1,0.93,h)[:,None,None]+rng.normal(0,2,(h,w,3))
    m=np.ones((h,w))
    for k in range(5): v=(k+1)/6; m[-k-1,:]*=v; m[:,k]*=v
    F[i,y:y+h,x:x+w]=(blk*m[...,None]+F[i,y:y+h,x:x+w]*(1-m[...,None])).clip(0,255).astype(np.uint8)
p=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fps,'-i','-','-i',clip,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-c:a','copy',out],stdin=subprocess.PIPE)
p.stdin.write(F.tobytes()); p.stdin.close(); p.wait(); print(out)
