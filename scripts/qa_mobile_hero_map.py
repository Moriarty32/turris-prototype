import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4173/turris-prototype'
TILE='<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect width="256" height="256" fill="#e9efec"/><path d="M0 90H256M90 0V256" stroke="white" stroke-width="10"/></svg>'
async def main():
    errors=[];sizes=[]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        c=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU')
        await c.route('https://tile.openstreetmap.org/**',lambda r:r.fulfill(content_type='image/svg+xml',body=TILE))
        page=await c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto(BASE+'/',wait_until='networkidle');await page.wait_for_selector('[data-map-loaded=true]')
        assert await page.locator('[data-hotel-map]').count()==1
        assert not await page.locator('.hero>.hero-visual').is_visible()
        assert await page.locator('.hero [data-hotel-map]').is_visible()
        assert await page.locator('[data-map-select]:visible').count()==4
        assert await page.locator('.hero [name=hotel]').input_value()==''
        assert await page.locator('[data-map-detail]:visible').count()==0
        box=await page.locator('.hero .map-stage').bounding_box()
        assert box['y']+box['height']<=844,box
        await page.screenshot(path=str(ROOT/'.qa/mobile-hero-map-initial.png'))
        for id in ['tverskaya','lubyansky','petrovsky','tagansky']:
            await page.locator('[data-map-select="'+id+'"]').click()
            assert await page.locator('.hero [name=hotel]').input_value()==id
            assert await page.locator('.booking-bottom [name=hotel]').input_value()==id
            assert await page.locator('[data-map-detail="'+id+'"]').is_visible()
        assert 'нет лифта' in await page.locator('[data-map-detail=tagansky]').inner_text()
        await page.locator('[data-map-reset]').click()
        for id,name in [('tverskaya','Тверская'),('lubyansky','Лубянский'),('petrovsky','Петровский'),('tagansky','Таганский')]:
            await page.locator('[data-map-reset]').click()
            await page.locator('.map-pin[title="Туррис '+name+'"]').click()
            assert await page.locator('.hero [name=hotel]').input_value()==id
        await page.locator('[data-map-reset]').click()
        await page.locator('.map-pin[title="Туррис Лубянский"]').focus();await page.keyboard.press('Enter')
        assert await page.locator('.hero [name=hotel]').input_value()=='lubyansky'
        await page.locator('[data-map-detail=lubyansky] [data-map-book-dates]').click()
        assert await page.locator('#dates-dialog').is_visible()
        await page.locator('#dates-form [name=checkin]').fill('2026-12-10');await page.locator('#dates-form [name=checkout]').fill('2026-12-13');await page.locator('#dates-form button[type=submit]').click()
        assert await page.locator('[data-map-select=lubyansky]').get_attribute('aria-pressed')=='true'
        await page.locator('.hero [name=hotel]').select_option('petrovsky')
        assert await page.locator('[data-map-detail=petrovsky]').is_visible()
        await page.locator('.hero [name=hotel]').select_option('')
        assert await page.locator('[data-map-detail]:visible').count()==0
        await page.locator('[data-map-select=lubyansky]').click()
        await page.locator('.hero [data-booking] button[type=submit]').click();await page.wait_for_selector('.bk-live-frame')
        assert 'hotel=lubyansky' in page.url
        assert await page.locator('.bk-live-frame').count()==1
        await page.goto(BASE+'/',wait_until='networkidle')
        assert await page.locator('[data-map-detail=lubyansky]').is_visible(), 'Saved selection must restore'
        await page.set_viewport_size({'width':1440,'height':1000})
        assert await page.locator('.hero>.hero-visual').is_visible()
        assert await page.locator('.hero [data-hotel-map]').count()==0
        await page.locator('[data-hotel-view=map]').click();await page.wait_for_selector('[data-map-loaded=true]')
        assert await page.locator('.map-pin').count()==4
        assert await page.locator('[data-map-detail=lubyansky]').is_visible()
        await page.set_viewport_size({'width':390,'height':844})
        assert await page.locator('.hero [data-hotel-map]').is_visible()
        assert await page.locator('[data-hotel-card]:visible').count()==4
        for width in [320,375,390,430,640,641,900,1440]:
            await page.set_viewport_size({'width':width,'height':900})
            await page.wait_for_timeout(100)
            assert not await page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),width
            assert await page.locator('[data-hotel-map]').count()==1
            sizes.append(width)
        # Map transport failure must not prevent choosing the hotel and dates.
        await c.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
        await page.set_viewport_size({'width':390,'height':844})
        await page.goto(BASE+'/?map-hotel=tagansky#map',wait_until='networkidle')
        await page.wait_for_selector('[data-map-loaded=true]')
        assert await page.locator('.hero [name=hotel]').input_value()=='tagansky'
        assert await page.locator('[data-map-status]').is_visible()
        await page.locator('[data-map-select=tverskaya]').click()
        assert await page.locator('.hero [name=hotel]').input_value()=='tverskaya'
        assert not errors,errors
        await b.close()
    report={'status':'PASS','first_screen_map':box,'widths':sizes,'single_map':True,'selection':'buttons, pointer and keyboard markers, form, persistence and booking verified','resize':'desktop image and explorer restored; mobile map relocated without duplication','fallback':'hotel selection remains usable with tile failure','js_errors':errors}
    (ROOT/'.qa/mobile-hero-map-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
