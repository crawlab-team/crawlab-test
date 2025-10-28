#!/usr/bin/env python3
"""
System utilities for testing infrastructure
Provides system-level operations like process management, file operations, etc.
"""

import logging
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import psutil


class ProcessManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def find_processes_by_pattern(self, pattern: str) -> List[psutil.Process]:
        """Find processes matching a pattern in command line"""
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])
                if pattern in cmdline:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def find_processes_by_name(self, name: str) -> List[psutil.Process]:
        """Find processes by name"""
        processes = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"] == name:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()  # SIGKILL
            else:
                proc.terminate()  # SIGTERM

            # Wait for process to die
            proc.wait(timeout=5)
            self.logger.info(f"Process {pid} terminated successfully")
            return True
        except psutil.NoSuchProcess:
            self.logger.info(f"Process {pid} does not exist")
            return True
        except psutil.TimeoutExpired:
            if not force:
                # Try force kill
                return self.kill_process(pid, force=True)
            self.logger.error(f"Failed to kill process {pid}")
            return False
        except Exception as e:
            self.logger.error(f"Error killing process {pid}: {e}")
            return False

    def kill_processes_by_pattern(self, pattern: str, force: bool = False) -> int:
        """Kill all processes matching pattern"""
        processes = self.find_processes_by_pattern(pattern)
        killed_count = 0

        for proc in processes:
            try:
                if self.kill_process(proc.pid, force):
                    killed_count += 1
            except Exception as e:
                self.logger.error(f"Error killing process {proc.pid}: {e}")

        return killed_count

    def is_process_running(self, pid: int) -> bool:
        """Check if a process is running"""
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False

    def get_process_children(self, pid: int) -> List[psutil.Process]:
        """Get child processes of a given PID"""
        try:
            parent = psutil.Process(pid)
            return parent.children(recursive=True)
        except psutil.NoSuchProcess:
            return []

    def create_zombie_process(self) -> int:
        """Create a zombie process for testing purposes"""
        # This is tricky - we need to create a process that exits but parent doesn't wait
        # This is more for demonstration - in real tests we'll simulate by killing processes
        pid = os.fork()
        if pid == 0:
            # Child process - exit immediately
            os._exit(0)
        else:
            # Parent process - don't wait for child (creates zombie)
            time.sleep(0.1)  # Give child time to exit
            return pid


class DockerManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def is_docker_available(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def list_containers(self, pattern: Optional[str] = None) -> List[Dict[str, str]]:
        """List Docker containers, optionally filtered by name pattern"""
        try:
            cmd = ["docker", "ps", "--format", "table {{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Image}}"]
            if pattern:
                cmd.extend(["--filter", f"name={pattern}"])

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            containers = []
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        containers.append({"id": parts[0], "name": parts[1], "status": parts[2], "image": parts[3]})
            return containers
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to list containers: {e}")
            return []

    def stop_container(self, container_name: str) -> bool:
        """Stop a Docker container"""
        try:
            subprocess.run(["docker", "stop", container_name], capture_output=True, check=True)
            self.logger.info(f"Stopped container: {container_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to stop container {container_name}: {e}")
            return False

    def start_container(self, container_name: str) -> bool:
        """Start a Docker container"""
        try:
            subprocess.run(["docker", "start", container_name], capture_output=True, check=True)
            self.logger.info(f"Started container: {container_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start container {container_name}: {e}")
            return False

    def restart_container(self, container_name: str) -> bool:
        """Restart a Docker container"""
        try:
            subprocess.run(["docker", "restart", container_name], capture_output=True, check=True)
            self.logger.info(f"Restarted container: {container_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to restart container {container_name}: {e}")
            return False

    def exec_in_container(self, container_name: str, command: List[str]) -> Tuple[int, str, str]:
        """Execute command in container"""
        try:
            cmd = ["docker", "exec", container_name, *command]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            self.logger.error(f"Failed to exec in container {container_name}: {e}")
            return -1, "", str(e)


class NetworkManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def block_ip(self, ip_address: str) -> bool:
        """Block traffic to/from an IP address using iptables"""
        try:
            # Block incoming traffic
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"], check=True)

            # Block outgoing traffic
            subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-d", ip_address, "-j", "DROP"], check=True)

            self.logger.info(f"Blocked IP address: {ip_address}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to block IP {ip_address}: {e}")
            return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock traffic to/from an IP address"""
        try:
            # Remove blocking rules
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"], check=True)

            subprocess.run(["sudo", "iptables", "-D", "OUTPUT", "-d", ip_address, "-j", "DROP"], check=True)

            self.logger.info(f"Unblocked IP address: {ip_address}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to unblock IP {ip_address}: {e}")
            return False

    def flush_iptables(self) -> bool:
        """Flush all iptables rules"""
        try:
            subprocess.run(["sudo", "iptables", "-F"], check=True)
            self.logger.info("Flushed iptables rules")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to flush iptables: {e}")
            return False


class FileSystemManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_temp_file(self, content: str, suffix: str = ".tmp") -> str:
        """Create a temporary file with content"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name

    def cleanup_temp_files(self, patterns: List[str]):
        """Clean up temporary files matching patterns"""
        import glob

        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    self.logger.debug(f"Removed temp file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to remove {file_path}: {e}")

    def tail_file(self, file_path: str, lines: int = 10) -> List[str]:
        """Get last N lines from a file"""
        try:
            with open(file_path) as f:
                return f.readlines()[-lines:]
        except Exception as e:
            self.logger.error(f"Failed to tail file {file_path}: {e}")
            return []


# Singleton instances for easy access
process_manager = ProcessManager()
docker_manager = DockerManager()
network_manager = NetworkManager()
filesystem_manager = FileSystemManager()
