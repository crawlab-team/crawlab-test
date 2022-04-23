import {login} from './test/e2e/auth/login';

async function globalSetup() {
  // login and save storage state
  await login();
}

export default globalSetup;
