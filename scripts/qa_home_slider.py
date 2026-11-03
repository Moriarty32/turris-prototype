"""Panoramic homepage: visual rotation, explicit hotel selection and trip handoff."""
import asyncio,json
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 errors=[];checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':1366,'height':768});page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.clock.install();await page.goto(BASE+'/');await page.evaluate('Promise.all([...document.querySelectorAll(".hero-slide img")].map(i=>i.decode()))');await page.mouse.move(1,1)
  slider=page.locator('[data-hero-carousel]');active=slider.locator('.hero-slide.is-active');hotel=page.locator('.home-booking [name=hotel]')
  await expect(active).to_have_attribute('data-hero-slide','tverskaya');state=await page.evaluate("sessionStorage.getItem('turris-context')")
  await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','lubyansky')
  await page.locator('h1').hover();await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','lubyansky')
  await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','petrovsky')
  await page.locator('[data-hero-play]').click();await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','petrovsky')
  await page.locator('[data-hero-next]').click();await expect(active).to_have_attribute('data-hero-slide','tagansky')
  await page.locator('[data-hero-next]').click();await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  await page.locator('[data-hero-prev]').click();await expect(active).to_have_attribute('data-hero-slide','tagansky')
  await page.locator('[data-hero-play]').click();await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  await page.locator('.home-booking [data-dates]').focus();await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  assert await page.evaluate("sessionStorage.getItem('turris-context')")==state
  assert await slider.locator('.hero-slide:not(.is-active)[inert]').count()==3
  checks.append('5s autoplay, hover/focus pause, explicit pause/resume and preview arrows preserve trip; inactive slides are inert')
  await page.locator('[data-hero-pick="2"]').click();await expect(hotel).to_have_value('petrovsky');await expect(page.locator('.booking-bottom [name=hotel]')).to_have_value('petrovsky')
  await expect(page.locator('[data-hotel-map]')).to_have_attribute('data-selected','petrovsky')
  await page.keyboard.press('ArrowRight');await expect(hotel).to_have_value('tagansky');await expect(active).to_have_attribute('data-hero-slide','tagansky')
  assert 'turris-hotel-tagansky/' in await active.locator('a').get_attribute('href')
  await page.locator('.home-booking .ui-select-trigger').click();await page.locator('.ui-select-popover:popover-open [role=option]').filter(has_text='Лубянский').click();await expect(active).to_have_attribute('data-hero-slide','lubyansky');await expect(page.locator('[data-hero-pick="1"]')).to_have_attribute('aria-pressed','true')
  checks.append('Hotel pills and keyboard select the booking hotel and map; dropdown selection updates preview and pressed state')
  for width,height in [(320,740),(360,800),(390,844),(768,900),(1024,600),(1100,700),(1366,768),(1920,1080)]:
   await page.set_viewport_size({'width':width,'height':height});await page.clock.run_for(900);assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
   if width>=768:
    rect=await page.locator('.home-booking .booking-form>.btn').bounding_box();assert rect['y']+rect['height']<=height,(width,rect)
    for control in await page.locator('.hero-carousel-controls button').all():
     rect=await control.bounding_box();assert rect['height']>=44 and rect['width']>=44,(width,rect)
   else:
    await expect(active).not_to_be_visible();await expect(page.locator('.home-mobile-map [data-hotel-map]')).to_have_count(1);await expect(page.locator('.hero-carousel-controls')).not_to_be_visible()
  checks.append('Eight viewports: desktop CTA inside first screen; 44px carousel controls; mobile retains map instead of photography; no overflow')
  await c.close()
  # Restore an explicit complete trip, select another hotel and follow the real local booking route.
  c=await b.new_context(viewport={'width':1024,'height':600},reduced_motion='reduce')
  await c.add_init_script("sessionStorage.setItem('turris-context',JSON.stringify({hotel:'tverskaya',checkin:'2026-12-30',checkout:'2027-01-02',adults:2,children:[0,8],guestAgesConfirmed:true,room:''}))")
  await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Проверка параметров</p>'))
  page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));await page.goto(BASE+'/');await page.evaluate('document.fonts.ready')
  await expect(page.locator('[data-hero-pick="0"]')).to_have_attribute('aria-pressed','true');await page.locator('[data-hero-pick="3"]').click()
  state=await page.evaluate("JSON.parse(sessionStorage.getItem('turris-context'))");assert state['children']==[0,8] and state['checkin']=='2026-12-30' and state['hotel']=='tagansky'
  await page.locator('.home-booking [data-dates]').click();await expect(page.locator('#dates-dialog')).to_be_visible();await page.keyboard.press('Escape')
  await page.locator('.home-booking [data-guests]').click();await expect(page.locator('#guests-dialog')).to_be_visible();await page.keyboard.press('Escape')
  await page.locator('.home-booking [type=submit]').click();await page.wait_for_url('**/bronirovanie/**');q=parse_qs(urlsplit(page.url).query)
  assert q['hotel']==['tagansky'] and q['checkin']==['2026-12-30'] and q['checkout']==['2027-01-02'] and json.loads(q['children'][0])==[0,8]
  await expect(page.locator('[data-live-hotel]')).to_have_attribute('data-live-hotel','tagansky')
  checks.append('Restored dates and infant/child ages survive hotel choice, dialogs and submit; booking receives selected hotel only; provider request stubbed')
  await c.close();c=await b.new_context(java_script_enabled=False);page=await c.new_page();await page.goto(BASE+'/');await expect(page.locator('.hero-slide.is-active a')).to_be_visible();await expect(page.locator('.hero-carousel-controls')).not_to_be_visible();await expect(page.locator('.home-booking select')).to_be_visible();checks.append('No-JS fallback keeps the hotel link and native form')
  await b.close()
 assert not errors,errors
 report={'checks':checks,'javascript_errors':errors,'reservation_payment_or_lead_submitted':False}
 Path('docs/slider-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
