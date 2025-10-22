# Deterministic UI Testing Framework

## Overview

This framework provides a structured, spec-driven approach to UI testing for Crawlab. It follows the same Standard Operating Procedure (SOP) pattern as other test categories (cluster, database, scheduler, dependencies, system), providing determinism, maintainability, and reusability.

## Architecture

The framework is organized into three main layers:

1. **Test Runners** (`runners/ui/`) - Python scripts that execute test specifications
2. **Action Library** (`helpers/ui/actions/`) - Reusable UI actions (login, navigate, create, etc.)
3. **Browser Layer** (`helpers/ui/browser/`) - Browser automation abstraction (Playwright)

```
├── runners/ui/                         # Test runner scripts
│   └── UI_001_spider_management.py    # Example: Spider management test
├── helpers/ui/                         # UI testing helpers
│   ├── actions/                        # Reusable action library
│   │   ├── auth_actions.py            # Authentication actions
│   │   └── navigation_actions.py      # Navigation actions
│   ├── browser/                        # Browser automation
│   │   └── playwright_wrapper.py      # Playwright wrapper
│   └── validators/                     # UI validators
└── helpers/libs/
    └── ui_base.py                      # Base UI test class
```

## Key Features

### ✅ Deterministic Execution
- Predictable, repeatable test runs
- Clear failure points
- No autonomous AI guessing

### ✅ Reusable Actions
- Composable action library
- DRY principle - write once, use everywhere
- Easy to maintain when UI changes

### ✅ Following SOP Pattern
- Same structure as cluster/scheduler/database tests
- Spec -> Code -> Test Results workflow
- Familiar to team members

### ✅ Comprehensive Logging
- Step-by-step execution logs
- Screenshot capture at each step
- Detailed error reporting

## Quick Start

### 1. Install Dependencies

```bash
cd tests
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run Example Test

```bash
# Make the runner executable
chmod +x runners/ui/UI_001_spider_management.py

# Run the test
./runners/ui/UI_001_spider_management.py
```

### 3. View Results

Results are saved in `tests/results/`:
- **Logs**: `results/logs/UI-001_*.log`
- **Screenshots**: `results/screenshots/UI-001/`

## Creating a New UI Test

### Step 1: Create Test Specification

Create a markdown file in `specs/ui/` following the SOP template:

```markdown
# UI-002 - Task Management Test

## Metadata
- **Category**: ui
- **Priority**: high
- **Complexity**: simple
- **Duration**: 5 minutes

## Test Steps

### Step 1: Login
**Method**: script
**Command**: `./runners/ui/UI_002_task_management.py`
**Expected**: User logged in successfully
**Validation**: Dashboard visible

[... more steps ...]
```

### Step 2: Create Test Runner

Create `runners/ui/UI_002_task_management.py`:

```python
#!/usr/bin/env python3
"""Test runner for UI-002 - Task Management"""

import sys
import asyncio
from pathlib import Path

# Add tests directory to path
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from helpers.libs.ui_base import UITestBase
from helpers.ui.actions.auth_actions import AuthActions
from helpers.ui.actions.navigation_actions import NavigationActions
from helpers.ui.browser.playwright_wrapper import PlaywrightWrapper


class TaskManagementTest(UITestBase):
    """Test runner for UI-002."""
    
    def __init__(self):
        super().__init__("UI-002")
        self.browser_wrapper = None
        self.auth_actions = None
        self.nav_actions = None
    
    async def setup(self):
        """Set up test environment."""
        await super().setup()
        
        # Initialize browser
        self.browser_wrapper = PlaywrightWrapper(
            headless=self.config["browser"]["headless"]
        )
        await self.browser_wrapper.start()
        self.page = self.browser_wrapper.page
        
        # Initialize actions
        self.auth_actions = AuthActions(
            self.browser_wrapper,
            self.config["base_url"]
        )
        self.nav_actions = NavigationActions(
            self.browser_wrapper,
            self.config["base_url"]
        )
    
    async def teardown(self):
        """Clean up."""
        if self.browser_wrapper:
            await self.browser_wrapper.close()
        await super().teardown()
    
    async def run(self):
        """Execute test steps."""
        # Step 1: Login
        await self.auth_actions.login("admin", "admin")
        self.record_step_result("Login", True, "Logged in successfully")
        
        # Step 2: Navigate to tasks
        await self.nav_actions.goto_tasks()
        self.record_step_result("Navigate to tasks", True, "Tasks page loaded")
        
        # Add more steps...


