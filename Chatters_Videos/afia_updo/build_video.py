"""Afia updo before/after reel: 1080x1920, 30 fps, 94 BPM shot grid, verbatim Phorest quote. Pipes raw frames to ffmpeg."""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, BPM = 1080, 1920, 30, 94
BEAT = 60 / BPM
UP = "/root/.claude/uploads/254c4376-c66e-58d3-a800-507814c958ac/"
D = sys.path[0] + "/"
src = {"B": Image.open(UP + "401f2c2c-image.jpg").convert("RGB"),
       "A": Image.open(UP + "ad9f1d34-image.jpg").convert("RGB")}
logo = Image.open(D + "brand/logo_white.png")
F = lambda n, s: ImageFont.truetype(D + "fonts/" + n, s)
serif, script, sans = F("Playfair.ttf", 86), F("GreatVibes.ttf", 132), F("Montserrat.ttf", 54)
quote_f, small = F("Playfair.ttf", 66), F("Montserrat.ttf", 40)

# (img, beats, cx, cy, z0, z1); z=1 -> 900x1600 window (1.2x upscale); max z 1.3 keeps total <1.6x
SHOTS = [
    ("B", 3, 610, 760, 1.00, 1.06),
    ("B", 1, 560, 330, 1.28, 1.31),
    ("B", 1, 330, 1000, 1.26, 1.30),
    ("B", 1.5, 600, 650, 1.22, 1.27),
    ("B", 1, 880, 950, 1.26, 1.30),
    ("B", 1, 620, 1080, 1.28, 1.31),
    ("B", 1, 450, 500, 1.26, 1.30),
    ("B", 1, 760, 520, 1.28, 1.31),
    ("B", 1, 300, 600, 1.27, 1.30),
    ("A", 3, 590, 800, 1.08, 1.00),
    ("A", 1, 760, 640, 1.28, 1.32),
    ("A", 1, 420, 560, 1.27, 1.30),
    ("A", 1.5, 560, 900, 1.25, 1.29),
    ("A", 1, 560, 420, 1.28, 1.31),
    ("A", 1, 780, 800, 1.26, 1.30),
    ("A", 1, 600, 700, 1.22, 1.26),
    ("A", 1.5, 700, 650, 1.18, 1.24),
    ("A", 1, 380, 820, 1.27, 1.30),
    ("A", 1, 720, 960, 1.27, 1.31),
    ("A", 1, 480, 1000, 1.27, 1.30),
    ("A", 1, 820, 560, 1.28, 1.31),
    ("A", 1, 640, 520, 1.26, 1.29),
    ("A", 1.5, 600, 760, 1.10, 1.15),
    ("Q1", 5, 600, 760, 1.05, 1.10),
    ("Q2", 5, 760, 640, 1.26, 1.30),
    ("SPLIT", 4, 0, 0, 1.0, 1.04),
    ("END", 3.5, 590, 800, 1.00, 1.04),
]
XFADE = set()  # hard cuts only: dissolves hide cuts from the house pacing check

QUOTE = ["\u201cShe is talented,", "professional, and", "genuinely takes the", "time to listen to", "what I want\u2026\u201d"]

def window(img, cx, cy, z, ww=900, wh=1600, ow=W, oh=H):
    w, h = ww / z, wh / z
    x0 = min(max(cx - w / 2, 0), img.width - w); y0 = min(max(cy - h / 2, 0), img.height - h)
    return img.transform((ow, oh), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)

def ease(t): return t * t * (3 - 2 * t)

def text(base, s, font, y, a, fill=(255, 255, 255), cx=W / 2):
    if a <= 0: return
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x = cx - d.textlength(s, font=font) / 2
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 3, y + 4), s, font=font, fill=(0, 0, 0, int(170 * a)))
    d.text((x, y), s, font=font, fill=fill + (int(255 * a),))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); base.alpha_composite(layer)

def fade(t, t0, t1, f=0.3):
    if t < t0 or t > t1: return 0
    return min(1, (t - t0) / f, (t1 - t) / f)

starts, acc = [], 0
for s in SHOTS: starts.append(acc); acc += s[1] * BEAT
TOTAL = acc
TB = lambda i: starts[i]

LOWER = [  # (text, t0, t1)
    ("Before", TB(1) + 0.1, TB(9) - 0.15),
    ("After", TB(9) + 0.5, TB(13) - 0.15),
    ("Soft curled updo", TB(13) + 0.15, TB(16) - 0.15),
    ("Styled by Afia", TB(16) + 0.15, TB(23) - 0.2),
]

def render_shot(i, t):
    k, beats, cx, cy, z0, z1 = SHOTS[i]
    p = ease(min(1, max(0, (t - starts[i]) / (beats * BEAT))))
    z = z0 + (z1 - z0) * p
    if k == "SPLIT":
        f = Image.new("RGB", (W, H))
        f.paste(window(src["B"], 610, 760, z, 450, 1600, 540, 1920), (0, 0))
        f.paste(window(src["A"], 590, 760, z, 450, 1600, 540, 1920), (540, 0))
        ImageDraw.Draw(f).rectangle((538, 0, 541, H), fill=(255, 255, 255))
        return f
    img = window(src["B" if k == "B" else "A"], cx, cy, z)
    if k in ("Q1", "Q2", "END"):
        a = min(1, (t - starts[i]) / 0.5) if k != "Q2" else 1
        img = ImageEnhance.Brightness(img).enhance(1 - 0.6 * a)
    return img

def frame(n):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t)
    f = render_shot(i, t)
    if i in XFADE and t - starts[i] < 0.2:
        f = Image.blend(render_shot(i - 1, t), f, (t - starts[i]) / 0.2)
    f = f.convert("RGBA")
    a = fade(t, 0.25, TB(1) - 0.05, 0.4)
    text(f, "From down to updo", serif, 330, a)
    text(f, "With Chatters", script, 470, a)
    for s, t0, t1 in LOWER:
        text(f, s, sans, 1360, fade(t, t0, t1, 0.25))
    k = SHOTS[i][0]
    if k in ("Q1", "Q2"):  # one quote held across both shots
        a = fade(t, TB(23) + 0.35, TB(25) - 0.1, 0.35)
        lines = QUOTE
        y0 = 760 - len(lines) * 45
        for j, line in enumerate(lines):
            text(f, line, quote_f, y0 + j * 92, a)
        text(f, "Debbie D., 5-star review for Afia", small, y0 + len(lines) * 92 + 40, a)
    if k == "SPLIT":
        a = fade(t, starts[i] + 0.2, starts[i] + SHOTS[i][1] * BEAT - 0.1, 0.25)
        for s, cx in (("Before", 270), ("After", 810)):
            text(f, s, sans, 1360, a, cx=cx)
    if k == "END":
        a = fade(t, starts[i] + 0.3, TOTAL + 1, 0.5)
        L = logo.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(L, ((W - L.width) // 2, 760))
        text(f, "Afia, Senior Stylist", small, 990, a)
        text(f, "Lawson Heights Mall, Saskatoon", small, 1050, a)
    return f.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]
    N = int(round(TOTAL * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(N):
        ff.stdin.write(frame(n).tobytes())
    ff.stdin.close(); ff.wait()
    print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, {len(SHOTS)/TOTAL:.2f} cuts/s")
