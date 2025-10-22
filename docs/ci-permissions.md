# GitHub Copilot CLI Permissions in CI Environments

## Problem

When running `run-with-copilot.py` in GitHub Actions CI environments, the Copilot CLI fails with:

```
Permission denied and could not request permission from user
```

This happens because Copilot CLI requires **interactive approval** for tool execution by default, but CI environments have:

- ❌ No TTY (terminal) available
- ❌ No stdin for user input  
- ❌ No user to approve tool requests
- ❌ Non-interactive shell

## Root Cause

The test runner has different execution modes (`interactive`, `automated`, `safe`, `ui`, `docker`), each with different tool approval configurations.

When `ui` mode was used in CI, it only pre-approved these tools:
```python
'--allow-tool', 'shell(npm)',
'--allow-tool', 'shell(node)',
'--allow-tool', 'shell(npx)',
```

But the test needed to run diagnostic commands like:
- `curl` - to check if app is accessible ❌
- `docker ps` - to check containers ❌
- `netstat`/`ss` - to check ports ❌
- `ps aux` - to check processes ❌

Since these weren't pre-approved, Copilot tried to request permission interactively, which failed in CI.

## Solution

The `run-with-copilot.py` script now:

### 1. Auto-detects CI Environments

```python
is_ci = os.getenv('CI') or os.getenv('GITHUB_ACTIONS')
```

### 2. Forces Full Tool Approval in CI

When CI is detected, regardless of the mode specified, it uses:

```python
if self.mode == 'automated' or is_ci:
    cmd.extend([
        '--allow-all-tools',  # Pre-approve all tools
        '--deny-tool', 'shell(rm -rf)',  # Safety guards
        '--deny-tool', 'shell(git push)',
        '--deny-tool', 'shell(git force-push)',
    ])
```

### 3. Enhanced UI Mode

The `ui` mode now includes essential diagnostic tools:

```python
elif self.mode == 'ui':
    cmd.extend([
        '--allow-tool', 'write',
        '--allow-tool', 'shell(npm)',
        '--allow-tool', 'shell(node)',
        '--allow-tool', 'shell(npx)',
        '--allow-tool', 'shell(curl)',      # Environment checks
        '--allow-tool', 'shell(docker)',    # Container checks
        '--allow-tool', 'shell(ps)',        # Process checks
        '--allow-tool', 'shell(netstat)',   # Port checks
        '--allow-tool', 'shell(ss)',        # Alternative port checker
        '--allow-tool', 'shell(python)',    # Test scripts
        '--deny-tool', 'shell(rm)',
    ])
```

## Usage

### In GitHub Actions

The script automatically detects CI and enables full tool approval:

```yaml
- name: Run UI Test
  run: |
    ./tests/run-with-copilot.py \
      specs/ui/UI-001-spider-management-workflow-validation.md \
      ui
```

You'll see:
```
CI environment detected - using automated mode with full tool approval
```

### Locally

For local development, you can still use different modes:

```bash
# Interactive mode (default) - manual approval
./tests/run-with-copilot.py specs/ui/UI-001.md

# Automated mode - full tool approval
./tests/run-with-copilot.py specs/ui/UI-001.md automated

# UI mode - selective but comprehensive tool approval
./tests/run-with-copilot.py specs/ui/UI-001.md ui
```

## Safety Considerations

The script maintains safety even with `--allow-all-tools`:

1. **Denies destructive operations**:
   - `rm -rf` 
   - `git push`
   - `git force-push`

2. **Runs from repository root** - not system root

3. **Logs all operations** to `tests/results/copilot_*.log`

4. **Generates structured output** for validation

## Best Practices

1. **Always use specific modes locally** - don't default to `automated`
2. **Review logs** after CI runs to understand what was executed
3. **Add new tool denials** if you discover risky patterns
4. **Test mode changes locally** before deploying to CI

## Related Files

- `/tests/run-with-copilot.py` - Main test runner
- `/tests/config.json` - Test configuration
- `/.github/workflows/*.yml` - CI workflow definitions
- `/tests/specs/ui/` - UI test specifications
- `/tests/docs/UI_TESTING_README.md` - UI testing guidelines
