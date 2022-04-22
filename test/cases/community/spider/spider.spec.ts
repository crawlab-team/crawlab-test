import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {getRandomName} from '../../../utils/name';
import {getTableCellByKey, getTableCellByTargetKey} from '../../../utils/table';

test.use({storageState: getStorageFilePath()});

test.describe.configure({mode: 'serial'});

test.describe('spider - crud', () => {
  const name = getRandomName('spider');
  const cmd = 'echo "hello world"';

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
  });

  test('should create spider', async ({page, context}) => {
    // click add button
    await page.click('#add-btn');
    await page.waitForSelector('.create-edit-dialog');

    // fill form and click confirm button
    await page.type('#name', name);
    await page.type('#cmd', cmd);
    await page.click('.create-edit-dialog .confirm-btn');
    await page.waitForSelector('.create-edit-dialog.hidden');
    await page.waitForTimeout(500); // TODO: replace hard-coded timeout with a mechanical way

    // expect table to display created row
    const elNames = await page.$$('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
    const names = await Promise.all(elNames.map(el => el.innerText()));
    await expect(names).toContain(name);
  });

  test('should run spider', async ({page}) => {
    // click run button
    const elAct = await getTableCellByTargetKey(page, 'name', name, 'actions');
    const elRunBtn = await elAct.$('.run-btn');
    await elRunBtn.click();
    await page.waitForSelector('.run-spider-dialog');

    // click confirm button
    await page.click('.run-spider-dialog .confirm-btn');
    await page.waitForFunction(() => !document.querySelector('.el-message-box'));
    await page.waitForTimeout(500);

    // last status
    const elLs = await getTableCellByTargetKey(page, 'name', name, 'last_status');
    await elLs.waitForSelector('.task-status.el-tag--success');
  });

  test('should update spider', async ({page}) => {
    // TODO: implement
  });

  test('should delete spider', async ({page}) => {
    // click delete button
    const elAct = await getTableCellByTargetKey(page, 'name', name, 'actions');
    const elDelBtn = await elAct.$('.delete-btn');
    await elDelBtn.click();

    // click confirm button
    await page.click('.delete-confirm-btn');
    await page.waitForFunction(() => !document.querySelector('.el-message-box'));
    await page.waitForTimeout(500);

    // expect table to not contains created row
    const elNames = await page.$$('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
    const names = await Promise.all(elNames.map(el => el.innerText()));
    await expect(names.includes(name)).toBeFalsy();
  });
});
