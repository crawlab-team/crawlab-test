import {test} from '@playwright/test';
import {login} from '@/e2e/actions/auth/login';

test.describe.serial('login', () => {
  test('should login', async ({browser}) => {
    await login({browser});
  });
});
