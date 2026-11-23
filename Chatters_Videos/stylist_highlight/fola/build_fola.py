"""Fola Stylist Highlight (2026-11-23): same format as Lorne v3, music-only (no video/audio of Fola exists; user).
Sources = user uploads: Fola's portrait photo, fola_birthday_transformations (4 clients), the 6 s braids reel,
two "Hair by Fola" Instagram-size clips (short cut). Badges/text overlays cropped off. Slow camera (user 2026-11-23).
On-screen facts: title "Senior Stylist" from the chatters.ca booking roster (facts.json, 2026-10-03).
"""
import os
import subprocess
import sys

from PIL import Image, ImageEnhance, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(
    "~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht  # noqa: E402

W, H, FPS = 1080, 1920, 30
S = 1.30  # seconds per work shot (2 beats at 92 BPM)
CTA_AT, TOTAL = 21.2, 25.7
# (start, end, still, mode, label)   mode: "pan" = 9:16 crop from a tall still, "card" = whole frame over its blur
SEG = [(0.0, 3.0, "portrait", "portrait", None), (3.0, 4.3, "portrait", "portrait2", None)]
WORK = [("c1_before", "pan", "Before"), ("c1_after", "pan", "After"), ("c2_before", "pan", "Before"),
        ("c2_after", "pan", "After"), ("c3_before", "pan", "Before"), ("c3_after", "pan", "After"),
        ("c6_before", "card", "Before"), ("c6_after", "card", "After"), ("c4_before", "pan", "Before"),
        ("c4_after", "pan", "After"), ("c7_after", "pan", None), ("c7_after2", "pan", None),  # 2026-11-23 upload
        ("c5_after", "card", None)]
t = 4.3
for k, m, lab in WORK:
    SEG.append((t, t + S, k, m, lab))
    t += S
SEG.append((t, TOTAL, "portrait", "cta", None))
assert abs(t - CTA_AT) < .01, t
FLASH_AT = SEG[3][0]  # first "After"
P = {f[:-4]: Image.open(f"{D}/src/{f}").convert("RGB") for f in os.listdir(f"{D}/src") if f.endswith(".jpg")}


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


def text_img(text, y, size, alpha=190):
    img = ht.canvas()
    f = ht.fit(text, lambda s: ht.sans(s, "Bold"), size, int(W * .86))
    ht.shadow_text(img, (W // 2, int(H * y)), text, f, ht.TITLE_WHITE, blur=6, alpha=alpha)
    return img


def pan(img, e, k):
    iw, ih = img.size
    cw = min(iw, ih * W / H) * (0.96 - 0.04 * e)       # slow push-in
    ch = cw * H / W
    cx = iw / 2 + (1 if k % 2 else -1) * 0.03 * iw * (e - .5)
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(ih * .45 - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def card(img, z, top=None, width=W, dim=0.7):
    bg = ImageEnhance.Brightness(img.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))).enhance(dim)
    w = int(width * z)
    h = int(img.height * w / img.width)
    fg = img.resize((w, h), Image.LANCZOS)
    bg.paste(fg, ((W - w) // 2, int(H * .45 - h / 2) if top is None else top))
    return bg


def meet():
    img = ht.canvas()
    ht.shadow_text(img, (W // 2, int(H * .70)), "Meet", ht.script(120), ht.TITLE_WHITE, blur=7, alpha=220)
    ht.shadow_text(img, (W // 2, int(H * .70) + 150), "Fola", ht.serif(210), ht.TITLE_WHITE, blur=8, alpha=220)
    return img


def cta():
    img = ht.canvas()
    lg = ht.logo("white", 0.42)
    img.alpha_composite(lg, ((W - lg.width) // 2, int(H * .88) - lg.height // 2))
    for txt, y, f in [("Book with Fola", .70, ht.serif(104)), ("chatters.ca  ·  306-931-3010", .755, ht.sans(50, "Bold")),
                      ("Lawson Heights Mall, Saskatoon", .79, ht.sans(40, "Bold"))]:
        ht.shadow_text(img, (W // 2, int(H * y)), txt, f, ht.TITLE_WHITE, blur=7, alpha=210)
    return img


O = {"meet": meet(), "who": ht.lower("Fola, Senior Stylist", "Chatters Lawson Heights", y=0.78),
     "skills": text_img("Colour, cuts & styling", .88, 64), "more": text_img("More by Fola", .88, 64), "cta": cta()}
LABELS = {k: text_img(k, .15, 78) for k in ("Before", "After")}
WHITE = Image.new("RGBA", (W, H), (255, 255, 255, 255))

out = f"{D}/CHATTERS_FOLA_stylist_highlight_SILENT.mp4"
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", "-an", out],
    stdin=subprocess.PIPE)
for n in range(round(TOTAL * FPS)):
    tt = n / FPS
    i, (a, b, k, m, lab) = next((j, s) for j, s in enumerate(SEG) if s[0] <= tt + 1e-9 < s[1] or j == len(SEG) - 1)
    p = min(1, (tt - a) / (b - a))
    e = p * p * (3 - 2 * p)
    if m == "portrait":
        fr = card(P[k], 1.0 + 0.03 * e, top=int(H * .06), width=980, dim=0.55)
    elif m == "portrait2":
        fr = card(P[k], 1.03 + 0.02 * e, top=int(H * .06), width=980, dim=0.55)
    elif m == "cta":
        fr = card(P[k], 0.72 + 0.03 * e, top=int(H * .08), width=980, dim=0.5)
    elif m == "card":
        fr = card(P[k], 1.0 + 0.04 * e)
    else:
        fr = pan(P[k], e, i)
    fr = fr.convert("RGBA")
    over(fr, O["meet"], 1.0 if tt < .3 else fade(tt, 0, 2.9, .3))
    over(fr, O["who"], fade(tt, 3.0, 4.25))
    over(fr, O["skills"], fade(tt, SEG[4][0], SEG[7][1] - .05, .25))
    over(fr, O["more"], fade(tt, SEG[10][0], CTA_AT - .05, .25))
    over(fr, O["cta"], fade(tt, CTA_AT + .2, TOTAL + 1, .35))
    if lab:
        over(fr, LABELS[lab], fade(tt, a + .05, b - .05, .12))
    d = tt - FLASH_AT
    flash = max(0.0, 1 + d / 0.07) if -0.07 < d < 0 else (2.718 ** (-d / 0.09) if 0 <= d < 0.4 else 0.0)
    over(fr, WHITE, min(1.0, flash) * 0.9)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"fola: {len(SEG)} shots, {TOTAL}s")
