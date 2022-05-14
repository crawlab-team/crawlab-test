import {expect} from '@playwright/test';
import {clickTableCellByKey, getTableCellTextsByKey} from '@/e2e/actions/components/table';
import {createProject, deleteProject, editProject} from '@/e2e/actions/project/common';
import {getRandomName} from '@/e2e/utils/name';
import {goToListPage, goToNavTab} from '@/e2e/actions/components/nav';
import {test} from '@/e2e/base/authTest';

test.describe.serial('project:common', () => {
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
    await goToListPage(page, 'projects');

    // create project
    await createProject(page, {...project});

    // expect table to display created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).toContain(project.name);
  });

  test('should edit project', async ({page}) => {
    // go to list page
    await goToListPage(page, 'projects');

    // go to detail page
    await clickTableCellByKey(page, 'name', project.name);
    await goToNavTab(page, 'overview');

    // edit project
    await editProject(page, {...projectEdited});

    // refresh page
    await page.reload();
    await goToNavTab(page, 'overview');

    // expect fields to be the same as edited
    await expect(await page.inputValue('#name input')).toEqual(projectEdited.name);
    await expect(await page.inputValue('#description textarea')).toEqual(projectEdited.description);

    // reset
    await editProject(page, {...project});
  });

  test('should delete project', async ({page}) => {
    // go to list page
    await goToListPage(page, 'projects');

    // delete spider
    await deleteProject(page, {name: project.name});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).not.toContain(project.name);
  });
});
