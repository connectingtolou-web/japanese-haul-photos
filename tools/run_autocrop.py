import os,sys; sys.path.insert(0,os.path.dirname(__file__)); from autocrop import crop
R=sys.argv[1]
for sku in sorted(os.listdir(f'{R}/Haul2/raw'),key=lambda s:int(s[1:])):
    if sku in('A1','A2'): continue
    os.makedirs(f'{R}/Haul2/{sku}',exist_ok=True)
    for f in sorted(os.listdir(f'{R}/Haul2/raw/{sku}')):
        crop(f'{R}/Haul2/raw/{sku}/{f}',f'{R}/Haul2/{sku}/{f}')
    print(sku,end=' ',flush=True)
