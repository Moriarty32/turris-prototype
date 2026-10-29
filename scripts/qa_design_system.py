"""Cross-template shell, readability and responsive layout acceptance."""
import asyncio,json
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]; BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
 pages=json.loads((ROOT/'data/routes.json').read_text(encoding='utf-8'))['pages']; signatures=set();errors=[];checks=[]
 for item in pages:
  soup=BeautifulSoup((ROOT/'dist'/item['url'].strip('/')/'index.html').read_text(encoding='utf-8'),'html.parser')
  signatures.add(tuple((a.get('href'),a.get_text(' ',strip=True)) for a in soup.select('.ux-header a')))
 assert len(signatures)==1, len(signatures)
 async with async_playwright() as pw:
  browser=await pw.chromium.launch();context=await browser.new_context(locale='ru-RU')
  await context.route('**/tile.openstreetmap.org/**',lambda r:r.abort())
  page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for width in [320,768,1440]:
   await page.set_viewport_size({'width':width,'height':900})
   for item in pages:
    await page.goto(BASE+item['url'],wait_until='load');await page.evaluate('document.fonts.ready')
    check=await page.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,small:[...document.querySelectorAll('main p,main .btn,main label,footer a')].filter(e=>e.getClientRects().length&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<12).map(e=>({class:e.className,text:e.textContent.trim().slice(0,50),size:getComputedStyle(e).fontSize})),outside:[...document.querySelectorAll('main .btn,main input:not([type=hidden]),main select')].filter(e=>e.getClientRects().length&&(e.getBoundingClientRect().right>innerWidth+1||e.getBoundingClientRect().left< -1)).map(e=>e.className)})''')
    checks.append({'url':item['url'],'width':width,**check})
  for width in [390,1440]:
   await page.set_viewport_size({'width':width,'height':900});await page.goto(BASE+'/',wait_until='networkidle')
   await page.screenshot(path=str(ROOT/f'.qa/system-home-{width}.png'))
   if width==390:await page.locator('.menu-button').click()
   await page.locator('[data-nav-section=hotels]>summary').click()
   assert await page.locator('.ux-mega').first.is_visible()
   await page.wait_for_timeout(250)
   await page.screenshot(path=str(ROOT/f'.qa/system-menu-{width}.png'))
   if width==390:assert await page.locator('main').evaluate('(e)=>e.inert')
   await page.keyboard.press('Escape');assert not await page.locator('.ux-mega').first.is_visible()
   assert not await page.locator('main').evaluate('(e)=>e.inert')
  await page.set_viewport_size({'width':390,'height':900})
  await page.locator('.menu-button').click();await page.keyboard.press('Tab')
  assert await page.evaluate('document.activeElement.closest(".ux-header")!==null')
  await page.set_viewport_size({'width':1440,'height':900})
  assert not await page.locator('main').evaluate('(e)=>e.inert')
  await page.emulate_media(reduced_motion='reduce')
  assert await page.locator('.header-booking').evaluate('e=>getComputedStyle(e).transitionDuration')=='0s'
  plain=await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
  raw=await plain.new_page();await raw.goto(BASE+'/')
  assert await raw.locator('.nav').is_visible()
  await raw.locator('[data-nav-section=offers]>summary').click()
  assert await raw.locator('[data-nav-section=offers] a[href$="/family/"]').is_visible()
  await plain.close()
  await context.close();await browser.close()
 report={'pages':len(pages),'shell_variants':len(signatures),'checks':len(checks),'overflow':[x for x in checks if x['overflow'] or x['outside']],'small_text':[x for x in checks if x['small']],'js_errors':errors}
 (ROOT/'.qa/design-system-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
 assert not report['overflow'] and not report['small_text'] and not errors
asyncio.run(main())
