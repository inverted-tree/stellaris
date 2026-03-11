import asyncio
from playwright.async_api import async_playwright

BASE = "http://localhost:8000"
VIEWPORT = {"width": 1440, "height": 900}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport=VIEWPORT)

        await page.goto(f"{BASE}/")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(10)
        await page.screenshot(path="docs/preview-home.png")

        await page.goto(f"{BASE}/projects/ray-tracer/02-sphere-intersection/")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(10)
        await page.screenshot(path="docs/preview-post.png")

        await browser.close()


asyncio.run(main())
