import {test} from '@playwright/test';
import {login} from '../../../actions/auth/login';
import {wrapUpdateTestCaseResultFn} from '../../../../sdk';
import {caseMapping} from '../../../../sdk/mapping/case';

test.describe.serial('login', () => {
  test.afterEach(wrapUpdateTestCaseResultFn(test, caseMapping.community.login));

  test('should login', async ({browser}) => {
    await login({browser});
  });
});
