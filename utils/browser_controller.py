"""
Browser controller module for managing Playwright browser interactions.
"""

import asyncio
import random
from typing import Optional, Dict
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, BrowserContext, Playwright


@dataclass
class BrowserOptions:
    """Configuration options for browser initialization."""
    headless: bool
    user_data_dir: str
    viewport: Optional[Dict[str, int]] = None


class BrowserController:
    """Controller for browser automation with stealth configuration."""
    
    def __init__(self):
        """Initialize BrowserController instance."""
        self.playwright: Optional[Playwright] = None
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def initialize(self, options: BrowserOptions) -> None:
        """
        Initialize browser with stealth configuration.
        
        Creates a persistent browser context with realistic settings to avoid detection:
        - Uses persistent browser context with user data directory
        - Sets realistic user agent string
        - Configures viewport to common resolution (1920x1080 default)
        - Disables automation indicators where possible
        
        Args:
            options: BrowserOptions containing headless mode, user_data_dir, and viewport settings
        """
        # Initialize Playwright
        self.playwright = await async_playwright().start()
        
        # Launch browser with Chromium (most common browser)
        self.browser = await self.playwright.chromium.launch(
            headless=options.headless
        )
        
        # Create persistent browser context with stealth configuration
        # Using launch_persistent_context instead of new_context for better stealth
        await self.browser.close()  # Close the initial browser
        
        args = [
            '--disable-blink-features=AutomationControlled',
        ]
        # Start maximized if not in headless mode
        if not options.headless:
            args.append('--start-maximized')
            
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=options.user_data_dir,
            headless=options.headless,
            viewport=options.viewport,
            no_viewport=True,  # Set to True so viewport stretches to 100% of window
            # Set realistic user agent (remove automation indicators)
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Disable automation flags
            args=args,
            # Additional stealth settings
            ignore_default_args=['--enable-automation'],
        )
        
        # Get the first page (persistent context creates one automatically)
        if len(self.browser.pages) > 0:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()
        
        # Store context reference
        self.context = self.browser
    
    async def navigate_to(self, url: str) -> None:
        """
        Navigate to specified URL.
        
        Args:
            url: The URL to navigate to
            
        Raises:
            Exception: If page is not initialized or navigation fails
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        await self.page.goto(url)
    
    async def click_element(self, selector: str, timeout: Optional[int] = None, force: bool = False) -> None:
        """
        Click element matching selector.
        
        Waits for the element to be visible and clickable before clicking.
        
        Args:
            selector: CSS selector for the element to click
            timeout: Timeout in milliseconds (default: 30000ms = 30s)
            force: Whether to bypass actionability checks
            
        Raises:
            Exception: If page is not initialized or element not found/clickable within timeout
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        # Default timeout is 30 seconds (30000ms) as per requirements
        timeout_ms = timeout if timeout is not None else 30000
        
        # For Flutter apps, canvas inputs might need force=True and evaluate click if they are off-screen
        if force:
            await self.page.locator(selector).evaluate("node => node.click()")
        else:
            await self.page.click(selector, timeout=timeout_ms)
    
    async def type_text(self, selector: str, text: str, human_like: bool = True) -> None:
        """
        Type text into element. For Flutter Web, directly setting the value and dispatching events is most reliable.
        
        Args:
            selector: CSS selector for the input element
            text: Text to type into the element
            human_like: If True, adds random delays between keystrokes (default: True)
            
        Raises:
            Exception: If page is not initialized or element not found
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        # Wait for the element to be attached
        await self.wait_for_selector(selector, state='attached')
        
        # Focus the element just in case, though Tab loop likely already focused it
        await self.page.locator(selector).evaluate("node => node.focus()")
        
        # Simulate typing at the keyboard level
        if human_like:
            for char in text:
                await self.page.keyboard.type(char)
                delay_ms = random.randint(50, 150)
                await asyncio.sleep(delay_ms / 1000.0)
        else:
            await self.page.keyboard.type(text)
            
    async def press_key(self, key: str) -> None:
        """
        Press a keyboard key.
        
        Args:
            key: Name of the key to press (e.g., 'Enter', 'Tab')
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        await self.page.keyboard.press(key)
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, state: str = 'visible') -> None:
        """
        Wait for element matching selector to appear.
        
        Args:
            selector: CSS selector for the element to wait for
            timeout: Timeout in milliseconds (default: 30000ms = 30s)
            state: Element state to wait for ('attached', 'detached', 'visible', 'hidden')
            
        Raises:
            Exception: If page is not initialized or element not found within timeout
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        # Default timeout is 30 seconds (30000ms) as per requirements
        timeout_ms = timeout if timeout is not None else 30000
        
        await self.page.wait_for_selector(selector, timeout=timeout_ms, state=state)
    
    async def screenshot(self, path: str) -> None:
        """
        Capture screenshot to specified path.
        
        Takes a screenshot of the current page and saves it to the specified file path.
        Used for error debugging and logging purposes.
        
        Args:
            path: File path where the screenshot should be saved (e.g., 'error.png')
            
        Raises:
            Exception: If page is not initialized or screenshot capture fails
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        await self.page.screenshot(path=path)
    
    async def close(self) -> None:
        """
        Close browser and cleanup resources.
        
        Performs cleanup operations to ensure no orphaned browser processes remain:
        - Closes all browser tabs
        - Closes the browser instance
        - Stops the Playwright instance
        
        This method should be called in a finally block to ensure cleanup
        happens even when errors occur during the registration flow.
        
        Raises:
            No exceptions are raised - errors during cleanup are silently handled
            to ensure cleanup completes even if some operations fail
        """
        try:
            # Close the browser context (which closes all pages/tabs)
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
        except Exception:
            # Silently handle errors during browser close to ensure cleanup continues
            pass
        
        try:
            # Stop the Playwright instance
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception:
            # Silently handle errors during playwright stop
            pass
    
    def get_current_page(self) -> Page:
        """
        Get current page object.
        
        Returns the current Playwright Page object for direct interaction.
        Useful for advanced operations not covered by the controller methods.
        
        Returns:
            Page: The current Playwright Page object
            
        Raises:
            Exception: If page is not initialized
        """
        if not self.page:
            raise Exception("Browser page not initialized. Call initialize() first.")
        
        return self.page
