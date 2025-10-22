# Test Tools

This directory contains tools that Copilot agents can use during test execution.

## report_test_result.py

Reports structured test execution results for the test framework.

### Purpose

When Copilot executes a test specification, it needs to report the results in a structured format that the CLI framework can parse. This tool provides a standardized way to report:

- Test status (passed/failed/skipped)
- Step counts (total, completed, failed, skipped)
- Failure reasons
- Duration
- Error details

### Usage

```bash
# All tests passed
./tests/tools/report_test_result.py \
  --status passed \
  --total-steps 6 \
  --completed-steps 6

# Test failed at step 3
./tests/tools/report_test_result.py \
  --status failed \
  --total-steps 6 \
  --completed-steps 2 \
  --failed-steps 1 \
  --reason "Step 3: Spider creation failed - missing required field" \
  --duration "45s"

# Test skipped due to prerequisites
./tests/tools/report_test_result.py \
  --status skipped \
  --reason "Prerequisites not met: Browser not available"

# Test failed with detailed error
./tests/tools/report_test_result.py \
  --status failed \
  --total-steps 6 \
  --completed-steps 4 \
  --failed-steps 1 \
  --reason "Step 5: Element not found" \
  --error-details "TimeoutError: Element '.spider-row' not found after 30s"
```

### Arguments

- `--status`: **Required**. One of: `passed`, `failed`, `skipped`
- `--reason`: Optional. Explanation for failure or skip
- `--total-steps`: Optional. Total number of test steps (default: 0)
- `--completed-steps`: Optional. Number of successfully completed steps (default: 0)
- `--failed-steps`: Optional. Number of failed steps (default: 0)
- `--skipped-steps`: Optional. Number of skipped steps (default: 0)
- `--duration`: Optional. Test duration (e.g., "2m 30s", "150s")
- `--error-details`: Optional. Detailed error information for debugging

### Output

The tool outputs JSON to stdout and saves it to `results/copilot_last_report.json`:

```json
{
  "test_execution_report": {
    "timestamp": "2025-10-10T12:15:06.242691",
    "executed": true,
    "status": "passed",
    "total_steps": 6,
    "completed_steps": 6,
    "failed_steps": 0,
    "skipped_steps": 0,
    "duration": "2m 15s"
  }
}
```

### Exit Codes

- `0`: Test passed or skipped
- `1`: Test failed

### Integration with CLI

The Copilot backend reads `results/copilot_last_report.json` after execution to determine the actual test status, rather than relying solely on exit codes.

This ensures:
- **Reliable status reporting**: Exit codes alone can be unreliable (e.g., 130 = user cancelled)
- **Rich metadata**: Step counts, durations, and failure details
- **Structured output**: Consistent JSON format for downstream processing

## Adding New Tools

When adding new tools for Copilot agents:

1. Create executable Python script in this directory
2. Add clear `--help` documentation
3. Use structured JSON output
4. Document in this README
5. Update test specifications to mention the tool
6. Consider exit codes and error handling
