"""
Copilot Backend

This backend executes test specifications using GitHub Copilot CLI.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .base import TestBackend


class CopilotBackend(TestBackend):
    """Backend for executing tests via GitHub Copilot CLI"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize CopilotBackend

        Args:
            base_dir: Base directory for tests (repo root)
        """
        if base_dir is None:
            # Check if current working directory has specs/ directory
            cwd = Path.cwd()
            if (cwd / "specs").exists():
                base_dir = cwd
            else:
                # Fall back to calculating from package location (development mode)
                # Package is at /repo/crawlab_test, so repo root is one level up
                package_dir = Path(__file__).parent.parent
                base_dir = package_dir.parent

        self.base_dir = Path(base_dir)
        # Copilot works from repo root
        self.repo_root = self.base_dir

    def get_name(self) -> str:
        """Get backend name"""
        return "copilot"

    def get_description(self) -> str:
        """Get backend description"""
        return "GitHub Copilot CLI execution backend"

    def check_prerequisites(self) -> bool:
        """Check if Copilot CLI is available and authenticated"""
        # Check for copilot command
        if not shutil.which("copilot"):
            print("Error: 'copilot' command not found in PATH")
            print("Install it with: npm install -g @github/copilot")
            return False

        # Check for authentication
        gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        gh_authenticated = False
        is_ci = os.getenv("CI") or os.getenv("GITHUB_ACTIONS")

        if shutil.which("gh"):
            try:
                result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=5)
                gh_authenticated = result.returncode == 0
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass

        if not gh_token and not gh_authenticated:
            if is_ci:
                print("Error: GitHub authentication required in CI environment")
                print("Set GITHUB_TOKEN secret in GitHub Actions workflow")
                return False
            else:
                print("Warning: GitHub authentication not detected")
                print("Copilot may require authentication for full functionality")

        return True

    def _setup_mcp_config(self) -> None:
        """
        Setup MCP configuration in ~/.copilot/mcp-config.json

        This copies the mcp-config.json from tests directory to the global
        Copilot config directory where Copilot CLI automatically looks for it.
        """
        import json

        source_config = self.base_dir / "mcp-config.json"
        home_dir = Path.home()
        copilot_dir = home_dir / ".copilot"
        target_config = copilot_dir / "mcp-config.json"

        # Ensure ~/.copilot directory exists
        copilot_dir.mkdir(parents=True, exist_ok=True)

        if source_config.exists():
            try:
                # Read source config
                with open(source_config) as f:
                    config_data = json.load(f)

                # Write to target location
                with open(target_config, "w") as f:
                    json.dump(config_data, f, indent=2)

                print(f"✓ MCP config installed to: {target_config}")
            except Exception as e:
                print(f"⚠ Warning: Could not setup MCP config: {e}")
        else:
            print(f"⚠ Warning: Source MCP config not found at {source_config}")

    def execute(self, spec_path: Path, config: Dict) -> Dict:
        """
        Execute test using Copilot CLI

        Args:
            spec_path: Path to test specification
            config: Configuration dictionary

        Returns:
            Result dictionary
        """
        result = {
            "backend": self.get_name(),
            "spec_path": str(spec_path),
            "start_time": datetime.now().isoformat(),
            "status": "unknown",
        }

        # Check authentication in CI
        if config.get("is_ci", False):
            gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
            if not gh_token:
                result["status"] = "skipped"
                result["error"] = "GitHub authentication required in CI"
                return result

        # Setup MCP configuration for Playwright support in ~/.copilot/mcp-config.json
        self._setup_mcp_config()

        print(f"Executing via Copilot CLI: {spec_path}")

        # Load shared UI testing guide if this is a UI test
        shared_guide_content = ""
        if spec_path.parts and len(spec_path.parts) > 0 and "ui" in spec_path.parts:
            shared_guide = self.base_dir / "specs" / "ui" / "_shared" / "copilot-testing-guide.md"
            if shared_guide.exists():
                try:
                    with open(shared_guide) as f:
                        shared_guide_content = f.read()
                    print("✓ Loaded shared UI testing guide")
                except Exception as e:
                    print(f"⚠ Warning: Could not load shared guide: {e}")

        # Build prompt
        try:
            spec_rel = spec_path.relative_to(self.repo_root)
        except ValueError:
            spec_rel = spec_path

        # Include shared guide in prompt if available
        guide_instruction = ""
        if shared_guide_content:
            guide_instruction = f"""
