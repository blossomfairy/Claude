"""Lucky birthday post: feed (1080x1350), story (1080x1920) and a 16.5 s reel with a piano Happy Birthday."""
import math, random, subprocess, sys
import mido
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = sys.path[0] + "/"
TEAL, AQUA, INK, GREY = (0, 131, 141), (169, 219, 219), (19, 18, 19), (106, 108, 106)
F = lambda n, s: ImageFont.truetype(D + "fonts/" + n, s)
logo = Image.open(D + "logo_dark.png")

def confetti(w, h, n=70, seed=7):
    r = random.Random(seed)
    return [dict(x=r.uniform(0, w), y=r.uniform(-h, h), s=r.uniform(8, 20), a=r.uniform(0, 360),
                 c=r.choice([TEAL, AQUA, (0, 104, 112), (210, 236, 236)]), v=r.uniform(40, 90), sp=r.uniform(-40, 40),
                 round=r.random() < 0.4) for _ in range(n)]

def background(w, h):
    bg = Image.new("RGB", (w, h))
    px = bg.load()
    for y in range(h):  # aqua top -> white bottom
        t = min(1, y / (h * 0.85))
        c = tuple(int(AQUA[i] + (255 - AQUA[i]) * t) for i in range(3))
        for x in range(w): px[x, y] = c
    return bg

def draw_confetti(img, pieces, t, h, keep_clear):
    d = ImageDraw.Draw(img, "RGBA")
    for p in pieces:
        y = (p["y"] + p["v"] * t) % (h + 60) - 30
        x = p["x"] + 12 * math.sin(t * 1.3 + p["a"])
        if keep_clear[0] < y < keep_clear[1] and 90 < x < img.width - 90: continue  # keep text area clean
        s = p["s"]
        if p["round"]:
            d.ellipse((x - s / 2, y - s / 2, x + s / 2, y + s / 2), fill=p["c"] + (230,))
        else:
            ang = math.radians(p["a"] + p["sp"] * t)
            pts = [(x + math.cos(ang + k) * s * m, y + math.sin(ang + k) * s * m)
                   for k, m in ((0, 0.6), (math.pi / 2, 0.25), (math.pi, 0.6), (3 * math.pi / 2, 0.25))]
            d.polygon(pts, fill=p["c"] + (230,))

def centred(img, text, font, y, fill, a=1.0):
    if a <= 0: return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.text(((img.width - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill + (int(255 * a),))
    img.alpha_composite(layer)

def card(w, h, t=None):
    """t=None renders the finished still; a time in seconds renders a reel frame with staggered fades."""
    tall = h > 1500
    img = background(w, h).convert("RGBA")
    top = int(h * (0.30 if tall else 0.22))
    draw_confetti(img, confetti(w, h), 0 if t is None else t, h, (top - 40, h - (190 if tall else 60)))  # text + logo stay clear
    fa = lambda t0: 1.0 if t is None else max(0, min(1, (t - t0) / 0.6))
    centred(img, "Happy birthday", F("GreatVibes.ttf", 150), top, TEAL, fa(0.3))
    centred(img, "Lucky", F("Playfair.ttf", 210), top + 170, INK, fa(0.9))
    body = F("Montserrat.ttf", 44)
    lines = ["Wishing you the sweetest birthday", "while you enjoy maternity leave.", "We miss you at Lawson Heights!"]
    for i, line in enumerate(lines):
        centred(img, line, body, top + 470 + i * 64, GREY, fa(2.0 + 0.3 * i))
    centred(img, "Love, your Chatters family", F("GreatVibes.ttf", 92), top + 700, TEAL, fa(3.4))
    L = logo.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * fa(4.0))))
    img.alpha_composite(L, ((w - L.width) // 2, h - (330 if tall else 190)))
    return img.convert("RGB")

def music(path_wav):
    """Happy Birthday (public domain) on GM acoustic piano, 3/4 at 100 BPM, light left-hand chords."""
    D4, E4, Fs4, G4, A4, B4, C5, D5 = 62, 64, 66, 67, 69, 71, 72, 74
    mel = [(D4, 0, .75), (D4, .75, .25), (E4, 1, 1), (D4, 2, 1), (G4, 3, 1), (Fs4, 4, 2),
           (D4, 6, .75), (D4, 6.75, .25), (E4, 7, 1), (D4, 8, 1), (A4, 9, 1), (G4, 10, 2),
           (D4, 12, .75), (D4, 12.75, .25), (D5, 13, 1), (B4, 14, 1), (G4, 15, 1), (Fs4, 16, 1), (E4, 17, 1),
           (C5, 18, .75), (C5, 18.75, .25), (B4, 19, 1), (G4, 20, 1), (A4, 21, 1), (G4, 22, 3.5)]
    G, Dm, C = [43, 55, 59, 62], [38, 54, 57, 60], [36, 55, 60, 64]
    chords = [(G, 1), (Dm, 4), (Dm, 7), (G, 10), (G, 13), (C, 16), (G, 19), (Dm, 21), (G, 22)]
    ev = [(b, n, dur, 70) for n, b, dur in mel]
    for i, (ch, b) in enumerate(chords):
        nxt = chords[i + 1][1] if i + 1 < len(chords) else b + 3.5
        ev += [(b, n, nxt - b, 44) for n in ch]
    tpb, msgs = 480, []
    for b, n, dur, v in ev:
        msgs += [(int(b * tpb), 1, n, v), (int((b + dur) * tpb), 0, n, 0)]
    mid = mido.MidiFile(ticks_per_beat=tpb); tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr += [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(100)), mido.Message("program_change", program=0)]
    last = 0
    for tick, on, n, v in sorted(msgs):
        tr.append(mido.Message("note_on" if on else "note_off", note=n, velocity=v, time=tick - last)); last = tick
    mid.save(D + "hb.mid")
    subprocess.run(["fluidsynth", "-ni", "-g", "0.8", "-r", "48000", "-F", path_wav, "/usr/share/sounds/sf2/FluidR3_GM.sf2", D + "hb.mid"],
                   check=True, capture_output=True)

if __name__ == "__main__":
    card(1080, 1350).save(D + "CHATTERS_LUCKY_birthday_feed_4x5.jpg", quality=95)
    card(1080, 1920).save(D + "CHATTERS_LUCKY_birthday_story_9x16.jpg", quality=95)
    if "--reel" in sys.argv:
        music(D + "hb.wav")
        FPS, DUR = 30, 16.5
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                               "-pix_fmt", "yuv420p", "-movflags", "+faststart", D + "reel_silent.mp4"], stdin=subprocess.PIPE)
        for n in range(int(DUR * FPS)):
            ff.stdin.write(card(1080, 1920, n / FPS).tobytes())
        ff.stdin.close(); ff.wait()
