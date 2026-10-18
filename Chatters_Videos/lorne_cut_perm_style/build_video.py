"""Lorne cut + perm + style reel: 1080x1920, 30 fps, 92 BPM shot grid. Pipes raw frames to ffmpeg."""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, BPM = 1080, 1920, 30, 92
BEAT = 60 / BPM
UP = "/root/.claude/uploads/254c4376-c66e-58d3-a800-507814c958ac/"
D = sys.path[0] + "/"
src = {k: Image.open(UP + f).convert("RGB") for k, f in {
    "B1": "76dac5aa-image.jpg", "B2": "7bd17ccc-image.jpg", "P": "0ad19bb9-image.jpg",
    "A1": "f01c9743-image.jpg", "A2": "50c90c19-image.jpg", "A3": "142fc8e1-image.jpg"}.items()}
logo = Image.open(D + "brand/logo_white.png")
F = lambda n, s: ImageFont.truetype(D + "fonts/" + n, s)
serif, script, sans = F("Playfair.ttf", 86), F("GreatVibes.ttf", 132), F("Montserrat.ttf", 54)
small = F("Montserrat.ttf", 40)

# (img, beats, cx, cy, z0, z1); z=1 -> 900x1600 window (1.2x upscale); max z 1.3 keeps total <1.6x
SHOTS = [
    ("B1", 3.5, 640, 800, 1.00, 1.07),
    ("B1", 1.5, 620, 900, 1.28, 1.32),
    ("B2", 1.5, 640, 800, 1.00, 1.05),
    ("B2", 1, 600, 600, 1.28, 1.30),
    ("B2", 1.5, 650, 1150, 1.25, 1.30),
    ("B1", 1, 650, 520, 1.28, 1.32),
    ("B2", 1, 720, 450, 1.25, 1.28),
    ("P", 2, 600, 800, 1.00, 1.06),
    ("P", 1, 600, 420, 1.26, 1.31),
    ("P", 1, 760, 800, 1.25, 1.28),
    ("P", 1.5, 520, 1050, 1.30, 1.32),
    ("P", 1, 420, 700, 1.25, 1.28),
    ("P", 1, 780, 450, 1.28, 1.30),
    ("A2", 3, 790, 800, 1.08, 1.00),
    ("A2", 1, 700, 1150, 1.28, 1.32),
    ("A2", 1, 800, 750, 1.25, 1.28),
    ("A1", 1.5, 480, 800, 1.00, 1.05),
    ("A1", 1, 500, 1250, 1.28, 1.30),
    ("A1", 1, 450, 600, 1.28, 1.32),
    ("A3", 1.5, 640, 800, 1.00, 1.05),
    ("A3", 1, 600, 650, 1.28, 1.30),
    ("A3", 1, 650, 1300, 1.25, 1.30),
    ("A2", 1, 720, 460, 1.28, 1.32),
    ("A1", 1, 520, 950, 1.25, 1.28),
    ("A3", 1.5, 680, 1000, 1.25, 1.28),
    ("SPLIT", 4, 0, 0, 1.0, 1.04),
    ("END", 3.5, 790, 800, 1.00, 1.04),
]
XFADE = {7, 13}  # soft 6-frame dissolves into process and reveal; hard cut into the comparison

def window(img, cx, cy, z, ww=900, wh=1600, ow=W, oh=H):
    w, h = ww / z, wh / z
    x0 = min(max(cx - w / 2, 0), img.width - w); y0 = min(max(cy - h / 2, 0), img.height - h)
    return img.transform((ow, oh), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)

def ease(t): return t * t * (3 - 2 * t)

def text(base, s, font, y, a, fill=(255, 255, 255)):
    if a <= 0: return
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    tw = d.textlength(s, font=font); x = (W - tw) / 2
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 3, y + 4), s, font=font, fill=(0, 0, 0, int(170 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    d.text((x, y), s, font=font, fill=fill + (int(255 * a),))
    base.alpha_composite(sh); base.alpha_composite(layer)

def fade(t, t0, t1, f=0.3):
    if t < t0 or t > t1: return 0
    return min(1, (t - t0) / f, (t1 - t) / f)

starts, acc = [], 0
for s in SHOTS: starts.append(acc); acc += s[1] * BEAT
TOTAL = acc
TB = lambda i: starts[i]  # shot start (s)

LOWER = [  # (text, t0, t1)
    ("Before", TB(1) + 0.1, TB(7) - 0.15),
    ("The perm wrap", TB(7) + 0.3, TB(13) - 0.2),
    ("After", TB(13) + 0.5, TB(16) - 0.15),
    ("Soft, defined curls", TB(16) + 0.15, TB(20) - 0.15),
    ("Cut, perm & style by Lorne", TB(20) + 0.15, TB(25) - 0.2),
]

def render_shot(i, t):
    k, beats, cx, cy, z0, z1 = SHOTS[i]
    p = ease(min(1, max(0, (t - starts[i]) / (beats * BEAT))))
    z = z0 + (z1 - z0) * p
    if k == "SPLIT":
        f = Image.new("RGB", (W, H))
        f.paste(window(src["B1"], 640, 800, z, 450, 1600, 540, 1920), (0, 0))
        f.paste(window(src["A2"], 760, 800, z, 450, 1600, 540, 1920), (540, 0))
        ImageDraw.Draw(f).rectangle((538, 0, 541, H), fill=(255, 255, 255))
        return f
    img = window(src["A2" if k == "END" else k], cx, cy, z)
    if k == "END":
        a = min(1, (t - starts[i]) / 0.5)
        img = ImageEnhance.Brightness(img).enhance(1 - 0.55 * a)
    return img

def frame(n):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t)
    f = render_shot(i, t)
    if i in XFADE and t - starts[i] < 0.2:
        f = Image.blend(render_shot(i - 1, t), f, (t - starts[i]) / 0.2)
    f = f.convert("RGBA")
    a = fade(t, 0.25, TB(1) - 0.05, 0.4)
    text(f, "Cut, perm & style", serif, 330, a)
    text(f, "With Chatters", script, 470, a)
    for s, t0, t1 in LOWER:
        text(f, s, sans, 1360, fade(t, t0, t1, 0.25))
    if SHOTS[i][0] == "SPLIT":
        a = fade(t, starts[i] + 0.2, starts[i] + SHOTS[i][1] * BEAT - 0.1, 0.25)
        for s, cx in (("Before", 270), ("After", 810)):
            lay = Image.new("RGBA", f.size); d = ImageDraw.Draw(lay)
            d.text((cx - d.textlength(s, font=sans) / 2, 1360), s, font=sans, fill=(255, 255, 255, int(255 * a)))
            sh = Image.new("RGBA", f.size); ImageDraw.Draw(sh).text((cx - d.textlength(s, font=sans) / 2 + 3, 1364), s, font=sans, fill=(0, 0, 0, int(170 * a)))
            f.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6))); f.alpha_composite(lay)
    if SHOTS[i][0] == "END":
        a = fade(t, starts[i] + 0.3, TOTAL + 1, 0.5)
        L = logo.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(L, ((W - L.width) // 2, 760))
        text(f, "Lorne, Elite Stylist", small, 990, a)
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
