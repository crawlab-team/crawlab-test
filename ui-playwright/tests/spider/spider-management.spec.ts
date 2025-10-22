import { test, expect } from '../../fixtures/base';
import { testData } from '../../config/test-config';

/**
 * UI-001: Spider Management Workflow Validation
 * 
 * This test validates the complete spider management workflow through the web interface,
 * ensuring users can create, configure, run, and monitor spiders effectively.
 * 
 * Test Steps:
 * 1. Login to Crawlab
 * 2. Navigate to spider management
 * 3. Verify spider list is visible
 * 4. Create a new spider
 * 5. Verify spider appears in list
 * 6. View spider details
 * 7. Clean up test data
 */

test.describe('Spider Management Workflow', () => {
  test.beforeEach(async ({ loginPage }) => {
    // Navigate to login page before each test
    await loginPage.goto();
  });
  
  test('should complete full spider management workflow', async ({ 
    loginPage, 
    dashboardPage, 
    spiderPage,
    testSpiders 
  }) => {
    // Step 1: Login
    await test.step('Login to Crawlab', async () => {
      await loginPage.login();
      await expect(loginPage.page).toHaveURL(/\/(dashboard|home)/);
    });
    
    // Step 2: Navigate to spider management
    await test.step('Navigate to spider management', async () => {
      await dashboardPage.goToSpiders();
      await expect(spiderPage.page).toHaveURL(/\/spider/);
    });
    
    // Step 3: Verify spider list is visible
    await test.step('Verify spider list is visible', async () => {
      const isTableVisible = await spiderPage.isSpiderTableVisible();
      expect(isTableVisible).toBeTruthy();
    });
    
    // Step 4: Create a new spider
    const testSpiderName = testData.spider.name('ui-001');
    await test.step('Create a new spider', async () => {
      const createdName = await spiderPage.createSpider(
        testSpiderName,
        testData.spider.description
      );
      
      // Track for cleanup
      testSpiders.push(createdName);
      
      // Verify success
      await spiderPage.waitForSuccessMessage();
    });
    
    // Step 5: Verify spider appears in list
    await test.step('Verify spider appears in list', async () => {
      const exists = await spiderPage.spiderExists(testSpiderName);
      expect(exists).toBeTruthy();
      
      // Verify spider row is visible
      const spiderRow = spiderPage.getSpiderRow(testSpiderName);
      await expect(spiderRow).toBeVisible();
    });
    
    // Step 6: View spider details
    await test.step('View spider details', async () => {
      await spiderPage.clickSpider(testSpiderName);
      await expect(spiderPage.page).toHaveURL(/\/spider\/[^\/]+$/);
    });
    
    // Step 7: Clean up - delete the test spider
    await test.step('Clean up test spider', async () => {
      // Navigate back to spider list
      await spiderPage.goto();
      
      // Delete the spider
      await spiderPage.deleteSpider(testSpiderName);
      
      // Verify spider is removed
      const exists = await spiderPage.spiderExists(testSpiderName);
      expect(exists).toBeFalsy();
    });
  });
  
  test('should validate spider creation form', async ({ 
    loginPage, 
    dashboardPage, 
    spiderPage 
  }) => {
    // Login and navigate
    await loginPage.login();
    await dashboardPage.goToSpiders();
    
    // Open create dialog
    await test.step('Open create spider dialog', async () => {
      await spiderPage.openCreateDialog();
      const isDialogVisible = await spiderPage.isCreateDialogVisible();
      expect(isDialogVisible).toBeTruthy();
    });
    
    // Verify form fields are present
    await test.step('Verify form fields exist', async () => {
      // Check name input
      const nameInput = spiderPage.page.locator('input[name="name"], input[placeholder*="name" i]');
      await expect(nameInput).toBeVisible();
      
      // Check confirm button
      const confirmButton = spiderPage.page.locator('button:has-text("Confirm"), button:has-text("确定")');
      await expect(confirmButton).toBeVisible();
      
      // Check cancel button
      const cancelButton = spiderPage.page.locator('button:has-text("Cancel"), button:has-text("取消")');
      await expect(cancelButton).toBeVisible();
    });
  });
  
  test('should handle spider search', async ({ 
    loginPage, 
    dashboardPage, 
    spiderPage,
    testSpiders 
  }) => {
    // Setup: Login and create a test spider
    await loginPage.login();
    await dashboardPage.goToSpiders();
    
    const searchSpiderName = testData.spider.name('search-test');
    const createdName = await spiderPage.createSpider(searchSpiderName);
    testSpiders.push(createdName);
    
    // Test: Search for the spider
    await test.step('Search for spider', async () => {
      await spiderPage.searchSpider(searchSpiderName);
      
      // Verify spider is found
      const exists = await spiderPage.spiderExists(searchSpiderName);
      expect(exists).toBeTruthy();
    });
    
    // Cleanup
    await spiderPage.deleteSpider(searchSpiderName);
  });
});
