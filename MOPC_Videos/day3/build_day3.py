#!/usr/bin/env python3
"""Build a Day 3 cut from a cut-list CSV: grade per camera, reframe without upscaling,
re-encode every segment, join, lay the music bed under the dialogue, loudnorm to -14 LUFS.

Supers, lower thirds and the end-card art come from mopc-video-editor (video.py overlay);
this script only produces the graded, timed picture and the mixed sound.
"""
import argparse, csv, json, os, subprocess, sys, tempfile

ROTATED = {"NBM_FX9_1536", "NBM_FX9_1537", "NBM_FX9_1538"}   # mounted on their side: native vertical


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed: {' '.join(cmd)}\n{r.stderr[-1500:]}")
    return r


def probe(path):
    j = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "json", path]).stdout)
    s = j["streams"][0]
    return s["width"], s["height"]


def grade_filter(name, a):
    lut = a.fx9_cube if "FX9" in name else a.r5c_lut if "CANON" in name else a.dlog_lut if name.startswith("DJI") else None
    if lut is None:
        sys.exit(f"no grade for {name}: pass the LUT for this camera")
    return f"format=gbrpf32le,lut3d=file='{lut}':interp=tetrahedral,format=yuv420p"


def reframe(name, w, h, tw, th, cx, a):
    """Crop the target aspect at source scale, placed at cx (0-1); refuse upscaling."""
    rot = ""
    if os.path.splitext(name)[0] in ROTATED:
        rot = f"transpose={a.rotate},"
        w, h = h, w
    if w / h > tw / th:
        cw, ch = round(h * tw / th) // 2 * 2, h
    else:
        cw, ch = w, round(w * th / tw) // 2 * 2
    if cw < tw or ch < th:
        sys.exit(f"REFUSED {name}: crop {cw}x{ch} would need upscaling to {tw}x{th}")
    x = max(0, min(w - cw, round(cx * w - cw / 2)))
    return f"{rot}crop={cw}:{ch}:{x}:{(h - ch) // 2},scale={tw}:{th}:flags=lanczos"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cuts"); p.add_argument("--src", required=True); p.add_argument("--out", required=True)
    p.add_argument("--size", default="1080x1920"); p.add_argument("--fps", default="30000/1001")
    p.add_argument("--fx9-cube"); p.add_argument("--r5c-lut"); p.add_argument("--dlog-lut")
    p.add_argument("--rotate", type=int, default=2, help="transpose value for rotated clips (1=cw, 2=ccw): check frame 1")
    p.add_argument("--endcard"); p.add_argument("--music")
    a = p.parse_args()
    tw, th = map(int, a.size.split("x"))
    tmp = tempfile.mkdtemp(prefix="day3_")
    segs, dialogue = [], []

    rows = list(csv.DictReader(open(a.cuts, encoding="utf-8")))
    t = 0.0
    for i, r in enumerate(rows):
        dur = float(r["out"]) - float(r["in"])
        seg = os.path.join(tmp, f"{i:02d}.mp4")
        if r["clip"] == "ENDCARD":
            if not a.endcard:
                sys.exit("cut list has an ENDCARD row: pass --endcard")
            run(["ffmpeg", "-v", "error", "-y", "-i", a.endcard, "-t", f"{dur}", "-vf", f"scale={tw}:{th},fps={a.fps}",
                 "-an", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", seg])
        else:
            src = os.path.join(a.src, r["clip"])
            w, h = probe(src)
            vf = ",".join([grade_filter(r["clip"], a), reframe(r["clip"], w, h, tw, th, float(r.get("cx") or 0.5), a),
                           f"fps={a.fps}"])
            run(["ffmpeg", "-v", "error", "-y", "-ss", r["in"], "-i", src, "-t", f"{dur}", "-vf", vf, "-an",
                 "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", seg])
            if "signoff" in r["label"]:   # dialogue keeps the clean mic channel (stream 1 per audio_verify)
                wav = os.path.join(tmp, f"{i:02d}.wav")
                run(["ffmpeg", "-v", "error", "-y", "-ss", r["in"], "-i", src, "-t", f"{dur}", "-map", "0:a:1",
                     "-ac", "2", "-ar", "48000", wav])
                dialogue.append((t, wav))
        segs.append(seg)
        t += dur

    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    pic = os.path.join(tmp, "picture.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", pic])

    ins, mix = ["-i", pic], []
    if a.music:
        ins += ["-i", a.music]
        mix.append(f"[1:a]atrim=0:{t},volume={'0.25' if dialogue else '1.0'}[m]")
    for k, (start, wav) in enumerate(dialogue):
        ins += ["-i", wav]
        n = len(ins) // 2 - 1
        mix.append(f"[{n}:a]adelay={int(start * 1000)}|{int(start * 1000)}[d{k}]")
    labels = (["[m]"] if a.music else []) + [f"[d{k}]" for k in range(len(dialogue))]
    if not labels:
        sys.exit("no sound: pass --music (silent sources are a rejected delivery)")
    mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{t}[pre]")

    # two-pass loudnorm to -14 LUFS / -1 dBTP
    m = run(["ffmpeg", "-v", "info", "-y", *ins, "-filter_complex", ";".join(mix) + ";[pre]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[a]",
             "-map", "[a]", "-f", "null", "-"]).stderr
    st = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
          f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(mix) + f";[pre]{ln},aresample=48000[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out])
    print(json.dumps({"out": a.out, "dur_s": round(t, 2), "segments": len(segs), "dialogue": len(dialogue)}))


if __name__ == "__main__":
    main()
