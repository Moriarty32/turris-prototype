"""Contacts reference acceptance: map, calls, clipboard, form and responsive layout."""
import asyncio,json,sys
from pathlib import Path
from urllib.parse import urlsplit,unquote
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'data'))
from hotel_details import DETAILS
BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 errors=[];requests=[];checks=[];densities=[]
 delivery=json.loads((ROOT/'data/image-delivery.json').read_text(encoding='utf-8'))
 dimensions={v['file']:(v['width'],v['height']) for d in delivery.values() for v in d['variants']}
 async with async_playwright() as p:
  b=await p.chromium.launch();c=await b.new_context(viewport={'width':1440,'height':1000},device_scale_factor=2,permissions=['clipboard-read','clipboard-write'])
  await c.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
  page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append((r.method,r.url)))
  for width in [320,390,640,768,901,1024,1440]:
   await page.set_viewport_size({'width':width,'height':844 if width<=640 else 1000})
   await page.goto(BASE+'/contacts/',wait_until='networkidle');await page.evaluate('document.fonts.ready')
   assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),width
   box=await page.locator('.ct-booking .btn').bounding_box();assert box['y']+box['height']<(844 if width<=640 else 1000),(width,box)
   await page.locator('.ct-map').scroll_into_view_if_needed()
   await expect(page.locator('.map-pin')).to_have_count(4)
   for hid,d in DETAILS.items():
    await page.locator('[data-map-select='+hid+']').click()
    await expect(page.locator('[data-map-detail]:visible')).to_have_count(1)
    await expect(page.locator('[data-map-select='+hid+']')).to_have_attribute('aria-expanded','true')
    assert d['admin'] in await page.locator('[data-map-detail='+hid+']').inner_text()
    await expect(page.locator('[data-contact-form] [name=hotel]')).to_have_value(hid)
   await page.locator('img[data-asset]').evaluate_all("async els=>{await Promise.all(els.map(async i=>{i.loading='eager';await i.decode()}))}")
   rows=await page.locator('img[data-asset]').evaluate_all("els=>els.map(i=>{const b=i.getBoundingClientRect();return {src:i.currentSrc,w:b.width,h:b.height}}).filter(r=>r.w&&r.h)")
   for row in rows:
    sw,sh=dimensions[unquote(urlsplit(row['src']).path).split('/assets/')[1]]
    density=min(sw/row['w'],sh/row['h']);densities.append(density);assert density>=1.95,(width,row,density)
   if width in [390,1440]:
    await page.locator('[data-map-select=tverskaya]').click()
    await page.locator('[data-map-reset]').click()
    await page.evaluate("scrollTo({top:0,behavior:'instant'})")
    await page.screenshot(path=str(ROOT/'.qa'/f'contacts-{width}.png'),full_page=True)
    await page.screenshot(path=str(ROOT/'.qa'/f'contacts-first-{width}.png'))
   checks.append({'width':width,'cta_visible':True,'map_selection':'passed','overflow':False})
  assert await page.locator('.nav-direct.current').inner_text()=='Контакты'
  await page.locator('.nav summary').first.focus();await page.keyboard.press('Enter');await expect(page.locator('.drop').first).to_be_visible();await page.keyboard.press('Escape')
  for hid,d in DETAILS.items():
   card=page.locator('#contact-'+hid)
   phone=''.join(c for c in d['admin'] if c.isdigit() or c=='+')
   assert await card.locator('.ct-admin-phone').get_attribute('href')=='tel:'+phone
   assert 'rtext=~' in await card.locator('.ct-card-actions .ct-blue').get_attribute('href')
  await page.locator('.ct-booking [data-contact-copy]').click()
  assert await page.evaluate('navigator.clipboard.readText()')=='m-br-1@turris-management.ru'
  await page.locator('#contact-tagansky [data-contact-copy]').click()
  assert 'Серебрянический' in await page.evaluate('navigator.clipboard.readText()')
  await page.evaluate("Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))},configurable:true})")
  await page.locator('#contact-tverskaya [data-contact-copy]').click()
  assert 'Скопируйте вручную' in await page.locator('[data-contact-copy-status]').inner_text()
  form=page.locator('[data-contact-form]')
  await form.locator('[name=hotel]').select_option('lubyansky');await expect(page.locator('[data-map-select=lubyansky]')).to_have_attribute('aria-pressed','true')
  await form.locator('[type=submit]').click();await expect(page.locator('.ct-error')).to_be_visible();assert await form.is_visible()
  await form.locator('[name=contact]').fill('invalid');await form.locator('[name=message]').fill('Тестовый вопрос об условиях приезда.');await form.locator('[name=consent]').check();await form.locator('[type=submit]').click()
  assert await form.locator('[name=contact]').evaluate('(e)=>!e.validity.valid')
  await form.locator('[name=contact]').fill('demo@example.com');await form.locator('[name=topic]').select_option(label='Приезд и заселение');await form.locator('[type=submit]').click()
  await expect(page.locator('[data-contact-result]')).to_be_visible();assert 'не отправлено' in await page.locator('[data-contact-result]').inner_text()
  assert 'Лубянский' in await page.locator('[data-contact-result-text]').inner_text()
  assert await page.locator('[data-contact-result]').evaluate('(e)=>e===document.activeElement')
  await page.locator('[data-contact-again]').click();await expect(form).to_be_visible()
  assert await form.locator('[name=message]').input_value()=='Тестовый вопрос об условиях приезда.'
  assert not any(method!='GET' for method,u in requests),requests
  assert not any('demo%40example' in u or 'demo@example' in u for method,u in requests)
  assert 'demo@example.com' not in await page.evaluate('JSON.stringify(sessionStorage)+JSON.stringify(localStorage)')
  for width in [390,1440,390]:
   await page.set_viewport_size({'width':width,'height':844});await expect(page.locator('[data-map-select]')).to_have_count(4);await expect(page.locator('.leaflet-container')).to_have_count(1)
  await page.locator('.menu-button').click();await expect(page.locator('.nav-direct.current')).to_be_visible();await page.keyboard.press('Escape')
  await page.goto(BASE+'/contacts/?map-hotel=petrovsky#map',wait_until='networkidle');await expect(page.locator('[data-contact-form] [name=hotel]')).to_have_value('petrovsky')
  nojs=await b.new_context(java_script_enabled=False,viewport={'width':390,'height':844});plain=await nojs.new_page();await plain.goto(BASE+'/contacts/')
  assert await plain.locator('[data-map-detail]:visible').count()==4
  assert await plain.locator('.ct-card').count()==4
  assert await plain.locator('[data-contact-form] [name=contact]').is_disabled()
  await b.close()
 assert not errors,errors
 report={'status':'PASS','responsive':checks,'minimum_image_density':round(min(densities),2),'functions':['4 direct phones and sourced routes','map/form selection and query parameter','one map across breakpoints','clipboard and permission failure','form validation, explicit unsent result, keyboard focus and edit','no network submission or personal-data storage','no-JavaScript contacts, routes and disabled form','desktop and mobile navigation'],'js_errors':errors}
 (ROOT/'.qa/contacts-reference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
