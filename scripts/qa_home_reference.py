"""Home-specific reference acceptance: first screen, navigation and map disclosure."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 errors=[];checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch()
  for width,height in [(390,844),(901,900),(1024,900),(1440,900)]:
   c=await b.new_context(viewport={'width':width,'height':height},locale='ru-RU')
   await c.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
   page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(BASE+'/',wait_until='networkidle')
   cta=await page.locator('.hero [type=submit]').bounding_box()
   assert cta['y']+cta['height']<height,(width,cta)
   if width==390:
    box=await page.locator('.hero .map-stage').bounding_box()
    assert box['y']+box['height']<=844,box
    await page.locator('.menu-button').click()
    await page.locator('.nav summary').nth(1).click()
    assert await page.locator('.nav a[href$="/family/"]').is_visible()
    await page.keyboard.press('Escape')
    assert not await page.locator('.nav').is_visible()
    await page.locator('.hero [data-guests]').click()
    for _ in range(2):await page.locator('[data-count=children][data-change="1"]').click()
    await page.locator('[data-age="0"]').select_option('4');await page.locator('[data-age="1"]').select_option('8')
    await page.locator('[data-save-guests]').click()
    assert await page.locator('.hero [name=children]').input_value()=='[4,8]'
   else:
    navbox=await page.locator('.nav>a[href$="/contacts/"]').bounding_box()
    actionbox=await page.locator('.header-booking').bounding_box()
    assert navbox['x']+navbox['width']<=actionbox['x'],(width,navbox,actionbox)
    await page.locator('.nav summary').first.click()
    assert await page.locator('.nav .drop').first.is_visible()
    await page.keyboard.press('Escape')
    assert not await page.locator('.nav .drop').first.is_visible()
    await page.locator('[data-hotel-view=map]').click()
    for hotel in ['lubyansky','petrovsky','tagansky','tverskaya']:
     await page.locator('[data-map-select='+hotel+']').click()
     assert await page.locator('.home-map-item [data-map-detail]:visible').count()==1
     assert await page.locator('[data-map-select='+hotel+']').get_attribute('aria-expanded')=='true'
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   checks.append({'width':width,'first_cta':cta,'navigation':'passed'})
   await c.close()
  await b.close()
 assert not errors,errors
 report={'status':'PASS','checks':checks,'js_errors':errors}
 (ROOT/'.qa/home-reference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
