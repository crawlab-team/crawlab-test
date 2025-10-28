"""
Playwright browser automation wrapper for UI testing.

This module provides a clean interface to Playwright for deterministic browser automation.
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError as e:
    print("Error: Playwright is not installed.")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


class PlaywrightWrapper:
    """Wrapper for Playwright browser automation.
    
    Provides a simplified interface for common browser operations
    with built-in error handling and logging.
    """
    
    def __init__(self, headless: bool = True, viewport: Optional[Dict[str, int]] = None):
        """Initialize Playwright wrapper.
        
        Args:
            headless: Whether to run browser in headless mode
            viewport: Optional viewport size dict with 'width' and 'height'
        """
        self.headless = headless
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger("playwright_wrapper")
    
    async def start(self, browser_type: str = "chromium"):
        """Start the browser.
        
        Args:
            browser_type: Type of browser ('chromium', 'firefox', 'webkit')
        """
        self.logger.info(f"Starting {browser_type} browser (headless={self.headless})")
        
        try:
            self.playwright = await async_playwright().start()
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self._print_browser_install_help()
                raise RuntimeError(
                    "Playwright browsers are not installed. "
                    "Run: ./setup-playwright.sh or python -m playwright install chromium"
                ) from e
            raise
        
        # Get browser launcher
        if browser_type == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
        
        # Launch browser
        try:
            self.browser = await browser_launcher.launch(headless=self.headless)
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                self._print_browser_install_help()
                raise RuntimeError(
                    "Playwright browsers are not installed. "
                    "Run: ./setup-playwright.sh or python -m playwright install chromium"
                ) from e
            raise
        
        # Create context with viewport
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        self.logger.info("Browser started successfully")
    
    def _print_browser_install_help(self):
        """Print helpful message about browser installation."""
        print("\n" + "=" * 80)
        print("ERROR: Playwright Browsers Not Installed")
        print("=" * 80)
        print("\nPlaywright requires browser binaries to be installed separately.")
        print("\nQuick Fix:")
        print("  cd tests")
        print("  ./setup-playwright.sh")
        print("\nAlternatively:")
        print("  python -m playwright install chromium")
        print("\nFor all browsers:")
        print("  ./setup-playwright.sh --all")
        print("\nWith system dependencies:")
        print("  ./setup-playwright.sh --with-deps")
        print("\n" + "=" * 80 + "\n")
    
    async def close(self):
        """Close the browser and cleanup resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        self.logger.info("Browser closed")
    
    async def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 30000):
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation successful ('load', 'domcontentloaded', 'networkidle')
            timeout: Navigation timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until=wait_until, timeout=timeout)
        self.logger.info(f"Navigation complete")
    
    async def click(self, selector: str, timeout: int = 10000):
        """Click on an element.
        
        Args:
            selector: CSS selector for the element
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Clicking element: {selector}")
        await self.page.click(selector, timeout=timeout)
    
    async def fill(self, selector: str, value: str, timeout: int = 10000):
        """Fill an input field.
        
        Args:
            selector: CSS selector for the input field
            value: Value to fill
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Filling field {selector} with value: {value}")
        await self.page.fill(selector, value, timeout=timeout)
    
    async def type_text(self, selector: str, text: str, delay: int = 50, timeout: int = 10000):
        """Type text into an input field character by character.
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            delay: Delay between keystrokes in milliseconds
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Typing text into {selector}")
        await self.page.type(selector, text, delay=delay, timeout=timeout)
    
    async def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000):
        """Wait for an element to appear.
        
        Args:
            selector: CSS selector for the element
            state: State to wait for ('attached', 'detached', 'visible', 'hidden')
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Waiting for selector: {selector}")
        await self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    async def wait_for_url(self, url: str, timeout: int = 30000):
        """Wait for URL to match pattern.
        
        Args:
            url: URL pattern to match
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Waiting for URL: {url}")
        await self.page.wait_for_url(url, timeout=timeout)
    
    async def screenshot(self, path: str, full_page: bool = False):
        """Take a screenshot.
        
        Args:
            path: Path to save the screenshot
            full_page: Whether to capture the full scrollable page
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        await self.page.screenshot(path=path, full_page=full_page)
        self.logger.debug(f"Screenshot saved to {path}")
    
    async def get_text(self, selector: str) -> str:
        """Get text content of an element.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Text content of the element
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        element = await self.page.query_selector(selector)
        if element:
            return await element.inner_text()
        return ""
    
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of an element.
        
        Args:
            selector: CSS selector for the element
            attribute: Attribute name
            
        Returns:
            Attribute value or None if not found
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return await self.page.get_attribute(selector, attribute)
    
    async def is_visible(self, selector: str) -> bool:
        """Check if an element is visible.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            True if element is visible, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            await self.page.wait_for_selector(selector, state="visible", timeout=1000)
            return True
        except:
            return False
    
    async def select_option(self, selector: str, value: str):
        """Select an option from a dropdown.
        
        Args:
            selector: CSS selector for the select element
            value: Value to select
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        self.logger.debug(f"Selecting option {value} in {selector}")
        await self.page.select_option(selector, value)
    
    async def press_key(self, key: str):
        """Press a keyboard key.
        
        Args:
            key: Key to press (e.g., 'Enter', 'Escape', 'Tab')
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        await self.page.keyboard.press(key)
    
    async def evaluate(self, script: str) -> Any:
        """Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of the script execution
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return await self.page.evaluate(script)
    
    async def wait_for_load_state(self, state: str = "networkidle", timeout: int = 30000):
        """Wait for a specific load state.
        
        Args:
            state: Load state to wait for ('load', 'domcontentloaded', 'networkidle')
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        await self.page.wait_for_load_state(state, timeout=timeout)
    
    async def get_page_content(self) -> str:
        """Get the full HTML content of the current page.
        
        Returns:
            HTML content as string
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return await self.page.content()
    
    async def get_current_url(self) -> str:
        """Get the current page URL.
        
        Returns:
            Current URL as string
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        return self.page.url
