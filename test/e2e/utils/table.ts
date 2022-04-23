import {ElementHandle, Page} from '@playwright/test';

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
  const els = await page.$$(`.table table.el-table__body tr.el-table__row > td.el-table__cell.${key}`);
  for (let el of els) {
    if (text === await el.innerText()) {
      return el;
    }
  }
};

export const getTableCellByTargetKey = async (page: Page, key: string, text: string, targetKey: string): Promise<ElementHandle | undefined> => {
  const elRow = await getTableRowByKey(page, key, text);
  return await elRow.$(`td.el-table__cell.${targetKey}`);
};
