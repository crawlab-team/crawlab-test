# GitHub Actions CI Integration for Spec-Based Testing

## Overview

This document explains how to use the GitHub Actions integration for Crawlab's spec-based testing framework. The CI system is designed to run comprehensive tests automatically when code is pushed to the `test` branch, providing fast feedback on system stability and functionality.

**Branch-Specific Test Behavior:**
- **`develop` branch**: UI tests are automatically skipped to enable faster development iteration
- **`test` and `main` branches**: All test categories including UI tests are executed
- To test UI changes on `develop`, manually trigger the workflow or merge to `test` branch

**New in 2025**: The CI system now uses the unified `cli.py` test runner with modular backends for improved test execution:
- **Script Backend**: Direct Python/shell script execution via runners
- **Copilot Backend**: AI-powered test execution via GitHub Copilot CLI
- **Playwright Backend**: TypeScript-based UI automation tests
- **Auto-detection**: Automatically selects the best backend for each test

## Key Features

- **Branch-Specific**: Only triggers on the `test` branch to avoid interfering with development workflows
- **Smart Test Selection**: Automatically determines which test categories to run based on file changes
- **Matrix Strategy**: Runs different test categories in parallel with appropriate environments
- **Docker Integration**: Sets up full Crawlab environments for infrastructure testing
- **Artifact Collection**: Saves test results, logs, and system information for analysis
- **Retry Logic**: Automatically retries flaky tests to reduce false negatives

## Workflow Triggers

### Automatic Triggers

The workflow automatically runs when:
- Code is pushed to the `test` branch
- A pull request is opened against the `test` branch
- Code is pushed to the `develop` branch **with `[test]` in the commit message**

### Manual Triggers

You can manually trigger tests with custom parameters:

1. Go to **Actions** tab in GitHub
2. Select **"Spec-Based Testing"** workflow
3. Click **"Run workflow"**
4. Choose your options:
   - **Test category**: `all`, `infrastructure`, `dependencies`, or `ui`
   - **Test method**: `auto`, `script`, or `copilot`
   - **Timeout**: Custom timeout in minutes (default: 30)

### Triggering Tests from Develop Branch

To run tests when pushing to the `develop` branch, include `[test]` in your commit message:

```bash
git commit -m "feat: add new spider feature [test]"
git commit -m "fix: resolve dependency issue [test]"
git commit -m "refactor: improve task reconciliation logic [test]"
```

**Examples:**
- ✅ `"feat: add authentication [test]"` - Will trigger tests
- ✅ `"fix: memory leak issue [test] - updated caching"` - Will trigger tests  
- ❌ `"feat: add authentication"` - Will NOT trigger tests
- ❌ `"docs: update README [tests]"` - Will NOT trigger tests (wrong format)

## Test Categories and Triggers

All test specifications follow the naming convention `[CODE]-[descriptive-name].md` where:
- **DEP**: Dependency-related test cases
- **INF**: Infrastructure-related test cases  
- **UI**: User interface-related test cases

### Infrastructure Tests
**Triggers when changes are detected in:**
- `core/**` - Core application code
- `tests/specs/infrastructure/**` - Infrastructure test specs
- `tests/helpers/infrastructure/**` - Infrastructure test helpers
- `docker/**` - Docker configuration
- `k8s/**` - Kubernetes configuration

**Test Specs:**
- `INF-003-docker-container-node-disconnection-and-recovery.md` - Tests container resilience
- `INF-001-master-worker-node-disconnection-and-reconnection-stability.md` - Tests cluster stability
- `INF-002-task-status-reconciliation-and-process-verification.md` - Tests task status reconciliation

**Environment:** Full Docker environment with Crawlab services

### Dependency Tests
**Triggers when changes are detected in:**
- `**/go.mod`, `**/go.sum` - Go dependencies
- `**/requirements.txt` - Python dependencies
- `**/package.json`, `**/package-lock.json` - Node.js dependencies
- `tests/specs/dependencies/**` - Dependency test specs
- `tests/helpers/dependencies/**` - Dependency test helpers

**Test Specs:**
- `DEP-002-dependency-handler-network-reconnection-resilience.md` - Tests dependency reconnection
- `DEP-001-dependencies-installation-robustness.md` - Tests package installation edge cases

