"""Highlight covers in the Chatters house look: official lockup + thin serif title, like the
brand's own end cards. Black (white lockup) and studio grey #D4DBD7 (black lockup)."""
import os, sys
from PIL import Image, ImageDraw
SK = os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638")
sys.path.insert(0, os.path.join(SK, "chatters-house-style", "scripts"))
sys.path.insert(0, os.path.join(SK, "chatters-post-designer"))
import house_titles as ht  # noqa: E402
import engine as E  # noqa: E402
D = os.path.dirname(os.path.abspath(__file__))
W, H, CY = 1080, 1920, 960
THEMES = {"black": (ht.BLACK, ht.TITLE_WHITE, "white"), "grey": (ht.STUDIO_GREY, ht.BLACK, "black")}


def cover(word, theme):
    bg, ink, lg_col = THEMES[theme]
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    lg = Image.open(os.path.join(ht.ASSETS, f"logo_{lg_col}.png")).convert("RGBA")
    lw = 520
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    img.paste(lg, ((W - lw) // 2, CY - 190), lg)          # lockup in the upper half of the circle
    d.line((W // 2 - 50, CY + 20, W // 2 + 50, CY + 20), fill=ink, width=3)
    d.text((W // 2, CY + 190), word, font=ht.serif(150), fill=ink, anchor="ms")
    return img


def circle_preview(imgs, out, size=220):
    sheet = Image.new("RGB", (len(imgs) * (size + 40) + 40, size + 40), (255, 255, 255))
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    for i, im in enumerate(imgs):
        sq = im.crop((0, CY - W // 2, W, CY + W // 2)).resize((size, size), Image.LANCZOS)
        sheet.paste(sq, (40 + i * (size + 40), 20), m)
    sheet.save(out)


imgs = []
for theme in THEMES:
    for word in ["Reviews", "Brands"]:
        im = cover(word, theme)
        imgs.append(im)
        E.save(im, os.path.join(D, f"chatters_highlight_{word.lower()}_{theme}.jpg"))
        print(word, theme, "audit", E.audit(im) if theme == "black" else "n/a (house studio grey)")
circle_preview(imgs, os.path.join(D, "qc_circle_preview_chatters.png"))
