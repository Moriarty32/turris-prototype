"""Booking selection contract, responsive screens, recovery and real deep links."""
import asyncio,json
from pathlib import Path
from datetime import date,timedelta
from urllib.parse import urlparse,parse_qs
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:4173/turris-prototype'
START=(date.today()+timedelta(days=14)).isoformat();END=(date.today()+timedelta(days=17)).isoformat()
async def dates(page):
 await page.locator('[data-dates]').click()
 await page.locator('#dates-form [name=checkin]').fill(START)
 await page.locator('#dates-form [name=checkout]').fill(END)
 await page.locator('#dates-form button[type=submit]').click()
async def main():
 errors=[];sizes=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch()
  for width in [320,390,640,768,1024,1440]:
   c=await browser.new_context(viewport={'width':width,'height':900},locale='ru-RU',is_mobile=width<700,has_touch=width<700)
   await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Provider contract stub</p>'))
   await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
   page=await c.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
   await page.goto(BASE+'/bronirovanie/',wait_until='networkidle')
   assert await page.locator('.bk-hotel-card').count()==4
   assert not await page.locator('#booking-results').is_visible()
   assert await page.locator('[data-booking] [name=hotel]').input_value()==''
   assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
   # Cards -> form -> selected card; form -> map; marker -> form and card.
   await page.locator('[data-booking-card=petrovsky] [data-pick-label]').click()
   assert await page.locator('[data-booking] [name=hotel]').input_value()=='petrovsky'
   assert await page.locator('[data-booking-card=petrovsky]').evaluate("e=>e.classList.contains('is-selected')")
   await page.locator('[data-booking] [name=hotel]').select_option('tagansky')
   assert await page.locator('#map').get_attribute('data-selected')=='tagansky'
   await page.locator('#map').scroll_into_view_if_needed()
   await page.wait_for_function("document.querySelector('#map').dataset.mapLoaded==='true'")
   assert await page.locator('.map-pin').count()==4
   await page.locator('.map-pin').first.focus();await page.keyboard.press('Enter')
   assert await page.locator('[data-booking] [name=hotel]').input_value()=='tverskaya'
   assert await page.locator('[data-map-select=tverskaya]').get_attribute('aria-expanded')=='true'
   await page.locator('[data-map-select=lubyansky]').click()
   assert await page.locator('[data-booking] [name=hotel]').input_value()=='lubyansky'
   assert await page.locator('[data-map-detail]:visible').count()==1
   await page.locator('[data-booking-expand]').click()
   assert await page.locator('[data-booking-expand]').get_attribute('aria-expanded')=='true'
   await page.keyboard.press('Escape')
   assert await page.locator('[data-booking-expand]').get_attribute('aria-expanded')=='false'
   # Date validation, guest ages, category results and URL retain one trip.
   await page.locator('[data-booking] [type=submit]').click()
   assert await page.locator('#dates-dialog').is_visible()
   await page.keyboard.press('Escape');await dates(page)
   await page.locator('[data-guests]').click()
   await page.locator('[data-count=children][data-change="1"]').click()
   await page.locator('[data-age="0"]').select_option('7')
   await page.locator('[data-save-guests]').click()
   await page.locator('.bk-promo summary').click()
   await page.locator('#booking-promo').fill('DEMO-TEST')
   await page.locator('[data-save-promo]').click()
   assert 'сохранён' in await page.locator('[data-promo-status]').inner_text()
   await page.locator('[data-booking] [type=submit]').click()
   await page.wait_for_selector('.bk-live-frame')
   assert await page.locator('.bk-live-frame').count()==1
   q=parse_qs(urlparse(await page.locator('.bk-live-frame').get_attribute('src')).query)
   assert q['children-age']==['7'] and q['children']==['1'] and q['promo-code-plain']==['DEMO-TEST']
   assert q['date']==[START] and q['nights']==['3']
   fallback=parse_qs(urlparse(await page.locator('[data-official-booking]').get_attribute('href')).query)
   assert all(fallback[key]==q[key] for key in fallback)
   assert 'lubyansky' in page.url and 'checkin='+START in page.url
   # Updated form must hide stale results until search is submitted again.
   await page.locator('[data-booking] [name=hotel]').select_option('tagansky')
   assert not await page.locator('#booking-results').is_visible()
   await page.locator('[data-booking] [type=submit]').click()
   await page.wait_for_selector('.bk-live-frame')
   assert await page.locator('.bk-live-frame').count()==1
   await page.reload(wait_until='networkidle')
   assert await page.locator('#booking-promo').input_value()=='DEMO-TEST'
   assert await page.locator('[data-booking] [name=hotel]').input_value()=='tagansky'
   assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,'results')
   sizes.append(width);await c.close()
  # Deep link to selected room survives date/guest edits, then explicit reset.
  c=await browser.new_context(viewport={'width':1440,'height':1000})
  await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Provider contract stub</p>'))
  await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
  page=await c.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
  await page.goto(BASE+'/bronirovanie/?hotel=tverskaya&room=tverskaya_room_1&checkin='+START+'&checkout='+END,wait_until='networkidle')
  await page.wait_for_selector('.bk-live-frame')
  assert await page.locator('.bk-live-frame').count()==1
  assert 'Вы смотрели' in await page.locator('.bk-live-room').inner_text()
  await dates(page);await page.locator('[data-booking] [type=submit]').click()
  assert await page.locator('.bk-live-frame').count()==1
  assert await page.locator('[data-booking] [name=room]').input_value()=='tverskaya_room_1'
  # A fresh hotel-only link must not inherit a room from an earlier trip.
  await page.goto(BASE+'/bronirovanie/?hotel=lubyansky',wait_until='networkidle')
  await page.wait_for_function("document.querySelectorAll('.bk-live-frame').length===1")
  assert await page.locator('[data-booking] [name=room]').input_value()==''
  await page.goto(BASE+'/bronirovanie/?hotel=tverskaya&room=tverskaya_room_1',wait_until='networkidle')
  await page.wait_for_selector('.bk-live-frame')
  await page.locator('[data-booking-clear-room]').click()
  assert await page.locator('.bk-live-room').count()==0
  await page.wait_for_function("document.querySelectorAll('.bk-live-frame').length===1")
  # Hotel-local booking route replaces the previous property's saved selection.
  await page.goto(BASE+'/hotels/turris-hotel-petrovsky/booking/',wait_until='networkidle')
  assert await page.locator('[data-booking] [name=hotel]').input_value()=='petrovsky'
  await page.wait_for_function("document.querySelectorAll('.bk-live-frame').length===1")
  # Data-provider failure is recoverable and does not invent availability.
  await page.route('**/site-data.json',lambda r:r.abort())
  await page.reload(wait_until='networkidle')
  await page.wait_for_selector('[data-retry-results]')
  await page.unroute('**/site-data.json');await page.locator('[data-retry-results]').click()
  await page.wait_for_selector('.bk-live-frame')
  await c.close()
  c=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  page=await c.new_page();await page.goto(BASE+'/bronirovanie/')
  assert await page.locator('.bk-card-actions a[href]').count()==8
  assert await page.locator('.bk-map-detail').count()==4
  await browser.close()
 assert not errors,errors
 report={'status':'PASS','responsive_widths':sizes,'checks':['card/form/map synchronization','keyboard marker selection','expanded map Escape','dates and child age','promo stored without discount claim','inline results and stale-state hiding','selected room retained and reset','hotel-local booking preset','provider failure and retry','no-JS links'],'js_errors':errors}
 (ROOT/'docs/verification-booking-reference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
