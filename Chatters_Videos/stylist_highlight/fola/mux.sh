#!/usr/bin/env bash
# Fola highlight: music-only beds D/E/F (final chord on the CTA), two-pass loudnorm -14 LUFS / -1.3 dBTP, 320k AAC.
set -euo pipefail
cd "$(dirname "$0")"
PIC=CHATTERS_FOLA_stylist_highlight_SILENT.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $PIC)
END_BEAT=28.52 python3 build_music_v2.py >/dev/null
for o in D_pop E_lofi F_funk; do
  PRE="atrim=0:$DUR,afade=t=in:d=0.15,afade=t=out:st=$(echo "$DUR-1.4"|bc):d=1.4"
  J=$(ffmpeg -hide_banner -i music_${o}_raw.wav -af "$PRE,loudnorm=I=-14:TP=-1.3:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -y -loglevel error -i $PIC -i music_${o}_raw.wav -map 0:v -map 1:a -c:v copy \
    -af "$PRE,loudnorm=I=-14:TP=-1.3:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
    -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart CHATTERS_FOLA_stylist_highlight_${o}.mp4
done
rm -f music_*_raw.wav
