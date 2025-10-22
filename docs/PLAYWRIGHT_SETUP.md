# Playwright Browser Setup for UI Testing

## Overview

Crawlab UI tests use Python's Playwright library for browser automation. Playwright requires separate browser binaries to be installed before running tests.

## Quick Setup

```bash
cd tests
./setup-playwright.sh
```

That's it! You're now ready to run UI tests.

## Detailed Installation Options

### Default Installation (Chromium Only)
```bash
./setup-playwright.sh
```
Installs only Chromium browser, which is sufficient for most UI tests.

### All Browsers
```bash
./setup-playwright.sh --all
```
Installs Chromium, Firefox, and WebKit browsers.

### With System Dependencies
```bash
./setup-playwright.sh --with-deps
```
Installs browser dependencies (fonts, libraries). May require sudo password.

### Manual Installation
```bash
# Install Python package (if not already installed)
pip install -r requirements.txt

# Install browsers
python -m playwright install chromium

# Or install all browsers
python -m playwright install

# Or install with system dependencies
python -m playwright install --with-deps chromium
```

## Verifying Installation

```bash
# Check Playwright is installed
python3 -c "from playwright.async_api import async_playwright; print('OK')"

# Check browser installation
ls ~/.cache/ms-playwright/
```

You should see directories like `chromium-1187`, `chromium_headless_shell-1187`, etc.

## Running UI Tests

After installation, run UI tests using the unified CLI:

```bash
# Run by test ID
./cli.py --spec UI-001

# Run by fuzzy search
./cli.py --spec "spider management"

# List available UI tests
./cli.py --list-specs --category ui
```

## Troubleshooting

### Error: "Executable doesn't exist at ..."

**Cause**: Browser binaries not installed.

**Solution**:
```bash
cd tests
./setup-playwright.sh
```

### Error: "playwright: command not found"

**Cause**: Playwright Python package not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

### Permission Errors on Linux

**Cause**: Missing system dependencies.

**Solution**:
```bash
./setup-playwright.sh --with-deps
```

This installs required system libraries and fonts.

### Browser Crashes or Hangs

**Causes**:
- Insufficient memory
- Missing system libraries
- Conflicting browser processes

**Solutions**:
1. Install with dependencies: `./setup-playwright.sh --with-deps`
2. Check available memory: `free -h`
3. Kill existing browser processes: `pkill chromium`
4. Run tests in headless mode (default)

### Tests Fail in CI/Docker

**Cause**: Missing system dependencies in container.

**Solution**: Ensure your Dockerfile includes:
```dockerfile
# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN pip install playwright && playwright install chromium --with-deps
```

## Architecture Notes

### Why Separate Installation?

Playwright's browser binaries are large (100MB+) and platform-specific. Installing them separately:
- Reduces initial package installation time
- Allows users to install only needed browsers
- Enables browser updates independent of Python package updates
- Supports multiple Playwright versions with different browser builds

### Browser Locations

Browsers are installed to:
- **Linux/macOS**: `~/.cache/ms-playwright/`
- **Windows**: `%USERPROFILE%\AppData\Local\ms-playwright\`

### Headless vs Headed Mode

Tests default to headless mode (no visible browser window) for:
- Faster execution
- CI/CD compatibility
- Lower resource usage

To run with visible browser (useful for debugging):
```python
# In test configuration
browser_wrapper = PlaywrightWrapper(headless=False)
```

## Related Documentation

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Test Runner Architecture](TEST_RUNNER_ARCHITECTURE.md)
- [UI Testing Guide](UI_TESTING_README.md)
- [Testing SOP](../TESTING_SOP.md)

## Support

For issues or questions:
1. Check this troubleshooting guide
2. Review test logs in `results/` directory
3. Consult Playwright documentation
4. Open an issue with full error output
