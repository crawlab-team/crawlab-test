#!/usr/bin/env python3
"""
Go Test Runner

Provides utilities for executing Go tests from Python test wrappers.
Handles test execution, environment setup, and result reporting.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, List


class GoTestRunner:
    """Runner for executing Go tests with proper environment and configuration"""
    
    def __init__(
        self,
        test_dir: Path,
        verbose: bool = True,
        coverage: bool = False,
        timeout: int = 2700,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Go test runner.
        
        Args:
            test_dir: Directory containing Go tests to run
            verbose: Enable verbose test output
            coverage: Enable coverage collection
            timeout: Test timeout in seconds (default: 45 minutes)
            logger: Optional logger instance (creates one if not provided)
        """
        self.test_dir = Path(test_dir).resolve()
        self.verbose = verbose
        self.coverage = coverage
        self.timeout = timeout
        self.logger = logger or self._setup_logging()
        
        # Check if we're in CI environment
        self.is_ci = os.getenv('CI_ENVIRONMENT') == 'true' or os.getenv('CI') == 'true'
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('GoTestRunner')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Only add handler if none exist
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def run(self, test_pattern: str = "./...", extra_flags: Optional[List[str]] = None) -> bool:
        """
        Execute Go tests.
        
        Args:
            test_pattern: Go test pattern (default: "./..." for all tests)
            extra_flags: Additional flags to pass to go test
            
        Returns:
            True if tests pass, False otherwise
        """
        self.logger.info("Starting Go tests...")
        self.logger.info(f"Test directory: {self.test_dir}")
        
        # Validate test directory
        if not self.test_dir.exists():
            self.logger.error(f"Test directory not found: {self.test_dir}")
            return False
            
        if not self.test_dir.is_dir():
            self.logger.error(f"Test path is not a directory: {self.test_dir}")
            return False
        
        # Build test command
        cmd = self._build_command(test_pattern, extra_flags)
        env = self._prepare_environment()
        
        self.logger.info(f"Executing: {' '.join(cmd)}")
        self.logger.info(f"Working directory: {self.test_dir}")
        
        try:
            # Execute tests
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env
            )
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            # Check result
            if result.returncode == 0:
                self.logger.info("✅ Go tests passed")
                return True
            else:
                self.logger.error(f"❌ Go tests failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Tests timed out after {self.timeout} seconds")
            return False
        except FileNotFoundError:
            self.logger.error("❌ 'go' command not found. Is Go installed?")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error running tests: {e}")
            return False
            
    def _build_command(self, test_pattern: str, extra_flags: Optional[List[str]] = None) -> List[str]:
        """Build the go test command with appropriate flags"""
        cmd = ["go", "test"]
        
        # Add verbose flag
        if self.verbose:
            cmd.append("-v")
        
        # Add coverage flags
        if self.coverage:
            cmd.extend([
                "-coverprofile=coverage.out",
                "-covermode=atomic"
            ])
        
        # Add timeout
        cmd.append(f"-timeout={self.timeout}s")
        
        # Add extra flags if provided
        if extra_flags:
            cmd.extend(extra_flags)
        
        # Add test pattern
        cmd.append(test_pattern)
        
        return cmd
        
    def _prepare_environment(self) -> Dict[str, str]:
        """Prepare environment variables for test execution"""
        env = os.environ.copy()
        
        # Set test mode
        env['GO_TEST_MODE'] = 'integration'
        
        # Add CI-specific environment variables
        if self.is_ci:
            env['CI'] = 'true'
            env['CI_ENVIRONMENT'] = 'true'
        
        return env


def run_go_tests(
    test_dir: Path,
    verbose: bool = True,
    coverage: bool = False,
    timeout: int = 2700,
    test_pattern: str = "./...",
    logger: Optional[logging.Logger] = None
) -> bool:
    """
    Convenience function to run Go tests.
    
    Args:
        test_dir: Directory containing Go tests
        verbose: Enable verbose output
        coverage: Enable coverage collection
        timeout: Test timeout in seconds
        test_pattern: Go test pattern
        logger: Optional logger instance
        
    Returns:
        True if tests pass, False otherwise
    """
    runner = GoTestRunner(
        test_dir=test_dir,
        verbose=verbose,
        coverage=coverage,
        timeout=timeout,
        logger=logger
    )
    
    return runner.run(test_pattern=test_pattern)


def main():
    """Main entry point for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Go tests from Python')
    parser.add_argument('test_dir', type=Path,
                        help='Directory containing Go tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Enable coverage collection')
    parser.add_argument('--timeout', '-t', type=int, default=2700,
                        help='Test timeout in seconds (default: 2700)')
    parser.add_argument('--pattern', '-p', type=str, default='./...',
                        help='Go test pattern (default: ./...)')
    
    args = parser.parse_args()
    
    success = run_go_tests(
        test_dir=args.test_dir,
        verbose=args.verbose,
        coverage=args.coverage,
        timeout=args.timeout,
        test_pattern=args.pattern
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
