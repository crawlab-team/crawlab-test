#!/usr/bin/env python3
"""
Node Manager Helper Script
Manages Crawlab worker nodes for testing scenarios including disconnection/reconnection simulation.
"""

import argparse
import json
import subprocess
import sys
import time
from typing import Dict, List, Optional

import requests


class NodeManager:
    def __init__(self, master_url: str = "http://localhost:8080", api_token: Optional[str] = None):
        self.master_url = master_url.rstrip("/")
        self.api_token = api_token
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}" if api_token else ""}
        self._disconnected_networks = []  # Track networks we disconnect from

    def _find_worker_container(
        self, include_stopped: bool = False, target_worker_node: Optional[Dict] = None
    ) -> Optional[str]:
        """Find the worker container name based on Docker compose setup"""
        import os

        compose_namespace = os.environ.get("CRAWLAB_COMPOSE_NAMESPACE", "crawlab_test")

        try:
            # List containers
            cmd = ["docker", "ps", "--format", "{{.Names}}"]
            if include_stopped:
                cmd.insert(2, "-a")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            containers = result.stdout.strip().split("\n") if result.stdout.strip() else []
            print(f"Available containers: {containers}")

            # If we have a target worker node, try to match by node info
            if target_worker_node:
                node_key = target_worker_node.get("key", "")
                node_name = target_worker_node.get("name", "")

                # Check if container name has any part of the worker info
                for container in containers:
                    if "worker" in container.lower():
                        # Try to match with node key or name components
                        if (
                            (node_key and any(part in container for part in node_key.split("-")[:2]))
                            or (node_name and node_name.lower() in container.lower())
                            or (node_key and node_key[-4:] in container)
                        ):  # Last 4 chars
                            print(f"Found matching worker container: {container} for node {node_name}/{node_key}")
                            return container

            # Look for worker containers by pattern matching
            worker_containers = []
            for container in containers:
                if "worker" in container.lower():
                    worker_containers.append(container)

            if not worker_containers:
                print(f"No worker containers found in: {containers}")
                return None

            # If multiple workers found, prefer the first one or specific patterns
            if len(worker_containers) == 1:
                print(f"Found single worker container: {worker_containers[0]}")
                return worker_containers[0]

            # If multiple workers, try to find one that matches our compose namespace or is numbered
            for container in worker_containers:
                if compose_namespace in container:
                    print(f"Found worker container matching namespace: {container}")
                    return container

            # Fallback to first worker container
            selected_worker = worker_containers[0]
            print(f"Multiple workers found, selecting first: {selected_worker}")
            print(f"All worker containers: {worker_containers}")
            return selected_worker

        except subprocess.CalledProcessError as e:
            print(f"Failed to find worker container: {e}")
            return None

    def get_nodes(self) -> List[Dict]:
        """Get list of all nodes from master"""
        try:
            response = requests.get(f"{self.master_url}/api/nodes", headers=self.headers)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"Error fetching nodes: {e}")
            return []

    def get_node_by_name(self, node_name: str) -> Optional[Dict]:
        """Find a specific node by name"""
        nodes = self.get_nodes()
        for node in nodes:
            if node.get("name") == node_name or node.get("key") == node_name:
                return node
        return None

    def disconnect_node(self, node_name: str, method: str = "network") -> bool:
        """
        Disconnect a worker node using specified method
        Methods: network, process, docker
        """
        print(f"Disconnecting node '{node_name}' using method '{method}'...")

        node = self.get_node_by_name(node_name)
        if not node:
            print(f"Error: Node '{node_name}' not found")
            return False

        if method == "network":
            return self._disconnect_network(node)
        elif method == "process":
            return self._disconnect_process(node)
        elif method == "docker":
            return self._disconnect_docker(node)
        else:
            print(f"Error: Unknown disconnection method '{method}'")
            return False

    def reconnect_node(self, node_name: str) -> bool:
        """Reconnect a previously disconnected node"""
        print(f"Reconnecting node '{node_name}'...")

        # For Docker environments, prioritize Docker methods
        methods = [self._reconnect_docker, self._reconnect_process, self._reconnect_network]

        for method in methods:
            try:
                if method(node_name):
                    print(f"Successfully reconnected '{node_name}'")
                    return self._wait_for_node_online(node_name)
            except Exception as e:
                print(f"Reconnection method failed: {e}")
                continue

        print(f"Error: Could not reconnect node '{node_name}'")
        return False

    def _disconnect_network(self, node: Dict) -> bool:
        """Simulate network disconnection using iptables"""
        node_ip = node.get("ip", "localhost")

        if node_ip == "localhost" or node_ip == "127.0.0.1":
            # For local testing, use docker network isolation
            return self._disconnect_docker_network(node)

        # Block traffic to/from node IP
        commands = [f"sudo iptables -A INPUT -s {node_ip} -j DROP", f"sudo iptables -A OUTPUT -d {node_ip} -j DROP"]

        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Network disconnection failed: {e}")
                return False

        print(f"Network disconnection successful for {node_ip}")
        return True

    def _disconnect_process(self, node: Dict) -> bool:
        """Stop the worker process"""
        node_name = node.get("name", node.get("key"))

        # Try different process stop methods
        commands = [
            f"pkill -f 'crawlab.*worker.*{node_name}'",
            f"systemctl stop crawlab-worker-{node_name}",
            f"docker stop crawlab-worker-{node_name}",
        ]

        for cmd in commands:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Process stopped successfully: {cmd}")
                    return True
            except Exception as e:
                print(f"Command failed: {cmd} - {e}")
                continue

        print("Could not stop worker process")
        return False

    def _disconnect_docker(self, node: Dict) -> bool:
        """Disconnect worker container from Docker network to simulate network partition"""
        node_name = node.get("name", node.get("key"))

        print(f"Attempting to disconnect worker container from network for node: {node_name}")
        print(f"Node info: key={node.get('key')}, name={node.get('name')}")

        # Find the worker container, passing node info for better matching
        worker_container = self._find_worker_container(include_stopped=False, target_worker_node=node)

        if not worker_container:
            print("Could not find running worker container")
            return False

        # First, inspect the container to find ALL networks it's actually connected to
        try:
            inspect_result = subprocess.run(
                ["docker", "inspect", worker_container, "--format", "{{json .NetworkSettings.Networks}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            import json

            networks_data = json.loads(inspect_result.stdout.strip())
            connected_networks = list(networks_data.keys())

            print(f"Container {worker_container} is connected to networks: {connected_networks}")

            if not connected_networks:
                print("Container is not connected to any networks")
                return False

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Failed to inspect container networks: {e}")
            # Fallback to trying common network names
            import os

            compose_namespace = os.environ.get("CRAWLAB_COMPOSE_NAMESPACE", "crawlab_test")
            connected_networks = [
                f"{compose_namespace}_crawlab_test",
                f"{compose_namespace}_default",
                "dev_default",
                "bridge",
            ]
            print(f"Falling back to trying common network names: {connected_networks}")

        disconnected_from = []

        for network_name in connected_networks:
            try:
                # Disconnect from this network
                result = subprocess.run(
                    ["docker", "network", "disconnect", network_name, worker_container], capture_output=True, text=True
                )

                if result.returncode == 0:
                    print(f"Successfully disconnected {worker_container} from network {network_name}")
                    disconnected_from.append(network_name)
                else:
                    print(f"Failed to disconnect from {network_name}: {result.stderr}")

            except subprocess.CalledProcessError as e:
                print(f"Could not disconnect container from {network_name}: {e}")
                continue

        if disconnected_from:
            # Store the networks we disconnected from for later reconnection
            self._disconnected_networks = disconnected_from
            print(f"Container {worker_container} disconnected from networks: {disconnected_from}")
            return True
        else:
            print(f"Could not disconnect {worker_container} from any networks")
            return False

    def _disconnect_docker_network(self, node: Dict) -> bool:
        """Disconnect node from docker network - delegates to main docker disconnect method"""
        # This method now delegates to the main _disconnect_docker method
        # which uses network disconnect instead of container stop
        return self._disconnect_docker(node)

    def _reconnect_network(self, node_name: str) -> bool:
        """Restore network connectivity"""
        # Remove iptables rules
        commands = ["sudo iptables -D INPUT -s {ip} -j DROP", "sudo iptables -D OUTPUT -d {ip} -j DROP"]

        # Try to remove rules (may fail if they don't exist)
        for _cmd_template in commands:
            try:
                # This is simplified - in real implementation, we'd need to track the IP
                subprocess.run(["sudo", "iptables", "-F"], capture_output=True)
            except:
                pass

        return True

    def _reconnect_process(self, node_name: str) -> bool:
        """Restart the worker process"""
        commands = [f"systemctl start crawlab-worker-{node_name}", f"docker start crawlab-worker-{node_name}"]

        for cmd in commands:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Process restarted successfully: {cmd}")
                    return True
            except Exception as e:
                print(f"Command failed: {cmd} - {e}")
                continue

        return False

    def _reconnect_docker(self, node_name: str) -> bool:
        """Reconnect worker container to Docker networks to restore connectivity"""
        print(f"Attempting to reconnect worker container networks for node: {node_name}")

        # Find the worker container (should still be running but disconnected)
        worker_container = self._find_worker_container(include_stopped=False)

        if not worker_container:
            print("Could not find running worker container for reconnection")
            return False

        # Check if we have stored networks from the disconnection
        disconnected_networks = getattr(self, "_disconnected_networks", [])

        if not disconnected_networks:
            # Fallback: try to connect to common networks
            import os

            compose_namespace = os.environ.get("CRAWLAB_COMPOSE_NAMESPACE", "crawlab_test")
            disconnected_networks = [
                f"{compose_namespace}_crawlab_test",
                f"{compose_namespace}_default",
                "dev_default",  # Current actual network name
                "bridge",
            ]
            print(f"No stored networks found, trying common networks: {disconnected_networks}")
        else:
            print(f"Reconnecting to previously disconnected networks: {disconnected_networks}")

        reconnected_to = []

        for network_name in disconnected_networks:
            try:
                result = subprocess.run(
                    ["docker", "network", "connect", network_name, worker_container], capture_output=True, text=True
                )

                if result.returncode == 0:
                    print(f"Successfully reconnected {worker_container} to network {network_name}")
                    reconnected_to.append(network_name)
                else:
                    # Network might not exist or container already connected
                    print(f"Could not reconnect to {network_name}: {result.stderr}")

            except subprocess.CalledProcessError as e:
                print(f"Exception reconnecting to {network_name}: {e}")
                continue

        if reconnected_to:
            print(f"Container {worker_container} reconnected to networks: {reconnected_to}")
            # Clear stored networks
            self._disconnected_networks = []

            # Give the network connections time to stabilize
            import time

            time.sleep(3)

            return True
        else:
            print(f"Could not reconnect {worker_container} to any networks")
            return False

    def _wait_for_node_online(self, node_name: str, timeout: int = 60) -> bool:
        """Wait for node to appear as online in master"""
        print(f"Waiting for node '{node_name}' to come online...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            node = self.get_node_by_name(node_name)
            if node and node.get("status") == "online":
                print(f"Node '{node_name}' is now online")
                return True

            time.sleep(2)

        print(f"Timeout waiting for node '{node_name}' to come online")
        return False

    def check_node_status(self, node_name: str) -> Dict:
        """Get current status of a specific node"""
        node = self.get_node_by_name(node_name)
        if not node:
            return {"error": f"Node {node_name} not found"}

        return {
            "name": node.get("name"),
            "status": node.get("status"),
            "ip": node.get("ip"),
            "last_seen": node.get("last_heartbeat_ts"),
            "tasks_running": node.get("available_runners", 0),
        }


def main():
    parser = argparse.ArgumentParser(description="Manage Crawlab worker nodes for testing")
    parser.add_argument("--master-url", default="http://localhost:8080", help="Crawlab master URL")
    parser.add_argument("--api-token", help="API token for authentication")

    subparsers = parser.add_subparsers(dest="action", help="Available actions")

    # Disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect a worker node")
    disconnect_parser.add_argument("node_name", help="Name of the node to disconnect")
    disconnect_parser.add_argument(
        "--method", choices=["network", "process", "docker"], default="network", help="Disconnection method"
    )

    # Reconnect command
    reconnect_parser = subparsers.add_parser("reconnect", help="Reconnect a worker node")
    reconnect_parser.add_argument("node_name", help="Name of the node to reconnect")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check node status")
    status_parser.add_argument("node_name", help="Name of the node to check")

    # List command
    subparsers.add_parser("list", help="List all nodes")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    manager = NodeManager(args.master_url, args.api_token)

    if args.action == "disconnect":
        success = manager.disconnect_node(args.node_name, args.method)
        sys.exit(0 if success else 1)

    elif args.action == "reconnect":
        success = manager.reconnect_node(args.node_name)
        sys.exit(0 if success else 1)

    elif args.action == "status":
        status = manager.check_node_status(args.node_name)
        print(json.dumps(status, indent=2))

    elif args.action == "list":
        nodes = manager.get_nodes()
        for node in nodes:
            status = manager.check_node_status(node.get("name", node.get("key")))
            print(f"{status.get('name', 'unknown')}: {status.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
