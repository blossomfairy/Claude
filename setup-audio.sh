#!/usr/bin/env bash
# Installs FFmpeg + Whisper, Kokoro TTS, soundfile and MoviePy.
# Kokoro >=0.8 requires Python <3.13, so the Python stack lives in a 3.12 venv.
set -euo pipefail

VENV="${VENV:-$HOME/.venv-audio}"

# FFmpeg
apt-get update && apt-get install -y ffmpeg

# Python 3.12 venv (uv fetches the interpreter if missing)
command -v uv >/dev/null || pip install uv
uv venv -p 3.12 "$VENV"
export VIRTUAL_ENV="$VENV"

# Python dependencies (transformers floor stops the resolver picking a
# source-only tokenizers build)
uv pip install openai-whisper kokoro soundfile moviepy "transformers>=4.40" pip

# spaCy English model used by misaki (Kokoro's G2P)
"$VENV/bin/python" -m spacy download en_core_web_sm

echo "Done. Activate with: source $VENV/bin/activate"
