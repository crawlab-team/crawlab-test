import { Page } from '@playwright/test';

/**
 * Base Page Object class
 * 
 * Provides common functionality for all page objects:
 * - Navigation
 * - Waiting utilities
 * - Screenshot helpers
 * - Common assertions
 */
export class BasePage {
  constructor(public readonly page: Page) {}
  
  /**
   * Navigate to a specific path
   */
  async goto(path: string = '') {
    const baseUrl = process.env.CRAWLAB_BASE_URL || 'http://localhost:8080';
    await this.page.goto(`${baseUrl}${path}`);
  }
  
  /**
   * Wait for the page to be fully loaded
   */
  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }
  
  /**
   * Take a screenshot with a descriptive name
   */
  async screenshot(name: string) {
    await this.page.screenshot({ 
      path: `screenshots/${name}.png`,
      fullPage: true,
    });
  }
  
  /**
   * Wait for a selector to be visible
   */
  async waitForSelector(selector: string, timeout?: number) {
    await this.page.waitForSelector(selector, { 
      state: 'visible',
      timeout,
    });
  }
  
  /**
   * Wait for navigation to complete
   */
  async waitForNavigation(urlPattern?: string | RegExp) {
    if (urlPattern) {
      await this.page.waitForURL(urlPattern);
    } else {
      await this.page.waitForLoadState('networkidle');
    }
  }
  
  /**
   * Click and wait for navigation
   */
  async clickAndWaitForNavigation(selector: string) {
    await Promise.all([
      this.page.waitForNavigation(),
      this.page.click(selector),
    ]);
  }
  
  /**
   * Fill form field
   */
  async fillField(selector: string, value: string) {
    await this.page.fill(selector, value);
  }
  
  /**
   * Click button
   */
  async click(selector: string) {
    await this.page.click(selector);
  }
  
  /**
   * Get text content
   */
  async getText(selector: string): Promise<string> {
    return await this.page.textContent(selector) || '';
  }
  
  /**
   * Check if element is visible
   */
  async isVisible(selector: string): Promise<boolean> {
    try {
      await this.page.waitForSelector(selector, { 
        state: 'visible',
        timeout: 1000,
      });
      return true;
    } catch {
      return false;
    }
  }
  
  /**
   * Wait for success message
   */
  async waitForSuccessMessage(timeout?: number) {
    await this.waitForSelector('.el-message--success', timeout);
  }
  
  /**
   * Wait for error message
   */
  async waitForErrorMessage(timeout?: number) {
    await this.waitForSelector('.el-message--error', timeout);
  }
  
  /**
   * Get success message text
   */
  async getSuccessMessage(): Promise<string> {
    return await this.getText('.el-message--success .el-message__content');
  }
  
  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string> {
    return await this.getText('.el-message--error .el-message__content');
  }
}
