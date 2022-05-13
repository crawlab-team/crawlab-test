import {Reporter, Suite, TestCase, TestResult, FullResult} from '@playwright/test/reporter';
import {FullConfig, TestStatus} from '@playwright/test';
import {get} from 'object-path';
import {saveTestRunState, TestRunState} from './state';
import {CodingTestStatus, createTestRun, updateTestCaseResult} from './api';
import {caseMapping} from './mapping/caseMapping';
import {getTestCaseCamelCaseName} from '../e2e/utils/name';

export const getCodingTestCaseStatus = (status: TestStatus): CodingTestStatus => {
  switch (status) {
    case 'failed':
    case 'timedOut':
      return 'FAILED';
    case 'passed':
      return 'PASSED';
    case 'skipped':
      return 'BLOCKED';
  }
};

export const getIdFromTest = (t: TestCase): number => {
  const suitePath = t.parent.title.replace(/[ :]/g, '.');
  const testPath = getTestCaseCamelCaseName(t.title);
  const path = `${suitePath}.${testPath}`;
  return get(caseMapping, path);
};

class SdkReporter implements Reporter {
  async onBegin(config: FullConfig, suite: Suite) {
    const caseIds: number[] = [];
    suite.allTests().forEach(t => {
      const id = getIdFromTest(t);
      caseIds.push(id);
    });
    const runId = await createTestRun({includeAll: false, cases: caseIds});
    const state: TestRunState = {
      runId,
      caseIds,
    };
    saveTestRunState(state);
  }

  async onTestEnd(t: TestCase, result: TestResult) {
    const id = getIdFromTest(t);
    await updateTestCaseResult(id, getCodingTestCaseStatus(result.status));
  }

  // async onEnd(result: FullResult) {
  //   const {runId} = getTestRunState();
  //   await createTestReport({runIds: [runId]});
  // }
}

export default SdkReporter;
