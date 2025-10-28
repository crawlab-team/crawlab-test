"""
Infrastructure Utilities

Core infrastructure for testing including API clients, Docker, database, and system utilities.
"""

# Re-export all common utilities for backwards compatibility
# Import order matters - some modules depend on others

try:
    from .api_client import CrawlabAPIClient
except ImportError as e:
    print(f"Warning: Could not import CrawlabAPIClient: {e}")
    CrawlabAPIClient = None

try:
    from .docker import DockerUtils, docker_utils
except ImportError as e:
    print(f"Warning: Could not import docker utils: {e}")
    docker_utils = None
    DockerUtils = None

try:
    from .database import (
        TASK_STATUS_ASSIGNED,
        TASK_STATUS_CANCELLED,
        TASK_STATUS_ERROR,
        TASK_STATUS_FINISHED,
        TASK_STATUS_NODE_DISCONNECTED,
        TASK_STATUS_PENDING,
        TASK_STATUS_RUNNING,
        DatabaseHelper,
    )
except ImportError as e:
    print(f"Warning: Could not import database helpers: {e}")
    DatabaseHelper = None
    TASK_STATUS_PENDING = None
    TASK_STATUS_RUNNING = None
    TASK_STATUS_FINISHED = None
    TASK_STATUS_NODE_DISCONNECTED = None
    TASK_STATUS_ASSIGNED = None
    TASK_STATUS_CANCELLED = None
    TASK_STATUS_ERROR = None

try:
    from .system import ProcessManager, process_manager
except ImportError as e:
    print(f"Warning: Could not import system utils: {e}")
    process_manager = None
    ProcessManager = None

try:
    from .utils import TestMetrics, format_duration, load_config, setup_logging, wait_for_condition, wait_with_timeout
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    setup_logging = None
    wait_for_condition = None
    wait_with_timeout = None
    format_duration = None
    TestMetrics = None
    load_config = None

try:
    from .cleanup import cleanup_all_resources
except ImportError as e:
    print(f"Warning: Could not import cleanup: {e}")
    cleanup_all_resources = None

try:
    from .ui_base import UITestBase
except ImportError as e:
    print(f"Warning: Could not import UITestBase: {e}")
    UITestBase = None

__all__ = [
    # API
    "CrawlabAPIClient",
    # Docker
    "docker_utils",
    "DockerUtils",
    # Database
    "DatabaseHelper",
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_FINISHED",
    "TASK_STATUS_NODE_DISCONNECTED",
    "TASK_STATUS_ASSIGNED",
    "TASK_STATUS_CANCELLED",
    "TASK_STATUS_ERROR",
    # System
    "process_manager",
    "ProcessManager",
    # Utilities
    "setup_logging",
    "wait_for_condition",
    "wait_with_timeout",
    "format_duration",
    "TestMetrics",
    "load_config",
    "cleanup_all_resources",
    # UI
    "UITestBase",
]
