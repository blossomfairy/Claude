"""Assemble the 30 s Kidvy Pickup AD (arrival + hand-off), FR and EN, 1920x1080 25 fps, with the music bed.

Run: python3 -I kidvy/ad30/build.py [fr|en ...] [--stock DIR] [--music A|B|C]
- Inputs: out/screens (node screens.js), out/music/option_X.wav (python3 compose.py), stock proxies in DIR
  (1080p H.264 made from Drive › Adobe_Stock, named AdobeStock_<id>.mp4).
- Grid: 100 BPM, 1 bar = 2.4 s = 60 frames; every cut sits on a bar line, the lift is on the hand-off (16.8 s).
- Rules (kidvy-pickup-ad): hook = people, no app; UI only as pills over footage (≤ 30 % of frames);
  shots 2.4-4.8 s; end card ≤ 4 s; -14 LUFS, limiter ceiling -2.0 dBFS so AAC stays ≤ -1 dBTP.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(HERE, "out", "screens")
MUS = os.path.join(HERE, "out", "music")
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
NB = " "
BAR = 2.4
# Music: Adobe Stock 487400182 "Folk Acoustic Light" (licensed 2026-10-21), 100 BPM, beats on 0.6 s from 0.0.
# Played from 108.0 s so its final chord (134.4 s, a downbeat) lands on the end card at 26.4 s.
MUSIC_IN = 108.0
GRADE = "eq=contrast=1.04:brightness=0.015:saturation=1.06:gamma=1.02,colorbalance=rm=0.025:bm=-0.02"

# (bars, clip id, in-point s, [(pill, x, y, start s, end s)], caption key) — times inside the shot
SHOTS = [
    (1, "624086363", 2.0, [], "c1"),
    (1, "424171310", 2.0, [], "c2"),
    (1, "624086363", 9.5, [], "c2"),
    (1, "283680613", 1.0, [("pill_here", 1180, 380, 0.25, 1.35), ("pill_notified", "W-w-140", 250, 1.35, 2.4)], "c3"),
    (1, "1831479379", 1.0, [], "c4"),
    (1, "2115633640", 3.0, [], "c4"),
    (2, "678770640", 0.0, [("pill_handed", "W-w-140", 140, 2.5, 4.8)], "c5"),
    (1, "573153209", 3.5, [], "c6"),
    (2, "753350890", 2.5, [], "c6"),
]
END_S = 30.0 - BAR * sum(s[0] for s in SHOTS)  # 3.6 s

# captions: (start s, end s, text) on the timeline; each line sized for ≤ 155 wpm
CAPS = {  # = the VO lines (vo.py); end card carries the tagline itself, so no caption there
    "fr": [(0.2, 7.0, "15 h 30. La file au portail.\nLe walkie-talkie. L’attente."), (7.3, 9.6, f"Le parent arrive{NB}: «{NB}Je suis là{NB}»."),
           (9.7, 14.3, "La classe le voit à l’écran.\nL’enfant se prépare."), (14.5, 19.1, "L’enfant est remis au parent."),
           (19.3, 26.3, "Chaque enfant remis est noté.\nL’esprit tranquille, pour l’école et les parents.")],
    "en": [(0.2, 7.0, "3:30. The line at the gate.\nThe walkie-talkie. The wait."), (7.3, 9.6, "The parent arrives: “I’m here.”"),
           (9.7, 14.3, "The class sees it on screen.\nThe child gets ready."), (14.5, 19.1, "The child is handed over."),
           (19.3, 26.3, "Each hand-off is on record.\nPeace of mind for schools and parents.")],
}


def run(cmd):
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr[-2000:])


def shot(lang, i, s, stock, tmp):
    bars, clip, inpt, pills, _ = s
    dur = bars * BAR
    out = os.path.join(tmp, f"{i:02d}.mp4")
    src = ["-ss", str(inpt), "-t", str(dur), "-i", os.path.join(stock, f"AdobeStock_{clip}.mp4")]
    chain = [f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,setsar=1,{GRADE},format=yuv420p[v0]"]
    last = "v0"
    for n, (name, x, y, a, b) in enumerate(pills, 1):
        src += ["-loop", "1", "-t", str(dur), "-i", os.path.join(SCR, f"{lang}_{name}.png")]
        # 0.3 s fade + 18 px rise in, 0.2 s fade out; RGBA overlay converted with bt709 to keep #F9413B true
        chain.append(f"[{n}:v]format=rgba,fade=t=in:st={a}:d=0.3:alpha=1,fade=t=out:st={b - 0.2}:d=0.2:alpha=1[p{n}]")
        chain.append(f"[{last}][p{n}]overlay=x={x}:y='{y}+18*max(0,1-(t-{a})/0.3)':enable='between(t,{a},{b})'"
                     f":format=yuv420[o{n}]")
        last = f"o{n}"
    run([*src, "-filter_complex", ";".join(chain), "-map", f"[{last}]", "-t", str(dur),
         "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-colorspace", "bt709", "-color_primaries", "bt709",
         "-color_trc", "bt709", out])
    return out


def endcard(lang, tmp):
    out = os.path.join(tmp, "end.mp4")
    # continuous slow push (no freeze), fade in from the last shot
    run(["-loop", "1", "-t", str(END_S), "-i", os.path.join(SCR, f"{lang}_endcard.png"), "-vf",
         f"fps=25,scale=w='trunc(1920*(1+0.05*t/{END_S})/2)*2':h=-2:eval=frame,crop=1920:1080,setsar=1,"
         "fade=in:0:8,format=yuv420p", "-c:v", "libx264", "-crf", "16", out])
    return out


def captions(lang, src, dst, tmp):
    filt = []
    for k, (a, b, txt) in enumerate(CAPS[lang]):
        f = os.path.join(tmp, f"cap_{lang}_{k}.txt")
        open(f, "w", encoding="utf-8").write(txt)
        filt.append(f"drawtext=fontfile={FONT}:textfile={f}:fontcolor=white:fontsize=46:line_spacing=12:"
                    f"box=1:boxcolor=black@0.45:boxborderw=20:x=(w-tw)/2:y=h-th-96:enable='between(t,{a},{b})'")
    run(["-i", src, "-vf", ",".join(filt), "-c:v", "libx264", "-crf", "16", "-preset", "medium", dst])


def mix(lang, music, tmp):
    """Licensed stock bed + VO. Bed ducks ~8 dB under the voice (sidechain), sits ~20 LU under it during speech;
    then linear gain to -14 LUFS and limiter -2.6 dBFS (AAC stays <= -1 dBTP)."""
    vo = os.path.join(HERE, "out", "vo", f"vo_{lang}.wav")
    pre = os.path.join(tmp, "pre.wav")
    run(["-ss", str(MUSIC_IN), "-t", "30", "-i", music, "-i", vo, "-filter_complex",
         "[0:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.25,volume=-17dB[m];"
         "[1:a]loudnorm=I=-16:TP=-3:LRA=7,aresample=48000,asplit=2[v][k];"
         "[m][k]sidechaincompress=threshold=0.02:ratio=4:attack=40:release=450:makeup=1[d];"
         "[d][v]amix=inputs=2:normalize=0:duration=longest,atrim=0:30[out]", "-map", "[out]", pre])
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", pre, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i_lufs = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    out = os.path.join(tmp, "mix.wav")
    run(["-i", pre, "-af", f"volume={-14.0 - i_lufs:.2f}dB,alimiter=limit=-2.6dB:level=false:latency=1",
         "-ar", "48000", out])
    return out


def build(lang, stock):
    with tempfile.TemporaryDirectory() as tmp:
        parts = [shot(lang, i, s, stock, tmp) for i, s in enumerate(SHOTS)] + [endcard(lang, tmp)]
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        pic = os.path.join(tmp, "pic.mp4")
        run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", pic])
        capd = os.path.join(tmp, "cap.mp4")
        captions(lang, pic, capd, tmp)
        audio = mix(lang, MUSIC, tmp)
        dst = os.path.join(HERE, "out", f"kidvy_pickup_ad30_{lang}_v3.mp4")
        run(["-i", capd, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
             "-t", "30", "-movflags", "+faststart", dst])
        return dst


if __name__ == "__main__":
    a = sys.argv[1:]
    stock = a[a.index("--stock") + 1] if "--stock" in a else os.path.join(HERE, "stock")
    MUSIC = a[a.index("--music") + 1] if "--music" in a else os.path.join(HERE, "stock", "487400182.wav")
    for lang in [x for x in a if x in ("fr", "en")] or ["fr", "en"]:
        print(build(lang, stock))
