#!/usr/bin/env python3
"""
Docker container management helper for Crawlab testing
Provides container-aware operations for testing infrastructure scenarios.
"""

import argparse
import sys
import time
import logging
from pathlib import Path

# Add tests directory to path
tests_dir = Path(__file__).resolve().parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from helpers.infrastructure.api_client import CrawlabAPIClient
from helpers.infrastructure.docker_utils import docker_utils

class DockerContainerManager:
    def __init__(self, api_client: CrawlabAPIClient = None):
        self.api_client = api_client or CrawlabAPIClient()
        self.docker = docker_utils
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available or accessible")
    
    def list_crawlab_containers(self):
        """List all Crawlab containers"""
        containers = self.docker.find_crawlab_containers()
        
        print(f"Found {len(containers)} Crawlab containers:")
        print("-" * 80)
        print(f"{'Name':<30} {'Image':<30} {'Status':<15} {'Ports'}")
        print("-" * 80)
        
        for container in containers:
            name = container.get('Names', '')
            image = container.get('Image', '')
            status = container.get('Status', '')
            ports = container.get('Ports', '')
            print(f"{name:<30} {image:<30} {status:<15} {ports}")
    
    def disconnect_worker(self, worker_name: str, method: str = "network"):
        """Disconnect a worker container"""
        containers = self.docker.get_all_containers("crawlab")
        worker_container = None
        
        for container in containers:
            if worker_name in container.get('Names', ''):
                worker_container = container
                break
        
        if not worker_container:
            self.logger.error(f"Worker container '{worker_name}' not found")
            return False
        
        container_name = worker_container['Names']
        
        if method == "network":
            # Disconnect from network
            inspect = self.docker.get_container_inspect(container_name)
            if inspect and 'NetworkSettings' in inspect:
                networks = inspect['NetworkSettings'].get('Networks', {})
                if networks:
                    network_name = list(networks.keys())[0]
                    success = self.docker.simulate_network_disconnect(container_name, network_name)
                    if success:
                        self.logger.info(f"Disconnected {container_name} from network {network_name}")
                        return True
                    else:
                        self.logger.error(f"Failed to disconnect {container_name} from network")
                        return False
        
        elif method == "pause":
            # Pause the container
            success = self.docker.pause_container(container_name)
            if success:
                self.logger.info(f"Paused container {container_name}")
                return True
            else:
                self.logger.error(f"Failed to pause container {container_name}")
                return False
        
        else:
            self.logger.error(f"Unknown disconnection method: {method}")
            return False
    
    def reconnect_worker(self, worker_name: str, network_name: str = None):
        """Reconnect a worker container"""
        containers = self.docker.get_all_containers("crawlab")
        worker_container = None
        
        for container in containers:
            if worker_name in container.get('Names', ''):
                worker_container = container
                break
        
        if not worker_container:
            self.logger.error(f"Worker container '{worker_name}' not found")
            return False
        
        container_name = worker_container['Names']
        
        # Check if container is paused
        inspect = self.docker.get_container_inspect(container_name)
        if inspect and inspect.get('State', {}).get('Paused', False):
            success = self.docker.unpause_container(container_name)
            if success:
                self.logger.info(f"Unpaused container {container_name}")
                return True
            else:
                self.logger.error(f"Failed to unpause container {container_name}")
                return False
        
        # Try to reconnect to network
        if not network_name:
            # Try to find the network name from other containers
            all_containers = self.docker.find_crawlab_containers()
            for container in all_containers:
                if container['Names'] != container_name:
                    other_inspect = self.docker.get_container_inspect(container['Names'])
                    if other_inspect and 'NetworkSettings' in other_inspect:
                        networks = other_inspect['NetworkSettings'].get('Networks', {})
                        if networks:
                            network_name = list(networks.keys())[0]
                            break
        
        if network_name:
            success = self.docker.simulate_network_reconnect(container_name, network_name)
            if success:
                self.logger.info(f"Reconnected {container_name} to network {network_name}")
                return True
            else:
                self.logger.error(f"Failed to reconnect {container_name} to network")
                return False
        
        self.logger.error(f"Could not determine network for reconnection")
        return False
    
    def check_cluster_health(self):
        """Check the health of the Crawlab cluster"""
        print("Checking Crawlab cluster health...")
        print("-" * 50)
        
        # Check API connectivity
        if self.api_client.ping():
            print("✓ API connectivity: OK")
        else:
            print("✗ API connectivity: FAILED")
            return False
        
        # Check nodes
        try:
            nodes = self.api_client.get_nodes()
            print(f"✓ Found {len(nodes)} nodes:")
            for node in nodes:
                name = node.get('name', 'Unknown')
                status = node.get('status', 'Unknown')
                is_master = node.get('is_master', False)
                node_type = "Master" if is_master else "Worker"
                print(f"  - {name} ({node_type}): {status}")
        except Exception as e:
            print(f"✗ Failed to get nodes: {e}")
            return False
        
        # Check containers
        containers = self.docker.find_crawlab_containers()
        print(f"✓ Found {len(containers)} Docker containers")
        
        return True
    
    def get_container_logs(self, container_name: str, lines: int = 50):
        """Get logs from a specific container"""
        logs = self.docker.get_container_logs(container_name, lines)
        print(f"Logs for {container_name} (last {lines} lines):")
        print("-" * 80)
        print(logs)
    
    def exec_command(self, container_name: str, command: list):
        """Execute command in container"""
        result = self.docker.exec_in_container(container_name, command)
        
        print(f"Executed '{' '.join(command)}' in {container_name}")
        print(f"Return code: {result['returncode']}")
        
        if result['stdout']:
            print("STDOUT:")
            print(result['stdout'])
        
        if result['stderr']:
            print("STDERR:")
            print(result['stderr'])
        
        return result['success']
    
    def simulate_container_failure(self, container_name: str, failure_type: str = "pause"):
        """Simulate various types of container failures"""
        if failure_type == "pause":
            return self.docker.pause_container(container_name)
        elif failure_type == "restart":
            return self.docker.restart_container(container_name)
        else:
            self.logger.error(f"Unknown failure type: {failure_type}")
            return False
    
    def monitor_reconciliation(self, timeout: int = 60):
        """Monitor task reconciliation during container disruption"""
        start_time = time.time()
        
        print("Monitoring task reconciliation...")
        print("-" * 50)
        
        while time.time() - start_time < timeout:
            try:
                # Get reconciliation status
                status = self.api_client.get_reconciliation_status()
                if status:
                    print(f"Reconciliation status: {status}")
                
                # Get task status summary
                tasks = self.api_client.get_tasks()
                if tasks:
                    status_counts = {}
                    for task in tasks:
                        status = task.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"Task status summary: {status_counts}")
                
                time.sleep(5)
                
            except Exception as e:
                print(f"Error monitoring reconciliation: {e}")
                time.sleep(5)
        
        print("Monitoring completed")


