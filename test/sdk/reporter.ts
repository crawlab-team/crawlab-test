import {Reporter, Suite, TestCase, TestResult, FullResult} from '@playwright/test/reporter';
import {FullConfig, TestStatus} from '@playwright/test';
import {get} from 'object-path';
import {saveTestRunState, TestRunState} from '@/sdk/state';
import {CodingTestStatus, createTestRun, updateTestCaseResult} from '@/sdk/api';
import {caseMapping} from '@/sdk/mapping/caseMapping';
import {getTestCaseCamelCaseName} from '@/e2e/utils/name';
import logger from '@/logger';

export const getCodingTestCaseStatus = ({status}: TestResult): CodingTestStatus => {
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
  status = new Set<number>();

  async onBegin(config: FullConfig, suite: Suite) {
    const caseIds: number[] = [];
    suite.allTests().forEach(t => {
      // case id
      const id = getIdFromTest(t);

      // add to case id list
      caseIds.push(id);

      // add to status
      this.status.add(id);
    });

    // run id
    const runId = await createTestRun({includeAll: false, cases: caseIds});

    // test run state
    const state: TestRunState = {
      runId,
      caseIds,
    };

    // save test run state
    saveTestRunState(state);
  }

  async onTestEnd(t: TestCase, result: TestResult) {
    // case id
    const id = getIdFromTest(t);

    // update test case result
    await updateTestCaseResult(id, getCodingTestCaseStatus(result));

    // print stack trace
    if (result.error?.stack) {
      if (logger.level === 'debug') {
        logger.error(result.error.stack);
      }
    }

    // remove from status
    this.status.delete(id);
  }

  async onEnd(result: FullResult) {
    let isTimeout = false;
    await setTimeout(() => isTimeout = true, 30 * 1e3);
    while (this.status.size > 0 && !isTimeout) {
      await new Promise(resolve => setTimeout(resolve, 1e3));
    }
    logger.info(`all tests ended. result: ${result.status}`);
    // const {runId} = getTestRunState();
    // await createTestReport({runIds: [runId]});
  }
}

export default SdkReporter;
