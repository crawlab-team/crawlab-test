import * as path from 'test/e2e/utils/path';

export const getRootPath = (): string => {
  return path.resolve(path.join(__dirname, '..', '..'));
};
