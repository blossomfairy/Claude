#!/usr/bin/env bash
# Transcribe MOPC raw interview MXFs to timestamped .srt for blooper/soundbite picking.
# Run in WSL on the PC where Google Drive (G:) syncs the MOPC Network shared folder.
# Usage: bash scripts/transcribe_interviews.sh [Carly|Gary|Chris|all]
set -euo pipefail

RAW="${RAW:-/mnt/g/.shortcut-targets-by-id/1uhJdtOHGNbD0DsHKm8UKuczi1VcLG0q4/MOPC Network/Marketing/Videos Photos/RAW/Interviews}"
OUT="${OUT:-/mnt/g/My Drive/MOPC Working (Amy)/Transcripts}"
WORK="${WORK:-$HOME/video-editor/transcribe-work}"
VENV="${VENV:-$HOME/.venv-audio}"
MODEL="${MODEL:-medium}"
WHO="${1:-all}"

declare -A FILES=(
  [Carly]="Copy of Interview Carly.MXF"
  [Gary]="Copy of Interview - Gary & Lynn (Residential).MXF"
  [Chris]="Copy of Interview - Chris (Pharmacy).MXF"
)

mkdir -p "$OUT" "$WORK"
[ -x "$VENV/bin/python" ] || { echo "No venv at $VENV. Run setup-audio.sh first."; exit 1; }
"$VENV/bin/python" -c "import faster_whisper" 2>/dev/null || "$VENV/bin/pip" install -q faster-whisper

for name in Carly Gary Chris; do
  [ "$WHO" = all ] || [ "$WHO" = "$name" ] || continue
  src="$RAW/${FILES[$name]}"
  [ -f "$src" ] || { echo "Missing: $src"; continue; }
  wav="$WORK/${name,,}.wav"
  # Lav mics sit on audio streams 2/3 in these MXFs; fall back to stream 0.
  if ! ffmpeg -loglevel error -y -i "$src" -map 0:a:2 -ac 1 -ar 16000 "$wav"; then
    ffmpeg -loglevel error -y -i "$src" -map 0:a:0 -ac 1 -ar 16000 "$wav"
  fi
  echo "Transcribing $name ($MODEL)..."
  "$VENV/bin/python" - "$wav" "$OUT/${name,,}.srt" "$MODEL" <<'PY'
import sys
from faster_whisper import WhisperModel
wav, out, model = sys.argv[1:4]
def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
segs, _ = WhisperModel(model, compute_type="int8").transcribe(wav, vad_filter=False, language="en")
with open(out, "w") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
print("wrote", out)
PY
done
echo "Done. SRTs in: $OUT"
