import {Page} from '@playwright/test';
import {ZERO_WIDTH_SPACE} from '../../constants/file';
import {BaseActionOptions} from '../base';

interface CreateSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
  fileContent?: string;
  targetName?: string;
}

interface CreateSpiderDirectoryOptions extends BaseActionOptions {
  directoryName?: string;
  targetName?: string;
}

interface OpenSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
}

interface ExpandSpiderDirectoryOptions extends BaseActionOptions {
  directoryName?: string;
}

interface EditSpiderFileContentOptions extends BaseActionOptions {
  fileContent?: string;
}

interface RenameSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
  newFileName?: string;
}

interface CloneSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
  newFileName?: string;
}

interface MoveSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
  targetName?: string;
}

interface DeleteSpiderFileOptions extends BaseActionOptions {
  fileName?: string;
}

interface RightClickSpiderFileOptions extends BaseActionOptions {
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

export const expandSpiderDirectory = async (page: Page, {
  directoryName,
  waitDuration,
}: ExpandSpiderDirectoryOptions = {}) => {
  await page.click(`.el-tree-node[data-key="/${directoryName}"] .el-tree-node__expand-icon`);
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
  const lines = await page.evaluate(() => {
    const lines = [];
    document.querySelectorAll('.code-mirror-editor .CodeMirror-line')
      .forEach(el => lines.push(el.textContent));
    return lines;
  });
  return lines.join('\n').split(ZERO_WIDTH_SPACE).join('');
};
