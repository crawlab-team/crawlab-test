import {expect} from '@playwright/test';
import {resolve, join} from 'path';
import {readFileSync} from 'fs';
import {clickTableCellByKey} from '../../../actions/components/table';
import {getRandomName} from '../../../utils/name';
import {createSpider, deleteSpider} from '../../../actions/spider/common';
import {
  uploadSpiderDirectory,
  uploadSpiderDirectoryFromList,
  uploadSpiderFiles,
  uploadSpiderFilesFromList
} from '../../../actions/spider/upload';
import {expandSpiderDirectory, openSpiderFile} from '../../../actions/spider/file';
import {goToNavTab} from '../../../actions/components/nav';
import {getFileContent} from '../../../actions/components/file';
import {test} from '../../../base/authTest';

test.describe.serial('spider:upload', () => {
  // settings
  const name = getRandomName('spider');
  const cmd = 'python3 main.py';
  const localDirectoryPath = resolve(join(__dirname, 'template', 'upload'));
  const mainFileName = 'main.py';
  const mainFilePath = join(localDirectoryPath, mainFileName);
  const mainFileContent = readFileSync(mainFilePath);
  const configDirectoryName = 'config';
  const configFileName = 'config/config.py';
  const configFilePath = join(localDirectoryPath, configFileName);
  const configFileContent = readFileSync(configFilePath);
  process.chdir(localDirectoryPath);

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    // create spider
    await createSpider(page, {name, cmd});
  });

  test.afterEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    // delete spider
    await deleteSpider(page, {name});
    await page.reload();
  });

  test('should upload spider directory', async ({page}) => {
    // click on created spider
    await clickTableCellByKey(page, 'name', name);

    // go to files tab
    await goToNavTab(page, 'files');

    // upload directory
    await uploadSpiderDirectory(page, {directoryPath: localDirectoryPath});

    // expect uploaded files to exist
    await expect(await page.$(`.el-tree-node[data-key="/${mainFileName}"]`)).not.toBeNull();
    await expect(await page.$(`.el-tree-node[data-key="/${configFileName}"]`)).not.toBeNull();

    // open file main.py and expect content to be the same as original
    await openSpiderFile(page, {fileName: mainFileName});
    let mainFileContentActual = await getFileContent(page);
    await expect(mainFileContentActual.trim()).toEqual(mainFileContent.toString().trim());

    // expand directory config
    await expandSpiderDirectory(page, {directoryName: configDirectoryName});

    // open file config/config.py and expect content to be the same as original
    await openSpiderFile(page, {fileName: configFileName});
    const configFileContentActual = await getFileContent(page);
    await expect(configFileContentActual.trim()).toEqual(configFileContent.toString().trim());
  });

  test('should upload spider file', async ({page}) => {
    // click on created spider
    await clickTableCellByKey(page, 'name', name);

    // go to files tab
    await goToNavTab(page, 'files');

    // upload files
    await uploadSpiderFiles(page, {
      files: [
        {name: mainFileName, mimeType: '', buffer: mainFileContent},
      ]
    });

    // expect uploaded files to exist
    await expect(await page.$(`.el-tree-node[data-key="/${mainFileName}"]`)).not.toBeNull();

    // open file main.py and expect content to be the same as original
    await openSpiderFile(page, {fileName: mainFileName});
    let mainFileContentActual = await getFileContent(page);
    await expect(mainFileContentActual.trim()).toEqual(mainFileContent.toString().trim());
  });

  test('should upload spider directory from list', async ({page}) => {
    // upload directory
    await uploadSpiderDirectoryFromList(page, {spiderName: name, directoryPath: localDirectoryPath});

    // click on created spider
    await clickTableCellByKey(page, 'name', name);

    // go to files tab
    await goToNavTab(page, 'files');
    await page.waitForTimeout(500);

    // expand directory config
    await expandSpiderDirectory(page, {directoryName: configDirectoryName});

    // expect uploaded files to exist
    await expect(await page.$(`.el-tree-node[data-key="/${mainFileName}"]`)).not.toBeNull();
    await expect(await page.$(`.el-tree-node[data-key="/${configFileName}"]`)).not.toBeNull();
  });

  test('should upload spider file from list', async ({page}) => {
    // upload file
    await uploadSpiderFilesFromList(page, {
      spiderName: name,
      files: [
        {name: mainFileName, mimeType: '', buffer: mainFileContent},
      ]
    });

    // click on created spider
    await clickTableCellByKey(page, 'name', name);

    // go to files tab
    await goToNavTab(page, 'files');

    // expect uploaded files to exist
    await expect(await page.$(`.el-tree-node[data-key="/${mainFileName}"]`)).not.toBeNull();
  });
});
