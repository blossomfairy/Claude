"""Chatters Black Friday reel: 1080x1920, 30 fps, silent (add trending audio in-app)."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SK = "/root/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638"
MONT = f"{SK}/chatters-house-style/assets/fonts/Montserrat-wght.ttf"
LOGO = Image.open(f"{SK}/chatters-house-style/assets/logo_white.png").convert("RGBA")
GOLD, GOLD2, GREEN, WHITE = (236, 210, 168), (196, 160, 110), (16, 74, 44), (255, 255, 255)


def font(size, w="Bold"):
    f = ImageFont.truetype(MONT, size)
    f.set_variation_by_name(w)
    return f


def cover(path):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def square_fill(path):
    sq = Image.open(path).convert("RGB")
    bg = cover(path).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.25)
    sq = sq.resize((W, W), Image.LANCZOS)
    bg.paste(sq, (0, (H - W) // 2))
    return bg


def ease_out(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def pop(t):  # 0 -> 1.15 -> 1 over 0.3 s
    if t <= 0: return 0
    if t < 0.18: return 1.15 * ease_out(t / 0.18)
    if t < 0.3: return 1.15 - 0.15 * ((t - 0.18) / 0.12)
    return 1.0


def fit_font(text, size, w, maxw=900):
    while size > 20 and font(size, w).getlength(text) > maxw:
        size -= 2
    return font(size, w)


def text_layer(lines):
    """lines: [(text, size, weight, fill, y)] centred, soft shadow."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sh)
    for text, size, w, fill, y in lines:
        f = fit_font(text, size, w)
        x = (W - f.getlength(text)) / 2
        ds.text((x + 4, y + 6), text, font=f, fill=(0, 0, 0, 200))
        d.text((x, y), text, font=f, fill=fill)
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(sh, lay)


def sticker(big, small, r=112):
    s = Image.new("RGBA", (r * 2 + 20, r * 2 + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.ellipse((14, 18, 14 + 2 * r, 18 + 2 * r), fill=(0, 0, 0, 110))
    s = s.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(s)
    for i in range(r, 0, -1):  # radial gold gradient
        k = i / r
        c = tuple(round(GOLD[j] * (1 - k * 0.35) + GOLD2[j] * k * 0.35) for j in range(3))
        d.ellipse((10 + r - i, 10 + r - i, 10 + r + i, 10 + r + i), fill=c)
    fb, fs = font(int(r * 0.6), "ExtraBold"), fit_font(small, int(r * 0.3), "ExtraBold", maxw=r * 1.6)
    cx = 10 + r
    d.text((cx, cx - r * 0.18), big, font=fb, fill=GREEN, anchor="mm")
    d.text((cx, cx + r * 0.42), small, font=fs, fill=GREEN, anchor="mm")
    return s.rotate(-8, resample=Image.BICUBIC, expand=True)


# ---------- scenes ----------
hero = cover("img/hero50.jpg")
hook_bg = Image.blend(hero.filter(ImageFilter.GaussianBlur(28)), Image.new("RGB", (W, H), (6, 30, 18)), 0.45)
hook_txt = [
    text_layer([("5 BLACK FRIDAY", 118, "ExtraBold", WHITE, 700)]),
    text_layer([("STEALS AT CHATTERS", 92, "ExtraBold", GOLD, 840)]),
    text_layer([("wait for #5", 64, "SemiBold", WHITE, 1010)]),
]

cta_bg = Image.new("RGB", (W, H), (0, 0, 0))
lg = LOGO.resize((640, round(LOGO.height * 640 / LOGO.width)), Image.LANCZOS)
cta_bg.paste(lg, ((W - 640) // 2, 560), lg)
cta_txt = [
    text_layer([("Send this to your", 70, "SemiBold", WHITE, 900)]),
    text_layer([("Black Friday buddy", 82, "ExtraBold", GOLD, 990)]),
    text_layer([("Exclusions apply. While supplies last.", 34, "Medium", (200, 200, 200), 1420)]),
]

# (kind, duration, base image, sticker(big, small) or None, sticker centre)
SCENES = [
    ("hook", 2.6, hook_bg, None, None),
    ("img", 2.4, hero, None, None),
    ("img", 2.4, cover("img/redken.jpg"), ("#1", "SAVE $18.90"), (950, 1160)),
    ("img", 2.4, cover("img/moroccanoil.jpg"), ("#2", "SAVE $31.20"), (950, 1160)),
    ("img", 2.6, cover("img/colour30.jpg"), ("#3", "SAVE 30%"), (930, 1260)),
    ("img", 2.4, square_fill("img/brow25.jpg"), ("#4", "$25 BROWS"), (900, 300)),
    ("img", 2.8, cover("img/vibe_iron.jpg"), ("#5", "SAVE $91"), (920, 1180)),
    ("cta", 3.4, cta_bg, None, None),
]
TOTAL = sum(s[1] for s in SCENES)
STK = {i: sticker(*s[3]) for i, s in enumerate(SCENES) if s[3]}


def frame(i, t, sc):
    kind, dur, base, stk, pos = sc
    p = t / dur
    # punch-in on cut, then slow push
    z = 1.0 + 0.06 * p + 0.10 * (1 - ease_out(t / 0.25))
    if kind == "cta": z = 1.0
    zw, zh = round(W * z), round(H * z)
    im = base.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
    # micro-shake on payoff deal
    if i == 6 and 0.3 < t < 0.6:
        dx = round(10 * math.sin(t * 90))
        im = im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, 0))
    im = im.convert("RGBA")
    if kind in ("hook", "cta"):
        layers = hook_txt if kind == "hook" else cta_txt
        for k, L in enumerate(layers):
            lt = t + 0.25 - 0.25 * k if kind == "hook" else t - 0.15 - 0.25 * k
            if lt <= 0: continue
            a = ease_out(lt / 0.25)
            dy = round(40 * (1 - a))
            L2 = L.transform(L.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy))
            if a < 1:
                L2.putalpha(L2.getchannel("A").point(lambda v: int(v * a)))
            im = Image.alpha_composite(im, L2)
    if stk:
        s = pop(t - 0.35)
        if s > 0:
            st = STK[i]
            st = st.resize((max(1, round(st.width * s)), max(1, round(st.height * s))), Image.BILINEAR)
            im.alpha_composite(st, (pos[0] - st.width // 2, pos[1] - st.height // 2))
    # white flash on cut
    if t < 0.1 and i > 0:
        im = Image.blend(im, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.55 * (1 - t / 0.1))
    return im


def main(out):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    g = 0
    elapsed = 0.0
    for i, sc in enumerate(SCENES):
        n = round(sc[1] * FPS)
        for f in range(n):
            t = f / FPS
            im = frame(i, t, sc).convert("RGB")
            # gold progress bar (retention cue)
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, round(W * (elapsed + t) / TOTAL), 9), fill=GOLD)
            ff.stdin.write(im.tobytes())
            g += 1
        elapsed += sc[1]
    ff.stdin.close()
    ff.wait()
    print(f"{out}: {g} frames, {TOTAL:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/chatters_black_friday_reel.mp4")
