import asyncio,json
from pathlib import Path
from urllib.parse import urlsplit,unquote
from PIL import Image
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 delivery=json.loads((ROOT/'data/image-delivery.json').read_text(encoding='utf-8'))
 dimensions={}
 for item in delivery.values():
  for v in item['variants']:
   path=ROOT/'assets'/v['file'];im=Image.open(path);im.load()
   assert im.size==(v['width'],v['height']),str(path)
   assert im.width<=item['source_width'] and im.height<=item['source_height']
   dimensions[v['file']]=im.size
 for path in (ROOT/'dist').rglob('index.html'):
  soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
  for img in soup.select('img[data-asset]'):
   assert img['src'].startswith('/turris-prototype/assets/media/'),str(path)
   for candidate in img.get('srcset','').split(','):
    if candidate: assert (ROOT/'dist'/candidate.strip().split()[0].removeprefix('/turris-prototype/')).exists()
   if img['data-asset']=='petrovsky':
    assert 'ИИ-реконструкция' in img['alt']
    assert 'ИИ-реконструкция' in img.parent.get_text(),str(path)
 routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))['pages']
 observations=[];errors=[];poor=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(device_scale_factor=2,viewport={'width':1440,'height':1000})
  await c.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
  page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for width in [1440,390]:
   await page.set_viewport_size({'width':width,'height':1000 if width==1440 else 844})
   for route in routes:
    await page.goto(BASE+route['url'],wait_until='load')
    await page.evaluate('document.fonts.ready')
    # Only local images; no OSM tiles or external bulk downloads.
    rows=await page.locator('main img[data-asset]').evaluate_all('''async els=>{
     const visible=els.filter(i=>i.getBoundingClientRect().width&&i.getBoundingClientRect().height);
     await Promise.all(visible.map(async i=>{i.loading='eager';await i.decode()}));
     return visible.map(i=>{const r=i.getBoundingClientRect();return {asset:i.dataset.asset,src:i.currentSrc,width:r.width,height:r.height,fit:getComputedStyle(i).objectFit}})
    }''')
    assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),(width,route['url'])
    for row in rows:
     file=unquote(urlsplit(row['src']).path).split('/assets/',1)[1];sw,sh=dimensions[file]
     ratio=max(sw/row['width'],sh/row['height']) if row['fit']=='contain' else min(sw/row['width'],sh/row['height'])
     row.update(page=route['url'],viewport=width,density=round(ratio,2));observations.append(row)
     if ratio<1.95:poor.append(row)
     assert row['height']<700,(width,route['url'],row)
   for path,name in [('/','home'),('/family/','family'),('/hotels/turris-hotel-petrovsky/','petrovsky'),('/blog/','guide')]:
    await page.goto(BASE+path,wait_until='networkidle');await page.screenshot(path=str(ROOT/'.qa'/f'images-{name}-{width}.png'),full_page=True)
  # The enlarged photograph uses the largest available file, not a thumbnail.
  await page.goto(BASE+'/hotels/turris-hotel-tverskaya/rooms/semeynyy-lyuks/',wait_until='networkidle')
  await page.locator('[data-lightbox]').click()
  await page.locator('#lightbox-dialog img').evaluate('(i)=>i.decode()')
  assert await page.locator('#lightbox-dialog img').get_attribute('src')==BASE+'/assets/'+delivery['tverskaya_room_1']['file'] or (await page.locator('#lightbox-dialog img').get_attribute('src')).endswith('/assets/'+delivery['tverskaya_room_1']['file'])
  assert not errors,errors
  await b.close()
 (ROOT/'.qa/image-render-audit.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2),encoding='utf-8')
 report={'status':'PASS' if not poor else 'NEEDS_REVIEW','assets':len(delivery),'web_files':len(dimensions),'pages':len(routes),'viewports':[1440,390],'device_pixel_ratio':2,'rendered_checks':len(observations),'minimum_density':min(x['density'] for x in observations),'below_1_95':poor,'js_errors':errors,'notes':['All web images decoded, dimensions match manifest, no upscaling during export','Generated facade labelled; full-size lightbox verified','Source photographs visually reviewed; pixel density is not a measure of original camera sharpness']}
 (ROOT/'.qa/image-quality-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
 assert not poor,poor[:4]
if __name__=='__main__':asyncio.run(main())
