"""Lorne Stylist Highlight v2: Lorne on camera, his own voice (perm-care tip, "Lorne - Ask a Stylist" 2026-09-18,
from the user's Drive) carries the reel; his perm work is cut in as B-roll; captions from the clip's own subtitle
track; slow camera (user 2026-11-23). Music bed D/E/F sits under the voice and lifts on the CTA.
Output: CHATTERS_LORNE_stylist_highlight_v2_SILENTPIC.mp4 (picture only); mux_v2b.sh adds voice + music.
"""
import os
import re
import subprocess
import sys

from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser(
    "~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht  # noqa: E402

W, H, FPS = 1080, 1920, 30
CLIP = f"{D}/src/lorne_ask_a_stylist.mp4"
SPEECH_END = 14.58
TOTAL = 20.5
# (start, end, source, clip_t0 | (cx, cy, z0, z1), label)
SEG = [
    (0.00, 4.00, "CLIP", 0.0, None),
    (4.00, 5.30, "before", (.50, .50, .80, .76), "Before"),
    (5.30, 6.60, "wrap", (.50, .45, .80, .76), "The perm wrap"),
    (6.60, 8.00, "after5", (.50, .50, .85, .78), "After"),
    (8.00, 9.30, "after1", (.45, .55, .80, .76), None),
    (9.30, 10.60, "after3", (.55, .45, .80, .76), None),
    (10.60, SPEECH_END, "CLIP", 10.6, None),
    (SPEECH_END, TOTAL, "after2", (.50, .45, .76, .92), None),
]
GRADE = "eq=contrast=1.05:saturation=1.04:gamma=1.02"
if not os.path.isdir(f"{D}/src/clip"):
    os.makedirs(f"{D}/src/clip")
    subprocess.run(["ffmpeg", "-v", "error", "-i", CLIP, "-vf", f"fps=30,{GRADE}", "-q:v", "2", f"{D}/src/clip/%04d.jpg"], check=True)
NC = len(os.listdir(f"{D}/src/clip"))
P = {k: Image.open(f"{D}/src/{k}.jpg").convert("RGB") for k in ("before", "wrap", "after1", "after2", "after3", "after5")}

subs = []
srt = subprocess.run(["ffmpeg", "-v", "error", "-i", CLIP, "-map", "0:s:0", "-f", "srt", "-"], capture_output=True, text=True).stdout
for a, b, txt in re.findall(r"(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)\n(.+?)(?:\n\n|\Z)", srt, re.S):
    ts = [sum(float(x) * m for x, m in zip(v.replace(",", ".").split(":"), (3600, 60, 1))) for v in (a, b)]
    subs.append((ts[0], ts[1], " ".join(txt.split())))


def text_img(text, y, size, font="sans", alpha=170):
    img = ht.canvas()
    f = ht.fit(text, (lambda s: ht.sans(s, "Bold")) if font == "sans" else ht.serif, size, int(W * .88))
    ht.shadow_text(img, (W // 2, int(H * y)), text, f, ht.TITLE_WHITE, blur=6, alpha=alpha)
    return img


def meet():
    img = ht.canvas()
    ht.shadow_text(img, (W // 2, int(H * .62)), "Meet", ht.script(120), ht.TITLE_WHITE, blur=7, alpha=210)
    ht.shadow_text(img, (W // 2, int(H * .62) + 150), "Lorne", ht.serif(200), ht.TITLE_WHITE, blur=8, alpha=210)
    return img


def cta():
    img = ht.endlogo()
    for txt, y, f in [("Book with Lorne", .62, ht.serif(104)), ("chatters.ca  ·  306-931-3010", .68, ht.sans(50, "Bold")),
                      ("Lawson Heights Mall, Saskatoon", .72, ht.sans(40, "Bold"))]:
        ht.shadow_text(img, (W // 2, int(H * y)), txt, f, ht.TITLE_WHITE, blur=7, alpha=200)
    return img


O = {"meet": meet(), "who": ht.lower("Lorne, Elite Stylist", "Chatters Lawson Heights", y=0.70),
     "proof": text_img("Named in a 5-star Google review", .74, 58), "cta": cta()}
def caption(text):  # wrap to <= 2 lines of ~22 chars so captions stay large
    import textwrap
    lines = textwrap.wrap(text, 22)
    img = ht.canvas()
    f = ht.sans(64, "Bold")
    y0 = int(H * .84) - (len(lines) - 1) * 40
    for k, ln in enumerate(lines):
        ht.shadow_text(img, (W // 2, y0 + k * 80), ln, f, ht.TITLE_WHITE, blur=6, alpha=210)
    return img


CAPS = {s[2]: caption(s[2]) for s in subs}
LABELS = {}


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


def still(img, cx, cy, z):
    iw, ih = img.size
    full = min(iw, ih * W / H)
    cw = W / 1.6 + (full - W / 1.6) * min(1, max(0, (z - .6) / .4))
    ch = cw * H / W
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def clipframe(t, z):
    n = min(NC, max(1, int(round(t * 30)) + 1))
    im = Image.open(f"{D}/src/clip/{n:04d}.jpg").convert("RGB")
    cw, ch = W * z, H * z
    return im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) * 0.3, (W + cw) / 2, (H - ch) * 0.3 + ch))


out = f"{D}/CHATTERS_LORNE_stylist_highlight_v2_SILENTPIC.mp4"
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", "-an", out],
    stdin=subprocess.PIPE)
for n in range(round(TOTAL * FPS)):
    t = n / FPS
    a, b, src, prm, lab = next(s for s in SEG if s[0] <= t + 1e-9 < s[1] + (1e-9 if s[1] == TOTAL else 0)) if t < TOTAL else SEG[-1]
    p = (t - a) / (b - a)
    e = p * p * (3 - 2 * p)
    if src == "CLIP":
        fr = clipframe(prm + (t - a), 1.0 - 0.04 * e)  # very slow push-in on Lorne
    else:
        cx, cy, z0, z1 = prm
        fr = still(P[src], cx + 0.04 * (e - .5), cy, z0 + (z1 - z0) * e)
    fr = fr.convert("RGBA")
    over(fr, O["meet"], 1.0 if t < .3 else fade(t, 0, 2.1, .3))
    over(fr, O["who"], fade(t, 2.2, 4.0))
    over(fr, O["proof"], fade(t, 11.0, SPEECH_END - .1, .3))
    over(fr, O["cta"], fade(t, SPEECH_END + .3, TOTAL + 1, .35))
    if lab:
        LABELS.setdefault(lab, text_img(lab, .15, 78))  # top: captions own the bottom
        over(fr, LABELS[lab], fade(t, a + .05, b - .05, .12))
    for s0, s1, txt in subs:
        if s0 <= t <= s1 + .15:
            over(fr, CAPS[txt], fade(t, s0, s1 + .15, .08))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"v2 picture {TOTAL}s, {len(SEG)} segments, {len(subs)} caption lines")
