#!/bin/bash
# edit.sh SPEC.txt OUT.mp4
# SPEC lines (# comments ok):
#   shot  FILE IN DUR [extra -vf filters]      clips in order (upscaled to 1080x1920, 30fps)
#   end   PNG DUR                              end card (hard cut)
#   song  FILE OFFSET [VOL=0.8]                music bed from OFFSET, fades out last 1.2 s
#   ov    PNG START END                        full-frame RGBA overlay window (seconds on output timeline)
#   ovshot PNG SHOT_INDEX [DELAY=0]            overlay for the whole of shot N (0-based)
# Output: H.264 High, yuv420p, AAC 320k 48k, -14 LUFS, true peak <= -1 dBTP.
set -e; SPEC=$1; OUT=$2; T=$(mktemp -d); W=1080; H=1920
: > $T/list; t=0; i=0; declare -a ST DU; SONG=; OVS=()
while read -r kind a b c d; do
  case "$kind" in
    shot) ST[$i]=$t; DU[$i]=$c
      ffmpeg -nostdin -loglevel error -y -ss $b -t $c -i "$a" -f lavfi -i anullsrc=r=48000:cl=stereo \
        -filter_complex "[0:v]scale=$W:$H:force_original_aspect_ratio=increase:flags=lanczos,crop=$W:$H,fps=30,setsar=1${d:+,$d},format=yuv420p[v];[0:a]aresample=48000[a0];[a0][1:a]amix=inputs=2:duration=first:normalize=0[a]" \
        -map "[v]" -map "[a]" -t $c -c:v libx264 -preset fast -crf 17 -c:a aac -b:a 192k -ac 2 $T/c$i.mp4 2>/dev/null || \
      ffmpeg -nostdin -loglevel error -y -ss $b -t $c -i "$a" -f lavfi -i anullsrc=r=48000:cl=stereo -vf "scale=$W:$H:force_original_aspect_ratio=increase:flags=lanczos,crop=$W:$H,fps=30,setsar=1${d:+,$d},format=yuv420p" \
        -map 0:v -map 1:a -t $c -c:v libx264 -preset fast -crf 17 -c:a aac -b:a 192k $T/c$i.mp4
      echo "file '$T/c$i.mp4'" >> $T/list; t=$(echo "$t+$c"|bc); i=$((i+1));;
    end) ffmpeg -nostdin -loglevel error -y -loop 1 -t $b -i "$a" -f lavfi -t $b -i anullsrc=r=48000:cl=stereo -vf fps=30,format=yuv420p -c:v libx264 -crf 17 -c:a aac -b:a 192k -shortest $T/end.mp4
      ENDD=$b;;
    song) SONG="$a"; SOFF=$b; SVOL=${c:-0.8};;
    ov) OVS+=("$a:$b:$c");;
    ovshot) OVSHOT+=("$a:$b:${c:-0}");;
  esac
done < <(grep -v '^\s*#' "$SPEC" | grep -v '^\s*$')
for o in "${OVSHOT[@]}"; do IFS=: read p n dl <<< "$o"; OVS+=("$p:$(echo "${ST[$n]}+$dl"|bc):$(echo "${ST[$n]}+${DU[$n]}"|bc)"); done
[ -f $T/end.mp4 ] && echo "file '$T/end.mp4'" >> $T/list
ffmpeg -loglevel error -y -f concat -safe 0 -i $T/list -c copy $T/body.mp4
TOT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/body.mp4)
IN="-i $T/body.mp4"; FC="[0:v]null[v0]"; k=0; n=1
[ -n "$SONG" ] && { IN="$IN -ss $SOFF -t $TOT -i $SONG"; n=2; }
for o in "${OVS[@]}"; do IFS=: read p s e <<< "$o"; IN="$IN -i $p"; FC="$FC;[v$k][$((n+k)):v]overlay=enable='between(t,$s,$e)'[v$((k+1))]"; k=$((k+1)); done
if [ -n "$SONG" ]; then FC="$FC;[1:a]aresample=48000,highpass=f=120,volume=$SVOL,afade=t=out:st=$(echo "$TOT-1.2"|bc):d=1.2[m];[m][0:a]amix=inputs=2:normalize=0[mx]"; else FC="$FC;[0:a]anull[mx]"; fi
FC="$FC;[mx]loudnorm=I=-14:TP=-1:LRA=11,volume=3dB,aresample=192000,alimiter=limit=0.75:level=disabled,aresample=48000[aout]"
ffmpeg -loglevel error -y $IN -filter_complex "$FC" -map "[v$k]" -map "[aout]" -t $TOT -c:v libx264 -profile:v high -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 320k -ar 48000 -movflags +faststart "$OUT"
rm -rf $T
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|Peak):' | tail -2
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
