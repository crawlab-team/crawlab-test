import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {getRandomName} from '../../../utils/name';
import {createSpider, deleteSpider} from '../../../actions/spider/common';
import {clickTableCellByKey, getTableCellByKey} from '../../../actions/components/table';
import {
  cloneSpiderFile, createSpiderDirectory,
  createSpiderFile, deleteSpiderFile,
  editSpiderFileContent,
  getSpiderFileContent, moveSpiderFile,
  openSpiderFile, renameSpiderFile, rightClickSpiderFileAction
} from '../../../actions/spider/file';

// basic configuration
test.use({storageState: getStorageFilePath()});
test.describe.configure({mode: 'serial'});

test.describe('spider: file', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'python3 main.py';
  const fileName = 'main.py';
  const fileNameRenamed = 'main2.py';
  const fileNameCloned = 'main3.py';
  const fileContent = 'print(\'hello world\')';
  const fileContentEdited = 'print(\'hello crawlab\')';
  const directoryName = 'test';

  test('should create spider file', async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    // create spider
    await createSpider(page, {name, cmd});

    // click on created spider
    await clickTableCellByKey(page, 'name', name);
    await page.waitForSelector('.nav-sidebar');

    // click on files tab
    await page.click('.el-menu-item.files');

    // create spider file
    await createSpiderFile(page, {fileName, fileContent});

    // refresh page
    await page.reload();
    await page.click('.el-menu-item.files');

    // open spider file
    await openSpiderFile(page, {fileName});

    // expect file content to be the same as the saved one
    const actualContent = await getSpiderFileContent(page);
    await expect(actualContent).toEqual(fileContent);
  });

  test('should edit spider file', async ({page}) => {
    // go to spider detail page
    await page.goto('/#/spiders');
    await clickTableCellByKey(page, 'name', name);

    // click on files tab
    await page.click('.el-menu-item.files');

    // open spider file
    await openSpiderFile(page, {fileName});

    // edit spider file content
    await editSpiderFileContent(page, {fileContent: fileContentEdited});

    // refresh page
    await page.reload();
    await page.click('.el-menu-item.files');

    // open spider file
    await openSpiderFile(page, {fileName});

    // expect file content to be the same as the saved one
    const actualContent = await getSpiderFileContent(page);
    await expect(actualContent).toEqual(fileContentEdited);
  });

  test('should rename spider file', async ({page}) => {
    // go to spider detail page
    await page.goto('/#/spiders');
    await clickTableCellByKey(page, 'name', name);

    // click on files tab
    await page.click('.el-menu-item.files');

    // rename spider file
    await renameSpiderFile(page, {fileName, newFileName: fileNameRenamed});

    // expect original file not exists
    await expect(await page.$(`.el-tree-node[data-key="/${fileName}"]`)).toBeNull();

    // expect new file to exist
    await expect(await page.$(`.el-tree-node[data-key="/${fileNameRenamed}"]`)).not.toBeNull();
  });

  test('should move spider file', async ({page}) => {
    // go to spider detail page
    await page.goto('/#/spiders');
    await clickTableCellByKey(page, 'name', name);

    // click on files tab
    await page.click('.el-menu-item.files');

    // create directory
    await createSpiderDirectory(page, {directoryName});

    // create file
    await createSpiderFile(page, {fileName, fileContent});

    // move file to created folder
    await moveSpiderFile(page, {fileName, targetName: directoryName});

    // expect original file not exists
    await expect(await page.$(`.el-tree-node[data-key="/${fileName}"]`)).toBeNull();

    // expect new file to exist
    await expect(await page.$(`.el-tree-node[data-key="/${directoryName}/${fileName}"]`)).not.toBeNull();
  });

  test('should clone spider file', async ({page}) => {
    // go to spider detail page
    await page.goto('/#/spiders');
    await clickTableCellByKey(page, 'name', name);

    // click on files tab
    await page.click('.el-menu-item.files');

    // create file
    await createSpiderFile(page, {fileName, fileContent});

    // rename spider file
    await cloneSpiderFile(page, {fileName, newFileName: fileNameCloned});

    // expect original file not exists
    await expect(await page.$(`.el-tree-node[data-key="/${fileName}"]`)).not.toBeNull();

    // expect new file to exist
    await expect(await page.$(`.el-tree-node[data-key="/${fileNameCloned}"]`)).not.toBeNull();

    // expect new file content to be the same as original
    await openSpiderFile(page, {fileName: fileNameCloned});
    await expect(await getSpiderFileContent(page)).toEqual(fileContent);
  });

  test('should delete spider file', async ({page}) => {
    // go to spider detail page
    await page.goto('/#/spiders');
    await clickTableCellByKey(page, 'name', name);

    // click on files tab
    await page.click('.el-menu-item.files');

    // delete spider file
    await deleteSpiderFile(page, {fileName});

    // expect file not exists
    await expect(await page.$(`.el-tree-node[data-key="/${fileName}"]`)).toBeNull();
  });
});
