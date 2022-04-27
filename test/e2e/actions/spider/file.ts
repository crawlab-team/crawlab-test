import {clickTableCellByKey} from '../../utils/table';
import {Page} from '@playwright/test';

interface CreateSpiderFileOptions {
  fileName?: string;
  fileContent?: string;
  targetDataKey?: string;
  waitDuration?: number;
}

interface OpenSpiderFileOptions {
  fileName?: string;
  waitDuration?: number;
}

interface EditSpiderFileContentOptions {
  fileContent?: string;
  waitDuration?: number;
}

interface RenameSpiderFileOptions {
  fileName?: string;
  newFileName?: string;
  waitDuration?: number;
}

interface RightClickSpiderFileOptions {
  fileName?: string;
  action?: string;
}

const getDataKey = (fileName: string): string => {
  return fileName === '~' ? fileName : ('/' + fileName);
};

export const createSpiderFile = async (page: Page, {
  fileName,
  fileContent,
  targetDataKey,
  waitDuration
}: CreateSpiderFileOptions = {}) => {
  // click on files tab
  const elFilesTab = await page.$('.el-menu-item.files');
  await elFilesTab.click();

  // right click spider file with action
  await rightClickSpiderFileAction(page, {fileName: targetDataKey || '~', action: 'new-file'});

  // enter file name and click confirm button
  await page.type('.el-message-box .el-input', fileName);
  await page.click('.el-message-box .confirm-btn');

  // double-click on created file
  await openSpiderFile(page, {fileName});

  // enter file content
  await editSpiderFileContent(page, {fileContent, waitDuration});
};

export const openSpiderFile = async (page: Page, {fileName, waitDuration}: OpenSpiderFileOptions = {}) => {
  await page.dblclick(`.el-tree-node[data-key="/${fileName}"]`);
  await page.click('.CodeMirror');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editSpiderFileContent = async (page: Page, {
  fileContent,
  waitDuration
}: EditSpiderFileContentOptions = {}) => {
  // edit file content
  await page.evaluate((fileContent) => {
    // @ts-ignore
    document.querySelector('.CodeMirror').CodeMirror.setValue(fileContent);
  }, fileContent);
  await page.waitForTimeout(waitDuration || 1000);

  // click on save button
  await page.click('#save-btn button');
  await page.waitForTimeout(waitDuration || 1000);
};

export const renameSpiderFile = async (page: Page, {
  fileName,
  newFileName,
  waitDuration,
}: RenameSpiderFileOptions = {}) => {
  // right click spider file with action
  await rightClickSpiderFileAction(page, {fileName, action: 'rename'});

  // enter new file name and click on confirm button
  await page.fill('.el-message-box .el-input input', newFileName);
  await page.click('.el-message-box .confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const rightClickSpiderFileAction = async (page: Page, {fileName, action}: RightClickSpiderFileOptions) => {
  // right-click on root node
  const targetNode = await page.$(`.el-tree-node[data-key="${getDataKey(fileName)}"]`);
  await targetNode.click({button: 'right'});

  // click on new file button
  await page.click(`.context-menu[aria-hidden=false] .context-menu-item.${action}`);
};

export const getSpiderFileContent = async (page: Page): Promise<string> => {
  return await page.evaluate(() => {
    const lines = [];
    document.querySelectorAll('.code-mirror-editor .CodeMirror-line')
      .forEach(el => lines.push(el.textContent));
    return lines.join('\n');
  });
};
