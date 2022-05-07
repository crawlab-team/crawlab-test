import {post} from './request';
import {getTestRunState, saveTestRunState, TestRunState} from './state';
import {test, TestType} from '@playwright/test';
import {getTestCaseCamelCaseName} from '../e2e/utils/name';

interface CreateTestRunOptions {
  name?: string;
  includeAll?: boolean;
  casesN?: number[];
  description?: string;
  executeType?: number;
}

type TestResult = 'UNTESTED' | 'PASSED' | 'BLOCKED' | 'RETEST' | 'FAILED';

interface UpdateTestCaseResultOptions {
  runId?: number;
  caseId?: number;
  status?: TestResult;
  customStepStatusN?: TestResult[];
}

interface UpdateTestCaseResultsOptions {
  runId?: number;
  caseIdsN?: number[];
  status?: TestResult;
}

const _createTestRun = async (opts: CreateTestRunOptions = {}): Promise<number> => {
  const res = await post({
    Action: 'CreateTestRun',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    Name: opts.name || `Test_Plan_${new Date().getTime()}`,
    IncludeAll: opts.includeAll || !opts.casesN,
    'Case.N': opts.casesN,
    Description: opts.description,
    ExecuteType: opts.executeType || 2,
  });
  return res?.Response?.Data?.Run?.Id;
};

const _updateTestCaseResult = async (opts: UpdateTestCaseResultOptions = {}) => {
  const res = await post({
    Action: 'CreateCaseResult',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    RunId: opts.runId,
    CaseId: opts.caseId,
    Status: opts.status,
    'CustomStepStatus.N': opts.customStepStatusN,
  });
  console.debug(res, opts);
};

const _updateTestCaseResults = async (opts: UpdateTestCaseResultsOptions = {}) => {
  if (!opts.caseIdsN?.length) return;
  const res = await post({
    Action: 'CreateTestResults',
    ProjectName: process.env.CODING_API_PROJECT_NAME || 'crawlab',
    RunId: opts.runId,
    'CaseIds.N': opts.caseIdsN,
    Status: opts.status,
  });
  console.debug(res);
};

export const initTestRun = async () => {
  const state: TestRunState = {};
  state.runId = await _createTestRun();
  saveTestRunState(state);
};

export const updateTestCaseResult = async (caseId: number, status: TestResult) => {
  const {runId} = getTestRunState();
  await _updateTestCaseResult({
    runId,
    caseId,
    status,
  });
};

export const wrapUpdateTestCaseResultFn = (test: TestType<any, any>, mapping: { [key: string]: number }): () => Promise<void> => {
  return async () => {
    const id = mapping[getTestCaseCamelCaseName(test.info().title)];
    await updateTestCaseResult(id, test.info().error ? 'FAILED' : 'PASSED');
  };
};
