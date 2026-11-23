"""Asma layered cut & style reel, built to be hard to skip: 1080x1920, 30 fps, 92 BPM grid, silent master.

Hook (gene research 2026-11-20 + house style): frame 1 is already moving (tight crop on the layers whipping out to
the full shape) under the serif title, then four half-beat cuts in the first 3 s, beat punches, a flash accent at the
drop, and the last shot lands on the hook framing so the replay loops seamlessly.
6 after photos (1500x2000), same mall-light grade. Privacy: mirror reflection of a stylist + poster face (p1) and
"$25" signage (p5, p6) are blurred on the source; p5/p6 crops stop before the client's profile. Zoom <= 1.6x.
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
SOFTEN = {1: [(1000, 250, 1500, 720)],
          5: [(60, 600, 280, 820), (1290, 480, 1500, 660)],
          6: [(80, 520, 250, 680), (1320, 480, 1500, 640)]}
BOUNDS = {1: (0, 1180, 0), 5: (430, 1500, 0), 6: (420, 1500, 0)}  # (xmin, xmax, ymin): keep the client's profile out
MIN_CW = W / 1.6


def soften(img, boxes):
    blurred = img.filter(ImageFilter.GaussianBlur(40))
    mask = Image.new("L", img.size, 0)
    for b in boxes:
        ImageDraw.Draw(mask).rectangle(b, fill=255)
    return Image.composite(blurred, img, mask.filter(ImageFilter.GaussianBlur(14)))


P = {}
for i in range(1, 7):
    im = Image.open(f"{D}/src/p{i}.jpg").convert("RGB")
    P[i] = soften(im, SOFTEN[i]) if i in SOFTEN else im
IW, IH = P[1].size

HOOK = (4, .52, .45)  # photo, cx, cy of the hook framing (the replay lands back here)
# (photo, beats, cx, cy, z0, z1)   z = visible width as a fraction of the allowed window
SHOTS = [
    (4, 2.5, .52, .40, .46, .72),   # hook: tight on the layers -> whips out to the shape, title
    (3, .5, .45, .40, .55, .52),    # half-beat burst x4
    (2, .5, .50, .45, .60, .57),
    (1, .5, .50, .40, .62, .59),
    (6, .5, .50, .42, .75, .70),
    (5, 1, .50, .45, .75, .70),     # FLASH accent on the drop
    (3, 1, .55, .55, .62, .58),
    (2, 1, .45, .62, .62, .58),
    (4, 1, .45, .60, .60, .56),
    (1, 1.5, .50, .55, .66, .62),
    (6, 1, .55, .40, .70, .66),
    (3, 1, .40, .40, .55, .52),
    (2, 1, .55, .40, .58, .55),
    (5, 1, .60, .55, .70, .66),
    (4, 1, .60, .45, .55, .52),
    (1, 1, .45, .45, .60, .57),
    (6, 1.5, .50, .55, .75, .70),
    (3, 1, .60, .62, .62, .58),
    (4, 1, .40, .40, .62, .58),
    (5, 1, .50, .65, .72, .68),
    (2, 1, .50, .55, .70, .66),     # lower third from here
    (3, 1, .50, .50, .70, .66),
    (5, 1, .55, .50, .75, .70),
    (1, 1, .50, .50, .72, .68),
    (6, 1, .50, .45, .72, .68),
    (2, 1, .45, .50, .66, .62),     # lower third ends
    (HOOK[0], 5, HOOK[1], .48, .74, .52),  # end: logo, pushes back in to the hook's tight framing -> loop
]
FLASH_AT, LOWER_FROM, LOWER_TO = 5, 20, 26

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc


def readable_title(text, brand, y=0.36):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=200)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=200)
    return img


title = readable_title("Layered Cut & Style", "Chatters")
lower = ht.lower("Asma", "Chatters Lawson Heights", y=0.70)
endlogo = ht.endlogo()
LOWER_T = (starts[LOWER_FROM] + 0.1, starts[LOWER_TO] - 0.05)
END_T = (starts[-1] + 0.4, starts[-1] + 5 * BEAT - 0.35)  # logo fades out before the loop point


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


def view(pi, cx, cy, z):
    xmin, xmax, ymin = BOUNDS.get(pi, (0, IW, 0))
    aw, ah = xmax - xmin, IH - ymin
    cw = max(aw * z, MIN_CW)
    ch = cw * H / W
    if ch > ah:
        ch = ah
        cw = ch * W / H
    x0 = min(max(xmin + cx * aw - cw / 2, xmin), xmax - cw)
    y0 = min(max(ymin + cy * ah - ch / 2, ymin), IH - ch)
    return P[pi].resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    pi, beats, cx, cy, z0, z1 = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = 1 - (1 - p) ** 3 if i == 0 else p * p * (3 - 2 * p)  # hook whips out fast, then settles
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.07 * math.exp(-dt / 0.10)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    return view(pi, cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_ASMA_layers_cut_style_SILENT.mp4"], stdin=subprocess.PIPE)

WHITE = Image.new("RGBA", (W, H), (255, 255, 255, 255))
for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.3))
    d = t - starts[FLASH_AT]
    flash = max(0.0, 1 + d / 0.07) if -0.07 < d < 0 else (math.exp(-d / 0.08) if 0 <= d < 0.35 else 0.0)
    over(fr, WHITE, min(1.0, flash) * 0.9)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
