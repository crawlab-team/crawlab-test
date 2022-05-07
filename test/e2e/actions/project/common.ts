import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';
import {deleteTableRowByName, getTableCellByTargetKey} from '../components/table';

interface CreateProjectOptions extends BaseActionOptions {
  name?: string;
  description?: string;
}

interface EditProjectOptions extends BaseActionOptions {
  name?: string;
  description?: string;
}

interface DeleteProjectOptions extends BaseActionOptions {
  name?: string;
}

export const createProject = async (page: Page, {
  name,
  description,
  waitDuration
}: CreateProjectOptions = {}) => {
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');
  await page.fill('#name input', name);
  await page.fill('#description textarea', description);
  await page.click('#confirm-btn button');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editProject = async (page: Page, {
  name,
  description,
  waitDuration
}: EditProjectOptions = {}) => {
  await page.fill('#name input', name);
  await page.fill('#description textarea', description);
  await page.click('#save-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const deleteProject = async (page: Page, {
  name,
}: DeleteProjectOptions = {}) => {  // click delete button
  return deleteTableRowByName(page, {name});
};
