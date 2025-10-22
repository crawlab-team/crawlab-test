import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Dashboard Page Object
 * 
 * Handles interactions with the main dashboard after login.
 */
export class DashboardPage extends BasePage {
  // Selectors
  private readonly sidebarMenu = '.el-menu, .sidebar-menu, nav';
  private readonly spidersMenuItem = 'a[href*="spider"], .menu-item:has-text("Spider"), .menu-item:has-text("爬虫")';
  private readonly tasksMenuItem = 'a[href*="task"], .menu-item:has-text("Task"), .menu-item:has-text("任务")';
  private readonly nodesMenuItem = 'a[href*="node"], .menu-item:has-text("Node"), .menu-item:has-text("节点")';
  private readonly schedulesMenuItem = 'a[href*="schedule"], .menu-item:has-text("Schedule"), .menu-item:has-text("定时")';
  private readonly userMenu = '.user-menu, .user-dropdown';
  
  constructor(page: Page) {
    super(page);
  }
  
  /**
   * Navigate to dashboard
   */
  async goto() {
    await super.goto('/');
    await this.waitForLoad();
  }
  
  /**
   * Navigate to spiders page
   */
  async goToSpiders() {
    await this.page.click(this.spidersMenuItem);
    await this.waitForNavigation(/\/spider/);
  }
  
  /**
   * Navigate to tasks page
   */
  async goToTasks() {
    await this.page.click(this.tasksMenuItem);
    await this.waitForNavigation(/\/task/);
  }
  
  /**
   * Navigate to nodes page
   */
  async goToNodes() {
    await this.page.click(this.nodesMenuItem);
    await this.waitForNavigation(/\/node/);
  }
  
  /**
   * Navigate to schedules page
   */
  async goToSchedules() {
    await this.page.click(this.schedulesMenuItem);
    await this.waitForNavigation(/\/schedule/);
  }
  
  /**
   * Check if sidebar menu is visible
   */
  async isSidebarVisible(): Promise<boolean> {
    return await this.isVisible(this.sidebarMenu);
  }
  
  /**
   * Get current page title
   */
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }
}
