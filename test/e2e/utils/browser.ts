import {Browser, chromium, LaunchOptions} from '@playwright/test';
import {getHeadless, getTimeout} from '@/utils/config';

export const createBrowser = async (options?: LaunchOptions): Promise<Browser> => {
  return await chromium.launch({
    headless: getHeadless(),
    timeout: getTimeout(),
    ...options,
  });
};
