"""Reference offer pages: responsive layout, actual trip state, category scope and map."""
import asyncio,json,sys
from pathlib import Path
from datetime import date,timedelta
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:4173/turris-prototype'
sys.path.insert(0,str(ROOT/'data'))
from offer_details import TEMPLATES
PAGES=[p for p in json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))['pages'] if p['template'] in TEMPLATES]
START=(date.today()+timedelta(days=20)).isoformat()
async def dates(page,nights=3):
 await page.locator('[data-offer-form] [data-dates]').click()
 await page.locator('#dates-form [name=checkin]').fill(START)
 await page.locator('#dates-form [name=checkout]').fill((date.fromisoformat(START)+timedelta(days=nights)).isoformat())
 await page.locator('#dates-form button[type=submit]').click()
async def main():
 errors=[];checks=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch()
  for width in [320,390,768,1440]:
   c=await browser.new_context(viewport={'width':width,'height':900},locale='ru-RU',is_mobile=width<700,has_touch=width<700)
   await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
   page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   for item in PAGES:
    await page.goto(BASE+item['url'],wait_until='networkidle')
    assert await page.locator('h1').count()==1,item['id']
    if width==390 and item['id']=='family':
     await page.locator('.menu-button').click()
     assert await page.locator('#main-nav').is_visible()
     await page.locator('#main-nav a[href="#conditions"]').click()
     assert not await page.locator('#main-nav').is_visible()
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(item['id'],width)
    bad=await page.locator('img[src]').evaluate_all('els=>els.filter(e=>e.complete&&!e.naturalWidth).map(e=>e.src)')
    assert not bad,(item['id'],bad)
    assert await page.locator('.of-hero-photo').evaluate('e=>e.getBoundingClientRect().height')<=360
    for anchor in await page.locator('.of-header a[href^="#"],.of-tabs a').evaluate_all('els=>els.map(e=>e.hash)'):
     assert await page.locator(anchor).count(),(item['id'],anchor)
    checks.append([item['id'],width])
   await c.close()
  c=await browser.new_context(viewport={'width':1440,'height':900},locale='ru-RU')
  await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
  page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/family/',wait_until='networkidle')
  assert await page.locator('.of-room').count()==4
  await page.locator('[data-family-count=children][data-delta="1"]').click()
  await page.locator('[data-family-count=children][data-delta="1"]').click()
  assert await page.locator('[data-family-ages] select:invalid').count()==2
  await page.locator('[data-family-ages] select').nth(0).select_option('4')
  await page.locator('[data-family-ages] select').nth(1).select_option('8')
  assert await page.locator('[data-offer-form] [name=children]').input_value()=='[4,8]'
  await dates(page)
  await page.locator('[data-offer-form] [type=submit]').click()
  await page.wait_for_url('**/bronirovanie/**')
  await page.wait_for_selector('#booking-results .room-card')
  assert await page.locator('#booking-results .room-card').count()==4
  assert 'scenario=family' in page.url and '4%2C8' in page.url
  await page.goto(BASE+'/family/',wait_until='networkidle')
  await page.locator('#map').scroll_into_view_if_needed()
  await page.wait_for_function("document.querySelector('#map').dataset.mapLoaded==='true'")
  assert await page.locator('.map-pin').count()==2
  await page.locator('[data-offer-map-expand]').click()
  assert await page.locator('.of-map-expanded .map-stage').get_attribute('aria-modal')=='true'
  await page.keyboard.press('Escape')
  assert await page.locator('.of-map-expanded').count()==0
  await page.locator('[data-offer-map-hotel=tverskaya]').click()
  assert await page.locator('.of-room:visible').count()==1
  await page.locator('[data-offer-clear]').click()
  assert await page.locator('.of-room:visible').count()==4
  await page.locator('[data-offer-room=lubyansky_room_3]').click()
  await page.wait_for_url('**/bronirovanie/**')
  await page.wait_for_selector('#booking-results .room-card')
  assert await page.locator('#booking-results .room-card').count()==1
  assert 'room=lubyansky_room_3' in page.url and '4%2C8' in page.url
  longstay=next(p for p in PAGES if p['id']=='longstay')
  await page.goto(BASE+longstay['url'],wait_until='networkidle')
  assert await page.locator('[data-offer-form] [name=hotel] option[value]:not([value=""])').count()==1
  await dates(page,3)
  await page.locator('[data-offer-form] [type=submit]').click()
  assert '21' in await page.locator('[data-offer-form] .form-error').inner_text()
  assert longstay['url'] in page.url
  await dates(page,21)
  await page.locator('[data-offer-form] [type=submit]').click()
  await page.wait_for_url('**/bronirovanie/**')
  assert 'hotel=petrovsky' in page.url
  await page.goto(BASE+next(p['url'] for p in PAGES if p['id']=='offer_3'),wait_until='networkidle')
  await page.locator('[data-offer-form] [name=hotel]').select_option('')
  await page.locator('[data-offer-form] [type=submit]').click()
  await page.wait_for_url('**/bronirovanie/**')
  await page.wait_for_selector('#booking-results .room-card')
  assert 'scenario=offer_four' in page.url
  assert await page.locator('#booking-results .room-card').count()==11
  await page.goto(BASE+'/groups/',wait_until='networkidle')
  await page.locator('[data-offer-map-hotel=lubyansky]').click()
  assert 'Лубянский' in await page.locator('[name=wishes]').input_value()
  await page.goto(BASE+'/offers/',wait_until='networkidle')
  await page.locator('[data-offer-filter]').select_option('petrovsky')
  assert await page.locator('[data-promo-hotel]:visible').count()==5
  await page.goto(BASE+next(p['url'] for p in PAGES if p['id']=='offer_8'),wait_until='networkidle')
  assert 'Действующая скидка не подтверждена' in await page.locator('#conditions').inner_text()
  nojs=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  n=await nojs.new_page();await n.goto(BASE+'/family/',wait_until='networkidle')
  assert await n.locator('.of-room a[href]').count()==12
  assert await n.locator('.of-map-cards a[target="_blank"]').count()==2
  await nojs.close()
  reduced=await browser.new_context(reduced_motion='reduce')
  r=await reduced.new_page();await r.goto(BASE+'/family/',wait_until='networkidle')
  assert await r.locator('.of-room-photo img').first.evaluate('e=>getComputedStyle(e).transitionDuration')=='0s'
  await reduced.close()
  assert not errors,errors
  await c.close();await browser.close()
 report={'status':'passed','pages':len(PAGES),'responsive_checks':len(checks),'widths':[320,390,768,1440],'flows':['family ages required and preserved','family results limited to four categories','selected category retained','two-property interactive map and fullscreen','hotel filter and reset','longstay minimum 21 nights','group location request','offer catalog hotel filter','unverified promotion status'],'javascript_errors':errors}
 (ROOT/'.qa/offers-reference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())

