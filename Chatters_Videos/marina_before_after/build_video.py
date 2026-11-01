"""Marina before/after reel: 1080x1920, 30 fps, 92 BPM grid, silent master.

p1 = before (side), p2-p6 = after. House style: serif title + "With Chatters" script, white bold-sans
labels and lower third, white logo over the last shot. Crops keep out the client's face (p1 cheek, p6 glasses),
the "Brow Wax $10" whiteboard (p2 top) and mirror reflections (p4/p5 top).
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(
    "~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht  # noqa: E402

W, H, FPS, BPM = 1080, 1920, 30, 92
BEAT = 60 / BPM
P = {i: Image.open(f"{D}/src/p{i}.jpg").convert("RGB") for i in range(1, 7)}
IW, IH = P[1].size  # 739x1600
XMIN = {1: 200, 6: 175}          # keep the cheek / glasses out
YMIN = {2: 175, 4: 130, 5: 130}  # whiteboard, mirror reflections

# (photo | "SPLIT", beats, cx, cy, z0, z1, label)
SHOTS = [
    (2, 2.5, .52, .55, 1.00, .94, None),      # hook: after + title (W)
    (1, 2, .62, .50, .72, .69, "Before"),     # before
    ("SPLIT", 2.5, 0, 0, 0, 0, None),         # before | after
    (3, 1, .52, .58, .95, .90, "After"),      # W
    (5, 1, .50, .50, .74, .71, None),         # T
    (4, 1, .52, .48, .95, .90, None),         # W
    (2, 1, .52, .58, .74, .71, None),         # T
    (3, 1.5, .55, .62, .74, .71, None),       # T different photo
    (1, 1, .62, .62, .72, .69, "Before"),     # before ends
    (5, 1, .52, .45, .95, .90, "After"),      # W
    (6, 1, .62, .55, .74, .71, None),         # T (no face)
    (4, 1, .52, .58, .74, .71, None),         # T
    (2, 1, .52, .52, .95, .90, None),         # W
    (1, 1, .62, .40, .72, .69, "Before"),     # before root
    (3, 1, .52, .50, .74, .71, "After"),      # T
    (5, 1.5, .52, .60, .74, .71, None),       # T, lower third from here
    (6, 1, .62, .48, .76, .73, None),
    (4, 1, .52, .45, .95, .90, None),
    (3, 1.5, .52, .55, .95, .90, None),
    (2, 1, .52, .62, .74, .71, None),         # lower third ends
    (2, 6, .52, .55, .92, 1.00, None),        # end + logo
]
LOWER_FROM, LOWER_TO = 15, 20

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc


def readable_title(text, brand, y=0.20):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=7, alpha=150)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=170)
    return img


def label(text, x=W // 2, size=78):
    img = ht.canvas()
    ht.shadow_text(img, (x, int(H * .80)), text, ht.sans(size, "Bold"), ht.TITLE_WHITE, blur=6, alpha=130)
    return img


title = readable_title("Colour, Cut & Style", "Chatters")
LABELS = {k: label(k) for k in ("Before", "After")}
SPLIT_LABELS = [label("Before", W // 4, 64), label("After", 3 * W // 4, 64)]
lower = ht.lower("Marina, Elite Stylist", "Chatters Lawson Heights", y=0.70)
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


def view(pi, cx, cy, z, ow=W, oh=H):
    xmin, ymin = XMIN.get(pi, 0), YMIN.get(pi, 0)
    cw = min(IW * z, IW - xmin)
    ch = cw * oh / ow
    if ch > IH - ymin:
        ch = IH - ymin
        cw = ch * ow / oh
    x0 = min(max(cx * IW - cw / 2, xmin), IW - cw)
    y0 = min(max(cy * IH - ch / 2, ymin), IH - ch)
    return P[pi].resize((ow, oh), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    kind, beats, cx, cy, z0, z1, _ = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = p * p * (3 - 2 * p)
    if kind == "SPLIT":
        out = Image.new("RGB", (W, H))
        out.paste(view(1, .62, .50, .60 - .03 * e, W // 2, H), (0, 0))
        out.paste(view(2, .52, .55, .62 - .03 * e, W // 2, H), (W // 2, 0))
        ImageDraw.Draw(out).rectangle((W // 2 - 2, 0, W // 2 + 1, H), fill=(255, 255, 255))
        return out
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.06 * math.exp(-dt / 0.11)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    return view(kind, cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_MARINA_before_after_SILENT.mp4"], stdin=subprocess.PIPE)

for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    lab = SHOTS[i][6]
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
