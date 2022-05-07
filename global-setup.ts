import {login} from './test/e2e/actions/auth/login';
import {getDefaultBrowser} from './test/e2e/utils/browser';
import {initTestRun} from './test/sdk';
import {FullConfig} from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // initialize global test run
  await initTestRun();

  // login and save storage state
  await login({
    browser: await getDefaultBrowser({
      headless: true,
    }),
    close: true,
  });
}

export default globalSetup;
