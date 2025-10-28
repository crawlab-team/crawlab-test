"""
Navigation-related UI actions for Crawlab.

This module provides reusable actions for navigating through the Crawlab UI.
"""

import logging
from typing import Optional
from ..browser.playwright_wrapper import PlaywrightWrapper


class NavigationActions:
    """Navigation actions for Crawlab UI."""
    
    def __init__(self, browser: PlaywrightWrapper, base_url: str = "http://localhost:8080"):
        """Initialize navigation actions.
        
        Args:
            browser: Browser wrapper instance
            base_url: Base URL of the Crawlab application
        """
        self.browser = browser
        self.base_url = base_url
        self.logger = logging.getLogger("navigation_actions")
    
    async def goto_home(self):
        """Navigate to the home/dashboard page."""
        self.logger.info("Navigating to home page")
        await self.browser.goto(f"{self.base_url}/home")
        await self.browser.wait_for_load_state("networkidle")
        self.logger.info("Home page loaded")
    
    async def goto_spiders(self):
        """Navigate to the spiders page."""
        self.logger.info("Navigating to spiders page")
        
        # Try clicking on sidebar menu item first
        spider_menu_selectors = [
            "a[href='/spiders']",
            ".sidebar a:has-text('Spiders')",
            ".sidebar a:has-text('爬虫')",  # Chinese: Spiders
            "[data-test='nav-spiders']"
        ]
        
        clicked = False
        for selector in spider_menu_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Spiders menu clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            # Fallback: direct navigation
            self.logger.debug("Direct navigation to spiders page")
            await self.browser.goto(f"{self.base_url}/spiders")
        
        # Wait for spider list to load
        await self.browser.wait_for_selector(".spider-list, .el-table, [data-test='spider-list']", timeout=10000)
        self.logger.info("Spiders page loaded")
    
    async def goto_tasks(self):
        """Navigate to the tasks page."""
        self.logger.info("Navigating to tasks page")
        
        task_menu_selectors = [
            "a[href='/tasks']",
            ".sidebar a:has-text('Tasks')",
            ".sidebar a:has-text('任务')",  # Chinese: Tasks
            "[data-test='nav-tasks']"
        ]
        
        clicked = False
        for selector in task_menu_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Tasks menu clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            await self.browser.goto(f"{self.base_url}/tasks")
        
        await self.browser.wait_for_selector(".task-list, .el-table, [data-test='task-list']", timeout=10000)
        self.logger.info("Tasks page loaded")
    
    async def goto_schedules(self):
        """Navigate to the schedules page."""
        self.logger.info("Navigating to schedules page")
        
        schedule_menu_selectors = [
            "a[href='/schedules']",
            ".sidebar a:has-text('Schedules')",
            ".sidebar a:has-text('定时任务')",  # Chinese: Scheduled Tasks
            "[data-test='nav-schedules']"
        ]
        
        clicked = False
        for selector in schedule_menu_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Schedules menu clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            await self.browser.goto(f"{self.base_url}/schedules")
        
        await self.browser.wait_for_selector(".schedule-list, .el-table, [data-test='schedule-list']", timeout=10000)
        self.logger.info("Schedules page loaded")
    
    async def goto_nodes(self):
        """Navigate to the nodes page."""
        self.logger.info("Navigating to nodes page")
        
        node_menu_selectors = [
            "a[href='/nodes']",
            ".sidebar a:has-text('Nodes')",
            ".sidebar a:has-text('节点')",  # Chinese: Nodes
            "[data-test='nav-nodes']"
        ]
        
        clicked = False
        for selector in node_menu_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Nodes menu clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            await self.browser.goto(f"{self.base_url}/nodes")
        
        await self.browser.wait_for_selector(".node-list, .el-table, [data-test='node-list']", timeout=10000)
        self.logger.info("Nodes page loaded")
    
    async def goto_projects(self):
        """Navigate to the projects page."""
        self.logger.info("Navigating to projects page")
        
        project_menu_selectors = [
            "a[href='/projects']",
            ".sidebar a:has-text('Projects')",
            ".sidebar a:has-text('项目')",  # Chinese: Projects
            "[data-test='nav-projects']"
        ]
        
        clicked = False
        for selector in project_menu_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Projects menu clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            await self.browser.goto(f"{self.base_url}/projects")
        
        await self.browser.wait_for_selector(".project-list, .el-table, [data-test='project-list']", timeout=10000)
        self.logger.info("Projects page loaded")
    
    async def goto_spider_detail(self, spider_id: str):
        """Navigate to a specific spider's detail page.
        
        Args:
            spider_id: ID of the spider
        """
        self.logger.info(f"Navigating to spider detail page: {spider_id}")
        await self.browser.goto(f"{self.base_url}/spiders/{spider_id}")
        await self.browser.wait_for_load_state("networkidle")
        self.logger.info("Spider detail page loaded")
    
    async def goto_task_detail(self, task_id: str):
        """Navigate to a specific task's detail page.
        
        Args:
            task_id: ID of the task
        """
        self.logger.info(f"Navigating to task detail page: {task_id}")
        await self.browser.goto(f"{self.base_url}/tasks/{task_id}")
        await self.browser.wait_for_load_state("networkidle")
        self.logger.info("Task detail page loaded")
    
    async def switch_to_tab(self, tab_name: str):
        """Switch to a tab within a detail page.
        
        Args:
            tab_name: Name of the tab to switch to
        """
        self.logger.info(f"Switching to tab: {tab_name}")
        
        tab_selectors = [
            f".el-tabs__item:has-text('{tab_name}')",
            f"[role='tab']:has-text('{tab_name}')",
            f".tab:has-text('{tab_name}')",
            f"[data-test='tab-{tab_name.lower()}']"
        ]
        
        clicked = False
        for selector in tab_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Tab clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            raise RuntimeError(f"Could not find tab: {tab_name}")
        
        # Wait for tab content to load
        await self.browser.wait_for_load_state("networkidle", timeout=5000)
        self.logger.info(f"Switched to tab: {tab_name}")
    
    async def open_create_dialog(self, entity_type: str = "spider"):
        """Open the create dialog for a specific entity.
        
        Args:
            entity_type: Type of entity to create ('spider', 'task', 'schedule', etc.)
        """
        self.logger.info(f"Opening create dialog for {entity_type}")
        
        # Common create button selectors
        create_button_selectors = [
            f"button:has-text('Create')",
            f"button:has-text('New {entity_type.title()}')",
            f"button:has-text('Add')",
            f"button:has-text('新建')",  # Chinese: Create
            f"button:has-text('创建')",  # Chinese: Create
            f".create-button",
            f"[data-test='create-{entity_type}']",
            f".fa-plus"  # Plus icon
        ]
        
        clicked = False
        for selector in create_button_selectors:
            try:
                if await self.browser.is_visible(selector):
                    await self.browser.click(selector)
                    clicked = True
                    self.logger.debug(f"Create button clicked using selector: {selector}")
                    break
            except:
                continue
        
        if not clicked:
            raise RuntimeError(f"Could not find create button for {entity_type}")
        
        # Wait for dialog to appear
        await self.browser.wait_for_selector(".el-dialog, .dialog, [role='dialog']", timeout=5000)
        self.logger.info("Create dialog opened")
