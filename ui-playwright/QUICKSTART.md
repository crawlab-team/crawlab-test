# Quick Start Guide - UI Testing with TypeScript Playwright

## Initial Setup

```bash
cd tests/ui-playwright

# Install dependencies
pnpm install

# Install Playwright browsers
pnpm run install:browsers
```

## Running Tests

### Using Python Orchestrator (Recommended)
```bash
# From tests/ directory
./run-ui-tests.py

# Run specific test category
./run-ui-tests.py --test tests/spider

# Run specific test file
./run-ui-tests.py --test tests/spider/spider-management.spec.ts
```

### Direct Playwright Execution
```bash
cd tests/ui-playwright

# Run all tests
pnpm test

# Run with UI
pnpm test:headed

# Run specific category
pnpm test:spider
pnpm test:auth

# Debug mode
pnpm test:debug
```

## Environment Configuration

Create `.env` file in `tests/ui-playwright/`:

```env
CRAWLAB_BASE_URL=http://localhost:8080
CRAWLAB_ADMIN_USERNAME=admin
CRAWLAB_ADMIN_PASSWORD=admin
```

## CI/CD Integration

The GitHub Actions workflow will:
1. Install Node.js and pnpm
2. Install Playwright dependencies
3. Execute tests via Python orchestrator
4. Collect JSON results
5. Generate unified reports

## Project Structure

```
ui-playwright/
├── package.json           # Dependencies and scripts
├── playwright.config.ts   # Playwright configuration
├── tsconfig.json         # TypeScript configuration
├── fixtures/             # Test fixtures
│   └── base.ts          # Custom test fixtures
├── pages/               # Page Object Models
│   ├── BasePage.ts
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   └── SpiderPage.ts
├── config/              # Configuration
│   └── test-config.ts   # Test data and selectors
└── tests/               # Test specifications
    ├── auth/
    │   └── login.spec.ts
    └── spider/
        └── spider-management.spec.ts
```

## Next Steps

1. Install dependencies: `cd tests/ui-playwright && pnpm install`
2. Install browsers: `pnpm run install:browsers`
3. Start Crawlab: `docker-compose -f tests/docker-compose.test.yml up`
4. Run tests: `./tests/run-ui-tests.py`
