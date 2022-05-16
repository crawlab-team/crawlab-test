import {expect} from '@playwright/test';
import {getRandomName} from '@/e2e/utils/name';
import {createSchedule, deleteSchedule, editSchedule} from '@/e2e/actions/schedule/common';
import {clickTableCellByKey, getTableCellTextsByKey} from '@/e2e/actions/components/table';
import {createSpider} from '@/e2e/actions/spider/common';
import {goToListPage, goToNavTab} from '@/e2e/actions/components/nav';
import {test} from '@/e2e/base/authTest';

test.describe.serial('schedule:common', () => {
  const schedule = {
    name: getRandomName('schedule'),
    cron: '* * * * *',
    enabled: true,
    spiderName: getRandomName('spider'),
    description: getRandomName('schedule_description'),
  };
  const scheduleEdited = {
    name: schedule.name + '_edited',
    cron: '0 * * * *',
    enabled: false,
    spiderName: schedule.spiderName,
    description: schedule.description + '_edited',
  };

  test.beforeAll(async ({browser}) => {
    // page
    const page = await browser.newPage();

    // go to page
    await goToListPage(page, 'spiders');

    // create spider
    await createSpider(page, {name: schedule.spiderName, cmd: 'echo hello'});

    // close page
    await page.close();
  });

  test('should create schedule', async ({page}) => {
    // go to list page
    await goToListPage(page, 'schedules');

    // create schedule
    await createSchedule(page, {...schedule});

    // expect table to display created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).toContain(schedule.name);
  });

  test('should edit schedule', async ({page}) => {
    // go to list page
    await goToListPage(page, 'schedules');

    // go to detail page
    await clickTableCellByKey(page, 'name', schedule.name);
    await goToNavTab(page, 'overview');

    // edit schedule
    await editSchedule(page, {...scheduleEdited});

    // refresh page
    await page.reload();
    await goToNavTab(page, 'overview');

    // expect fields to be the same as edited
    await expect(await page.inputValue('#name input')).toEqual(scheduleEdited.name);
    await expect(await page.inputValue('#cron input')).toEqual(scheduleEdited.cron);
    await expect(await page.$('#enabled.is-checked')).toBeNull();
    await expect(await page.inputValue('#description textarea')).toEqual(scheduleEdited.description);

    // reset
    await editSchedule(page, {...schedule});
  });

  test('should delete schedule', async ({page}) => {
    // go to list page
    await goToListPage(page, 'schedules');

    // delete spider
    await deleteSchedule(page, {name: schedule.name});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).not.toContain(schedule.name);
  });
});
