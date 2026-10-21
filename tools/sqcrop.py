import sys
from PIL import Image, ImageFilter, ImageEnhance, ImageStat
src,dst,cx,cy,size=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
im=Image.open(src).convert('RGB'); W,H=im.size
l,t=cx-size//2,cy-size//2
bg=im.resize((size,size)).filter(ImageFilter.GaussianBlur(60))
canvas=bg.copy()
box=(max(l,0),max(t,0),min(l+size,W),min(t+size,H))
canvas.paste(im.crop(box),(box[0]-l,box[1]-t))
canvas=ImageEnhance.Brightness(canvas).enhance(1.06)
canvas=ImageEnhance.Contrast(canvas).enhance(1.05)
canvas.resize((1200,1200),Image.LANCZOS).save(dst,quality=90)
