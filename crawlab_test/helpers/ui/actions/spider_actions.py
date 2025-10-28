"""
Spider-related UI actions for Crawlab.

This module provides reusable actions for spider management operations.
"""

import logging
from typing import Any, Dict, Optional

from ..browser.playwright_wrapper import PlaywrightWrapper


class SpiderActions:
    """Spider management actions for Crawlab UI."""

    def __init__(self, browser: PlaywrightWrapper, base_url: str = "http://localhost:8080"):
        """Initialize spider actions.

        Args:
            browser: Browser wrapper instance
            base_url: Base URL of the Crawlab application
        """
        self.browser = browser
        self.base_url = base_url
        self.logger = logging.getLogger("spider_actions")

    async def create_spider(self, spider_data: Dict[str, Any]) -> Optional[str]:
        """Create a new spider.

        Args:
            spider_data: Dictionary containing spider configuration
                Required: name, type
                Optional: description, project_id, etc.

        Returns:
            Spider ID if successful, None otherwise
        """
        self.logger.info(f"Creating spider: {spider_data.get('name')}")

        # Fill spider name
        name_selectors = ["input[name='name']", "input[placeholder*='name' i]", ".spider-name input"]

        name_filled = False
        for selector in name_selectors:
            if await self.browser.is_visible(selector):
                await self.browser.fill(selector, spider_data["name"])
                name_filled = True
                self.logger.debug(f"Spider name filled using selector: {selector}")
                break

        if not name_filled:
            raise RuntimeError("Could not find spider name field")

        # Select spider type if provided
        if "type" in spider_data:
            type_selectors = ["select[name='type']", ".spider-type select", "select[placeholder*='type' i]"]

            for selector in type_selectors:
                if await self.browser.is_visible(selector):
                    await self.browser.select_option(selector, spider_data["type"])
                    self.logger.debug(f"Spider type selected: {spider_data['type']}")
                    break

        # Fill description if provided
        if "description" in spider_data:
            desc_selectors = [
                "textarea[name='description']",
                "textarea[placeholder*='description' i]",
                ".spider-description textarea",
            ]

            for selector in desc_selectors:
                if await self.browser.is_visible(selector):
                    await self.browser.fill(selector, spider_data["description"])
                    self.logger.debug("Spider description filled")
                    break

        # Submit form
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Confirm')",
            "button:has-text('Create')",
            "button:has-text('确定')",  # Chinese: Confirm
            ".submit-button",
        ]

        submitted = False
        for selector in submit_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    submitted = True
                    self.logger.debug(f"Form submitted using selector: {selector}")
                    break
            except:
                continue

        if not submitted:
            raise RuntimeError("Could not submit spider creation form")

        # Wait for creation to complete
        await self.browser.wait_for_load_state("networkidle", timeout=10000)

        # Try to extract spider ID from URL or response
        # This is a simplified version - actual implementation depends on UI behavior
        spider_id = None
        try:
            current_url = self.browser.page.url
            if "/spiders/" in current_url:
                spider_id = current_url.split("/spiders/")[-1].split("/")[0]
                self.logger.info(f"✓ Spider created with ID: {spider_id}")
        except:
            self.logger.warning("Could not extract spider ID from URL")

        self.logger.info(f"✓ Spider created: {spider_data.get('name')}")
        return spider_id

    async def verify_spider_exists(self, spider_name: str) -> bool:
        """Verify that a spider exists in the spider list.

        Args:
            spider_name: Name of the spider to verify

        Returns:
            True if spider exists, False otherwise
        """
        self.logger.info(f"Verifying spider exists: {spider_name}")

        # Look for spider in the list
        selectors = [
            f"text='{spider_name}'",
            f"[data-spider-name='{spider_name}']",
            f".spider-name:has-text('{spider_name}')",
        ]

        for selector in selectors:
            try:
                await self.browser.wait_for_selector(selector, timeout=5000)
                self.logger.info(f"✓ Spider found: {spider_name}")
                return True
            except:
                continue

        self.logger.warning(f"Spider not found: {spider_name}")
        return False

    async def delete_spider(self, spider_name: str):
        """Delete a spider.

        Args:
            spider_name: Name of the spider to delete
        """
        self.logger.info(f"Deleting spider: {spider_name}")

        # Find and click on spider row
        row_selectors = [f"tr:has-text('{spider_name}')", f"[data-spider-name='{spider_name}']"]

        found = False
        for selector in row_selectors:
            if await self.browser.is_visible(selector):
                # Look for delete button within the row
                delete_selectors = [
                    f"{selector} button:has-text('Delete')",
                    f"{selector} .delete-button",
                    f"{selector} [data-action='delete']",
                    f"{selector} .fa-trash",
                ]

                for del_selector in delete_selectors:
                    try:
                        if await self.browser.is_visible(del_selector):
                            await self.browser.click(del_selector)
                            found = True
                            self.logger.debug(f"Delete button clicked: {del_selector}")
                            break
                    except:
                        continue

                if found:
                    break

        if not found:
            raise RuntimeError(f"Could not find delete button for spider: {spider_name}")

        # Handle confirmation dialog
        await self.confirm_deletion()

        # Wait for deletion to complete
        await self.browser.wait_for_load_state("networkidle", timeout=10000)

        self.logger.info(f"✓ Spider deleted: {spider_name}")

    async def confirm_deletion(self):
        """Confirm a deletion dialog."""
        self.logger.debug("Confirming deletion")

        confirm_selectors = [
            "button:has-text('Confirm')",
            "button:has-text('OK')",
            "button:has-text('Delete')",
            "button:has-text('确定')",  # Chinese: Confirm
            ".el-message-box__btns button.el-button--primary",
        ]

        confirmed = False
        for selector in confirm_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    confirmed = True
                    self.logger.debug(f"Deletion confirmed using selector: {selector}")
                    break
            except:
                continue

        if not confirmed:
            raise RuntimeError("Could not confirm deletion")

    async def run_spider(self, spider_name: str):
        """Run a spider.

        Args:
            spider_name: Name of the spider to run
        """
        self.logger.info(f"Running spider: {spider_name}")

        # Find spider row and click run button
        row_selectors = [f"tr:has-text('{spider_name}')", f"[data-spider-name='{spider_name}']"]

        found = False
        for selector in row_selectors:
            if await self.browser.is_visible(selector):
                # Look for run button
                run_selectors = [
                    f"{selector} button:has-text('Run')",
                    f"{selector} .run-button",
                    f"{selector} [data-action='run']",
                    f"{selector} .fa-play",
                ]

                for run_selector in run_selectors:
                    try:
                        if await self.browser.is_visible(run_selector):
                            await self.browser.click(run_selector)
                            found = True
                            self.logger.debug(f"Run button clicked: {run_selector}")
                            break
                    except:
                        continue

                if found:
                    break

        if not found:
            raise RuntimeError(f"Could not find run button for spider: {spider_name}")

        # Wait for task to be created
        await self.browser.wait_for_load_state("networkidle", timeout=5000)

        self.logger.info(f"✓ Spider run initiated: {spider_name}")

    async def get_spider_count(self) -> int:
        """Get the total count of spiders.

        Returns:
            Number of spiders in the list
        """
        self.logger.debug("Getting spider count")

        # Try to get count from UI
        count_selectors = [".total-count", ".spider-count", "[data-test='spider-count']"]

        for selector in count_selectors:
            try:
                if await self.browser.is_visible(selector):
                    count_text = await self.browser.get_text(selector)
                    # Extract number from text (e.g., "Total: 5" -> 5)
                    import re

                    match = re.search(r"\d+", count_text)
                    if match:
                        count = int(match.group())
                        self.logger.debug(f"Spider count: {count}")
                        return count
            except:
                continue

        # Fallback: count table rows
        try:
            # Count visible spider rows (excluding header)
            rows = await self.browser.page.query_selector_all("tr.spider-row, .el-table__row")
            count = len(rows)
            self.logger.debug(f"Spider count (from rows): {count}")
            return count
        except:
            self.logger.warning("Could not determine spider count")
            return 0
