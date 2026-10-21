"""Festive Lucky birthday post: bunting, balloons, cake with flickering candles, round photo slot.
usage: python build2.py [--photo lucky.jpg] [--reel]   (no photo -> the cake fills the circle)"""
import argparse, math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

D = sys.path[0] + "/"
TEAL, DTEAL, AQUA, INK, GREY, WHITE = (0, 131, 141), (0, 98, 106), (169, 219, 219), (19, 18, 19), (106, 108, 106), (255, 255, 255)
FLAME, FLAME_IN = (255, 166, 48), (255, 230, 140)  # candle flames only
F = lambda n, s: ImageFont.truetype(D + "fonts/" + n, s)
logo = Image.open(D + "logo_dark.png")
SS = 3  # supersampling for sprites

def sprite(w, h, draw_fn):
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(im), SS)
    return im.resize((w, h), Image.LANCZOS)

def balloon_sprite(r, col):
    w, h = int(r * 1.8), int(r * 4.2)
    def fn(d, s):
        cx, cy, rx, ry = w * s / 2, r * 1.15 * s, r * 0.85 * s, r * 1.05 * s
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col)
        d.ellipse((cx - rx * 0.55, cy - ry * 0.7, cx - rx * 0.15, cy - ry * 0.15), fill=(255, 255, 255, 90))
        k = cy + ry
        d.polygon([(cx, k - 4 * s), (cx - 9 * s, k + 12 * s), (cx + 9 * s, k + 12 * s)], fill=col)
        pts = [(cx + 10 * s * math.sin(i / 6), k + 12 * s + i * 5 * s) for i in range(int(r * 0.4))]
        d.line(pts, fill=(120, 130, 130, 200), width=2 * s)
    return sprite(w, h, fn)

def cake_sprite(w):
    h = int(w * 0.95)
    def fn(d, s):
        W, Hh = w * s, h * s
        d.ellipse((W * 0.04, Hh * 0.86, W * 0.96, Hh * 0.99), fill=(225, 238, 238))            # plate
        def tier(x0, x1, y0, y1, body, drip):
            d.rounded_rectangle((x0, y0, x1, y1), radius=int(W * 0.03), fill=body)
            d.rectangle((x0, y0, x1, y0 + (y1 - y0) * 0.22), fill=drip)
            n = 9; step = (x1 - x0) / n
            for i in range(n):                                                                   # frosting drips
                dx = x0 + step * (i + 0.5); dl = (y1 - y0) * (0.28 + 0.18 * ((i * 7) % 3) / 2)
                d.rounded_rectangle((dx - step * 0.28, y0, dx + step * 0.28, y0 + dl), radius=int(step * 0.28), fill=drip)
            r = random.Random(int(x0))
            for _ in range(22):                                                                  # sprinkles
                sx, sy = r.uniform(x0 + 10 * s, x1 - 10 * s), r.uniform(y0 + (y1 - y0) * 0.55, y1 - 8 * s)
                d.rounded_rectangle((sx, sy, sx + 10 * s, sy + 4 * s), radius=2 * s, fill=r.choice([WHITE, AQUA, DTEAL]))
        tier(W * 0.12, W * 0.88, Hh * 0.56, Hh * 0.9, TEAL, WHITE)
        tier(W * 0.24, W * 0.76, Hh * 0.30, Hh * 0.58, AQUA, WHITE)
        for i, cx in enumerate((0.36, 0.5, 0.64)):                                              # candles
            x = W * cx; d.rounded_rectangle((x - 9 * s, Hh * 0.15, x + 9 * s, Hh * 0.31), radius=4 * s, fill=WHITE)
            for k in range(3):
                d.line((x - 9 * s, Hh * (0.18 + k * 0.045), x + 9 * s, Hh * (0.16 + k * 0.045)), fill=TEAL, width=4 * s)
    return sprite(w, h, fn), h

def flame_sprite(w):
    def fn(d, s):
        W = w * s; d.ellipse((W * 0.2, W * 0.15, W * 0.8, W * 1.35), fill=FLAME)
        d.polygon([(W * 0.5, 0), (W * 0.25, W * 0.6), (W * 0.75, W * 0.6)], fill=FLAME)
        d.ellipse((W * 0.36, W * 0.6, W * 0.64, W * 1.2), fill=FLAME_IN)
    return sprite(w, int(w * 1.4), fn).filter(ImageFilter.GaussianBlur(0.6))

