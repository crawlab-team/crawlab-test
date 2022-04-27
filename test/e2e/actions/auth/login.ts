import {Browser, expect} from '@playwright/test';
import {saveStorageState} from '../../utils/storage';
import {getDefaultBrowser} from '../../utils/browser';
import {DEFAULT_APP_URL, DEFAULT_PASSWORD, DEFAULT_USERNAME} from '../../constants/default';

export interface LoginProps {
  browser?: Browser,
  close?: boolean,
}

export const login = async ({browser, close}: LoginProps = {}) => {
  // browser
  if (!browser) {
    browser = await getDefaultBrowser();
  }

  // page
  const page = await browser.newPage({baseURL: process.env.APP_URL || DEFAULT_APP_URL});

  // go to default page
  await page.goto('/');

  // expect url to have 'login'
  await expect(page.url()).toContain('login');

  // enter username and password and click login button
  await page.type('input[name="username"]', process.env.USERNAME || DEFAULT_USERNAME);
  await page.type('input[name="password"]', process.env.PASSWORD || DEFAULT_PASSWORD);
  await page.click('.el-form-item button');

  // expect url to have 'home'
  await page.waitForSelector('.basic-layout'); // TODO: parameterize wait selector
  await expect(page.url()).toContain('home');
  await page.waitForTimeout(1000);

  // store storage state into the file
  await saveStorageState(browser.contexts()[0]);

  // close browser
  if (close) {
    await browser.close();
  }
};
