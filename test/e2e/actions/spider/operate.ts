import {Page} from '@playwright/test';
import {getTableCellByTargetKey} from '../../utils/table';

interface CreateSpiderOptions {
  name?: string;
  cmd?: string;
}

export const createSpider = async (page: Page, opts: CreateSpiderOptions) => {
  if (!opts) opts = {};
  const {
    name,
    cmd,
  } = opts;

  // click add button
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');

  // fill form and click confirm button
  await page.type('#name', name);
  await page.type('#cmd', cmd);
  await page.click('.create-edit-dialog .confirm-btn');
  await page.waitForSelector('.create-edit-dialog.hidden');
  await page.waitForTimeout(500); // TODO: replace hard-coded timeout with a mechanical way
};

export const deleteSpider = async (page: Page, {name}) => {
  // click delete button
  const elAct = await getTableCellByTargetKey(page, 'name', name, 'actions');
  const elDelBtn = await elAct.$('.delete-btn');
  await elDelBtn.click();

  // click confirm button
  await page.click('.delete-confirm-btn');
  await page.waitForFunction(() => !document.querySelector('.el-message-box'));
  await page.waitForTimeout(500);
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
