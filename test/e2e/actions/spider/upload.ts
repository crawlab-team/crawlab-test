import {Page} from '@playwright/test';
import {readFileSync} from 'fs';
import {extname} from 'path';
import {eachFileSync} from 'rd';
import {getType} from 'mime';
import {BaseActionOptions} from '../base';
import {clickTableCellActionByKey, getTableRowByKey} from '../components/table';

interface File {
  name: string;
  mimeType: string;
  buffer: Buffer;
}

interface UploadSpiderDirectoryOptions extends BaseActionOptions {
  directoryPath?: string;
  clickUploadBtn?: boolean;
}

interface UploadSpiderFilesOptions extends BaseActionOptions {
  files?: File[];
  clickUploadBtn?: boolean;
  clickModeSelectBtn?: boolean;
}

interface UploadSpiderDirectoryFromListOptions extends BaseActionOptions {
  spiderName?: string;
  directoryPath?: string;
}

interface UploadSpiderFilesFromListOptions extends BaseActionOptions {
  spiderName?: string;
  files?: File[];
}

export const uploadSpiderDirectory = async (page: Page, {
  directoryPath,
  clickUploadBtn,
  waitDuration,
}: UploadSpiderDirectoryOptions = {}) => {
  // files
  const files: File[] = [];

  // iterate directory recursively to get all files
  eachFileSync(directoryPath, (filename: string) => {
    const ext = extname(filename).replace(/^\./, '');
    const mimeType = getType(ext) || '';
    files.push({
      name: `.${filename.replace(directoryPath, '')}`,
      mimeType,
      buffer: readFileSync(filename),
    });
  });

  // upload files
  await uploadSpiderFiles(page, {files, clickUploadBtn, clickModeSelectBtn: false, waitDuration});
};

export const uploadSpiderFiles = async (page: Page, {
  files,
  clickUploadBtn,
  clickModeSelectBtn,
  waitDuration,
}: UploadSpiderFilesOptions = {}) => {
  // click on upload file button
  if (clickUploadBtn || clickUploadBtn === undefined) await page.click('#upload-btn button');

  // select upload type
  if (clickModeSelectBtn || clickModeSelectBtn === undefined) await page.click('.file-upload .mode-select .el-radio.files');

  // click on folder upload button
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.locator('.el-dialog .file-upload .file-upload-action').click(),
  ]);

  // add files
  await fileChooser.setFiles(files);

  // click on confirm button
  await page.click('.el-dialog.visible #confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const uploadSpiderDirectoryFromList = async (page: Page, {
  spiderName,
  directoryPath,
  waitDuration
}: UploadSpiderDirectoryFromListOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'name', text: spiderName, action: '.upload-files-btn', waitDuration});
  await uploadSpiderDirectory(page, {directoryPath, clickUploadBtn: false, waitDuration});
};

export const uploadSpiderFilesFromList = async (page: Page, {
  spiderName,
  files,
  waitDuration
}: UploadSpiderFilesFromListOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'name', text: spiderName, action: '.upload-files-btn', waitDuration});
  await uploadSpiderFiles(page, {files, clickUploadBtn: false, waitDuration});
};
