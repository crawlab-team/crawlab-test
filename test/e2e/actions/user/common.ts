import {Page} from '@playwright/test';
import {BaseActionOptions} from '../base';
import {deleteTableRowByKey, deleteTableRowByName, getTableCellByTargetKey} from '../components/table';
import {selectFromItems} from '@/e2e/actions/components/select';

interface CreateUserOptions extends BaseActionOptions {
  username?: string;
  password?: string;
  email?: string;
  role?: string;
}

interface EditUserOptions extends BaseActionOptions {
  username?: string;
  email?: string;
  role?: string;
}

interface EditUserPasswordOptions extends BaseActionOptions {
  password?: string;
}

interface DeleteUserOptions extends BaseActionOptions {
  username?: string;
}

export const createUser = async (page: Page, {
  username,
  password,
  email,
  role,
  waitDuration
}: CreateUserOptions = {}) => {
  await page.click('#add-btn');
  await page.waitForSelector('.create-edit-dialog');
  await page.fill('#username input', username);
  await page.fill('#password input', password);
  await page.fill('#email input', email);
  await selectFromItems(page, {key: '#role', value: role});
  await page.click('#confirm-btn button');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editUser = async (page: Page, {
  username,
  email,
  role,
  waitDuration
}: EditUserOptions = {}) => {
  if (username) await page.fill('#username input', username);
  if (email) await page.fill('#email input', email);
  if (role) await selectFromItems(page, {key: '#role', value: role});
  await page.click('#save-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editUserPassword = async (page: Page, {
  password,
  waitDuration
}: EditUserPasswordOptions = {}) => {
  await page.click('#password');
  await page.fill('.el-message-box__input input', password);
  await page.click('.edit-user-password-confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const deleteUser = async (page: Page, {
  username,
}: DeleteUserOptions = {}) => {  // click delete button
  return deleteTableRowByKey(page, {key: 'username', text: username});
};
