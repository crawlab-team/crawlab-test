import {Page} from '@playwright/test';
import {BaseActionOptions} from './index';
import {getTableCellByTargetKey} from '../../utils/table';

interface DeleteTableRowByNameOptions extends BaseActionOptions {
  name?: string;
}

export const deleteTableRowByName = async (page: Page, {name}: DeleteTableRowByNameOptions = {}) => {
  const elAct = await getTableCellByTargetKey(page, 'name', name, 'actions');
  const elDelBtn = await elAct.$('.delete-btn');
  await elDelBtn.click();

  // click confirm button
  await page.click('.delete-confirm-btn');
  await page.waitForFunction(() => !document.querySelector('.el-message-box'));
  await page.waitForTimeout(500);
};
