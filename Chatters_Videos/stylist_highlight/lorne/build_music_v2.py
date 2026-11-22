"""New beds for the Lorne highlight (user 2026-11-23: "use different music"): groove-based, not the
pizzicato/piano/guitar set. 92 BPM, Am7-Dm7-G7-Cmaj7 (own composition), drum kit on channel 10.
D_pop (Rhodes + finger bass + pop kit), E_lofi (soft EP, swung hats, no snare backbeat until bar 3), F_funk (clav + slap bass).
Final Cmaj7 rings from the END beat (CTA shot)."""
import subprocess
import sys

import mido

D = sys.path[0] + "/"
BPM, TPB, END = 92, 480, 26.5
CH = [(45, [57, 60, 64, 67]), (50, [57, 60, 62, 65]), (43, [55, 59, 62, 65]), (48, [55, 59, 64, 67])]
OPTS = {"D_pop": (4, 33, 0.0, True), "E_lofi": (4, 32, 0.12, False), "F_funk": (7, 36, 0.0, True)}


def build(name, cprog, bprog, swing, backbeat):
    mid = mido.MidiFile(ticks_per_beat=TPB)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr += [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)),
           mido.Message("program_change", channel=0, program=cprog),
           mido.Message("program_change", channel=1, program=bprog)]
    ev = []

    def note(ch, n, b0, dur, v):
        ev.append((int(b0 * TPB), mido.Message("note_on", channel=ch, note=n, velocity=v)))
        ev.append((int((b0 + dur) * TPB), mido.Message("note_off", channel=ch, note=n)))

    for bar in range(int(END // 4) + 1):
        b = bar * 4
        if b >= END:
            break
        bass, chord = CH[bar % 4]
        for k, (off, dur) in enumerate([(0, 1.4), (1.5, .4), (2, 1.4), (3.5, .4)]):  # chord stabs
            if b + off < END:
                for m in chord:
                    note(0, m, b + off, dur, 62 if k % 2 == 0 else 50)
        for off, n in [(0, 0), (.75, 0), (1.5, 7), (2, 0), (2.75, 12), (3.5, 7)]:  # bass line
            if b + off < END:
                note(1, bass - 12 + n, b + off, .4, 80)
        for e8 in range(8):  # drums
            t = b + e8 * .5 + (swing if e8 % 2 else 0)
            if t >= END:
                break
            note(9, 42, t, .1, 55 if e8 % 2 else 70)       # closed hat
            if e8 in (0, 5):
                note(9, 36, t, .1, 95)                      # kick
            if e8 in (2, 6) and (backbeat or bar >= 2):
                note(9, 38 if backbeat else 37, t, .1, 85)  # snare / rim
    for m in [48, 55, 59, 64, 67, 71]:  # final Cmaj7
        note(0, m, END, 5, 70)
    note(1, 36, END, 5, 80)
    note(9, 49, END, 2, 70)  # crash on the CTA
    ev.sort(key=lambda e: (e[0], e[1].type == "note_on"))
    last = 0
    for t, m in ev:
        tr.append(m.copy(time=t - last))
        last = t
    p = D + f"music_{name}.mid"
    mid.save(p)
    return p


for name, a in OPTS.items():
    m = build(name, *a)
    raw = D + f"music_{name}_raw.wav"
    subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "48000", "-F", raw, "/usr/share/sounds/sf2/FluidR3_GM.sf2", m],
                   check=True, capture_output=True)
    print("rendered", raw)
