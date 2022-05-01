import {expect, test} from '@playwright/test';
import {getStorageFilePath} from '../../../utils/storage';
import {clickTableCellByKey} from '../../../utils/table';
import {createProject, deleteProject, editProject} from '../../../actions/project/common';
import {getRandomName} from '../../../utils/name';

test.use({storageState: getStorageFilePath()});
test.describe.configure({mode: 'serial'});

test.describe('project: common', () => {
  const project = {
    name: getRandomName('project'),
    description: getRandomName('project_description'),
  };
  const projectEdited = {
    name: project.name + '_edited',
    description: project.description + '_edited',
  };

  test('should create project', async ({page}) => {
    // go to list page
    await page.goto('/#/projects');

    // create project
    await createProject(page, {...project});

    // expect table to display created row
    const names = await page.evaluate(() => {
      const names = [];
      const els = document.querySelectorAll('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
      els.forEach(el => {
        names.push(el.textContent);
      });
      return names;
    });
    await expect(names).toContain(project.name);
  });

  test('should edit project', async ({page}) => {
    // go to list page
    await page.goto('/#/projects');
    await page.waitForSelector('#add-btn');

    // go to detail page
    await clickTableCellByKey(page, 'name', project.name);
    await page.click('.el-menu-item.overview');

    // edit project
    await editProject(page, {...projectEdited});

    // refresh page
    await page.reload();
    await page.click('.el-menu-item.overview');

    // expect fields to be the same as edited
    await expect(await page.inputValue('#name input')).toEqual(projectEdited.name);
    await expect(await page.inputValue('#description textarea')).toEqual(projectEdited.description);

    // reset
    await editProject(page, {...project});
  });

  test('should delete project', async ({page}) => {
    // go to list page
    await page.goto('/#/projects');
    await page.waitForSelector('#add-btn');

    // delete spider
    await deleteProject(page, {name: project.name});

    // expect table to not contains created row
    const elNames = await page.$$('.table table.el-table__body tr.el-table__row > td.el-table__cell.name');
    const names = await Promise.all(elNames.map(el => el.innerText()));
    await expect(names.includes(project.name)).toBeFalsy();
  });
});
