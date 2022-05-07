import {join} from 'path';
import {getRootPath} from '../e2e/utils/path';
import {existsSync, mkdirSync, writeFileSync, readFileSync} from 'fs';
import {DEFAULT_SDK_STATE_FILE_NAME} from './constants/default';

export interface TestRunState {
  runId?: number;
  caseIds?: number[];
}

export const getTestRunDirectoryPath = () => {
  return join(getRootPath(), 'data', 'sdk');
};

export const saveTestRunState = (state: TestRunState, stateFileName?: string) => {
  const dataDir = join(getRootPath(), 'data', 'sdk');
  if (!existsSync(dataDir)) mkdirSync(dataDir, {recursive: true});
  const stateFilePath = getTestRunStatePath(stateFileName);
  writeFileSync(stateFilePath, JSON.stringify(state));
};

export const getTestRunStatePath = (storageFileName?: string) => {
  return join(getTestRunDirectoryPath(), storageFileName || DEFAULT_SDK_STATE_FILE_NAME);
};

export const getTestRunState = (stateFileName?: string): TestRunState => {
  const stateFilePath = getTestRunStatePath(stateFileName);
  const data = readFileSync(stateFilePath);
  return JSON.parse(data.toString());
};