**Environment:** Lightweight environment without Docker

### UI Tests
**Triggers when changes are detected in:**
- `crawlab/frontend/**` - Frontend code
- `tests/specs/ui/**` - UI test specs
- `tests/helpers/ui/**` - UI test helpers

**⚠️ Branch Behavior:**
- **Skipped on `develop` branch** to enable faster development iteration
- **Run on `test` and `main` branches** for comprehensive validation
- To test UI changes from `develop`, merge to `test` branch or manually trigger workflow

**Test Specs:**
- `UI-001-spider-management-workflow-validation.md` - Tests spider management workflows

**Environment:** Full Docker environment with browser automation

## Understanding Test Results

### Status Indicators

- ✅ **Passed**: Test completed successfully
- ❌ **Failed**: Test failed validation criteria
- ⏰ **Timeout**: Test exceeded time limit
- ⏭️ **Skipped**: Test was skipped (manual tests in CI, excluded tests)
- 💥 **Error**: Test encountered an execution error

### Test Summary

Each workflow run includes a summary with:
- Overall test status
- Category breakdown
- Links to test artifacts
- Execution time and environment details

### Artifacts

Test artifacts are automatically collected and stored for 30 days:
- **Test Results**: JSON files with detailed execution results
- **Docker Logs**: Container logs for infrastructure tests
- **System Information**: Environment details and versions
- **Screenshots**: UI test screenshots (when applicable)

## Configuration

### Environment Variables

The following environment variables can be set in GitHub repository settings:

- `CRAWLAB_API_TOKEN`: API token for Crawlab authentication (optional)
- `TEST_TIMEOUT_MINUTES`: Global timeout override (default: 30)
- `TEST_RETRY_COUNT`: Number of retries for flaky tests (default: 2)

### CI Configuration File

The `tests/ci.env` file contains CI-specific settings:

```bash
# Test Execution Settings
TEST_TIMEOUT_MINUTES=30
TEST_RETRY_COUNT=2

# Docker Settings
CRAWLAB_STARTUP_TIMEOUT=120

# Test Exclusions
EXCLUDED_TESTS=manual-interaction,browser-specific
```

## Troubleshooting

### Common Issues

#### Tests Timing Out
- Check if timeout values are appropriate for your tests
- Verify Docker services are starting correctly
- Look at system resource usage in artifacts

#### Docker Service Failures
- Check Docker logs in test artifacts
- Verify docker-compose.yml is correct
- Ensure all required ports are available

#### Flaky Tests
- Tests automatically retry up to 2 times
- Check test artifacts for intermittent issues
- Consider adjusting timeout values in `ci.env`

### Debugging Steps

1. **Review the workflow log**: Check GitHub Actions logs for detailed execution
2. **Download artifacts**: Get test results and logs for local analysis
3. **Run locally**: Execute the same test spec locally using the test runner
4. **Check CI config**: Verify settings in `tests/ci.env` are appropriate

### Example Debugging Commands

```bash
# Run the same test locally using the new unified CLI
cd tests/
./cli.py --spec specs/infrastructure/INF-003-docker-container-node-disconnection-and-recovery.md --ci

# Or use spec ID directly
./cli.py --spec INF-003 --ci

# Check test runner configuration
./cli.py --list-specs

# Search for tests
./cli.py --search docker

# Run with specific backend
./cli.py --spec INF-001 --backend script
./cli.py --spec UI-001 --backend copilot

# Dry run to see what would execute
./cli.py --spec INF-001 --dry-run
```

## Best Practices

### For Developers

1. **Test locally first**: Run tests locally before pushing to test branch using `./cli.py --spec <test-id>`
2. **Use the unified CLI**: Prefer `cli.py` over legacy scripts for better auto-detection and error messages
3. **Use meaningful commit messages**: Help identify what changes might affect tests
4. **Monitor test results**: Check GitHub Actions after pushing changes
5. **Update test specs**: Keep test specifications current with code changes
6. **Leverage backend flexibility**: Use `--backend` flag to test with specific execution methods

### For Test Maintenance

1. **Regular spec updates**: Review and update test specifications quarterly
2. **Timeout tuning**: Adjust timeouts based on actual execution times
3. **Helper script maintenance**: Keep helper scripts current with API changes
4. **Artifact cleanup**: Regularly review and clean up old test artifacts

