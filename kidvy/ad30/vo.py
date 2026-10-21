"""Temporary voice-over for the 30 s ad (until the client's paid talent records), FR + EN.

Engine: Kokoro v1.0 via kokoro-onnx (Apache-2.0); voices ff_siwis (FR) and af_heart (EN).
Each line is synthesised separately and placed at its slot start; the script fails if a line overruns its slot.
Run: python3 -I kidvy/ad30/vo.py <dir with kokoro-v1.0.onnx + voices-v1.0.bin>  -> out/vo/vo_{fr,en}.wav (30.0 s, 48 kHz)
"""
import os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "vo")
SR = 24000

# (slot start s, slot end s, text) — same slots as the captions in build.py
LINES = {
    "fr": [(0.2, 7.0, "Quinze heures trente. La file au portail. Le walkie-talkie. L’attente."),
           (7.3, 9.6, "Le parent arrive : je suis là."),
           (9.7, 14.3, "La classe le voit à l’écran. L’enfant se prépare."),
           (14.5, 19.1, "L’enfant est remis au parent."),
           (19.3, 26.3, "Chaque enfant remis est noté. L’esprit tranquille, pour l’école et les parents."),
           (26.45, 29.95, "Le ramassage, plus simple et plus calme.")],
    "en": [(0.2, 7.0, "Three-thirty. The line at the gate. The walkie-talkie. The wait."),
           (7.3, 9.6, "The parent arrives: I’m here."),
           (9.7, 14.3, "The class sees it on screen. The child gets ready."),
           (14.5, 19.1, "The child is handed over."),
           (19.3, 26.3, "Each hand-off is on record. Peace of mind for schools and parents."),
           (26.45, 29.95, "Kidvy Pickup. Simpler, and calmer.")],
}
VOICE = {"fr": ("ff_siwis", "fr-fr", 0.74), "en": ("af_heart", "en-us", 0.8)}


def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x[idx[0]:idx[-1] + 1] if len(idx) else x


def main(model_dir):
    k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
    os.makedirs(OUT, exist_ok=True)
    for lang, lines in LINES.items():
        voice, code, speed = VOICE[lang]
        track = np.zeros(int(30.0 * SR), dtype=np.float32)
        tot_w = tot_s = 0
        for a, b, text in lines:
            s, sr = k.create(text, voice=voice, speed=speed, lang=code)
            s = trim(np.asarray(s, dtype=np.float32))
            dur = len(s) / sr
            words = len([w for w in text.replace("’", " ").split() if w.strip(":.,")])
            tot_w, tot_s = tot_w + words, tot_s + dur
            print(f"{lang} {a:5.2f}-{b:<5} {dur:4.2f}s {words / dur * 60:4.0f} wpm  {text}")
            if a + dur > b:
                sys.exit(f"overrun: {lang} line at {a}s is {dur:.2f}s for a {b - a:.2f}s slot")
            i = int(a * SR)
            track[i:i + len(s)] += s
        print(f"{lang} overall {tot_w} words / {tot_s:.1f} s spoken = {tot_w / tot_s * 60:.0f} wpm")
        raw = os.path.join(OUT, f"vo_{lang}_24k.wav")
        sf.write(raw, track, SR)
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", raw, "-af",
                        "highpass=f=80,acompressor=threshold=-24dB:ratio=2.5:attack=5:release=120,"
                        "aresample=48000,aformat=channel_layouts=stereo", os.path.join(OUT, f"vo_{lang}.wav")], check=True)
        os.remove(raw)


if __name__ == "__main__":
    main(sys.argv[1])
