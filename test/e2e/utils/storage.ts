import {join} from 'path';
import {getRootPath} from './path';
import {existsSync, mkdirSync} from 'fs';
import {BrowserContext} from '@playwright/test';
import {DEFAULT_STORAGE_FILE_NAME} from '../constants/default';

export const getStorageDirectoryPath = () => {
  return join(getRootPath(), 'data', 'e2e');
};

export const saveStorageState = async (context: BrowserContext, storageFileName?: string) => {
  const dataDir = getStorageDirectoryPath();
  if (!existsSync(dataDir)) mkdirSync(dataDir, {recursive: true});
  const storageFilePath = getStorageFilePath(storageFileName);
  await context.storageState({path: storageFilePath});
};

export const getStorageFilePath = (storageFileName?: string): string => {
  return join(getStorageDirectoryPath(), storageFileName || DEFAULT_STORAGE_FILE_NAME);
};
