---
name: ai-video-ads
description: End-to-end production of short realistic AI video ads (Reels/Shorts/TikTok, 9:16 or 16:9) from reference videos: reference analysis, concept, photoreal shot generation, frame-by-frame QC, tracking/compositing fixes, music, captions, brand end card, loudness. Use for any "make a video/ad like this link" request, and for fixing details in generated footage. Built from the MOPC "Not everything is reliable" spot; includes MOPC brand specs.
---

# AI Video Ads

Goal: a spot a picky client and locals cannot fault. Everything below was learned from real client rejections; each rule exists because it was flagged.

## 1. Study the references first (free, do before any spend)
- Download: `scripts/fetch_ref.sh <url> <outdir>` (yt-dlp; Vimeo falls back to player-page HLS). Facebook reels work with yt-dlp.
- Frame sheet: `ffmpeg -i ref.mp4 -vf "fps=1/2,scale=240:-1,tile=6x6" -frames:v 1 sheet.jpg`, then view it.
- Transcribe VO/lyrics: `python3 scripts/transcribe.py ref.mp4` (faster-whisper; decodes via ffmpeg so no PyAV issues).
- Write down: structure (montage? single gag?), shot length, camera (static/handheld), grade, music role (ironic? sincere?), VO, payoff line, end card. Copy the *mechanism*, never the footage.

## 2. Concept rules
- Name the persona (see the brand skill) and the single message. Payoff shot must *show* the message (a call must be visibly working, not implied).
- Do not make location claims you cannot prove. AI cannot reproduce real places; "Not everything in <town>" invites locals to call it out. Either use real location photos as plates or keep claims generic.
- Locale accuracy: red sand = PEI, not Pictou County (pale/golden sand). Check climate, vehicles, landscape, signage conventions for the claimed region.
- Claims: no speeds/prices/coverage; route to "check your address". Flag any reliability wording for client approval.

## 3. Generation recipe (Higgsfield MCP)
Order: location plate → (optional keyframe still) → video. Never text-only video for hero shots.
1. **Location plate**: `soul_cinematic`, 2k, 9:16, "Photoreal documentary film still … Empty scene, no people, no text, no logos." ~0.12 cr each; make 2 takes.
   - Soul Cinema draws people into "empty" plates often. Inspect every plate; reject any with a person, readable text, or wrong logic (bare road when snow is needed, no visible ice, etc.).
2. **Keyframe-first when details matter** (screens, props, identity): edit a real frame with `gpt_image_2_5` (quality high, 2k) using the frame as `image_references`; change ONE thing; zoom-check the whole still for collateral changes. ~0.25 cr.
3. **Video**:
   - `seedance_2_5` omni_reference, 720p, 5s, plate as `image_references` (~35 cr). Best realism + native SFX.
   - `kling3_0` std 5s with `start_image` (~7.5 cr, silent with sound off). Best for animating an approved keyframe cheaply; keeps screen content.
   - Always `get_cost:true` first. Canary one shot before batching. If a "preset recommended" error appears, resubmit with `declined_preset_id`.
4. Prompt blocks that prevent the flagged failures:
   - Eye contact: "seen from behind / in side profile … never turns toward the camera". Back-to-camera is the only guaranteed fix.
   - Physics/logic: name the mechanism explicitly ("plow truck with a large steel blade on its front; the blade throws road snow"; "road fully covered in snow, no bare pavement"; "brown rubber-soled winter boots, not skates").
   - Continuity: restate colours/patterns that must hold ("keeps its red, blue and white stripes the whole time").
   - Screens: models invent a self-view thumbnail with a stranger. Either design it in a keyframe (step 2) or composite it (section 5).
   - Framing: "camera closer than the reference: medium shot, subject fills a third of the frame" so gags read on a phone.
   - Always end with "no music, no speech, no text, no logos" unless dialogue is wanted.
5. Poll with `jobs_wait`; while waiting, schedule a check-in (`send_later`) rather than spin.

