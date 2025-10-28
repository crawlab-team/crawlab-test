# CI/CD Troubleshooting Guide

## Investigation Workflow

When tests fail in CI/CD environments, follow this systematic approach:

### 1. Identify the Failure

- Check GitHub Actions workflow status
- Note which test(s) failed
- Check if it's a single failure, pattern, or flaky behavior

### 2. Access Workflow Logs and Artifacts

**Via GitHub Web UI:**
- Navigate to Actions tab → Failed workflow run
- Review job logs for error messages
- Download artifacts (test results, screenshots, logs)

**Via GitHub CLI (if available):**
```bash
# List recent workflow runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### 3. Analyze Artifacts

Test runs produce several artifacts that help diagnose issues:

| Artifact | Contains | Use For |
|----------|----------|---------|
| **test-results** | JSON test reports, pass/fail status | Understanding what assertions failed |
| **screenshots** | UI test screenshots at each step | Visual debugging of UI tests |
| **system-info** | Docker containers, network state, versions | Environment verification |
| **logs** | Application logs, test runner logs | Detailed execution traces |

### 4. Reproduce Locally

```bash
# Run test with CI flag to simulate CI environment
uv run ./cli.py --spec <TEST-ID> --ci --timeout 15

# Or run in Docker if needed
docker-compose -f docker-compose.test.yml up -d
uv run ./cli.py --spec <TEST-ID>
```

### 5. Compare Environments

Common differences between local and CI:

| Aspect | Local | CI |
|--------|-------|-----|
| **Resources** | Full system resources | CPU/memory limits |
| **Network** | Fast localhost | Potential latency |
| **State** | May have leftover data | Clean state each run |
| **Timing** | Faster | Potential throttling |

## Common Failure Patterns

### Timeout Failures

**Symptoms:**
- Test exceeds time limit (default 15min)
- Hangs waiting for response
- No output for extended period

**Investigation:**
1. Check workflow logs for last action before timeout
2. Review container health in system-info artifact
3. Look for network-related errors

**Common Causes:**
- Container not starting properly
- Database connection issues
- Task stuck in "pending" state
- API endpoint not responding

**Solutions:**
```bash
# Increase timeout for specific tests
uv run ./cli.py --spec <TEST-ID> --timeout 30

# Add health checks before proceeding
./helpers/tools/docker_manager.py --action health

# Verify all services are up
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Flaky Tests

**Symptoms:**
- Test passes sometimes, fails others
- Different failure points across runs
- Race conditions or timing issues

**Investigation:**
1. Run test multiple times locally (5-10 runs)
2. Compare multiple CI runs to find patterns
3. Check for non-deterministic operations

**Common Causes:**
- Insufficient wait times for async operations
- Race conditions in concurrent operations
- External service dependencies
- Random test data causing conflicts

**Solutions:**
```python
# Add explicit waits
time.sleep(2)  # Wait for async operation

# Poll for conditions instead of fixed waits
for _ in range(30):  # 30 seconds max
    status = get_task_status(task_id)
    if status in ['finished', 'error']:
        break
    time.sleep(1)

# Use deterministic test data
test_name = f"test-spider-{int(time.time())}-{os.getpid()}"
```

### Environment Issues

**Symptoms:**
- "Connection refused" errors
- Missing dependencies
- Configuration mismatches

**Investigation:**
1. Download system-info artifact
2. Verify all containers are running
3. Check environment variables

**Common Causes:**
- Docker containers not fully started
- Database not ready to accept connections
- Missing environment variables
- Volume mount issues in CI

**Solutions:**
```bash
# Add startup wait in test script
echo "Waiting for services to be ready..."
sleep 10

# Verify service health before tests
docker exec crawlab_master curl -f http://localhost:8080/health || exit 1

# Check environment
env | grep CRAWLAB
```

### Assertion Failures

**Symptoms:**
- Expected vs actual value mismatch
- Unexpected error responses
- Missing data in responses

**Investigation:**
1. Review test output in test-results artifact
2. Check application logs for backend errors
3. Verify API response format (see [API_TEST_TROUBLESHOOTING.md](API_TEST_TROUBLESHOOTING.md))

