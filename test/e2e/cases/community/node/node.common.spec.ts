import {expect} from '@playwright/test';
import {clickTableCellByKey} from '../../../actions/components/table';
import {editNode} from '../../../actions/node/common';
import {goToNavTab} from '../../../actions/components/nav';
import {test} from '../../../base/authTest';

test.describe.serial('node: common', () => {
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
    await goToNavTab(page, 'overview');

    // expect fields to be the same as edited
    await expect(await page.inputValue('#name input')).toEqual(nodeEdited.name);
    await expect(await page.inputValue('#description textarea')).toEqual(nodeEdited.description);
    await expect(await page.$('#enabled.is-checked')).toBeNull();
    await expect(await page.inputValue('#max_runners input')).toEqual(nodeEdited.maxRunners.toString());

    // reset
    await editNode(page, {...node});
  });
});
