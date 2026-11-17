"""Asma before/after reel: 1080x1920, 30 fps, 92 BPM grid, silent master.

Sources (all pre-graded with the same mall-light correction, see README in posting_plan.md):
before.jpg (back, before), after1.jpg / after2.jpg (back, after), v/NNNN.jpg = after video at 30 fps
(478x850, upscaled with lanczos + unsharp). The side photo is NOT used (client's face). Video frames
stop at 17.4 s: the client's glasses/face turn into frame at 17.5 s.
House style: serif title + "With Chatters" script, white bold-sans labels + lower third, white logo on the last shot.
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(
    "~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht  # noqa: E402

W, H, FPS, BPM = 1080, 1920, 30, 92
BEAT = 60 / BPM
GRADE = "eq=contrast=1.09:saturation=1.06:gamma=1.02,colorbalance=rs=0.03:bs=-0.03"  # mall-light grade, all sources
if not os.path.isdir(f"{D}/src/v"):  # after video -> graded 30 fps frames, stop before the face turn at 17.5 s
    os.makedirs(f"{D}/src/v")
    subprocess.run(["ffmpeg", "-v", "error", "-i", f"{D}/src/after_video.mov", "-t", "17.4", "-vf", f"fps=30,{GRADE}",
                    "-q:v", "2", f"{D}/src/v/%04d.jpg"], check=True)
P = {k: Image.open(f"{D}/src/{k}.jpg").convert("RGB") for k in ("before", "after1", "after2")}
NV = len(os.listdir(f"{D}/src/v"))
_vc = {}


def vframe(t):
    n = min(NV, max(1, int(round(t * 30)) + 1))
    if n not in _vc:
        _vc.clear() if len(_vc) > 40 else None
        _vc[n] = Image.open(f"{D}/src/v/{n:04d}.jpg").convert("RGB")
    return _vc[n]


# (source, beats, t_in(video) | None, cx, cy, z0, z1, label)   z = visible width fraction of the source
SHOTS = [
    ("V", 2.5, 4.25, .50, .50, .96, .90, None),        # hook: after in motion + title
    ("before", 2, None, .47, .50, .74, .70, "Before"),
    ("SPLIT", 2.5, None, 0, 0, 0, 0, None),            # before | after
    ("after1", 1, None, .50, .55, .74, .70, "After"),
    ("V", 1, 1.40, .50, .55, .92, .86, None),           # curls bounce
    ("after2", 1, None, .52, .62, .60, .57, None),
    ("V", 1, 12.00, .50, .60, .92, .86, None),          # ends spread, colour shows
    ("before", 1, None, .50, .72, .55, .52, "Before"),  # frizzy ends
    ("V", 1, 7.30, .50, .50, .92, .86, "After"),        # hands through curls
    ("after1", 1, None, .50, .75, .55, .52, None),      # curl detail
    ("V", 1.5, 10.30, .50, .55, .94, .88, None),        # side, hand lifts hair
    ("after2", 1, None, .50, .70, .52, .49, None),
    ("V", 1, 3.00, .50, .55, .90, .85, None),
    ("V", 1, 12.65, .50, .62, .88, .83, None),
    ("before", 1, None, .45, .35, .55, .52, "Before"),  # dark, grey root area
    ("after1", 1, None, .50, .35, .55, .52, "After"),   # blended root
    ("V", 1, 16.72, .50, .55, .92, .87, None),          # lower third from here
    ("after2", 1.5, None, .52, .60, .58, .55, None),
    ("V", 1, 8.30, .50, .55, .92, .86, None),
    ("V", 1, 5.20, .50, .52, .90, .85, None),
    ("after1", 1, None, .52, .60, .62, .58, None),      # lower third ends
    ("after1", 5, None, .50, .52, .66, .74, None),      # reveal held, pull back, logo
]
LOWER_FROM, LOWER_TO = 16, 21

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc
for s, st in zip(SHOTS, starts):  # never reach the face turn
    assert s[0] != "V" or s[2] + s[1] * BEAT <= 17.4, s


def readable_title(text, brand, y=0.20):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=190)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=170)
    return img


def label(text, x=W // 2, size=78):
    img = ht.canvas()
    ht.shadow_text(img, (x, int(H * .80)), text, ht.sans(size, "Bold"), ht.TITLE_WHITE, blur=6, alpha=130)
    return img


title = readable_title("Colour, Cut & Style", "Chatters", y=0.37)  # over the dark crown; the white "happy" wall at 0.20 kills legibility
LABELS = {k: label(k) for k in ("Before", "After")}
SPLIT_LABELS = [label("Before", W // 4, 64), label("After", 3 * W // 4, 64)]
lower = ht.lower("Asma", "Chatters Lawson Heights", y=0.70)
endlogo = ht.endlogo()
LOWER_T = (starts[LOWER_FROM] + 0.1, starts[LOWER_TO] - 0.05)
END_T = (starts[-1] + 0.5, TOTAL + 1)


def fade(t, a, b, f=0.2):
    if t < a or t > b:
        return 0.0
    return max(0.0, min(1.0, (t - a) / f, (b - t) / f))


def over(fr, ov, a):
    if a <= 0:
        return
    if a < 1:
        ov = ov.copy()
        ov.putalpha(ov.getchannel("A").point(lambda v: int(v * a)))
    fr.alpha_composite(ov)


def view(img, cx, cy, z, ow=W, oh=H, sharpen=False):
    iw, ih = img.size
    cw = iw * z
    ch = cw * oh / ow
    if ch > ih:
        ch = ih
        cw = ch * ow / oh
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    out = img.resize((ow, oh), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return out.filter(ImageFilter.UnsharpMask(2.2, 70, 2)) if sharpen else out


def frame(i, t):
    kind, beats, tin, cx, cy, z0, z1, _ = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = p * p * (3 - 2 * p)
    if kind == "SPLIT":
        out = Image.new("RGB", (W, H))
        out.paste(view(P["before"], .47, .50, .50 - .03 * e, W // 2, H), (0, 0))
        out.paste(view(P["after1"], .50, .52, .50 - .03 * e, W // 2, H), (W // 2, 0))
        ImageDraw.Draw(out).rectangle((W // 2 - 2, 0, W // 2 + 1, H), fill=(255, 255, 255))
        return out
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.06 * math.exp(-dt / 0.11)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    if kind == "V":
        return view(vframe(tin + dt), cx, cy, z, sharpen=True)
    return view(P[kind], cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_ASMA_before_after_SILENT.mp4"], stdin=subprocess.PIPE)

for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    lab = SHOTS[i][7]
    if lab:
        over(fr, LABELS[lab], fade(t, starts[i] + 0.03, starts[i] + SHOTS[i][1] * BEAT - 0.03, 0.08))
    if SHOTS[i][0] == "SPLIT":
        for L in SPLIT_LABELS:
            over(fr, L, fade(t, starts[i] + 0.05, starts[i + 1] - 0.05, 0.12))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.35))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
