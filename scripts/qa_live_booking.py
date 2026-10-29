"""Live TravelLine checks: public embedding, selected hotel, trip, tariffs. Never submits a booking."""
import asyncio,json,os
from pathlib import Path
from datetime import date,timedelta
from urllib.parse import urlparse,parse_qs
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('QA_BASE','http://127.0.0.1:4173/turris-prototype')
START=(date.today()+timedelta(days=12)).isoformat();END=(date.today()+timedelta(days=14)).isoformat()
async def main():
 checks=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  for hotel,width in [('tverskaya',390),('lubyansky',1440),('petrovsky',390),('tagansky',1440)]:
   c=await browser.new_context(viewport={'width':width,'height':900},locale='ru-RU');page=await c.new_page()
   await page.goto(BASE+'/bronirovanie/?hotel='+hotel+'&checkin='+START+'&checkout='+END+'&adults=2',wait_until='domcontentloaded')
   await expect(page.locator('[data-live-hotel='+hotel+']')).to_be_visible()
   module=page.frame_locator('.bk-live-frame').frame_locator('iframe[src*="/booking2/"]').first
   await expect(module.get_by_role('button',name='Выбрать',exact=True).first).to_be_visible(timeout=60000)
   provider=next(f for f in page.frames if '/booking2/' in f.url and '/s/cart' not in f.url)
   q=parse_qs(urlparse(provider.url).query)
   assert q['date']==[START] and q['nights']==['2'] and q['adults']==['2']
   assert '₽' in await provider.locator('body').inner_text()
   await page.wait_for_function("parseFloat(document.querySelector('.bk-live-frame').style.height)>700")
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   await expect(page.locator('[data-live-status]')).to_be_hidden()
   # Nonbinding category choice, stop at tariffs (no guest details, no payment).
   await module.get_by_role('button',name='Выбрать',exact=True).first.click()
   await expect(module.get_by_text('Выберите тариф',exact=True)).to_be_visible(timeout=20000)
   await page.locator('.bk-live-frame').scroll_into_view_if_needed()
   await page.screenshot(path=str(ROOT/'.qa'/('live-verified-'+hotel+'.png')))
   checks.append({'hotel':hotel,'width':width,'provider_id':q.get('providerId'),'real_prices':True,'dates_transferred':True,'tariff_selection':True,'overflow':False})
   print('PASS',hotel,width,flush=True);await c.close()
  # Real bridge loading failure: all documented loader hosts unavailable.
  c=await browser.new_context();page=await c.new_page()
  await c.route('**/integration/loader.js',lambda r:r.abort())
  await page.goto(BASE+'/bronirovanie/?hotel=tagansky&checkin='+START+'&checkout='+END,wait_until='domcontentloaded')
  await expect(page.locator('[data-live-status]')).to_contain_text('Не удалось подключить',timeout=15000)
  await expect(page.locator('[data-official-booking]')).to_have_attribute('href',__import__('re').compile('https://turris.online/hotels/turris-hotel-tagansky/booking/'))
  # Untrusted same-origin message without matching iframe source must be ignored.
  await page.evaluate("window.postMessage({source:'turris-booking',type:'ready'},location.origin)")
  await expect(page.locator('[data-live-status]')).to_contain_text('Не удалось подключить')
  await browser.close()
 report={'status':'PASS','date':date.today().isoformat(),'base':BASE,'live_checks':checks,'loader_failure_fallback':True,'untrusted_message_ignored':True,'actual_booking_submitted':False,'payment_tested':False}
 (ROOT/'docs/live-booking-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
