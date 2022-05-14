import {expect} from '@playwright/test';
import {createSpider} from '@/e2e/actions/spider/common';
import {getRandomName} from '@/e2e/utils/name';
import {uploadSpiderDirectory} from '@/e2e/actions/spider/upload';
import {join, resolve} from 'path';
import {
  clickTableCellActionByKey,
  clickTableCellByKey,
  getTableCellByTargetKey,
  getTableCellTextsByKey, waitForTableColumnToBeReady
} from '@/e2e/actions/components/table';
import {cancelTask, createTask, deleteTask, viewTaskData, viewTaskLogs} from '@/e2e/actions/task/common';
import {goToListPage, goToNavTab} from '@/e2e/actions/components/nav';
import {getFileContent} from '@/e2e/actions/components/file';
import {test} from '@/e2e/base/authTest';

test.describe.serial('task:common', () => {
  const spiderName = getRandomName('spider');
  const spiderCmd = 'python3 main.py';
  const longTaskCmd = 'python3 long_task.py';
  const logContent = 'hello world';
  const localDirectoryPath = resolve(join(__dirname, 'template', 'common'));

  test.beforeAll(async ({browser}) => {
    const page = await browser.newPage();
    await goToListPage(page, 'spiders');
    await createSpider(page, {name: spiderName, cmd: spiderCmd});
    await clickTableCellByKey(page, 'name', spiderName);
    await page.waitForSelector('.nav-sidebar');
    await goToNavTab(page, 'files');
    process.chdir(localDirectoryPath);
    await uploadSpiderDirectory(page, {directoryPath: localDirectoryPath});
  });

  test.beforeEach(async ({page}) => {
    await goToListPage(page, 'tasks');
  });

  test('should create task', async ({page}) => {
    await createTask(page, {spiderName});
    const names = await getTableCellTextsByKey(page, 'spider_id');

    // expect spider name to exist
    await expect(names).toContain(spiderName);

    // expect result count to be greater than 0
    const elRc = await getTableCellByTargetKey(page, 'spider_id', spiderName, 'stat_result_count');
    await expect(elRc).not.toBeNull();
    await elRc.waitForSelector('.task-results.el-tag--success');
    await expect(await elRc.textContent()).toEqual('1');
  });

  test('should view task logs', async ({page}) => {
    await clickTableCellActionByKey(page, {key: 'spider_id', text: spiderName, action: '.view-btn'});
    await goToNavTab(page, 'logs');
    let fileContent = (await getFileContent(page)).trim();
    await expect(fileContent).toEqual(logContent);

    await page.click('#back-btn');
    await page.waitForSelector('#add-btn');
    await viewTaskLogs(page, {spiderName});
    fileContent = (await getFileContent(page)).trim();
    await expect(fileContent).toEqual(logContent);
  });

  test('should view task data', async ({page}) => {
    await viewTaskData(page, {spiderName});
    await page.waitForTimeout(500);
    const values = await getTableCellTextsByKey(page, 'hello');
    await expect(values).toContain('world');
  });

  test('should restart task', async ({page}) => {
    await clickTableCellActionByKey(page, {key: 'spider_id', text: spiderName, action: '.restart-btn'});
    // click confirm button
    await page.click('.restart-confirm-btn');
    await page.waitForFunction(() => !document.querySelector('.el-message-box'));
    await page.waitForTimeout(500);
    const names = (await getTableCellTextsByKey(page, 'spider_id')).filter(n => n === spiderName);
    await expect(names.length).toEqual(2);
  });

  test('should delete task', async ({page}) => {
    await waitForTableColumnToBeReady(page, 'spider_id', spiderName);
    await deleteTask(page, {spiderName});
    const names = (await getTableCellTextsByKey(page, 'spider_id')).filter(n => n === spiderName);
    await expect(names.length).toEqual(1);
  });

  test('should cancel task', async ({page}) => {
    await createTask(page, {
      spiderName,
      cmd: longTaskCmd,
    });
    await waitForTableColumnToBeReady(page, 'spider_id', spiderName);
    await cancelTask(page, {spiderName});
    await page.waitForSelector('.el-table__cell.status .task-status.el-tag--info');
  });
});
