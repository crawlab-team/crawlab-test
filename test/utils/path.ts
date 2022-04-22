import * as path from 'path';

export const getRootPath = (): string => {
  return path.resolve(path.join(__dirname, '..', '..'));
};