## 4. QC — run on EVERY clip before editing, and on the final render
Make sheets: `scripts/qc_sheet.sh clip.mp4` (2 fps, 5x2) and zoom crops at native res of: faces, hands, screens/monitors, reflections, signage, plates, background people.
Checklist (one line per item, pass/fail):
- [ ] Setting logic (snow on the road being plowed, ice looks frozen, props used correctly)
- [ ] Physics/cause→effect (snow comes from the blade, wave doesn't appear before the cause)
- [ ] Eye contact with lens (also self-views and on-screen people; flag those)
- [ ] Identity/clothing continuity within and across shots
- [ ] Object continuity (pattern/colour/props)
- [ ] Screens: every face on a screen is the right person; self-view mirrors the person's actions
- [ ] Locale accuracy for any implied place
- [ ] Stray text, logos, readable plates/signs
- [ ] Gag readable at phone size
- [ ] Audio: speech/voices only where mouths match (`python3 scripts/transcribe.py` with VAD); SFX belong to the clip that made them. Never borrow audio from another render of a shot.
- [ ] Captions don't cover the action or the payoff (screens!), stay out of UI safe zones (top 250 px, bottom 400 px on 9:16)
Report failures as a table: shot · problem · fix. Fix before showing; never deliver an unchecked render.

## 5. Fixing footage in post (no regeneration)
- **Track a small region** (thumbnail, sign, screen corner): `python3 scripts/track.py clip.mp4 x y w h out.npy` — multi-scale template tracking, handles push-ins; verify with its overlay PNG.
- **Paint out** a tracked region: `scripts/paintout.py` (fills from a clean sampled area, grain, feathered). Only acceptable for tiny UI elements; a visible patch is a fail, and removing expected UI (self-view) looks wrong.
- **Composite a synced insert** (e.g., self-view that mirrors the person): generate the insert with matching action timing (map the hero's actions at 4 fps first), then `scripts/composite_insert.py` (mirror, per-frame colour/contrast match to the original region, feathered paste into tracked boxes). Check sync at 4-5 timestamps side by side.
- Never edit faces with local code; regenerate or composite whole generated subjects.

## 6. Edit, music, captions, end card
- Edit: `scripts/edit.sh` — shot list `"file in dur [vf]"`, upscale to 1080x1920 lanczos, 30 fps, overlays with time windows, song from an offset, end card, loudnorm. Trim to the gag (2.5-3.5 s per vignette); trim away any frame with eye contact.
- Music: public-domain recordings from Internet Archive 78rpm (`collection:georgeblood`). Pre-1929 US recordings of songs by composers dead before 1972 are PD in both Canada and the US. Ironic/period songs suit montage comedy. Transcribe lyrics and check every line is ad-safe.
- Loudness: `-14 LUFS`, true peak ≤ -1 dBTP. Single-pass loudnorm undershoots; follow with `volume=+3dB,aresample=192000,alimiter=limit=0.75:level=disabled,aresample=48000` and measure with `ebur128=peak=true`.
- Fonts: download Google Fonts TTF via `cdn.jsdelivr.net/gh/google/fonts@main/ofl/<family>/<File>%5Bwght%5D.ttf` (github raw is blocked); set variable weight with `font.set_variation_by_name(b'Bold')`.

## 7. MOPC Network specs (measured from the client's approved bumper reels)
- End card (9:16): background RGB(241,242,245); colour logo `MOPC_Logo_Colour.svg` (Drive id 1Omrh8M0dbjYzRp7w863AZH_Txl6zWp-J, public download via drive.usercontent) rasterised at 540 px wide, top at y=766; green pill RGB(137,187,59) x 280-799, y 1032-1151, white Montserrat Bold "Check your address."; hard cut, ~3.5 s. `scripts/brand_overlays.py` renders it.
- Captions: purple RGB(120,77,158) rounded box (radius 20), white Montserrat Bold 64 px, box height 112.
- Name tag: white box, navy RGB(40,64,120) Montserrat Bold 40 px, top-left (80,300).
- Brand rules: no direct eye contact, no third-party logos, no speeds/prices, CTA = check availability at the address. Pictou County locals will catch fake locations.
- Ad guide (Oct 8 shoot) prefers real people, documentary; disclose when a spot is AI-generated.

## 8. Budget discipline
- Quote every model before use. Typical: plate 0.12, gpt_image 0.25, Kling 5 s 7.5, Seedance 5 s 720p 35 (1080p 80).
- Spend on the fewest shots that carry the idea; reserve ~20% for fixes. Tell the user remaining credits after each round.