def bunting(img, y, sag, t=0):
    d = ImageDraw.Draw(img, "RGBA"); w = img.width
    pts = [(x, y + sag * (1 - ((x - w / 2) / (w / 2)) ** 2)) for x in range(-20, w + 21, 10)]
    d.line(pts, fill=(90, 110, 110, 255), width=3)
    cols = [TEAL, AQUA, WHITE, DTEAL]
    for i, x in enumerate(range(10, w, 90)):
        yy = y + sag * (1 - ((x - w / 2) / (w / 2)) ** 2); sw = 3 * math.sin(t * 2 + i)
        d.polygon([(x - 34, yy), (x + 34, yy), (x + sw, yy + 78)], fill=cols[i % 4] + (255,), outline=(90, 110, 110, 255))

def confetti(w, h, n=80, seed=7):
    r = random.Random(seed)
    return [dict(x=r.uniform(0, w), y=r.uniform(0, h), s=r.uniform(8, 18), a=r.uniform(0, 6.3),
                 c=r.choice([TEAL, AQUA, DTEAL, FLAME_IN]), v=r.uniform(35, 80), round=r.random() < 0.4) for _ in range(n)]

def background(w, h):
    g = Image.linear_gradient("L").resize((w, h))
    top, bot = Image.new("RGB", (w, h), AQUA), Image.new("RGB", (w, h), WHITE)
    return Image.composite(bot, top, g.point(lambda v: min(255, int(v * 1.25)))).convert("RGBA")

def text_c(img, s, font, y, fill, a=1.0, shadow=False):
    if a <= 0: return
    lay = Image.new("RGBA", img.size); d = ImageDraw.Draw(lay)
    x = (img.width - d.textlength(s, font=font)) / 2
    if shadow:
        sh = Image.new("RGBA", img.size); ImageDraw.Draw(sh).text((x + 2, y + 4), s, font=font, fill=(255, 255, 255, int(220 * a)))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    d.text((x, y), s, font=font, fill=fill + (int(255 * a),)); img.alpha_composite(lay)

def photo_circle(photo, dia):
    p = ImageOps.fit(photo.convert("RGB"), (dia, dia), Image.LANCZOS, centering=(0.5, 0.4))
    m = Image.new("L", (dia * SS, dia * SS)); ImageDraw.Draw(m).ellipse((0, 0, dia * SS, dia * SS), fill=255)
    out = Image.new("RGBA", (dia, dia)); out.paste(p, (0, 0), m.resize((dia, dia), Image.LANCZOS)); return out

