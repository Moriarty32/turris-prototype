"""Web delivery only: original pixels, proportional downsampling, no crops or AI edits.
The Petrovsky restoration is a separately generated and explicitly labelled master.
"""
from pathlib import Path
from io import BytesIO
import json,re,hashlib
import requests
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
MEDIA=ROOT/'assets/media';MEDIA.mkdir(exist_ok=True)
CACHE=ROOT/'.qa/originals';CACHE.mkdir(parents=True,exist_ok=True)
assets=json.loads((ROOT/'data/asset-sources.json').read_text(encoding='utf-8'))
items={a['id']:dict(a) for a in assets}
for id,file in [('hero-room','hero-room-v2.png'),('family-room','family-room.png'),('work-stay','work-stay.png')]:
 items[id]={'file':file,'kind':'concept','source':'built-in image_gen','width':1536,'height':1024}
result={};encoded={}
for id,a in items.items():
 if id=='petrovsky':
  source=ROOT/'assets/petrovsky-restored.png';source_url='built-in image_gen, reference: '+a['source'];label='ИИ-реконструкция по фото'
 elif a['kind']=='room':
  source_url=re.sub(r'/resize_cache/iblock/([^/]+)/[^/]+/',r'/iblock/\1/',a['source'])
  source=CACHE/source_url.rsplit('/',1)[1];label=''
  if not source.exists():
   response=requests.get(source_url,timeout=45);response.raise_for_status()
   check=Image.open(BytesIO(response.content));check.load();source.write_bytes(response.content)
 else:source=ROOT/'assets'/a['file'];source_url=a['source'];label=''
 raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 im=ImageOps.exif_transpose(Image.open(source)).convert('RGB');im.load()
 # Never enlarge; 2560 maximum long edge is sufficient for the largest 1068px lightbox.
 maxwidth=min(im.width,round(2560*im.width/max(im.size)))
 widths=sorted(set([w for w in [320,640,960,1280,1600] if w<maxwidth]+[maxwidth]))
 if sha in encoded:variants=encoded[sha]
 else:
  variants=[]
  for w in widths:
   h=round(im.height*w/im.width);name=f'media/{sha[:12]}-{w}.webp';dest=ROOT/'assets'/name
   if not dest.exists():im.resize((w,h),Image.Resampling.LANCZOS).save(dest,format='WEBP',quality=90,method=6)
   variants.append({'file':name,'width':w,'height':h,'bytes':dest.stat().st_size})
  encoded[sha]=variants
 result[id]={'file':variants[-1]['file'],'width':variants[-1]['width'],'height':variants[-1]['height'],'variants':variants,'source':source_url,'source_width':im.width,'source_height':im.height,'source_bytes':len(raw),'source_sha256':sha,'label':label,'kind':a['kind'],'reviewed':'2026-10-29'}
(ROOT/'data/image-delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'assets':len(result),'unique_masters':len(encoded),'web_files':sum(len(x) for x in encoded.values()),'web_bytes':sum(v['bytes'] for x in encoded.values() for v in x)},indent=2))
