# Test Runner Architecture

## Architecture Overview

```mermaid
graph TB
    CLI[cli.py<br/>Main Entry Point<br/>• Parse arguments<br/>• Select backend<br/>• Handle results]
    
    subgraph "Core Modules"
        SF[spec_finder.py<br/>Find & search specs]
        RH[result_handler.py<br/>Save results]
        DD[docker_detector.py<br/>Detect Docker env]
        CF[config.py<br/>Load config]
    end
    
    subgraph "Backends"
        SB[script_backend<br/>• Run Python/shell<br/>• Parse output<br/>• Retry logic]
        CB[copilot_backend<br/>• Auth & setup<br/>• AI execution<br/>• MCP tools]
    end
    
    CLI --> SF
    CLI --> RH
    CLI --> DD
    CLI --> CF
    CLI --> SB
    CLI --> CB
    
    CB -.MCP.-> PT[Playwright Tools<br/>Browser automation]
    
    style CLI fill:#4CAF50,stroke:#333,stroke-width:3px,color:#fff
    style SB fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style CB fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style PT fill:#9C27B0,stroke:#333,stroke-width:2px,color:#fff
    style SF fill:#e3f2fd,stroke:#333,stroke-width:1px,color:#000
    style RH fill:#e3f2fd,stroke:#333,stroke-width:1px,color:#000
    style DD fill:#e3f2fd,stroke:#333,stroke-width:1px,color:#000
    style CF fill:#e3f2fd,stroke:#333,stroke-width:1px,color:#000
```

## Component Responsibilities

### cli.py (Main Entry Point)
- **Purpose**: Single unified interface for all test execution
- **Responsibilities**:
  - Parse command-line arguments
  - Load configuration
  - Select appropriate backend
  - Coordinate test execution
  - Handle results and reporting
- **Dependencies**: All core modules, all backends

### Core Modules

#### spec_finder.py
- Find specs by ID (e.g., `UI-001`)
- Fuzzy search by title/keywords
- List available specs
- Parse spec metadata

#### result_handler.py
- Save test results to JSON
- Generate reports (text, JSON, markdown)
- CI integration (GitHub Actions summaries)
- Result validation

#### docker_detector.py
- Detect Docker environment
- Find Crawlab containers
- Get API URLs
- Container health checks

#### config.py
- Load ci.env configuration
- Environment variable handling
- Timeout and retry settings
- Category-specific config

### Backends

#### script_backend.py
- Execute Python/Shell test scripts
- Retry logic
- Output capture and parsing
- Return code handling

#### copilot_backend.py
- GitHub authentication check
- Build Copilot prompts
- Execute via Copilot CLI
- Validate test execution
- Parse structured results

#### playwright_backend.py
- Check Node.js/pnpm
- Install dependencies
- Install Playwright browsers
- Execute TypeScript tests
- Parse Playwright JSON results

## Data Flow

```mermaid
flowchart TD
    A[User Command<br/>./cli.py --spec UI-001 --backend auto]
    B[cli.py: Parse arguments]
    C[spec_finder.py<br/>Find spec<br/>UI-001 → specs/ui/UI-001-....md]
    D[config.py<br/>Load configuration<br/>ci.env, env vars, timeouts]
    E[cli.py: Select backend<br/>auto → script runner found]
    F[script_backend.py<br/>• Check prerequisites<br/>• Execute runner<br/>• Capture output<br/>• Return result]
    G[result_handler.py<br/>• Save to results/<br/>• Generate summary<br/>• GitHub Actions output]
    H[Exit Code<br/>0=success, 1=fail]
    
    A --> B --> C --> D --> E --> F --> G --> H
    
    style A fill:#e1f5ff,stroke:#333,stroke-width:2px,color:#000
    style B fill:#fff3e0,stroke:#333,stroke-width:2px,color:#000
    style C fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style E fill:#fff3e0,stroke:#333,stroke-width:2px,color:#000
    style F fill:#e3f2fd,stroke:#333,stroke-width:2px,color:#000
    style G fill:#e8f5e9,stroke:#333,stroke-width:2px,color:#000
    style H fill:#c8e6c9,stroke:#333,stroke-width:3px,color:#000
```

