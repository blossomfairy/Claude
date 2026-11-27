"""Rose layered cut & style, trending after reel: 1080x1920, 30 fps, 92 BPM grid, 32 beats (20.9 s), silent master.

Hook: the after video (hair flip, HDR tonemapped per chatters-reel-editor) is moving from frame 1 under the title.
Then 1-beat cuts between 3 after photos (1932x2576) and the video, gentle camera (user taste 2026-11-23: pan <= 0.06,
punch <= 2.5 %), lower third "Rose, Apprentice Stylist" (facts.json rule: always "apprentice"), white logo on the end
shot, which pushes back to the hook framing so the replay loops.
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
P = {i: Image.open(f"{D}/src/p{i}.jpg").convert("RGB") for i in (1, 2, 3)}
NV = len(os.listdir(f"{D}/src/v"))
VDUR = NV / 30


def vframe(t):
    n = min(NV, max(1, int(round(t * 30)) + 1))
    return Image.open(f"{D}/src/v/{n:04d}.jpg").convert("RGB")


# (src, beats, t_in | None, cx, cy, z0, z1)   z = visible width fraction (photos: 0.35..0.75)
SHOTS = [
    ("V", 3, 0.00, .50, .50, 1.00, .96),   # hook: hair flip in motion + title
    (1, 1, None, .50, .45, .74, .71),
    (3, 1, None, .50, .55, .74, .71),
    (2, 1, None, .48, .50, .74, .71),
    ("V", 1.5, 2.00, .50, .50, .97, .93),
    (1, 1, None, .55, .72, .46, .44),      # curled-under ends
    (3, 1, None, .45, .62, .46, .44),
    (2, 1, None, .55, .30, .48, .46),      # crown shine
    ("V", 1, 3.00, .50, .55, .95, .92),
    (1, 1.5, None, .50, .50, .70, .67),
    (3, 1, None, .55, .40, .50, .48),
    (2, 1, None, .45, .75, .50, .48),
    (1, 1, None, .40, .60, .52, .50),      # lower third from here
    (3, 1, None, .50, .50, .72, .69),
    (2, 1, None, .50, .55, .70, .67),
    ("V", 1, 0.60, .50, .55, .95, .92),
    (1, 1, None, .60, .40, .50, .48),
    (3, 1.5, None, .45, .70, .52, .50),
    (2, 1, None, .55, .62, .50, .48),      # lower third ends
    (1, 1.5, None, .50, .55, .74, .71),
    ("V", 1, 1.20, .50, .50, .95, .92),
    (3, 1, None, .55, .30, .50, .48),
    (2, 1, None, .45, .45, .62, .60),
    (1, 5, None, .50, .48, .62, .75),      # end: logo, pulls back
]
LOWER_FROM, LOWER_TO = 12, 19
starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc
assert abs(sum(s[1] for s in SHOTS) - 32) < 1e-6
for s in SHOTS:
    assert s[0] != "V" or s[2] + s[1] * BEAT <= VDUR + 0.02, s


def readable_title(text, brand, y=0.30):
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=8, alpha=210)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    ht.shadow_text(img, (x, cy + 74), f"With {brand}", ht.script(112), ht.TITLE_WHITE, anchor="ls", blur=6, alpha=210)
    return img


title = readable_title("Layered Cut & Style", "Chatters")
lower = ht.lower("Rose, Apprentice Stylist", "Chatters Lawson Heights", y=0.70)
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


def view(img, cx, cy, z, video=False):
    iw, ih = img.size
    cw = iw * z if video else max(iw * z, W / 1.6)
    cw = min(cw, iw, ih * W / H)
    ch = cw * H / W
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def frame(i, t):
    src, beats, tin, cx, cy, z0, z1 = SHOTS[i]
    dt = t - starts[i]
    p = min(1.0, max(0.0, dt / (beats * BEAT)))
    e = p * p * (3 - 2 * p)
    z = z0 + (z1 - z0) * e
    if 0 < i < len(SHOTS) - 1:
        z *= 1 - 0.025 * math.exp(-dt / 0.15)  # soft beat punch
    cx += (0.03 if i % 2 else -0.03) * (e - .5)
    if src == "V":
        return view(vframe(tin + dt), cx, cy, z, video=True)
    return view(P[src], cx, cy, z)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", "-an",
     f"{D}/CHATTERS_ROSE_layers_trend_SILENT.mp4"], stdin=subprocess.PIPE)
for n in range(round(TOTAL * FPS)):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    fr = frame(i, t).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.35))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s")
