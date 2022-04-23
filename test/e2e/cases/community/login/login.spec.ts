import {test} from '@playwright/test';
import {login} from '../../../auth/login';

test('should login', async ({browser}) => {
  await login(browser);
});