async def main():
    test = TaskManagementTest()
    result = await test.execute()
    print(f"Test {result['status']}: {result['test_id']}")
    sys.exit(0 if result['status'] == 'passed' else 1)


if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Make Runner Executable

```bash
chmod +x runners/ui/UI_002_task_management.py
```

### Step 4: Run the Test

```bash
./runners/ui/UI_002_task_management.py
```

## Action Library

### AuthActions

Authentication-related actions:

```python
from helpers.ui.actions.auth_actions import AuthActions

auth = AuthActions(browser, base_url)

# Login
await auth.login("username", "password")

# Logout
await auth.logout()

# Individual steps
await auth.navigate_to_login()
await auth.fill_login_form("user", "pass")
await auth.submit_login()
await auth.verify_login_success()
```

### NavigationActions

Page navigation actions:

```python
from helpers.ui.actions.navigation_actions import NavigationActions

nav = NavigationActions(browser, base_url)

# Navigate to pages
await nav.goto_home()
await nav.goto_spiders()
await nav.goto_tasks()
await nav.goto_schedules()
await nav.goto_nodes()
await nav.goto_projects()

# Navigate to detail pages
await nav.goto_spider_detail(spider_id)
await nav.goto_task_detail(task_id)

# Switch tabs
await nav.switch_to_tab("Files")

# Open dialogs
await nav.open_create_dialog("spider")
```

## Browser Wrapper

### PlaywrightWrapper

Low-level browser automation:

```python
from helpers.ui.browser.playwright_wrapper import PlaywrightWrapper

browser = PlaywrightWrapper(headless=True)
await browser.start()

# Navigation
await browser.goto("http://localhost:5173")

# Interactions
await browser.click(".button")
await browser.fill("input[name='username']", "admin")
await browser.type_text("input", "text", delay=50)

# Waiting
await browser.wait_for_selector(".element")
await browser.wait_for_url("**/home")

# Information
text = await browser.get_text(".element")
attr = await browser.get_attribute(".element", "id")
visible = await browser.is_visible(".element")

# Screenshots
await browser.screenshot("path/to/file.png")

# Cleanup
await browser.close()
```

## Base Test Class

All UI tests inherit from `UITestBase`:

```python
from helpers.libs.ui_base import UITestBase

class MyTest(UITestBase):
    def __init__(self):
        super().__init__("UI-XXX")
    
    async def setup(self):
        """Override to add custom setup"""
        await super().setup()
        # Your setup code
    
    async def teardown(self):
        """Override to add custom cleanup"""
        # Your cleanup code
        await super().teardown()
    
    async def run(self):
        """Implement test steps"""
        pass
```

### Available Methods

- `take_screenshot(name)` - Capture screenshot
- `record_step_result(name, success, message)` - Record step outcome
- `get_test_summary()` - Get test results summary

## Configuration

Default configuration in `UITestBase`:

```python
{
    "browser": {
        "headless": True,  # Override with HEADLESS env var
        "viewport": {
            "width": 1920,
            "height": 1080
        }
    },
    "timeouts": {
        "default": 30000,
        "navigation": 60000,
        "action": 10000
    },
    "screenshots": {
        "enabled": True,
        "on_failure": True,
        "on_step": True
    },
    "base_url": "http://localhost:5173"  # Override with CRAWLAB_URL env var
}
```

## Environment Variables