## Backend Selection Logic

```python
def select_backend(spec_path: Path, backend_arg: str) -> TestBackend:
    """Select appropriate backend for test execution"""
    
    if backend_arg != "auto":
        # User explicitly specified backend
        return get_backend(backend_arg)
    
    # Auto-detect based on spec and environment
    
    # 1. Check for category-specific runner
    category = get_category(spec_path)
    runner_script = find_runner_script(category, spec_path)
    
    if runner_script:
        return ScriptBackend()
    
    # 2. Check for UI/Playwright specs
    if category == "ui" and playwright_available():
        return PlaywrightBackend()
    
    # 3. Check for helper scripts (legacy)
    helper_script = find_helper_script(category, spec_path)
    
    if helper_script:
        return ScriptBackend()
    
    # 4. Default to Copilot for unimplemented tests
    if copilot_available():
        return CopilotBackend()
    
    # 5. Fail if no backend available
    raise NoBackendAvailableError(
        "No suitable backend found for this test. "
        "Consider adding a runner script or using --backend copilot"
    )
```

## Migration Path

```mermaid
graph LR
    subgraph "Phase 1: Coexistence"
        P1A[Legacy Scripts<br/>Still work]
        P1B[New CLI<br/>Available]
    end
    
    subgraph "Phase 2: Deprecation"
        P2A[Legacy Scripts<br/>Show warnings]
        P2B[New CLI<br/>Recommended]
    end
    
    subgraph "Phase 3: Complete"
        P3[cli.py<br/>Single entry point]
    end
    
    P1A -.-> P1B
    P1B --> P2A
    P2A -.-> P2B
    P2B --> P3
    
    style P1A fill:#fff3e0,stroke:#333,color:#000
    style P1B fill:#e8f5e9,stroke:#333,color:#000
    style P2A fill:#ffe0b2,stroke:#333,color:#000
    style P2B fill:#c8e6c9,stroke:#333,color:#000
    style P3 fill:#4CAF50,stroke:#333,stroke-width:3px,color:#fff
```

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Entry points** | 3 separate scripts | 1 main CLI + 3 wrappers |
| **Code duplication** | High (3 scripts) | Low (shared core) |
| **Maintainability** | Hard (scattered) | Easy (modular) |
| **Testability** | Difficult | Easy (unit test each module) |
| **User clarity** | Confusing | Clear (`cli.py` is main) |
| **Extensibility** | Hard (modify scripts) | Easy (add backend) |
| **Backward compat** | N/A | Maintained via wrappers |

## Future Enhancements

Once the refactoring is complete, these enhancements become easier:

1. **New backends**: Add Go test backend, REST API backend, etc.
2. **Parallel execution**: Run multiple tests concurrently
3. **Test queuing**: Queue tests in CI environment
4. **Better reporting**: HTML reports, test trends, dashboards
5. **Plugin system**: User-defined backends
6. **Remote execution**: Run tests on remote workers
7. **Test orchestration**: Complex test workflows

## Conclusion

The refactoring transforms the test infrastructure from a collection of scripts into a well-architected system with clear responsibilities and modular design. This follows the **Occam's Razor** principle by simplifying the architecture while maintaining all functionality.


## Execution Details & Reporting

The Copilot backend now captures comprehensive execution details including step-by-step results, issues, logs, and error information. This data is automatically parsed and displayed in GitHub Actions summaries for better visibility and debugging.

## Features

### 1. Step Execution Tracking

The system automatically detects and parses step execution from Copilot output:

- **Pattern Recognition**: Detects common step indicators like "Step 1:", "✓ Step", "✗ Step"
- **Status Tracking**: Identifies passed (✅), failed (❌), and skipped (⚠️) steps
- **Display**: Shows up to 20 steps in GitHub Actions summary

### 2. Issue Detection

Automatically captures errors, warnings, and exceptions:

- **Error Patterns**: Detects "Error:", "Exception:", "Failed:", "Warning:"
- **Context**: Captures the full error message
- **Display**: Shows first 10 issues in GitHub Actions summary

