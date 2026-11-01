"""Ear piercing before/after reel (AI-generated illustration): 1080x1920, 30 fps, 92 BPM grid, silent master.

House style (chatters-house-style): serif title + "With Chatters" script, white bold-sans labels with soft shadow,
white logo over the last shot. Cuts alternate wide/close so every cut is a visible change. A wipe reveal sweeps
before -> after. A small "AI-generated image" line stays on screen the whole time (Meta AI-label rule).
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
P = {k: Image.open(f"{D}/src/{k}.png").convert("RGB") for k in ("before", "after")}
IW, IH = P["before"].size  # 752x1344
LOBE, EAR = (.46, .48), (.52, .40)

# (img | "WIPE", beats, cx, cy, z0, z1, label)  z = visible width fraction
SHOTS = [
    ("after", 3, .50, .50, 1.00, .95, None),  # hook + title
    ("before", 1, *EAR, .78, .74, "Before"),
    ("before", 1, *LOBE, .46, .43, "Before"),
    ("after", 1, .50, .50, 1.00, .95, "After"),
    ("before", 1, *LOBE, .46, .43, "Before"),
    ("after", 1, *EAR, .78, .74, "After"),
    ("before", 1, .50, .50, 1.00, .95, "Before"),
    ("after", 1.5, *LOBE, .46, .43, "After"),
    ("WIPE", 3, .50, .45, .80, .80, None),  # wipe reveal
    ("after", 1, *LOBE, .46, .43, None),  # flash
    ("after", 1, .50, .50, 1.00, .95, None),
    ("before", 1, *LOBE, .46, .43, "Before"),
    ("after", 1, *EAR, .78, .74, "After"),
    ("before", 1, .50, .50, 1.00, .95, "Before"),
    ("after", 1.5, *LOBE, .46, .43, "After"),
    ("after", 1, *EAR, .78, .74, None),  # lower third
    ("after", 1, .50, .50, 1.00, .95, None),
    ("after", 1, *LOBE, .46, .43, None),
    ("after", 1, *EAR, .78, .74, None),
    ("after", 1, *LOBE, .46, .43, None),
    ("after", 6, .50, .50, .92, 1.00, None),  # end + logo
]
starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc

title = ht.canvas()
_t = ht.fit("Ear Piercing", ht.serif, 118, int(W * 0.66))
ht.shadow_text(title, (W // 2, int(H * .20)), "Ear Piercing", _t, ht.TITLE_WHITE, blur=7, alpha=150)
_tw = _t.getlength("Ear Piercing")
from PIL import ImageDraw, ImageFilter  # noqa: E402
_x = int(W // 2 - _tw / 2 + _tw * 0.16)
# Script line in white (not house brown): the hook sits on dark brown hair, where #493836 is unreadable.
ht.shadow_text(title, (_x, int(H * .20) + 74), "With Chatters", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=170)


def label(text):
    img = ht.canvas()
    ht.shadow_text(img, (W // 2, int(H * .80)), text, ht.sans(78, "Bold"), ht.TITLE_WHITE, blur=6, alpha=130)
    return img


LABELS = {k: label(k) for k in ("Before", "After")}
lower = ht.lower("Ear Piercing · 15 min", "Chatters Lawson Heights", y=0.70)
endlogo = ht.endlogo()
ai = ht.canvas()
ht.shadow_text(ai, (W // 2, H - 150), "AI-generated image", ht.sans(30, "SemiBold"), ht.TITLE_WHITE, blur=3, alpha=120)
LOWER_T = (starts[15] + 0.1, starts[20] - 0.05)
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


def view(img, cx, cy, z):
    cw = IW * z
    ch = cw * 16 / 9
    if ch > IH:
        ch, cw = IH, IH * 9 / 16
    x0 = min(max(cx * IW - cw / 2, 0), IW - cw)
    y0 = min(max(cy * IH - ch / 2, 0), IH - ch)
    return P[img].resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    kind, beats, cx, cy, z0, z1, _ = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1 and kind != "WIPE":
        z *= 1 - 0.06 * math.exp(-dt / 0.11)  # beat punch
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    if kind != "WIPE":
        return view(kind, cx, cy, z)
    a, b = view("before", cx, cy, z), view("after", cx, cy, z)
    x = int(W * min(1.0, max(0.0, (p - 0.15) / 0.7)))  # line sweeps left -> right
    out = a.copy()
    if x:
        out.paste(b.crop((0, 0, x, H)), (0, 0))
        ImageDraw.Draw(out).rectangle((x - 2, 0, x + 2, H), fill=(255, 255, 255))
    return out


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_EAR_PIERCING_before_after_SILENT.mp4"], stdin=subprocess.PIPE)

for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    fl = max(0.0, 1 - abs(t - starts[9]) / 0.15) * 0.6  # flash after the wipe lands
    if fl > 0:
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), fl)
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    lab = SHOTS[i][6]
    if lab:
        over(fr, LABELS[lab], fade(t, starts[i] + 0.03, starts[i] + SHOTS[i][1] * BEAT - 0.03, 0.08))
    if SHOTS[i][0] == "WIPE":
        p = (t - starts[i]) / (SHOTS[i][1] * BEAT)
        over(fr, LABELS["Before"], fade(p, 0.0, 0.35, 0.08))
        over(fr, LABELS["After"], fade(p, 0.75, 1.0, 0.08))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.35))
    over(fr, ai, 1.0)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
