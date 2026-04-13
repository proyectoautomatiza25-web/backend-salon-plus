import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto('https://app-v2.fu.do')
        await asyncio.sleep(8)
        html = await pg.content()
        with open('fudov2.html', 'w', encoding='utf-8') as f:
            f.write(html)
        await b.close()

asyncio.run(run())
