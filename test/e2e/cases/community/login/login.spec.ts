import {test} from '@playwright/test';
import {login} from '../../../actions/auth/login';

test('should login', async ({browser}) => {
  await login({browser});
});
