#!/usr/bin/env python3
"""
Runner script for CLS-004 - Dependency Handler Network Reconnection Resilience

This script executes the dependency handler reconnection test suite,
validating that Crawlab's dependency handler can recover gracefully from
network disconnections and maintain dependency synchronization functionality.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from crawlab_test.helpers.suites.dependencies.dependency_reconnection_suite import main

if __name__ == "__main__":
    # Check for CI environment
    is_ci = os.getenv("CI", "").lower() == "true"

    # Set default master URL based on environment
    if is_ci:
        # In CI, the master URL might be different
        default_master_url = os.getenv("CRAWLAB_MASTER_URL", "http://localhost:8080")
    else:
        default_master_url = "http://localhost:8080"

    # Check if --master-url argument is provided, otherwise add it
    if "--master-url" not in sys.argv and not any(arg.startswith("http") for arg in sys.argv):
        sys.argv.extend(["--master-url", default_master_url])

    # Run the main test
    sys.exit(main())
