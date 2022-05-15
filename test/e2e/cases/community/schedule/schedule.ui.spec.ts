import {test} from '@/e2e/base/authTest';
import {goToListPage, goToNavTab, selectNavSidebarItem} from '@/e2e/actions/components/nav';
import {getRandomName} from '@/e2e/utils/name';
import {createSpider} from '@/e2e/actions/spider/common';
import {join, resolve} from 'path';
import {uploadSpiderDirectoryFromList} from '@/e2e/actions/spider/upload';
import {clickTableCellByKey, getTableCellByKey} from '@/e2e/actions/components/table';
import {createSchedule, deleteSchedule} from '@/e2e/actions/schedule/common';
import {expect} from '@playwright/test';

test.describe.serial('schedule:ui', () => {
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
    // very slow test
    test.setTimeout(300 * 1e3);

    // page
    const page = await browser.newPage();

    // create spiders
    await goToListPage(page, 'spiders');
    for (let i = 0; i < spiders.length; i++) {
      // spider
      const spider = spiders[i];

      // create spider
      await createSpider(page, {name: spider.name, cmd: spider.cmd});

      // upload files
      const directoryPath = resolve(join(__dirname, 'template', 'ui', `spider${i + 1}`));
      await uploadSpiderDirectoryFromList(page, {spiderName: spider.name, directoryPath});
    }

    // create schedules
    await goToListPage(page, 'schedules');
    for (let i = 0; i < spiders.length; i++) {
      // spider
      const spider = spiders[i];

      // schedule
      const schedule = schedules[i];

      // create schedule
      await createSchedule(page, {name: schedule.name, spiderName: spider.name, cron: '* * * * *', enabled: true});
    }

    // wait for schedules to trigger
    await goToListPage(page, 'tasks');
    await getTableCellByKey(page, 'schedule_id', schedules[0].name);
    await getTableCellByKey(page, 'schedule_id', schedules[1].name);

    // close browser
    await browser.close();
  });

  test.beforeEach(async ({page}) => {
    await goToListPage(page, 'schedules');
  });

  test.afterAll(async ({browser}) => {
    const page = await browser.newPage();
    await goToListPage(page, 'schedules');
    for (const schedule of schedules) {
      await deleteSchedule(page, {name: schedule.name});
    }
  });

  test('should switch schedule overview', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', schedules[0].name);
    await goToNavTab(page, 'overview');

    // expect name to be correct
    await expect(page.locator('#name input')).toHaveValue(schedules[0].name);

    // select nav sidebar item
    await selectNavSidebarItem(page, schedules[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/overview/);

    // expect name to be correct
    await expect(page.locator('#name input')).toHaveValue(schedules[1].name);
  });

  test('should switch schedule tasks', async ({page}) => {
    // go to tab
    await clickTableCellByKey(page, 'name', schedules[0].name);
    await goToNavTab(page, 'tasks');

    // expect to contain schedule
    await expect(getTableCellByKey(page, 'schedule_id', schedules[0].name)).not.toBeNull();

    // select nav sidebar item
    await selectNavSidebarItem(page, schedules[1].name);

    // expect url to be correct
    await expect(page).toHaveURL(/tasks/);

    // expect to contain schedule
    await expect(await getTableCellByKey(page, 'schedule_id', schedules[1].name)).not.toBeNull();
  });
});
