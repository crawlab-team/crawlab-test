import {test as base} from '@playwright/test';
import {getStorageFilePath} from '../utils/storage';

export const test = base.extend({
  storageState: async ({}, use) => {
    await use(getStorageFilePath());
  },
});
