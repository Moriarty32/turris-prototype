"""Article map, booking handoff and checklist acceptance checks."""
import asyncio,json
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4173/turris-prototype'

async def main():
 errors=[];checks=[]
 pages=[p for p in json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))['pages'] if p['template']=='article']
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  context=await browser.new_context(viewport={'width':1440,'height':1000},locale='ru-RU')
  await context.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
  page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for item in pages:
   await page.goto(BASE+item['url'],wait_until='networkidle')
   root=page.locator('.ar-map')
   config=json.loads(await root.locator('[data-map-config]').text_content())
   await root.scroll_into_view_if_needed()
   await expect(root.locator('.leaflet-marker-icon')).to_have_count(len(config))
   assert await root.locator('.home-map-item').count()==len(config)
   assert await page.locator('.home-header .nav-direct.current').inner_text()=='Гид по Москве'
   assert await page.locator('.ar-related-card').count()==3
   assert await page.locator('#article-sources a').count()>=len(config)
   for hotel in config:
    button=root.locator('[data-map-select='+hotel+']')
    await button.click()
    await expect(button).to_have_attribute('aria-expanded','true')
    await expect(root.locator('[data-map-detail]:visible')).to_have_count(1)
    await expect(page.locator('.ar-booking [name=hotel]')).to_have_value(hotel)
   checks.append({'article':item['url'],'map_hotels':list(config),'map_and_booking':'passed'})
  await page.goto(BASE+'/blog/choose-area/',wait_until='networkidle')
  await page.locator('.ar-booking [name=hotel]').select_option('tagansky')
  await expect(page.locator('[data-map-select=tagansky]')).to_have_attribute('aria-pressed','true')
  for width in [390,1440,320,768,390]:
   await page.set_viewport_size({'width':width,'height':900})
   await page.locator('.ar-map').scroll_into_view_if_needed()
   await expect(page.locator('.leaflet-container')).to_have_count(1)
   assert await page.locator('[data-map-select]').count()==4
   assert await page.locator('[data-map-detail]').count()==4
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   await page.locator('[data-map-select=lubyansky]').click()
   await expect(page.locator('[data-map-detail=lubyansky]')).to_be_visible()
  await page.locator('.menu-button').click()
  await expect(page.locator('.nav-direct.current')).to_be_visible()
  await page.keyboard.press('Escape')
  await expect(page.locator('.nav')).not_to_be_visible()
  await page.locator('.ar-booking [data-dates]').click()
  await page.locator('#dates-form [name=checkin]').fill('2026-12-10')
  await page.locator('#dates-form [name=checkout]').fill('2026-12-13')
  await page.locator('#dates-form [type=submit]').click()
  await page.locator('.ar-booking [data-guests]').click()
  await page.locator('[data-count=children][data-change="1"]').click()
  await page.locator('[data-age="0"]').select_option('7')
  await page.locator('[data-save-guests]').click()
  await page.locator('.ar-booking [type=submit]').click()
  await page.wait_for_url('**/bronirovanie/**')
  await expect(page.locator('#booking-results .room-card')).to_have_count(7)
  query=parse_qs(urlsplit(page.url).query)
  assert query['hotel']==['lubyansky'] and query['checkin']==['2026-12-10'] and query['checkout']==['2026-12-13'],query
  assert await page.locator('[data-booking] [name=children]').first.input_value()=='[7]'
  checks.append('Responsive reparenting keeps one map and four controls; map/form selection, mobile navigation, dates and child age reach booking')
  await page.goto(BASE+'/blog/choose-area/',wait_until='networkidle')
  await page.locator('[data-guide-check="1"]').check()
  await expect(page.locator('[data-check-progress]')).to_have_js_property('value',1)
  await page.reload(wait_until='networkidle')
  await expect(page.locator('[data-map-select=lubyansky]')).to_have_attribute('aria-pressed','true')
  await expect(page.locator('[data-check-progress]')).to_have_js_property('value',1)
  await page.goto(BASE+'/blog/twin-double/',wait_until='networkidle')
  await expect(page.locator('[data-check-progress]')).to_have_js_property('value',0)
  await page.goto(BASE+'/blog/choose-area/',wait_until='networkidle')
  await page.locator('[data-check-reset]').click()
  await expect(page.locator('[data-check-progress]')).to_have_js_property('value',0)
  checks.append('Native progress, per-article session persistence and reset')
  for width in [1440,390]:
   await page.set_viewport_size({'width':width,'height':1000 if width==1440 else 844})
   await page.goto(BASE+'/blog/choose-area/',wait_until='networkidle')
   await page.locator('.ar-map').scroll_into_view_if_needed()
   await page.locator('img').evaluate_all("els=>els.forEach(e=>e.loading='eager')")
   await page.wait_for_function("[...document.querySelectorAll('img[data-asset]')].every(i=>i.complete && i.naturalWidth>0)")
   await page.locator('img[data-asset]').evaluate_all('(els)=>Promise.all(els.map(i=>i.decode()))')
   await page.evaluate('document.fonts.ready')
   await page.evaluate("scrollTo({top:0,behavior:'instant'})")
   await page.screenshot(path=str(ROOT/'.qa'/f'article-reference-{width}.png'),full_page=True)
  plain=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  raw=await plain.new_page();await raw.goto(BASE+'/blog/choose-area/')
  assert await raw.locator('[data-map-detail]:visible').count()==4
  assert await raw.locator('.ar-related-card a').count()==9
  await plain.close();await context.close();await browser.close()
 assert not errors,errors
 report={'status':'PASS','articles':len(pages),'checks':checks,'js_errors':errors}
 (ROOT/'.qa/article-reference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
