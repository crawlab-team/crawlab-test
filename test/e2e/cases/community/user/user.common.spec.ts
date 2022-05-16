import {test} from '@/e2e/base/authTest';
import {goToListPage, goToNavTab} from '@/e2e/actions/components/nav';
import {createUser, deleteUser, editUser, editUserPassword} from '@/e2e/actions/user/common';
import {getRandomName} from '@/e2e/utils/name';
import {clickTableCellByKey, getTableCellTextsByKey} from '@/e2e/actions/components/table';
import {expect} from '@playwright/test';
import {loginIncognito} from '@/e2e/actions/auth/login';
import {createBrowser} from '@/e2e/utils/browser';

test.describe.serial('user:common', () => {
  const user = {
    username: getRandomName('user'),
    email: getRandomName('email') + '@crawlab.com',
    password: 'password',
    role: 'admin',
  };
  const userEdited = {
    username: getRandomName('user'),
    email: getRandomName('email') + '@crawlab.com',
    password: 'password_edited',
    role: 'normal',
  };

  test.beforeEach(async ({page}) => {
    await goToListPage(page, 'users');
  });

  test('should create user', async ({page}) => {
    // create user
    await createUser(page, {...user});

    // expect table to display created row
    const names = await getTableCellTextsByKey(page, 'username');
    await expect(names).toContain(user.username);

    // login
    const browser = await createBrowser();
    await loginIncognito({browser, username: user.username, password: user.password});
    await expect(page).not.toHaveURL(/login/);
    await browser.close();
  });

  test('should edit user', async ({page}) => {
    // go to detail page
    await clickTableCellByKey(page, 'username', user.username);

    // edit user
    await editUser(page, {username: userEdited.username, email: userEdited.email, role: userEdited.role});

    // refresh page
    await page.reload();
    await goToNavTab(page, 'overview');

    // expect info to be correct
    await expect(await page.inputValue('#username input')).toEqual(userEdited.username);
    await expect(await page.inputValue('#email input')).toEqual(userEdited.email);
    await expect((await page.inputValue('#role input')).toLowerCase()).toEqual(userEdited.role);
  });

  test('should edit user password', async ({page}) => {
    // go to detail page
    await clickTableCellByKey(page, 'username', userEdited.username);

    // edit user password
    await editUserPassword(page, {password: userEdited.password});

    // login
    const browser = await createBrowser();
    await loginIncognito({browser, username: userEdited.username, password: userEdited.password});
    await expect(page).not.toHaveURL(/login/);
    await browser.close();
  });

  test('should delete user', async ({page}) => {
    // delete user
    await deleteUser(page, {username: userEdited.username});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'username');
    await expect(names).not.toContain(userEdited.username);
  });
});
