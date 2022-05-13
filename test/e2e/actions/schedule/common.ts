import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';
import {deleteTableRowByName, getTableCellByTargetKey} from '../components/table';
import {toggleSwitch} from '../components/switch';
import {selectFromItems} from '../components/select';

interface CreateScheduleOptions extends BaseActionOptions {
  name?: string;
  spiderName?: string;
  cron?: string;
  enabled?: boolean;
  description?: string;
}

interface EditScheduleOptions extends BaseActionOptions {
  name?: string;
  spiderName?: string;
  cron?: string;
  enabled?: boolean;
  description?: string;
}

interface DeleteScheduleOptions extends BaseActionOptions {
  name?: string;
}

export const createSchedule = async (page: Page, {
  name,
  spiderName,
  cron,
  enabled,
  description,
  waitDuration
}: CreateScheduleOptions = {}) => {
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');
  await page.fill('#name input', name);
  await page.fill('#cron input', cron);
  await page.waitForTimeout(waitDuration || 1000);
  await selectFromItems(page, {key: '#spider_id', label: spiderName});
  if (description) await page.fill('#description textarea', description);
  await toggleSwitch(page, enabled);
  await page.click('#confirm-btn button');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editSchedule = async (page: Page, {
  name,
  cron,
  enabled,
  description,
  waitDuration
}: EditScheduleOptions = {}) => {
  await page.fill('#name input', name);
  await page.fill('#cron input', cron);
  await page.waitForTimeout(waitDuration || 1000);
  await page.fill('#description textarea', description);
  await toggleSwitch(page, enabled);
  await page.click('#save-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const deleteSchedule = async (page: Page, {
  name,
}: DeleteScheduleOptions = {}) => {  // click delete button
  return deleteTableRowByName(page, {name});
};
