import {test as _test} from '@playwright/test';
import {getStorageFilePath} from '../utils/storage';

export const test = _test.extend({
  storageState: async ({}, use) => {
    await use(getStorageFilePath());
  },
});
