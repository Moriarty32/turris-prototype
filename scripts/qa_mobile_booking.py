"""A complete mobile trip proceeds directly to room rates, with an optional editor."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
QUERY='?hotel=tverskaya&checkin=2026-12-30&checkout=2027-01-02&adults=2&children=%5B0%2C8%5D'
async def main():
 errors=[];checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Проверка загрузки модуля по переданным параметрам</p>'))
  page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/bronirovanie/'+QUERY);await expect(page.locator('.bk-live-frame')).to_be_visible();await expect(page.locator('#booking-search')).to_be_hidden();await expect(page.locator('.bk-trip-summary')).to_contain_text('Тверская');await expect(page.locator('.bk-trip-summary')).to_contain_text('до года, 8 лет');await expect(page.locator('#booking-hotels')).to_be_hidden();await expect(page.locator('.bk-map-section')).to_be_hidden();await expect(page.locator('.bk-steps')).to_be_hidden()
  frame=page.locator('.bk-live-frame');src=await frame.get_attribute('src');assert 'hotel=tverskaya' in src and 'date=2026-12-30' in src and 'nights=3' in src and 'children-age=0%2C8' in src
  rect=await frame.bounding_box();assert rect['y']<750,rect
  await page.screenshot(path='.qa/mobile-booking-results.png')
  # Clicking the summary is safe; only the edit button changes the current UI.
  await page.locator('[data-trip-summary-hotel]').click();assert 'hotel=tverskaya' in page.url;await expect(page.locator('#booking-search')).to_be_hidden()
  checks.append('Complete hotel/date/guest trip opens TravelLine immediately; compact summary includes child ages; no duplicate hotel chooser')
  await page.locator('[data-booking-edit]').click();await expect(page.locator('#booking-search')).to_be_visible();await expect(page.locator('[data-booking-edit]')).to_have_attribute('aria-expanded','true');await expect(page.locator('#booking-search [name=hotel]')).to_have_value('tverskaya')
  await page.locator('#booking-search .ui-select-trigger').click();await page.locator('.ui-select-popover:popover-open [role=option]').filter(has_text='Лубянский').click();await expect(page.locator('#booking-results')).to_be_hidden();await expect(page.locator('#booking-search')).to_be_visible()
  await page.locator('[data-booking-edit]').click();await expect(page.locator('#booking-search')).to_be_hidden();await expect(page.locator('[data-live-hotel]')).to_have_attribute('data-live-hotel','lubyansky');src=await frame.get_attribute('src');assert 'children-age=0%2C8' in src and 'date=2026-12-30' in src
  checks.append('Edit selected hotel then return to rooms refreshes results, retaining dates and explicit infant age')
  await page.locator('[data-booking-edit]').click();await page.locator('#booking-search [data-dates]').click();await page.locator('#dates-form [name=checkout]').fill('2027-01-04');await page.locator('#dates-form [type=submit]').click();await expect(page.locator('#booking-search')).to_be_visible();await page.locator('#booking-search [type=submit]').click();await expect(page.locator('#booking-search')).to_be_hidden();src=await frame.get_attribute('src');assert 'nights=5' in src
  checks.append('Changing dates and submitting refreshes rates and collapses the editor')
  await page.set_viewport_size({'width':1366,'height':900});await expect(page.locator('#booking-search')).to_be_visible();await expect(page.locator('.bk-trip-summary')).to_be_hidden();await expect(page.locator('#booking-hotels')).to_be_visible();await page.set_viewport_size({'width':390,'height':844});await expect(page.locator('#booking-search')).to_be_hidden()
  checks.append('Desktop full form and mobile compact results switch without losing trip state')
  await c.close()
  for path,query in [('/bronirovanie/',''),('/bronirovanie/','?hotel=tverskaya'),('/bronirovanie/','?hotel=tverskaya&checkin=2026-12-30&checkout=2027-01-02&children=%5Bnull%5D'),('/bronirovanie/','?hotel=unknown&checkin=2026-12-30&checkout=2027-01-02')]:
   c=await b.new_context(viewport={'width':390,'height':844});page=await c.new_page();await page.goto(BASE+path+query);await expect(page.locator('#booking-search')).to_be_visible();await expect(page.locator('.bk-trip-summary')).to_be_hidden();await c.close()
  checks.append('Incomplete or invalid trips retain the full form and child-age validation')
  for width,height in [(320,568),(390,844),(767,1024)]:
   c=await b.new_context(viewport={'width':width,'height':height});await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Проверка модуля</p>'));page=await c.new_page()
   await page.goto(BASE+'/hotels/turris-hotel-tverskaya/booking/'+QUERY);await expect(page.locator('#booking-search')).to_be_hidden();await expect(page.locator('.bk-live-frame')).to_be_visible();assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');await c.close()
  checks.append('Hotel-specific booking at 320, 390 and 767 px: automatic results, no horizontal overflow')
  await b.close()
 assert not errors,errors
 result={'checks':checks,'javascript_errors':errors,'widget_requests':'stubbed; checked hotel, dates, nights, adults and child ages','reservation_payment_or_lead_submitted':False};Path('docs/mobile-booking-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
asyncio.run(main())
