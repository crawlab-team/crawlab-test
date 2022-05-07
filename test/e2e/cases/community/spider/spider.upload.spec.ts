import {expect} from '@playwright/test';
import {resolve, join} from 'path';
import {readFileSync} from 'fs';
import {clickTableCellByKey} from '../../../actions/components/table';
import {getRandomName} from '../../../utils/name';
import {createSpider} from '../../../actions/spider/common';
import {uploadSpiderDirectory, uploadSpiderFiles} from '../../../actions/spider/upload';
import {expandSpiderDirectory, openSpiderFile} from '../../../actions/spider/file';
import {goToNavTab} from '../../../actions/components/nav';
import {getFileContent} from '../../../actions/components/file';
import {wrapUpdateTestCaseResultFn} from '../../../../sdk';
import {caseMapping} from '../../../../sdk/mapping/case';
import {test} from '../../../base/authTest';

test.describe.serial('spider: upload', () => {
  test.afterEach(wrapUpdateTestCaseResultFn(test, caseMapping.community.spider.upload));

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

  test.beforeAll(async ({browser}) => {
    const page = await browser.newPage();

    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    // create spider
    await createSpider(page, {name, cmd});
  });

  test.beforeEach(async ({page}) => {
    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    // click on created spider
    await clickTableCellByKey(page, 'name', name);
    await page.waitForSelector('.nav-sidebar');

    // click on files tab
    await goToNavTab(page, 'files');
  });

  test('should upload spider directory', async ({page}) => {
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
});
