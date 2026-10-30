"""Audit spacing before and after content actions across every route; excludes form control groups."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
JS='''() => {
 const visible=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
 const out=[];
 for(const action of document.querySelectorAll('main :is(.btn,.text-link)')) {
  if(!visible(action)||action.closest('form,.map-toolbar,.hero-carousel,.hotel-tabs,.of-tabs,.ar-toc,.guide-tools,.jr-filters')) continue;
  let group=action,previous=action.previousElementSibling;
  if(!previous && action.parentElement.children.length && action.parentElement.matches('[class*=actions],[class*=action],.hd-room-price,.bk-card-actions,.cta-actions')){group=action.parentElement;previous=group.previousElementSibling;}
  if(!previous||!visible(previous)||!previous.textContent.trim()||previous.matches('a,button,svg,img,label,form'))continue;
  const a=group.getBoundingClientRect(),t=previous.getBoundingClientRect();
  if(Math.min(a.right,t.right)-Math.max(a.left,t.left)<16||a.top<t.top)continue;
  const gap=Math.round((a.top-t.bottom)*10)/10;
  if(gap<15.5)out.push({parent:action.parentElement.className,previous:previous.tagName+'.'+previous.className,action:action.textContent.trim().slice(0,60),gap});
 }
 for(const action of document.querySelectorAll('main :is(.btn,.text-link)')) {
  if(!visible(action)||action.closest('form,.map-toolbar,.hero-carousel,.hotel-tabs,.of-tabs,.ar-toc,.guide-tools,.jr-filters'))continue;
  const next=action.nextElementSibling;
  if(!next||!visible(next)||!next.textContent.trim()||next.matches('a,button,svg,img,label,form'))continue;
  const a=action.getBoundingClientRect(),t=next.getBoundingClientRect();
  if(Math.min(a.right,t.right)-Math.max(a.left,t.left)<16||t.top<a.top)continue;
  const gap=Math.round((t.top-a.bottom)*10)/10;
  if(gap<15.5)out.push({parent:action.parentElement.className,following:next.tagName+'.'+next.className,action:action.textContent.trim().slice(0,60),gap});
 }
 return out;
}'''
async def main():
 routes=json.loads(Path('data/routes.json').read_text(encoding='utf8'))['pages'];cases={}
 for r in routes:cases[r['id']]=r
 result=[];checked=0;errors=[]
 async with async_playwright() as p:
  b=await p.chromium.launch();page=await b.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for width,height in [(320,568),(390,844),(1366,900)]:
   await page.set_viewport_size({'width':width,'height':height})
   for r in cases.values():
    await page.goto('http://127.0.0.1:4173/turris-prototype'+r['url'],wait_until='domcontentloaded');await page.evaluate('document.fonts.ready');findings=await page.evaluate(JS)
    checked+=1
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(r['url'],width)
    if findings:result.append({'route':r['url'],'viewport':width,'findings':findings})
  await b.close()
 report={'layouts_checked':checked,'minimum_content_to_action_gap':16,'findings':result,'javascript_errors':errors,'reservation_or_lead_submitted':False};Path('docs/spacing-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2));assert not result and not errors
asyncio.run(main())
