import {join} from 'test/e2e/utils/path';
import {getRootPath} from './path';
import {existsSync, mkdirSync} from 'fs';
import {BrowserContext} from '@playwright/test';
import {DEFAULT_STORAGE_FILE_NAME} from '../constants/default';

export const saveStorageState = async (context: BrowserContext, storageFileName?: string) => {
  const dataDir = join(getRootPath(), 'data');
  if (!existsSync(dataDir)) mkdirSync(dataDir);
  const storageFilePath = getStorageFilePath(storageFileName);
  await context.storageState({path: storageFilePath});
};

export const getStorageFilePath = (storageFileName?: string): string => {
  return join(getRootPath(), 'data', storageFileName || DEFAULT_STORAGE_FILE_NAME);
};
