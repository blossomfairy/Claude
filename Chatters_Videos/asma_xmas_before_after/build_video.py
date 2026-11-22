"""Asma before/after Christmas reel, hard to skip, before first: 1080x1920, 30 fps, 92 BPM grid (Jingle Bells in
cut time), silent master.

Hook: the before is already moving (tight -> full), title + "Before", then a 4-cut half-beat burst on the before,
white flash on the drop into the after video. Same mall-light grade on all sources.
Privacy: the after video shows the stylist and the client's face in the mirror at 0-4.5, 6-7.5 and 13-16 s, so only
the clean windows CLEAN are used (asserted). Photos: before 1500x2000, after 1126x2000; zoom <= 1.6x on photos.
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
GRADE = "eq=contrast=1.09:saturation=1.06:gamma=1.02,colorbalance=rs=0.03:bs=-0.03"
CLEAN = [(8.0, 12.45), (16.6, 25.0)]
P = {k: Image.open(f"{D}/src/{k}.jpg").convert("RGB") for k in ("before", "after")}

if not os.path.isdir(f"{D}/src/v"):
    os.makedirs(f"{D}/src/v")
    subprocess.run(["ffmpeg", "-v", "error", "-i", f"{D}/src/after_video.mp4", "-vf", f"fps=30,{GRADE}",
                    "-q:v", "2", f"{D}/src/v/%04d.jpg"], check=True)
NV = len(os.listdir(f"{D}/src/v"))


def vframe(t):
    n = min(NV, max(1, int(round(t * 30)) + 1))
    return Image.open(f"{D}/src/v/{n:04d}.jpg").convert("RGB")


# (source, beats, t_in(video)|None, cx, cy, z0, z1, label)
SHOTS = [
    ("before", 2.5, None, .50, .40, .46, .74, "Before"),   # hook: moving before + title
    ("before", .5, None, .50, .22, .50, .47, None),        # burst: regrowth at the part
    ("before", .5, None, .55, .78, .50, .47, None),        # dry ends
    ("before", .5, None, .22, .60, .50, .47, None),
    ("before", .5, None, .72, .45, .55, .52, None),
    ("V", 2.5, 8.30, .50, .50, .96, .88, "After"),         # FLASH -> after in motion
    ("after", 1, None, .50, .55, .95, .90, None),
    ("before", 1, None, .50, .25, .52, .49, "Before"),
    ("V", 1, 17.00, .50, .55, .92, .86, "After"),
    ("SPLIT", 2.5, None, 0, 0, 0, 0, None),
    ("V", 1, 10.20, .50, .50, .92, .86, None),
    ("after", 1, None, .50, .30, .66, .62, None),          # blended root
    ("V", 1.5, 18.00, .50, .55, .94, .88, None),
    ("before", 1, None, .55, .80, .55, .52, "Before"),
    ("V", 1, 11.20, .50, .55, .90, .85, "After"),
    ("after", 1, None, .50, .75, .66, .62, None),          # curls
    ("V", 1, 11.70, .50, .50, .92, .86, None),
    ("before", 1, None, .30, .50, .55, .52, "Before"),
    ("after", 1, None, .50, .45, .72, .68, "After"),
    ("V", 1, 19.50, .50, .55, .92, .86, None),             # lower third from here
    ("V", 1, 22.00, .50, .55, .92, .86, None),
    ("after", 1.5, None, .50, .50, .82, .78, None),
    ("V", 1, 23.20, .50, .55, .92, .86, None),
    ("after", 1, None, .50, .78, .62, .60, None),          # lower third ends (tight curls, distinct from the wide end)
    ("after", 4.5, None, .50, .50, .92, 1.00, None),       # reveal held, logo
]
FLASH_AT, LOWER_FROM, LOWER_TO = 5, 19, 24

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc
for s in SHOTS:
    if s[0] == "V":
        a, b = s[2], s[2] + s[1] * BEAT
        assert any(lo <= a and b <= hi for lo, hi in CLEAN), f"video window {a:.2f}-{b:.2f} shows the mirror"


def readable_title(text, brand, y=0.36):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=200)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=200)
    return img


def label(text, x=W // 2, size=78):
    img = ht.canvas()
    ht.shadow_text(img, (x, int(H * .80)), text, ht.sans(size, "Bold"), ht.TITLE_WHITE, blur=6, alpha=150)
    return img


title = readable_title("Colour, Cut & Style", "Chatters")
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


def view(img, cx, cy, z, ow=W, oh=H, video=False):
    iw, ih = img.size
    cw = iw * z if video else max(iw * z, ow / 1.6 if ow == W else 0)
    cw = min(cw, iw)
    ch = cw * oh / ow
    if ch > ih:
        ch = ih
        cw = ch * ow / oh
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    out = img.resize((ow, oh), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return out.filter(ImageFilter.UnsharpMask(2.2, 70, 2)) if video else out


def frame(i, t):
    kind, beats, tin, cx, cy, z0, z1, _ = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = 1 - (1 - p) ** 3 if i == 0 else p * p * (3 - 2 * p)
    if kind == "SPLIT":
        out = Image.new("RGB", (W, H))
        out.paste(view(P["before"], .50, .50, .45 - .02 * e, W // 2, H), (0, 0))
        out.paste(view(P["after"], .50, .50, .60 - .02 * e, W // 2, H), (W // 2, 0))
        ImageDraw.Draw(out).rectangle((W // 2 - 2, 0, W // 2 + 1, H), fill=(255, 255, 255))
        return out
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.07 * math.exp(-dt / 0.10)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    if kind == "V":
        return view(vframe(tin + dt), cx, cy, z, video=True)
    return view(P[kind], cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_ASMA_xmas_before_after_SILENT.mp4"], stdin=subprocess.PIPE)

WHITE = Image.new("RGBA", (W, H), (255, 255, 255, 255))
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
    d = t - starts[FLASH_AT]
    flash = max(0.0, 1 + d / 0.07) if -0.07 < d < 0 else (math.exp(-d / 0.09) if 0 <= d < 0.4 else 0.0)
    over(fr, WHITE, min(1.0, flash) * 0.95)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
