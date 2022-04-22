import {login} from './test/auth/login';

async function globalSetup() {
  // login and save storage state
  await login();
}

export default globalSetup;
