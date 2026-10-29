"""Compact layouts and shared selection-state regressions."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4173/turris-prototype'
async def main():
    results=[];errors=[]
    async with async_playwright() as p:
        b=await p.chromium.launch();c=await b.new_context(viewport={'width':1440,'height':1000})
        await c.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
        page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto(BASE+'/',wait_until='networkidle')
        cards=await page.locator('[data-hotel-card]').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})')
        assert len(set(round(x['y']) for x in cards))==1, cards
        assert all(.75<x['width']/x['height']<1.25 for x in cards),cards
        assert not await page.locator('[data-explorer-panel=map]').is_visible()
        assert await page.locator('.booking-bottom [name=hotel]').is_visible()
        await page.locator('[data-booking] [name=hotel]').first.select_option('lubyansky')
        assert await page.locator('.booking-bottom [name=hotel]').input_value()=='lubyansky'
        await page.locator('[data-dates]').first.click()
        await page.locator('#dates-form [name=checkin]').fill('2026-12-10');await page.locator('#dates-form [name=checkout]').fill('2026-12-13')
        await page.locator('#dates-form button[type=submit]').click()
        assert await page.locator('[data-booking] [name=hotel]').first.input_value()=='lubyansky'
        await page.locator('.booking-bottom [name=hotel]').select_option('tagansky')
        await page.locator('.booking-bottom [data-guests]').click();await page.locator('[data-save-guests]').click()
        assert await page.locator('[data-booking] [name=hotel]').first.input_value()=='tagansky'
        await page.locator('[data-hotel-view=map]').click();await page.wait_for_selector('[data-map-loaded=true]')
        for _ in range(2):
            await page.locator('[data-hotel-view=cards]').click()
            assert not await page.locator('[data-explorer-panel=map]').is_visible()
            await page.locator('[data-show-hotel-map=petrovsky]').click()
            assert await page.locator('[data-explorer-panel=map]').is_visible()
            assert await page.locator('[data-map-detail=petrovsky]').is_visible()
        await page.locator('[data-hotel-view=cards]').click()
        await page.locator('[data-compare-hotels]').click();await page.wait_for_url('**/hotels/#comparison')
        assert await page.locator('#comparison table').is_visible()
        await page.locator('[data-hotel-filter]').select_option('longstay')
        await page.locator('[data-reset-hotels]').click()
        assert await page.locator('[data-hotel-card]:not([hidden])').count()==4
        assert not await page.locator('[data-reset-hotels]').is_visible()
        # A preset hotel must not override an explicit new choice when the date dialog saves.
        await page.goto(BASE+'/hotels/turris-hotel-tverskaya/',wait_until='networkidle')
        await page.locator('[data-booking] [name=hotel]').first.select_option('petrovsky')
        await page.locator('[data-dates]').first.click();await page.locator('#dates-form button[type=submit]').click()
        assert await page.locator('[data-booking] [name=hotel]').first.input_value()=='petrovsky'
        assert await page.locator('.booking-bottom [name=hotel]').input_value()=='petrovsky'
        for width in [320,390,640,768,900,901,1024,1150,1151,1280,1440]:
            await page.set_viewport_size({'width':width,'height':900})
            for path in ['/','/blog/attic-room/','/groups/','/bronirovanie/']:
                await page.goto(BASE+path,wait_until='networkidle')
                assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),(width,path)
            results.append({'width':width,'pages':4,'overflow':False})
        await page.set_viewport_size({'width':1440,'height':1000});await page.goto(BASE+'/',wait_until='networkidle')
        await page.screenshot(path=str(ROOT/'.qa/compact-home-desktop.png'),full_page=True)
        height=await page.evaluate('document.documentElement.scrollHeight')
        await page.set_viewport_size({'width':390,'height':844});await page.goto(BASE+'/',wait_until='networkidle')
        await page.screenshot(path=str(ROOT/'.qa/compact-home-mobile.png'),full_page=True)
        await b.close()
    assert not errors,errors
    report={'status':'PASS','cards':cards,'desktop_home_height':height,'responsive':results,'forms':'hotel persists across date/guest changes and synchronizes upper/lower forms','explorer':'cards/map mutually exclusive; repeated switching, selected hotel and comparison anchor verified','catalog':'reset filter works','js_errors':errors}
    (ROOT/'.qa/compact-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
