"""Only the chosen hotel's room categories; no mixed result list, including delayed requests."""
import asyncio,json,os
from pathlib import Path
from datetime import date,timedelta
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1];BASE=os.environ.get('QA_BASE','http://127.0.0.1:4173/turris-prototype')
START=(date.today()+timedelta(days=20)).isoformat();END=(date.today()+timedelta(days=23)).isoformat();QUERY='?checkin='+START+'&checkout='+END
async def main():
 errors=[];checks=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  for width in [390,1440]:
   c=await browser.new_context(viewport={'width':width,'height':900})
   await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Provider contract stub</p>'))
   await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
   page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(BASE+'/bronirovanie/'+QUERY,wait_until='networkidle')
   await expect(page.locator('[data-booking-choose-hotel]')).to_be_visible()
   assert await page.locator('.bk-live-frame').count()==0
   await page.locator('[data-booking] [type=submit]').click()
   assert 'Выберите отель' in await page.locator('[data-booking] .form-error').inner_text()
   for hotel,count in [('tverskaya',6),('lubyansky',7),('petrovsky',4),('tagansky',4)]:
    await page.locator('[data-booking] [name=hotel]').select_option(hotel)
    assert await page.locator('.bk-live-frame').count()==0
    await expect(page.locator('[data-booking-card]:visible')).to_have_count(1)
    await expect(page.locator('[data-booking-card='+hotel+']')).to_be_visible()
    await page.locator('[data-booking] [type=submit]').click()
    await expect(page.locator('.bk-live-frame')).to_have_count(1)
    assert await page.locator('[data-live-hotel]').get_attribute('data-live-hotel')==hotel
    assert 'hotel='+hotel in await page.locator('.bk-live-frame').get_attribute('src')
    assert hotel in page.url
   await page.locator('[data-booking-change-hotel]').click()
   await expect(page.locator('[data-booking-card]:visible')).to_have_count(4)
   await page.locator('[data-booking-card=lubyansky] [data-pick-label]').click()
   await expect(page.locator('[data-booking-card]:visible')).to_have_count(1)
   assert await page.locator('.bk-live-frame').count()==0
   await page.reload(wait_until='networkidle')
   await expect(page.locator('[data-live-hotel=lubyansky]')).to_have_count(1)
   await page.locator('[data-map-select=petrovsky]').click()
   assert await page.locator('.bk-live-frame').count()==0
   await page.locator('[data-booking] [type=submit]').click()
   await expect(page.locator('[data-live-hotel=petrovsky]')).to_have_count(1)
   await page.locator('[data-booking] [name=hotel]').select_option('')
   assert await page.locator('.bk-live-frame').count()==0
   await page.reload(wait_until='networkidle')
   await expect(page.locator('[data-booking-choose-hotel]')).to_be_visible()
   await page.goto(BASE+'/bronirovanie/'+QUERY+'&hotel=lubyansky&scenario=offer_four',wait_until='networkidle')
   await page.locator('[data-booking] [name=hotel]').select_option('petrovsky')
   assert 'scenario=' not in page.url
   await page.reload(wait_until='networkidle')
   await expect(page.locator('[data-live-hotel=petrovsky]')).to_have_count(1)
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   checks.append({'width':width,'four_hotels_scoped':True,'change_hotel_and_reload':True,'map_selection':True,'unselected_no_categories':True})
   await c.close()
  # In-flight old search may not repaint the selected hotel's screen.
  c=await browser.new_context();await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Provider contract stub</p>'));await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort());page=await c.new_page()
  gate=asyncio.Event();started=asyncio.Event()
  async def delay(route):
   started.set();await gate.wait();await route.fulfill(content_type='application/json',body=(ROOT/'dist/site-data.json').read_text(encoding='utf-8'))
  await page.route('**/site-data.json',delay)
  await page.goto(BASE+'/bronirovanie/'+QUERY+'&hotel=tverskaya',wait_until='domcontentloaded');await started.wait()
  await page.locator('[data-booking] [name=hotel]').select_option('tagansky');gate.set()
  await page.wait_for_load_state('networkidle')
  assert await page.locator('.bk-live-frame').count()==0
  await page.locator('[data-booking] [type=submit]').click()
  await expect(page.locator('[data-live-hotel=tagansky]')).to_have_count(1)
  await browser.close()
 assert not errors,errors
 report={'status':'PASS','checks':checks,'stale_request_guard':'passed','js_errors':errors}
 (ROOT/'.qa/booking-scope-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())

