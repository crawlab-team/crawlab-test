import {Page} from '@playwright/test';
import {ZERO_WIDTH_SPACE} from '../../constants/file';

export const getFileContent = async (page: Page): Promise<string> => {
  const lines = await page.evaluate(() => {
    const lines = [];
    document.querySelectorAll('.CodeMirror .CodeMirror-line')
      .forEach(el => lines.push(el.textContent));
    return lines;
  });
  return lines.join('\n').split(ZERO_WIDTH_SPACE).join('');
};
