"""Reference guide acceptance: layout, generated media, filters, pagination, map and booking."""
import asyncio,json,os
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1];BASE=os.environ.get('QA_BASE','http://127.0.0.1:4173/turris-prototype')
async def main():
 checks=[];errors=[]
 for name in ['guide-documents','guide-arrival']:
  assert Image.open(ROOT/'assets'/f'{name}.png').size==(2048,768)
  assert Image.open(ROOT/'assets'/f'{name}.webp').size==(2048,768)
 async with async_playwright() as p:
  b=await p.chromium.launch()
  for width in [320,390,640,768,1024,1440]:
   c=await b.new_context(viewport={'width':width,'height':900},locale='ru-RU');page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(BASE+'/blog/',wait_until='networkidle')
   await expect(page.locator('[data-journal-card]:visible')).to_have_count(6)
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),width
   assert 'rgb(0, 106, 239)'==await page.locator('.jr-feature .btn').evaluate('e=>getComputedStyle(e).backgroundColor')
   for card in await page.locator('[data-journal-card]:visible').all():
    await card.scroll_into_view_if_needed();await expect(card.locator('img')).to_have_js_property('complete',True)
    await page.wait_for_function('(im)=>im.naturalWidth>0',arg=await card.locator('img').element_handle())
   await page.locator('[data-journal-more]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(12)
   await page.locator('[data-journal-more]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(16);await expect(page.locator('[data-journal-more]')).to_be_hidden()
   await page.locator('[data-journal-pages] [data-page="2"]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(6)
   await page.reload(wait_until='networkidle');await expect(page.locator('[data-journal-card]:visible')).to_have_count(6);assert 'page=2' in page.url
   await page.locator('[data-journal-more]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(10)
   await page.locator('[data-journal-rubric]').select_option('districts');await expect(page.locator('[data-journal-card]:visible')).to_have_count(5)
   await page.locator('[data-journal-hotel]').select_option('tagansky');await expect(page.locator('[data-journal-card]:visible')).to_have_count(2)
   await page.locator('[data-journal-search]').fill('Серебрянический');await expect(page.locator('[data-journal-card]:visible')).to_have_count(2)
   await page.locator('[data-journal-search]').fill('неттакогоматериала');await expect(page.locator('[data-journal-empty]')).to_be_visible()
   await page.locator('[data-journal-clear]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(6)
   await page.locator('[data-journal-topic=family]').click();await expect(page.locator('[data-journal-card]:visible')).to_have_count(2)
   await page.locator('[data-journal-reset]').click()
   # Real Leaflet engine and markers, actual tile service is allowed.
   await page.locator('#guide-map').scroll_into_view_if_needed()
   await page.wait_for_function("document.querySelector('#map').dataset.mapLoaded==='true'")
   await expect(page.locator('.map-pin')).to_have_count(4)
   await page.locator('[data-map-select=lubyansky]').click();await expect(page.locator('[data-map-detail]:visible')).to_have_count(1)
   await expect(page.locator('[data-map-select=lubyansky]')).to_have_attribute('aria-expanded','true')
   assert '/blog/lubyanka-walk/' in await page.locator('[data-map-detail=lubyansky] .btn').get_attribute('href')
   assert await page.locator('.jr-booking [name=hotel]').input_value()=='lubyansky'
   await page.locator('[data-journal-map-expand]').click();await expect(page.locator('.jr-map-expanded .map-stage')).to_have_attribute('aria-modal','true')
   await page.keyboard.press('Escape');assert not await page.locator('.jr-map-expanded').count()
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),(width,'map')
   checks.append({'width':width,'filters':True,'pagination':True,'map':True,'no_overflow':True});await c.close()
  c=await b.new_context(viewport={'width':1440,'height':1000});page=await c.new_page();await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='Provider contract stub'))
  await page.goto(BASE+'/blog/',wait_until='networkidle');await page.locator('.jr-booking [name=hotel]').select_option('tagansky');await page.locator('.jr-booking [data-dates]').click();await page.locator('#dates-form [name=checkin]').fill('2026-12-10');await page.locator('#dates-form [name=checkout]').fill('2026-12-12');await page.locator('#dates-form [type=submit]').click();await page.locator('.jr-booking [type=submit]').click();await expect(page.locator('[data-live-hotel=tagansky]')).to_be_visible()
  for rubric,count in [('districts',5),('family',2),('business',3),('stay',6)]:
   await page.goto(BASE+'/blog/'+rubric+'/',wait_until='networkidle');await expect(page.locator('[data-journal-card]:visible')).to_have_count(count)
  await page.locator('[data-journal-rubric]').select_option('family');await page.wait_for_url('**/blog/?topic=family**');await expect(page.locator('[data-journal-card]:visible')).to_have_count(2)
  await c.close()
  c=await b.new_context(java_script_enabled=False);page=await c.new_page();await page.goto(BASE+'/blog/');assert await page.locator('[data-journal-card]:visible').count()==16;assert await page.locator('[data-map-detail] .btn').count()==4;await c.close()
  c=await b.new_context(reduced_motion='reduce');page=await c.new_page();await page.goto(BASE+'/blog/');assert await page.locator('.jr-card-photo img').first.evaluate('e=>getComputedStyle(e).transitionDuration')=='0s';await c.close()
  await b.close()
 assert not errors,errors
 report={'status':'PASS','reference':'image-1.png','responsive_checks':checks,'generated_assets':[2048,768],'all_16_articles_accessible':True,'rubric_pages':True,'no_js_links':True,'reduced_motion':True,'live_booking_handoff':True,'js_errors':errors}
 (ROOT/'docs/blog-reference-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
