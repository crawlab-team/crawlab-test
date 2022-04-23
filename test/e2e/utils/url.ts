import {DEFAULT_API_ENDPOINT, DEFAULT_APP_URL} from '../constants/default';

export const getAppUrl = (): string => {
  return process.env.APP_URL || DEFAULT_APP_URL;
};

export const getApiEndpoint = (): string => {
  return process.env.API_ENDPOINT || DEFAULT_API_ENDPOINT;
};
