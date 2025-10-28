#!/usr/bin/env python3
"""
Common utilities and helper functions for testing
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Add the helpers directory to Python path for imports


def setup_logging(level: Union[str, int] = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration"""
    if isinstance(level, int):
        logging_level = level
    elif isinstance(level, str):
        logging_level = getattr(logging, level.upper(), logging.INFO)
    else:
        logging_level = logging.INFO

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config = {
        # MongoDB settings
        "mongodb": {
            "uri": os.getenv("CRAWLAB_MONGO_URI", "mongodb://localhost:27017"),
            "database": os.getenv("CRAWLAB_MONGO_DATABASE", "crawlab_test"),
        },
        # API settings
        "api": {
            "base_url": os.getenv("CRAWLAB_MASTER_URL", "http://localhost:8080"),
            "token": os.getenv("CRAWLAB_API_TOKEN"),
        },
        # Test settings
        "test": {
            "timeout": int(os.getenv("TEST_TIMEOUT", "300")),
            "poll_interval": float(os.getenv("TEST_POLL_INTERVAL", "2.0")),
            "cleanup_on_exit": os.getenv("TEST_CLEANUP_ON_EXIT", "true").lower() == "true",
        },
        # Reconciliation settings
        "reconciliation": {
            "cycle_interval": int(os.getenv("RECONCILIATION_CYCLE_INTERVAL", "30")),
            "max_wait_time": int(os.getenv("RECONCILIATION_MAX_WAIT_TIME", "90")),
        },
    }

    # Load from config file if provided
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file) as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logging.warning(f"Failed to load config file {config_file}: {e}")

    return config


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {secs:.1f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def wait_with_timeout(
    condition_func, timeout: int = 60, poll_interval: float = 1.0, description: str = "condition"
) -> bool:
    """Wait for a condition to be true with timeout"""
    start_time = time.time()
    logger = logging.getLogger("wait_with_timeout")

    while time.time() - start_time < timeout:
        try:
            if condition_func():
                elapsed = time.time() - start_time
                logger.info(f"{description} satisfied after {format_duration(elapsed)}")
                return True
        except Exception as e:
            logger.warning(f"Error checking {description}: {e}")

        time.sleep(poll_interval)

    elapsed = time.time() - start_time
    logger.error(f"Timeout waiting for {description} after {format_duration(elapsed)}")
    return False


def wait_for_condition(condition_func, timeout: int = 60, check_interval: float = 1.0) -> bool:
    """Wait for a condition to be true with timeout

    Args:
        condition_func: A callable that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        True if condition was met, False if timeout occurred
    """
    start_time = time.time()
    logger = logging.getLogger("wait_for_condition")

    while time.time() - start_time < timeout:
        try:
            if condition_func():
                elapsed = time.time() - start_time
                logger.debug(f"Condition satisfied after {format_duration(elapsed)}")
                return True
        except Exception as e:
            logger.debug(f"Error checking condition: {e}")

        time.sleep(check_interval)

    elapsed = time.time() - start_time
    logger.debug(f"Timeout waiting for condition after {format_duration(elapsed)}")
    return False


def validate_test_environment() -> List[str]:
    """Validate that the test environment is properly set up"""
    issues = []

    # Check MongoDB connection
    try:
        from .database import DatabaseHelper

        db = DatabaseHelper()
        db.connect()
        db.disconnect()
    except Exception as e:
        issues.append(f"MongoDB connection failed: {e}")

    # Check API connectivity
    try:
        from .api_client import CrawlabAPIClient

        api = CrawlabAPIClient()
        if not api.ping():
            issues.append("Crawlab API is not accessible")
    except Exception as e:
        issues.append(f"API client setup failed: {e}")

    # Check required environment variables
    required_vars = []
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        issues.append(f"Missing environment variables: {missing_vars}")

    return issues


def create_test_summary(test_results: Dict[str, Any]) -> str:
    """Create a formatted test summary"""
    summary_lines = [
        "=" * 60,
        "TASK RECONCILIATION TEST SUMMARY",
        "=" * 60,
        f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Duration: {format_duration(test_results.get('total_duration', 0))}",
        "",
        "Results by Step:",
    ]

    for step_name, step_result in test_results.get("steps", {}).items():
        status = "✓ PASS" if step_result.get("success", False) else "✗ FAIL"
        duration = format_duration(step_result.get("duration", 0))
        summary_lines.append(f"  {status} {step_name} ({duration})")

        if not step_result.get("success", False):
            error = step_result.get("error", "Unknown error")
            summary_lines.append(f"      Error: {error}")

    summary_lines.extend(
        [
            "",
            f"Success Rate: {test_results.get('success_rate', 0):.1f}%",
            f"Total Steps: {test_results.get('total_steps', 0)}",
            f"Passed: {test_results.get('passed_steps', 0)}",
            f"Failed: {test_results.get('failed_steps', 0)}",
            "=" * 60,
        ]
    )

    return "\n".join(summary_lines)


class TestMetrics:
    """Track test execution metrics"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.steps = {}
        self.current_step = None

    def start_test(self, test_name: str):
        """Start tracking a test"""
        self.test_name = test_name
        self.start_time = time.time()
        logging.info(f"Starting test: {test_name}")

    def start_step(self, step_name: str):
        """Start tracking a test step"""
        if self.current_step:
            self.end_step()

        self.current_step = step_name
        self.steps[step_name] = {"start_time": time.time(), "success": False, "error": None, "duration": 0}
        logging.info(f"Starting step: {step_name}")

    def end_step(self, success: bool = True, error: Optional[str] = None):
        """End tracking current test step"""
        if not self.current_step:
            return

        step = self.steps[self.current_step]
        step["end_time"] = time.time()
        step["duration"] = step["end_time"] - step["start_time"]
        step["success"] = success
        step["error"] = error

        status = "✓" if success else "✗"
        duration = format_duration(step["duration"])
        logging.info(f"{status} Completed step: {self.current_step} ({duration})")

        if error:
            logging.error(f"Step error: {error}")

        self.current_step = None

    def end_test(self):
        """End tracking the test"""
        if self.current_step:
            self.end_step()

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time if self.start_time else 0

        # Calculate summary statistics
        total_steps = len(self.steps)
        passed_steps = sum(1 for step in self.steps.values() if step["success"])
        failed_steps = total_steps - passed_steps
        success_rate = (passed_steps / total_steps * 100) if total_steps > 0 else 0

        results = {
            "test_name": getattr(self, "test_name", "Unknown"),
            "total_duration": total_duration,
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "success_rate": success_rate,
            "steps": self.steps,
        }

        logging.info(f"Test completed: {format_duration(total_duration)}")
        logging.info(f"Success rate: {success_rate:.1f}% ({passed_steps}/{total_steps})")

        return results
