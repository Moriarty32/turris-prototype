import asyncio,json
from pathlib import Path
from urllib.parse import urlparse,unquote,parse_qs
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 errors=[];checked=0;flows=[]
 for file in (ROOT/'dist').rglob('index.html'):
  soup=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser');checked+=1
  for el in soup.select('a[href],img[src],script[src],link[href]'):
   u=el.get('href',el.get('src',''))
   if u.startswith('/turris-prototype/'):
    dest=ROOT/'dist'/unquote(urlparse(u).path).removeprefix('/turris-prototype/')
    if dest.is_dir():dest=dest/'index.html'
    assert dest.exists(),(file,u)
 async with async_playwright() as p:
  b=await p.chromium.launch()
  for path,hotel in [('/','lubyansky'),('/hotels/turris-hotel-tagansky/','tagansky'),('/blog/choose-area/','petrovsky'),('/hotels/turris-hotel-tverskaya/rooms/semeynyy-lyuks/','tverskaya')]:
   c=await b.new_context(viewport={'width':390,'height':844});await c.route('**/assets/booking-widget.html?*',lambda r:r.fulfill(content_type='text/html',body='<p>Provider contract stub</p>'))
   page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   await page.goto(BASE+path,wait_until='domcontentloaded')
   form=page.locator('[data-booking]').first
   print('CHECK',path,flush=True)
   select=form.locator('[name=hotel]')
   if await select.is_visible():await select.select_option(hotel)
   elif path=='/':await page.locator('[data-map-select='+hotel+']').first.click()
   else:assert await select.input_value()==hotel
   await form.locator('[data-dates]').click();await page.locator('#dates-form [name=checkin]').fill('2026-12-10');await page.locator('#dates-form [name=checkout]').fill('2026-12-13');await page.locator('#dates-form [type=submit]').click()
   await form.locator('[type=submit]').click();await page.wait_for_url('**/bronirovanie/**')
   await expect(page.locator('[data-live-hotel='+hotel+']')).to_be_visible()
   q=parse_qs(urlparse(await page.locator('.bk-live-frame').get_attribute('src')).query)
   assert q['hotel']==[hotel] and q['date']==['2026-12-10'] and q['nights']==['3']
   if '/rooms/' in path:await expect(page.locator('.bk-live-room')).to_contain_text('Семейный люкс')
   flows.append(path);await c.close()
  await b.close()
 assert not errors,errors
 report={'status':'PASS','static_pages':checked,'booking_entrypoints':flows,'js_errors':errors}
 (ROOT/'docs/booking-entrypoints-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
asyncio.run(main())
