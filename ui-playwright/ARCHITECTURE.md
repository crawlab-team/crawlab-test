# UI Testing Architecture - TypeScript Playwright + Python Orchestrator

## Overview

The UI testing framework uses **TypeScript Playwright** for actual browser automation, with **Python as a lightweight orchestrator** for test lifecycle management and integration with the broader Crawlab test infrastructure.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Python Test Orchestrator               │
│                  (run-ui-tests.py)                      │
│                                                          │
│  • Environment setup                                     │
│  • Dependency management (pnpm)                          │
│  • Test execution coordination                           │
│  • Result collection & parsing                           │
│  • Unified report generation                             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Executes: pnpm test
                  ▼
┌─────────────────────────────────────────────────────────┐
│           TypeScript Playwright Test Suite              │
│           (tests/ui-playwright/)                        │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Test Specifications (.spec.ts)                 │   │
│  │  • spider-management.spec.ts                    │   │
│  │  • login.spec.ts                                │   │
│  │  • ...                                          │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                                │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Page Object Models (pages/)                    │   │
│  │  • LoginPage.ts                                 │   │
│  │  • SpiderPage.ts                                │   │
│  │  • DashboardPage.ts                             │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                                │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Fixtures & Helpers (fixtures/)                 │   │
│  │  • Custom test fixtures                         │   │
│  │  • Test data generators                         │   │
│  │  • Cleanup utilities                            │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                                │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Playwright Test Runner                         │   │
│  │  • Browser automation (Chromium)                │   │
│  │  • Parallel execution                           │   │
│  │  • Screenshot/video capture                     │   │
│  │  • JSON reporter                                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Generates: playwright-results.json
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Test Results & Artifacts                    │
│                                                          │
│  • playwright-results.json    (structured results)      │
│  • playwright-report/         (HTML report)             │
│  • playwright-artifacts/      (screenshots, videos)     │
│  • result_TIMESTAMP.json      (unified format)          │
└─────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. **Simple Solutions Over Complex** (Occam's Razor)
- Use TypeScript Playwright natively, not Python wrappers
- Python only handles orchestration, not browser automation
- Leverage Playwright's built-in features (auto-wait, retries, reporters)

### 2. **Type Safety**
- TypeScript provides compile-time type checking
- Page Objects have typed interfaces
- Prevents common runtime errors

### 3. **Idiomatic Code**
- Use Playwright's recommended patterns
- Follow Page Object Model best practices
- Align with Playwright documentation

### 4. **Maintainability**
- Clear separation of concerns
- Reusable Page Objects
- Centralized configuration
- Easy to extend for new test cases

## Key Components

### TypeScript Layer (Test Logic)

#### **Test Specifications** (`tests/*.spec.ts`)
- Actual test scenarios
- Uses Playwright Test framework
- Leverages custom fixtures
- Clear test steps with `test.step()`

#### **Page Object Models** (`pages/*.ts`)
- Encapsulate page interactions
- Abstract selectors and actions
- Reusable across tests
- Inherit from `BasePage` for common functionality

#### **Fixtures** (`fixtures/base.ts`)
- Custom test fixtures for Crawlab-specific setup
- Authenticated sessions
- Test data tracking for cleanup
- Pre-configured page objects

#### **Configuration** (`config/test-config.ts`)
- Environment variables
- Test data generators
- Common selectors
- API endpoints

### Python Layer (Orchestration)

#### **Test Runner** (`run-ui-tests.py`)
- Dependency checks (Node.js, pnpm)
- Install dependencies and browsers
- Execute Playwright tests via subprocess
- Parse JSON results
- Generate unified reports
- Integration with CI/CD

## Workflow

### Local Development
```bash
# 1. Setup (one-time)
cd tests/ui-playwright
pnpm install
pnpm run install:browsers

# 2. Run tests
cd tests
./run-ui-tests.py

# Or direct execution
cd ui-playwright
pnpm test
```

### CI/CD Pipeline
```yaml
1. Install Python dependencies
2. Install Node.js and pnpm (action-setup)
3. Install TypeScript dependencies (pnpm install)
4. Install Playwright browsers (pnpm run install:browsers)
5. Start Crawlab services (Docker Compose)
6. Execute tests via Python orchestrator
7. Collect results (JSON + HTML reports)
8. Upload artifacts
```

## Benefits of This Architecture

### ✅ **Better Developer Experience**
- TypeScript autocomplete and type checking
- Playwright Inspector for debugging
- Codegen for creating new tests
- Rich VSCode integration

### ✅ **Reliability**
- Playwright's auto-waiting mechanism
- Built-in retry logic
- Screenshot/video on failure
- Trace viewer for debugging

### ✅ **Performance**
- Parallel test execution
- Fast browser automation
- Efficient pnpm dependency management

### ✅ **Maintainability**
- Clear separation: orchestration (Python) vs automation (TypeScript)
- Reusable Page Objects
- Type-safe test code
- Easy to onboard new developers

### ✅ **Integration**
- Python orchestrator integrates with existing test infrastructure
- Unified JSON report format
- Compatible with current CI/CD pipelines
- Consistent result structure

## Migration from Python Playwright Wrapper

### Before (Complex)
```python
# Python wrapping Playwright with async/await
from helpers.ui.browser.playwright_wrapper import PlaywrightWrapper

wrapper = PlaywrightWrapper()
await wrapper.start()
await wrapper.goto("http://localhost:8080")
await wrapper.click(".login-button")
# ... complex Python async code
```

### After (Simple)
```typescript
// Native TypeScript Playwright
import { test, expect } from '@playwright/test';

test('login', async ({ page }) => {
  await page.goto('http://localhost:8080');
  await page.click('.login-button');
  await expect(page).toHaveURL(/dashboard/);
});
```

## Adding New Tests

### 1. Create Test File
```bash
# Create new test spec
touch tests/ui-playwright/tests/task/task-execution.spec.ts
```

### 2. Create Page Object (if needed)
```bash
# Create page object
touch tests/ui-playwright/pages/TaskPage.ts
```

### 3. Write Test
```typescript
import { test, expect } from '../fixtures/base';
import { TaskPage } from '../pages/TaskPage';

test.describe('Task Execution', () => {
  test('should run task successfully', async ({ authenticatedPage }) => {
    const taskPage = new TaskPage(authenticatedPage);
    await taskPage.goto();
    await taskPage.runTask('my-spider');
    await expect(taskPage.getTaskStatus()).toBe('completed');
  });
});
```

### 4. Run Test
```bash
./run-ui-tests.py --test tests/task
```

## Troubleshooting

### Issue: Browsers not installed
```bash
cd tests/ui-playwright
pnpm run install:browsers
```

### Issue: Dependency errors
```bash
cd tests/ui-playwright
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Issue: Test timeouts
Increase timeout in `playwright.config.ts`:
```typescript
timeout: 120 * 1000, // 2 minutes
```

### Issue: TypeScript errors
```bash
cd tests/ui-playwright
pnpm install  # Ensure @playwright/test is installed
```

## References

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Crawlab Testing SOP](../TESTING_SOP.md)
- [AGENTS.md Guidelines](../../AGENTS.md)
