#!/usr/bin/env python3
"""
Docker utilities for Crawlab testing
Provides Docker container discovery, management, and interaction capabilities.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional


class DockerUtils:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._docker_available = self._check_docker_availability()

    def _check_docker_availability(self) -> bool:
        """Check if Docker is available and accessible"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if Docker is available"""
        return self._docker_available

    def is_running_in_container(self) -> bool:
        """Check if we're running inside a Docker container"""
        try:
            # Check for Docker container indicators
            if os.path.exists("/.dockerenv"):
                return True

            # Check cgroup for Docker
            with open("/proc/1/cgroup") as f:
                if "docker" in f.read():
                    return True
        except:
            pass

        return False

    def find_crawlab_containers(self) -> List[Dict[str, Any]]:
        """Find all running Crawlab containers"""
        if not self._docker_available:
            return []

        try:
            # Get running containers with crawlab in name or image
            result = subprocess.run(
                ["docker", "ps", "--format", "json", "--filter", "name=crawlab", "--filter", "status=running"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            containers = []
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        containers.append(json.loads(line))

            # Also try filtering by image if no containers found by name
            if not containers:
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--format",
                        "json",
                        "--filter",
                        "ancestor=crawlabteam/crawlab-pro",
                        "--filter",
                        "status=running",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            containers.append(json.loads(line))

            return containers

        except Exception as e:
            self.logger.debug(f"Failed to find Crawlab containers: {e}")
            return []

    def find_master_container(self) -> Optional[Dict[str, Any]]:
        """Find the Crawlab master container"""
        containers = self.find_crawlab_containers()

        # Look for master container first
        for container in containers:
            names = container.get("Names", "")
            image = container.get("Image", "")

            # Check if this is a master container
            if (
                any(keyword in names.lower() for keyword in ["master", "_master_", "test_master"])
                or "master" in image.lower()
            ):
                return container

        # If no explicit master found, use first crawlab container
        return containers[0] if containers else None

    def get_container_port_mapping(self, container_name: str, container_port: str) -> Optional[Dict[str, str]]:
        """Get port mapping for a Docker container"""
        if not self._docker_available:
            return None

        try:
            result = subprocess.run(
                ["docker", "port", container_name, container_port], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse output like "0.0.0.0:8080->8080/tcp"
                port_mapping = result.stdout.strip().split("\n")[0]
                if "->" in port_mapping:
                    host_part = port_mapping.split("->")[0]
                    if ":" in host_part:
                        host_ip, host_port = host_part.rsplit(":", 1)
                        return {"host_ip": host_ip, "host_port": host_port, "container_port": container_port}

            return None
        except Exception:
            return None

    def detect_crawlab_api_url(self) -> Optional[str]:
        """Detect Crawlab API URL from running containers"""
        master_container = self.find_master_container()
        if not master_container:
            return None

        container_name = master_container["Names"]

        # Get the port mapping for the container
        port_info = self.get_container_port_mapping(container_name, "8080")
        if port_info:
            if self.is_running_in_container():
                # If we're in Docker, use container name as hostname
                url = f"http://{container_name}:8080"
            else:
                # If we're on host, use mapped port
                url = f"http://localhost:{port_info['host_port']}"

            return url

        return None

    def get_all_containers(self, filter_name: str = "crawlab") -> List[Dict[str, Any]]:
        """Get list of Docker containers matching filter"""
        if not self._docker_available:
            return []

        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "json", "--filter", f"name={filter_name}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            containers = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    containers.append(json.loads(line))

            return containers
        except Exception as e:
            self.logger.error(f"Failed to get Docker containers: {e}")
            return []

    def get_container_logs(self, container_name: str, lines: int = 100) -> str:
        """Get logs from a Docker container"""
        if not self._docker_available:
            return "Docker not available"

        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_name], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return result.stdout + result.stderr
            else:
                return f"Failed to get logs: {result.stderr}"
        except Exception as e:
            return f"Failed to get logs: {e}"

    def exec_in_container(self, container_name: str, command: List[str]) -> Dict[str, Any]:
        """Execute command in Docker container"""
        if not self._docker_available:
            return {"returncode": -1, "stdout": "", "stderr": "Docker not available", "success": False}

        try:
            result = subprocess.run(
                ["docker", "exec", container_name, *command], capture_output=True, text=True, timeout=30
            )

            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }
        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    def exec_command(self, container_name: str, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command in Docker container and capture output"""
        if not self._docker_available:
            return {"exit_code": -1, "output": "", "error": "Docker not available"}

        try:
            result = subprocess.run(
                ["docker", "exec", container_name, "/bin/sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {"exit_code": result.returncode, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"exit_code": -1, "output": "", "error": str(e)}

    def pause_container(self, container_name: str) -> bool:
        """Pause a Docker container"""
        if not self._docker_available:
            return False

        try:
            result = subprocess.run(["docker", "pause", container_name], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def unpause_container(self, container_name: str) -> bool:
        """Unpause a Docker container"""
        if not self._docker_available:
            return False

        try:
            result = subprocess.run(["docker", "unpause", container_name], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def restart_container(self, container_name: str) -> bool:
        """Restart a Docker container"""
        if not self._docker_available:
            return False

        try:
            result = subprocess.run(["docker", "restart", container_name], capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def get_container_stats(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get resource statistics for a Docker container"""
        if not self._docker_available:
            return None

        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "json", container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout.strip())
            return None
        except Exception:
            return None

    def get_container_inspect(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed container information"""
        if not self._docker_available:
            return None

        try:
            result = subprocess.run(["docker", "inspect", container_name], capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                return data[0] if data else None
            return None
        except Exception:
            return None

    def get_network_info(self, network_name: Optional[str] = None) -> Dict[str, Any]:
        """Get Docker network information"""
        if not self._docker_available:
            return {}

        try:
            cmd = ["docker", "network", "ls", "--format", "json"]
            if network_name:
                cmd.extend(["--filter", f"name={network_name}"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        networks.append(json.loads(line))
                return {"networks": networks}

            return {}
        except Exception:
            return {}

    def simulate_network_disconnect(self, container_name: str, network_name: Optional[str] = None) -> bool:
        """Simulate network disconnection by disconnecting container from network"""
        if not self._docker_available:
            return False

        try:
            # If no network specified, find the network the container is on
            if not network_name:
                inspect = self.get_container_inspect(container_name)
                if inspect and "NetworkSettings" in inspect:
                    networks = inspect["NetworkSettings"].get("Networks", {})
                    if networks:
                        network_name = next(iter(networks.keys()))

            if not network_name:
                return False

            result = subprocess.run(
                ["docker", "network", "disconnect", network_name, container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0
        except Exception:
            return False

    def simulate_network_reconnect(self, container_name: str, network_name: str) -> bool:
        """Reconnect container to network"""
        if not self._docker_available:
            return False

        try:
            result = subprocess.run(
                ["docker", "network", "connect", network_name, container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0
        except Exception:
            return False


# Global instance for easy import
docker_utils = DockerUtils()
