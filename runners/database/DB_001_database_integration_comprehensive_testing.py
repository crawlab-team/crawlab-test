#!/usr/bin/env python3
"""
Integration Test Spec Wrapper

This script acts as a bridge between the spec test framework and Go integration tests.
It's invoked by the test runner when executing INT-001 spec and runs the Go database tests.
"""

import sys
import os
from pathlib import Path

# Add tests directory to path for helper imports
tests_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(tests_dir))

from helpers.libs.go_test_runner import run_go_tests
from helpers.libs.utils import setup_logging

def main():
    """Execute database integration tests"""
    print("="*60)
    print("Database Integration Test Wrapper")
    print("="*60)
    
    # Setup logging
    logger = setup_logging("DB-001")
    
    # Calculate paths
    tests_dir = Path(__file__).resolve().parent.parent.parent
    project_root = tests_dir.parent
    database_dir = project_root / "core" / "database"
    
    logger.info(f"Project root: {project_root}")
    logger.info(f"Database test directory: {database_dir}")
    
    # Check if we're in CI environment
    is_ci = os.getenv('CI_ENVIRONMENT') == 'true' or os.getenv('CI') == 'true'
    
    # Run Go tests using helper
    success = run_go_tests(
        test_dir=database_dir,
        verbose=True,
        coverage=is_ci,  # Only collect coverage in CI
        timeout=2700,  # 45 minutes for CI (matches test matrix timeout)
        logger=logger
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
