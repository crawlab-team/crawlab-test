import {ElementHandle, Page} from '@playwright/test';
import {BaseActionOptions} from '../base';

interface DeleteTableRowByKeyOptions extends BaseActionOptions {
  key?: string;
  text?: string;
}

interface DeleteTableRowByNameOptions extends BaseActionOptions {
  name?: string;
}

interface ClickTableCellActionByKeyOptions extends BaseActionOptions {
  key?: string;
  text?: string;
  action?: string;
}

interface ClickTableCellByTargetKeyOptions extends BaseActionOptions {
  key?: string;
  text?: string;
  targetKey?: string;
}

export const getTableColumnIndexByKey = async (page: Page, key: string): Promise<number> => {
  const els = await page.$$('.table table.el-table__header tr > th');
  return els.findIndex(async el => {
    const cls = await el.getAttribute('class');
    return cls.split(' ').includes(key);
  });
};

export const getTableRowIndexByKey = async (page: Page, key: string, text: string): Promise<number> => {
  const els = await page.$$(`.table table.el-table__body tr.el-table__row > td.el-table__cell.${key}`);
  return els.findIndex(async el => {
    return text = await el.innerText();
  });
};

export const getTableRowByKey = async (page: Page, key: string, text: string): Promise<ElementHandle | undefined> => {
  const rowIdx = await getTableRowIndexByKey(page, key, text);
  const els = await page.$$(`.table table.el-table__body tr.el-table__row`);
  return els?.[rowIdx];
};

export const getTableCellByKey = async (page: Page, key: string, text: string): Promise<ElementHandle | undefined> => {
  return await page.locator(`.table table.el-table__body tr.el-table__row > td.el-table__cell.${key} :text-is("${text}")`).elementHandle();
};

export const getTableCellByTargetKey = async (page: Page, key: string, text: string, targetKey: string): Promise<ElementHandle | undefined> => {
  const elRow = await getTableRowByKey(page, key, text);
  return await elRow.$(`td.el-table__cell.${targetKey}`);
};

export const clickTableCellByKey = async (page: Page, key: string, text: string) => {
  const el = await getTableCellByKey(page, key, text);
  await el.click();
};

export const clickTableCellByTargetKey = async (page: Page, {
  key,
  text,
  targetKey
}: ClickTableCellByTargetKeyOptions) => {
  const el = await getTableCellByTargetKey(page, key, text, targetKey);
  await el.click();
};

export const getTableCellTextsByKey = async (page: Page, key: string) => {
  return await page.evaluate((key) => {
    const names = [];
    const els = document.querySelectorAll(`.table table.el-table__body tr.el-table__row > td.el-table__cell.${key}`);
    els.forEach(el => {
      names.push(el.textContent);
    });
    return names;
  }, key);
};

export const deleteTableRowByName = async (page: Page, {name, waitDuration}: DeleteTableRowByNameOptions = {}) => {
  return await deleteTableRowByKey(page, {key: 'name', text: name, waitDuration});
};

export const deleteTableRowByKey = async (page: Page, {key, text}: DeleteTableRowByKeyOptions = {}) => {
  const elAct = await getTableCellByTargetKey(page, key, text, 'actions');
  const elDelBtn = await elAct.$('.delete-btn');
  await elDelBtn.click();

  // click confirm button
  await page.click('.delete-confirm-btn');
  await page.waitForFunction(() => !document.querySelector('.el-message-box'));
  await page.waitForTimeout(500);
};

export const clickTableCellActionByKey = async (page: Page, {
  key,
  text,
  action,
  waitDuration
}: ClickTableCellActionByKeyOptions = {}) => {
  const elAct = await getTableCellByTargetKey(page, key, text, 'actions');
  const elBtn = await elAct.$(action);
  await elBtn.click();
  await page.waitForTimeout(waitDuration || 1000);
};

export const getTableRowId = async (page: Page, key: string, text: string): Promise<string> => {
  await clickTableCellByKey(page, key, text);
  const regex = /([a-f\d]{24})/;
  await page.waitForURL(regex);
  const m = await page.url().match(regex);
  await page.click('#back-btn');
  await page.waitForSelector('#add-btn');
  return m?.[1];
};

export const waitForTableColumnToBeReady = async (page: Page, key: string, text: string) => {
  await page.waitForTimeout(1000);
  await page.waitForFunction(({key, text}) => {
    const els = document.querySelectorAll(`.table table.el-table__body tr.el-table__row > td.el-table__cell.${key}`);
    const names = [];
    els.forEach(el => names.push(el.textContent.trim()));
    return names.filter(n => n === text).length > 0;
  }, {key, text});
};