**Common Causes:**
- API format changes
- Incorrect assumptions about response structure
- Backend logic changes
- Test data setup issues

**Solutions:**
1. Check OpenAPI spec for current format
2. Update test expectations
3. Add more defensive parsing
4. Improve error messages in tests

## GitHub Actions Integration

### Workflow Structure

Typical test workflow has these steps:

1. **Checkout code** - Get latest code
2. **Setup dependencies** - Install Python, uv, etc.
3. **Start services** - Docker compose up
4. **Wait for readiness** - Health checks
5. **Run tests** - Execute test suite
6. **Upload artifacts** - Save results/screenshots
7. **Cleanup** - Stop containers

### Creating Issues for Failures

When a test consistently fails:

```markdown
**Title:** [TEST-ID] Test failing in CI: <brief description>

**Labels:** bug, test-failure, ci

**Body:**
## Test Information
- Test ID: <TEST-ID>
- Test Name: <name>
- Failure Rate: X/Y runs

## Failure Pattern
<Description of what's failing>

## Reproduction Steps
1. Run test in CI environment
2. Observe failure at step X

## Logs and Artifacts
- Workflow run: <link>
- Error message: <paste relevant logs>
- Screenshots: <if UI test>

## Investigation
<What you've checked so far>

## Environment
- CI Runner: <ubuntu/macos>
- Docker version: <from system-info>
- Crawlab version: <from system-info>
```

### Commenting on Existing Issues

When adding new information to existing test failure issues:

```markdown
## Update - <Date>

**Status:** Still failing / Fixed / Intermittent

**Recent Runs:**
- Run #123: Failed - <link>
- Run #124: Passed - <link>
- Run #125: Failed - <link>

**New Findings:**
<What you discovered>

**Potential Root Cause:**
<Your analysis>

**Next Steps:**
- [ ] Try fix X
- [ ] Investigate Y
- [ ] Update test to Z
```

## Best Practices

### Before Committing

```bash
# Run test locally multiple times
for i in {1..5}; do
    echo "Run $i of 5"
    uv run ./cli.py --spec <TEST-ID> || exit 1
done

# Run with CI flag
uv run ./cli.py --spec <TEST-ID> --ci

# Check Docker state
./helpers/tools/docker_manager.py --action health
```

### After CI Failure

1. **Don't assume it's flaky** - Investigate first
2. **Download artifacts** - Check screenshots/logs before re-running
3. **Look for patterns** - Check if same test fails elsewhere
4. **Fix, don't skip** - Disabled tests accumulate technical debt
5. **Update docs** - Document known issues and workarounds

### Test Maintenance

```bash
# Regularly clean up Docker
docker system prune -f

# Update dependencies
cd crawlab-test
uv sync --upgrade

# Verify all tests still pass
uv run ./cli.py --list-specs | while read spec; do
    echo "Testing $spec..."
    uv run ./cli.py --spec "$spec" --ci || echo "FAILED: $spec"
done
```

## Quick Reference

### Essential Commands

```bash
# Check CI test locally
uv run ./cli.py --spec <TEST-ID> --ci

# View Docker logs
docker-compose logs -f master

# Check container health
./helpers/tools/docker_manager.py --action health

# Download latest CI artifacts
gh run download $(gh run list --limit 1 --json databaseId -q '.[0].databaseId')

# Re-run failed workflow
gh run rerun <run-id>
```

### Key Files

- **CI Workflow**: `.github/workflows/test.yml` (if exists)
- **Docker Compose**: `docker-compose.test.yml`
- **Test Config**: `config.json`
- **CI Environment**: `ci.env`

### Links

- [API Test Troubleshooting](API_TEST_TROUBLESHOOTING.md)
- [Testing SOP](../TESTING_SOP.md)
- [CI Integration Guide](../CI_INTEGRATION.md)
- [Architecture Overview](architecture.md)

---

**Remember:** Most CI failures are reproducible locally with the right setup. Take time to investigate properly rather than re-running hoping for success. 🔍
