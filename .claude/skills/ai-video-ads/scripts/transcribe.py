"""transcribe.py MEDIA [--words] [--ss S --t D] : print timed speech (faster-whisper, VAD). No speech -> 'none'."""
import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
a=sys.argv; f=a[1]; words='--words' in a
ss=a[a.index('--ss')+1] if '--ss' in a else '0'; cmd=['ffmpeg','-loglevel','error','-ss',ss,'-i',f]
if '--t' in a: cmd+=['-t',a[a.index('--t')+1]]
pcm=np.frombuffer(subprocess.run(cmd+['-ar','16000','-ac','1','-f','s16le','-'],capture_output=True).stdout,np.int16).astype(np.float32)/32768
segs,_=WhisperModel('small',compute_type='int8').transcribe(pcm,vad_filter=True,word_timestamps=words)
out=False
for s in segs:
    out=True; print(f'{s.start+float(ss):6.1f}-{s.end+float(ss):6.1f} {s.text.strip()}')
    if words: print('   '+' '.join(f'{w.word.strip()}@{w.start+float(ss):.1f}' for w in s.words))
if not out: print('none')
