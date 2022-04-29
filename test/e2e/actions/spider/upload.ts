import {Page} from '@playwright/test';
import {readFileSync} from 'fs';
import {extname} from 'path';
import {eachFileSync} from 'rd';
import {getType} from 'mime';
import {BaseActionOptions} from '../base';

interface File {
  name: string;
  mimeType: string;
  buffer: Buffer;
}

interface UploadSpiderDirectoryOptions extends BaseActionOptions {
  directoryPath?: string;
}

interface UploadSpiderFilesOptions extends BaseActionOptions {
  files?: File[];
}

export const uploadSpiderDirectory = async (page: Page, {
  directoryPath,
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

  // click on upload file button
  await page.click('#upload-btn button');

  // click on folder upload button
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.locator('.el-dialog .folder-upload button').click(),
  ]);

  // add files
  await fileChooser.setFiles(files);

  // click on confirm button
  await page.click('#confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const uploadSpiderFiles = async (page: Page, {
  files,
  waitDuration,
}: UploadSpiderFilesOptions) => {
  // click on upload file button
  await page.click('#upload-btn button');

  // select upload type
  await page.click('.file-upload .mode-select .el-radio.files');

  // click on folder upload button
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.locator('.el-dialog .el-upload').click(),
  ]);

  // add files
  await fileChooser.setFiles(files);

  // click on confirm button
  await page.click('#confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};
