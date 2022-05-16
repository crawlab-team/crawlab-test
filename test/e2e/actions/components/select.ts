import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';

interface SelectFromItemsOptions extends BaseActionOptions {
  key?: string;
  label?: string;
  value?: string;
}

export const selectFromItems = async (page: Page, {key, label, value, waitDuration}: SelectFromItemsOptions = {}) => {
  await page.click(key);
  await page.waitForSelector(`${key} .el-input.is-focus`);
  await page.waitForTimeout(waitDuration || 1000);

  if (label !== undefined) {
    const elOps = await page.$$('.el-select-dropdown__item');
    for (const el of elOps) {
      if (await el.textContent() === label) {
        await el.click();
        await page.waitForTimeout(waitDuration || 1000);
        return;
      }
    }
  } else {
    await page.click(`#${value}`);
  }
};
