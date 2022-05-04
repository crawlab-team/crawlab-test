import {Page} from '@playwright/test';

export const toggleSwitch = async (page: Page, enabled: boolean) => {
  if (enabled && !(await page.$('#enabled.is-checked')) ||
    !enabled && (await page.$('#enabled.is-checked'))) {
    await page.click('#enabled');
  }
};
