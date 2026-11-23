# Stylist Highlight series

One reel per stylist from one template: `python3 build_highlight.py <stylist>` → `<stylist>/CHATTERS_<NAME>_stylist_highlight_SILENT.mp4`; then in `<stylist>/`: `python3 build_music.py && bash mux.sh`.

Structure (20-21 s, 92 BPM): moving hook + "Meet / NAME" → lower third "NAME, TITLE" → before / process / after with labels and a flash reveal → skills line → one verified proof line → "Book with NAME" + chatters.ca / phone + white logo, pulling back to the hook framing so it loops.

Rules: every on-screen claim comes from `chatters-brand/assets/facts.json` (title from the booking roster, proof from reviews) and is cited in the stylist's config. No faces, mirror reflections or clients without consent.

| # | Stylist | Status | Source footage |
|---|---|---|---|
| 1 | Lorne | built 2026-11-23 | stills from the 2026-10-18 cut/perm/style reel |
| 2 | Marina | next | `marina_colour_cut_style`, `marina_before_after` |
| 3 | Asma | next | `asma_*` (not on the online roster: CTA "call and ask for Asma") |
| 4 | Gabby | next | `gabby_colour_cut_style` (title unknown) |

Pacing note: house_check at the default threshold merges cuts between stills of the same client (Lorne measured 0.58 cps); the edit list is 24 cuts / 20.5 s = 1.17 cps, median 0.65 s, longest 1.63 s before the end card.
