import asyncio,json,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from PIL import Image
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True)
BASE='http://127.0.0.1:4173/turris-prototype';DIST=ROOT/'dist'
async def main():
 problems=[];pages=list(DIST.rglob('index.html'))
 for f in pages:
  soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
  if len(soup.select('h1'))!=1:problems.append([str(f),'h1 count'])
  if not soup.select_one('meta[name="robots"][content="noindex,nofollow"]'):problems.append([str(f),'noindex'])
  for tag,attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
   for el in soup.select(f'{tag}[{attr}]'):
    u=el[attr]
    if u.startswith('/turris-prototype/'):
     path=unquote(urlsplit(u).path).removeprefix('/turris-prototype/')
     dest=DIST/path
     if dest.is_dir():dest=dest/'index.html'
     if not dest.exists():problems.append([str(f),u])
 for f in ['hero-room-v2','family-room','work-stay','moscow-guide']:
  assert Image.open(ROOT/'assets'/f'{f}.png').size==(1536,1024)
 assert not problems,problems[:10]
 errors=[];observations=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  desktop=await browser.new_context(viewport={'width':1440,'height':1000},locale='ru-RU')
  page=await desktop.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
  await page.goto(BASE+'/',wait_until='networkidle')
  await page.screenshot(path=str(OUT/'home-desktop.png'),full_page=True)
  await page.screenshot(path=str(OUT/'home-first-screen.png'))
  observations.append({'desktop_main_cta_y':await page.locator('[data-booking] .btn').first.bounding_box()})
  await page.locator('[data-dates]').first.click()
  await page.locator('#dates-form [name=checkin]').fill('2026-12-10');await page.locator('#dates-form [name=checkout]').fill('2026-12-13')
  await page.locator('#dates-form button[type=submit]').click()
  await page.locator('[data-guests]').first.click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('[data-age="0"]').select_option('7');await page.locator('[data-save-guests]').click()
  await page.locator('[data-booking] select[name=hotel]').first.select_option('lubyansky')
  await page.locator('[data-booking] button[type=submit]').first.click()
  await page.wait_for_url('**/bronirovanie/**');await page.wait_for_selector('#booking-results .room-card')
  assert await page.locator('#booking-results .room-card').count()==7
  assert '7' in await page.locator('.results-summary').inner_text()
  await page.screenshot(path=str(OUT/'booking-desktop.png'),full_page=True)
  observations.append({'booking':'dates,2adults,child7 retained;7Lubyansky categories'})
  data=json.loads((DIST/'site-data.json').read_text(encoding='utf-8'))
  room=next(x for x in data['pages'] if x['type']=='room' and 'semeynyy' in x['url'])
  await page.goto(BASE+room['url'],wait_until='networkidle');await page.locator('[data-booking] button[type=submit]').click();await page.wait_for_selector('#booking-results .room-card')
  assert await page.locator('#booking-results .room-card').count()==1
  assert room['id'] in page.url
  observations.append({'room_context':'family suite preserved'})
  await page.goto(BASE+'/groups/',wait_until='networkidle')
  await page.locator('[name=arrival]').fill('2026-12-10');await page.locator('[name=departure]').fill('2026-12-13');await page.locator('[data-next-step]').click();await page.locator('[name=name]').fill('Демонстрация');await page.locator('[name=email]').fill('demo@example.com');await page.locator('[name=consent]').check();await page.locator('[data-lead] button[type=submit]').click();await page.wait_for_selector('.form-success');assert 'не отправлена' in await page.locator('.form-success').inner_text();observations.append({'group_form':'two steps and explicit unsent success'})
  await page.screenshot(path=str(OUT/'groups-desktop.png'),full_page=True)
  await page.goto(BASE+'/blog/',wait_until='networkidle');await page.locator('[data-rubric-filter=family]').click();assert await page.locator('[data-article]:visible').count()==2;await page.locator('[data-blog-search]').fill('несуществующий');assert await page.locator('[data-blog-empty]').is_visible();observations.append({'blog':'rubric and empty search work'})
  await page.goto(BASE+'/search/?q=мансарда',wait_until='networkidle');await page.wait_for_selector('.search-result');observations.append({'search_results':await page.locator('.search-result').count()})
  representatives={}
  for row in data['pages']:representatives.setdefault(row['type'],row)
  for kind,row in representatives.items():
   response=await page.goto(BASE+row['url'],wait_until='domcontentloaded');assert response.status==200
   assert await page.locator('h1').count()==1
   overflow=await page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   assert not overflow,('desktop overflow',row['url'])
  mobile=await browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,locale='ru-RU')
  m=await mobile.new_page();m.on('pageerror',lambda err:errors.append(str(err)))
  await m.goto(BASE+'/',wait_until='networkidle');await m.screenshot(path=str(OUT/'home-mobile.png'),full_page=True);await m.screenshot(path=str(OUT/'home-mobile-first-screen.png'))
  box=await m.locator('[data-booking] .btn').first.bounding_box();assert box['y']+box['height']<844,box
  await m.locator('.menu-button').click();assert await m.locator('.nav').is_visible();await m.locator('.nav summary').filter(has_text='Отели').click();assert await m.locator('.nav .drop').first.is_visible();await m.keyboard.press('Escape');assert not await m.locator('.nav').is_visible()
  for kind,row in representatives.items():
   await m.goto(BASE+row['url'],wait_until='domcontentloaded');assert not await m.evaluate('document.documentElement.scrollWidth>innerWidth+1'),('mobile overflow',row['url'])
  await m.goto(BASE+'/blog/attic-room/',wait_until='networkidle');await m.screenshot(path=str(OUT/'article-mobile.png'),full_page=True)
  await m.set_viewport_size({'width':320,'height':800});await m.goto(BASE+'/',wait_until='networkidle');assert not await m.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'320px home overflow'
  await browser.close()
 assert not errors,errors
 report={'status':'PASS','static_pages':len(pages),'templates_browser_checked':len(representatives),'generated_dimensions':'4x1536x1024','local_links':'all resolved','js_errors':errors,'observations':observations}
 (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
