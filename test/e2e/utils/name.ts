export const getRandomName = (prefix?: string): string => {
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 1e3)}`;
};
