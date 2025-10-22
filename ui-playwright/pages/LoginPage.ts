import { Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { config } from '../config/test-config';

/**
 * Login Page Object
 * 
 * Handles all interactions with the login page.
 */
export class LoginPage extends BasePage {
  // Selectors
  private readonly usernameInput = 'input[name="username"], input[placeholder*="username" i], input[type="text"]';
  private readonly passwordInput = 'input[name="password"], input[placeholder*="password" i], input[type="password"]';
  private readonly loginButton = 'button[type="submit"], button:has-text("Login"), button:has-text("登录")';
  private readonly loginForm = 'form, .login-form';
  
  constructor(page: Page) {
    super(page);
  }
  
  /**
   * Navigate to login page
   */
  async goto() {
    await super.goto('/login');
    await this.waitForLoad();
  }
  
  /**
   * Perform login with credentials
   */
  async login(
    username: string = config.credentials.admin.username,
    password: string = config.credentials.admin.password
  ) {
    // Wait for login form to be visible
    await this.waitForSelector(this.loginForm);
    
    // Fill credentials
    await this.page.fill(this.usernameInput, username);
    await this.page.fill(this.passwordInput, password);
    
    // Click login and wait for navigation
    await Promise.all([
      this.page.waitForNavigation({ waitUntil: 'networkidle' }),
      this.page.click(this.loginButton),
    ]);
    
    // Verify we're no longer on login page
    await this.page.waitForURL(/\/(dashboard|home)/, { timeout: 10_000 });
  }
  
  /**
   * Check if already logged in
   */
  async isLoggedIn(): Promise<boolean> {
    const url = this.page.url();
    return !url.includes('/login');
  }
  
  /**
   * Get validation error message
   */
  async getValidationError(): Promise<string> {
    const errorSelector = '.el-form-item__error, .error-message';
    await this.waitForSelector(errorSelector);
    return await this.getText(errorSelector);
  }
}
