"""Redesign acceptance. No reservation, payment or real lead is submitted."""
import asyncio,json,os
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1];BASE=os.getenv('QA_BASE','http://127.0.0.1:4173/turris-prototype')
async def navigate(page,url):
 for attempt in range(3):
  try:
   await page.goto(url,wait_until='domcontentloaded');return
  except Exception as e:
   if 'ERR_NETWORK_CHANGED' not in str(e) or attempt==2:raise
   await page.wait_for_timeout(400)
async def main():
 checks=[];errors=[];shots=ROOT/'.qa/redesign';shots.mkdir(exist_ok=True)
 routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf8'))['pages']
 # Every route is built with the same navigation and noindex. Validate local links.
 menus=[]
 for route in routes:
  soup=BeautifulSoup((ROOT/'dist'/route['url'].strip('/')/'index.html').read_text(encoding='utf8'),'html.parser')
  assert 'noindex' in soup.select_one('meta[name=robots]')['content']
  menus.append([a['href'] for a in soup.select('.ux-header a[href]')])
  for dialog in soup.select('dialog'):assert dialog.get('aria-label') or dialog.get('aria-labelledby'),route['id']
  for a in soup.select('a[href]'):
   href=a['href'].split('?')[0].split('#')[0]
   if href.startswith('/turris-prototype/'):
    local=ROOT/'dist'/href.removeprefix('/turris-prototype/')
    assert local.is_file() or (local/'index.html').exists(),(route['id'],href)
 assert all(m==menus[0] for m in menus)
 checks.append('109 routes: identical navigation links, local links resolve, named dialogs, noindex')
 async with async_playwright() as p:
  browser=await p.chromium.launch();context=await browser.new_context(viewport={'width':1366,'height':768},locale='ru-RU');page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await navigate(page,BASE+'/');await page.wait_for_timeout(350)
  assert await page.locator('.home-booking').evaluate('e=>e.getBoundingClientRect().bottom<=innerHeight')
  await page.screenshot(path=str(shots/'home-desktop.png'))
  await page.locator('.menu-button').click();await page.wait_for_timeout(250);await page.screenshot(path=str(shots/'menu-desktop.png'));await page.keyboard.press('Escape');await expect(page.locator('.menu-button')).to_be_focused()
  await expect(page.locator('.home-explorer')).to_have_count(0);await expect(page.locator('.home-hero + .home-map-section')).to_have_count(1);assert await page.locator('[data-booking]').first.locator('[name=hotel]').input_value()==''
  # Trip draft, cancellation, explicit age including zero.
  await page.locator('[data-guests]').first.click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('[data-save-guests]').click();await expect(page.locator('[data-age="0"]')).to_have_attribute('aria-invalid','true');await expect(page.locator('#guests-dialog')).to_be_visible()
  await page.screenshot(path=str(shots/'guests-desktop.png'));await page.locator('[data-age="0"]').select_option('0');await page.locator('[data-save-guests]').click();await page.locator('[data-guests]').last.click();await expect(page.locator('[data-age="0"]')).to_have_value('0');await page.locator('[data-count=adults][data-change="1"]').click();await page.keyboard.press('Escape');await page.locator('[data-guests]').first.click();await expect(page.locator('[data-count-value=adults]')).to_have_text('2');await page.keyboard.press('Escape')
  await page.locator('[data-dates]').first.click();await page.wait_for_timeout(250);await page.screenshot(path=str(shots/'calendar-desktop.png'));assert await page.locator('.calendar-month:visible').count()==2
  await page.locator('#dates-form [name=checkin]').fill('2026-12-30');await page.locator('#dates-form [name=checkout]').fill('2027-01-02');await page.locator('#dates-form [type=submit]').click();await expect(page.locator('[data-booking]').last.locator('[name=checkout]')).to_have_value('2027-01-02')
  await page.locator('[data-dates]').last.click();await page.locator('#dates-form [name=checkout]').fill('2027-01-06');await page.keyboard.press('Escape');await page.locator('[data-dates]').first.click();await expect(page.locator('#dates-form [name=checkout]')).to_have_value('2027-01-02');await page.keyboard.press('Escape')
  # Invalid range stays editable and returns a local error.
  await page.locator('[data-dates]').first.click();await page.locator('#dates-form [name=checkout]').fill('2026-12-30');await page.locator('#dates-form [type=submit]').click();await expect(page.locator('#dates-form .form-error')).not_to_be_empty();await page.keyboard.press('Escape')
  # Map is lazy, preview is independent, explicit CTA preserves the trip.
  await page.locator('#map').scroll_into_view_if_needed();await page.wait_for_selector('#map .leaflet-marker-icon',timeout=20000);await page.locator('#map [data-map-select=tagansky]').click();assert await page.locator('[data-booking]').first.locator('[name=hotel]').input_value()==''
  await page.wait_for_timeout(700);await page.locator('#map').screenshot(path=str(shots/'map-desktop.png'))
  await page.locator('.map-expand').click();assert await page.locator('.ux-header').evaluate('e=>e.inert');await expect(page.locator('#map')).to_have_attribute('aria-modal','true');await page.keyboard.press('Escape');await expect(page.locator('.map-expand')).to_be_focused();assert not await page.locator('.ux-header').evaluate('e=>e.inert')
  await page.locator('#map [data-map-detail=tagansky] [data-trip-hotel]').click();await page.wait_for_url('**/bronirovanie/?*');assert 'hotel=tagansky' in page.url and 'checkin=2026-12-30' in page.url;await expect(page.locator('[data-booking-card]:visible')).to_have_count(1);await expect(page.locator('[data-booking-card=tagansky]')).to_be_visible()
  checks.append('Desktop hero, menu, map-first home, date/guest draft cancellation, explicit zero age, year boundary, range validation, real Leaflet, modal isolation, preserved booking handoff, one-hotel scope')
  # Real provider network is not needed for interaction tests; loading/error fallback retains parameters.
  await page.route('**/assets/booking-widget.html?*',lambda route:route.fulfill(status=200,content_type='text/html',body='<html><head><title>QA</title></head><body>Provider isolated for UI test</body></html>'))
  await page.reload();frame=page.locator('.bk-live-frame');await expect(frame).to_be_visible();src=await frame.get_attribute('src');assert 'nights=3' in src and 'children=1' in src and 'children-age=0' in src
  await page.locator('[data-retry-results]').click();await expect(page.locator('[data-official-booking]')).to_have_attribute('href',__import__('re').compile(r'https://turris.online/hotels/turris-hotel-tagansky/booking/.*'))
  checks.append('TravelLine iframe and official fallback retain dates, nights, children and explicitly selected infant age; retry remains available')
  await context.close()
  # Mobile navigation modal; forms first; state survives resize and reduced motion.
  for width in [320,360,390,768,1100,1366,1440]:
   context=await browser.new_context(viewport={'width':width,'height':900},locale='ru-RU');page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   for name,url in [('home','/'),('hotel','/hotels/turris-hotel-tverskaya/'),('booking','/bronirovanie/'),('family','/family/'),('contacts','/contacts/'),('blog','/blog/'),('article','/blog/choose-area/')]:
    await navigate(page,BASE+url);await page.wait_for_timeout(250);assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(name,width)
    if width in [390,1366]:
     await page.evaluate('Promise.all([...document.images].filter(i=>i.loading!=="lazy").map(i=>i.decode().catch(()=>{})))');await page.screenshot(path=str(shots/f'{name}-{width}.png'))
   await navigate(page,BASE+'/');await page.locator('.menu-button').click();await page.wait_for_timeout(250)
   if width<768:
    assert await page.locator('main').evaluate('e=>e.inert');await expect(page.locator('.ux-header')).to_have_attribute('aria-modal','true')
    await page.locator('.menu-booking').scroll_into_view_if_needed();await page.keyboard.press('Tab');assert await page.evaluate('document.querySelector(".ux-header").contains(document.activeElement)')
   if width==390:await page.screenshot(path=str(shots/'menu-mobile.png'))
   await page.keyboard.press('Escape');assert not await page.locator('main').evaluate('e=>e.inert')
   await page.locator('[data-dates]').first.click();await page.wait_for_timeout(250);assert await page.locator('.calendar-month:visible').count()==(1 if width<768 else 2)
   if width==390:await page.screenshot(path=str(shots/'calendar-mobile.png'))
   await page.keyboard.press('Escape');await page.locator('[data-guests]').first.click();await page.locator('[data-count=children][data-change="1"]').click();await page.wait_for_timeout(250)
   if width==390:await page.screenshot(path=str(shots/'guests-mobile.png'))
   await page.keyboard.press('Escape');await context.close()
  checks.append('Seven responsive widths × seven key pages; mobile menu semantics/focus isolation; one/two month calendar; no horizontal overflow')
  # Existing persisted zero is uncertain; explicitly chosen new zero is preserved above.
  context=await browser.new_context();await context.add_init_script("sessionStorage.setItem('turris-context',JSON.stringify({adults:2,children:[0],hotel:'tagansky'}))");page=await context.new_page();await navigate(page,BASE+'/');await page.locator('[data-guests]').first.click();await expect(page.locator('[data-age="0"]')).to_have_value('');await context.close();checks.append('Legacy implicit infant age requests explicit confirmation')
  context=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});page=await context.new_page();await navigate(page,BASE+'/');await expect(page.locator('[data-map-detail]')).to_have_count(4);await expect(page.locator('.site-menu')).to_be_visible();await context.close();checks.append('Without JS all hotel content and navigation remain available')
  context=await browser.new_context(reduced_motion='reduce');page=await context.new_page();await navigate(page,BASE+'/');await page.locator('.menu-button').click();assert await page.locator('.site-menu').evaluate('e=>getComputedStyle(e).animationName')=='none';await context.close();checks.append('Reduced-motion navigation has no entrance animation')
  await browser.close()
 assert not errors,errors
 report={'date':'2026-10-30','checks':checks,'javascript_errors':errors,'screenshots':str(shots),'reservation_or_payment_submitted':False}
 (ROOT/'docs/redesign-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
