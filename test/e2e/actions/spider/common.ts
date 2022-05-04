import {Page} from '@playwright/test';
import {clickTableCellByKey, deleteTableRowByName, getTableCellByTargetKey} from '../components/table';

interface CreateSpiderOptions {
  name?: string;
  cmd?: string;
  waitDuration?: number;
}

export const createSpider = async (page: Page, {name, cmd, waitDuration}: CreateSpiderOptions = {}) => {
  // click add button
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');

  // fill form and click confirm button
  await page.type('#name', name);
  await page.type('#cmd', cmd);
  await page.click('.create-edit-dialog .confirm-btn');
  await page.waitForSelector('.create-edit-dialog.hidden');
  await page.waitForTimeout(waitDuration || 1000);
};

export const deleteSpider = async (page: Page, {name}) => {
  return deleteTableRowByName(page, {name});
};

export const runSpider = async (page: Page, {name}) => {
  // click run button
  const elAct = await getTableCellByTargetKey(page, 'name', name, 'actions');
  const elRunBtn = await elAct.$('.run-btn');
  await elRunBtn.click();
  await page.waitForSelector('.run-spider-dialog');

  // click confirm button
  await page.click('.run-spider-dialog .confirm-btn');
  await page.waitForFunction(() => !document.querySelector('.el-message-box'));
  await page.waitForTimeout(500);
};
