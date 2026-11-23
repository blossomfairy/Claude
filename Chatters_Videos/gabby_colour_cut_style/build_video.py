"""Gabby colour + cut + style after-photo reel: 1080x1920, 30 fps, 92 BPM grid, silent master.

4 after photos (1200x1600), pre-graded with the same mall-light correction. House style: serif title +
"With Chatters" script, white bold-sans lower third, white logo over the last shot.
Crop bounds keep out: the phone + pink poster on p1, the promo poster face and mirror reflection on p3,
and the other client in the next chair on p4. Zoom <= 1.6x.
"""
import math
import os
import subprocess
import sys

from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(
    "~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht  # noqa: E402

W, H, FPS, BPM = 1080, 1920, 30, 92
BEAT = 60 / BPM
P = {i: Image.open(f"{D}/src/p{i}.jpg").convert("RGB") for i in range(1, 5)}
IW, IH = P[1].size  # 1200x1600
# allowed source window per photo: (xmin, xmax, ymin)
BOUNDS = {1: (150, 1200, 130), 2: (0, 1200, 0), 3: (110, 1010, 215), 4: (0, 810, 0)}
MIN_CW = W / 1.6  # 675 px -> max 1.6x upscale

# (photo, beats, cx, cy, z0, z1)   z = visible width as a fraction of the allowed window
SHOTS = [
    (1, 2.5, .50, .45, 1.00, .95),  # hook: full after + title
    (3, 1, .50, .55, .85, .80),
    (2, 1, .55, .45, .85, .80),
    (4, 1.5, .50, .55, .95, .90),
    (1, 1, .45, .75, .80, .76),     # wave ends
    (3, 1, .50, .35, .80, .76),     # crown shine
    (2, 1, .40, .70, .80, .76),
    (4, 1, .45, .40, .90, .86),
    (1, 1.5, .55, .30, .80, .76),   # root to mid
    (3, 1, .45, .75, .80, .76),
    (2, 1, .60, .35, .85, .80),
    (4, 1, .50, .75, .90, .86),
    (1, 1, .40, .55, .80, .76),
    (3, 1.5, .55, .50, .95, .90),
    (2, 1, .35, .55, .80, .76),
    (4, 1, .55, .35, .90, .86),
    (3, 1, .40, .60, .85, .80),
    (4, 1, .55, .50, .85, .80),
    (1, 1, .60, .60, .82, .78),     # lower third from here
    (3, 1, .50, .70, .85, .80),
    (2, 1.5, .50, .50, .95, .90),
    (4, 1, .45, .60, .95, .90),
    (3, 1, .50, .45, .88, .84),     # lower third ends
    (1, 5, .50, .40, .88, .96),     # reveal held, pull back, logo
]
LOWER_FROM, LOWER_TO = 18, 23

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc


def readable_title(text, brand, y=0.37):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=190)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=190)
    return img


title = readable_title("Colour, Cut & Style", "Chatters")
lower = ht.lower("Gabby", "Chatters Lawson Heights", y=0.70)
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


def view(pi, cx, cy, z):
    xmin, xmax, ymin = BOUNDS[pi]
    aw, ah = xmax - xmin, IH - ymin
    cw = aw * z
    ch = cw * H / W
    if ch > ah:
        ch = ah
        cw = ch * W / H
    cw = max(cw, MIN_CW)
    ch = cw * H / W
    assert cw <= aw + 1 and ch <= ah + 1, (pi, cw, ch)
    x0 = min(max(xmin + cx * aw - cw / 2, xmin), xmax - cw)
    y0 = min(max(ymin + cy * ah - ch / 2, ymin), IH - ch)
    return P[pi].resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    pi, beats, cx, cy, z0, z1 = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.06 * math.exp(-dt / 0.11)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    return view(pi, cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_GABBY_colour_cut_style_SILENT.mp4"], stdin=subprocess.PIPE)

for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.35))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
