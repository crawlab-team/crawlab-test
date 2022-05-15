import {Browser, chromium, LaunchOptions} from '@playwright/test';

export const createBrowser = async (options?: LaunchOptions): Promise<Browser> => {
  return await chromium.launch({
    headless: !process.env.DISPLAY_BROWSER,
    ...options,
  });
};
