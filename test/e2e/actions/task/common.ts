import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';
import {
  clickTableCellActionByKey,
  clickTableCellByKey, clickTableCellByTargetKey,
  deleteTableRowByKey,
  deleteTableRowByName, getTableCellByTargetKey
} from '../components/table';
import {selectFromItems} from '../components/select';

interface CreateTaskOptions extends BaseActionOptions {
  spiderName?: string;
  cmd?: string;
  param?: string;
}

interface ViewTaskLogsOptions extends BaseActionOptions {
  spiderName?: string;
}

interface ViewTaskDataOptions extends BaseActionOptions {
  spiderName?: string;
}

interface CancelTaskOptions extends BaseActionOptions {
  spiderName?: string;
}

interface DeleteTaskOptions extends BaseActionOptions {
  spiderName?: string;
}

export const createTask = async (page: Page, {
  spiderName,
  cmd,
  param,
  waitDuration
}: CreateTaskOptions = {}) => {
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');
  await selectFromItems(page, {key: '#spider_id', label: spiderName});
  await page.waitForTimeout(500);
  if (cmd) await page.fill('#cmd input', cmd);
  if (param) await page.fill('#param input', param);
  await page.click('#confirm-btn button');
  await page.waitForTimeout(waitDuration || 1000);
};

export const viewTaskLogs = async (page: Page, {
  spiderName,
  waitDuration
}: ViewTaskLogsOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'spider_id', text: spiderName, action: '.view-logs-btn', waitDuration});
};

export const viewTaskData = async (page: Page, {
  spiderName,
  waitDuration
}: ViewTaskDataOptions = {}) => {
  const el = await getTableCellByTargetKey(page, 'spider_id', spiderName, 'stat_result_count');
  const elAct = await el.$('.task-results');
  await elAct.click();
  await page.waitForTimeout(waitDuration || 1000);
};

export const cancelTask = async (page: Page, {
  spiderName,
}: CancelTaskOptions = {}) => {  // click delete button
  await clickTableCellActionByKey(page, {key: 'spider_id', text: spiderName, action: '.cancel-btn'});
  await page.click('.cancel-confirm-btn');
  await page.waitForFunction(() => !document.querySelector('.el-message-box'));
  await page.waitForTimeout(500);
};

export const deleteTask = async (page: Page, {
  spiderName,
}: DeleteTaskOptions = {}) => {  // click delete button
  return deleteTableRowByKey(page, {key: 'spider_id', text: spiderName});
};
