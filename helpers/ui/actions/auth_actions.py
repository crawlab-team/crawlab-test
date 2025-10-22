"""
Authentication-related UI actions for Crawlab.

This module provides reusable actions for login, logout, and authentication flows.
Uses role-based selectors compatible with Element Plus UI framework.

Note: Selectors were discovered using MCP Playwright tools for UI exploration,
then implemented here for reliable automated test execution.
"""

import asyncio
import logging
from typing import Optional
from ..browser.playwright_wrapper import PlaywrightWrapper


class AuthActions:
    """
    Authentication-related UI actions for Crawlab web interface.
    
    This class handles user login, logout, and authentication verification.
    """
    
    def __init__(self, browser: PlaywrightWrapper, base_url: str = "http://localhost:8080"):
        """
        Initialize authentication actions.
        
        Args:
            browser: PlaywrightWrapper instance for browser automation
            base_url: Base URL of the Crawlab application
        """
        self.browser = browser
        self.base_url = base_url
        self.logger = logging.getLogger("auth_actions")
    
    async def navigate_to_login(self):
        """Navigate to the login page."""
        self.logger.info("Navigating to login page")
        # Navigate to base URL - it will redirect to /#/login
        await self.browser.goto(f"{self.base_url}")
        
        # Wait for page to fully load
        self.logger.info("Waiting for page to load...")
        await self.browser.wait_for_load_state("domcontentloaded", timeout=30000)
        
        # Give frontend app time to initialize and render
        import asyncio
        await asyncio.sleep(2)
        
        # Wait for login form to appear - use input element selectors
        try:
            # Wait for username input using name attribute (from Vue template)
            await self.browser.page.wait_for_selector('input[name="username"]', timeout=10000)
            self.logger.info("Login form loaded")
        except Exception as e:
            # Debug: get page content
            current_url = await self.browser.get_current_url()
            page_content = await self.browser.get_page_content()
            self.logger.error(f"Current URL: {current_url}")
            self.logger.error(f"Page content length: {len(page_content)}")
            self.logger.error(f"Page content preview: {page_content[:500]}")
            raise RuntimeError(
                f"Login page did not load properly. No login form elements found.\\n"
                f"Current URL: {current_url}\\n"
                f"Expected: {self.base_url}/#/login\\n"
                f"Error: {e}"
            )
        
        self.logger.info("Login page loaded successfully")
    
    async def fill_login_form(self, username: str, password: str):
        """Fill in the login form.
        
        Args:
            username: Username to enter
            password: Password to enter
        """
        self.logger.info(f"Filling login form for user: {username}")
        
        # Use name attribute selectors from Vue template (most reliable)
        # Vue template has: name="username" and name="password" attributes
        try:
            # Fill username - use Playwright's get_by_placeholder for i18n compatibility
            username_input = self.browser.page.locator('input[name="username"]')
            await username_input.fill(username)
            self.logger.debug("Username filled")
            
            # Fill password
            password_input = self.browser.page.locator('input[name="password"]')
            await password_input.fill(password)
            self.logger.debug("Password filled")
            
            self.logger.info("Login form filled successfully")
        except Exception as e:
            raise RuntimeError(f"Could not fill login form: {e}")
    
    async def submit_login(self):
        """Submit the login form."""
        self.logger.info("Submitting login form")
        
        # Use name attribute selector from Vue template: name="submit"
        try:
            submit_button = self.browser.page.locator('button[name="submit"]')
            await submit_button.click()
            self.logger.info("Login form submitted")
        except Exception as e:
            raise RuntimeError(f"Could not submit login form: {e}")
    
    async def verify_login_success(self, timeout: int = 10000):
        """Verify that login was successful.
        
        Args:
            timeout: Maximum time to wait for verification (milliseconds)
        """
        self.logger.info("Verifying login success")
        
        # Wait for redirect to home (hash routing: /#/home)
        try:
            # Check if URL contains /#/home
            await self.browser.page.wait_for_url("**/#/home", timeout=timeout)
            self.logger.info("✓ Successfully redirected to home page")
            return
        except Exception as e:
            self.logger.debug(f"URL wait failed: {e}")
        
        # Alternative: check current URL contains home
        try:
            current_url = await self.browser.get_current_url()
            if "/#/home" in current_url or "/home" in current_url:
                self.logger.info(f"✓ Login verified by URL: {current_url}")
                return
        except Exception as e:
            self.logger.debug(f"URL check failed: {e}")
        
        # Alternative: check for dashboard elements
        dashboard_indicators = [
            "text='Home'",  # Sidebar menu
            "text='Nodes'",
            "text='Spiders'",
            ".sidebar",
            "[role='menubar']",  # Sidebar menu
        ]
        
        for selector in dashboard_indicators:
            try:
                await self.browser.wait_for_selector(selector, timeout=3000)
                self.logger.info(f"✓ Login verified by presence of: {selector}")
                return
            except:
                continue
        
        # If we got here, login verification failed
        current_url = await self.browser.get_current_url()
        raise RuntimeError(
            f"Could not verify login success. Current URL: {current_url}"
        )
    
    async def login(self, username: str, password: str):
        """Complete login flow.
        
        Args:
            username: Username for login
            password: Password for login
        """
        self.logger.info(f"Executing login flow for user: {username}")
        
        # First navigate to app to check current state
        await self.browser.goto(f"{self.base_url}")
        await asyncio.sleep(2)  # Wait for redirect
        
        # Check if already logged in by looking at URL
        current_url = await self.browser.get_current_url()
        self.logger.debug(f"Current URL after navigation: {current_url}")
        
        if "/#/login" not in current_url:
            self.logger.info("✓ Already logged in, skipping login flow")
            return
        
        # Not logged in, proceed with login
        await self.navigate_to_login()
        await self.fill_login_form(username, password)
        await self.submit_login()
        await self.verify_login_success()
        
        self.logger.info("✓ Login completed successfully")
    
    async def click_user_menu(self):
        """Click on the user menu/avatar to open user dropdown."""
        self.logger.info("Opening user menu")
        
        user_menu_selectors = [
            ".user-avatar",
            ".user-menu",
            "[data-test='user-menu']",
            ".header .avatar",
            ".el-avatar"  # Element UI avatar
        ]
        
        clicked = False
        for selector in user_menu_selectors:
            if await self.browser.is_visible(selector):
                await self.browser.click(selector)
                clicked = True
                self.logger.debug(f"User menu clicked using selector: {selector}")
                break
        
        if not clicked:
            raise RuntimeError("Could not find user menu")
        
        # Wait for dropdown to appear
        await self.browser.wait_for_selector(".user-dropdown, .el-dropdown-menu", timeout=3000)
        self.logger.info("User menu opened")
    
    async def click_logout_option(self):
        """Click the logout option in the user menu."""
        self.logger.info("Clicking logout option")
        
        logout_selectors = [
            "button:has-text('Logout')",
            "button:has-text('Sign Out')",
            "button:has-text('退出')",  # Chinese: Exit/Logout
            "a:has-text('Logout')",
            "[data-test='logout']",
            ".logout-button"
        ]
        
        clicked = False
        for selector in logout_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Logout clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            raise RuntimeError("Could not find logout option")
    
    async def verify_logout_success(self, timeout: int = 10000):
        """Verify that logout was successful.
        
        Args:
            timeout: Maximum time to wait for verification (milliseconds)
        """
        self.logger.info("Verifying logout success")
        
        # Wait for redirect to login page
        try:
            await self.browser.wait_for_url("**/login", timeout=timeout)
            self.logger.info("✓ Successfully redirected to login page")
        except:
            # Alternative: check for login form
            login_indicators = [
                "input[type='password']",
                ".login-form",
                "button:has-text('Sign In')"
            ]
            
            success = False
            for selector in login_indicators:
                if await self.browser.is_visible(selector):
                    success = True
                    self.logger.info(f"✓ Logout verified by presence of: {selector}")
                    break
            
            if not success:
                raise RuntimeError("Could not verify logout success")
    
    async def logout(self):
        """Complete logout flow."""
        self.logger.info("Executing logout flow")
        
        await self.click_user_menu()
        await self.click_logout_option()
        await self.verify_logout_success()
        
        self.logger.info("✓ Logout completed successfully")
