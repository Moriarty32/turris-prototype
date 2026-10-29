"""Browser regressions for the premium UI. Public tile servers are never crawled."""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.qa'
BASE = 'http://127.0.0.1:4173/turris-prototype'
TILE = '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><rect width="256" height="256" fill="#e8eeeb"/><path d="M0 80H256M80 0V256" stroke="white" stroke-width="12"/></svg>'

async def main():
    errors, checks = [], []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width':1440,'height':1000}, locale='ru-RU')
        await ctx.route('https://tile.openstreetmap.org/**', lambda r: r.fulfill(content_type='image/svg+xml', body=TILE))
        page = await ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.goto(BASE + '/', wait_until='networkidle')
        assert await page.locator('.leaflet-container').count() == 0, 'Map should load only near viewport'
        await page.locator('[data-show-hotel-map="tagansky"]').click()
        await page.wait_for_selector('[data-map-loaded="true"]')
        assert await page.locator('.map-pin').count() == 4
        assert await page.locator('[data-map-detail="tagansky"]').is_visible()
        assert 'нет лифта' in await page.locator('[data-map-detail="tagansky"]').inner_text()
        assert await page.locator('.map-pin.selected').get_attribute('title') == 'Туррис Таганский'
        await page.locator('.map-pin[title="Туррис Петровский"]').focus()
        await page.keyboard.press('Enter')
        assert await page.locator('[data-map-detail="petrovsky"]').is_visible()
        await page.locator('[data-map-reset]').click()
        assert await page.locator('.map-pin').count() == 4
        route = await page.locator('[data-map-detail="petrovsky"] a[target="_blank"]').get_attribute('href')
        assert '55.768313,37.614639' in route
        assert await page.locator('.leaflet-control-attribution').is_visible()
        await page.locator('.hotel-map').screenshot(path=str(OUT/'map-desktop-fixture.png'))
        checks.append('4 sourced markers; card -> map -> hotel detail; keyboard marker; route; reset; attribution')
        await page.goto(BASE + '/hotels/', wait_until='networkidle')
        await page.locator('[data-hotel-filter]').select_option('longstay')
        await page.locator('[data-hotel-view=map]').click()
        await page.wait_for_selector('[data-map-loaded="true"]')
        assert await page.locator('.map-pin').count() == 1
        assert await page.locator('[data-map-select]:visible').count() == 1
        assert await page.locator('[data-map-detail="petrovsky"]').is_visible()
        await page.locator('[data-hotel-filter]').select_option('family')
        assert await page.locator('.map-pin').count() == 2
        assert await page.locator('[data-hotel-card]:not([hidden])').count() == 2
        await page.locator('[data-hotel-filter]').select_option('all')
        assert await page.locator('.map-pin').count() == 4
        checks.append('Catalogue purpose filter synchronizes cards, choices and markers before/after map initialization')
        await page.goto(BASE + '/about/', wait_until='networkidle')
        await page.locator('[data-show-hotel-map="lubyansky"]').click()
        await page.wait_for_url('**/?map-hotel=lubyansky#map')
        assert await page.locator('[data-map-detail="lubyansky"]').is_visible()
        checks.append('Cross-page card link opens selected hotel on the home map')
        # Header keyboard, active section and close behavior.
        await page.goto(BASE + '/blog/attic-room/', wait_until='networkidle')
        assert 'current' in await page.locator('[data-nav-section=guide]').get_attribute('class')
        await page.locator('.nav summary').first.focus(); await page.keyboard.press('Enter')
        assert await page.locator('.drop').first.is_visible()
        await page.keyboard.press('Escape')
        assert not await page.locator('.drop').first.is_visible()
        checks.append('Active navigation, native keyboard disclosure and Escape')
        # All 109 generated pages must opt into the same new design and script.
        for path in (ROOT/'dist').rglob('index.html'):
            html = path.read_text(encoding='utf-8')
            assert '/assets/premium.css' in html and '/assets/experience.js' in html
            # Hotel and booking screens use compact headers; every template
            # must still retain the primary navigation and skip-to-content link.
            assert 'id="main-nav"' in html and 'href="#main"' in html
        mobile = await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ru-RU')
        await mobile.route('https://tile.openstreetmap.org/**', lambda r: r.fulfill(content_type='image/svg+xml',body=TILE))
        m = await mobile.new_page(); m.on('pageerror', lambda e: errors.append(str(e)))
        await m.goto(BASE + '/?map-hotel=tagansky#map', wait_until='networkidle')
        await m.wait_for_selector('[data-map-loaded="true"]')
        assert await m.locator('.map-pin').count() == 4
        await m.locator('.map-move').click()
        assert await m.locator('.map-move').get_attribute('aria-pressed') == 'true'
        await m.locator('.map-move').click()
        assert await m.locator('.map-move').get_attribute('aria-pressed') == 'false'
        await m.locator('[data-map-select="tverskaya"]').click()
        assert await m.locator('[data-map-detail="tverskaya"]').is_visible()
        assert not await m.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
        await m.locator('.hotel-map').screenshot(path=str(OUT/'map-mobile-fixture.png'))
        await m.locator('.menu-button').click()
        await m.locator('.nav summary').first.click()
        await m.screenshot(path=str(OUT/'menu-mobile.png'))
        await m.keyboard.press('Escape')
        assert not await m.locator('.nav').is_visible()
        checks.append('Touch map selection, explicit drag mode, mobile menu, no overflow')
        await ctx.route('https://tile.openstreetmap.org/**', lambda r: r.abort())
        await page.goto(BASE + '/#map', wait_until='networkidle')
        await page.wait_for_selector('[data-map-loaded="true"]')
        await page.wait_for_timeout(250)
        assert await page.locator('[data-map-status]').is_visible()
        await page.locator('[data-map-select="tagansky"]').click()
        assert await page.locator('[data-map-detail="tagansky"] .btn').is_visible()
        await ctx.route('**/vendor/leaflet/leaflet.js', lambda r: r.abort())
        await page.reload(wait_until='networkidle')
        await page.wait_for_selector('[data-map-loaded="error"]')
        await page.locator('[data-map-select="lubyansky"]').click()
        assert await page.locator('[data-map-detail="lubyansky"] .btn').is_visible()
        checks.append('Tile outage and library outage: readable status, usable hotel cards and directions')
        reduced = await browser.new_context(reduced_motion='reduce', viewport={'width':1440,'height':900})
        await reduced.route('https://tile.openstreetmap.org/**', lambda r: r.abort())
        r = await reduced.new_page(); await r.goto(BASE + '/',wait_until='networkidle')
        assert await r.locator('.btn').first.evaluate('(e)=>getComputedStyle(e).transitionDuration') == '0s'
        assert await r.evaluate('getComputedStyle(document.documentElement).scrollBehavior') == 'auto'
        await r.locator('.feature').first.scroll_into_view_if_needed()
        assert await r.locator('.feature').first.evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
        nojs = await browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        n = await nojs.new_page(); await n.goto(BASE + '/',wait_until='networkidle')
        assert await n.locator('[data-map-detail]:visible').count() == 4
        assert await n.locator('[data-map-detail] a[target="_blank"]').count() == 4
        checks.append('Reduced motion disables effects; no-JS renders all four addresses and route links')
        assert not errors, errors
        await browser.close()
    report = {'status':'PASS','checks':checks,'js_errors':errors,'tiles':'isolated fixtures; public tile service not exercised by automated pan/zoom'}
    (OUT/'experience-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == '__main__': asyncio.run(main())
