import {parseBoolean} from '@/utils/dataType';

export const getTimeout = (): number => {
  return process.env.TIMEOUT ? (Number(process.env.TIMEOUT) * 1000) : 60 * 1000;
};

export const getRetries = (): number => {
  return process.env.RETRIES ? Number(process.env.RETRIES) : 2;
};

export const getWorkers = (): number => {
  return process.env.WORKERS ? Number(process.env.WORKERS) : 2;
};

export const getHeadless = (): boolean => {
  return !parseBoolean(process.env.DISPLAY_BROWSER);
};
