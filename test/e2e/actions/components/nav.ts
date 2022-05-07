import {Page} from '@playwright/test';

export const goToNavTab = async (page: Page, key: string) => {
  await page.click(`.el-menu-item.${key}`);
  await page.waitForTimeout(500);
};
