"""Joint Afia + Rose birthday post: background-removed portraits on a studio backdrop inside two arch frames,
with the festive pieces from the Lucky post. Outputs feed 4:5, story 9:16 and a 16.5 s reel."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(1, sys.path[0] + "/../lucky")
from build2 import (TEAL, DTEAL, AQUA, INK, GREY, WHITE, F, SS, sprite, balloon_sprite, cake_sprite, flame_sprite,
                    bunting, confetti, background, text_c, logo)

D = sys.path[0] + "/"
PEOPLE = [("Afia", ["afia1", "afia2"]), ("Rose", ["rose1", "rose3"])]  # (name, zoom) zooms a close selfie out

def studio(w, h):
    """Portrait-studio backdrop: soft light behind the head falling off to a deep teal-grey, fine canvas grain."""
    yy, xx = [Image.linear_gradient("L").resize((w, h)), Image.linear_gradient("L").rotate(90, expand=True).resize((w, h))]
    r = Image.radial_gradient("L").resize((int(w * 1.3), int(h * 1.25)))
    r = r.crop((int(w * 0.15), int(h * 0.2), int(w * 0.15) + w, int(h * 0.2) + h))  # light centred behind the head
    light, dark = Image.new("RGB", (w, h), (196, 212, 210)), Image.new("RGB", (w, h), (52, 78, 82))
    bg = Image.composite(dark, light, r.point(lambda v: min(255, int(v * 1.7))))
    noise = Image.effect_noise((w, h), 28).filter(ImageFilter.GaussianBlur(1.2)).convert("RGB")
    return Image.blend(bg, noise, 0.06).convert("RGBA")

def arch_mask(w, h):
    m = Image.new("L", (w * SS, h * SS)); d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, w * SS, h * SS), radius=w * SS // 2, fill=255)
    d.rectangle((0, h * SS // 2, w * SS, h * SS), fill=255)
    return m.resize((w, h), Image.LANCZOS)

def portrait(name, w, h, zoom=1.0):
    """Cutout scaled to fill the frame width, bottom-anchored; whatever runs past the top is clipped by the arch."""
    cut = Image.open(D + f"cut/{name}.png")
    s = max(w * 1.02 / cut.width, h * 0.82 / cut.height) * zoom
    if zoom < 1:  # zoomed-out selfie: oval soft-edge vignette hides where the photo itself cut the hair and body off
        a = cut.getchannel("A"); fade = Image.new("L", cut.size, 0)
        ImageDraw.Draw(fade).ellipse((cut.width * 0.08, -cut.height * 0.1, cut.width * 0.92, cut.height * 0.94), fill=255)
        fade = fade.filter(ImageFilter.GaussianBlur(cut.width * 0.06))
        cut.putalpha(Image.composite(a, Image.new("L", a.size, 0), fade))
    cut = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
    img = studio(w, h)
    shadow = Image.new("RGBA", (w, h)); a = cut.getchannel("A").filter(ImageFilter.GaussianBlur(14))
    sh = Image.new("RGBA", cut.size, (20, 35, 38, 0)); sh.putalpha(a.point(lambda v: int(v * 0.45)))
    x, y = (w - cut.width) // 2, (h - cut.height if zoom >= 1 else int(h * 0.12))  # zoomed: head at the same height as the others
    shadow.alpha_composite(sh, (x + 10, y + 6)); img.alpha_composite(shadow); img.alpha_composite(cut, (x, y))
    return img

class Card:
    def __init__(self, w, h):
        self.w, self.h = w, h; tall = h > 1500
        self.L = (dict(bunt=110, script=270, name=380, fw=460, fh=640, fy=640, label=1300, msg=1395, sign=1470, logo=1610) if tall else
                  dict(bunt=30, script=110, name=200, fw=400, fh=540, fy=410, label=965, msg=1040, sign=1105, logo=1215))
        L = self.L; self.gap = 50
        self.mask = arch_mask(L["fw"], L["fh"])
        self.frames = [[portrait(*((n, L["fw"], L["fh"]) if isinstance(n, str) else (n[0], L["fw"], L["fh"], n[1]))) for n in names] for _, names in PEOPLE]
        ring = L["fw"] + 24
        self.border = sprite(ring, L["fh"] + 24, lambda d, s: d.rounded_rectangle(
            (0, 0, ring * s, (L["fh"] + 24) * s), radius=ring * s // 2, fill=TEAL))
        self.bg = background(w, h)
        self.cake, self.cake_h = cake_sprite(250); self.cw = 250; self.flame = flame_sprite(18)
        self.balloons = [(balloon_sprite(r, c), x, y, ph) for r, c, x, y, ph in
                         ([(56, TEAL, 0.06, 0.20, 0.0), (56, AQUA, 0.94, 0.20, 0.7),
                           (46, AQUA, 0.09, 0.84, 1.3), (46, DTEAL, 0.91, 0.84, 2.6)] if tall else [(40, TEAL, 0.05, 0.16, 0.0), (40, AQUA, 0.95, 0.16, 0.7)])]
        self.conf = confetti(w, h, 70, seed=11)
        k = 1.0 if tall else 0.85
        self.f_script, self.f_name = F("GreatVibes.ttf", int(140 * k)), F("Playfair.ttf", int(150 * k))
        self.f_label, self.f_body, self.f_sign = F("Playfair.ttf", int(64 * k)), F("Montserrat.ttf", int(42 * k)), F("GreatVibes.ttf", int(84 * k))

    def render(self, t=None):
        L, w, h = self.L, self.w, self.h; tt = 0 if t is None else t
        fa = lambda t0: 1.0 if t is None else max(0, min(1, (t - t0) / 0.6))
        img = self.bg.copy(); d = ImageDraw.Draw(img, "RGBA")
        for p in self.conf:
            y = (p["y"] + p["v"] * tt) % (h + 40) - 20; x = p["x"] + 10 * math.sin(tt * 1.2 + p["a"])
            if L["script"] - 30 < y < L["logo"] + 130 and 120 < x < w - 120: continue
            s = p["s"]
            if p["round"]: d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=p["c"] + (220,))
            else: d.rounded_rectangle((x - s / 2, y - s / 5, x + s / 2, y + s / 5), radius=2, fill=p["c"] + (220,))
        bunting(img, L["bunt"], 55, tt)
        for spr, fx, fy, ph in self.balloons:
            img.alpha_composite(spr, (int(fx * w - spr.width / 2), int(fy * h - spr.height / 2 + 12 * math.sin(tt * 1.1 + ph))))
        x0 = (w - 2 * L["fw"] - self.gap) // 2
        for i, ((label, _), pics) in enumerate(zip(PEOPLE, self.frames)):
            fx = x0 + i * (L["fw"] + self.gap)
            hold, xf = 3.6, 0.5; j = int((tt + i * 1.8) // hold) % len(pics); pic = pics[j]
            if t is not None and len(pics) > 1 and (tt + i * 1.8) % hold > hold - xf:
                pic = Image.blend(pic, pics[(j + 1) % len(pics)], ((tt + i * 1.8) % hold - (hold - xf)) / xf)
            img.alpha_composite(self.border, (fx - 12, L["fy"] - 12))
            framed = Image.new("RGBA", pic.size); framed.paste(pic, (0, 0), self.mask)
            img.alpha_composite(framed, (fx, L["fy"]))
            lay = Image.new("RGBA", img.size); ld = ImageDraw.Draw(lay)
            ld.text((fx + (L["fw"] - ld.textlength(label, font=self.f_label)) / 2, L["label"]), label, font=self.f_label,
                    fill=INK + (int(255 * fa(1.4 + i * 0.3)),)); img.alpha_composite(lay)
        cx, cy = w // 2, L["fy"] + L["fh"] - self.cake_h // 2 + 30                                # cake between the frames
        cx0, cy0 = cx - self.cw // 2, cy - self.cake_h // 2
        img.alpha_composite(self.cake, (cx0, cy0))
        for i, fx in enumerate((0.36, 0.5, 0.64)):
            sc = 1 + 0.12 * math.sin(tt * 11 + i * 2.1) + 0.06 * math.sin(tt * 23 + i)
            fl = self.flame.resize((self.flame.width, max(2, int(self.flame.height * sc))))
            img.alpha_composite(fl, (int(cx0 + self.cw * fx - fl.width / 2), int(cy0 + self.cake_h * 0.155 - fl.height)))
        text_c(img, "Happy birthday", self.f_script, L["script"], TEAL, fa(0.3), shadow=True)
        text_c(img, "Afia & Rose", self.f_name, L["name"], INK, fa(0.8), shadow=True)
        text_c(img, "Wishing you both a wonderful year ahead!", self.f_body, L["msg"], GREY, fa(2.2))
        text_c(img, "Love, your Chatters family", self.f_sign, L["sign"], TEAL, fa(3.0))
        lg = logo.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * fa(3.6))))
        img.alpha_composite(lg, ((w - lg.width) // 2, L["logo"]))
        return img.convert("RGB")

if __name__ == "__main__":
    Card(1080, 1350).render().save(D + "CHATTERS_AFIA_ROSE_birthday_feed_4x5.jpg", quality=95)
    story = Card(1080, 1920); story.render().save(D + "CHATTERS_AFIA_ROSE_birthday_story_9x16.jpg", quality=95)
    if "--reel" in sys.argv:
        FPS, DUR = 30, 16.5
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                               "-i", "-", "-i", D + "../lucky/hb.wav", "-af", "apad,atrim=0:16.5,afade=t=out:st=15.5:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k",
                               "-ar", "48000", "-shortest", "-movflags", "+faststart", D + "CHATTERS_AFIA_ROSE_birthday_reel.mp4"], stdin=subprocess.PIPE)
        for n in range(int(DUR * FPS)):
            ff.stdin.write(story.render(n / FPS).tobytes())
        ff.stdin.close(); ff.wait()
