"""Check readable button labels and selected/hover/focus/active colors; never submits bookings."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright,expect
BASE='http://127.0.0.1:4173/turris-prototype'
CONTRAST_JS=r"""() => {
 const parse=s=>{const v=s.match(/[\d.]+/g);return v?[+v[0],+v[1],+v[2],v[3]===undefined?1:+v[3]]:null;};
 const mix=(f,b)=>[0,1,2].map(i=>f[i]*f[3]+b[i]*(1-f[3]));
 const lum=c=>c.map(n=>{n/=255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4;}).reduce((s,n,i)=>s+n*[.2126,.7152,.0722][i],0);
 const ratio=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
 const out=[];
 for(const action of document.querySelectorAll('button,a.btn,a.text-link,[role=button],[role=option],summary')){
  if(window.__contrastProbe&&action!==window.__contrastProbe)continue;
  if(!action.getClientRects().length||action.matches(':disabled')||action.closest('[hidden],[inert],[aria-hidden=true],fieldset:disabled,.hero-carousel'))continue;
  const walk=document.createTreeWalker(action,NodeFilter.SHOW_TEXT);let node;
  while(node=walk.nextNode()){
   const el=node.parentElement;if(!node.textContent.trim()||el.closest('button,a.btn,a.text-link,[role=button],[role=option],summary')!==action)continue;
   const range=document.createRange();range.selectNode(node);if(!range.getBoundingClientRect().width)continue;
   let chain=[],unknown=false,hidden=false;
   for(let at=el;at;at=at.parentElement){const s=getComputedStyle(at);if(s.visibility==='hidden'||+s.opacity<.8){hidden=true;break;}const bg=parse(s.backgroundColor);if(s.backgroundImage!=='none'){unknown=true;break;}if(bg){chain.push(bg);if(bg[3]===1)break;}}
   if(hidden||unknown)continue;let bg=[255,255,255];for(const color of chain.reverse())bg=mix(color,bg);
   const style=getComputedStyle(el),fg=parse(style.color);if(!fg)continue;const contrast=ratio(mix(fg,bg),bg),size=parseFloat(style.fontSize),weight=parseInt(style.fontWeight)||400,minimum=size>=24||(size>=18.66&&weight>=700)?3:4.5;
   if(contrast<minimum-.05)out.push({element:action.tagName.toLowerCase()+'.'+String(action.className),text:node.textContent.trim().slice(0,80),ratio:+contrast.toFixed(2),minimum,color:style.color,background:bg.map(Math.round),pressed:action.getAttribute('aria-pressed'),current:action.getAttribute('aria-current')});
  }
 }
 return out;
}"""

async def main():
 routes=json.loads(Path('data/routes.json').read_text(encoding='utf8'))['pages'];examples={}
 for route in routes:examples.setdefault(route['template'],route)
 examples['article-with-related-offer']=next(route for route in routes if route['id']=='article_6')
 findings=[];errors=[];layouts=0;pseudo_checks=0;state_checks=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch();context=await browser.new_context(reduced_motion='reduce');page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for width,height in [(390,844),(1366,900)]:
   await page.set_viewport_size({'width':width,'height':height})
   for route in routes:
    await page.goto(BASE+route['url'],wait_until='domcontentloaded');await page.evaluate('document.fonts.ready');bad=await page.evaluate(CONTRAST_JS);layouts+=1
    if bad:findings.append({'page':route['id'],'width':width,'state':'normal','items':bad})
   print('Checked labels:',layouts,'layouts',flush=True)
  await page.set_viewport_size({'width':1366,'height':900});cdp=await context.new_cdp_session(page);await cdp.send('DOM.enable');await cdp.send('CSS.enable')
  for route in examples.values():
   await page.goto(BASE+route['url'],wait_until='domcontentloaded');await page.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important}')
   doc=await cdp.send('DOM.getDocument');seen=set()
   for element in await page.locator('button,a.btn,a.text-link,summary').all():
    if not await element.is_visible() or not await element.is_enabled():continue
    key=await element.evaluate("e=>[e.tagName,e.className,e.getAttribute('aria-pressed'),e.getAttribute('aria-current'),e.closest('section,form,nav,header')?.className].join('|')")
    if key in seen:continue
    seen.add(key);await element.evaluate("e=>{e.setAttribute('data-contrast-probe','');window.__contrastProbe=e}")
    node=await cdp.send('DOM.querySelector',{'nodeId':doc['root']['nodeId'],'selector':'[data-contrast-probe]'})
    for state in ['hover','focus-visible','active']:
     await cdp.send('CSS.forcePseudoState',{'nodeId':node['nodeId'],'forcedPseudoClasses':[state]});bad=await page.evaluate(CONTRAST_JS);pseudo_checks+=1
     if bad:findings.append({'page':route['id'],'state':state,'items':bad})
    await cdp.send('CSS.forcePseudoState',{'nodeId':node['nodeId'],'forcedPseudoClasses':[]});await element.evaluate("e=>{e.removeAttribute('data-contrast-probe');window.__contrastProbe=null}")
  # Actual state changes verify that selected backgrounds retain legible labels.
  await page.goto(BASE+'/hotels/');await page.locator('[data-hotel-view=map]').click();bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'selected-map-view','items':bad})
  await page.locator('[data-hotel-view=cards]').click();bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'selected-card-view','items':bad})
  await expect(page.locator('[data-hotel-view=cards]')).to_have_attribute('aria-pressed','true');await page.locator('.view-switch').screenshot(path='.qa/contrast-view-switch.png');state_checks.append('Both selected hotel views')
  await page.goto(BASE+'/blog/');await page.locator('.jr-pagination nav button').nth(1).click();await expect(page.locator('.jr-pagination nav [aria-current=page]')).to_have_text('2');bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'selected-pagination-page','items':bad})
  state_checks.append('Guide pagination after selecting another page')
  await context.close();context=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');page=await context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  await page.goto(BASE+'/');await expect(page.locator('[data-hotel-map]')).to_have_attribute('data-map-loaded','true',timeout=15000);await page.locator('.map-expand').click();await page.locator('.map-move').click();await expect(page.locator('.map-move')).to_have_attribute('aria-pressed','true');bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'active-touch-map-movement','items':bad})
  await page.keyboard.press('Escape');await page.locator('.home-booking [data-dates]').click();await page.locator('[data-month-next]').click();days=page.locator('.calendar-day:not(:disabled)');await days.nth(1).click();await days.nth(3).click();bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'selected-calendar-range','items':bad})
  await page.keyboard.press('Escape');await page.locator('.home-booking [data-guests]').click();await page.locator('[data-count=children][data-change="1"]').click();await page.locator('#guests-dialog .ui-select-trigger').click();bad=await page.evaluate(CONTRAST_JS)
  if bad:findings.append({'state':'guest-age-options','items':bad})
  state_checks+=['Active touch-map movement button','Selected calendar dates and guest-age options'];await context.close();await browser.close()
 report={'layouts_checked':layouts,'pseudo_states_checked':pseudo_checks,'interactive_states_checked':state_checks,'findings':findings,'javascript_errors':errors,'reservation_payment_or_lead_submitted':False,'scope':'Enabled text actions on resolved CSS backgrounds; image overlays are inspected separately.'}
 Path('docs/button-contrast-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2));assert not findings and not errors
asyncio.run(main())
