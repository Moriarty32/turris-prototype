"""Custom form controls: real user selection, accessibility and native state contracts."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
async def choose(page,trigger,text):
 await trigger.click();panel=page.locator('.ui-select-popover:popover-open');await expect(panel).to_be_visible();await panel.get_by_role('option').filter(has_text=text).first.click()
async def main():
 errors=[];checks=[];shots=Path('.qa/forms');shots.mkdir(exist_ok=True)
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':1366,'height':900},locale='ru-RU');page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/');hotel=page.locator('.home-booking .ui-select-trigger')
  await choose(page,hotel,'Таганский');await expect(page.locator('.home-booking select')).to_have_value('tagansky');await expect(page.locator('.booking-bottom .ui-select-value')).to_have_text('Таганский')
  await hotel.click();await page.keyboard.press('Home');await page.keyboard.press('Escape');await expect(page.locator('.home-booking select')).to_have_value('tagansky');await expect(hotel).to_be_focused()
  await hotel.press('ArrowDown');await hotel.dispatch_event('keydown',{'key':'п'});await page.keyboard.press('Enter');await expect(page.locator('.home-booking select')).to_have_value('petrovsky')
  await page.locator('.home-booking select').select_option('lubyansky');await expect(hotel).to_contain_text('Лубянский')
  await hotel.click();await page.locator('h1').click();await expect(page.locator('.ui-select-popover:popover-open')).to_have_count(0)
  checks.append('Hotel pointer/keyboard/typeahead, Escape cancellation, outside close, native change and both booking forms synchronize')
  await page.locator('.home-booking [data-guests]').click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('[data-save-guests]').click();age=page.locator('#guests-dialog .ui-select-trigger');await expect(age).to_have_attribute('aria-invalid','true');await expect(age).to_be_focused()
  await age.click();await page.keyboard.press('Escape');await expect(page.locator('#guests-dialog')).to_be_visible();await expect(age).to_be_focused()
  await choose(page,age,'До года');await expect(page.locator('[data-age="0"]')).to_have_value('0');await page.locator('[data-save-guests]').click();await expect(page.locator('.home-booking [data-guest-label]')).to_contain_text('1 ребёнок')
  state=await page.evaluate("JSON.parse(sessionStorage.getItem('turris-context'))");assert state['children']==[0] and state['guestAgesConfirmed']
  checks.append('Dynamic infant age in modal: validation focus, nested Escape keeps dialog open, explicit age zero saves correctly')
  await page.goto(BASE+'/family/');await page.locator('[data-family-count=children][data-delta="1"]').click();await choose(page,page.locator('[data-family-ages] .ui-select-trigger').last,'8 лет');assert await page.locator('[data-family-ages] select').last.input_value()=='8';await expect(page.locator('[data-family-ages] .ui-select-trigger').last).to_contain_text('8 лет')
  checks.append('Family child-age controls are enhanced after rendering and retain the correct age')
  await page.goto(BASE+'/blog/');topic=page.locator('[data-journal-rubric]').locator('..').locator('.ui-select-trigger');await choose(page,topic,'Москва с детьми');await page.locator('[data-journal-reset]').click();await expect(topic).to_contain_text('Все материалы')
  await page.goto(BASE+'/contacts/');await page.locator('[data-map-select=tagansky]').click();await expect(page.locator('[data-contact-form] [name=hotel]')).to_have_value('tagansky');await expect(page.locator('[data-contact-form] [name=hotel]').locator('..').locator('.ui-select-trigger')).to_contain_text('Таганский')
  checks.append('Guide filter/reset and contacts map update their visible select values; no contact submission')
  await page.goto(BASE+'/bronirovanie/');await choose(page,page.locator('#booking-search .ui-select-trigger'),'Тверская');await expect(page.locator('[data-booking-card]:visible')).to_have_count(1);await expect(page.locator('[data-booking-card]:visible')).to_have_attribute('data-booking-card','tverskaya')
  checks.append('Booking hotel selection retains one-hotel results scope')
  await c.close()
  for w,h in [(320,568),(390,844),(768,1024),(1024,600),(1366,768),(1920,1080)]:
   c=await b.new_context(viewport={'width':w,'height':h});page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   for name,path in [('home','/'),('booking','/bronirovanie/'),('family','/family/'),('hotel','/hotels/turris-hotel-tverskaya/'),('article','/blog/choose-area/'),('contacts','/contacts/'),('blog','/blog/')]:
    await page.goto(BASE+path,wait_until='domcontentloaded');await page.wait_for_timeout(80);assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(name,w)
   await page.goto(BASE+'/');await page.locator('.home-booking .ui-select-trigger').click();await page.wait_for_timeout(180);panel=page.locator('.ui-select-popover:popover-open');r=await panel.bounding_box();assert r['x']>=0 and r['y']>=0 and r['x']+r['width']<=w+1 and r['y']+r['height']<=h+1,(w,r)
   if w in [390,1366]:await page.screenshot(path=str(shots/f'hotel-dropdown-{w}.png'))
   await page.keyboard.press('Escape');await page.locator('.home-booking [data-guests]').click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('#guests-dialog .ui-select-trigger').click();await page.keyboard.press('End');await page.keyboard.press('Enter');await expect(page.locator('[data-age="0"]')).to_have_value('17');await page.locator('[data-save-guests]').click()
   await c.close()
  checks.append('Seven page types across six sizes; popup stays within viewport; long age list reaches 17 via keyboard')
  c=await b.new_context(java_script_enabled=False);page=await c.new_page();await page.goto(BASE+'/');await expect(page.locator('.home-booking select')).to_be_visible();assert await page.locator('.ui-select-trigger').count()==0;await c.close()
  c=await b.new_context(reduced_motion='reduce');page=await c.new_page();await page.goto(BASE+'/');await page.locator('.home-booking .ui-select-trigger').click();assert await page.locator('.ui-select-popover:popover-open').evaluate('e=>getComputedStyle(e).animationName')=='none';await c.close();checks.append('Native no-JS fallback and reduced-motion popup verified')
  await b.close()
 assert not errors,errors
 result={'checks':checks,'javascript_errors':errors,'reservation_payment_or_lead_submitted':False};Path('docs/forms-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
asyncio.run(main())
