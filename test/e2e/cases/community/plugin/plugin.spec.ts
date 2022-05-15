import {test} from '@/e2e/base/authTest';
import {goToListPage} from '@/e2e/actions/components/nav';
import {
  editPluginGlobalSettings,
  installPlugin,
  startPlugin,
  stopPlugin,
  uninstallPlugin
} from '@/e2e/actions/plugin/common';
import {getTableCellByTargetKey, getTableCellTextsByKey} from '@/e2e/actions/components/table';
import {expect} from '@playwright/test';

test.describe.serial('plugin:common', () => {
  const plugin = {
    name: 'plugin-dependency',
    shortName: 'dependency',
  };
  const settings = {
    installSource: process.env.PLUGIN_INSTALL_SOURCE || 'GitHub',
    goProxy: process.env.PLUGIN_GOPROXY || 'Goproxy.cn',
  };

  test.beforeEach(async ({page}) => {
    await goToListPage(page, 'plugins');
  });

  test('should edit plugin global settings', async ({page}) => {
    // edit settings
    await editPluginGlobalSettings(page, {...settings});

    // reload page
    await page.reload();

    // expect info to be correct
    await page.click('#settings-btn');
    await page.waitForTimeout(500);
    await expect(await page.locator('#install-source input')).toHaveValue(settings.installSource);
    await expect(await page.locator('#go-proxy input')).toHaveValue(settings.goProxy);
  });

  test('should install plugin', async ({page}) => {
    // slow test
    test.slow();

    // install plugin
    await installPlugin(page, {name: plugin.name});

    // status
    const elLs = await getTableCellByTargetKey(page, 'name', plugin.name, 'status');
    await elLs.waitForSelector('.plugin-status .el-tag--success');
  });

  test('should stop plugin', async ({page}) => {
    // stop plugin
    await stopPlugin(page, {name: plugin.shortName});

    // status
    const elLs = await getTableCellByTargetKey(page, 'name', plugin.name, 'status');
    await elLs.waitForSelector('.plugin-status .el-tag--info');
  });

  test('should start plugin', async ({page}) => {
    // start plugin
    await startPlugin(page, {name: plugin.shortName});

    // status
    const elLs = await getTableCellByTargetKey(page, 'name', plugin.name, 'status');
    await elLs.waitForSelector('.plugin-status .el-tag--success');
  });

  test('should uninstall plugin', async ({page}) => {
    // uninstall plugin
    await uninstallPlugin(page, {name: plugin.shortName});

    // expect table to not contains created row
    const names = await getTableCellTextsByKey(page, 'name');
    await expect(names).not.toContain(plugin.shortName);
  });
});
