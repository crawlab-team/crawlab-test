export const getRandomName = (prefix?: string): string => {
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 1e3)}`;
};

export const getTestCaseCamelCaseName = (title: string) => {
  const words = title.split(' ').map((w, i) => {
    const chars = w.split('');
    if (i > 0) {
      chars[0] = chars[0].toUpperCase();
    }
    return chars.join('');
  });
  return words.join('');
};
