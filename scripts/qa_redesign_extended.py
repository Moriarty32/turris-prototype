import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':390,'height':844},locale='ru-RU',permissions=['clipboard-read','clipboard-write']);page=await c.new_page()
  await page.goto(BASE+'/');await page.locator('[data-dates]').first.click();await page.locator('#dates-form [name=checkin]').fill('2026-11-10');await page.locator('.calendar-day[data-date="2026-11-12"]').click();await expect(page.locator('#dates-form [name=checkout]')).to_have_value('2026-11-12');await page.keyboard.press('ArrowRight');await expect(page.locator('.calendar-day[data-date="2026-11-13"]')).to_be_focused();await page.locator('#dates-form [type=submit]').click();await expect(page.locator('[data-booking]').first.locator('[name=checkout]')).to_have_value('2026-11-12');checks.append('Calendar pointer range and roving keyboard focus work on mobile')
  # Fullscreen map semantics, background isolation and focus return in each template.
  for url,selector,modal in [('/hotels/turris-hotel-tverskaya/','[data-map-expand]','.hd-map'),('/family/','[data-offer-map-expand]','.map-stage'),('/bronirovanie/','[data-booking-expand]','.map-stage'),('/blog/','[data-journal-map-expand]','.map-stage')]:
   await page.goto(BASE+url);await page.locator(selector).click();await expect(page.locator(modal)).to_have_attribute('aria-modal','true');assert await page.locator('.ux-header').evaluate('e=>e.inert');await page.keyboard.press('Escape');assert not await page.locator('.ux-header').evaluate('e=>e.inert');await expect(page.locator(selector)).to_be_focused()
  checks.append('Hotel, offer, booking and blog fullscreen maps isolate background, Escape restores trigger focus')
  await page.goto(BASE+'/hotels/turris-hotel-tverskaya/');await page.locator('[data-hotel-photo]').first.click();await expect(page.locator('#hotel-gallery-dialog')).to_be_visible();before=await page.locator('[data-gallery-caption]').inner_text();await page.keyboard.press('ArrowRight');assert before!=await page.locator('[data-gallery-caption]').inner_text();await page.keyboard.press('Escape');await expect(page.locator('[data-hotel-photo]').first).to_be_focused();checks.append('Hotel gallery named dialog, next/previous keyboard and focus return')
  await page.goto(BASE+'/contacts/');await page.locator('[data-contact-copy]').filter(has=page.locator('svg')).first.click();assert await page.evaluate('navigator.clipboard.readText()');await expect(page.locator('[data-contact-copy-status]')).to_contain_text('Скопировано');checks.append('Contacts clipboard confirmation; no contact form submitted')
  await page.goto(BASE+'/blog/');await page.locator('[data-journal-rubric]').select_option('family');await expect(page.locator('[data-journal-card]:visible')).to_have_count(2);await page.locator('[data-journal-reset]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(6);await page.locator('[data-journal-more]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(12);checks.append('Guide topic filters, reset and progressive loading retained')
  await c.close()
  c=await b.new_context();page=await c.new_page();await c.route('**/assets/vendor/leaflet/leaflet.js',lambda route:route.abort());await page.goto(BASE+'/');await page.locator('#map').scroll_into_view_if_needed();await expect(page.locator('.map-retry')).to_be_visible();await expect(page.locator('[data-map-detail=tverskaya] .address')).to_be_visible();await c.unroute('**/assets/vendor/leaflet/leaflet.js');await page.locator('.map-retry').click();await page.wait_for_selector('#map .leaflet-marker-icon',timeout=20000);checks.append('Map engine failure exposes addresses/retry; retry successfully initializes one map')
  await c.close();c=await b.new_context(viewport={'width':1366,'height':900});page=await c.new_page()
  for url in ['/','/family/','/contacts/','/blog/choose-area/']:
   await page.goto(BASE+url);await page.evaluate("document.documentElement.style.zoom='2'");assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),url
  checks.append('200% zoom: home, family, contacts and article have no horizontal document overflow')
  await b.close()
 Path('docs/redesign-functional-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(checks,ensure_ascii=False,indent=2))
asyncio.run(main())
