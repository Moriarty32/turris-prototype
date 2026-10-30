import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
CASES=[('home','/','.home-booking .btn'),('hotel','/hotels/turris-hotel-tverskaya/','.hd-booking .btn'),('family','/family/','.of-search .btn'),('contacts','/contacts/','.ct-booking .btn'),('booking','/bronirovanie/','.bk-search .btn'),('room','/hotels/turris-hotel-tverskaya/rooms/semeynyy-lyuks/','.hotel-hero .btn'),('article','/blog/choose-area/','.guide-tools a')]
async def main():
 out=[];errors=[]
 shots=Path('.qa/adaptive-heroes');shots.mkdir(exist_ok=True)
 async with async_playwright() as p:
  b=await p.chromium.launch();page=await b.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for w,h in [(1024,600),(1280,720),(1366,768),(1440,900),(1920,1080),(2560,1440),(3840,2160)]:
   await page.set_viewport_size({'width':w,'height':h})
   for name,path,sel in CASES:
    await page.goto(BASE+path,wait_until='domcontentloaded');await page.evaluate('document.fonts.ready');rect=await page.locator(sel).first.bounding_box();bottom=round(rect['y']+rect['height']);assert bottom<=h,(name,w,h,bottom)
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(name,w,h)
    out.append({'page':name,'viewport':[w,h],'cta_bottom':bottom,'content_width':await page.locator('main .wrap').first.evaluate('e=>e.clientWidth')})
    if (w,h) in [(1024,600),(1920,1080)] and name in ['home','hotel','family','article']:
     await page.evaluate('Promise.all([...document.images].filter(i=>i.loading!=="lazy").map(i=>i.decode().catch(()=>{})))');await page.screenshot(path=str(shots/f'{name}-{w}.png'))
  await page.set_viewport_size({'width':1366,'height':768});await page.goto(BASE+'/');await page.locator('.home-booking [name=hotel]').select_option('tagansky');await page.locator('.home-booking [data-dates]').click();await expect(page.locator('#dates-dialog')).to_be_visible();await page.keyboard.press('Escape')
  await page.set_viewport_size({'width':1024,'height':600});await expect(page.locator('.home-booking [name=hotel]')).to_have_value('tagansky');await page.locator('.home-booking [data-guests]').click();await expect(page.locator('#guests-dialog')).to_be_visible();await page.keyboard.press('Escape')
  for name,path,_ in CASES:
   await page.set_viewport_size({'width':1366,'height':768});await page.goto(BASE+path);await page.evaluate("document.documentElement.style.zoom='2'");assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),('zoom',name)
  await b.close()
 assert not errors,errors
 report={'checks':out,'resize_preserves_selected_hotel':True,'date_and_guest_dialogs':'passed','zoom_200_percent':'no horizontal overflow on seven key pages','javascript_errors':errors,'reservation_or_payment_submitted':False}
 Path('docs/adaptive-heroes-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('PASS: 49 desktop first screens, seven zoom checks, booking dialogs and resize state.')
asyncio.run(main())
