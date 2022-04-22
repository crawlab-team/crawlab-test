import {Browser, chromium, LaunchOptions} from '@playwright/test';

export const getDefaultBrowser = async (options?: LaunchOptions): Promise<Browser> => {
  return await chromium.launch({
    headless: true,
    ...options,
  });
};
