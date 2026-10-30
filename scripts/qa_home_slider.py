"""Homepage carousel: autoplay, pause, accessible controls and trip independence."""
import asyncio,json,os
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE=os.getenv('QA_BASE','http://127.0.0.1:4173/turris-prototype')
async def main():
 errors=[];checks=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':1366,'height':768});page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.clock.install();await page.goto(BASE+'/');await page.mouse.move(1,1)
  slider=page.locator('[data-hero-carousel]');active=slider.locator('.hero-slide.is-active')
  await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  state=await page.evaluate("sessionStorage.getItem('turris-context')")
  await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','lubyansky')
  await slider.hover();await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','lubyansky')
  await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','petrovsky')
  await page.locator('[data-hero-play]').click();await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','petrovsky')
  await page.locator('[data-hero-next]').click();await expect(active).to_have_attribute('data-hero-slide','tagansky')
  await page.locator('[data-hero-next]').click();await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  await page.locator('[data-hero-prev]').click();await expect(active).to_have_attribute('data-hero-slide','tagansky')
  await page.locator('[data-hero-play]').click();await page.mouse.move(1,1);await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  await page.locator('.home-booking [data-dates]').focus();await page.clock.run_for(5600);await expect(active).to_have_attribute('data-hero-slide','tverskaya')
  assert await page.evaluate("sessionStorage.getItem('turris-context')")==state
  assert await slider.locator('.hero-slide:not(.is-active)[inert]').count()==3
  await page.locator('[data-hero-pick="2"]').click();await page.keyboard.press('ArrowRight');await expect(active).to_have_attribute('data-hero-slide','tagansky')
  assert 'turris-hotel-tagansky/' in await active.locator('a').get_attribute('href')
  checks.append('5s autoplay, hover pause, explicit pause/resume, focus pause, arrows, all four hotels and wraparound; booking state unchanged')
  await page.locator('[data-hero-pick="0"]').click();await page.clock.run_for(700)
  await page.evaluate('Promise.all([...document.querySelectorAll(".hero-slide img")].map(i=>i.decode()))')
  button=await page.locator('.home-booking .booking-form>.btn').bounding_box();assert button['y']+button['height']<768
  await asyncio.sleep(.8);await page.screenshot(path='.qa/slider-desktop.png')
  for width in [320,360,390,768,1100,1366,1440]:
   await page.set_viewport_size({'width':width,'height':900});await page.clock.run_for(700)
   assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
   for control in await slider.locator('button').all():
    rect=await control.bounding_box();assert rect['height']>=44 and rect['width']>=24,(width,rect)
  checks.append('Seven viewport widths; desktop booking CTA stays in first screen; controls have 44px height')
  await c.close()
  c=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');page=await c.new_page();await page.clock.install();await page.goto(BASE+'/');slider=page.locator('[data-hero-carousel]');await slider.scroll_into_view_if_needed();await page.clock.run_for(6000)
  await expect(slider.locator('.hero-slide.is-active')).to_have_attribute('data-hero-slide','tverskaya')
  await slider.dispatch_event('pointerdown',{'pointerType':'touch','clientX':300,'clientY':100});await slider.dispatch_event('pointerup',{'pointerType':'touch','clientX':90,'clientY':110})
  await expect(slider.locator('.hero-slide.is-active')).to_have_attribute('data-hero-slide','lubyansky')
  await page.evaluate('Promise.all([...document.querySelectorAll(".hero-slide img")].map(i=>i.decode()))');await asyncio.sleep(.8)
  await page.screenshot(path='.qa/slider-mobile.png');checks.append('Reduced motion disables autoplay by default; mobile swipe changes hotel')
  await c.close();c=await b.new_context(java_script_enabled=False);page=await c.new_page();await page.goto(BASE+'/');await expect(page.locator('.hero-slide.is-active a')).to_be_visible();await expect(page.locator('.hero-carousel-controls')).not_to_be_visible();checks.append('Without JavaScript: first hotel and its link remain usable')
  await b.close()
 assert not errors,errors
 report={'checks':checks,'javascript_errors':errors,'reservation_submitted':False}
 Path('docs/slider-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
