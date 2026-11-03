"""Export each homepage hero directly from its native master, without upscaling.

Run explicitly after changing docs/home-hero-quality-v3.json, before build.py.
The build itself never needs network access or image-generation credentials.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json
import requests
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'docs/home-hero-quality-v3.json'

def main():
 plan=json.loads(PLAN.read_text(encoding='utf-8'))
 manifest_path=ROOT/'data/image-delivery.json'
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 cache=ROOT/'.qa/originals';cache.mkdir(parents=True,exist_ok=True)
 output=ROOT/'assets/hero';output.mkdir(parents=True,exist_ok=True)
 for row in plan['images']:
  if row['source'].startswith('https://'):
   source=cache/row['source'].rsplit('/',1)[1]
   if not source.exists():
    response=requests.get(row['source'],timeout=45);response.raise_for_status()
    Image.open(BytesIO(response.content)).verify()
    source.write_bytes(response.content)
  else:
   source=ROOT/row['source']
  raw=source.read_bytes()
  im=ImageOps.exif_transpose(Image.open(source)).convert('RGB');im.load()
  assert list(im.size)==row['native_dimensions'],(row['hotel'],im.size)
  widths=sorted(set([w for w in [960,1600,1920,2560,3840,5120] if w<im.width]+[im.width]))
  variants=[]
  for width in widths:
   height=round(im.height*width/im.width)
   dest=output/f'{row["hotel"]}-native-v3-{width}.webp'
   frame=im if width==im.width else im.resize((width,height),Image.Resampling.LANCZOS)
   frame.save(dest,'WEBP',quality=96,method=6)
   variants.append(dict(file=dest.relative_to(ROOT/'assets').as_posix(),width=width,height=height,bytes=dest.stat().st_size))
  asset='hero_'+row['hotel']+'_v3'
  manifest[asset]=dict(file=variants[-1]['file'],width=im.width,height=im.height,variants=variants,source=row['source'],source_width=im.width,source_height=im.height,source_sha256=hashlib.sha256(raw).hexdigest(),label=row['label'],kind=row['kind'],reviewed=plan['date'])
  row['asset_id']=asset;row['variants']=variants
  print(row['hotel'],im.size,variants[-1]['bytes'],'bytes; no upscaling')
 manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 PLAN.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