IMPORTANT: Before executing the test, review these UI testing guidelines:

{shared_guide_content}

Pay special attention to:
- Element Plus dropdown interaction (use click-based approach, NOT .selectOption())
- High-level instructions without hard-coded selectors
- Snapshot-based discovery before interactions
- Semantic element finding

"""

        prompt = f"""{guide_instruction}Execute the test specification at {spec_rel}.

Follow all steps including prerequisites, setup, execution, validation, and cleanup.
After each major step, show validation results.

IMPORTANT: At the end of execution, you MUST report results using the reporting tool:

./tests/tools/report_test_result.py \\
  --status passed|failed|skipped \\
  --total-steps <number> \\
  --completed-steps <number> \\
  --failed-steps <number> \\
  [--reason "explanation if failed/skipped"] \\
  [--duration "time taken"] \\
  [--step-details '<json_array_of_step_results>'] \\
  [--issues '<json_array_of_issues>']

Examples:
  # All tests passed with step details
  ./tests/tools/report_test_result.py --status passed --total-steps 6 --completed-steps 6 --duration "3m 45s" \\
    --step-details '[{{"step": 1, "name": "Login", "status": "passed"}}, {{"step": 2, "name": "Navigate", "status": "passed"}}]'

  # Test failed at step 3
  ./tests/tools/report_test_result.py --status failed --total-steps 6 --completed-steps 2 --failed-steps 1 \\
    --reason "Step 3: Spider creation failed - form validation error" \\
    --issues '[{{"type": "error", "message": "Form field validation failed", "step": 3}}]'

  # Test skipped
  ./tests/tools/report_test_result.py --status skipped --reason "Prerequisites not met: Browser not available"

The reporting tool will output JSON that the test framework will parse.

