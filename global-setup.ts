import {login} from '@/e2e/actions/auth/login';
import {createBrowser} from '@/e2e/utils/browser';
import {FullConfig} from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // browser
  const browser = await createBrowser({
    headless: true,
  });

  // page
  const page = await browser.newPage({baseURL: process.env.APP_URL});
  await page.goto('/');

  // login and save storage state
  await login(page, {saveContext: true});

  // close browser
  await browser.close();
}

export default globalSetup;
