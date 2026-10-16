#!/bin/bash
# qc_sheet.sh CLIP [FPS=2] [COLSxROWS=5x2] [WIDTH=288] -> CLIP.qc.jpg
F=$1; R=${2:-2}; T=${3:-5x2}; W=${4:-288}
ffmpeg -loglevel error -y -i "$F" -vf "fps=$R,scale=$W:-1,tile=$T" -frames:v 1 "${F%.*}.qc.jpg" && echo "${F%.*}.qc.jpg"
