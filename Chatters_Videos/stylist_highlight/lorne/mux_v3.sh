#!/usr/bin/env bash
# Lorne highlight v3: Lorne's voice (clip audio 0-14.58 s) over a ducked music bed that lifts on the CTA,
# two-pass loudnorm to -14 LUFS / -1.3 dBTP, 320k AAC.
set -euo pipefail
cd "$(dirname "$0")"
PIC=CHATTERS_LORNE_stylist_highlight_v3_SILENTPIC.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $PIC)
END_BEAT=34.32 python3 build_music_v2.py >/dev/null
for o in D_pop E_lofi F_funk; do
  G="[0:a]atrim=0:14.6,afade=t=out:st=14.45:d=0.15,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,volume=2.0,apad=whole_dur=$DUR[v];[1:a]atrim=0:$DUR,volume='if(lt(t,14.3),0.16,0.16+0.84*min(1,(t-14.3)/0.6))':eval=frame,afade=t=out:st=$(echo "$DUR-1.4"|bc):d=1.4[m];[v][m]amix=inputs=2:normalize=0[mix]"
  J=$(ffmpeg -hide_banner -i src/lorne_ask_a_stylist.mp4 -i music_${o}_raw.wav -filter_complex "$G;[mix]loudnorm=I=-14:TP=-1.3:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -y -loglevel error -i src/lorne_ask_a_stylist.mp4 -i music_${o}_raw.wav -i $PIC \
    -filter_complex "$G;[mix]loudnorm=I=-14:TP=-1.3:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000[a]" \
    -map 2:v -map "[a]" -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart CHATTERS_LORNE_stylist_highlight_v3_${o}.mp4
done
rm -f music_*_raw.wav
