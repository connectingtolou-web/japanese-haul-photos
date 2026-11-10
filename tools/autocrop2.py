"""Haul 2 photo editor v2 (10 Nov): no blurred padding.
Square crop taken fully inside the photo, centred on the product,
then auto-levels + brighten. Output 1200x1200, upright pixels, no EXIF."""
import sys, numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

def item_box(im):
    W, H = im.size; s = 0.2
    sm = im.resize((int(W*s), int(H*s)))
    g = np.asarray(ImageOps.grayscale(sm).filter(ImageFilter.GaussianBlur(1.5)), float)
    hsv = np.asarray(sm.convert('HSV'), float)
    gx = np.abs(np.diff(g, axis=1))[:-1, :]; gy = np.abs(np.diff(g, axis=0))[:, :-1]
    edge = (gx + gy) > 22
    sat = hsv[:-1, :-1, 1] > 120
    m = (edge.astype(float) + 2*sat.astype(float))
    h, w = m.shape; b = int(min(h, w)*0.04)
    m[:b] = 0; m[-b:] = 0; m[:, :b] = 0; m[:, -b:] = 0
    T = m.sum()
    if T < 50:
        return W/2, H/2, W*0.5, H*0.5
    ys = np.cumsum(m.sum(1)); xs = np.cumsum(m.sum(0))
    y0, y1 = np.searchsorted(ys, T*0.02)/s, np.searchsorted(ys, T*0.98)/s
    x0, x1 = np.searchsorted(xs, T*0.02)/s, np.searchsorted(xs, T*0.98)/s
    cy = np.searchsorted(ys, T*0.5)/s; cx = np.searchsorted(xs, T*0.5)/s
    sm2 = sat.astype(float); sm2[:b] = 0; sm2[-b:] = 0; sm2[:, :b] = 0; sm2[:, -b:] = 0
    S = sm2.sum()
    if S > 0.01*sm2.size:   # centre on the colourful product art, not radiator/table edges
        cy = np.searchsorted(np.cumsum(sm2.sum(1)), S*0.5)/s
        cx = np.searchsorted(np.cumsum(sm2.sum(0)), S*0.5)/s
    return cx, cy, x1-x0, y1-y0

def crop(src, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB'); W, H = im.size
    cx, cy, bw, bh = item_box(im)
    # portrait 4:5 frame (Vinted shows portrait thumbnails); never bigger than the photo
    fw = max(bw*1.15, bh*1.15*0.8, min(W, H)*0.85)
    fw = min(fw, W, H*0.8); fh = fw*1.25
    l = int(min(max(cx - fw/2, 0), W - fw))
    t = int(min(max(cy - fh/2, 0), H - fh))
    out = im.crop((l, t, int(l+fw), int(t+fh)))
    out = ImageOps.autocontrast(out, cutoff=1)
    out = ImageEnhance.Brightness(out).enhance(1.10)
    out = ImageEnhance.Color(out).enhance(1.05)
    out = out.resize((1200, 1500), Image.LANCZOS)
    out.save(dst, quality=90)

if __name__ == '__main__':
    crop(sys.argv[1], sys.argv[2])
