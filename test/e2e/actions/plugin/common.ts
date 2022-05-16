import {Page} from '@playwright/test';
import {BaseActionOptions} from '@/e2e/actions/base';
import {clickTableCellActionByKey} from '@/e2e/actions/components/table';
import {selectFromItems} from '@/e2e/actions/components/select';

interface InstallPluginOptions extends BaseActionOptions {
  name?: string;
}

interface UninstallPluginOptions extends BaseActionOptions {
  name?: string;
}

interface StartPluginOptions extends BaseActionOptions {
  name?: string;
}

interface StopPluginOptions extends BaseActionOptions {
  name?: string;
}

interface EditPluginGlobalSettingsOptions extends BaseActionOptions {
  installSource?: string;
  goProxy?: string;
}

export const installPlugin = async (page: Page, {name, waitDuration}: InstallPluginOptions = {}) => {
  await page.click('#add-btn');
  const el = await page.locator(`.public-plugin-item :has-text("${name}")`);
  const elAct = await el.locator('.install-btn');
  await elAct.click();
  await page.click('.install-plugin-confirm-btn');
  await page.waitForTimeout(waitDuration || 500);
  await page.click('#confirm-btn');
  await page.waitForTimeout(waitDuration || 500);
};

export const stopPlugin = async (page: Page, {name, waitDuration}: StopPluginOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'name', text: name, action: '.stop-btn'});
  await page.click('.stop-plugin-confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const startPlugin = async (page: Page, {name, waitDuration}: StartPluginOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'name', text: name, action: '.start-btn'});
  await page.click('.start-plugin-confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const uninstallPlugin = async (page: Page, {name, waitDuration}: UninstallPluginOptions = {}) => {
  await clickTableCellActionByKey(page, {key: 'name', text: name, action: '.delete-btn'});
  await page.click('.delete-confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};

export const editPluginGlobalSettings = async (page: Page, {
  installSource,
  goProxy,
  waitDuration,
}: EditPluginGlobalSettingsOptions = {}) => {
  await page.click('#settings-btn');
  if (installSource) await selectFromItems(page, {key: '#install-source', label: installSource});
  if (goProxy) await selectFromItems(page, {key: '#go-proxy', label: goProxy});
  await page.click('#confirm-btn');
  await page.waitForTimeout(waitDuration || 1000);
};
