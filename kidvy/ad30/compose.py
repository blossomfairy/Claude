"""Original music beds for the 30 s Kidvy Pickup ad (licence-clean: own composition, FluidR3 GM soundfont = MIT).

100 BPM, 4/4 -> 1 bar = 2.4 s = 60 frames at 25 fps, so every cut on a bar line lands on a downbeat (same grid as build.py).
Form (11 bars + ring-out to 30.0 s):
  bars 1-3   hook / problem    : soft piano (+pad), sparse (0-7.2 s)
  bars 4-7   « Je suis là »    : rhythm instrument enters at 7.2 s (guitar / pizz / shaker)
  bar  8     HAND-OFF (16.8 s) : the one lift - strings + bass + light percussion
  bars 8-11  hand-off + walk   : full bed
  bar 12     END CARD (26.4 s) : resolve on the tonic, ring out to 30.0 s
Run: python3 -I kidvy/ad30/compose.py  -> out/music/option_{A,B,C}.wav (48 kHz, raw; loudness set in the mix)
"""
import os, subprocess
import mido

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "music")
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM, TPB = 100, 480
BAR = 4 * TPB
LIFT_BAR, END_BEAT = 7, 11 * 4  # 0-based: bar 8 (16.8 s) = index 7; end card on bar 12 downbeat (26.4 s)

OPTIONS = {  # name: (tonic midi, progression as semitone offsets of chord roots (major/minor), instruments)
    "A": dict(key=62, desc="felt piano + nylon guitar, D major", rhythm=24, lead=0, pad=89, lift=48),
    "B": dict(key=67, desc="piano + pizzicato strings, G major", rhythm=45, lead=0, pad=88, lift=49),
    "C": dict(key=60, desc="felt piano + soft shaker + warm pad, C major", rhythm=None, lead=0, pad=89, lift=48),
}
# I - V/3 - vi - IV, two bars each would be slow; one chord per bar keeps it moving under 2.5 s shots
PROG = [(0, "M"), (7, "M"), (9, "m"), (5, "M")]


def chord(root, q):
    return [root, root + (4 if q == "M" else 3), root + 7]


def track(name, prog, ch):
    t = mido.MidiTrack()
    t.append(mido.MetaMessage("track_name", name=name))
    t.append(mido.Message("program_change", program=prog, channel=ch, time=0))
    return t


def place(events, track_):
    """events: list of (abs_tick, msg) -> delta-time track."""
    last = 0
    for tick, msg in sorted(events, key=lambda e: (e[0], e[1].type == "note_on")):
        track_.append(msg.copy(time=tick - last))
        last = tick


def note(ev, ch, n, start, dur, vel):
    ev.append((start, mido.Message("note_on", channel=ch, note=n, velocity=vel)))
    ev.append((start + dur, mido.Message("note_off", channel=ch, note=n, velocity=0)))


def compose(opt):
    o = OPTIONS[opt]
    key = o["key"]
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
    mid.tracks.append(tempo)
    piano, pad, rhy, lift, bass, perc = ([] for _ in range(6))
    end = END_BEAT * TPB
    for bar in range(12):
        r, q = PROG[bar % 4]
        c = chord(key + r - 12, q)
        b0 = bar * BAR
        if b0 >= end:
            break
        # piano: broken chord in 8ths, gentle; denser after the turn
        arp = [c[0], c[1] + 12, c[2], c[1] + 12, c[0] + 12, c[2], c[1] + 12, c[2] + 12]
        step = TPB // 2
        for i, n in enumerate(arp):
            t = b0 + i * step
            if t >= end:
                break
            if bar < 3 and i % 2:  # sparse in the hook
                continue
            note(piano, 0, n, t, step * 2, 52 + (6 if i == 0 else 0) + (6 if bar >= LIFT_BAR else 0))
        # pad: whole-bar chord, swells from bar 2
        if bar >= 1:
            for n in c:
                note(pad, 1, n - 12, b0, BAR - 10, 38 if bar < LIFT_BAR else 46)
        # rhythm layer from bar 4 (« Je suis là »)
        if bar >= 3:
            if o["rhythm"] is not None:
                for beat in range(4):
                    t = b0 + beat * TPB + (TPB // 2 if beat % 2 else 0)
                    for k, n in enumerate(c):
                        note(rhy, 2, n + 12, t + k * 18, TPB, 50 if bar < LIFT_BAR else 58)
            else:  # option C: soft shaker 8ths (GM 70 maracas)
                for i in range(8):
                    note(perc, 9, 70, b0 + i * (TPB // 2), 60, 34 + (10 if i % 2 == 0 else 0))
        # the lift: strings + bass + soft tambourine on 2 and 4, bars 8-10
        if LIFT_BAR <= bar <= 10:
            for n in c:
                note(lift, 3, n + 12, b0, BAR - 10, 54)
            note(bass, 4, c[0] - 12, b0, TPB * 2 - 10, 70)
            note(bass, 4, c[0] - 5, b0 + TPB * 2, TPB * 2 - 10, 64)
            for beat in (1, 3):
                note(perc, 9, 54, b0 + beat * TPB, 60, 30)
    # resolve on the tonic at the end card, ring out to 30 s
    tonic = chord(key - 12, "M")
    for n in tonic + [tonic[0] + 12, tonic[1] + 12]:
        note(piano, 0, n, end, TPB * 6, 58)
    for n in tonic:
        note(pad, 1, n - 12, end, TPB * 6, 40)
    note(bass, 4, tonic[0] - 12, end, TPB * 6, 56)
    for name, prog, ch, ev in (("piano", o["lead"], 0, piano), ("pad", o["pad"], 1, pad),
                               ("rhythm", o["rhythm"] or 0, 2, rhy), ("lift", o["lift"], 3, lift),
                               ("bass", 32, 4, bass), ("perc", 0, 9, perc)):
        if ev:
            t = track(name, prog, ch)
            place(ev, t)
            mid.tracks.append(t)
    os.makedirs(OUT, exist_ok=True)
    mpath, wpath = os.path.join(OUT, f"option_{opt}.mid"), os.path.join(OUT, f"option_{opt}_raw.wav")
    mid.save(mpath)
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-R", "1", "-C", "1", "-r", "48000", "-F", wpath, SF2, mpath],
                   check=True, capture_output=True)
    # exact 30.000 s, gentle 1.5 s fade at the very end (ring-out), stereo 48 kHz
    final = os.path.join(OUT, f"option_{opt}.wav")
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", wpath, "-af",
                    "apad,atrim=0:30,afade=t=out:st=28.5:d=1.5,aformat=sample_rates=48000:channel_layouts=stereo",
                    final], check=True)
    os.remove(wpath)
    return final, o["desc"]


if __name__ == "__main__":
    for k in OPTIONS:
        print(*compose(k))