## Integration with Development Workflow

### Recommended Branch Strategy

```
main ← develop ← feature-branch
  ↑
test (CI testing)
```

1. **Development**: Work on feature branches, merge to `develop`
2. **Testing**: Merge `develop` to `test` branch for CI validation
3. **Release**: Merge tested changes from `test` to `main`

### Pre-Release Testing

Before major releases:

1. Merge latest `develop` to `test` branch
2. Run comprehensive tests via manual workflow dispatch
3. Review all test artifacts and results
4. Fix any issues and re-test
5. Merge to `main` when all tests pass

## MCP (Model Context Protocol) Configuration

**✅ Configured in GitHub Actions**: The MCP configuration is automatically set up in our workflow.

### Playwright MCP Server

The `tests/mcp-config.json` file is automatically installed to `~/.copilot/mcp-config.json` during CI setup:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

### GitHub Actions Integration

The setup is handled in `.github/workflows/copilot-setup-steps.yml`:

- **Step 11**: Sets up MCP configuration and installs Playwright MCP server
- **Location**: `~/.copilot/mcp-config.json` 
- **Automatic**: Copilot CLI automatically loads configs from this standard location

When you create additional test workflows that use the Copilot backend:

```yaml
- name: Setup MCP configuration
  run: |
    mkdir -p ~/.copilot
    cp tests/mcp-config.json ~/.copilot/mcp-config.json
    npm install -g @playwright/mcp

- name: Run tests with Copilot
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    ./tests/cli.py --spec UI-001 --backend copilot --ci
```

For more details, see [MCP_SETUP.md](MCP_SETUP.md).

## Extending the CI System

### Adding New Test Categories

1. Create test specs in `tests/specs/[new-category]/`
2. Add runners in `tests/runners/[new-category]/` (for script backend)
3. Optionally add helpers in `tests/helpers/[new-category]/`
4. Create a `_matrix.json` configuration file in `tests/specs/[new-category]/`:
   ```json
   {
     "timeout": 30,
     "default_method": "script",
     "paths": [
       "path/to/trigger/files/**",
       "tests/specs/[new-category]/**"
     ]
   }
   ```
4. Update `.github/workflows/spec-tests.yml` matrix configuration
5. Update path filters in `detect-changes` job
6. Test the new category manually

**Matrix Configuration Options:**
- `timeout`: Test timeout in minutes (default: 30)
- `default_method`: Execution method - `"script"` or `"copilot"` (default: auto-detected)
- `paths`: File patterns that trigger tests for this category
- `fallback`: If true, runs when no specific category matches (default: false)
- `extra_triggers`: Additional trigger conditions (e.g., `["CHANGES_CORE_CODE"]`)

### Adding New Test Specs

1. Use `tests/SPEC_TEMPLATE.md` as starting point
2. Place in appropriate category directory
3. Create helper scripts if needed
4. Test locally before committing
5. Document any special requirements

### Customizing Test Execution

Modify `tests/ci.env` to adjust:
- Timeout values per category
- Retry counts for flaky tests
- Test exclusions for CI environment
- Resource limits and constraints

## Monitoring and Alerts

### GitHub Integration

- Test results appear as status checks on pull requests
- Failed tests block merge if branch protection is enabled
- Test summaries are posted as workflow comments

### Notification Options

Configure GitHub repository settings for:
- Email notifications on test failures
- Slack/Teams integration for team alerts
- Custom webhooks for advanced monitoring

## Security Considerations

- API tokens are stored as encrypted GitHub secrets
- Test environments are isolated and ephemeral
- No sensitive data is stored in test artifacts
- Docker containers run with minimal privileges

## Performance Optimization

### Parallel Execution
- Different test categories run in parallel
- Matrix strategy maximizes resource utilization
- Conditional triggers avoid unnecessary test runs

### Caching
- Python dependencies are cached between runs
- Docker layers are cached when possible
- Test artifacts are compressed for faster uploads

### Resource Management
- Tests have strict timeout limits
- Docker containers are cleaned up after each run
- System resources are monitored and limited

---

For more information about the underlying test framework, see:
- [README.md](README.md) - Framework overview
- [TESTING_SOP.md](TESTING_SOP.md) - Detailed testing procedures
- [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) - Template for creating new tests