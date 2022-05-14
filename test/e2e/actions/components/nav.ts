import {Page} from '@playwright/test';

type ListPage = 'nodes' | 'projects' | 'spiders' | 'schedules' | 'tasks' | 'users' | 'tokens' | 'plugins';

export const goToListPage = async (page: Page, name: ListPage) => {
  await page.goto(`/#/${name}`);
  await page.waitForSelector('#add-btn');
};

export const goToNavTab = async (page: Page, key: string) => {
  await page.click(`.el-menu-item.${key}`);
  await page.waitForTimeout(500);
};

export const selectNavSidebarItem = async (page: Page, name: string) => {
  await page.locator(`.nav-sidebar .el-menu-item > .title:text-is("${name}")`).click();
  await page.waitForTimeout(500);
};
