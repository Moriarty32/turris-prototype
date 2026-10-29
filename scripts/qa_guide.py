import asyncio,json
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4173/turris-prototype'

async def main():
 routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))
 articles=[p for p in routes['pages'] if p['template']=='article']
 blogs=[p for p in routes['pages'] if p['template']=='blog']
 for p in articles:
  soup=BeautifulSoup((ROOT/'dist'/p['url'].strip('/')/'index.html').read_text(encoding='utf-8'),'html.parser')
  assert len(soup.select('h1'))==1
  assert len(soup.select('.guide-table tbody tr'))>=3
  assert len(soup.select('[data-guide-check]'))==4
  for link in soup.select('[data-toc-link]'): assert soup.select_one(link['href']),p['url']
  assert json.loads(soup.select_one('script[type="application/ld+json"]').text)['@type']=='BlogPosting'
 errors=[];checks=[]
 async with async_playwright() as playwright:
  browser=await playwright.chromium.launch()
  context=await browser.new_context(viewport={'width':1440,'height':1000},permissions=['clipboard-read','clipboard-write'])
  await context.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
  page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/blog/',wait_until='networkidle')
  assert await page.locator('[data-journal-card]').count()==16
  await page.locator('[data-journal-search]').fill('Большая Садовая')
  assert await page.locator('[data-journal-card]:visible').count()==1
  assert '1' in await page.locator('[data-journal-count]').inner_text()
  await page.locator('[data-journal-reset]').click()
  await page.locator('[data-journal-topic=family]').click()
  assert await page.locator('[data-journal-card]:visible').count()==2
  await page.locator('[data-journal-search]').fill('несуществующее')
  assert await page.locator('[data-journal-empty]').is_visible()
  await page.locator('[data-journal-reset]').click()
  assert await page.locator('[data-journal-card]:visible').count()==6
  await page.goto(BASE+'/blog/business/')
  await page.wait_for_url(BASE+'/blog/business/')
  assert await page.locator('[data-journal-card]').count()==3
  checks.append('Catalogue: full-content search, combined filter, count, empty state, reset and rubric navigation')
  await page.goto(BASE+'/blog/tverskaya-walk/',wait_until='networkidle')
  await page.locator('[data-guide-check="0"]').check()
  await page.locator('[data-guide-check="2"]').check()
  assert '2 из 4' in await page.locator('[data-check-count]').inner_text()
  await page.reload(wait_until='networkidle')
  assert await page.locator('[data-guide-check="2"]').is_checked()
  await page.locator('[data-check-reset]').click()
  assert await page.locator('[data-guide-check]:checked').count()==0
  await page.locator('[data-copy-article]').click()
  assert await page.evaluate('navigator.clipboard.readText()')==BASE+'/blog/tverskaya-walk/'
  await page.evaluate("Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))},configurable:true})")
  await page.locator('[data-copy-article]').click()
  assert 'строки браузера' in await page.locator('[data-copy-status]').inner_text()
  href=await page.locator('#article-route a').get_attribute('href')
  q=parse_qs(urlsplit(href).query)
  assert q['rtt']==['pd'] and 'Тверская Застава' in q['rtext'][0] and 'Большая Садовая' in q['rtext'][0]
  checks.append('Checklist persistence/reset, clipboard success/fallback, route origin and destination')
  await page.set_viewport_size({'width':390,'height':844})
  assert not await page.locator('.guide-toc').evaluate('(e)=>e.open')
  await page.locator('.guide-toc summary').click()
  await page.locator('[data-toc-link][href="#article-checklist"]').click()
  await page.wait_for_timeout(800)
  position=await page.locator('#article-checklist').bounding_box()
  assert 65<=position['y']<=180,position
  await expect(page.locator('[data-toc-link][href="#article-checklist"]')).to_have_attribute('aria-current','true')
  checks.append('Mobile contents disclosure, anchor position below fixed header and active section')
  for width in [320,390,768,1440]:
   await page.set_viewport_size({'width':width,'height':844 if width<900 else 1000})
   for item in articles+blogs:
    await page.goto(BASE+item['url'],wait_until='load')
    await page.evaluate('document.fonts.ready')
    assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),(width,item['url'])
    if item['template']=='article':
     box=await page.locator('.guide-cover img').bounding_box()
     assert box['height']<=(64 if width<=640 else 230),(width,item['url'],box)
     assert await page.locator('#article-summary').is_visible()
  checks.append('All 16 articles and 5 catalogue pages at 320, 390, 768 and 1440 px; no overflow; bounded cover images')
  for width in [390,1440]:
   await page.set_viewport_size({'width':width,'height':844 if width==390 else 1000})
   for slug in ['','tverskaya-walk/','attic-room/']:
    await page.goto(BASE+'/blog/'+slug,wait_until='networkidle')
    # Load below-fold photographs before capturing the whole page.
    await page.locator('img').evaluate_all("els=>els.forEach(e=>e.loading='eager')")
    await page.wait_for_function("[...document.images].every(i=>i.complete)")
    await page.screenshot(path=str(ROOT/'.qa'/f'guide-{slug.strip("/") or "index"}-{width}.png'),full_page=True)
  nojs=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
  plain=await nojs.new_page();await plain.goto(BASE+'/blog/lubyanka-walk/')
  assert await plain.locator('.guide-toc nav').is_visible()
  assert await plain.locator('.guide-table').is_visible()
  assert await plain.locator('#article-sources a').count()>=2
  checks.append('No-JavaScript answer, contents, comparison, checklist and source links remain in HTML')
  assert not errors,errors
  await browser.close()
 report={'status':'PASS','articles':16,'catalogue_pages':5,'widths':[320,390,768,1440],'checks':checks,'js_errors':errors}
 (ROOT/'.qa/guide-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
