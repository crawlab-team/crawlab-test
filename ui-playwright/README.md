# Crawlab UI Tests - TypeScript Playwright

This directory contains the UI end-to-end tests for Crawlab using TypeScript and Playwright.

## Architecture

```
ui-playwright/
├── tests/              # Test specifications
│   ├── auth/          # Authentication tests
│   ├── spider/        # Spider management tests
│   ├── task/          # Task execution tests
│   └── ...
├── pages/             # Page Object Models
│   ├── LoginPage.ts
│   ├── SpiderPage.ts
│   └── ...
├── fixtures/          # Test fixtures and setup
│   └── base.ts
├── helpers/           # Utility functions
│   ├── api.ts
│   ├── data.ts
│   └── ...
└── config/            # Configuration files
    └── test-data.ts
```

## Getting Started

### Installation

```bash
# Install dependencies
pnpm install

# Install Playwright browsers
pnpm run install:browsers
```

### Running Tests

```bash
# Run all tests (headless)
pnpm test

# Run tests with UI (headed mode)
pnpm test:headed

# Run specific test category
pnpm test:spider
pnpm test:auth

# Debug mode
pnpm test:debug

# Interactive UI mode
pnpm test:ui

# View test report
pnpm report
```

### Environment Variables

Create a `.env` file for local development:

```env
CRAWLAB_BASE_URL=http://localhost:8080
CRAWLAB_ADMIN_USERNAME=admin
CRAWLAB_ADMIN_PASSWORD=admin
HEADLESS=false
```

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from '@pages/LoginPage';

test.describe('Spider Management', () => {
  test('should create a new spider', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('admin', 'admin');
    
    // Your test logic here
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
```

### Using Page Objects

Page Object Models are located in the `pages/` directory and provide a clean abstraction for page interactions.

```typescript
import { SpiderPage } from '@pages/SpiderPage';

test('spider workflow', async ({ page }) => {
  const spiderPage = new SpiderPage(page);
  await spiderPage.goto();
  await spiderPage.createSpider('test-spider', 'python');
  await expect(spiderPage.getSpiderByName('test-spider')).toBeVisible();
});
```

### Test Data

Test data and configuration are managed in `config/test-data.ts` for consistency across tests.

## Integration with Python Test Runner

The Python test runner executes these TypeScript tests and collects results:

1. Python runner starts Docker services
2. Executes `pnpm test` in this directory
3. Reads `playwright-results.json` 
4. Generates unified test report

## CI/CD Integration

Tests run automatically in GitHub Actions:
- Browsers installed via `playwright install --with-deps chromium`
- Results uploaded as artifacts
- HTML reports generated on failure

## Best Practices

1. **Use Page Objects**: Encapsulate page interactions in Page Object Models
2. **Explicit Waits**: Use Playwright's auto-waiting; avoid arbitrary timeouts
3. **Isolation**: Each test should be independent and not rely on others
4. **Cleanup**: Use `test.afterEach` to clean up test data
5. **Selectors**: Prefer `data-testid` attributes over CSS classes
6. **Assertions**: Use Playwright's built-in assertions for auto-retrying

## Debugging

```bash
# Run with Playwright Inspector
pnpm test:debug

# Generate code from browser actions
pnpm codegen http://localhost:8080

# View trace files
pnpm exec playwright show-trace trace.zip
```

## Troubleshooting

### Browsers not found
```bash
pnpm run install:browsers
```

### Connection refused
Ensure Crawlab is running:
```bash
cd ../.. && docker-compose -f tests/docker-compose.test.yml up
```

### Timeout errors
Increase timeout in `playwright.config.ts` or specific tests:
```typescript
test.setTimeout(120_000); // 2 minutes
```

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Crawlab Testing SOP](../TESTING_SOP.md)
