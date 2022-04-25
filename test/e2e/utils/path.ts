import {join, resolve} from 'path';

export const getRootPath = (): string => {
  return resolve(join(__dirname, '..', '..'));
};
