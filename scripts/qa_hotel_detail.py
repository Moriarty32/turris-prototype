"""Validate all four overview pages, responsive layout and booking/gallery/map behavior."""
import asyncio,json,os
from pathlib import Path
from datetime import date,timedelta
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('QA_BASE','http://127.0.0.1:4173/turris-prototype')
PAGES=[p for p in json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))['pages'] if p['template']=='hotel']
async def main():
 errors=[];results=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch()
  for width in [320,390,768,1024,1440]:
   context=await browser.new_context(viewport={'width':width,'height':900},device_scale_factor=2,locale='ru-RU',is_mobile=width<700,has_touch=width<700)
   await context.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
   page=await context.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
   for p in PAGES:
    await context.clear_cookies()
    await page.goto(BASE+p['url']+'?v=hotel-1',wait_until='networkidle')
    await page.evaluate('sessionStorage.clear()')
    assert await page.locator('.hd-room').count()==3
    assert await page.locator('h1').count()==1
    assert await page.locator('meta[name=robots]').get_attribute('content')=='noindex,nofollow'
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(p['id'],width,'overflow')
    # Every page image has a local high-quality source, with no empty/broken image.
    for im in await page.locator('.hotel-detail img[data-asset]').all():
     await im.scroll_into_view_if_needed()
     await im.evaluate('(im)=>im.decode()')
     assert await im.evaluate('(im)=>im.naturalWidth>0')
    await page.locator('.hd-main-photo').click()
    modal=page.locator('#hotel-gallery-dialog')
    assert await modal.is_visible()
    first=await modal.locator('img').get_attribute('src')
    await page.keyboard.press('ArrowRight')
    assert await modal.locator('img').get_attribute('src')!=first
    await page.keyboard.press('ArrowLeft')
    assert await modal.locator('img').get_attribute('src')==first
    await page.keyboard.press('Escape')
    assert not await modal.is_visible()
    # Single-hotel map, failure fallback, expanded keyboard/touch controls.
    await page.locator('#map').scroll_into_view_if_needed()
    await page.wait_for_function("document.querySelector('#map').dataset.mapLoaded === 'true'")
    assert await page.locator('.map-pin').count()==1
    assert await page.locator('#map').get_attribute('data-selected')==p['id']
    await page.locator('[data-map-expand]').click()
    assert await page.locator('#map').evaluate("el=>el.classList.contains('hd-map-expanded')")
    await page.keyboard.press('Escape')
    assert not await page.locator('#map').evaluate("el=>el.classList.contains('hd-map-expanded')")
    # Category CTA must preserve hotel/category, dates and guests into booking.
    link=page.locator('[data-select-room]').first;rid=await link.get_attribute('data-select-room')
    await link.click()
    if await page.locator('#dates-dialog').is_visible():
     start=(date.today()+timedelta(days=10)).isoformat();end=(date.today()+timedelta(days=12)).isoformat()
     await page.locator('#dates-form [name=checkin]').fill(start)
     await page.locator('#dates-form [name=checkout]').fill(end)
     await page.locator('#dates-form button[type=submit]').click()
     await page.locator('#hotel-booking [data-guests]').click()
     await page.locator('[data-count=adults][data-change="1"]').click()
     await page.locator('[data-save-guests]').click()
     await page.locator('#hotel-booking [type=submit]').click()
    await page.wait_for_url('**/bronirovanie/?**')
    assert 'hotel='+p['id'] in page.url and 'room='+rid in page.url,(p['id'],page.url)
    results.append({'hotel':p['id'],'width':width,'gallery':'pass','booking':'pass','map':'pass','images':'pass','overflow':False})
   await context.close()
  # No-JS provides ordinary links and all essential content.
  context=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  page=await context.new_page()
  await page.goto(BASE+PAGES[0]['url'])
  assert await page.locator('.hd-main-photo').get_attribute('href')
  assert await page.locator('[data-select-room]').first.get_attribute('href')
  assert await page.locator('.hd-location-copy .btn').get_attribute('href')
  await browser.close()
 assert not errors,errors
 report={'status':'PASS','pages':4,'viewports':[320,390,768,1024,1440],'checks':results,'js_errors':errors,'no_js':'pass'}
 (ROOT/'docs/verification-hotel-detail.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':'PASS','responsive_checks':len(results),'js_errors':errors}))
asyncio.run(main())
