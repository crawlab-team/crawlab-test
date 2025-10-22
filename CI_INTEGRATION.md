# GitHub Actions CI Integration for Spec-Based Testing

## Overview

This document explains the GitHub Actions CI/CD workflows for the Crawlab test framework. There are two main workflows:

1. **Smoke Tests** (`smoke-test.yml`) - Fast validation of test framework integrity
2. **Test Specs** (`test.yml`) - Full spec-based testing with intelligent category detection

## Workflows

### 1. Smoke Tests

**Purpose**: Fast validation that the test framework itself is working correctly.

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**What it tests**:
- Python syntax validation for all core modules
- CLI functionality (`cli.py --help`, `--list-specs`)
- Test structure integrity (specs directories, backends)
- Spec finder module functionality

**Duration**: ~2-3 minutes

**Artifacts**: None (fast feedback only)

### 2. Test Specs

**Purpose**: Execute actual test specifications to validate Crawlab functionality.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches  
- Manual workflow dispatch with custom parameters

**Test Categories**:
- `api` - API endpoint tests
- `cluster` - Cluster and distributed system tests
- `database` - Database integration tests
- `dependencies` - Package installation and dependency tests
- `scheduler` - Task scheduling and execution tests
- `system` - System configuration and locale tests
- `ui` - User interface and browser automation tests

**Smart Category Detection**: Automatically runs only the test categories affected by your changes:
- Changed `specs/api/**` → Runs API tests only
- Changed `core/**` or `cli.py` → Runs all tests (framework change)
- Changed `specs/ui/**` → Runs UI tests only

**Duration**: Varies by category (5-30 minutes per category)

**Artifacts**: Test results stored for 30 days

## Configuration

### Workflow Parameters (Manual Dispatch)

When manually triggering the **Test Specs** workflow:

- **category**: Choose which tests to run
  - `all` (default) - Run all test categories
  - `api`, `cluster`, `database`, `dependencies`, `scheduler`, `system`, `ui` - Run specific category
  
- **backend**: Choose execution method
  - `auto` (default) - Auto-detect best backend
  - `script` - Use Python script runners
  - `copilot` - Use AI-powered execution
  
- **spec_id**: Run a specific test by ID (e.g., `UI-001`, `CLS-001`)

- **timeout**: Test timeout in minutes (default: 30)

### Environment Variables

Set in GitHub repository settings under **Settings** → **Secrets and variables** → **Actions**:

- `CRAWLAB_LICENSE` - **Required**: Crawlab Pro license key for running tests
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### Docker Image Configuration

The CI workflow uses **Crawlab Pro** by default (`crawlabteam/crawlab-pro:develop`). This is required for:
- gRPC file synchronization tests (CLS-003)
- Advanced clustering features (CLS-001, CLS-002)
- Pro-specific API endpoints
- Enhanced task scheduling

You can specify a different image tag when manually triggering the workflow:
- `develop` (default) - Latest development build
- `latest` - Latest stable release
- `v0.x.x` - Specific version tag

**Note**: Community Edition (`crawlabteam/crawlab:develop`) lacks these features and many tests will fail.

## Understanding Test Results

### Smoke Test Results

The smoke test provides a simple pass/fail summary:

```
✅ Spec finder tests passed
✅ Python syntax checks completed
✅ CLI is executable and functional  
✅ Test structure validated

Status: ✅ All smoke tests passed
```

### Test Spec Results

Each test category produces:

1. **Test Summary** - Pass/fail counts for the category
2. **Detailed Results** - Individual spec outcomes with status
3. **Artifacts** - JSON result files with execution details

Example summary:
```
## Test Results - api

### Results:
- Total tests: 3
- Passed: ✅ 2
- Failed: ❌ 1

### Details:
- ✅ API-001-endpoint-validation
- ✅ API-002-authentication
- ❌ API-003-rate-limiting
```

### Status Indicators

- ✅ **Passed** - Test completed successfully
- ❌ **Failed** - Test failed validation  
- ⏭️ **Skipped** - Test was not run (no changes detected)

## Typical Workflow

### Development on Feature Branch

```bash
# Make changes
git checkout -b feature/my-feature
git commit -m "Add new feature"

# Push to remote - triggers smoke tests on PR
git push origin feature/my-feature
```

### Creating Pull Request

1. Open PR against `main` or `develop`
2. **Smoke tests** run automatically (2-3 min)
3. **Test specs** run automatically for affected categories
4. Review results and fix any failures
5. Merge when all checks pass

### Manual Testing

```bash
# Navigate to Actions tab in GitHub
# Select "Test Specs" workflow
# Click "Run workflow"
# Choose:
#   - category: api
#   - backend: auto
#   - spec_id: (leave blank for all)
#   - timeout: 30
```

## Local Testing Before Push

Always test locally before pushing:

```bash
# List available tests
./cli.py --list-specs

# Run specific test
./cli.py --spec API-001

# Run all tests in a category
./cli.py --list-specs --category api
# Then run each one manually or use shell loop

# Dry run to preview
./cli.py --spec UI-001 --dry-run

# CI mode (same as GitHub Actions runs)
./cli.py --spec CLS-001 --ci
```

