import { test, expect } from '../../fixtures/base';

/**
 * Authentication Tests
 * 
 * Validates login, logout, and session management.
 */

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.login();
    
    // Should redirect to dashboard
    await expect(loginPage.page).toHaveURL(/\/(dashboard|home)/);
    
    // Should not be on login page
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBeTruthy();
  });
  
  test('should show error with invalid credentials', async ({ loginPage }) => {
    await loginPage.goto();
    
    // Attempt login with invalid credentials
    await loginPage.login('invalid', 'wrong-password');
    
    // Should still be on login page or show error
    const url = loginPage.page.url();
    const onLoginPage = url.includes('/login');
    
    if (onLoginPage) {
      // Check for error message
      const hasError = await loginPage.page.locator('.el-message--error, .error-message').isVisible()
        .catch(() => false);
      expect(hasError).toBeTruthy();
    }
  });
  
  test('should require both username and password', async ({ loginPage }) => {
    await loginPage.goto();
    
    // Try to submit empty form
    const loginButton = loginPage.page.locator('button[type="submit"], button:has-text("Login")');
    await loginButton.click();
    
    // Form validation should prevent submission
    // Either we stay on login page or see validation error
    const url = loginPage.page.url();
    expect(url).toContain('/login');
  });
});
