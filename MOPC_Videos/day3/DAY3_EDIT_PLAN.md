# MOPC Day 3 (Oct 8 install + tower repair): edit plan

Source: Drive `Footage Day 3` (New Brooklyn Media). Review data: Drive `MOPC Footage Day 3 review` (audio_verify.json, *_av.jpg sheets, *_listen.mp3).
Rules applied: mopc-content, mopc-video-editor, mopc-color-grade, footage-editing-pipeline, Oct 8 shoot guide (`MOPC_Install_Shoot_Ad_Guide_Oct8.pdf`).

## Shot log (every FX9 + R5C clip seen on contact sheets)

| Clip | Dur | Picture | Sound | Use |
|---|---|---|---|---|
| FX9 1451 | 6.7 s | Wide: MOPC van at a rural home, crew walking, two dogs | crew chatter | Opener / establishing |
| FX9 1453 | 9.2 s | Crew + homeowner briefing in the yard, faces visible | "You go down to the pole…" | Faces early; music under |
| FX9 1499 | 14.7 s | Two crew walking a gravel lane, fall colours, dog | unrelated chatter (do not use) | B-roll |
| FX9 1512 | 38.4 s | Tech preps gear by MOPC truck, looks up at pole, gets in cab | silent | B-roll |
| FX9 1513 | 8.7 s | Dog on the lawn | silent | Warmth insert |
| FX9 1514 | 13.3 s | Installer in hard hat mounting on the house siding | silent | Install hero |
| FX9 1536 | 18.2 s | VERTICAL (rotated). Two installers in front of van, line, walk off | line at 5.7–9.9 | Sign-off (see flags) |
| FX9 1537 | 16.5 s | VERTICAL. Same set-up | line at 2.9–7.0 (cleanest) | Sign-off (see flags) |
| FX9 1538 | 44.5 s | VERTICAL. Tech at van door, resets | 2nd take 32.1–37.2 | Back-up take |
| FX9 1548 | 33.0 s | Hands scrolling a phone by a ladder | chatter | Only after checking the screen for personal info |
| FX9 1562 | 7.7 s | Tower site, truck, staff walking | silent | 5–8 s only (Ford grille logo in 0–5 s) |
| FX9 1563 | 85.9 s | Tech gearing up in harness at the tower, MOPC truck, "Built For Us" hoodie | silent | Prep B-roll |
| R5C 266 | 16.5 s | not on a sheet yet | no speech (earlier "Thank you for watching" was a Whisper hallucination) | Check by eye |
| R5C 267 | 137.7 s | Tower climb, wide to close, gear at the top | crew "That's crazy, man" | Hero B-roll |
| Drone 0916–0944 | ~20 clips | NOT viewed yet | n/a | Reveal shots, pick by eye |

## Flags to decide before cutting (brand rules)
1. **The sign-off is a fed line delivered to camera.** The slate says "Right to the camera, action". That breaks three rules: the shoot guide's "questions, not lines", the mopc-video-editor rejected entry for interviewer-fed taglines (2026-10-08), and no direct eye contact. Default: the b-roll cuts below work **without** it. The 9:16 cut uses it only if you approve.
2. "Another **happy customer**": captions must not add "customer" anywhere else (the audience is *subscribers*). Spoken words stay verbatim in burned captions.
3. **No homeowner or staff speaking on camera** anywhere in Day 3, so the guide's face-first and "every voice has a face" spots (Bob A–C, Olivia, In-stream 15/30 with dialogue) can't be built from this day. What can be built is a music-led "day of the work" piece.
4. **Grade is per camera**:
   - FX9 is S-Log3 / S-Gamut3.Cine. Use `mopc_femu_learned_v1.cube` (fitted on FS7, same encoding, untested on FX9). It must pass the `mopc_qc.py` `natural` check.
   - The R5C is C-Log3. The learned cube does NOT apply; it needs a Canon C-Log3 / Cinema Gamut to Rec.709 LUT.
   - Drone is D-Log. The skill note "DJI is already Rec.709" is wrong for Day 3; it needs the DJI D-Log to Rec.709 LUT.
5. Third-party brand: the Ford grille in 1562 at 0–5 s and the truck front in 1512. Keep them out of frame.
6. "Pictou County" in the first 3 s (Meta) or 5 s (YouTube) has to be a super, because nobody says it.

## Cuts (timecodes from 5 s contact sheets: confirm each in/out by eye)
- `cuts_916_18s.csv`: Meta Reel, 9:16. Faces, prep, tower, install, sign-off (if approved), end card.
- `cuts_169_30s.csv`: YouTube in-stream 30, 16:9. No vertical shots, no dialogue; music bed.
- `cuts_bumper6.csv`: 6 s bumper, 16:9 + 9:16.

## Build (on the PC, WSL, per mopc-video-editor)
```
~/.venvs/music/bin/python build_day3.py cuts_916_18s.csv --src ~/day3_src --out ~/day3_out/reel_916.mp4 \
  --size 1080x1920 --fx9-cube ~/mopc_lut/mopc_femu_learned_v1.cube --r5c-lut ~/luts/clog3_709.cube \
  --dlog-lut ~/luts/dji_dlog_709.cube --endcard ENDCARD_916.mp4 --music BED.wav
~/.venvs/music/bin/python .../mopc-video-editor/scripts/mopc_qc.py ~/day3_out/reel_916.mp4
```
- Copy the source clips off `G:\My Drive` to local disk first. Never render onto the Drive mount.
- Cuts are re-encoded, never `-c copy`. The script refuses any shot that would need upscaling. The vertical clips are rotated, and the rotation direction must be confirmed on the first frame.
- Loudness: -14 LUFS integrated, ≤ -1 dBTP (two-pass). Keep the speaker's own pause at joins.
- Titles are ink on a paper or tint pill (`video.py lower_third/caption`), never white text with a drop shadow. Logo and end card follow the mopc.json rules.
- Gates before delivery: `mopc_qc.py` exit 0, `ad_check`, contrast ≥ 4.5, a faces-vs-text check, and a look at the contact sheet.

## Decisions (2026-10-25, after research)
| Decision | Choice | Why |
|---|---|---|
| Sign-off line | **Drop the words. Keep the installers walking back to the van (1537 7.0–9.5 s) as a wordless closer.** | The line was cued ("Right to the camera. Action."), repeated over several takes and delivered into the lens. That breaks the no-eye-contact rule, the guide's "questions, not lines", and the 2026-10-08 rejected entry. Research found no hard data either way; practitioner sources consistently say natural, unscripted delivery beats polished scripted lines on Meta. |
| R5C grade | **Canon official C-Log3 / Cinema Gamut to BT.709, 65-point 3D LUT** (Canon support page for the EOS R5 C, "Canon lookup table"). Correct exposure before the LUT. | The learned cube is FS7 S-Log3 only. Third-party packs are unverified. |
| Drone grade | **DJI official Mavic 3 "D-Log to Rec.709" LUT** (dji.com/lut). | The SRT metadata says `color_md: d_log` (not D-Log M), f/2.8 variable aperture. |
| Jev review | Spec ready: `jev_review_day3.json`. **Not sent: no key in this session.** | Run `jev_adapters.py send jev_review_day3.json`, then again with `--reverse`, and act only where both orders agree. |

The drone SRT files carry GPS for the shoot location. Never publish them.
