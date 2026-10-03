from __future__ import annotations

from pathlib import Path

from playwright.async_api import BrowserContext, Page, async_playwright

from ..config import Settings


class LocalBrowser:
    """Persistent headed Chromium running on the user's machine."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._playwright = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def start(self) -> None:
        if self.context:
            return
        self._playwright = await async_playwright().start()
        profile = Path(self.settings.paths.browser_profile)
        profile.mkdir(parents=True, exist_ok=True)
        self.context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile),
            headless=False,
            viewport={"width": 1280, "height": 800},
        )
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()

    async def open(self, url: str) -> str:
        await self.start()
        assert self.page is not None
        await self.page.goto(url, wait_until="domcontentloaded")
        return self.page.url

    async def click(self, selector: str) -> None:
        await self.start()
        assert self.page is not None
        await self.page.locator(selector).click()

    async def fill(self, selector: str, value: str) -> None:
        await self.start()
        assert self.page is not None
        await self.page.locator(selector).fill(value)

    async def text(self, selector: str = "body") -> str:
        await self.start()
        assert self.page is not None
        return await self.page.locator(selector).inner_text()

    async def screenshot(self, path: str | Path) -> str:
        await self.start()
        assert self.page is not None
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        await self.page.screenshot(path=str(target), full_page=True)
        return str(target)

    async def close(self) -> None:
        if self.context:
            await self.context.close()
            self.context = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
