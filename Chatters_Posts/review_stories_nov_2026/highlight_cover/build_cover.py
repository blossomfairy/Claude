"""Instagram highlight cover for "Reviews": 1080x1920, icon centred in the circle-safe zone.
Three options: A serif quote mark, B single star, C five stars. Plus a circle preview at highlight size."""
import math, os, sys
from PIL import Image, ImageDraw
SK = os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638")
sys.path.insert(0, os.path.join(SK, "chatters-post-designer"))
import engine as E  # noqa: E402
D = os.path.dirname(os.path.abspath(__file__))
W, H, CY = 1080, 1920, 960

def star(d, cx, cy, r):
    pts = [(cx + (r if k % 2 == 0 else r * 0.42) * math.sin(k * math.pi / 5),
            cy - (r if k % 2 == 0 else r * 0.42) * math.cos(k * math.pi / 5)) for k in range(10)]
    d.polygon(pts, fill=E.INK)

def cover(kind):
    img = Image.new("RGB", (W, H), E.SAND); d = ImageDraw.Draw(img)
    if kind == "quote":
        lay = Image.new("L", (1400, 1400), 0)
        ImageDraw.Draw(lay).text((200, 200), "“", font=E.serif(900), fill=255)
        lay = lay.crop(lay.getbbox())  # true ink bounds, so the mark sits dead centre
        img.paste(E.INK, (W // 2 - lay.width // 2, CY - lay.height // 2), lay)
    elif kind == "star":
        star(d, W // 2, CY + 20, 230)
    else:
        for i in range(5):
            star(d, W // 2 + (i - 2) * 150, CY - 70, 62)
        d.text((W // 2, CY + 120), "Reviews", font=E.serif(110), fill=E.INK, anchor="ms")
    return img

def circle_preview(imgs, out, size=220):
    sheet = Image.new("RGB", (len(imgs) * (size + 40) + 40, size + 80), E.PAPER)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    for i, im in enumerate(imgs):
        sq = im.crop((0, CY - W // 2, W, CY + W // 2)).resize((size, size), Image.LANCZOS)
        sheet.paste(sq, (40 + i * (size + 40), 20), m)
    sheet.save(out)

imgs = []
for tag, kind in [("A", "quote"), ("B", "star"), ("C", "stars")]:
    im = cover(kind); imgs.append(im)
    E.save(im, os.path.join(D, f"highlight_reviews_{tag}_{kind}.jpg"))
    print(tag, kind, "audit", E.audit(im))
circle_preview(imgs, os.path.join(D, "qc_circle_preview.png"))
