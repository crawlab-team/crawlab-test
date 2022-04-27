import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {getRandomName} from '../../../utils/name';
import {createSpider, deleteSpider} from '../../../actions/spider/operate';
import {clickTableCellByKey, getTableCellByKey} from '../../../utils/table';
import {createSpiderFile, openSpiderFile} from '../../../actions/spider/file';

// basic configuration
test.use({storageState: getStorageFilePath()});
test.describe.configure({mode: 'serial'});

// case
test.describe('spider - file', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'python3 main.py';
  const fileName = 'main.py';
  const fileContent = 'print(\'hello world\')';

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
  });

  test('should create spider file', async ({page}) => {
    // create spider
    await createSpider(page, {name, cmd});

    // create spider file
    await createSpiderFile(page, {spiderName: name, fileName, fileContent});

    // refresh page
    await page.reload();
    await page.click('.el-menu-item.files');

    // double-click on saved file
    await openSpiderFile(page, {fileName});

    // expect file content to be the same as the saved one
    const actualContent = await page.evaluate(() => {
      const lines = [];
      document.querySelectorAll('.code-mirror-editor .CodeMirror-line')
        .forEach(el => lines.push(el.textContent));
      return lines.join('\n');
    });
    await expect(actualContent).toEqual(fileContent);

    // delete spider
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
    await deleteSpider(page, {name});
  });
});
