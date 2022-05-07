/**
 * caseName -> caseId
 */
export const caseMapping = {
  community: {
    login: {
      shouldLogin: 88,
    },
    node: {
      common: {
        shouldEditNode: 156,
      },
    },
    project: {
      common: {
        shouldCreateProject: 158,
        shouldEditProject: 159,
        shouldDeleteProject: 160,
      },
    },
    spider: {
      common: {
        shouldCreateSpider: 90,
        shouldRunSpider: 91,
        shouldEditSpider: 92,
        shouldDeleteSpider: 93,
      },
      batch: {},
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
      },
    },
    schedule: {
      common: {
        shouldCreateSchedule: 161,
        shouldEditSchedule: 162,
        shouldDeleteSchedule: 164,
      },
    },
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
  },
  pro: {},
};
