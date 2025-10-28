"""
Base classes for UI testing.

This module provides base classes and utilities for building deterministic UI tests.
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UITestBase(ABC):
    """Base class for all UI tests.

    Provides common functionality like logging, screenshot capture,
    test state management, and cleanup.
    """

    def __init__(self, test_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the test base.

        Args:
            test_id: Unique identifier for this test
            config: Optional configuration dictionary
        """
        self.test_id = test_id
        self.config = config or self._load_default_config()
        self.logger = self._setup_logger()

        # Test state
        self.browser = None
        self.page = None
        self.test_results: List[Dict[str, Any]] = []
        self.test_start_time: Optional[datetime] = None
        self.screenshots: List[str] = []  # Track screenshot filenames

        # Ensure screenshots directory exists
        self.screenshots_dir = Path(self.config.get("screenshots_dir", "tests/results/screenshots"))
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "browser": {
                "headless": os.getenv("HEADLESS", "true").lower() == "true",
                "viewport": {"width": 1920, "height": 1080},
            },
            "timeouts": {"default": 30000, "navigation": 60000, "action": 10000},
            "screenshots": {"enabled": True, "on_failure": True, "on_step": True},
            "base_url": os.getenv("CRAWLAB_URL", "http://localhost:8080"),
        }

    def _setup_logger(self) -> logging.Logger:
        """Set up logger for this test."""
        logger = logging.getLogger(f"ui_test.{self.test_id}")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(f"%(asctime)s - {self.test_id} - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        log_dir = Path(__file__).parent.parent.parent / "results" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{self.test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    async def setup(self):
        """Set up test environment.

        Override this method to add custom setup steps.
        """
        self.logger.info(f"Setting up test {self.test_id}")
        self.test_start_time = datetime.now()

    async def teardown(self):
        """Clean up test environment.

        Override this method to add custom cleanup steps.
        """
        self.logger.info(f"Tearing down test {self.test_id}")
        if self.browser:
            await self.close_browser()

    async def take_screenshot(self, name: str) -> Optional[Path]:
        """Take a screenshot of the current page.

        Args:
            name: Name for the screenshot file (without extension)

        Returns:
            Path to the saved screenshot, or None if failed
        """
        try:
            if not self.page:
                self.logger.warning("Cannot take screenshot: no page available")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.test_id}_{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename

            await self.page.screenshot(path=str(filepath))
            self.logger.info(f"Screenshot saved: {filename}")

            # Track screenshot
            self.screenshots.append(filename)

            return filepath

        except Exception as e:
            self.logger.error(f"Failed to take screenshot '{name}': {e}")
            return None

    def record_step_result(self, step_name: str, success: bool, message: str = "", duration: float = 0):
        """Record the result of a test step.

        Args:
            step_name: Name of the test step
            success: Whether the step succeeded
            message: Optional message about the step
            duration: Duration of the step in seconds
        """
        result = {
            "step": step_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✓" if success else "✗"
        self.logger.info(f"{status} {step_name}: {message}")

    def get_test_summary(self) -> Dict[str, Any]:
        """Get a summary of test results.

        Returns:
            Dictionary containing test summary
        """
        total_steps = len(self.test_results)
        passed_steps = sum(1 for r in self.test_results if r["success"])
        failed_steps = total_steps - passed_steps

        duration = 0
        if self.test_start_time:
            duration = (datetime.now() - self.test_start_time).total_seconds()

        return {
            "test_id": self.test_id,
            "status": "passed" if failed_steps == 0 else "failed",
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "duration": duration,
            "results": self.test_results,
            "screenshots": self.screenshots,  # Include screenshot list
        }

    async def close_browser(self):
        """Close the browser and clean up resources."""
        if self.browser:
            try:
                await self.browser.close()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.browser = None
                self.page = None

    @abstractmethod
    async def run(self):
        """Execute the test.

        This method must be implemented by subclasses.
        """
        pass

    async def execute(self) -> Dict[str, Any]:
        """Execute the complete test with setup and teardown.

        Returns:
            Dictionary containing test results
        """
        try:
            await self.setup()
            await self.run()
            return self.get_test_summary()
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}", exc_info=True)
            self.record_step_result("execution", False, str(e))
            return self.get_test_summary()
        finally:
            await self.teardown()


class UITestResult:
    """Container for UI test results."""

    def __init__(self, test_id: str):
        self.test_id = test_id
        self.status = "pending"
        self.steps: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.screenshots: List[Path] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def add_step(self, step_name: str, success: bool, message: str = ""):
        """Add a step result."""
        self.steps.append(
            {"name": step_name, "success": success, "message": message, "timestamp": datetime.now().isoformat()}
        )

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)

    def add_screenshot(self, screenshot_path: Path):
        """Add a screenshot path."""
        self.screenshots.append(screenshot_path)

    def mark_complete(self, status: str):
        """Mark the test as complete with given status."""
        self.status = status
        self.end_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        duration = 0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            "test_id": self.test_id,
            "status": self.status,
            "duration": duration,
            "steps": self.steps,
            "errors": self.errors,
            "warnings": self.warnings,
            "screenshots": [str(p) for p in self.screenshots],
        }
