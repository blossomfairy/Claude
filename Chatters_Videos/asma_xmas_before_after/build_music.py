"""Christmas beds: "Jingle Bells" chorus (James Lord Pierpont, 1857, public domain), own arrangement.
Cut-time feel: one melody quarter = an eighth of the 92 BPM video grid, so cuts land on the half-note pulse.
3 options (celesta + sleigh bells / piano + bells / music box + strings), all end on a held C chord at the reveal.
"""
import subprocess
import sys

import mido

D = sys.path[0] + "/"
BPM, TPB = 92, 480
Q = 0.5  # one melody quarter = half a video beat
C4, D4, E4, F4, G4 = 60, 62, 64, 65, 67
C5 = 72
MEL = [  # (note, melody quarters)
    (E4, 1), (E4, 1), (E4, 2), (E4, 1), (E4, 1), (E4, 2), (E4, 1), (G4, 1), (C4, 1.5), (D4, .5), (E4, 4),
    (F4, 1), (F4, 1), (F4, 1.5), (F4, .5), (F4, 1), (E4, 1), (E4, 1), (E4, .5), (E4, .5), (E4, 1), (D4, 1), (D4, 1),
    (E4, 1), (D4, 2), (G4, 2),
    (E4, 1), (E4, 1), (E4, 2), (E4, 1), (E4, 1), (E4, 2), (E4, 1), (G4, 1), (C4, 1.5), (D4, .5), (E4, 4),
    (F4, 1), (F4, 1), (F4, 1), (F4, 1), (F4, 1), (E4, 1), (E4, 1), (E4, .5), (E4, .5), (G4, 1), (G4, 1), (F4, 1),
    (D4, 1), (C4, 4),
]
CH = {"C": (48, [60, 64, 67]), "F": (41, [60, 65, 69]), "D7": (50, [62, 66, 72]), "G7": (43, [59, 62, 65])}
BARS = ["C", "C", "C", "C", "F", "C", "D7", "G7", "C", "C", "C", "C", "F", "C", "G7", "C"]  # 4 melody quarters each
OPTS = {  # melody prog, chord prog, bass prog, bells
    "A_celesta": (8, 0, 32, True),
    "B_piano": (0, 0, 32, True),
    "C_musicbox": (10, 48, 32, False),
}


def build(name, mprog, cprog, bprog, bells):
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr += [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)),
           mido.Message("program_change", channel=0, program=mprog),
           mido.Message("program_change", channel=1, program=cprog),
           mido.Message("program_change", channel=2, program=bprog)]
    ev = []

    def note(ch, n, b0, dur, v):
        ev.append((int(b0 * TPB), mido.Message("note_on", channel=ch, note=n, velocity=v)))
        ev.append((int((b0 + dur) * TPB), mido.Message("note_off", channel=ch, note=n)))

    b = 0.0
    for n, d in MEL:
        note(0, n + 12, b * Q, d * Q * 0.92, 92)
        b += d
    total = b * Q
    for i, c in enumerate(BARS):
        bass, tri = CH[c]
        t0 = i * 4 * Q
        last = i == len(BARS) - 1
        for k in range(4 if not last else 1):  # oom-pah on melody quarters
            t = t0 + k * Q
            if k % 2 == 0:
                note(2, bass - 12 + (7 if k == 2 else 0), t, Q * 0.9 if not last else 2.5, 72)
            else:
                for m in tri:
                    note(1, m, t, Q * 0.8, 50 if cprog == 0 else 40)
        if last:
            for m in tri + [C5]:
                note(1, m, t0, 2.5, 60)
    if bells:
        t = 0.0
        while t < total - 1e-6:  # sleigh bells: tambourine on every melody eighth, accent on the pulse
            note(9, 54, t, 0.1, 70 if abs((t / Q) % 1) < 1e-6 else 42)
            t += Q / 2
        note(9, 81, total - 4 * Q, 2, 70)  # triangle ring on the last chord
    ev.sort(key=lambda e: (e[0], e[1].type == "note_on"))
    last = 0
    for t, m in ev:
        tr.append(m.copy(time=t - last))
        last = t
    p = D + f"music_{name}.mid"
    mid.save(p)
    return p, total


for name, (mp, cp, bp, bl) in OPTS.items():
    m, total = build(name, mp, cp, bp, bl)
    raw = D + f"music_{name}_raw.wav"
    subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "48000", "-F", raw, "/usr/share/sounds/sf2/FluidR3_GM.sf2", m],
                   check=True, capture_output=True)
    print("rendered", raw, f"{total} beats")
