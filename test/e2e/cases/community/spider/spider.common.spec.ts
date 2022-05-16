import {expect} from '@playwright/test';
import {getRandomName} from '@/e2e/utils/name';
import {clickTableCellByKey, getTableCellByTargetKey, getTableCellTextsByKey} from '@/e2e/actions/components/table';
import {createSpider, deleteSpider, editSpider, runSpider} from '@/e2e/actions/spider/common';
import {test} from '@/e2e/base/authTest';
import {goToListPage, goToNavTab} from '@/e2e/actions/components/nav';

test.describe.serial('spider:common', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'echo "hello world"';
  const cmdEdited = 'echo "hello crawlab"';

  test.beforeEach(async ({page}) => {
    // go to page
    await goToListPage(page, 'spiders');
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

  test('should edit spider', async ({page}) => {
    await clickTableCellByKey(page, 'name', name);

    await editSpider(page, {cmd: cmdEdited});

    // refresh page
    await page.reload();
    await goToNavTab(page, 'overview');

    await expect(await page.inputValue('#cmd')).toEqual(cmdEdited);
  });

  test('should delete spider', async ({page}) => {
    // delete spider
    await deleteSpider(page, {name});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).not.toContain(name);
  });
});
