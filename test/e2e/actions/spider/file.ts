import {Page} from '@playwright/test';

interface CreateSpiderFileOptions {
  fileName?: string;
  fileContent?: string;
  targetName?: string;
  waitDuration?: number;
}

interface CreateSpiderDirectoryOptions {
  directoryName?: string;
  targetName?: string;
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

interface CloneSpiderFileOptions {
  fileName?: string;
  newFileName?: string;
  waitDuration?: number;
}

interface MoveSpiderFileOptions {
  fileName?: string;
  targetName?: string;
  waitDuration?: number;
}

interface DeleteSpiderFileOptions {
  fileName?: string;
  waitDuration?: number;
}

interface RightClickSpiderFileOptions {
  targetName?: string;
  action?: string;
}

const getDataKey = (targetName: string): string => {
  return (!targetName || targetName === '~') ? '~' : ('/' + targetName);
};

export const createSpiderFile = async (page: Page, {
  fileName,
  fileContent,
  targetName,
  waitDuration
}: CreateSpiderFileOptions = {}) => {
  // right click spider file with action
  await rightClickSpiderFileAction(page, {targetName, action: 'new-file'});

  // enter file name and click confirm button
  await page.type('.el-message-box .el-input', fileName);
  await page.click('.el-message-box .confirm-btn');

  // double-click on created file
  await openSpiderFile(page, {fileName});

  // enter file content
  await editSpiderFileContent(page, {fileContent, waitDuration});
};

export const createSpiderDirectory = async (page: Page, {
  directoryName,
  targetName,
  waitDuration
}: CreateSpiderDirectoryOptions = {}) => {
  // right click spider file with action
  await rightClickSpiderFileAction(page, {targetName, action: 'new-directory'});

  // enter new directory name
  await page.fill('.el-message-box .el-input input', directoryName);
  await page.click('.el-message-box .confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
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
  await rightClickSpiderFileAction(page, {targetName: fileName, action: 'rename'});

  // enter new file name and click on confirm button
  await page.fill('.el-message-box .el-input input', newFileName);
  await page.click('.el-message-box .confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const moveSpiderFile = async (page: Page, {fileName, targetName, waitDuration}: MoveSpiderFileOptions = {}) => {
  // file
  const file = await page.locator(`.el-tree-node[data-key="${getDataKey(fileName)}"]`);

  // target
  const target = await page.locator(`.el-tree-node[data-key="${getDataKey(targetName)}"]`);

  // move file to target
  await file.dragTo(target);
  await page.waitForTimeout(waitDuration || 1000);
};

export const cloneSpiderFile = async (page: Page, {
  fileName,
  newFileName,
  waitDuration
}: CloneSpiderFileOptions = {}) => {
  // right-click on file with action
  await rightClickSpiderFileAction(page, {targetName: fileName, action: 'clone'});

  // enter new file name and click on confirm button
  await page.fill('.el-message-box .el-input input', newFileName);
  await page.click('.el-message-box .confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const deleteSpiderFile = async (page: Page, {fileName, waitDuration}: DeleteSpiderFileOptions = {}) => {
  // right-click on file with action
  await rightClickSpiderFileAction(page, {targetName: fileName, action: 'delete'});

  // click on the confirm button
  await page.click('.el-message-box .confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const rightClickSpiderFileAction = async (page: Page, {targetName, action}: RightClickSpiderFileOptions) => {
  // right-click on file
  const targetNode = await page.$(`.el-tree-node[data-key="${getDataKey(targetName)}"] .el-tree-node__content`);
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
