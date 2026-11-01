"""Remembrance Day 2026 (feed 1080x1350 + story 1080x1920). Quiet layout: black ground, white serif, white logo.
No poppy (Royal Canadian Legion trademark; commercial use needs Legion permission) and no sales call to action."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.expanduser("~/.claude/skills/synced/aaa4054b-393e-49a4-a4aa-cf26603f340c_09a11075-96da-4ac6-a038-39dc0a7b9638/chatters-house-style/scripts"))
import house_titles as ht

BLACK, WHITE, GREY = (0, 0, 0), ht.TITLE_WHITE, (206, 206, 206)
D = os.path.dirname(os.path.abspath(__file__))

def post(w, h, name):
    img = Image.new("RGB", (w, h), BLACK); d = ImageDraw.Draw(img)
    top = int(h * (0.33 if h > 1500 else 0.27))
    d.text((w // 2, top), "NOVEMBER 11", font=ht.sans(34, "SemiBold"), fill=GREY, anchor="ms")
    d.text((w // 2, top + 150), "Lest We", font=ht.serif(150), fill=WHITE, anchor="ms")
    d.text((w // 2, top + 300), "Forget", font=ht.serif(150), fill=WHITE, anchor="ms")
    y = top + 390
    d.line((w // 2 - 60, y, w // 2 + 60, y), fill=GREY, width=2)
    for k, line in enumerate(["Today we remember those who served,", "and those who serve."]):
        d.text((w // 2, y + 90 + k * 60), line, font=ht.sans(40, "SemiBold"), fill=WHITE, anchor="ms")
    d.text((w // 2, y + 300), "Pause with us at 11 a.m.", font=ht.fit("Pause with us at 11 a.m.", ht.script, 92, int(w * 0.8)), fill=WHITE, anchor="ms")
    lg = Image.open(os.path.join(ht.ASSETS, "logo_white.png")).convert("RGBA")
    lw = int(w * 0.30); lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    ly = h - (400 if h > 1500 else 150) - lg.height // 2
    img.paste(lg, ((w - lw) // 2, ly), lg)
    img.save(os.path.join(D, name), quality=95)
    print(name, img.size)

post(1080, 1350, "remembrance_day_2026_feed.jpg")
post(1080, 1920, "remembrance_day_2026_story.jpg")