EXECUTION GUIDELINES:
- Print clear step headers (e.g., "Step 1: Login to system")
- Use status indicators: ✓ for success, ✗ for failure, ⚠ for warnings
- Log important actions and their outcomes
- Capture and report any errors or issues encountered
- Provide detailed failure reasons when tests don't pass
- Report actual vs expected results for validation failures"""

        # Build command
        cmd = ["copilot", "--prompt", prompt, "--no-custom-instructions"]

        # Add model if specified
        model = config.get("model")
        if model:
            cmd.extend(["--model", model])
            print(f"Using model: {model}")

        cmd.extend(
            [
                "--allow-all-tools",
                "--deny-tool",
                "shell(rm -rf)",
                "--deny-tool",
                "shell(git push)",
            ]
        )

        # Get timeout
        timeout_minutes = config.get("timeout_minutes", 30)
        timeout_seconds = timeout_minutes * 60

        # Execute
        try:
            # Change to repo root for execution
            original_dir = os.getcwd()
            os.chdir(self.repo_root)

            print("\n" + "=" * 80)
            print("COPILOT EXECUTION OUTPUT:")
            print("=" * 80 + "\n")

            # Capture output for detailed logging
            process = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_seconds)

            # Store raw output
            stdout = process.stdout or ""
            stderr = process.stderr or ""

            # Print output for real-time visibility
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)

            print("\n" + "=" * 80)
            print("END COPILOT OUTPUT")
            print("=" * 80 + "\n")

            os.chdir(original_dir)

            result["exit_code"] = process.returncode
            result["stdout"] = stdout
            result["stderr"] = stderr

            # Parse execution details from output
            execution_details = self._parse_execution_details(stdout, stderr)
            if execution_details:
                result["execution_details"] = execution_details

            # Check for test execution report in a dedicated file
            report_file = self.base_dir / "results" / "copilot_last_report.json"
            if report_file.exists():
                try:
                    import json

                    with open(report_file) as f:
                        report_data = json.load(f)

                    test_report = report_data.get("test_execution_report", {})
                    if test_report.get("executed"):
                        result["status"] = test_report.get("status", "unknown")
                        result["test_report"] = test_report
                    else:
                        result["status"] = "skipped"
                        result["validation_reason"] = "Test not executed"
                except Exception as e:
                    print(f"Warning: Could not parse report file: {e}")
                    result["status"] = "passed" if process.returncode == 0 else "failed"
            else:
                # Fallback: rely on exit code
                print("Note: No test execution report found. Relying on exit code.")
                result["status"] = "passed" if process.returncode == 0 else "failed"

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = f"Execution timed out after {timeout_seconds} seconds"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        result["end_time"] = datetime.now().isoformat()
        return result

    def _parse_execution_details(self, stdout: str, stderr: str) -> dict:
        """
        Parse execution details from Copilot output

        Args:
            stdout: Standard output from Copilot
            stderr: Standard error from Copilot

        Returns:
            Dictionary with execution details including steps, issues, logs
        """
        import re

        details = {"steps": [], "issues": [], "logs": []}

        combined_output = stdout + "\n" + stderr

        # Parse step execution patterns
        # Look for common step indicators: "Step 1:", "Step 2:", "✓ Step", "✗ Step", etc.
        step_patterns = [
            r"Step\s+(\d+):\s*(.+?)(?=\n|$)",
            r"(✓|✗|❌|✅)\s*Step\s+(\d+):\s*(.+?)(?=\n|$)",
            r"(\d+)\)\s+(.+?)(?:\.\.\.|:)\s*(passed|failed|completed|skipped)",
        ]

        for pattern in step_patterns:
            for match in re.finditer(pattern, combined_output, re.MULTILINE | re.IGNORECASE):
                step_info = {"step": match.group(0), "raw": match.group(0)}

                # Try to extract status
                step_text = match.group(0).lower()
                if any(x in step_text for x in ["✓", "✅", "passed", "completed"]):
                    step_info["status"] = "passed"
                elif any(x in step_text for x in ["✗", "❌", "failed", "error"]):
                    step_info["status"] = "failed"
                elif "skipped" in step_text:
                    step_info["status"] = "skipped"
                else:
                    step_info["status"] = "unknown"

                details["steps"].append(step_info)

        # Parse error/issue patterns
        error_patterns = [
            r"Error:\s*(.+?)(?=\n|$)",
            r"Exception:\s*(.+?)(?=\n|$)",
            r"Failed:\s*(.+?)(?=\n|$)",
            r"Warning:\s*(.+?)(?=\n|$)",
        ]

        for pattern in error_patterns:
            for match in re.finditer(pattern, combined_output, re.MULTILINE):
                issue = {"type": match.group(0).split(":")[0].lower(), "message": match.group(1).strip()}
                details["issues"].append(issue)

        # Extract log entries (lines with timestamps, INFO, DEBUG, etc.)
        log_pattern = r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|INFO|DEBUG|WARNING|ERROR).*?(?=\n|$)"
        for match in re.finditer(log_pattern, combined_output, re.MULTILINE):
            log_entry = match.group(0).strip()
            if log_entry:  # Only add non-empty logs
                details["logs"].append(log_entry)

        # Limit log entries to avoid bloat (keep first 50 and last 50)
        if len(details["logs"]) > 100:
            details["logs"] = (
                details["logs"][:50] + ["... (log entries truncated for brevity) ..."] + details["logs"][-50:]
            )

        return details

    def _validate_execution(self, output: str) -> tuple[bool, str]:
        """
        Validate that tests were actually executed

        Args:
            output: Copilot output

        Returns:
            (is_valid, reason) tuple
        """
        # Look for structured result in output
        import json
        import re

        # Try to find JSON result block
        json_match = re.search(r'```json\s*(\{.*?"test_execution".*?\})\s*```', output, re.DOTALL)

        if json_match:
            try:
                result_data = json.loads(json_match.group(1))
                test_execution = result_data.get("test_execution", {})

                if test_execution.get("executed") is True:
                    return True, "Test execution confirmed"
                else:
                    reason = test_execution.get("reason", "Tests not executed")
                    return False, reason
            except json.JSONDecodeError:
                pass

        # Fallback: check for execution indicators
        indicators = [
            "test passed",
            "test completed",
            "validation passed",
            "all steps completed",
            "successfully executed",
        ]

        output_lower = output.lower()
        if any(indicator in output_lower for indicator in indicators):
            return True, "Execution indicators found"

        return False, "No execution confirmation found"
