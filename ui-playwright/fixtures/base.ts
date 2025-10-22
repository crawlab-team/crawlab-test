import { test as base, Page } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { SpiderPage } from '../pages/SpiderPage';
import { DashboardPage } from '../pages/DashboardPage';

/**
 * Custom fixtures for Crawlab UI tests
 * 
 * These fixtures provide:
 * - Authenticated sessions
 * - Page object instances
 * - Test data cleanup
 */

type CrawlabFixtures = {
  // Authenticated context
  authenticatedPage: Page;
  
  // Page objects
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  spiderPage: SpiderPage;
  
  // Test data tracking for cleanup
  testSpiders: string[];
  testTasks: string[];
};

export const test = base.extend<CrawlabFixtures>({
  /**
   * Login page instance
   */
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },
  
  /**
   * Dashboard page instance
   */
  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await use(dashboardPage);
  },
  
  /**
   * Spider page instance
   */
  spiderPage: async ({ page }, use) => {
    const spiderPage = new SpiderPage(page);
    await use(spiderPage);
  },
  
  /**
   * Pre-authenticated page for tests that don't need to test login
   */
  authenticatedPage: async ({ page, loginPage }, use) => {
    await loginPage.goto();
    await loginPage.login();
    await use(page);
  },
  
  /**
   * Track test spiders for cleanup
   */
  testSpiders: async ({ }, use) => {
    const spiders: string[] = [];
    await use(spiders);
    
    // Cleanup: Delete test spiders after test
    if (spiders.length > 0) {
      // eslint-disable-next-line no-console
      console.log(`Cleaning up ${spiders.length} test spider(s)`);
      // TODO: Implement cleanup via API
    }
  },
  
  /**
   * Track test tasks for cleanup
   */
  testTasks: async ({ }, use) => {
    const tasks: string[] = [];
    await use(tasks);
    
    // Cleanup: Delete test tasks after test
    if (tasks.length > 0) {
      // eslint-disable-next-line no-console
      console.log(`Cleaning up ${tasks.length} test task(s)`);
      // TODO: Implement cleanup via API
    }
  },
});

export { expect } from '@playwright/test';