### 3. Log Extraction

Captures execution logs for debugging:

- **Format Recognition**: Detects timestamped logs and standard log levels (INFO, DEBUG, ERROR)
- **Truncation**: Keeps first 50 and last 50 entries if logs exceed 100 lines
- **Display**: Collapsible section in GitHub Actions summary

### 4. Raw Output Capture

Preserves complete stdout and stderr:

- **Full Capture**: All console output is saved
- **Truncation**: Automatically truncates very long output (>10KB for stdout, >5KB for stderr)
- **Display**: Collapsible sections in GitHub Actions summary

## GitHub Actions Summary Format

When tests run in CI, the summary includes:

```markdown
# ✅ Test Execution: PASSED

## Test Information
| Attribute | Value |
|-----------|-------|
| **Specification** | `specs/ui/UI-001-...` |
| **Status** | ✅ **PASSED** |
| **Exit Code** | `0` |
| **Timestamp** | 2025-10-10 14:30:00 UTC |

## 📊 Test Execution Summary
| Metric | Value |
|--------|-------|
| **Total Steps** | 6 |
| **Completed** | ✅ 6 |
| **Failed** | ❌ 0 |
| **Backend** | `copilot` |

## 📝 Step Execution Details
1. ✅ Step 1: Login to Crawlab
2. ✅ Step 2: Navigate to Spiders Page
3. ✅ Step 3: Verify Spider List
4. ✅ Step 4: Create New Spider
5. ✅ Step 5: Verify Spider in List
6. ✅ Step 6: Delete Test Spider

## 📋 Execution Logs
<details>
<summary>Click to expand logs</summary>
...
</details>

## 📋 Raw Output (stdout)
<details>
<summary>Click to expand stdout</summary>
...
</details>
```

## Enhanced Test Reporting

### For Copilot-Executed Tests

When Copilot executes tests, it should use the enhanced reporting tool:

```bash
./tests/tools/report_test_result.py \
  --status passed \
  --total-steps 6 \
  --completed-steps 6 \
  --duration "3m 45s" \
  --step-details '[
    {"step": 1, "name": "Login", "status": "passed"},
    {"step": 2, "name": "Navigate", "status": "passed"},
    {"step": 3, "name": "Create Spider", "status": "passed"}
  ]' \
  --issues '[]'
```

### For Failed Tests

```bash
./tests/tools/report_test_result.py \
  --status failed \
  --total-steps 6 \
  --completed-steps 3 \
  --failed-steps 1 \
  --reason "Step 4: Spider creation failed - form validation error" \
  --issues '[
    {"type": "error", "message": "Required field missing: spider name", "step": 4},
    {"type": "validation", "message": "Form validation failed", "step": 4}
  ]'
```

## Parsing Details

### Step Recognition Patterns

The system looks for:
- `Step N:` - Standard numbered steps
- `✓ Step N:` or `✗ Step N:` - Steps with status indicators
- `N) Action... passed/failed` - Alternative numbering

### Error/Issue Patterns

- `Error: <message>`
- `Exception: <message>`
- `Failed: <message>`
- `Warning: <message>`

### Log Patterns

- Lines with timestamps: `2025-10-10 14:30:00`
- Lines with log levels: `INFO`, `DEBUG`, `WARNING`, `ERROR`

## Benefits

1. **Better Visibility**: See exactly what happened during test execution
2. **Faster Debugging**: Quickly identify which step failed and why
3. **Historical Record**: All execution details saved in result JSON files
4. **CI Integration**: Rich summaries in GitHub Actions without digging through logs
5. **Pattern Analysis**: Automated parsing means consistent data structure

## Configuration

No configuration needed! The parsing happens automatically in the Copilot backend.

To adjust parsing behavior, edit:
- `/tests/backends/copilot_backend.py` - `_parse_execution_details()` method

## Example Output

See `/tests/results/` directory for example JSON result files with execution details.

## Future Enhancements

Potential improvements:
- Screenshot/artifact capture
- Performance metrics (step duration)
- Test coverage reporting
- Flakiness detection
- Automatic retry with detailed comparison
