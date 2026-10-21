# Kidvy Pickup — 30 s ad: arrival + hand-off (v2, rough cut)

Rules: kidvy-pickup + kidvy-pickup-ad (12 criteria) + kidvy-music-director (Drive skills, read 2026-10-21).
Footage: Drive › Adobe_Stock (15 Adobe Stock clips, licensed by the owner). Framing: "check-in" = « Je suis là » / "I’m here"; "check-out" = « Remis au parent » / "Handed over". Pills over footage, never a step-by-step walk-through.

## Locked cut (100 BPM grid: 1 bar = 2.4 s = 60 frames at 25 fps; every cut on a bar line)
| s | Adobe Stock clip @ in-point | Picture | Pill (exact app string) | Caption FR / EN |
|---|---|---|---|---|
| 0.0–2.4 | 624086363 @ 2.0 | impatient line of parents | — | La file au portail. / The line at the gate. |
| 2.4–4.8 | 424171310 @ 2.0 | walkie-talkie close-up | — | Le walkie-talkie. L’attente. / The walkie-talkie. The wait. |
| 4.8–7.2 | 624086363 @ 9.5 | a waiting face | — | (same) |
| 7.2–9.6 | 283680613 @ 1.0 | phone in a parent’s hand | « Je suis là » → « L’école est avisée. Merci de patienter. » | Juste « Je suis là ». / Just “I’m here.” |
| 9.6–12.0 | 1831479379 @ 1.0 | teacher looks at a tablet | — | La classe le voit à l’écran. L’enfant se prépare. / The class sees it on screen. The child gets ready. |
| 12.0–14.4 | 2115633640 @ 3.0 | teacher helps a child with her backpack | — | (same) |
| 14.4–19.2 | 678770640 @ 0.0 | girl runs to her dad, hug — **music lift at 16.8** | « Remis au parent » / "Handed over" | L’enfant est remis. / The child is handed over. |
| 19.2–21.6 | 573153209 @ 3.5 | hands join | — | Chaque enfant remis est noté. L’esprit tranquille. / Each hand-off is on record. Peace of mind. |
| 21.6–26.4 | 753350890 @ 2.5 | same girl + dad walk off hand in hand | — | (same) |
| 26.4–30.0 | end card | logo + tagline + CTA | — | Le ramassage, plus simple et plus calme. Demandez une démo : kidvy.com/pickup / Pickup, simpler and calmer. Request a demo: kidvy.com/pickup |

## Music — 3 original options (you pick; nothing approved yet)
Composed to the locked cut (`compose.py`, own composition rendered with the FluidR3 GM soundfont, MIT licence). Same form for all: soft open (0–7.2), rhythm enters on « Je suis là » (7.2), one lift on the hand-off (16.8), resolve on the end card (26.4).
- **A** felt piano + nylon guitar, D major (default) · **B** piano + pizzicato strings, G major · **C** felt piano + soft shaker + warm pad, C major.
- Hits measured vs the cut: 7.2 / 16.8 / 26.4 s within −54…+29 ms (limit 2 frames = 80 ms).

## QC (all 6 renders, 2026-10-21)
| Criterion | Rule | Measured |
|---|---|---|
| Duration | 30 s | 30.000 s |
| Hook | people, no app, ≤ 3 s | 0–2.4 s line of parents, no UI |
| UI share | ≤ 30 % of frames | ≈ 4.4 s / 30 s ≈ 15 %; longest UI run ≈ 2.2 s |
| UI form | ≥ 70 % pill/phone-in-hand | 100 % pills over footage |
| Shots | mean 2.4–3.1 s, none > 5 s | 9 shots / 26.4 s = 2.93 s mean, longest 4.8 s; scene detector cuts = 2.4, 4.8 … 26.4 exactly |
| End card | ≤ 4 s, logo + one action | 3.6 s, slow push, freezedetect (n=0.003, d=2): 0 freezes |
| Captions | ≤ 155 wpm | max 143 wpm (EN C1) |
| Loudness | −14 LUFS, ≤ −1 dBTP, LRA ≤ 6 | −14.0 LUFS, −2.0…−1.8 dBTP, LRA 4.4 LU (AAC 320k) |
| Claims | brief §9 | emulated claims-lint grep: no hits (real `claims_lint.py` not in this session) |

## Build
1. Proxies: Adobe_Stock clips → 1080p 25 fps H.264 (`AdobeStock_<id>.mp4`) in one folder.
2. `node kidvy/ad30/screens.js` (pills, end card) → `python3 -I kidvy/ad30/compose.py` (music) → `python3 -I kidvy/ad30/build.py fr en --stock <proxies> --music A|B|C`.

## Open items (hand-off list)
1. Pick music A, B or C.
2. CTA kidvy.com/pickup still returns 404 (checked 2026-10-21) → must be live before release.
3. No VO: no recording from the client’s paid voice talent yet → captions carry the words (no temporary text-to-speech, per kidvy-pickup-ad).
4. Casting: the parents in the queue (624086363) and the classroom teacher/child (1831479379, 2115633640) are different people from the hero dad and girl. Acceptable as "other families / staff"; the owner should confirm. Kids appear as licensed stock actors (owner still to confirm, brief §9).
5. Counsel check before paid ads: « Chaque enfant remis est noté » / "Each hand-off is on record".
6. Only 16:9 delivered; 9:16 and 1:1 need native reframes.
7. Final masters not uploaded to Drive (the connector can't carry 31 MB files); copy from the session or the repo outputs.
