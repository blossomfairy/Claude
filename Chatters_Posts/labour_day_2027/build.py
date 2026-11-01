"""Labour Day 2027 greeting (feed 1080x1350 + story 1080x1920). House type: serif + script, black logo on a brand tint."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht

SAND, INK, BROWN, LINE = (229, 207, 201), (0, 0, 0), ht.SCRIPT_BROWN, (206, 206, 206)
D = os.path.dirname(os.path.abspath(__file__))

def post(w, h, name):
    img = Image.new("RGB", (w, h), SAND); d = ImageDraw.Draw(img)
    top = int(h * (0.30 if h > 1500 else 0.20))
    d.text((w // 2, top), "Happy", font=ht.serif(150), fill=INK, anchor="ms")
    d.text((w // 2, top + 160), "Labour Day", font=ht.serif(150), fill=INK, anchor="ms")
    d.text((w // 2, top + 300), "from Chatters Lawson Heights", font=ht.fit("from Chatters Lawson Heights", ht.script, 96, int(w * 0.80)), fill=BROWN, anchor="ms")
    y = top + 400
    d.line((w // 2 - 60, y, w // 2 + 60, y), fill=INK, width=2)
    for k, line in enumerate(["Thank you to everyone who works", "to keep Saskatoon going.", "Enjoy the long weekend."]):
        d.text((w // 2, y + 90 + k * 62), line, font=ht.sans(42, "SemiBold"), fill=INK, anchor="ms")
    d.text((w // 2, y + 330), "MONDAY, SEPTEMBER 6, 2027", font=ht.sans(30, "Bold"), fill=INK, anchor="ms")
    lg = Image.open(os.path.join(ht.ASSETS, "logo_black.png")).convert("RGBA")
    lw = int(w * 0.42); lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    ly = h - (420 if h > 1500 else 150) - lg.height // 2
    img.paste(lg, ((w - lw) // 2, ly), lg)
    img.save(os.path.join(D, name), quality=95)
    print(name, img.size)

post(1080, 1350, "labour_day_2027_feed.jpg")
post(1080, 1920, "labour_day_2027_story.jpg")
