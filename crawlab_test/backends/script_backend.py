"""
Script Backend

This backend executes test specifications using Python/Shell scripts.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .base import TestBackend


class ScriptBackend(TestBackend):
    """Backend for executing Python/Shell test scripts"""

    def __init__(self, base_dir: Optional[Path] = None, runners_dir: Optional[Path] = None):
        """
        Initialize ScriptBackend

        Args:
            base_dir: Base directory for tests (defaults to package location)
            runners_dir: Directory containing runner scripts (defaults to package's runners/)
        """
        # Everything is relative to package location - simple and reliable
        # From crawlab_test/backends/script_backend.py, go up one level to crawlab_test/
        package_dir = Path(__file__).parent.parent

        # Default to package directory
        if base_dir is None:
            base_dir = package_dir

        self.base_dir = Path(base_dir)
        
        # Runners are always in the package directory
        # Allow override for subprocess context (passed from main process)
        if runners_dir is not None:
            self.runners_dir = Path(runners_dir)
        else:
            self.runners_dir = package_dir / "runners"
            
        self.helpers_dir = package_dir / "helpers"

    def get_name(self) -> str:
        """Get backend name"""
        return "script"

    def get_description(self) -> str:
        """Get backend description"""
        return "Python/Shell script execution backend"

    def check_prerequisites(self) -> bool:
        """Check if Python is available"""
        return sys.executable is not None

    def supports_spec(self, spec_path: Path) -> bool:
        """Check if a runner script exists for this spec"""
        runner_script = self._find_runner_script(spec_path)
        return runner_script is not None

    def execute(self, spec_path: Path, config: Dict) -> Dict:
        """
        Execute test using runner script

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

        # Find runner script
        runner_script = self._find_runner_script(spec_path)

        if not runner_script:
            result["status"] = "error"
            result["error"] = f"No runner script found for {spec_path}"
            return result

        print(f"Executing script: {runner_script}")

        # Get configuration
        timeout_minutes = config.get("timeout_minutes", 30)
        retry_count = config.get("retry_count", 1)
        is_ci = config.get("is_ci", False)

        # Execute with retries
        last_error = None
        for attempt in range(1, retry_count + 1):
            try:
                if attempt > 1:
                    print(f"Retry attempt {attempt}/{retry_count} for {runner_script}")

                # Build command
                timeout_seconds = timeout_minutes * 60
                cmd = [sys.executable, str(runner_script)]

                # Add spec file if script supports it
                if "--spec" in str(runner_script) or "spec" in runner_script.stem:
                    cmd.extend(["--spec", str(spec_path)])

                # Add CI flag if in CI environment
                if is_ci:
                    cmd.extend(["--ci"])

                # Execute
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    env={**os.environ, "CI_ENVIRONMENT": str(is_ci)},
                )

                result["status"] = "passed" if process.returncode == 0 else "failed"
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                result["exit_code"] = process.returncode
                result["attempt"] = attempt

                if result["status"] == "passed":
                    break
                else:
                    last_error = f"Script failed with exit code {process.returncode}"
                    if attempt < retry_count:
                        print(f"Attempt {attempt} failed, retrying...")
                        time.sleep(2)

            except subprocess.TimeoutExpired:
                result["error"] = f"Script execution timed out after {timeout_seconds} seconds"
                result["status"] = "timeout"
                last_error = result["error"]
                break
            except Exception as e:
                error_msg = f"Script execution failed: {e}"
                result["error"] = error_msg
                result["status"] = "error"
                last_error = error_msg
                if attempt < retry_count:
                    print(f"Attempt {attempt} failed with error: {e}, retrying...")
                    time.sleep(2)

        # If all retries failed, use the last error
        if result["status"] not in ["passed", "timeout"] and last_error:
            result["error"] = last_error
            print(f"All {retry_count} attempts failed: {last_error}")

        result["end_time"] = datetime.now().isoformat()
        return result

    def _find_runner_script(self, spec_path: Path) -> Optional[Path]:
        """
        Find runner script for a specification

        Only matches by spec ID (e.g., API-001), not the full filename.
        This allows flexible naming of runner scripts as long as they include the spec ID.

        Args:
            spec_path: Path to spec file

        Returns:
            Path to runner script or None
        """
        import re

        # Get category from spec path
        try:
            parts = spec_path.parts
            specs_index = parts.index("specs")
            category = parts[specs_index + 1] if specs_index + 1 < len(parts) else spec_path.parent.name
        except (ValueError, IndexError):
            category = spec_path.parent.name

        # Look in runners/ directory (new structure)
        runner_dir = self.runners_dir / category

        if not runner_dir.exists():
            # Fall back to helpers/ directory (old structure)
            runner_dir = self.helpers_dir / category

        if not runner_dir.exists():
            return None

        # Extract spec ID from filename (e.g., API-001, UI-002, CLS-001)
        spec_id_match = re.search(r"([A-Z]+)-(\d+)", spec_path.stem)
        if not spec_id_match:
            return None

        spec_id = spec_id_match.group(0)  # e.g., "API-001"
        spec_id_underscore = spec_id.replace("-", "_")  # e.g., "API_001"

        # Look for runner scripts that start with the spec ID (with underscore)
        # e.g., API_001_*.py matches the spec API-001-*.md
        test_scripts = list(runner_dir.glob(f"{spec_id_underscore}*.py"))

        if test_scripts:
            return test_scripts[0]

        # Try with hyphen format (less common but possible)
        test_scripts = list(runner_dir.glob(f"{spec_id}*.py"))

        if test_scripts:
            return test_scripts[0]

        return None
