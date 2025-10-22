#!/usr/bin/env python3
"""
Wrapper script for TC-DEP-002 - Dependency Handler Network Reconnection Resilience

This script bridges the spec-based runner with the existing automation in
`dependency-reconnection-test.py` so specs executed with the generic runner
use the fully automated workflow instead of falling back to manual mode.
"""

import sys
from pathlib import Path

# Ensure helper modules are importable when executed from arbitrary working dirs
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Import the main function from dependency_reconnection_suite.py in suites directory
dependency_reconnection_module = TESTS_DIR / "helpers" / "suites" / "dependencies" / "dependency_reconnection_suite.py"
if not dependency_reconnection_module.exists():
    print(f"ERROR: dependency-reconnection-test.py not found at {dependency_reconnection_module}")
    sys.exit(1)

# Use importlib to import the module dynamically
import importlib.util
spec = importlib.util.spec_from_file_location("dependency_reconnection_test", dependency_reconnection_module)
dependency_reconnection_test = importlib.util.module_from_spec(spec)
sys.modules["dependency_reconnection_test"] = dependency_reconnection_test
spec.loader.exec_module(dependency_reconnection_test)

run_reconnection_suite = dependency_reconnection_test.main


if __name__ == "__main__":
    run_reconnection_suite()
