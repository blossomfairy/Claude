"""Three 92 BPM beds (pizzicato / piano / nylon guitar), F-Dm-Bb-C, final F chord rings out on the end card."""
import mido, subprocess, sys
D = sys.path[0] + "/"
BPM, TPB = 92, 480
CHORDS = [(53, [65, 69, 72]), (50, [62, 65, 69]), (46, [62, 65, 70]), (48, [64, 67, 72])]  # bass, triad
OPTS = {"A_pizz": (45, 45), "B_piano": (0, 0), "C_guitar": (24, 32)}  # (melody prog, bass prog)

END = 38  # beat where the END shot starts
FINAL = set()

def build(name, prog, bprog):
    FINAL.clear()
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr += [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)),
           mido.Message("program_change", channel=0, program=prog),
           mido.Message("program_change", channel=1, program=bprog)]
    ev = []  # (tick, msg)
    def note(ch, n, b0, dur, v):
        if b0 >= END and n not in FINAL: return
        ev.append((int(b0 * TPB), mido.Message("note_on", channel=ch, note=n, velocity=v)))
        ev.append((int((b0 + dur) * TPB), mido.Message("note_off", channel=ch, note=n)))
    bars = 10  # groove until END beat (end-card cut), then final chord
    for bar in range(bars):
        bass, tri = CHORDS[bar % 4]
        b = bar * 4
        note(1, bass - 12 if bprog != 0 else bass - 12, b, 1.8, 70); note(1, bass - 12, b + 2, 1.8, 60)
        pat = [tri[0], tri[1], tri[2], tri[1] + 12, tri[2], tri[1], tri[0] + 12, tri[2]]  # 8th-note arpeggio
        for k, n in enumerate(pat):
            v = 62 + (10 if k % 2 == 0 else 0) - (8 if bar == 0 and k < 4 else 0)
            note(0, n, b + k * 0.5, 0.45 if prog == 45 else 0.9, v)
    end = END
    for n in (41, 65, 69, 72, 77): FINAL.add(n)
    note(1, 41, end, 6, 70)
    for n in (65, 69, 72, 77): note(0, n, end, 6, 66)
    ev.sort(key=lambda e: (e[0], e[1].type == "note_on"))
    last = 0
    for t, m in ev:
        tr.append(m.copy(time=t - last)); last = t
    p = D + f"music_{name}.mid"; mid.save(p); return p

for name, (p, bp) in OPTS.items():
    m = build(name, p, bp)
    raw = D + f"music_{name}_raw.wav"
    subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "48000", "-F", raw, "/usr/share/sounds/sf2/FluidR3_GM.sf2", m],
                   check=True, capture_output=True)
    print("rendered", raw)
