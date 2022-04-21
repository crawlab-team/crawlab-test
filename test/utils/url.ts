import {DEFAULT_APP_URL} from '../constants/default';

export const getAppUrl = (): string => {
  return process.env.APP_URL || DEFAULT_APP_URL;
};
