import {expect, test} from '@playwright/test';

test('should login', async ({page}) => {
  await page.goto('/');

  // expect url to have 'login'
  await expect(page.url()).toContain('login');

  // enter username and password and click login button
  await page.$('input[name="username"]').then(async el => await el.type('admin'));
  await page.$('input[name="password"]').then(async el => await el.type('admin'));
  await page.$('.el-form-item button').then(async el => await el.click());

  // expect url to have 'home'
  await page.waitForSelector('.basic-layout'); // TODO: parameterize wait selector
  await expect(page.url()).toContain('home');
});
