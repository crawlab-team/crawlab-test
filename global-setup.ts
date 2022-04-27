import {login} from './test/e2e/actions/auth/login';
import {getDefaultBrowser} from './test/e2e/utils/browser';

async function globalSetup() {
  // login and save storage state
  await login({
    browser: await getDefaultBrowser({
      headless: true,
    }),
    close: true,
  });
}

export default globalSetup;
