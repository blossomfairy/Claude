"""Marina before/after reel (trend format: before first, white-flash snap into the reveal): 1080x1920, 30 fps,
92 BPM grid, silent master.

Sources (same mall-light grade on all): before_video.mov (478x850, 4.3 s walk-around), before_top / before_side /
after_right / after_left photos (739x1600). Background people, sale signage and a poster face are softened with a
feathered blur on the source (BLUR), never shown sharp. Photos are narrower than 9:16, so crops stay at full width
(<= 1.46x) and motion is a vertical drift; zoom never exceeds 1.6x.
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
# (x0, y0, x1, y1) regions to soften per photo
BLUR = {
    "before_top": [(0, 0, 739, 140)],              # in-store sign
    "before_side": [(0, 0, 739, 430)],             # other customers at the counter, shelf
    "after_right": [(0, 0, 739, 490)],             # sale signage / price tags
    "after_left": [(0, 0, 739, 375), (650, 375, 739, 1000)],  # poster with a face, shelves
}


def soften(img, boxes):
    blurred = img.filter(ImageFilter.GaussianBlur(22))
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    for b in boxes:
        d.rectangle(b, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(14))
    return Image.composite(blurred, img, mask)


P = {k: soften(Image.open(f"{D}/src/{k}.jpg").convert("RGB"), BLUR[k]) for k in BLUR}

if not os.path.isdir(f"{D}/src/v"):
    os.makedirs(f"{D}/src/v")
    subprocess.run(["ffmpeg", "-v", "error", "-i", f"{D}/src/before_video.mov", "-vf", f"fps=30,{GRADE}",
                    "-q:v", "2", f"{D}/src/v/%04d.jpg"], check=True)
NV = len(os.listdir(f"{D}/src/v"))


def vframe(t):
    n = min(NV, max(1, int(round(t * 30)) + 1))
    return Image.open(f"{D}/src/v/{n:04d}.jpg").convert("RGB")


# (source, beats, t_in | None, cx, cy, z0, z1, label)   z = visible width fraction of the source
SHOTS = [
    ("V", 3, 0.00, .50, .50, 1.00, .92, "Before"),          # hook: before in motion + title
    ("before_top", 1.5, None, .50, .45, 1.00, .94, None),   # grey regrowth at the part
    ("before_side", 1, None, .50, .62, 1.00, .94, None),
    ("after_left", 3, None, .50, .55, .94, 1.00, "After"),  # REVEAL (white flash in)
    ("after_right", 1, None, .50, .62, 1.00, .94, None),
    ("before_top", 1, None, .50, .40, .94, .92, "Before"),
    ("after_left", 1, None, .50, .45, .94, .92, "After"),
    ("V", 1, 2.30, .50, .50, .90, .86, "Before"),
    ("after_right", 1, None, .50, .50, .94, .92, "After"),
    ("SPLIT", 2.5, None, 0, 0, 0, 0, None),                 # before | after
    ("after_left", 1, None, .50, .70, 1.00, .94, None),
    ("after_right", 1, None, .50, .40, .94, .92, None),
    ("before_side", 1, None, .50, .70, .94, .92, "Before"),
    ("after_right", 1.5, None, .50, .55, 1.00, .94, "After"),
    ("V", 1, 3.20, .50, .50, .90, .86, "Before"),
    ("after_left", 1, None, .50, .60, 1.00, .94, "After"),
    ("after_right", 1, None, .50, .70, .94, .92, None),     # lower third from here
    ("after_left", 1, None, .50, .40, .94, .92, None),
    ("after_right", 1.5, None, .50, .55, 1.00, .94, None),
    ("after_left", 1, None, .50, .65, .94, .92, None),
    ("after_right", 1, None, .50, .45, .94, .92, None),     # lower third ends
    ("after_left", 5, None, .50, .55, .92, 1.00, None),     # reveal held, logo
]
REVEAL = 3
LOWER_FROM, LOWER_TO = 16, 21

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc
for s in SHOTS:
    assert s[0] != "V" or s[2] + s[1] * BEAT <= 4.25, s


def readable_title(text, brand, y=0.30):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=190)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=190)
    return img


def label(text, x=W // 2, size=78):
    img = ht.canvas()
    ht.shadow_text(img, (x, int(H * .80)), text, ht.sans(size, "Bold"), ht.TITLE_WHITE, blur=6, alpha=150)
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


def view(img, cx, cy, z, ow=W, oh=H, sharpen=False):
    iw, ih = img.size
    cw = iw * z if sharpen else max(iw * z, ow / 1.6 if ow == W else 0)  # 1.6x floor on photos only
    cw = min(cw, iw)
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
        out.paste(view(P["before_side"], .50, .62, .70 - .03 * e, W // 2, H), (0, 0))
        out.paste(view(P["after_left"], .50, .55, .70 - .03 * e, W // 2, H), (W // 2, 0))
        ImageDraw.Draw(out).rectangle((W // 2 - 2, 0, W // 2 + 1, H), fill=(255, 255, 255))
        return out
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.06 * math.exp(-dt / 0.11)  # beat punch
    cy += 0.004 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    if kind == "V":
        return view(vframe(tin + dt), cx, cy, z, sharpen=True)
    return view(P[kind], cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", f"{D}/CHATTERS_MARINA_colour_cut_style_SILENT.mp4"], stdin=subprocess.PIPE)

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
    d = t - starts[REVEAL]  # white flash: ramps up over 2 frames before the cut, decays ~0.25 s after
    flash = max(0.0, 1 + d / 0.07) if -0.07 < d < 0 else (math.exp(-d / 0.09) if 0 <= d < 0.4 else 0.0)
    over(fr, WHITE, min(1.0, flash) * 0.95)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
