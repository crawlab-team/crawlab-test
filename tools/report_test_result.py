#!/usr/bin/env python3
"""
Test Result Reporting Tool

This tool allows Copilot agents to report structured test execution results.
When Copilot completes a test, it should call this script with the test results.

Usage:
    # Simple pass
    ./tools/report_test_result.py --status passed --total-steps 6 --completed-steps 6

    # Pass with step details
    ./tools/report_test_result.py --status passed --total-steps 6 --completed-steps 6 --duration "3m 45s" \\
        --step-details '[{"step": 1, "name": "Login", "status": "passed"}, {"step": 2, "name": "Navigate", "status": "passed"}]'

    # Failure with details
    ./tools/report_test_result.py --status failed --reason "Step 3 failed" --total-steps 6 --completed-steps 2 --failed-steps 1 \\
        --issues '[{"type": "error", "message": "Element not found", "step": 3}]'

    # Skipped test
    ./tools/report_test_result.py --status skipped --reason "Prerequisites not met"
"""

import argparse
import json
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Report test execution results in structured format")

    parser.add_argument(
        "--status", choices=["passed", "failed", "skipped"], required=True, help="Test execution status"
    )

    parser.add_argument("--reason", help="Reason for failure or skip (optional for passed tests)")

    parser.add_argument("--total-steps", type=int, default=0, help="Total number of test steps")

    parser.add_argument("--completed-steps", type=int, default=0, help="Number of completed steps")

    parser.add_argument("--failed-steps", type=int, default=0, help="Number of failed steps")

    parser.add_argument("--skipped-steps", type=int, default=0, help="Number of skipped steps")

    parser.add_argument("--duration", help='Test duration (e.g., "2m 30s" or "150s")')

    parser.add_argument("--error-details", help="Detailed error information (optional)")

    parser.add_argument("--step-details", help="JSON string with step-by-step execution details (optional)")

    parser.add_argument("--issues", help="JSON string with issues/errors encountered (optional)")

    args = parser.parse_args()

    # Build structured result
    result = {
        "test_execution_report": {
            "timestamp": datetime.now().isoformat(),
            "executed": True,
            "status": args.status,
            "total_steps": args.total_steps,
            "completed_steps": args.completed_steps,
            "failed_steps": args.failed_steps,
            "skipped_steps": args.skipped_steps,
        }
    }

    # Add optional fields
    if args.reason:
        result["test_execution_report"]["reason"] = args.reason

    if args.duration:
        result["test_execution_report"]["duration"] = args.duration

    if args.error_details:
        result["test_execution_report"]["error_details"] = args.error_details

    # Parse and add step details if provided
    if args.step_details:
        try:
            step_details = json.loads(args.step_details)
            result["test_execution_report"]["step_details"] = step_details
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse step details JSON: {e}", file=sys.stderr)

    # Parse and add issues if provided
    if args.issues:
        try:
            issues = json.loads(args.issues)
            result["test_execution_report"]["issues"] = issues
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse issues JSON: {e}", file=sys.stderr)

    # Output as JSON (this is what the CLI backend will parse)
    print("\n" + "=" * 80)
    print("TEST EXECUTION REPORT")
    print("=" * 80)
    print(json.dumps(result, indent=2))
    print("=" * 80 + "\n")

    # Also write to file for backend to read
    from pathlib import Path

    tests_dir = Path(__file__).parent.parent
    results_dir = tests_dir / "results"
    results_dir.mkdir(exist_ok=True)

    report_file = results_dir / "copilot_last_report.json"
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"✓ Test report saved to: {report_file}\n")

    # Exit with appropriate code
    if args.status == "passed" or args.status == "skipped":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
