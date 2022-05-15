import {post} from './request';
import {getTestRunState} from './state';
import {TEST_RUN_EXECUTE_TYPE_AUTO} from './constants/testRun';
import logger from '@/logger';

interface CreateTestRunOptions {
  name?: string;
  includeAll?: boolean;
  cases?: number[];
  description?: string;
  executeType?: number;
}

export type CodingTestStatus = 'UNTESTED' | 'PASSED' | 'BLOCKED' | 'RETEST' | 'FAILED';

interface UpdateTestCaseResultOptions {
  runId?: number;
  caseId?: number;
  status?: CodingTestStatus;
  customStepStatus?: CodingTestStatus[];
}

interface UpdateTestCaseResultsOptions {
  runId?: number;
  caseIds?: number[];
  status?: CodingTestStatus;
}

interface CreateAttachmentPrepareSignUrlOptions {
  fileName?: string;
}

interface CreateTestReportOptions {
  name?: string;
  runIds?: number[];
  attachmentIds?: number[];
}

const _createTestRun = async (opts: CreateTestRunOptions = {}): Promise<number> => {
  const res = await post({
    Action: 'CreateTestRun',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    Name: opts.name || `Test_Plan_${new Date().getTime()}`,
    IncludeAll: opts.includeAll || !opts.cases,
    Cases: opts.cases,
    Description: opts.description,
    ExecuteType: opts.executeType || TEST_RUN_EXECUTE_TYPE_AUTO,
  });
  logger.debug('_createTestRun', res, opts);
  return res?.Response?.Data?.Run?.Id;
};

const _updateTestCaseResult = async (opts: UpdateTestCaseResultOptions = {}) => {
  const res = await post({
    Action: 'CreateCaseResult',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    RunId: opts.runId,
    CaseId: opts.caseId,
    Status: opts.status,
    CustomStepStatus: opts.customStepStatus,
  });
  logger.debug('_updateTestCaseResult', res, opts);
};

const _updateTestCaseResults = async (opts: UpdateTestCaseResultsOptions = {}) => {
  if (!opts.caseIds?.length) return;
  const res = await post({
    Action: 'CreateTestResults',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    RunId: opts.runId,
    CaseIds: opts.caseIds,
    Status: opts.status,
  });
  logger.debug('_updateTestCaseResults', res, opts);
};

const _createAttachmentPrepareSignUrl = async (opts: CreateAttachmentPrepareSignUrlOptions = {}) => {
  if (!opts.fileName) return;
  const res = await post({
    Action: 'CreateAttachmentPrepareSignUrl',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    FileName: opts.fileName,
  });
  logger.debug('_createAttachmentPrepareSignUrl', res, opts);
};

const _createTestReport = async (opts: CreateTestReportOptions = {}) => {
  if (!opts.runIds?.length) return;
  const res = await post({
    Action: 'CreateReport',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    Name: opts.name || `Test_Report_${new Date().getTime()}`,
    RunIds: opts.runIds,
    AttachmentIds: opts.attachmentIds,
  });
  logger.debug('_createTestReport', res, opts);
};

export const createTestRun = async (opts?: CreateTestRunOptions) => {
  return await _createTestRun(opts);
};

export const updateTestCaseResult = async (caseId: number, status: CodingTestStatus) => {
  const {runId} = getTestRunState();
  await _updateTestCaseResult({
    runId,
    caseId,
    status,
  });
};

export const createTestReport = async (opts?: CreateTestReportOptions) => {
  return await _createTestReport(opts);
};