## Troubleshooting CI Failures

### Smoke Test Failures

**Symptom**: Python syntax errors or CLI failures

**Solutions**:
1. Run `python -m py_compile <file>` locally to check syntax
2. Test CLI: `./cli.py --help` and `./cli.py --list-specs`
3. Check Python version (must be 3.8+)

**Common causes**:
- Missing dependencies in `requirements.txt`
- Import errors in core modules
- Invalid spec file format

### Test Spec Failures

**Symptom**: Individual test specs failing

**Solutions**:
1. Download artifacts from failed workflow run
2. Review JSON results for error details
3. Run locally: `./cli.py --spec <SPEC-ID> --ci`
4. Check logs for specific error messages

**Common causes**:
- API endpoint changes not reflected in tests
- Timing issues (increase timeout)
- Environment differences (Docker vs local)
- Test data conflicts

### Category Detection Issues

**Symptom**: Wrong tests running or no tests running

**Solutions**:
1. Check which files you changed
2. Verify path patterns in `test.yml` detect-changes job
3. For core changes, all tests should run
4. Manual dispatch lets you override detection

## Advanced Topics

### Backends Explained

**Script Backend** (`--backend script`):
- Executes Python test runners directly
- Fast and deterministic
- Best for API, system, database tests
- Requires runner file in `runners/<category>/`

**Copilot Backend** (`--backend copilot`):
- AI-powered test execution
- Can handle complex scenarios
- Best for exploratory testing
- Slower but more flexible

**Auto Backend** (default):
- Detects best backend per test
- Checks for runner file → uses script
- Falls back to copilot if no runner
- Recommended for most cases

### Environment Requirements

**Smoke Tests**:
- Python 3.9
- Dependencies from `requirements.txt`
- No Docker required

**API/System/Database Tests**:
- Python 3.9
- Crawlab API accessible at `localhost:8080`
- No Docker required (tests remote API)

**Cluster/Scheduler Tests**:
- Python 3.9
- Docker and docker-compose
- Crawlab containers running

**UI Tests**:
- Python 3.9
- Playwright with Chromium
- Crawlab UI accessible
- Docker for full environment

### Artifacts Deep Dive

Each test category produces artifacts with:

**Structure**:
```
test-results-<category>-<run-number>/
  ├── <SPEC-ID>.json      # Detailed test results
  ├── screenshots/        # UI test screenshots
  ├── logs/              # Container/application logs
  └── system-info.txt    # Environment details
```

**Result JSON format**:
```json
{
  "spec_id": "API-001",
  "status": "passed",
  "duration": 12.5,
  "backend": "script",
  "timestamp": "2025-10-22T14:30:00Z",
  "errors": [],
  "steps": [...]
}
```

### Extending Workflows

To add a new test category:

1. **Create specs**: `specs/mynewcat/CAT-001-test-name.md`

2. **Update detection** in `.github/workflows/test.yml`:
```yaml
if echo "$CHANGED_FILES" | grep -qE "^specs/mynewcat/|^runners/mynewcat/"; then
  CATEGORIES+=("mynewcat")
fi
```

3. **Add to matrix**:
```yaml
# Add "mynewcat" to categories array
categories: ${{ fromJson(needs.detect-changes.outputs.categories) }}
```

4. **Test manually**:
```bash
./cli.py --spec CAT-001 --ci
```

5. **Commit and push** - workflow will pick up new category

## Best Practices Summary

✅ **DO**:
- Test locally before pushing
- Use descriptive spec IDs and names
- Keep tests deterministic and fast
- Document prerequisites in specs
- Clean up test data after execution
- Use `--ci` flag to match CI behavior

❌ **DON'T**:
- Rely on external state or data
- Create tests that modify production
- Use hardcoded timeouts (use config)
- Skip cleanup steps
- Commit results/ directory

## Quick Reference

### Common Commands

```bash
# List all tests
./cli.py --list-specs

# Run specific test
./cli.py --spec <SPEC-ID>

# CI mode
./cli.py --spec <SPEC-ID> --ci

# Search tests
./cli.py --search <keyword>

# Dry run
./cli.py --spec <SPEC-ID> --dry-run

# Specific backend
./cli.py --spec <SPEC-ID> --backend script
```

### Workflow Files

- `.github/workflows/smoke-test.yml` - Fast framework validation
- `.github/workflows/test.yml` - Full spec-based testing
- `config.json` - Test framework configuration
- `ci.env` - CI-specific environment (if exists)

### Key Directories

- `specs/` - Test specifications
- `runners/` - Python test runners (script backend)
- `helpers/` - Reusable test utilities
- `backends/` - Backend implementations
- `results/` - Test results (gitignored)

---

**For more details**:
- Framework: [README.md](README.md)
- Testing procedures: [TESTING_SOP.md](TESTING_SOP.md)
- Creating tests: [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)