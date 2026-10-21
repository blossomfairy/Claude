"""Assemble the 30 s Kidvy Pickup ad (arrival + handover), FR and EN, 1920x1080 25 fps.

Run: python3 -I kidvy/ad30/build.py [fr|en ...] [--stock DIR]
- Inserts come from out/screens (run screens.js first).
- Stock: DIR holds the Adobe_Stock .mov files; each beat's clip + in-point is set in SHOTS.
  A beat without a clip on disk renders a labelled slate, so timing can be reviewed before footage arrives.
- Captions and inserts stay inside the centred 9:16 column (608 px) for the vertical cut.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(HERE, "out", "screens")
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
NB = " "

# (duration s, stock clip or None, in-point s, slate note, [(insert, start s, end s)], caption fr, caption en)
SHOTS = [
    (4, None, 0, "parents waiting outside a school, end of day", [],
     f"15 h 30.\nLa file au portail.", "3:30.\nThe line at the gate."),
    (5, None, 0, "parent arriving, phone in hand", [("parent_here", 0, 2.5), ("parent_notified", 2.5, 5)],
     f"Le parent arrive{NB}:\n«{NB}Je suis là{NB}».", "The parent arrives:\n“I’m here.”"),
    (5, None, 0, "teacher with a class tablet", [("class_waiting", 0, 2.5), ("class_onway", 2.5, 5)],
     "La classe le voit\nà l’écran.", "The class sees it\non screen."),
    (6, None, 0, "staff at the entrance holding a tablet", [("gate_scan", 0, 6)],
     "Au portail, on scanne\nle code du parent.", "At the gate, the parent’s\ncode is scanned."),
    (5, None, 0, "child walks out to the parent (wide / from behind)", [("gate_handed", 0, 5)],
     "L’enfant est remis.\nChaque enfant remis est noté.", "The child is handed over.\nEach hand-off is on record."),
    (5, "ENDCARD", 0, "", [], "", ""),
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr[-1500:])


def seg(lang, i, shot, stock_dir, tmp):
    dur, clip, inpt, note, inserts, cap_fr, cap_en = shot
    out = os.path.join(tmp, f"{i:02d}.mp4")
    if clip == "ENDCARD":
        run(["ffmpeg", "-y", "-loop", "1", "-t", str(dur), "-i", os.path.join(SCR, f"{lang}_endcard.png"),
             "-vf", "fps=25,format=yuv420p,fade=in:0:10", "-c:v", "libx264", "-crf", "18", out])
        return out
    path = clip and os.path.join(stock_dir or "", clip)
    if path and os.path.exists(path):
        src = ["-ss", str(inpt), "-t", str(dur), "-i", path]
        base = "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,setsar=1[bg]"
    else:  # slate until footage is available
        notefile = os.path.join(tmp, f"note{i}.txt")
        open(notefile, "w", encoding="utf-8").write(f"STOCK — {note}")
        src = ["-f", "lavfi", "-t", str(dur), "-i", "color=c=0x2b3440:s=1920x1080:r=25"]
        base = (f"[0:v]drawtext=fontfile={FONT}:textfile={notefile}:fontcolor=0x9aa5b1:fontsize=30:"
                f"x=(w-tw)/2:y=60,setsar=1[bg]")
    chain, last, n = [base], "bg", 1
    for name, a, b in inserts:
        src += ["-i", os.path.join(SCR, f"{lang}_{name}.png")]
        h = 560 if name.startswith("parent") else 330  # phone vs tablet strip, both < 608 px wide
        chain.append(f"[{n}:v]scale=-1:{h},scale='min(iw,560)':-1[i{n}]")
        chain.append(f"[{last}][i{n}]overlay=x=(W-w)/2:y=150:enable='between(t,{a},{b})'[v{n}]")
        last, n = f"v{n}", n + 1
    capfile = os.path.join(tmp, f"cap{i}.txt")
    open(capfile, "w", encoding="utf-8").write(cap_fr if lang == "fr" else cap_en)
    chain.append(f"[{last}]drawtext=fontfile={FONT}:textfile={capfile}:fontcolor=white:fontsize=40:"
                 f"line_spacing=10:box=1:boxcolor=black@0.55:boxborderw=18:x=(w-tw)/2:y=h-th-110,format=yuv420p[out]")
    run(["ffmpeg", "-y", *src, "-filter_complex", ";".join(chain), "-map", "[out]",
         "-t", str(dur), "-c:v", "libx264", "-crf", "18", out])
    return out


def build(lang, stock_dir):
    with tempfile.TemporaryDirectory() as tmp:
        parts = [seg(lang, i, s, stock_dir, tmp) for i, s in enumerate(SHOTS)]
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        dst = os.path.join(HERE, "out", f"kidvy_pickup_30s_{lang}{'' if stock_dir else '_slates'}.mp4")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", dst])
        return dst


if __name__ == "__main__":
    args = sys.argv[1:]
    stock = args[args.index("--stock") + 1] if "--stock" in args else None
    langs = [a for a in args if a in ("fr", "en")] or ["fr", "en"]
    for lang in langs:
        print(build(lang, stock))
