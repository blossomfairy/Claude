"""Stylist Highlight series: one reusable reel template per stylist. Usage: python3 build_highlight.py lorne

Format (gene research 2026-11-20: stylist intro = our #2 format; hard-to-skip recipe 2026-11-22):
  hook   moving after shot + "Meet" (script) / NAME (serif)
  who    lower third NAME, TITLE  (title verified from chatters.ca booking roster, facts.json)
  work   their real work on the 92 BPM grid: before -> process -> after, with labels
  proof  one verified line (e.g. named in 5-star Google reviews)
  CTA    "Book with NAME" + chatters.ca / phone over the work, white logo
Only verified facts go on screen: each stylist's config cites its source.
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

STYLISTS = {
    "lorne": {
        "name": "Lorne",
        "title": "Elite Stylist",               # facts.json team: "Stylist Elite" (chatters.ca roster 2026-10-03)
        "skills": "Cuts, perms & styling",      # shown in Lorne's own work: cut/perm/style reel 2026-10-18
        "proof": "Named in a 5-star Google review",  # facts.json google.named_in_recent_5star (verified 2026-10-03)
        "book": "Book with Lorne",              # on the online roster -> bookable by name
        # stills cut from the graded 2026-10-18 reel, labels cropped off; face/mirror-free
        "shots": [  # (still, beats, cx, cy, z0, z1, label)
            ("after1", 2.5, .50, .45, .94, .70, None),        # hook: whips in from wide
            ("after3", .5, .50, .40, .66, .64, None),          # half-beat burst
            ("after5", .5, .45, .55, .66, .64, None),
            ("after2", .5, .55, .35, .66, .64, None),
            ("after1", .5, .50, .70, .66, .64, None),
            ("after3", 2, .50, .50, .92, .86, None),          # who: lower third
            ("before", 1.5, .50, .50, .92, .86, "Before"),    # the work
            ("before2", 1, .60, .50, .92, .86, "Before"),
            ("wrap", 1.5, .50, .45, .92, .86, "The perm wrap"),
            ("wrap", 1, .40, .60, .70, .66, "The perm wrap"),
            ("after5", 1.5, .50, .50, .95, .88, "After"),     # FLASH reveal
            ("after2", 1, .50, .40, .70, .66, None),
            ("after1", 1, .45, .65, .70, .66, None),
            ("after3", 1, .55, .45, .70, .66, None),
            ("after5", 1, .50, .70, .70, .66, None),          # skills card from here
            ("after2", 1, .45, .55, .80, .76, None),
            ("after1", 1, .55, .40, .80, .76, None),
            ("after3", 1.5, .50, .55, .85, .80, None),        # proof card
            ("after5", 1, .50, .40, .72, .68, None),
            ("after2", 1, .50, .65, .72, .68, None),
            ("after3", 1, .50, .60, .72, .68, None),
            ("after5", 1, .50, .35, .72, .68, None),
            ("after2", 1, .55, .50, .72, .68, None),
            ("wrap", 1, .55, .40, .72, .68, None),
            ("after1", 5, .50, .45, .70, .94, None),          # CTA + logo, pulls back to the hook framing (loop)
        ],
        "flash_at": 10, "who": (5, 6), "skills_at": (14, 17), "proof_at": (17, 20),
    },
}

key = sys.argv[1] if len(sys.argv) > 1 else "lorne"
C = STYLISTS[key]
SRC = f"{D}/{key}/src"
P = {f[:-4]: Image.open(f"{SRC}/{f}").convert("RGB") for f in os.listdir(SRC) if f.endswith(".jpg")}
SHOTS = C["shots"]
starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc


def meet(name):
    img = ht.canvas()
    cy = int(H * 0.36)
    ht.shadow_text(img, (W // 2, cy - 40), "Meet", ht.script(130), ht.TITLE_WHITE, blur=7, alpha=200)
    ht.shadow_text(img, (W // 2, cy + 130), name, ht.fit(name, ht.serif, 210, int(W * 0.7)), ht.TITLE_WHITE, blur=8, alpha=200)
    return img


def line(text, y, size=64):
    img = ht.canvas()
    ht.shadow_text(img, (W // 2, int(H * y)), text, ht.fit(text, lambda s: ht.sans(s, "Bold"), size, int(W * .86)),
                   ht.TITLE_WHITE, blur=6, alpha=170)
    return img


def cta(book):
    img = ht.endlogo()
    ht.shadow_text(img, (W // 2, int(H * .62)), book, ht.fit(book, ht.serif, 104, int(W * .8)), ht.TITLE_WHITE, blur=8, alpha=200)
    ht.shadow_text(img, (W // 2, int(H * .68)), "chatters.ca  ·  306-931-3010", ht.sans(50, "Bold"), ht.TITLE_WHITE, blur=6, alpha=170)
    ht.shadow_text(img, (W // 2, int(H * .72)), "Lawson Heights Mall, Saskatoon", ht.sans(40, "Bold"), ht.TITLE_WHITE, blur=6, alpha=170)
    return img


O = {
    "meet": meet(C["name"]),
    "who": ht.lower(f"{C['name']}, {C['title']}", "Chatters Lawson Heights", y=0.70),
    "skills": line(C["skills"], .74),
    "proof": line(C["proof"], .74, 58),
    "cta": cta(C["book"]),
}
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


def view(img, cx, cy, z):
    iw, ih = img.size
    full = min(iw, ih * W / H)                          # widest 9:16 window the still allows
    cw = W / 1.6 + (full - W / 1.6) * min(1, max(0, (z - .6) / .4))  # z 0.6..1.0 -> 1.6x..widest
    ch = cw * H / W
    if ch > ih:
        ch = ih
        cw = ch * W / H
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    k, beats, cx, cy, z0, z1, _ = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = 1 - (1 - p) ** 3 if i == 0 else p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.07 * math.exp(-dt / 0.10)
    cx += (0.18 if i % 2 else -0.18) * (e - 0.5)       # pan across the still (stills are only ~1.5x wide)
    cx += 0.004 * math.sin(2 * math.pi * 0.6 * t + i)
    cy += 0.003 * math.cos(2 * math.pi * 0.45 * t + 2 * i)
    return view(P[k], cx, cy, z)


def span(a, b):
    return starts[a] + 0.1, starts[b] - 0.05


out = f"{D}/{key}/CHATTERS_{key.upper()}_stylist_highlight_SILENT.mp4"
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
     "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-movflags", "+faststart", "-an", out], stdin=subprocess.PIPE)
WHITE = Image.new("RGBA", (W, H), (255, 255, 255, 255))
for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, O["meet"], 1.0 if t < 0.3 else fade(t, 0, starts[5] - 0.05))
    over(fr, O["who"], fade(t, *span(*C["who"])))
    over(fr, O["skills"], fade(t, *span(*C["skills_at"])))
    over(fr, O["proof"], fade(t, *span(*C["proof_at"])))
    over(fr, O["cta"], fade(t, starts[-1] + 0.3, starts[-1] + 5 * BEAT - 0.3, 0.3))
    lab = SHOTS[i][6]
    if lab:
        if lab not in LABELS:
            LABELS[lab] = line(lab, .80, 78)
        over(fr, LABELS[lab], fade(t, starts[i] + 0.03, starts[i] + SHOTS[i][1] * BEAT - 0.03, 0.08))
    d = t - starts[C["flash_at"]]
    flash = max(0.0, 1 + d / 0.07) if -0.07 < d < 0 else (math.exp(-d / 0.08) if 0 <= d < 0.35 else 0.0)
    over(fr, WHITE, min(1.0, flash) * 0.9)
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{key}: {len(SHOTS)} shots, {TOTAL:.2f}s, end beat {sum(s[1] for s in SHOTS[:-1])}")
