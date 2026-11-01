"""Asma colour + cut + style after-photo reel: 1080x1920, 30 fps, 92 BPM shot grid, silent master.

Rules applied (chatters-house-style, chatters-reel-editor, Lorne 2026-10-18 precedent):
serif title + "With Chatters" script, white bold-sans lower third, white logo over the last shot,
zoom <= 1.6x, cuts on 1-1.5 beat grid, last shot pulls back to the hook frame so the reel loops.
The in-store "Brow Wax $10" whiteboard (photos 2-4, top 28 %) is cropped out of every shot.
"""
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
P = {i: Image.open(f"{D}/src/p{i}.jpg").convert("RGB") for i in range(1, 6)}  # graded identically
IW, IH = P[1].size  # 1126x2000; z = visible width fraction, z >= 0.63 keeps upscale <= 1.6x
BOARD_Y = 560        # whiteboard bottom edge on photos 2-4

# (photo, beats, cx, cy, z0, z1)
SHOTS = [
    (1, 2.5, .44, .50, .85, .80),  # hook: full after + title
    (5, 1, .50, .35, .70, .66),
    (3, 1, .50, .66, .66, .63),
    (1, 1.5, .40, .75, .66, .63),
    (5, 1, .45, .72, .66, .63),
    (4, 1, .55, .64, .68, .65),
    (2, 1.5, .45, .66, .66, .63),
    (5, 1, .55, .50, .80, .76),
    (1, 1, .42, .40, .70, .66),    # root melt
    (3, 1, .38, .70, .66, .63),
    (4, 1.5, .62, .68, .66, .63),
    (5, 1, .40, .30, .66, .63),
    (2, 1, .58, .70, .66, .63),
    (1, 1, .55, .70, .72, .68),
    (5, 1.5, .60, .80, .66, .63),
    (3, 1, .55, .64, .70, .67),
    (4, 1, .45, .66, .70, .67),
    (5, 1, .35, .45, .66, .63),
    (2, 1, .40, .64, .70, .67),
    (1, 1, .60, .62, .66, .63),
    (5, 1.5, .50, .55, .95, .90),  # lower third starts
    (2, 1.5, .50, .64, .71, .68),
    (3, 1.5, .50, .64, .71, .68),
    (1, 6, .44, .50, .80, .85),    # end: pull back to hook framing, logo
]

starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc)
    acc += s[1] * BEAT
TOTAL = acc
def readable_title(text, brand, y=0.20):
    """ht.title geometry, but legible over a light wall + ash hair: darker soft shadow under the white
    serif, soft light glow under the brown script. Still no boxes/pills (house rule)."""
    from PIL import ImageDraw, ImageFilter
    img = ht.canvas()
    f = ht.fit(text, ht.serif, 118, int(W * 0.66))
    cy = int(H * y)
    ht.shadow_text(img, (W // 2, cy), text, f, ht.TITLE_WHITE, blur=7, alpha=150)
    tw = f.getlength(text)
    x = int(W // 2 - tw / 2 + tw * 0.16)
    glow = ht.canvas()
    ImageDraw.Draw(glow).text((x, cy + 74), f"With {brand}", font=ht.script(112), fill=(255, 255, 255, 230), anchor="ls")
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    img.alpha_composite(glow)
    img.alpha_composite(glow)
    ImageDraw.Draw(img).text((x, cy + 74), f"With {brand}", font=ht.script(112), fill=ht.SCRIPT_BROWN + (255,), anchor="ls")
    return img


title = readable_title("Colour, Cut & Style", "Chatters")
lower = ht.lower("Asma", "Chatters Lawson Heights")
endlogo = ht.endlogo()
LOWER_T = (starts[-4] + 0.1, starts[-1] - 0.05)
END_T = (starts[-1] + 0.5, TOTAL + 1)


def fade(t, a, b, f=0.25):
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


def window(pi, cx, cy, z):
    cw = IW * z
    ch = cw * 16 / 9
    if ch > IH:
        ch, cw = IH, IH * 9 / 16
    x0 = min(max(cx * IW - cw / 2, 0), IW - cw)
    ymin = BOARD_Y if pi in (2, 3, 4) else 0
    y0 = min(max(cy * IH - ch / 2, ymin), IH - ch)
    assert pi not in (2, 3, 4) or y0 >= BOARD_Y - 1, f"board visible in photo {pi}"
    assert z >= 0.63 - 1e-9, "upscale over 1.6x"
    return (x0, y0, x0 + cw, y0 + ch)


ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", "-an",
     f"{D}/CHATTERS_ASMA_colour_cut_style_SILENT.mp4"], stdin=subprocess.PIPE)

nframes = round(TOTAL * FPS)
for n in range(nframes):
    t = n / FPS
    i = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-9)
    pi, beats, cx, cy, z0, z1 = SHOTS[i]
    p = (t - starts[i]) / (beats * BEAT)
    p = p * p * (3 - 2 * p)  # ease
    fr = P[pi].resize((W, H), Image.BICUBIC, box=window(pi, cx, cy, z0 + (z1 - z0) * p)).convert("RGBA")
    over(fr, title, 1.0 if t < 0.3 else fade(t, 0, starts[1] - 0.05))
    over(fr, lower, fade(t, *LOWER_T))
    over(fr, endlogo, fade(t, *END_T, f=0.35))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print(f"{len(SHOTS)} shots, {TOTAL:.2f}s, {len(SHOTS) / TOTAL:.2f} cuts/s, end beat {sum(s[1] for s in SHOTS[:-1])}")
