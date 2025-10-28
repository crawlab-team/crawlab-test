#!/usr/bin/env python3
"""
Automation harness for TC-DEP-001 - Dependencies Installation Robustness.

This script exercises core dependency installation scenarios directly inside a
Crawlab worker container to validate that the dependency subsystem is
functioning. It is intentionally lightweight so it can run in CI environments
without consuming excessive resources while still covering the most critical
behaviours described in the spec.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Ensure tests directory is importable regardless of working directory
TESTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from helpers.infrastructure.docker_utils import docker_utils  # noqa: E402
from helpers.infrastructure.utils import format_duration, setup_logging  # noqa: E402


@dataclass
class StepResult:
    name: str
    success: bool
    message: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class DependencyInstallationRobustnessTest:
    """Implements the key automated checks for TC-DEP-001."""

    def __init__(self, worker_hint: Optional[str] = None, keep_env: bool = False):
        if not docker_utils.is_available():
            raise RuntimeError("Docker is not available; cannot execute dependency tests")

        self.logger = setup_logging("INFO")
        self.worker_container = self._select_worker_container(worker_hint)
        self.keep_env = keep_env
        self.created_paths: List[str] = []
        self.step_results: List[StepResult] = []
        self.start_time = time.time()
        self.logger.info("Selected worker container: %s", self.worker_container)

    def _select_worker_container(self, worker_hint: Optional[str]) -> str:
        containers = docker_utils.find_crawlab_containers()
        if not containers:
            raise RuntimeError("No Crawlab containers detected; ensure the stack is running")

        # Normalise names and attempt to match worker containers first
        def normalise(name: str) -> str:
            return name.lstrip('/')

        worker_hint_norm = normalise(worker_hint) if worker_hint else None
        worker_candidates = []
        for container in containers:
            name = normalise(container.get('Names', ''))
            if not name:
                continue
            if worker_hint_norm and worker_hint_norm in name:
                return name
            if 'worker' in name.lower():
                worker_candidates.append(name)

        if worker_candidates:
            return worker_candidates[0]

        # Fall back to the first container if no obvious worker was found
        return normalise(containers[0].get('Names', ''))

    def _exec(self, command: List[str], timeout: int = 90, check: bool = False) -> subprocess.CompletedProcess:
        cmd = ['docker', 'exec', self.worker_container] + command
        self.logger.debug("Executing: %s", ' '.join(cmd))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            message = f"Command timed out after {timeout}s: {' '.join(command)}"
            self.logger.error(message)
            raise RuntimeError(message) from exc

        if check and result.returncode != 0:
            self.logger.error("Command failed (%s): %s", result.returncode, result.stderr.strip())
            raise RuntimeError(result.stderr.strip() or 'Command failed')

        return result

    def _record_step(self, name: str, success: bool, message: str,
                     stdout: Optional[str] = None, stderr: Optional[str] = None) -> bool:
        stdout_trimmed = (stdout or '').strip() or None
        stderr_trimmed = (stderr or '').strip() or None
        self.step_results.append(StepResult(name, success, message, stdout_trimmed, stderr_trimmed))
        if success:
            self.logger.info("✓ %s: %s", name, message)
        else:
            self.logger.error("✗ %s: %s", name, message)
            if stderr_trimmed:
                self.logger.error("    stderr: %s", stderr_trimmed)
        return success

    def _create_virtualenv(self, path: str) -> None:
        # Remove existing env if present to guarantee clean state
        self._exec(['rm', '-rf', path], timeout=60)
        self._exec(['python3', '-m', 'venv', path], timeout=120, check=True)
        self.created_paths.append(path)

    def _pip(self, venv_path: str, args: List[str], timeout: int = 120,
             check: bool = False) -> subprocess.CompletedProcess:
        pip_path = f"{venv_path}/bin/pip"
        cmd = [
            pip_path,
            'install',
            '--disable-pip-version-check',
            '--no-input',
            '--timeout',
            '60',
        ] + args
        return self._exec(cmd, timeout=timeout, check=check)

    def _python(self, venv_path: str, args: List[str], timeout: int = 60, check: bool = False) -> subprocess.CompletedProcess:
        python_path = f"{venv_path}/bin/python"
        cmd = [python_path] + args
        return self._exec(cmd, timeout=timeout, check=check)

    def step_verify_package_managers(self) -> bool:
        name = "verify_package_managers"
        commands = [
            ("python3 -m pip --version", ['python3', '-m', 'pip', '--version']),
            ("pip --version", ['pip', '--version']),
            ("npm --version", ['npm', '--version']),
        ]
        messages = []
        success = True

        for label, cmd in commands:
            result = self._exec(cmd, timeout=30)
            if result.returncode == 0:
                snippet = result.stdout.strip() or result.stderr.strip()
                messages.append(f"{label}: {snippet}")
            else:
                # npm may be optional on some images; treat as warning not failure
                if 'npm' in label.lower():
                    messages.append(f"{label}: unavailable ({result.stderr.strip() or 'command failed'})")
                else:
                    success = False
                    messages.append(f"{label}: failed ({result.stderr.strip() or 'no output'})")

        return self._record_step(name, success, '; '.join(messages))

    def step_normal_installation(self) -> bool:
        name = "normal_installation_flow"
        venv = '/tmp/dep_robustness_env'
        try:
            self._create_virtualenv(venv)
            install = self._pip(venv, ['requests==2.28.0', 'beautifulsoup4==4.11.1'], timeout=150, check=True)
            verification = self._python(
                venv,
                ['-c', "import requests, bs4; print(requests.__version__)"],
                timeout=30,
                check=True,
            )
            message = f"Installed requests==2.28.0 & beautifulsoup4==4.11.1 (requests version {verification.stdout.strip()})"
            return self._record_step(name, True, message, stdout=install.stdout)
        except Exception as exc:
            return self._record_step(name, False, f"Normal installation failed: {exc}")

    def step_conflicting_dependencies(self) -> bool:
        name = "conflicting_dependencies"
        venv = '/tmp/dep_conflict_env'
        try:
            self._create_virtualenv(venv)
            self._pip(venv, ['django==3.2'], timeout=180, check=True)
            conflict = self._exec(
                [
                    f"{venv}/bin/pip",
                    'install',
                    '--disable-pip-version-check',
                    '--no-input',
                    '--timeout',
                    '60',
                    'django==3.2',
                    'django==4.1',
                ],
                timeout=180,
            )
            if conflict.returncode == 0:
                return self._record_step(name, False, "Expected version conflict but pip succeeded", stdout=conflict.stdout)
            message = conflict.stderr.strip() or conflict.stdout.strip()
            verification = self._exec([f"{venv}/bin/pip", 'show', 'django'], timeout=60)
            current_version = "unknown"
            for line in verification.stdout.splitlines():
                if line.lower().startswith('version:'):
                    current_version = line.split(':', 1)[1].strip()
                    break
            return self._record_step(
                name,
                True,
                f"Conflict detected as expected (active version {current_version})",
                stderr=message,
            )
        except Exception as exc:
            return self._record_step(name, False, f"Conflict scenario failed: {exc}")

    def step_isolation_between_envs(self) -> bool:
        name = "package_isolation"
        env_a = '/tmp/dep_iso_env_a'
        env_b = '/tmp/dep_iso_env_b'
        try:
            self._create_virtualenv(env_a)
            self._create_virtualenv(env_b)
            self._pip(env_a, ['requests==2.28.0'], timeout=150, check=True)
            self._pip(env_b, ['requests==2.25.0'], timeout=150, check=True)
            check_a = self._python(
                env_a,
                ['-c', "import importlib.metadata; print(importlib.metadata.version('requests'))"],
                timeout=30,
                check=True,
            )
            check_b = self._python(
                env_b,
                ['-c', "import importlib.metadata; print(importlib.metadata.version('requests'))"],
                timeout=30,
                check=True,
            )
            version_a = check_a.stdout.strip()
            version_b = check_b.stdout.strip()
            success = version_a == '2.28.0' and version_b == '2.25.0'
            message = f"Env A requests={version_a}, Env B requests={version_b}"
            return self._record_step(name, success, message)
        except Exception as exc:
            return self._record_step(name, False, f"Isolation check failed: {exc}")

    def step_missing_dependency_detection(self) -> bool:
        name = "missing_dependency_detection"
        try:
            result = self._exec([
                'python3',
                '-c',
                "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('nonexistent_package_12345') is None else 1)",
            ], timeout=15)
            success = result.returncode == 0
            message = "Missing dependency correctly reported" if success else "Unexpected module discovery"
            return self._record_step(name, success, message)
        except Exception as exc:
            return self._record_step(name, False, f"Missing dependency detection failed: {exc}")

    def cleanup(self) -> None:
        if self.keep_env:
            self.logger.info("Preserving virtual environments as requested")
            return
        for path in reversed(self.created_paths):
            try:
                self._exec(['rm', '-rf', path], timeout=60)
            except Exception as exc:
                self.logger.warning("Failed to remove %s: %s", path, exc)

    def run(self) -> bool:
        overall_success = True
        overall_success &= self.step_verify_package_managers()
        if not overall_success:
            self.logger.error("Aborting remaining steps due to prerequisite failure")
        else:
            overall_success &= self.step_normal_installation()
            overall_success &= self.step_conflicting_dependencies()
            overall_success &= self.step_isolation_between_envs()
            overall_success &= self.step_missing_dependency_detection()
        self.cleanup()
        return overall_success

    def summary(self) -> str:
        duration = format_duration(time.time() - self.start_time)
        lines = [
            "=" * 60,
            "DEPENDENCY INSTALLATION ROBUSTNESS SUMMARY",
            "=" * 60,
            f"Worker Container: {self.worker_container}",
            f"Duration: {duration}",
            "",
            "Step Results:",
        ]
        for step in self.step_results:
            icon = "✅" if step.success else "❌"
            lines.append(f"  {icon} {step.name}: {step.message}")
            if step.stdout:
                lines.append(f"      stdout: {step.stdout}")
            if step.stderr:
                lines.append(f"      stderr: {step.stderr}")
        lines.append("=" * 60)
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dependency installation robustness test harness")
    parser.add_argument("--worker", help="Specific worker container name to target")
    parser.add_argument("--keep-env", action="store_true", help="Preserve temporary virtualenvs for debugging")
    parser.add_argument("--ci", action="store_true", help="Running in CI environment (ignored, for compatibility)")
    args = parser.parse_args()

    try:
        test = DependencyInstallationRobustnessTest(worker_hint=args.worker, keep_env=args.keep_env)
        success = test.run()
        print("\n" + test.summary())
        sys.exit(0 if success else 1)
    except Exception as exc:  # pragma: no cover - defensive guard for CI visibility
        logging.basicConfig(level=logging.ERROR)
        logging.error("Dependency installation robustness test failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
