export const parseBoolean = (value: string): boolean => {
  value = value.toLowerCase();
  if (value === 'true' || value === 't' || value === '1') return true;
  if (value === 'false' || value === 'f' || value === '0') return false;
  return !!value;
};
