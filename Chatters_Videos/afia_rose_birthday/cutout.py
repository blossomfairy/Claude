"""Crop each photo to head-and-shoulders and remove the background locally (rembg)."""
import sys, time
from PIL import Image
from rembg import remove, new_session
U = "/root/.claude/uploads/254c4376-c66e-58d3-a800-507814c958ac/"
JOBS = {  # name: (file, crop box as fractions x0, y0, x1, y1)
    "rose1": ("e7eb557f-image.jpg", (0.18, 0.15, 0.78, 0.62)),
    "rose2": ("581f33f2-image.jpg", (0.30, 0.03, 0.68, 0.56)),
    "afia1": ("0f213448-image.jpg", (0.08, 0.05, 0.92, 0.62)),
    "afia2": ("75feb142-image.jpg", (0.06, 0.00, 0.94, 0.60)),
    "afia3": ("48d5f0c0-image.jpg", (0.00, 0.05, 1.00, 0.70)),
}
sess = new_session(sys.argv[1] if len(sys.argv) > 1 else "birefnet-portrait")
import os
for name, (f, (a, b, c, d)) in JOBS.items():
    if os.path.exists(sys.path[0] + f"/cut/{name}.png"): continue
    im = Image.open(U + f).convert("RGB"); w, h = im.size
    crop = im.crop((int(a * w), int(b * h), int(c * w), int(d * h)))
    t = time.time(); out = remove(crop, session=sess, post_process_mask=True)
    out.save(sys.path[0] + f"/cut/{name}.png"); print(name, crop.size, f"{time.time() - t:.1f}s")
