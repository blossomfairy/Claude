---
name: jev-adapters
description: Use when Jev (TypeSafe System One) must judge something it cannot do natively - video, audio, images, maths, dates, counting, extraction, multi-select, big option lists, long state, option-order bias. Each adapter moves that part into code and hands Jev a narrow text judgement.
---

# Jev adapters: teach Jev what it can't do

Hosted Jev cannot be retrained. "Teaching" it means two things:
1. **Adapters** (below): code converts the input so Jev only makes a snap judgement on text.
2. **Fine-tuning a local stand-in** on our own labels (last section). That is the only real training route.

Script: `scripts/jev_adapters.py` (stdlib + ffmpeg). Paid send needs `AI_GATEWAY_API_KEY` in the environment, never in chat.

| Jev can't | Adapter | Function |
|---|---|---|
| Watch video / hear audio | Whisper → SRT → timed text windows (with before/after context); ffmpeg 1 fps contact sheet for a human or vision model to label; Jev judges the text | `video` cmd, `srt_windows`, `contact_sheet` |
| See images | A vision model or person writes a literal description into state. Jev 1.14 has a vision tag, but it's untested here | state field |
| Count, add, compare dates, apply cutoffs | Compute in code, put the result in state as a fact ("posted 3 days ago", "today is 2026-10-25") | `facts` |
| Extract a value without inventing it | Regex finds candidate spans, Jev picks one or `none` | `candidates`, `pick_question` |
| Multi-select | One noul per label, combined in code | `per_label_nouls` |
| More than 255 options (26 local) | Walk a hierarchy level by level (beam over choice probabilities) | jev-building-guide |
| Long state (context rot) | Chunk, rank chunks with one noul each, send only the top ones | jev-bulk-offload `rank` |
| Option-order bias | Ask again with options reversed, and act only when both runs agree | `reversed_questions`, `order_consistent` |
| Write text | Keep the LLM for drafting; Jev only screens the drafts | n/a |
| Know our brand rules | Rules go into the instructions and criteria (boundary cases spelled out), facts go into state | spec |
| Be calibrated on our data | Label 20+ real cases, fit thresholds (jev-calibration); confidence is not accuracy | calibrate_local.py |

## MOPC example (testimonial selects)
1. `jev_adapters.py video chris_proxy.mp4 --srt chris.srt --out chris_jev` writes `items.jsonl` (8 s windows) plus `sheet.png`.
2. Per window, in one request:
   - score `completeness` with levels written as situations
   - noul `standalone`
   - noul `names_speed_or_price` (any promise of speed or price is a reject)
   - noul `implies_guaranteed_coverage` (also a reject)
   - choice `persona` over the 7 MOPC personas plus `none`
3. Code rejects windows with a high claim risk, ranks the rest, and keeps faces centred for the 1:1 crop. A human listens to the selects before cutting.

## Fine-tuning a local stand-in (real training)
- Base: Jev-Style-0.8B-Decision-v3 (Apache-2.0, already serves `/v1/systemone`). It scored 0.80 on the Typed Decisions sample, which is in-domain for that model.
- Data: our blind-labelled cases (state, question, gold label), split into tune and hold-out.
- Train on Colab (LoRA). Score the hold-out with jev-evals-benchmarks and jev-calibration. Switch only if it beats the current judge on our hold-out.
- Never train on client data that may not leave the client's tree. Run security-privacy-review first.

## Gotchas
- An adapter result is only as good as its input: Whisper hallucinates, so verify chosen quotes by listening.
- Results not from a real Jev call are labelled `jev_called: false`. Never invent Jev probabilities.
