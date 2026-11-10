"""Group-shot (photo -1) crops set by hand, 10 Nov.
BOX = item area as fractions (x0,y0,x1,y1) of the upright raw photo.
Portrait raws -> 4:5 portrait. Landscape raws -> 1:1 or 4:3, whichever fits.
ROT: extra rotation in degrees after cropping (PIL, positive = anticlockwise)."""
import sys
from PIL import Image, ImageOps, ImageEnhance

BOX = {
 'A3': (0, .02, 1, .88), 'A4': (.1, .3, .99, .78), 'A5': (.26, .07, .78, 1),
 'A6': (.2, .1, .8, .9), 'A7': (.1, .06, .99, .76), 'A8': (0, .1, 1, .68),
 'A9': (0, .08, .9, .88), 'A10': (.2, .06, .85, .76), 'A11': (.04, .28, .98, .76),
 'A12': (.24, .07, .82, .96), 'A13': (.18, .1, .7, 1), 'A14': (.15, .38, 1, .72),
 'A15': (.26, .07, .82, .85), 'A16': (0, .06, 1, .82), 'A17': (0, .12, 1, .74),
 'A18': (.18, .16, .85, .64), 'A19': (.12, .16, .9, .64), 'A20': (.02, .16, 1, .64),
 'A21': (0, .04, .82, .96), 'A22': (.24, .07, .76, .92), 'A23': (0, .24, 1, .6),
 'A24': (.18, .22, 1, .84),
}
ROT = {'A5': -90}
ASP = {'A4': 1.0, 'A5': 1.0}   # per-photo aspect override (w/h) to keep the radiator out
BOX.update({'A10-7': (.1, 0, .85, .72), 'A5': (.24, .07, .70, 1), 'A4': (.1, .3, .99, .74), 'A12': (.24, .07, .80, .96)})

def frame(W, H, bx, aspect, sku_tight=False):  # aspect = w/h
    x0, y0, x1, y1 = bx[0]*W, bx[1]*H, bx[2]*W, bx[3]*H
    cx, cy = (x0+x1)/2, (y0+y1)/2
    m = 1.02 if sku_tight else 1.12
    fw = max((x1-x0)*m, (y1-y0)*m*aspect)
    fw = min(fw, W, H*aspect); fh = fw/aspect
    l = min(max(cx-fw/2, 0), W-fw); t = min(max(cy-fh/2, 0), H-fh)
    return (int(l), int(t), int(l+fw), int(t+fh))

def run(sku, src, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB'); W, H = im.size
    bx = BOX[sku]; rot = ROT.get(sku, 0)
    if sku in ASP:
        asp = ASP[sku]
    elif H >= W:
        asp = 0.8
    elif rot in (90, -90):
        asp = 1.25            # becomes 4:5 portrait after rotating
    else:
        bw, bh = (bx[2]-bx[0])*W, (bx[3]-bx[1])*H
        asp = 1.0 if bw*1.12 <= H else 4/3
    out = im.crop(frame(W, H, bx, asp, sku in ('A4', 'A5', 'A12')))
    if rot: out = out.rotate(rot, expand=True)
    if sku == 'A5':   # trim radiator strip along the bottom
        w, h = out.size; out = out.crop((0, 0, w, int(h*0.89)))
    out = ImageOps.autocontrast(out, cutoff=1)
    out = ImageEnhance.Brightness(out).enhance(1.10)
    out = ImageEnhance.Color(out).enhance(1.05)
    w, h = out.size
    out = out.resize((1200, int(1200*h/w)), Image.LANCZOS)
    out.save(dst, quality=90)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], sys.argv[3])
