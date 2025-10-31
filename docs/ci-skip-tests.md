# CI Skip Tests

## Overview

The `CI Skip` feature allows test specifications to be marked for exclusion from default CI runs while still being available for manual execution and on-demand testing.

## Use Cases

Mark tests with `CI Skip: true` when they:
- Run for extended periods (24h+ stability tests)
- Consume excessive resources (high-load stress tests)
- Require special infrastructure not available in CI
- Are exploratory/diagnostic tests not needed for regular validation

## Implementation

### 1. Marking Tests

Add `CI Skip: true` to the test specification metadata:

```markdown
## Metadata
- **Category**: performance
- **Priority**: critical
- **Complexity**: complex
- **Duration**: 24-48 hours
- **CI Skip**: true
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker(s), mongodb
```

### 2. CLI Usage

**List tests excluding CI skip**:
```bash
./cli.py --list-specs --category performance --ci-skip
```

**Include all tests (override CI skip)**:
```bash
./cli.py --list-specs --category performance --ci-skip --include-long-running
```

**Run category tests excluding CI skip**:
```bash
./cli.py --category performance --parallel 2 --ci-skip
```

**Run including long-running tests**:
```bash
./cli.py --category performance --parallel 1 --include-long-running
```

### 3. GitHub Actions

CI workflows automatically use `--ci-skip` flag to exclude long-running tests.

**Manual workflow dispatch** includes an `include_long_running` toggle:
- Default (`false`): Excludes CI skip tests for fast validation
- Set to `true`: Includes all tests for comprehensive validation

## Currently Marked Tests

The following tests are marked with `CI Skip: true`:

| Test ID | Category | Duration | Reason |
|---------|----------|----------|--------|
| PERF-003 | performance | 24-48 hours | Long-term stability monitoring |
| PERF-004 | performance | 30-60 minutes | Database load profiling |
| INT-001 | integration | 30-45 minutes | Comprehensive database integration |

## Benefits

1. **Faster CI feedback**: Default CI runs complete in 15-30 minutes instead of hours
2. **Resource efficiency**: Reduces CI runner costs and resource consumption
3. **Flexibility**: Long-running tests available for nightly runs or manual execution
4. **Clear labeling**: Tests marked with `[CI_SKIP]` indicator in listings
5. **Easy override**: Single flag to include all tests when needed

## Best Practices

- Mark tests > 30 minutes as `CI Skip: true`
- Document reason in test specification
- Run CI skip tests regularly (nightly/weekly) to ensure they still work
- Consider creating shorter variants of long tests for CI
- Use `CI Skip: false` or omit field for standard tests
