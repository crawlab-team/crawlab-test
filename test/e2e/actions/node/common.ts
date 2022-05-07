import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';

interface EditNodeOptions extends BaseActionOptions {
  name?: string;
  description?: string;
  enabled?: boolean;
  maxRunners?: number;
}

export const editNode = async (page: Page, {
  name,
  description,
  enabled,
  maxRunners,
  waitDuration
}: EditNodeOptions = {}) => {
  if (name) await page.fill('#name input', name);
  if (description) await page.fill('#description textarea', description);
  if (maxRunners !== undefined) await page.fill('#max_runners input', maxRunners.toString());
  if (enabled !== undefined) {
    if (enabled && !(await page.$('#enabled.is-checked')) ||
      !enabled && (await page.$('#enabled.is-checked'))) {
      await page.click('#enabled');
    }
  }

  await page.click('#save-btn');
  await page.waitForTimeout(waitDuration || 1000);
};
