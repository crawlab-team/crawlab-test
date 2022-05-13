import {test} from '../../../base/authTest';
import {createSpider, runSpider} from '../../../actions/spider/common';
import {getRandomName} from '../../../utils/name';
import {clickTableCellByKey, getTableCellByKey, getTableCellByTargetKey} from '../../../actions/components/table';
import {goToListPage, goToNavTab, selectNavSidebarItem} from '../../../actions/components/nav';
import {expect} from '@playwright/test';
import {uploadSpiderDirectoryFromList} from '../../../actions/spider/upload';
import {join, resolve} from 'path';
import {createSchedule} from '../../../actions/schedule/common';

test.describe.serial('spider:ui', () => {
  const spiders = [
    {
      name: getRandomName('spider'),
      cmd: 'python3 main.py',
    },
    {
      name: getRandomName('spider'),
      cmd: 'python3 main2.py',
    },
  ];
  const schedules = [
    {
      name: getRandomName('schedule'),
    },
    {
      name: getRandomName('schedule'),
    }
  ];

  test.beforeAll(async ({browser}) => {
    // page
    const page = await browser.newPage({});

    // prevent timeout
    page.setDefaultTimeout(90 * 1e3);

    // go to page
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');

    for (let i = 0; i < spiders.length; i++) {
      // spider
      const spider = spiders[i];

      // create spider
      await createSpider(page, {name: spider.name, cmd: spider.cmd});

      // upload files
      const directoryPath = resolve(join(__dirname, 'template', 'ui', `spider${i + 1}`));
      await uploadSpiderDirectoryFromList(page, {spiderName: spider.name, directoryPath});

      // run task
      await runSpider(page, {name: spider.name});
      const elLs = await getTableCellByTargetKey(page, 'name', spider.name, 'last_status');
      await elLs.waitForSelector('.task-status.el-tag--success');
    }

    await goToListPage(page, 'schedules');
    for (let i = 0; i < spiders.length; i++) {
      // spider
      const spider = spiders[i];

      // schedule
      const schedule = schedules[i];

      // create schedule
      await createSchedule(page, {name: schedule.name, spiderName: spider.name, cron: '* * * * *', enabled: false});
    }
  });

  test.beforeEach(async ({page}) => {
    await page.goto('/#/spiders');
    await page.waitForSelector('#add-btn');
  });

  test('should switch spider overview', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', spiders[0].name);
    await goToNavTab(page, 'overview');

    // expect name to be correct
    await expect(page.locator('#name')).toHaveValue(spiders[0].name);

    // select nav sidebar item
    await selectNavSidebarItem(page, spiders[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/overview/);

    // expect name to be correct
    await expect(page.locator('#name')).toHaveValue(spiders[1].name);
  });

  test('should switch spider files', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', spiders[0].name);
    await goToNavTab(page, 'files');

    // expect file to exist
    await expect(await page.$(`.el-tree-node[data-key="/main.py"]`)).not.toBeNull();

    // select nav sidebar item
    await selectNavSidebarItem(page, spiders[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/files/);

    // expect file to exist
    await expect(await page.$(`.el-tree-node[data-key="/main2.py"]`)).not.toBeNull();
  });

  test('should switch spider git', async ({page}) => {
    // TODO: implement
  });

  test('should switch spider tasks', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', spiders[0].name);
    await goToNavTab(page, 'tasks');

    // expect to contain spider
    await expect(getTableCellByKey(page, 'spider_id', spiders[0].name)).not.toBeNull();

    // select nav sidebar item
    await selectNavSidebarItem(page, spiders[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/tasks/);

    // expect to contain spider
    await expect(await getTableCellByKey(page, 'spider_id', spiders[1].name)).not.toBeNull();
  });

  test.only('should switch spider schedules', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', spiders[0].name);
    await goToNavTab(page, 'schedules');

    // expect to contain spider
    await expect(await page.textContent('.table')).toContain(schedules[0].name);

    // select nav sidebar item
    await selectNavSidebarItem(page, spiders[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/schedules/);

    // expect to contain spider
    await expect(await page.textContent('.table')).toContain(schedules[1].name);
  });

  test('should switch spider data', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', spiders[0].name);
    await goToNavTab(page, 'data');

    // expect data to be correct
    await expect(await page.textContent('.table')).toContain('world');

    // select nav sidebar item
    await selectNavSidebarItem(page, spiders[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/data/);

    // expect to contain spider
    await expect(await page.textContent('.table')).toContain('crawlab');
  });
});
