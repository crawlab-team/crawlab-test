import {expect, test} from '@playwright/test';
import {login, logout} from '@/e2e/actions/auth/login';

test.describe.serial('login', () => {
  test.beforeEach(async ({page}) => {
    await page.goto('/');
  });

  test('should login admin', async ({page}) => {
    await login(page);
    await expect(page).toHaveURL(/home/);
  });

  test('should logout', async ({page}) => {
    await login(page);
    await logout(page);
    await expect(page).toHaveURL(/login/);
  });
});
