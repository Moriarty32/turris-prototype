"""Mobile navigation, map-to-trip state and layout acceptance; no live booking sent."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 errors=[];checks=[];shots=Path('.qa/mobile');shots.mkdir(exist_ok=True)
 async with async_playwright() as p:
  browser=await p.chromium.launch();context=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
  page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/');await page.evaluate('document.fonts.ready');root=page.locator('[data-hotel-map]');await expect(root).to_have_attribute('data-map-loaded','true')
  await expect(page.locator('[data-hero-carousel]')).to_be_hidden();await expect(root).to_have_count(1);await expect(page.locator('.home-mobile-map [data-hotel-map]')).to_have_count(1)
  await expect(page.locator('.home-mobile-actions')).to_be_visible();await expect(page.locator('.home-booking select')).to_have_value('')
  stage=await page.locator('.map-stage').bounding_box()
  for pin in await page.locator('.map-pin').all():
   r=await pin.bounding_box();assert r['x']>=stage['x'] and r['y']>=stage['y']+44 and r['x']+r['width']<=stage['x']+stage['width'] and r['y']+r['height']<=stage['y']+stage['height'],r
  await page.screenshot(path=str(shots/'home-390.png'))
  for hotel in ['tverskaya','lubyansky','petrovsky','tagansky']:
   await page.locator('[data-map-select='+hotel+']').click();await expect(page.locator('.home-booking select')).to_have_value(hotel);await expect(page.locator('.booking-bottom select')).to_have_value(hotel)
  await expect(page.locator('[data-map-detail=tagansky]')).to_contain_text('лифта')
  await page.locator('[data-map-reset]').click();await page.locator('.map-pin').first.click();await expect(page.locator('.home-booking select')).to_have_value('tverskaya')
  checks.append('One hero map, no mobile carousel; four visible markers; marker and button selection update both booking forms')
  await page.locator('[data-mobile-book]').click();await expect(page.locator('#dates-dialog')).to_be_visible();await expect(page.locator('.home-mobile-actions')).to_be_hidden();await page.keyboard.press('Escape')
  await page.locator('.home-booking [data-guests]').click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('#guests-dialog .ui-select-trigger').click();await page.locator('.ui-select-popover:popover-open [role=option]').filter(has_text='До года').click();await page.locator('[data-save-guests]').click()
  await page.locator('[data-map-select=tagansky]').click();state=await page.evaluate("JSON.parse(sessionStorage.getItem('turris-context'))");assert state['children']==[0] and state['hotel']=='tagansky'
  await page.locator('.home-booking .ui-select-trigger').click();await page.locator('.ui-select-popover:popover-open [role=option]').filter(has_text='Любой из четырёх').click();await expect(root).to_have_attribute('data-selected','');await expect(page.locator('.map-choice[aria-pressed=true]')).to_have_count(0)
  checks.append('Sticky action opens calendar; guest ages survive map changes; any-hotel selection clears map highlight')
  await page.locator('.map-expand').click();await expect(root).to_have_attribute('aria-modal','true');await expect(page.locator('.home-mobile-actions')).to_be_hidden();await expect(page.locator('.map-move')).to_be_visible();await page.locator('.map-move').click();await expect(page.locator('.map-move')).to_have_attribute('aria-pressed','true');await page.keyboard.press('Escape');await expect(root).not_to_have_class('map-expanded');await expect(page.locator('.map-move')).to_have_attribute('aria-pressed','false')
  await page.locator('.menu-button').click();await expect(page.locator('.home-mobile-actions')).to_be_hidden();await expect(page.locator('main')).to_have_attribute('inert','');await page.keyboard.press('Escape')
  await page.locator('.footer-toggle').first.click();await expect(page.locator('#footer-links-0')).to_be_visible();await page.locator('.footer-toggle').first.click();await expect(page.locator('#footer-links-0')).to_be_hidden()
  checks.append('Fullscreen map, touch movement, menu/modal isolation and footer disclosures work')
  await page.set_viewport_size({'width':1366,'height':768});await expect(page.locator('.home-map-section [data-hotel-map]')).to_have_count(1);await expect(page.locator('[data-hero-carousel]')).to_be_visible();await expect(page.locator('.home-mobile-actions')).to_be_hidden();await expect(page.locator('#footer-links-0')).to_be_visible();await expect(page.locator('[data-map-detail=tverskaya]')).to_be_visible()
  await page.set_viewport_size({'width':390,'height':844});await expect(page.locator('.home-mobile-map [data-hotel-map]')).to_have_count(1);await expect(page.locator('.home-booking [data-guest-label]')).to_contain_text('1 ребёнок')
  checks.append('Responsive relocation keeps one map, guest state and desktop carousel; footer links restored on desktop')
  await context.close()
  routes=json.loads(Path('data/routes.json').read_text(encoding='utf8'))['pages'];layouts=[]
  for width,height in [(320,568),(390,844)]:
   context=await browser.new_context(viewport={'width':width,'height':height},is_mobile=True,has_touch=True);page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   for route in routes:
    await page.goto(BASE+route['url'],wait_until='domcontentloaded');await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(route['id'],width)
    layouts.append([route['id'],width]);assert 'noindex' in await page.locator('meta[name=robots]').get_attribute('content')
   await context.close()
  checks.append('109 routes at 320 and 390 px: no horizontal overflow, noindex retained')
  context=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});page=await context.new_page();await page.goto(BASE+'/');await expect(page.locator('.home-booking select')).to_be_visible();await expect(page.locator('.footer-links').first).to_be_visible();await expect(page.locator('.map-choices')).to_be_visible();await context.close()
  checks.append('No-JS fallback retains forms, map address choices and footer links')
  await browser.close()
 assert not errors,errors
 result={'checks':checks,'layouts_tested':len(layouts),'javascript_errors':errors,'reservation_payment_or_lead_submitted':False};Path('docs/mobile-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
asyncio.run(main())
