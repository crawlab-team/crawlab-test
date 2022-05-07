import axios, {AxiosRequestConfig} from 'axios';

const endpoint = process.env.CODING_API_ENDPOINT;
const token = process.env.CODING_API_TOKEN;

export const request = async ({url, method, params, data}: AxiosRequestConfig) => {
  const res = await axios.request({
    url: url || endpoint,
    method,
    params,
    data,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    }
  });
  return res?.data;
};

export const post = async (data) => {
  return await request({method: 'POST', data});
};

export const get = async (params) => {
  return await request({method: 'GET', params});
};
