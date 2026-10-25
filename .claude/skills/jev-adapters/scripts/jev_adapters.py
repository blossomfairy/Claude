#!/usr/bin/env python3
"""Adapters that turn what Jev can't judge into typed questions it can.

Jev reads text state and returns probabilities. It cannot watch video, hear
audio, count, do maths or dates, invent extracted values, multi-select, or
handle huge option lists or long state. Each adapter moves that part into
code and hands Jev only a narrow judgement.

Usage:
  jev_adapters.py video  CLIP.mp4 --srt CLIP.srt --out DIR [--window 8]
  jev_adapters.py payload SPEC.json [--reverse]          # TypeSafe wire format
  jev_adapters.py send    SPEC.json [--reverse]          # needs AI_GATEWAY_API_KEY
"""
import argparse, json, os, re, subprocess, sys, urllib.request
from datetime import date

GATEWAY = "https://ai-gateway.vercel.sh/typesafe/v1/systemone"
MODEL = "typesafe-ai/jev"


# ---- video / audio: Jev never sees media, so give it timed text ----------
def srt_windows(srt_text, window_s=8.0):
    """Merge SRT cues into ~window_s text windows with absolute times."""
    cues = []
    for block in re.split(r"\n\s*\n", srt_text.strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*)",
                      block, re.S)
        if not m:
            continue
        g = [int(x) for x in m.groups()[:8]]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        cues.append((start, end, " ".join(m.group(9).split())))
    out, cur = [], None
    for s, e, t in cues:
        if cur and e - cur["start"] <= window_s:
            cur["end"], cur["text"] = e, cur["text"] + " " + t
        else:
            cur = {"start": s, "end": e, "text": t}
            out.append(cur)
    for i, w in enumerate(out):
        w["id"] = f"w{i:03d}"
        w["before"] = out[i - 1]["text"] if i else ""
        w["after"] = out[i + 1]["text"] if i + 1 < len(out) else ""
    return out


def contact_sheet(video, out_png, fps=1, cols=6, rows=10):
    """1 frame/s grid for a human or vision model to label; Jev gets the labels."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
                    f"fps={fps},scale=320:-1,tile={cols}x{rows}", "-frames:v", "1", out_png],
                   check=True)


def probe(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
                        "-of", "json", video], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    vs = next(s for s in j["streams"] if "width" in s)
    return {"duration_s": round(float(j["format"]["duration"]), 2), "width": vs["width"], "height": vs["height"]}


# ---- maths, counts, dates: compute, then state the result as a fact --------
def facts(today=None, **computed):
    """Pre-computed facts Jev should trust instead of deriving."""
    f = {"today": (today or date.today()).isoformat()}
    f.update(computed)
    return f


# ---- extraction: code finds candidates, Jev only picks one -----------------
def candidates(text, pattern, limit=25):
    seen = []
    for m in re.finditer(pattern, text):
        if m.group(0) not in seen:
            seen.append(m.group(0))
    return seen[:limit]


def pick_question(qid, instructions, spans):
    crit = {f"c{i}": s for i, s in enumerate(spans)}
    crit["none"] = "none of these spans is correct"
    return qid, {"type": "choice", "instructions": instructions, "criteria": crit}


# ---- multi-select: one noul per label, never one choice ---------------------
def per_label_nouls(prefix, template, labels):
    return {f"{prefix}_{k}": {"type": "noul", "instructions": template.format(label=v)}
            for k, v in labels.items()}


# ---- option-order bias: same question, options reversed ---------------------
def reversed_questions(questions):
    out = {}
    for qid, q in questions.items():
        q = dict(q)
        c = q.get("criteria")
        if q["type"] == "choice" and isinstance(c, dict):
            q["criteria"] = dict(reversed(list(c.items())))
        out[qid] = q
    return out


def order_consistent(fwd, rev):
    """Act on a choice only when both orderings agree on the winner."""
    return {qid: fwd[qid].get("choice") == rev[qid].get("choice")
            for qid in fwd if "choice" in fwd[qid]}


# ---- wire format + optional paid send --------------------------------------
def payload(spec, reverse=False):
    qs = spec["questions"]
    return {"model": spec.get("model", MODEL), "state": spec["state"],
            "questions": reversed_questions(qs) if reverse else qs}


def send(body):
    key = os.environ.get("AI_GATEWAY_API_KEY")
    if not key:
        sys.exit("AI_GATEWAY_API_KEY not set: add it in the environment settings, never in chat.")
    req = urllib.request.Request(os.environ.get("TYPESAFE_URL", GATEWAY), json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("video"); v.add_argument("video"); v.add_argument("--srt"); v.add_argument("--out", required=True)
    v.add_argument("--window", type=float, default=8.0)
    for name in ("payload", "send"):
        p = sub.add_parser(name); p.add_argument("spec"); p.add_argument("--reverse", action="store_true")
    a = ap.parse_args()

    if a.cmd == "video":
        os.makedirs(a.out, exist_ok=True)
        meta = probe(a.video)
        contact_sheet(a.video, os.path.join(a.out, "sheet.png"))
        wins = srt_windows(open(a.srt, encoding="utf-8").read(), a.window) if a.srt else []
        with open(os.path.join(a.out, "items.jsonl"), "w", encoding="utf-8") as f:
            for w in wins:
                f.write(json.dumps({"id": w["id"], "state": {**w, "clip": meta}}) + "\n")
        print(json.dumps({"clip": meta, "windows": len(wins), "sheet": os.path.join(a.out, "sheet.png")}))
    else:
        body = payload(json.load(open(a.spec, encoding="utf-8")), a.reverse)
        print(json.dumps(send(body) if a.cmd == "send" else body, indent=2))


if __name__ == "__main__":
    main()
