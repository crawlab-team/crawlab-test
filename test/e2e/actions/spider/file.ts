import {createSpider} from './operate';
import {clickTableCellByKey} from '../../utils/table';
import {Page} from '@playwright/test';

interface CreateSpiderFileOptions {
  spiderName?: string;
  fileName?: string;
  fileContent?: string;
}

interface OpenSpiderFileOptions {
  fileName?: string;
  waitDuration?: number;
}

export const createSpiderFile = async (page: Page, opts: CreateSpiderFileOptions) => {
  if (!opts) opts = {};
  const {
    spiderName,
    fileName,
    fileContent,
  } = opts;

  // click on created spider
  await clickTableCellByKey(page, 'name', spiderName);
  await page.waitForSelector('.nav-sidebar');

  // click on files tab
  const elFilesTab = await page.$('.el-menu-item.files');
  await elFilesTab.click();

  // right-click on root node
  const elRootNode = await page.$('.file-editor-nav-menu .el-tree-node');
  await elRootNode.click({button: 'right'});

  // click on new file button
  await page.click('.context-menu-item.new-file');

  // enter file name and click confirm button
  await page.type('.el-message-box .el-input', fileName);
  await page.click('.el-message-box .confirm-btn');

  // double-click on created file
  await openSpiderFile(page, {fileName});

  // enter file content
  await page.evaluate((fileContent) => {
    // @ts-ignore
    document.querySelector('.CodeMirror').CodeMirror.setValue(fileContent);
  }, fileContent);
  await page.waitForTimeout(1000);

  // click on save button
  await page.click('#save-btn button');
  await page.waitForTimeout(1000);
};

export const openSpiderFile = async (page: Page, opts: OpenSpiderFileOptions) => {
  if (!opts) opts = {};
  const {
    fileName,
    waitDuration,
  } = opts;

  await page.dblclick(`.el-tree-node[data-key="/${fileName}"]`);
  await page.click('.CodeMirror');
  await page.waitForTimeout(waitDuration || 1000);
};
