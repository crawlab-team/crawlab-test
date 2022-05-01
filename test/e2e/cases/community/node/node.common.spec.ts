import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {clickTableCellByKey} from '../../../utils/table';
import {editNode} from '../../../actions/node/common';

test.use({storageState: getStorageFilePath()});
test.describe.configure({mode: 'serial'});

test.describe('node: common', () => {
  const node = {
    name: 'Master Node',
    description: '',
    enabled: true,
    maxRunners: 8,
  };
  const nodeEdited = {
    name: 'Master Node 2',
    description: 'This is Master Node 2',
    enabled: false,
    maxRunners: 4,
  };

  test('should edit node', async ({page}) => {
    // go to list page
    await page.goto('/#/nodes');
    await page.waitForSelector('#add-btn');

    // go to detail page
    await clickTableCellByKey(page, 'name', node.name);

    // edit node
    await editNode(page, {...nodeEdited});

    // refresh page
    await page.reload();
    await page.click('.el-menu-item.overview');

    // expect fields to be the same as edited
    await expect(await page.inputValue('#name input')).toEqual(nodeEdited.name);
    await expect(await page.inputValue('#description textarea')).toEqual(nodeEdited.description);
    await expect(await page.$('#enabled.is-checked')).toBeNull();
    await expect(await page.inputValue('#max_runners input')).toEqual(nodeEdited.maxRunners.toString());

    // reset
    await editNode(page, {...node});
  });
});
