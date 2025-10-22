import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';
import { testData } from '../config/test-config';

/**
 * Spider Page Object
 * 
 * Handles all interactions with the spider management page.
 */
export class SpiderPage extends BasePage {
  // Selectors
  private readonly createButton = 'button:has-text("Create"), button:has-text("新建"), button:has-text("创建"), .create-button';
  private readonly spiderTable = '.el-table, .spider-list, table';
  private readonly spiderTableRow = '.el-table__row, tr';
  private readonly createDialog = '.el-dialog, [role="dialog"]';
  private readonly nameInput = 'input[name="name"], input[placeholder*="name" i]';
  private readonly descriptionInput = 'textarea[name="description"], textarea[placeholder*="description" i]';
  private readonly typeSelect = 'select[name="type"], .el-select:has-text("Type")';
  private readonly confirmButton = 'button:has-text("Confirm"), button:has-text("确定"), button:has-text("OK")';
  private readonly cancelButton = 'button:has-text("Cancel"), button:has-text("取消")';
  
  constructor(page: Page) {
    super(page);
  }
  
  /**
   * Navigate to spiders page
   */
  async goto() {
    await super.goto('/spiders');
    await this.waitForLoad();
  }
  
  /**
   * Open create spider dialog
   */
  async openCreateDialog() {
    await this.page.click(this.createButton);
    await this.waitForSelector(this.createDialog);
  }
  
  /**
   * Create a new spider
   */
  async createSpider(
    name?: string,
    description?: string,
    type: string = 'customized'
  ) {
    const spiderName = name || testData.spider.name();
    
    // Open create dialog
    await this.openCreateDialog();
    
    // Fill form
    await this.page.fill(this.nameInput, spiderName);
    
    if (description) {
      await this.page.fill(this.descriptionInput, description);
    }
    
    // Select type if dropdown exists
    if (await this.isVisible(this.typeSelect)) {
      await this.page.selectOption(this.typeSelect, type);
    }
    
    // Submit form
    await this.page.click(this.confirmButton);
    
    // Wait for success message or dialog to close
    await this.page.waitForSelector(this.createDialog, { state: 'hidden' });
    
    return spiderName;
  }
  
  /**
   * Get spider row by name
   */
  getSpiderRow(name: string): Locator {
    return this.page.locator(this.spiderTableRow, { hasText: name });
  }
  
  /**
   * Check if spider exists in list
   */
  async spiderExists(name: string): Promise<boolean> {
    const row = this.getSpiderRow(name);
    return await row.isVisible({ timeout: 5000 }).catch(() => false);
  }
  
  /**
   * Click on spider row to view details
   */
  async clickSpider(name: string) {
    const row = this.getSpiderRow(name);
    await row.click();
    await this.waitForNavigation(/\/spider\/[^\/]+$/);
  }
  
  /**
   * Delete spider by name
   */
  async deleteSpider(name: string) {
    const row = this.getSpiderRow(name);
    
    // Find and click delete button in row
    const deleteButton = row.locator('button:has-text("Delete"), button:has-text("删除"), .delete-button');
    await deleteButton.click();
    
    // Confirm deletion in dialog
    const confirmDeleteButton = this.page.locator('.el-message-box button:has-text("Confirm"), .el-message-box button:has-text("确定")');
    await confirmDeleteButton.click();
    
    // Wait for success message
    await this.waitForSuccessMessage();
  }
  
  /**
   * Get total spider count
   */
  async getSpiderCount(): Promise<number> {
    const rows = this.page.locator(this.spiderTableRow);
    return await rows.count();
  }
  
  /**
   * Search for spider
   */
  async searchSpider(query: string) {
    const searchInput = 'input[placeholder*="search" i], input.search-input';
    await this.page.fill(searchInput, query);
    await this.page.press(searchInput, 'Enter');
    await this.waitForLoad();
  }
  
  /**
   * Check if create dialog is visible
   */
  async isCreateDialogVisible(): Promise<boolean> {
    return await this.isVisible(this.createDialog);
  }
  
  /**
   * Check if spider table is visible
   */
  async isSpiderTableVisible(): Promise<boolean> {
    return await this.isVisible(this.spiderTable);
  }
}
