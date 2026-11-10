import sys, os, numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
def find_center(im):
    W,H=im.size; s=0.25
    g=np.asarray(ImageOps.grayscale(im).resize((int(W*s),int(H*s))).filter(ImageFilter.GaussianBlur(2)),dtype=float)
    hsv=np.asarray(im.resize((int(W*s),int(H*s))).convert('HSV'),dtype=float)
    gx=np.abs(np.diff(g,axis=1))[:-1,:]; gy=np.abs(np.diff(g,axis=0))[:,:-1]
    e=(gx+gy)>18
    sat=hsv[:-1,:-1,1]>110   # colourful product art/cards
    m=(e|sat).astype(float)
    # ignore outer 3% border
    h,w=m.shape; b=int(min(h,w)*0.03); m[:b,:]=0;m[-b:,:]=0;m[:,:b]=0;m[:,-b:]=0
    ys=np.cumsum(m.sum(1)); xs=np.cumsum(m.sum(0)); T=ys[-1]
    if T<50: return W//2,H//2,min(W,H)
    y0=np.searchsorted(ys,T*0.02)/s; y1=np.searchsorted(ys,T*0.98)/s
    x0=np.searchsorted(xs,T*0.02)/s; x1=np.searchsorted(xs,T*0.98)/s
    cx,cy=(x0+x1)/2,(y0+y1)/2
    size=int(max(y1-y0,x1-x0)*1.18)
    size=max(size,int(min(W,H)*0.8)); size=min(size,int(max(W,H)*0.95))
    # prefer staying inside the frame: if size<=W keep crop within width
    if size<=W: cx=min(max(cx,size/2),W-size/2)
    if size<=H: cy=min(max(cy,size/2),H-size/2)
    return int(cx),int(cy),size
def crop(src,dst):
    im=ImageOps.exif_transpose(Image.open(src)).convert('RGB'); W,H=im.size
    cx,cy,size=find_center(im)
    l,t=cx-size//2,cy-size//2
    bg=im.resize((size,size)).filter(ImageFilter.GaussianBlur(60))
    canvas=bg.copy(); box=(max(l,0),max(t,0),min(l+size,W),min(t+size,H))
    canvas.paste(im.crop(box),(box[0]-l,box[1]-t))
    canvas=ImageEnhance.Brightness(canvas).enhance(1.06)
    canvas=ImageEnhance.Contrast(canvas).enhance(1.05)
    canvas.resize((1200,1200),Image.LANCZOS).save(dst,quality=90)
if __name__=='__main__':
    crop(sys.argv[1],sys.argv[2])
