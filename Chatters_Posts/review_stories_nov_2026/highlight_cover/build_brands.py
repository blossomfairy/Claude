"""Instagram highlight cover for "Brands": same sand ground and centring as the Reviews cover.
Drawn product shapes only, no third-party logos. A pump bottle, B bottle + tube, C "Brands" wordmark."""
import os, sys
from PIL import Image, ImageDraw
SK = os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638")
sys.path.insert(0, os.path.join(SK, "chatters-post-designer"))
import engine as E  # noqa: E402
D = os.path.dirname(os.path.abspath(__file__))
W, H, CY = 1080, 1920, 960
SS = 4  # supersample for smooth edges


def pump_bottle(d, cx, top, s):
    """Pump bottle: nozzle, neck, collar, rounded body with a ground-coloured label band."""
    k = lambda v: int(v * s)
    d.rectangle((cx - k(70), top, cx + k(10), top + k(26)), fill=E.INK)                 # nozzle
    d.rectangle((cx - k(14), top, cx + k(14), top + k(90)), fill=E.INK)                 # stem
    d.rounded_rectangle((cx - k(46), top + k(80), cx + k(46), top + k(130)), radius=k(8), fill=E.INK)  # collar
    d.rounded_rectangle((cx - k(110), top + k(124), cx + k(110), top + k(470)), radius=k(36), fill=E.INK)  # body
    d.rectangle((cx - k(110), top + k(250), cx + k(110), top + k(330)), fill=E.SAND)   # label band
    return top + k(470)


def tube(d, cx, bottom, s):
    """Squeeze tube standing on its cap."""
    k = lambda v: int(v * s)
    d.rounded_rectangle((cx - k(50), bottom - k(60), cx + k(50), bottom), radius=k(10), fill=E.INK)  # cap
    d.polygon([(cx - k(80), bottom - k(64)), (cx + k(80), bottom - k(64)),
               (cx + k(95), bottom - k(360)), (cx - k(95), bottom - k(360))], fill=E.INK)  # body
    d.rectangle((cx - k(100), bottom - k(390), cx + k(100), bottom - k(360)), fill=E.INK)  # crimp
    d.rectangle((cx - k(84), bottom - k(250), cx + k(84), bottom - k(200)), fill=E.SAND)  # label band


def render(kind):
    big = Image.new("RGB", (W * SS, H * SS), E.SAND)
    d = ImageDraw.Draw(big)
    c, y = W * SS // 2, CY * SS
    if kind == "bottle":
        pump_bottle(d, c, y - 235 * SS, SS)
    elif kind == "duo":
        pump_bottle(d, c - 130 * SS, y - 235 * SS, SS * 0.9)
        tube(d, c + 150 * SS, y + int(188 * SS), SS * 0.9)
    img = big.resize((W, H), Image.LANCZOS)
    if kind == "word":
        dd = ImageDraw.Draw(img)
        dd.text((W // 2, CY + 40), "Brands", font=E.serif(190), fill=E.INK, anchor="ms")
        dd.line((W // 2 - 70, CY + 110, W // 2 + 70, CY + 110), fill=E.INK, width=4)
    return img


def circle_preview(imgs, out, size=220):
    sheet = Image.new("RGB", (len(imgs) * (size + 40) + 40, size + 40), E.PAPER)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    for i, im in enumerate(imgs):
        sq = im.crop((0, CY - W // 2, W, CY + W // 2)).resize((size, size), Image.LANCZOS)
        sheet.paste(sq, (40 + i * (size + 40), 20), m)
    sheet.save(out)


imgs = []
for tag, kind in [("A", "bottle"), ("B", "duo"), ("C", "word")]:
    im = render(kind)
    imgs.append(im)
    E.save(im, os.path.join(D, f"highlight_brands_{tag}_{kind}.jpg"))
    print(tag, kind, "audit", E.audit(im))
circle_preview(imgs, os.path.join(D, "qc_circle_preview_brands.png"))
