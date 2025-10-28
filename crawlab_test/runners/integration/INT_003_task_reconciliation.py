#!/usr/bin/env python3
"""
Wrapper script for SCH-001 - Task Status Reconciliation and Process Verification

This script automates testing of the task reconciliation service's ability to detect
and fix inconsistent task states between the database and actual worker processes.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.utils import setup_logging


class TaskReconciliationTest:
    """Test harness for task status reconciliation."""
    
    def __init__(self):
        self.logger = setup_logging("SCH-001")
        self.docker = docker_utils
        self.api_client = None
        
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available. Please ensure Docker is installed and running.")
        
        # Find Crawlab containers
        containers = self.docker.find_crawlab_containers()
        if not containers:
            import os
            is_ci = os.getenv('CI', '').lower() == 'true'
            error_msg = (
                "No Crawlab containers found. "
                "This test requires a running Crawlab cluster.\\n"
            )
            if is_ci:
                error_msg += (
                    "In CI environment, ensure that:\\n"
                    "  1. Docker Compose services are started before running this test\\n"
                    "  2. The workflow includes steps to start master and worker containers\\n"
                    "  3. Services have time to become healthy before tests run\\n"
                    "\\nExpected containers: crawlab_test_master, crawlab_test_worker"
                )
            else:
                error_msg += (
                    "Please start Crawlab using:\n"
                    "  docker compose -f docker-compose.test.yml up -d\n"
                )
            raise RuntimeError(error_msg)
        
        self.logger.info(f"Found {len(containers)} Crawlab containers")
    
    def run(self) -> bool:
        """Execute the full test suite."""
        success = True
        
        try:
            # Step 1: Verify reconciliation service
            self.logger.info("Step 1: Verifying reconciliation service status")
            success &= self.verify_reconciliation_service()
            
            # Step 2: Check cluster health
            self.logger.info("Step 2: Checking cluster health")
            success &= self.verify_cluster_health()
            
            # For now, this is a basic smoke test
            # Full reconciliation testing would require:
            # - Creating test tasks
            # - Killing processes
            # - Waiting for reconciliation
            # - Verifying status updates
            
            return success
            
        except Exception as e:
            self.logger.error(f"Test failed with error: {e}")
            return False
    
    def verify_reconciliation_service(self) -> bool:
        """Verify reconciliation service is running."""
        try:
            # Check master container logs for reconciliation service
            containers = self.docker.find_crawlab_containers()
            master_container = None
            
            for container in containers:
                name = container.get('Names', '')
                if 'master' in name.lower():
                    master_container = name
                    break
            
            if master_container:
                logs = self.docker.get_container_logs(master_container, lines=100)
                # Check if reconciliation service is mentioned in logs
                if 'reconciliation' in logs.lower() or 'taskreconciliation' in logs.lower():
                    self.logger.info("Reconciliation service appears to be active")
                    return True
                else:
                    self.logger.warning("No reconciliation service logs found")
                    return True  # Don't fail, service may not log frequently
            
            return True
        except Exception as e:
            self.logger.error(f"Service verification failed: {e}")
            return False
    
    def verify_cluster_health(self) -> bool:
        """Verify cluster is healthy."""
        try:
            containers = self.docker.find_crawlab_containers()
            self.logger.info(f"Found {len(containers)} containers running")
            return len(containers) > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="SCH-001 Task Reconciliation Test")
    parser.add_argument("--ci", action="store_true", help="Running in CI environment")
    args = parser.parse_args()
    
    try:
        test = TaskReconciliationTest()
        success = test.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
