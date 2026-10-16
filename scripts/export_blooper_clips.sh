#!/usr/bin/env bash
# Cut the blooper moments (MOPC_Bloopers_Plan.md) from raw interview MXFs into small 720p proxies,
# then commit and push them so the cloud session can finish the edit.
# Run from the repo root in WSL on the PC that syncs G:. Usage: bash scripts/export_blooper_clips.sh
set -euo pipefail

RAW="${RAW:-/mnt/g/.shortcut-targets-by-id/1uhJdtOHGNbD0DsHKm8UKuczi1VcLG0q4/MOPC Network/Marketing/Videos Photos/RAW/Interviews}"
OUT="MOPC_Videos/blooper_clips"
H=0.5   # handle seconds on each side
mkdir -p "$OUT"

src() {  # subject -> MXF path
  case "$1" in
    jeff)   echo "$RAW/Copy of Interview - Jeff.MXF" ;;
    sharon) echo "$RAW/Copy of Interview - Sharon (Pickleball).MXF" ;;
    brad)   ls "$RAW"/*2922*.MXF | head -1 ;;
  esac
}

# name subject in out (seconds, from the Whisper transcripts)
CLIPS="
01_jeff_loveoflove jeff 10.0 12.3
02_brad_fullname brad 3.3 7.1
03_sharon_forgot sharon 64.2 71.2
04_sharon_didntlook sharon 82.9 84.9
05_jeff_max jeff 29.8 30.9
06_jeff_dogs jeff 709.7 727.9
07_brad_blinds brad 66.4 73.4
08_sharon_expressive sharon 44.4 52.3
09_jeff_lifeflight jeff 444.5 449.4
10a_jeff_onemore jeff 18.6 19.3
10b_jeff_onemore jeff 26.4 27.1
10c_brad_onemore brad 14.5 15.2
10d_jeff_onemore jeff 643.4 644.9
10e_sharon_onemore sharon 695.3 697.3
11_sharon_cuecard sharon 737.4 739.4
12_jeff_tagline jeff 414.9 419.9
13_sharon_signup sharon 787.7 789.7
"

while read -r name who in out; do
  [ -n "$name" ] || continue
  f="$(src "$who")"; [ -f "$f" ] || { echo "Missing source for $who: $f"; exit 1; }
  ss=$(awk "BEGIN{v=$in-$H; print (v<0?0:v)}"); t=$(awk "BEGIN{print $out-$in+2*$H}")
  # Lav mics are on audio streams 2/3; fall back to stream 0.
  for a in 2 0; do
    ffmpeg -loglevel error -y -ss "$ss" -i "$f" -t "$t" -map 0:v:0 -map "0:a:$a" \
      -vf "scale=1280:-2" -c:v libx264 -crf 23 -preset veryfast -pix_fmt yuv420p \
      -c:a aac -b:a 128k -ac 1 "$OUT/$name.mp4" && break
  done
  echo "ok $name"
done <<< "$CLIPS"

du -sh "$OUT"
git add "$OUT"
git commit -m "Add blooper clip proxies from raw interviews"
git push origin claude/mopc-humour-bloopers
echo "Pushed. Tell Claude the clips are up."
