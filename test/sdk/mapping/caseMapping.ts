/**
 * caseName -> caseId
 */
export const caseMapping = {
  login: {
    shouldLoginAdmin: 88,
    shouldLogout: 3464,
  },

  // node
  node: {
    common: {
      shouldEditNode: 156,
    },
  },

  // project
  project: {
    common: {
      shouldCreateProject: 158,
      shouldEditProject: 159,
      shouldDeleteProject: 160,
    },
  },

  // spider
  spider: {
    common: {
      shouldCreateSpider: 90,
      shouldRunSpider: 91,
      shouldEditSpider: 92,
      shouldDeleteSpider: 93,
    },
    file: {
      shouldCreateSpiderFile: 132,
      shouldEditSpiderFile: 140,
      shouldRenameSpiderFile: 141,
      shouldMoveSpiderFile: 142,
      shouldCloneSpiderFile: 144,
      shouldDeleteSpiderFile: 143,
    },
    upload: {
      shouldUploadSpiderDirectory: 133,
      shouldUploadSpiderFile: 147,
      shouldUploadSpiderDirectoryFromList: 2308,
      shouldUploadSpiderFileFromList: 2390,
    },
    ui: {
      shouldSwitchSpiderOverview: 2566,
      shouldSwitchSpiderFiles: 2607,
      shouldSwitchSpiderGit: 2648,
      shouldSwitchSpiderTasks: 2689,
      shouldSwitchSpiderSchedules: 2730,
      shouldSwitchSpiderData: 2771,
    },
  },

  // schedule
  schedule: {
    common: {
      shouldCreateSchedule: 161,
      shouldEditSchedule: 162,
      shouldDeleteSchedule: 164,
    },
    ui: {
      shouldSwitchScheduleOverview: 3005,
      shouldSwitchScheduleTasks: 3046,
    },
  },

  // task
  task: {
    common: {
      shouldCreateTask: 165,
      shouldViewTaskLogs: 168,
      shouldViewTaskData: 250,
      shouldRestartTask: 166,
      shouldDeleteTask: 167,
      shouldCancelTask: 252,
    },
  },

  // user
  user: {
    common: {
      shouldCreateUser: 3225,
      shouldEditUser: 3266,
      shouldEditUserPassword: 3348,
      shouldDeleteUser: 3307,
    },
  },

  // plugin
  plugin: {
    common: {
      shouldEditPluginGlobalSettings: 3673,
      shouldInstallPlugin: 83,
      shouldStartPlugin: 3102,
      shouldStopPlugin: 3184,
      shouldUninstallPlugin: 3143,
    },
  },
};
