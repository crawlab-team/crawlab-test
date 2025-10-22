#!/usr/bin/env python3
"""
Wrapper script for CLS-002 - Docker Container Node Disconnection and Recovery

This script automates Docker container disconnection testing, validating that
the cluster can handle container-level network failures gracefully.
"""

import sys
import time
import logging
from pathlib import Path

# Add parent directory to path for imports
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from helpers.libs.docker_utils import docker_utils
from helpers.libs.api_client import CrawlabAPIClient
from helpers.libs.utils import setup_logging


class DockerContainerDisconnectionTest:
    """Test harness for Docker container disconnection scenarios."""
    
    def __init__(self):
        self.logger = setup_logging("CLS-002")
        self.docker = docker_utils
        self.api_client = None
        self.worker_container = None
        self.network_name = None
        
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available")
        
        # Find Crawlab containers
        containers = self.docker.find_crawlab_containers()
        if not containers:
            raise RuntimeError("No Crawlab containers found")
        
        # Find worker container
        for container in containers:
            name = container.get('Names', '')
            if 'worker' in name.lower():
                self.worker_container = name
                break
        
        if not self.worker_container:
            raise RuntimeError("No worker container found")
        
        self.logger.info(f"Selected worker container: {self.worker_container}")
        
        # Get network name
        inspect = self.docker.get_container_inspect(self.worker_container)
        if inspect and 'NetworkSettings' in inspect:
            networks = inspect['NetworkSettings'].get('Networks', {})
            if networks:
                self.network_name = list(networks.keys())[0]
        
        if not self.network_name:
            raise RuntimeError("Could not determine container network")
        
        self.logger.info(f"Using network: {self.network_name}")
    
    def run(self) -> bool:
        """Execute the full test suite."""
        success = True
        
        try:
            # Step 1: List containers
            self.logger.info("Step 1: Listing Docker containers")
            success &= self.list_containers()
            
            # Step 2: Health check
            self.logger.info("Step 2: Verifying cluster health")
            success &= self.verify_cluster_health()
            
            # Step 3: Network disconnection test
            self.logger.info("Step 3: Testing network disconnection")
            success &= self.test_network_disconnection()
            
            # Step 4: Pause/unpause test
            self.logger.info("Step 4: Testing container pause/unpause")
            success &= self.test_container_pause()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Test failed with error: {e}")
            return False
    
    def list_containers(self) -> bool:
        """List all Crawlab containers."""
        try:
            containers = self.docker.find_crawlab_containers()
            self.logger.info(f"Found {len(containers)} Crawlab containers:")
            for container in containers:
                name = container.get('Names', '')
                status = container.get('Status', '')
                self.logger.info(f"  - {name}: {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to list containers: {e}")
            return False
    
    def verify_cluster_health(self) -> bool:
        """Verify cluster is healthy."""
        try:
            containers = self.docker.find_crawlab_containers()
            running = sum(1 for c in containers if 'Up' in c.get('Status', ''))
            self.logger.info(f"Found {running}/{len(containers)} containers running")
            return running > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def test_network_disconnection(self) -> bool:
        """Test network disconnection and reconnection."""
        try:
            # Disconnect
            self.logger.info(f"Disconnecting {self.worker_container} from network")
            if not self.docker.simulate_network_disconnect(self.worker_container, self.network_name):
                self.logger.error("Failed to disconnect")
                return False
            
            # Wait
            time.sleep(5)
            
            # Reconnect
            self.logger.info(f"Reconnecting {self.worker_container} to network")
            if not self.docker.simulate_network_reconnect(self.worker_container, self.network_name):
                self.logger.error("Failed to reconnect")
                return False
            
            # Verify
            time.sleep(5)
            return self.verify_cluster_health()
            
        except Exception as e:
            self.logger.error(f"Network disconnection test failed: {e}")
            # Ensure cleanup
            try:
                self.docker.simulate_network_reconnect(self.worker_container, self.network_name)
            except:
                pass
            return False
    
    def test_container_pause(self) -> bool:
        """Test container pause and unpause."""
        try:
            # Pause
            self.logger.info(f"Pausing {self.worker_container}")
            if not self.docker.pause_container(self.worker_container):
                self.logger.error("Failed to pause container")
                return False
            
            # Wait
            time.sleep(5)
            
            # Unpause
            self.logger.info(f"Unpausing {self.worker_container}")
            if not self.docker.unpause_container(self.worker_container):
                self.logger.error("Failed to unpause container")
                return False
            
            # Verify
            time.sleep(5)
            return self.verify_cluster_health()
            
        except Exception as e:
            self.logger.error(f"Container pause test failed: {e}")
            # Ensure cleanup
            try:
                self.docker.unpause_container(self.worker_container)
            except:
                pass
            return False


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="CLS-002 Docker Container Disconnection Test")
    parser.add_argument("--ci", action="store_true", help="Running in CI environment")
    args = parser.parse_args()
    
    try:
        test = DockerContainerDisconnectionTest()
        success = test.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
