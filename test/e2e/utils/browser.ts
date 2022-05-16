import {Browser, chromium, LaunchOptions} from '@playwright/test';
import {parseBoolean} from '@/e2e/utils/bool';

export const createBrowser = async (options?: LaunchOptions): Promise<Browser> => {
  const headless = !parseBoolean(process.env.DISPLAY_BROWSER);
  return await chromium.launch({
    headless,
    ...options,
  });
};
