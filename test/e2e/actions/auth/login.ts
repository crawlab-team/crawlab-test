import {Browser, Page} from '@playwright/test';
import {saveStorageState} from '@/e2e/utils/storage';
import {DEFAULT_PASSWORD, DEFAULT_USERNAME} from '@/e2e/constants/default';
import {createBrowser} from '@/e2e/utils/browser';
import {goToPage} from '@/e2e/actions/components/nav';

export interface LoginOptions {
  username?: string;
  password?: string;
  saveContext?: boolean;
}

interface LoginIncognitoOptions {
  browser?: Browser;
  username?: string;
  password?: string;
}

export const login = async (page: Page, {username, password, saveContext}: LoginOptions = {}) => {
  // enter username and password and click login button
  await page.fill('input[name="username"]', username || process.env.USERNAME || DEFAULT_USERNAME);
  await page.fill('input[name="password"]', password || process.env.PASSWORD || DEFAULT_PASSWORD);
  await page.click('.el-form-item button');

  // wait
  await page.waitForURL(/home/, {waitUntil: 'domcontentloaded'});
  await page.waitForTimeout(1000);

  // store storage state into the file
  if (saveContext) await saveStorageState(page.context());
};

export const logout = async (page: Page) => {
  await page.hover('#me');
  await page.click('#logout');
};

export const loginIncognito = async ({browser, username, password}: LoginIncognitoOptions = {}) => {
  if (!browser) browser = await createBrowser();
  const page = await browser.newPage({storageState: undefined});
  await goToPage(page, '/');
  await login(page, {username, password});
};
