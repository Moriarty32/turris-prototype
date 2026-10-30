"""Compare labeled inputs and adjacent action heights/bottom edges across all routes."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
JS='''()=>{
 const out=[],vis=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
 const control=e=>e.matches('input:not([type=hidden]),button,select:not(.ui-select-native)')?e:[...e.querySelectorAll('.ui-select-trigger,input:not([type=hidden]),select:not(.ui-select-native),button.select-button')].filter(vis).at(-1);
 for(const parent of document.querySelectorAll('main :is([data-booking],.catalog-tools,.jr-filters,.form-grid,.ct-form-grid,.search-form,.of-search-grid,.bk-fields)')) {
  const cells=[...parent.querySelectorAll(':scope > *')].filter(e=>vis(e)&&e.matches('label,.field,.btn,button,.of-inline-counter')).map(e=>({outer:e,control:control(e)})).filter(x=>x.control&&vis(x.control));
  for(let i=0;i<cells.length;i++)for(let j=i+1;j<cells.length;j++){
   const x=cells[i],y=cells[j],a=x.control.getBoundingClientRect(),b=y.control.getBoundingClientRect(),oa=x.outer.getBoundingClientRect(),ob=y.outer.getBoundingClientRect();
   const sideBySide=Math.min(oa.right,ob.right)-Math.max(oa.left,ob.left)<2;
   const rowOverlap=Math.min(oa.bottom,ob.bottom)-Math.max(oa.top,ob.top);
   if(sideBySide&&rowOverlap>Math.min(a.height,b.height)*.6&&(Math.abs(a.bottom-b.bottom)>2||Math.abs(a.height-b.height)>2))out.push({container:parent.className,one:x.control.className,two:y.control.className,bottomDelta:Math.round(a.bottom-b.bottom),heights:[a.height,b.height]});
  }
 }
 return out;
}'''
async def navigate(page,url):
 for attempt in range(3):
  try:
   await page.goto(url,wait_until='domcontentloaded');return
  except Exception as error:
   if attempt==2 or not any(code in str(error) for code in ['ERR_CONNECTION_REFUSED','ERR_NETWORK_CHANGED']):raise
   await page.wait_for_timeout(300)
async def main():
 routes=json.loads(Path('data/routes.json').read_text(encoding='utf8'))['pages'];cases={}
 for r in routes:cases[r['id']]=r
 out=[];errors=[];checked=0
 async with async_playwright() as p:
  b=await p.chromium.launch();page=await b.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for w,h in [(320,568),(390,844),(768,1024),(1024,768),(1366,900),(1920,1080)]:
   await page.set_viewport_size({'width':w,'height':h})
   for r in cases.values():
    await navigate(page,'http://127.0.0.1:4173/turris-prototype'+r['url']);await page.evaluate('document.fonts.ready');await page.wait_for_timeout(70)
    if r['id']=='hotels':await page.locator('[data-hotel-filter]').select_option('beds')
    findings=await page.evaluate(JS);checked+=1
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(r['id'],w)
    if findings:out.append({'page':r['id'],'width':w,'findings':findings})
   print('Checked',w,'px:',checked,'layouts',flush=True)
  await b.close()
 report={'layouts_checked':checked,'alignment_tolerance_px':2,'findings':out,'javascript_errors':errors,'reservation_or_lead_submitted':False};Path('docs/control-alignment-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2));assert not out and not errors
asyncio.run(main())
