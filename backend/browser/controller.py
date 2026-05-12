from playwright.async_api import async_playwright, Browser, Page
from typing import Dict, Any, Optional, Tuple
import asyncio

class BrowserController:
    """Manages browser instances for portal automation"""
    
    def __init__(self):
        self._browser: Optional[Browser] = None
        self._pages: Dict[str, Page] = {}
    
    async def _get_browser(self):
        """Get or create browser instance"""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=False)
        return self._browser
    
    async def _get_page(self, session_id: str) -> Page:
        """Get existing page or create new one for session"""
        if session_id in self._pages and not self._pages[session_id].is_closed():
            return self._pages[session_id]
        
        browser = await self._get_browser()
        context = await browser.new_context()
        page = await context.new_page()
        self._pages[session_id] = page
        return page
    
    async def close_session(self, session_id: str):
        """Close browser session"""
        if session_id in self._pages:
            await self._pages[session_id].close()
            del self._pages[session_id]

# Singleton instance
_browser_controller = None

def get_browser_controller():
    global _browser_controller
    if _browser_controller is None:
        _browser_controller = BrowserController()
    return _browser_controller