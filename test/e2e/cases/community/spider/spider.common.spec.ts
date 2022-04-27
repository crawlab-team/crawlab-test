import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {getRandomName} from '../../../utils/name';
import {getTableCellByTargetKey} from '../../../utils/table';
import {createSpider, deleteSpider, runSpider} from '../../../actions/spider/operate';

// basic configuration
test.use({storageState: getStorageFilePath()});
test.describe.configure({mode: 'serial'});

// case
test.describe('spider - crud', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'echo "hello world"';

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
  });

  test('should create spider', async ({page, context}) => {
    // create spider
    await createSpider(page, {name, cmd});

    // expect table to display created row
    const elNames = await page.$$('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
    const names = await Promise.all(elNames.map(el => el.innerText()));
    await expect(names).toContain(name);
  });

  test('should run spider', async ({page}) => {
    // run spider
    await runSpider(page, {name});

    // last status
    const elLs = await getTableCellByTargetKey(page, 'name', name, 'last_status');
    await elLs.waitForSelector('.task-status.el-tag--success');
  });

  test('should update spider', async ({page}) => {
    // TODO: implement
  });

  test('should delete spider', async ({page}) => {
    // delete spider
    await deleteSpider(page, {name});

    // expect table to not contains created row
    const elNames = await page.$$('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
    const names = await Promise.all(elNames.map(el => el.innerText()));
    await expect(names.includes(name)).toBeFalsy();
  });
});