class Card:
    def __init__(self, w, h, photo=None):
        self.w, self.h, self.photo = w, h, photo
        tall = h > 1500; k = 1.0 if tall else 0.75; self.k = k
        self.L = (dict(bunt=110, script=290, name=390, cy=940, dia=500, msg=1240, sign=1415, logo=1590) if tall else
                  dict(bunt=30, script=120, name=215, cy=655, dia=405, msg=905, sign=1065, logo=1195))
        self.bg = background(w, h)
        self.ring = sprite(self.L["dia"] + 40, self.L["dia"] + 40, lambda d, s: (
            d.ellipse((0, 0, (self.L["dia"] + 40) * s, (self.L["dia"] + 40) * s), fill=TEAL),
            d.ellipse((10 * s, 10 * s, (self.L["dia"] + 30) * s, (self.L["dia"] + 30) * s), fill=WHITE)))
        self.inner = photo_circle(photo, self.L["dia"]) if photo else None
        cw = int((300 if photo else self.L["dia"] * 0.78) * k) if photo else int(self.L["dia"] * 0.78)
        self.cake, self.cake_h = cake_sprite(cw); self.cw = cw
        self.flame = flame_sprite(max(14, int(cw * 0.07)))
        self.balloons = [(balloon_sprite(int(r * k), c), x, y, ph) for r, c, x, y, ph in
                         [(70, TEAL, 0.10, 0.48, 0.0), (58, AQUA, 0.20, 0.55, 1.3), (52, DTEAL, 0.06, 0.62, 2.1),
                          (70, AQUA, 0.90, 0.47, 0.7), (58, TEAL, 0.80, 0.56, 2.6), (52, (210, 236, 236), 0.94, 0.63, 1.8)]]
        self.conf = confetti(w, h)
        self.f_script, self.f_name = F("GreatVibes.ttf", int(150 * k)), F("Playfair.ttf", int(200 * k))
        self.f_body, self.f_sign = F("Montserrat.ttf", int(44 * k)), F("GreatVibes.ttf", int(92 * k))

    def render(self, t=None):
        L, w, h, k = self.L, self.w, self.h, self.k
        tt = 0 if t is None else t
        fa = lambda t0: 1.0 if t is None else max(0, min(1, (t - t0) / 0.6))
        img = self.bg.copy(); d = ImageDraw.Draw(img, "RGBA")
        for p in self.conf:                                                                       # confetti
            y = (p["y"] + p["v"] * tt) % (h + 40) - 20; x = p["x"] + 10 * math.sin(tt * 1.2 + p["a"])
            if L["script"] - 30 < y < L["logo"] + 130 and 150 < x < w - 150: continue
            s = p["s"]
            if p["round"]: d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=p["c"] + (220,))
            else: d.rounded_rectangle((x - s / 2, y - s / 5, x + s / 2, y + s / 5), radius=2, fill=p["c"] + (220,))
        bunting(img, L["bunt"], 60 * k, tt)
        for spr, fx, fy, ph in self.balloons:                                                    # balloons bob
            img.alpha_composite(spr, (int(fx * w - spr.width / 2), int(fy * h - spr.height / 2 + 14 * math.sin(tt * 1.1 + ph))))
        r = self.ring; img.alpha_composite(r, ((w - r.width) // 2, L["cy"] - r.height // 2))
        if self.inner:
            img.alpha_composite(self.inner, ((w - L["dia"]) // 2, L["cy"] - L["dia"] // 2))
            cx, cy = w // 2 + int(L["dia"] * 0.36), L["cy"] + int(L["dia"] * 0.28)               # cake "sticker"
        else:
            cx, cy = w // 2, L["cy"] - self.cake_h // 2 + int(L["dia"] * 0.08)
            cy += self.cake_h // 2
        x0, y0 = cx - self.cw // 2, cy - self.cake_h // 2
        img.alpha_composite(self.cake, (x0, y0))
        for i, fx in enumerate((0.36, 0.5, 0.64)):                                               # flickering flames
            sc = 1 + 0.12 * math.sin(tt * 11 + i * 2.1) + 0.06 * math.sin(tt * 23 + i)
            fl = self.flame.resize((self.flame.width, max(2, int(self.flame.height * sc))))
            img.alpha_composite(fl, (int(x0 + self.cw * fx - fl.width / 2), int(y0 + self.cake_h * 0.155 - fl.height)))
        text_c(img, "Happy birthday", self.f_script, L["script"], TEAL, fa(0.3), shadow=True)
        text_c(img, "Lucky", self.f_name, L["name"], INK, fa(0.9), shadow=True)
        for i, line in enumerate(["Wishing you the sweetest birthday", "while you enjoy maternity leave.", "We miss you at Lawson Heights!"]):
            text_c(img, line, self.f_body, L["msg"] + i * int(62 * k), GREY, fa(2.0 + 0.3 * i))
        text_c(img, "Love, your Chatters family", self.f_sign, L["sign"], TEAL, fa(3.4))
        lg = logo.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * fa(4.0))))
        img.alpha_composite(lg, ((w - lg.width) // 2, L["logo"]))
        return img.convert("RGB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--photo"); ap.add_argument("--reel", action="store_true"); a = ap.parse_args()
    photo = Image.open(a.photo) if a.photo else None
    tag = "_photo" if photo else ""
    Card(1080, 1350, photo).render().save(D + f"CHATTERS_LUCKY_birthday_festive{tag}_feed_4x5.jpg", quality=95)
    story = Card(1080, 1920, photo); story.render().save(D + f"CHATTERS_LUCKY_birthday_festive{tag}_story_9x16.jpg", quality=95)
    if a.reel:
        FPS, DUR = 30, 16.5
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                               "-i", "-", "-i", D + "hb.wav", "-af", "apad,atrim=0:16.5,afade=t=out:st=15.5:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k",
                               "-ar", "48000", "-shortest", "-movflags", "+faststart", D + f"CHATTERS_LUCKY_birthday_festive{tag}_reel.mp4"],
                              stdin=subprocess.PIPE)
        for n in range(int(DUR * FPS)):
            ff.stdin.write(story.render(n / FPS).tobytes())
        ff.stdin.close(); ff.wait()
