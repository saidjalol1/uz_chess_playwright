"""
Tab manager module for handling browser tab operations.
"""

import asyncio
from typing import List, Optional
from playwright.async_api import Page, BrowserContext


class TabManager:
    """Manager for browser tab operations."""
    
    def __init__(self, browser_context: BrowserContext):
        """
        Initialize tab manager with browser context.
        
        Args:
            browser_context: Playwright browser context to manage tabs for
        """
        self._context = browser_context
        self._new_page: Optional[Page] = None
        self._new_page_event = asyncio.Event()
    
    async def wait_for_new_tab(self, timeout: Optional[int] = None) -> Page:
        """
        Wait for new tab to open and return page object.
        
        Args:
            timeout: Maximum time to wait in seconds (default: 10)
            
        Returns:
            Page object for the newly opened tab
            
        Raises:
            asyncio.TimeoutError: If no new tab opens within timeout period
        """
        if timeout is None:
            timeout = 10
        
        # Reset event and page for new wait
        self._new_page_event.clear()
        self._new_page = None
        
        # Set up event listener for new pages
        def on_page(page: Page):
            self._new_page = page
            self._new_page_event.set()
        
        self._context.on('page', on_page)
        
        try:
            # Wait for the event with timeout
            await asyncio.wait_for(
                self._new_page_event.wait(),
                timeout=timeout
            )
            
            # Wait for the page to load
            if self._new_page:
                await self._new_page.wait_for_load_state('domcontentloaded')
            
            return self._new_page
        finally:
            # Clean up event listener
            self._context.remove_listener('page', on_page)
    
    async def switch_to_tab(self, page: Page) -> None:
        """
        Switch focus to specified tab.
        
        Args:
            page: Page object to switch focus to
        """
        await page.bring_to_front()
    
    def get_all_tabs(self) -> List[Page]:
        """
        Get list of all open tabs.
        
        Returns:
            List of all open Page objects in the browser context
        """
        return self._context.pages
    
    async def close_all_tabs(self) -> None:
        """
        Close all open tabs in the browser context.
        """
        pages = self.get_all_tabs()
        for page in pages:
            await page.close()