def main():
    parser = argparse.ArgumentParser(description="Docker Container Manager for Crawlab Testing")
    parser.add_argument('--action', choices=['list', 'disconnect', 'reconnect', 'health', 'logs', 'exec', 'fail', 'monitor'], 
                       required=True, help='Action to perform')
    parser.add_argument('--container', help='Container name')
    parser.add_argument('--method', choices=['network', 'pause'], default='network', 
                       help='Disconnection method')
    parser.add_argument('--network', help='Network name for reconnection')
    parser.add_argument('--lines', type=int, default=50, help='Number of log lines to show')
    parser.add_argument('--command', nargs='+', help='Command to execute in container')
    parser.add_argument('--failure-type', choices=['pause', 'restart'], default='pause',
                       help='Type of failure to simulate')
    parser.add_argument('--timeout', type=int, default=60, help='Monitoring timeout in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        manager = DockerContainerManager()
        
        if args.action == 'list':
            manager.list_crawlab_containers()
        
        elif args.action == 'disconnect':
            if not args.container:
                print("Error: --container is required for disconnect action")
                sys.exit(1)
            success = manager.disconnect_worker(args.container, args.method)
            sys.exit(0 if success else 1)
        
        elif args.action == 'reconnect':
            if not args.container:
                print("Error: --container is required for reconnect action")
                sys.exit(1)
            success = manager.reconnect_worker(args.container, args.network)
            sys.exit(0 if success else 1)
        
        elif args.action == 'health':
            success = manager.check_cluster_health()
            sys.exit(0 if success else 1)
        
        elif args.action == 'logs':
            if not args.container:
                print("Error: --container is required for logs action")
                sys.exit(1)
            manager.get_container_logs(args.container, args.lines)
        
        elif args.action == 'exec':
            if not args.container or not args.command:
                print("Error: --container and --command are required for exec action")
                sys.exit(1)
            success = manager.exec_command(args.container, args.command)
            sys.exit(0 if success else 1)
        
        elif args.action == 'fail':
            if not args.container:
                print("Error: --container is required for fail action")
                sys.exit(1)
            success = manager.simulate_container_failure(args.container, args.failure_type)
            sys.exit(0 if success else 1)
        
        elif args.action == 'monitor':
            manager.monitor_reconciliation(args.timeout)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()