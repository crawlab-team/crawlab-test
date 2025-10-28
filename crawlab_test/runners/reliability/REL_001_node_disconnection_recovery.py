#!/usr/bin/env python3
"""
Wrapper script for CLS-001 - Master/Worker Node Disconnection and Reconnection Stability

This script automates the execution of the cluster test for node disconnection
and reconnection, integrating with the docker-manager utility and test framework.
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
from crawlab_test.helpers.infrastructure.utils import setup_logging, wait_for_condition


class NodeDisconnectionTest:
    """Test harness for master/worker node disconnection scenarios."""
    
    def __init__(self):
        self.logger = setup_logging("CLS-001")
        self.docker = docker_utils
        self.api_client = None
        self.worker_container = None
        self.worker_node_name = None
        self.worker_container_id = None
        self.network_name = None
        
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available. Please ensure Docker is installed and running.")
        
        # Find Crawlab containers
        containers = self.docker.find_crawlab_containers()
        if not containers:
            import os
            is_ci = os.getenv('CI', '').lower() == 'true'
            error_msg = (
                "No Crawlab containers found. "
                "This test requires a running Crawlab cluster.\n"
            )
            if is_ci:
                error_msg += (
                    "In CI environment, ensure that:\n"
                    "  1. Docker Compose services are started before running this test\n"
                    "  2. The workflow includes steps to start master and worker containers\n"
                    "  3. Services have time to become healthy before tests run\n"
                    "\nExpected containers: crawlab_test_master, crawlab_test_worker"
                )
            else:
                error_msg += (
                    "Please start Crawlab using:\n"
                    "  docker compose -f docker-compose.test.yml up -d\n"
                )
            raise RuntimeError(error_msg)
        
        # Find worker container
        for container in containers:
            name = container.get('Names', '')
            if 'worker' in name.lower():
                self.worker_container = name
                break
        
        if not self.worker_container:
            raise RuntimeError("No worker container found")
        
        self.logger.info(f"Selected worker container: {self.worker_container}")
        
        # Get the node name from container environment and container ID for matching
        try:
            import subprocess
            
            # Get CRAWLAB_NODE_NAME if set
            result = subprocess.run(
                ['docker', 'exec', self.worker_container, 'env'],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('CRAWLAB_NODE_NAME='):
                    self.worker_node_name = line.split('=', 1)[1].strip()
                    break
            
            # Get container ID for fallback matching
            inspect = self.docker.get_container_inspect(self.worker_container)
            if inspect and 'Id' in inspect:
                self.worker_container_id = inspect['Id'][:12]  # Short container ID
                self.logger.info(f"Worker container ID: {self.worker_container_id}")
            
            if self.worker_node_name:
                self.logger.info(f"Worker node name: {self.worker_node_name}")
            else:
                self.logger.warning("CRAWLAB_NODE_NAME not set, will use container ID for matching")
        except Exception as e:
            self.logger.warning(f"Failed to get worker node info: {e}")
        
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
            # Step 1: Verify initial state
            self.logger.info("Step 1: Verifying initial cluster state")
            success &= self.verify_cluster_health()
            
            # Step 2: Simulate disconnection
            self.logger.info("Step 2: Simulating worker disconnection")
            success &= self.disconnect_worker()
            
            # Step 3: Wait for detection
            self.logger.info("Step 3: Waiting for disconnection detection")
            time.sleep(10)
            
            # Step 4: Reconnect worker
            self.logger.info("Step 4: Reconnecting worker")
            success &= self.reconnect_worker()
            
            # Step 5: Verify recovery
            self.logger.info("Step 5: Verifying cluster recovery and task execution")
            # Wait for worker to be fully ready to accept tasks
            # Use longer timeout in CI due to resource constraints
            import os
            is_ci = os.getenv('CI', '').lower() == 'true'
            ready_timeout = 180 if is_ci else 120  # 3 minutes in CI, 2 minutes locally
            self.logger.info(f"Waiting for worker to fully stabilize (timeout: {ready_timeout}s, CI: {is_ci})")
            success &= self.wait_for_worker_ready(timeout=ready_timeout)
            if not success:
                self.logger.error("Worker failed to become ready within timeout")
                return False
            success &= self.verify_cluster_health()
            success &= self.verify_task_execution_on_reconnected_worker()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Test failed with error: {e}")
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
    
    def disconnect_worker(self) -> bool:
        """Disconnect worker from network."""
        try:
            success = self.docker.simulate_network_disconnect(
                self.worker_container,
                self.network_name
            )
            if success:
                self.logger.info(f"Disconnected {self.worker_container} from {self.network_name}")
            else:
                self.logger.error("Failed to disconnect worker")
            return success
        except Exception as e:
            self.logger.error(f"Disconnection failed: {e}")
            return False
    
    def reconnect_worker(self) -> bool:
        """Reconnect worker to network."""
        try:
            success = self.docker.simulate_network_reconnect(
                self.worker_container,
                self.network_name
            )
            if success:
                self.logger.info(f"Reconnected {self.worker_container} to {self.network_name}")
            else:
                self.logger.error("Failed to reconnect worker")
            return success
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
            return False
    
    def wait_for_worker_ready(self, timeout: int = 120) -> bool:
        """
        Wait for worker to be fully ready to accept tasks after reconnection.
        
        This method uses an intelligent polling approach to wait for:
        1. Node to appear in API and be marked as active=true, status=online
        2. Node to remain stable for at least the required period
        
        The stability period must account for the master's monitoring behavior:
        - Master monitors every 20 seconds (increased from 15s for stability)
        - Master requires 2 consecutive failures before marking offline (40s grace period)
        - Therefore, we need to wait at least 45s for stability confirmation
        
        This ensures that the master's monitoring loop has run at least twice
        and confirmed the node's health, preventing race conditions.
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            bool: True if worker is ready and stable, False otherwise
        """
        try:
            # Check if running in CI environment
            import os
            is_ci = os.getenv('CI', '').lower() == 'true'
            
            if not self.api_client:
                self.api_client = CrawlabAPIClient()
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.api_client.login()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Login attempt {attempt+1} failed: {e}, retrying...")
                            time.sleep(2)
                        else:
                            self.logger.error(f"Failed to login to API after {max_retries} attempts: {e}")
                            return False
            
            start_time = time.time()
            check_interval = 2  # Check every 2 seconds
            first_active_time = None  # Track when node first becomes active
            
            # Stability period must be > 2 * monitor_interval to ensure master has confirmed health
            # Master now has: monitor_interval=20s, requires 2 failures before offline
            # So we need: 45s stability (> 2 * 20s = 40s grace period)
            stability_period = 50 if is_ci else 45  # Extra buffer in CI for slower systems
            
            # Allow more flaps since master itself tolerates 2 failures before marking offline
            # We should be at least as tolerant as the master
            max_flaps_allowed = 3  # Increased from 2 to match master's tolerance
            flap_count = 0
            
            self.logger.info(f"Polling for worker readiness (stability_period={stability_period}s, timeout={timeout}s, CI={is_ci})")
            
            while time.time() - start_time < timeout:
                try:
                    # Get nodes to find our worker
                    nodes = self.api_client.get_nodes()
                    reconnected_node = None
                    
                    # Find the worker node using same matching logic
                    if self.worker_node_name:
                        for node in nodes:
                            if node.get('name') == self.worker_node_name:
                                reconnected_node = node
                                break
                    
                    if not reconnected_node and self.worker_container_id:
                        for node in nodes:
                            node_key = node.get('key', '')
                            if self.worker_container_id.lower() in node_key.lower():
                                reconnected_node = node
                                break
                    
                    if not reconnected_node:
                        worker_nodes = [n for n in nodes if not n.get('is_master', False)]
                        if len(worker_nodes) == 1:
                            reconnected_node = worker_nodes[0]
                    
                    # Check if node is ready
                    if reconnected_node:
                        is_active = reconnected_node.get('active', False)
                        is_enabled = reconnected_node.get('enabled', True)
                        status = reconnected_node.get('status', '')
                        
                        # Check if node meets all readiness criteria
                        is_ready = is_active and is_enabled and status == 'online'
                        
                        if is_ready:
                            current_time = time.time()
                            
                            # First time we see it as active
                            if first_active_time is None:
                                first_active_time = current_time
                                elapsed = current_time - start_time
                                self.logger.info(
                                    f"Worker became active after {elapsed:.1f}s - "
                                    f"waiting {stability_period}s for stability confirmation..."
                                )
                            
                            # Check if it's been stable long enough
                            stable_duration = current_time - first_active_time
                            if stable_duration >= stability_period:
                                total_elapsed = current_time - start_time
                                self.logger.info(
                                    f"✓ Worker is ready and stable after {total_elapsed:.1f}s "
                                    f"(stable for {stable_duration:.1f}s > {stability_period}s)"
                                )
                                return True
                            else:
                                remaining = stability_period - stable_duration
                                self.logger.debug(
                                    f"Worker stable for {stable_duration:.1f}s, "
                                    f"waiting {remaining:.1f}s more..."
                                )
                        else:
                            # Node not ready, reset stability timer (with tolerance for flaps)
                            if first_active_time is not None:
                                elapsed = time.time() - start_time
                                flap_count += 1
                                
                                if flap_count <= max_flaps_allowed:
                                    # Allow brief flaps - don't reset timer yet
                                    self.logger.warning(
                                        f"Worker temporarily inactive after {elapsed:.1f}s - "
                                        f"flap {flap_count}/{max_flaps_allowed} (active={is_active}, status={status}), "
                                        f"keeping stability timer..."
                                    )
                                else:
                                    # Too many flaps, reset the timer
                                    self.logger.error(
                                        f"Worker went inactive too many times ({flap_count} flaps) - "
                                        f"resetting stability timer (active={is_active}, status={status})"
                                    )
                                    first_active_time = None
                                    flap_count = 0
                            else:
                                self.logger.debug(
                                    f"Worker not ready: active={is_active}, "
                                    f"enabled={is_enabled}, status={status}"
                                )
                    else:
                        if first_active_time is not None:
                            self.logger.warning("Worker node disappeared from API - resetting stability timer")
                            first_active_time = None
                            flap_count = 0  # Reset flap count when node disappears
                        else:
                            self.logger.debug("Worker node not found in API yet")
                
                except Exception as e:
                    self.logger.debug(f"Error checking worker readiness: {e}")
                    # Don't reset stability timer on transient API errors in CI
                    # Only reset after repeated errors
                    if not is_ci and first_active_time is not None:
                        first_active_time = None
                
                time.sleep(check_interval)
            
            # Timeout reached
            elapsed = time.time() - start_time
            if first_active_time is not None:
                stable_duration = time.time() - first_active_time
                self.logger.error(
                    f"Timeout: Worker became active but not stable enough "
                    f"(stable for {stable_duration:.1f}s < {stability_period}s required, "
                    f"flaps: {flap_count}, CI: {is_ci})"
                )
            else:
                self.logger.error(
                    f"Timeout: Worker never became active and ready within {timeout}s "
                    f"(elapsed: {elapsed:.1f}s, CI: {is_ci})"
                )
                
            # Log final node state for debugging
            try:
                nodes = self.api_client.get_nodes()
                self.logger.error(f"Final node states at timeout: {[(n.get('name'), n.get('active'), n.get('status')) for n in nodes]}")
            except:
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to wait for worker ready: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def verify_task_execution_on_reconnected_worker(self) -> bool:
        """Verify reconnected worker can execute new tasks."""
        try:
            # Initialize API client if needed
            if not self.api_client:
                self.api_client = CrawlabAPIClient()
                # Retry login with backoff
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.api_client.login()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Login attempt {attempt+1} failed: {e}, retrying...")
                            time.sleep(2)
                        else:
                            self.logger.error(f"Failed to login to API after {max_retries} attempts: {e}")
                            return False
            
            # 1. Get worker node info from API
            nodes = self.api_client.get_nodes()
            reconnected_node = None
            
            # Strategy 1: Match by explicit node name (most reliable when CRAWLAB_NODE_NAME is set)
            if self.worker_node_name:
                for node in nodes:
                    node_name = node.get('name', '')
                    if node_name == self.worker_node_name:
                        reconnected_node = node
                        self.logger.info(f"Matched node by name: {self.worker_node_name}")
                        break
            
            # Strategy 2: Match by container ID in node key (when node name is UUID, container ID should match)
            # This works because Docker hostname in container = container ID, and when no CRAWLAB_NODE_NAME is set,
            # the node key becomes a UUID that typically incorporates the container ID
            if not reconnected_node and self.worker_container_id:
                for node in nodes:
                    node_key = node.get('key', '')
                    # Check if container ID appears in the node key
                    if self.worker_container_id and self.worker_container_id.lower() in node_key.lower():
                        reconnected_node = node
                        self.logger.info(f"Matched node by container ID in key: {self.worker_container_id}")
                        break
            
            # Strategy 3: For dynamically named test containers, try matching by exclusion
            # (if there are only 2 worker nodes and we can identify the master, pick the other one)
            if not reconnected_node:
                worker_nodes = [n for n in nodes if not n.get('is_master', False)]
                if len(worker_nodes) == 1:
                    reconnected_node = worker_nodes[0]
                    self.logger.info(f"Matched node by exclusion (only worker): {reconnected_node.get('name')}")
            
            if not reconnected_node:
                self.logger.error(f"Cannot find reconnected worker in API")
                self.logger.error(f"Search criteria: name='{self.worker_node_name}', container_id='{self.worker_container_id}', container='{self.worker_container}'")
                self.logger.error(f"Available nodes: {[(n.get('name'), n.get('key'), n.get('is_master'), n.get('status')) for n in nodes]}")
                return False
            
            self.logger.info(f"Found reconnected node: {reconnected_node.get('name')} (key={reconnected_node.get('key')})")
            
            # 2. Verify node status
            if not reconnected_node.get('active', False):
                self.logger.error(f"Node not active after reconnection: active={reconnected_node.get('active')}")
                return False
            
            if not reconnected_node.get('enabled', True):
                self.logger.error(f"Node not enabled after reconnection: enabled={reconnected_node.get('enabled')}")
                return False
            
            node_status = reconnected_node.get('status', '')
            if node_status != 'online':
                self.logger.error(f"Node not online after reconnection: status={node_status}")
                return False
            
            self.logger.info(f"Node status verified: active={reconnected_node['active']}, enabled={reconnected_node.get('enabled', True)}, status={node_status}")
            
            # 3. Get or create a test spider
            spiders = self.api_client.get_spiders()
            test_spider = None
            for spider in spiders:
                if spider.get('name') == 'test-spider':
                    test_spider = spider
                    break
            
            if not test_spider:
                # Create a simple test spider
                try:
                    test_spider = self.api_client.create_spider({
                        'name': 'test-spider',
                        'cmd': 'echo "Test spider for reconnected worker"',
                        'type': 'customized'
                    })
                    self.logger.info(f"Created test spider: {test_spider.get('_id')}")
                except Exception as e:
                    self.logger.warning(f"Could not create test spider: {e}")
                    # Use first available spider
                    if spiders:
                        test_spider = spiders[0]
                    else:
                        self.logger.error("No spiders available for testing")
                        return False
            
            # 4. Create a test task specifically for this node
            task = self.api_client.create_task({
                'spider_id': test_spider['_id'],
                'mode': 'selected-nodes',
                'node_ids': [reconnected_node['_id']],
                'cmd': 'echo "Testing reconnected worker"'
            })
            
            self.logger.info(f"Created test task {task['_id']} for reconnected worker")
            
            # 5. Wait for task to be assigned and start executing
            # Use longer timeout in CI environments
            import os
            is_ci = os.getenv('CI', '').lower() == 'true'
            task_start_timeout = 60 if is_ci else 30
            
            def check_task_running():
                t = self.api_client.get_task_by_id(task['_id'])
                if not t:
                    return False
                task_status = t.get('status', '')
                return task_status in ['running', 'finished']
            
            task_started = wait_for_condition(
                check_task_running,
                timeout=task_start_timeout,
                check_interval=3
            )
            
            if not task_started:
                final_task = self.api_client.get_task_by_id(task['_id'])
                task_status = final_task.get('status', 'unknown') if final_task else 'not found'
                task_error = final_task.get('error', 'N/A') if final_task else 'N/A'
                self.logger.error(f"Task never started executing. Status: {task_status}, Error: {task_error}")
                return False
            
            # 6. Wait for completion
            def check_task_complete():
                t = self.api_client.get_task_by_id(task['_id'])
                if not t:
                    return False
                task_status = t.get('status', '')
                return task_status in ['finished', 'error']
            
            task_completed = wait_for_condition(
                check_task_complete,
                timeout=60,
                check_interval=2
            )
            
            final_task = self.api_client.get_task_by_id(task['_id'])
            final_status = final_task.get('status', 'unknown') if final_task else 'unknown'
            self.logger.info(f"Task completed with status: {final_status}")
            
            return task_completed and final_status == 'finished'
            
        except Exception as e:
            self.logger.error(f"Task execution verification failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="CLS-001 Node Disconnection Test")
    parser.add_argument("--ci", action="store_true", help="Running in CI environment")
    args = parser.parse_args()
    
    try:
        test = NodeDisconnectionTest()
        success = test.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
