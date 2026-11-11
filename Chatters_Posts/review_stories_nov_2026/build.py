"""Review stories (1080x1920): six verbatim 5/5 Phorest quotes + one booking card.
Sources: Phorest review emails forwarded by the store manager to Amy's Gmail, Oct 6-22 2026.
Type-and-panel only (no client photos), so every frame must pass E.audit()."""
import os, sys
from PIL import Image, ImageDraw

SK = os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638")
sys.path.insert(0, os.path.join(SK, "chatters-post-designer"))
import engine as E  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
LOGO = os.path.join(SK, "chatters-house-style", "assets", "logo_black.png")

# (stylist, reviewer as first name + last initial, verbatim text, received)
REVIEWS = [
    ("Rose", "Dolores D.", "Rose was excellent, listening to my needs, and providing suggestions, based on my features and type of hair.", "2026-10-22"),
    ("Afia", "Eleanor W.", "Afia is a personable hair stylist who does an excellent job. She listens to what type of style the customer wants…", "2026-10-12"),
    ("Lorne", "Marie-Anne W.", "Always a pleasure to visit with an old friend…and get a great haircut to boot!", "2026-10-14"),
    ("Fola", "Hilda C.", "Fola always gives me a fantastic haircut. She's a warm lovely person", "2026-10-13"),
    ("Marina", "Judy K.", "Everyone was friendly and courteous. Once again a great haircut and style. Thanks Marina!", "2026-10-07"),
    ("Afia", "Dale P.", "Friendly staff and I was very satisfied with my hair cut, didn't have to wait I was in the chair at my booked time.", "2026-10-11"),
]
TINTS = [E.SAND, E.BLUSH, E.SAGE, E.TAUPE, E.MIST, E.AQUA]


def ctext(d, y, text, fnt, fill=E.INK, ls=0):
    if ls:
        w = E.ls_width(text, fnt, ls)
        x = (W - w) / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill, anchor="ls")
            x += d.textlength(ch, font=fnt) + ls
    else:
        d.text((W // 2, y), text, font=fnt, fill=fill, anchor="ms")


def stars(d, y, n=5, r=26, gap=70):
    import math
    x0 = W // 2 - gap * (n - 1) // 2
    for i in range(n):
        cx = x0 + i * gap
        pts = [(cx + (r if k % 2 == 0 else r * 0.42) * math.sin(k * math.pi / 5),
                y - (r if k % 2 == 0 else r * 0.42) * math.cos(k * math.pi / 5)) for k in range(10)]
        d.polygon(pts, fill=E.INK)


def button(d, y, text):
    f = E.F(32, "Bold")
    tw = E.ls_width(text, f, 1)
    bw, bh = tw + 120, 100
    d.rounded_rectangle(((W - bw) // 2, y, (W + bw) // 2, y + bh), radius=3, fill=E.TEAL)
    ctext(d, y + bh // 2 + 12, text, f, fill=E.PAPER, ls=1)


def logo(img, y, width=300):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.resize((width, int(lg.height * width / lg.width)), Image.LANCZOS)
    img.paste(lg, ((W - width) // 2, y), lg)


def quote_block(d, text, top, bottom):
    """Largest serif size whose wrapped quote fits between top and bottom, centred there."""
    for size in range(76, 40, -2):
        f = E.serif(size)
        lines = E.wrap(text, f, 860)
        lead = int(size * 1.42)
        if len(lines) * lead <= bottom - top:
            break
    y = top + ((bottom - top) - len(lines) * lead) // 2 + int(size * 0.95)
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=E.INK, anchor="ms")
        y += lead
    return y - lead


def review_story(stylist, who, text, tint):
    img = Image.new("RGB", (W, H), tint)
    d = ImageDraw.Draw(img)
    ctext(d, 330, "CLIENT REVIEW", E.F(30, "Bold"), ls=3)
    stars(d, 410)
    d.text((W // 2, 640), "“", font=E.serif(240), fill=E.INK, anchor="ms")
    last = quote_block(d, text, 640, 1140)
    y = max(last + 90, 1190)
    d.line((W // 2 - 60, y, W // 2 + 60, y), fill=E.INK, width=2)
    ctext(d, y + 80, who, E.F(44, "SemiBold"))
    ctext(d, y + 135, f"5 out of 5 for {stylist}, Lawson Heights", E.F(30, "Medium"))
    button(d, 1430, f"BOOK WITH {stylist.upper()}")
    logo(img, 1590)
    return img


def cta_story():
    img = Image.new("RGB", (W, H), E.GROUND)
    d = ImageDraw.Draw(img)
    ctext(d, 330, "LAWSON HEIGHTS MALL", E.F(30, "Bold"), ls=3)
    for i, ln in enumerate(["Thank you for", "the kind words."]):
        d.text((W // 2, 560 + i * 120), ln, font=E.serif(104), fill=E.INK, anchor="ms")
    d.line((W // 2 - 60, 780, W // 2 + 60, 780), fill=E.INK, width=2)
    for i, ln in enumerate(["Rose, Afia, Lorne, Fola, Marina:", "every quote here is a real client."]):
        ctext(d, 880 + i * 62, ln, E.F(40, "Medium"))
    for i, ln in enumerate(["Bay 30, 134 Primrose Drive, Saskatoon", "306-931-3010"]):
        ctext(d, 1080 + i * 58, ln, E.F(36, "Regular"))
    button(d, 1430, "BOOK ONLINE")
    logo(img, 1590)
    return img


if __name__ == "__main__":
    out = []
    for i, (stylist, who, text, _) in enumerate(REVIEWS, 1):
        im = review_story(stylist, who, text, TINTS[i - 1])
        name = f"review_story_{i}_{stylist.lower()}.jpg"
        E.save(im, os.path.join(D, name))
        out.append(im)
        print(name, "audit", E.audit(im))
    im = cta_story()
    E.save(im, os.path.join(D, "review_story_7_book.jpg"))
    out.append(im)
    print("review_story_7_book.jpg audit", E.audit(im))
    E.contact_sheet(out, os.path.join(D, "qc_contact_sheet.png"), cols=7)
