#!/usr/bin/env bash
# Rose: music beds D/E/F (final chord at beat 27, the end shot) + Jingle Bells celesta (32 beats = full reel); -14 LUFS / -1.3 dBTP.
set -euo pipefail
cd "$(dirname "$0")"
PIC=CHATTERS_ROSE_layers_trend_SILENT.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $PIC)
END_BEAT=27 python3 build_music_v2.py >/dev/null
python3 build_music_xmas.py >/dev/null; mv music_A_celesta_raw.wav music_X_xmas_raw.wav; rm -f music_B_piano_raw.wav music_C_musicbox_raw.wav
for o in D_pop E_lofi F_funk X_xmas; do
  PRE="atrim=0:$DUR,afade=t=in:d=0.15,afade=t=out:st=$(echo "$DUR-1.4"|bc):d=1.4"
  J=$(ffmpeg -hide_banner -i music_${o}_raw.wav -af "$PRE,loudnorm=I=-14:TP=-1.3:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -y -loglevel error -i $PIC -i music_${o}_raw.wav -map 0:v -map 1:a -c:v copy \
    -af "$PRE,loudnorm=I=-14:TP=-1.3:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
    -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart CHATTERS_ROSE_layers_trend_${o}.mp4
done
rm -f music_*_raw.wav
