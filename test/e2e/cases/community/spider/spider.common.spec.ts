import {expect} from '@playwright/test';
import {getRandomName} from '../../../utils/name';
import {getTableCellByTargetKey, getTableCellTextsByKey} from '../../../actions/components/table';
import {createSpider, deleteSpider, runSpider} from '../../../actions/spider/common';
import {test} from '../../../base/authTest';

test.describe.serial('spider: crud', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'echo "hello world"';

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
  });

  test('should create spider', async ({page}) => {
    // create spider
    await createSpider(page, {name, cmd});

    // expect table to display created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).toContain(name);
  });

  test('should run spider', async ({page}) => {
    // run spider
    await runSpider(page, {name});

    // last status
    const elLs = await getTableCellByTargetKey(page, 'name', name, 'last_status');
    await elLs.waitForSelector('.task-status.el-tag--success');
  });

  test.skip('should edit spider', async ({page}) => {
    // TODO: implement
  });

  test('should delete spider', async ({page}) => {
    // delete spider
    await deleteSpider(page, {name});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).not.toContain(name);
  });
});
