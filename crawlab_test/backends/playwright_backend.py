"""
Playwright Backend

This backend executes UI tests using TypeScript/Playwright framework.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .base import TestBackend


class PlaywrightBackend(TestBackend):
    """Backend for executing TypeScript/Playwright UI tests"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize PlaywrightBackend

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
        # UI Playwright tests are at repo root (if they exist)
        self.ui_playwright_dir = self.base_dir / "ui-playwright"

    def get_name(self) -> str:
        """Get backend name"""
        return "playwright"

    def get_description(self) -> str:
        """Get backend description"""
        return "TypeScript/Playwright UI test execution backend"

    def check_prerequisites(self) -> bool:
        """Check if Node.js, pnpm, and Playwright are available"""
        # Check Node.js
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Node.js is not installed or not in PATH")
            return False

        # Check pnpm
        try:
            subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: pnpm is not installed or not in PATH")
            print("Install with: npm install -g pnpm")
            return False

        return True

    def supports_spec(self, spec_path: Path) -> bool:
        """Check if this is a UI test specification"""
        # Support UI category specs if ui-playwright directory exists
        try:
            category = self._get_category_from_spec_path(spec_path)
            return category == "ui" and self.ui_playwright_dir.exists()
        except:
            return False

    def execute(self, spec_path: Path, config: Dict) -> Dict:
        """
        Execute UI test using TypeScript/Playwright

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

        if not self.ui_playwright_dir.exists():
            result["status"] = "error"
            result["error"] = (
                f"UI Playwright directory not found: {self.ui_playwright_dir}. "
                "This backend requires a TypeScript/Playwright test suite."
            )
            return result

        # Find test file
        test_file = self._find_test_file(spec_path)
        if not test_file:
            result["status"] = "error"
            result["error"] = f"No TypeScript test file found for {spec_path}"
            return result

        print(f"Executing Playwright test: {test_file}")

        # Get configuration
        timeout_minutes = config.get("timeout_minutes", 15)  # UI tests typically need more time
        is_ci = config.get("is_ci", False)

        try:
            # Change to ui-playwright directory
            original_cwd = os.getcwd()
            os.chdir(self.ui_playwright_dir)

            # Install dependencies if needed
            if not self._check_dependencies():
                print("Installing dependencies...")
                self._install_dependencies()

            # Install Playwright browsers if needed
            if not self._check_browsers():
                print("Installing Playwright browsers...")
                self._install_browsers()

            # Build test command
            cmd = ["pnpm", "exec", "playwright", "test"]

            # Add test file
            cmd.append(str(test_file.relative_to(self.ui_playwright_dir)))

            # Add CI configuration
            if is_ci:
                cmd.extend(["--reporter=json"])

            # Add timeout
            timeout_ms = timeout_minutes * 60 * 1000
            cmd.extend([f"--timeout={timeout_ms}"])

            # Execute test
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_minutes * 60)

            result["command"] = " ".join(cmd)
            result["exit_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr

            # Parse results
            if process.returncode == 0:
                result["status"] = "passed"
                result["message"] = "Test passed"
            else:
                result["status"] = "failed"
                result["message"] = "Test failed"

                # Try to parse JSON output for detailed results
                if is_ci and process.stdout:
                    try:
                        playwright_results = json.loads(process.stdout)
                        result["playwright_results"] = playwright_results
                    except json.JSONDecodeError:
                        pass

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = f"Test timed out after {timeout_minutes} minutes"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            result["end_time"] = datetime.now().isoformat()

        return result

    def _get_category_from_spec_path(self, spec_path: Path) -> str:
        """Extract category from spec path"""
        parts = spec_path.parts
        if "specs" in parts:
            specs_idx = parts.index("specs")
            if len(parts) > specs_idx + 1:
                return parts[specs_idx + 1]
        return "unknown"

    def _find_test_file(self, spec_path: Path) -> Optional[Path]:
        """Find corresponding TypeScript test file for a spec"""
        # Extract test ID from spec filename
        spec_name = spec_path.stem

        # Look for test files with matching ID
        test_patterns = [f"{spec_name}.spec.ts", f"{spec_name}.test.ts", f"{spec_name}.ts"]

        for pattern in test_patterns:
            test_file = self.ui_playwright_dir / "tests" / pattern
            if test_file.exists():
                return test_file

        # Look recursively in tests directory
        tests_dir = self.ui_playwright_dir / "tests"
        if tests_dir.exists():
            for test_file in tests_dir.rglob("*.spec.ts"):
                if spec_name in test_file.stem:
                    return test_file
            for test_file in tests_dir.rglob("*.test.ts"):
                if spec_name in test_file.stem:
                    return test_file

        return None

    def _check_dependencies(self) -> bool:
        """Check if Node.js dependencies are installed"""
        package_json = self.ui_playwright_dir / "package.json"
        node_modules = self.ui_playwright_dir / "node_modules"

        return package_json.exists() and node_modules.exists()

    def _install_dependencies(self) -> None:
        """Install Node.js dependencies"""
        subprocess.run(["pnpm", "install"], check=True, cwd=self.ui_playwright_dir)

    def _check_browsers(self) -> bool:
        """Check if Playwright browsers are installed"""
        try:
            subprocess.run(
                ["pnpm", "exec", "playwright", "--version"], capture_output=True, check=True, cwd=self.ui_playwright_dir
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _install_browsers(self) -> None:
        """Install Playwright browsers"""
        subprocess.run(["pnpm", "exec", "playwright", "install", "chromium"], check=True, cwd=self.ui_playwright_dir)