- `HEADLESS` - Run browser in headless mode (default: true)
- `CRAWLAB_URL` - Base URL of Crawlab application (default: http://localhost:5173)

## Comparison with Copilot Approach

### Before (Autonomous Copilot)

❌ Unpredictable execution
❌ Hard to debug failures
❌ No code reuse
❌ Difficult to maintain
❌ Can't run specific steps

### After (Deterministic Framework)

✅ Predictable, repeatable
✅ Clear failure points
✅ Reusable action library
✅ Easy to maintain
✅ Step-by-step execution

## CI/CD Integration

### GitHub Actions Example

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd tests
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Start Crawlab
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30
      
      - name: Run UI Tests
        run: |
          cd tests
          ./runners/ui/UI_001_spider_management.py
        env:
          HEADLESS: true
          CRAWLAB_URL: http://localhost:5173
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: ui-test-results
          path: tests/results/
```

## Adding New Actions

### Creating a New Action Module

1. Create file in `helpers/ui/actions/`:

```python
# helpers/ui/actions/spider_actions.py
"""Spider-related UI actions."""

import logging
from ..browser.playwright_wrapper import PlaywrightWrapper


class SpiderActions:
    """Actions for spider management."""
    
    def __init__(self, browser: PlaywrightWrapper, base_url: str):
        self.browser = browser
        self.base_url = base_url
        self.logger = logging.getLogger("spider_actions")
    
    async def create_spider(self, name: str, spider_type: str = "python"):
        """Create a new spider."""
        self.logger.info(f"Creating spider: {name}")
        
        # Fill form
        await self.browser.fill("input[name='name']", name)
        await self.browser.select_option("select[name='type']", spider_type)
        
        # Submit
        await self.browser.click("button[type='submit']")
        
        # Verify
        await self.browser.wait_for_selector(f"text='{name}'")
        self.logger.info(f"✓ Spider created: {name}")
```

2. Add to `helpers/ui/actions/__init__.py`:

```python
from .spider_actions import SpiderActions

__all__ = [..., 'SpiderActions']
```

3. Use in test runner:

```python
from helpers.ui.actions.spider_actions import SpiderActions

self.spider = SpiderActions(self.browser_wrapper, self.config["base_url"])
await self.spider.create_spider("my-spider")
```

## Troubleshooting

### Browser doesn't start

```bash
# Install Playwright browsers
playwright install chromium

# Or install all browsers
playwright install
```

### Test fails immediately

- Check that Crawlab is running at the configured URL
- Verify credentials (default: admin/admin)
- Check browser logs in test output

### Screenshots not saving

- Ensure `results/screenshots/` directory exists
- Check write permissions
- Verify `screenshots.enabled` config is True

### Element not found errors

- UI selectors may have changed
- Check actual UI with browser DevTools
- Update selectors in action modules
- Use multiple fallback selectors

## Best Practices

1. **Use Action Library** - Don't write raw Playwright code in tests
2. **Multiple Selectors** - Provide fallback selectors for robustness
3. **Take Screenshots** - Capture state at each step
4. **Log Liberally** - Help future debugging
5. **Test Idempotency** - Tests should clean up after themselves
6. **Meaningful Names** - Clear step names and messages
7. **Error Handling** - Graceful failure with helpful messages

## Future Enhancements

- [ ] Visual regression testing
- [ ] Performance metrics tracking
- [ ] Accessibility testing
- [ ] Cross-browser support (Firefox, Safari)
- [ ] Mobile/responsive testing
- [ ] Video recording on failure
- [ ] Parallel test execution

## Resources

- **Design Document**: `/tests/docs/UI_TESTING_FRAMEWORK.md`
- **Testing SOP**: `/tests/TESTING_SOP.md`
- **Playwright Docs**: https://playwright.dev/python/
- **Example Runner**: `/tests/runners/ui/UI_001_spider_management.py`

## Support

For questions or issues:
1. Check this README
2. Review design document
3. Check example test runner
4. Review action library code
5. Open an issue with logs and screenshots
