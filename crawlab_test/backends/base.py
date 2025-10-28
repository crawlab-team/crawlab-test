"""
Base Backend Interface

This module defines the abstract interface that all test backends must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class TestBackend(ABC):
    """Abstract base class for test execution backends"""

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this backend

        Returns:
            Backend name (e.g., 'script', 'copilot', 'playwright')
        """
        pass

    @abstractmethod
    def check_prerequisites(self) -> bool:
        """
        Check if this backend can run (all dependencies available)

        Returns:
            True if backend is ready to execute tests
        """
        pass

    @abstractmethod
    def execute(self, spec_path: Path, config: Dict) -> Dict:
        """
        Execute a test specification

        Args:
            spec_path: Path to test specification file
            config: Configuration dictionary

        Returns:
            Result dictionary with test outcome
        """
        pass

    def supports_spec(self, spec_path: Path) -> bool:
        """
        Check if this backend supports the given spec (optional)

        Args:
            spec_path: Path to test specification file

        Returns:
            True if this backend can handle the spec
        """
        # Default implementation - all backends support all specs
        return True

    def get_description(self) -> str:
        """
        Get a human-readable description of this backend

        Returns:
            Description string
        """
        return f"{self.get_name()} backend"
