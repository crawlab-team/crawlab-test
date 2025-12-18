#!/usr/bin/env python3
"""
INT-005: Auto Node Group Registration on Startup Test Runner

Integration test that validates the complete workflow of worker nodes automatically
registering themselves into node groups upon startup using the CRAWLAB_NODE_GROUPS
environment variable. Tests node registration, group auto-creation, and cluster state.
"""

import os
import subprocess
import sys
import time
import uuid

from crawlab_test.helpers.api import AuthHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.node_group import NodeGroupHelper
from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.utils import setup_logging, wait_for_condition


def print_step(step_num: int, description: str):
    """Print test step header."""
    print(f"\n{'=' * 80}")
    print(f"Step {step_num}: {description}")
    print("=" * 80)


class WorkerManager:
    """Manages test worker containers using docker_utils infrastructure."""

    def __init__(self, logger, network: str | None = None, image: str | None = None):
        """Initialize worker manager with docker utilities.

        Args:
            logger: Logger instance for output
            network: Docker network name (auto-detected if not provided)
            image: Docker image to use (auto-detected if not provided)
        """
        self.logger = logger
        self.docker = docker_utils
        self.containers = []

        if not self.docker.is_available():
            raise RuntimeError("Docker is not available. Please ensure Docker is installed and running.")

        # Auto-detect network and image from existing master container
        master = self.docker.find_master_container()
        if not master:
            is_ci = os.getenv("CI", "").lower() == "true"
            error_msg = "No Crawlab master container found. This test requires a running Crawlab cluster.\n"
            if is_ci:
                error_msg += (
                    "In CI environment, ensure that:\n"
                    "  1. Docker Compose services are started before running this test\n"
                    "  2. The workflow includes steps to start master container\n"
                    "  3. Services have time to become healthy before tests run"
                )
            else:
                error_msg += "Please start Crawlab using:\n  docker compose -f docker-compose.test.yml up -d"
            raise RuntimeError(error_msg)

        # Detect network from master container
        if not network:
            inspect = self.docker.get_container_inspect(master["Names"])
            if inspect and "NetworkSettings" in inspect:
                networks = inspect["NetworkSettings"].get("Networks", {})
                if networks:
                    self.network = next(iter(networks.keys()))
                    self.logger.info(f"Auto-detected network: {self.network}")
        else:
            self.network = network

        # Use master's image if not specified
        self.image = image or master.get("Image", "crawlabteam/crawlab-pro:develop")
        self.logger.info(f"Using image: {self.image}")

        # Get master container name for worker connection
        # Strip leading slash from container name (Docker adds it)
        self.master_name = master["Names"].lstrip("/")
        self.logger.info(f"Using master container: {self.master_name}")

    def start_worker(self, name: str, groups: str) -> bool:
        """Start a worker container with specified node groups.

        Args:
            name: Container name
            groups: Comma-separated list of node groups

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Starting worker {name} with groups: {groups}")

        try:
            # Get master container env to replicate settings
            master = self.docker.find_master_container()
            master_inspect = self.docker.get_container_inspect(master["Names"])
            master_env = {}
            if master_inspect and "Config" in master_inspect:
                env_list = master_inspect["Config"].get("Env", [])
                for env_var in env_list:
                    # Extract MongoDB and license settings from master
                    if "CRAWLAB_MONGO" in env_var or "CRAWLAB_LICENSE" in env_var:
                        key, _, value = env_var.partition("=")
                        master_env[key] = value

            # Build docker run command with inherited settings
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "--network",
                self.network,
                "-e",
                "CRAWLAB_NODE_MASTER=N",
                "-e",
                f"CRAWLAB_NODE_MASTER_ADDRESS={self.master_name}:9666",
            ]

            # Add MongoDB settings from master or defaults
            mongo_settings = {
                "CRAWLAB_MONGO_HOST": master_env.get("CRAWLAB_MONGO_HOST", "crawlab_dev_mongo"),
                "CRAWLAB_MONGO_PORT": master_env.get("CRAWLAB_MONGO_PORT", "27017"),
                "CRAWLAB_MONGO_DB": master_env.get("CRAWLAB_MONGO_DB", "crawlab"),
                "CRAWLAB_MONGO_USERNAME": master_env.get("CRAWLAB_MONGO_USERNAME", "dev_user"),
                "CRAWLAB_MONGO_PASSWORD": master_env.get("CRAWLAB_MONGO_PASSWORD", "dev_password"),
                "CRAWLAB_MONGO_AUTHSOURCE": master_env.get("CRAWLAB_MONGO_AUTHSOURCE", "admin"),
            }

            for key, value in mongo_settings.items():
                cmd.extend(["-e", f"{key}={value}"])

            # Add license from master if available (critical for Crawlab Pro)
            if "CRAWLAB_LICENSE" in master_env:
                cmd.extend(["-e", f"CRAWLAB_LICENSE={master_env['CRAWLAB_LICENSE']}"])

            # Add node groups and name
            cmd.extend(["-e", f"CRAWLAB_NODE_GROUPS={groups}", "-e", f"CRAWLAB_NODE_NAME={name}", self.image])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.containers.append(name)
                self.logger.info(f"✓ Worker {name} started successfully")
                return True
            else:
                self.logger.error(f"Failed to start worker: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Exception starting worker: {e}")
            return False

    def stop_worker(self, name: str):
        """Stop and remove a worker container.

        Args:
            name: Container name to stop
        """
        self.logger.info(f"Stopping worker {name}")
        self.docker.stop_container(name, timeout=10)
        self.docker.remove_container(name)
        if name in self.containers:
            self.containers.remove(name)

    def cleanup(self):
        """Cleanup all started containers."""
        self.logger.info("Cleaning up worker containers...")
        for name in list(self.containers):
            self.stop_worker(name)


def main():
    """Run auto node group registration test."""
    # Setup logging
    logger = setup_logging("INT-005")

    logger.info("=" * 80)
    logger.info("INT-005: Auto Node Group Registration Test")
    logger.info("=" * 80)

    # Check Docker availability first
    if not docker_utils.is_available():
        logger.error("Docker is not available. This test requires Docker.")
        return 1

    # Initialize helpers
    auth = AuthHelper()
    node_group_helper = NodeGroupHelper()
    node_helper = NodeHelper()

    try:
        worker_manager = WorkerManager(logger)
    except RuntimeError as e:
        logger.error(f"Failed to initialize worker manager: {e}")
        return 1

    token = None
    test_group_names = ["auto-group-1", "auto-group-2", "auto-group-3", "AUTO-GROUP-1"]

    try:
        # Step 1: Authenticate
        print_step(1, "Authenticate and Setup")
        token, response = auth.login()
        if not token:
            logger.error(f"Authentication failed: {response}")
            return 1
        logger.info("✓ Authenticated successfully")

        # Cleanup any existing groups with our test names
        logger.info("Checking for existing test node groups...")
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        if groups:
            for g in groups:
                if g["name"].lower() in [n.lower() for n in test_group_names]:
                    logger.info(f"Cleaning up existing group: {g['name']}")
                    node_group_helper.delete_node_group(token, g["_id"])

        # Step 2: Auto-Registration with Single Group
        print_step(2, "Auto-Registration with Single Group")

        worker1_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        if not worker_manager.start_worker(worker1_name, "auto-group-1"):
            return 1

        # Wait for node to register and group to be created
        logger.info("Waiting for node to register and group to be created...")

        def check_group_created():
            groups, _ = node_group_helper.list_node_groups(token, filter_str="auto-group-1")
            if groups:
                logger.debug(f"Found {len(groups)} groups matching filter")
            return any(g["name"] == "auto-group-1" for g in groups)

        if not wait_for_condition(check_group_created, timeout=30, check_interval=2):
            logger.error("Timeout waiting for group 'auto-group-1' to be created")
            # Log container logs for debugging
            logger.info(f"Checking worker container logs for {worker1_name}...")
            try:
                result = subprocess.run(
                    ["docker", "logs", "--tail", "50", worker1_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info(f"Worker logs:\n{result.stdout}")
                    if result.stderr:
                        logger.info(f"Worker stderr:\n{result.stderr}")
            except Exception as e:
                logger.warning(f"Failed to get worker logs: {e}")
            return 1

        # Verify node group creation
        groups, _ = node_group_helper.list_node_groups(token, filter_str="auto-group-1")
        group1 = next((g for g in groups if g["name"] == "auto-group-1"), None)
        logger.info(f"✓ Group 'auto-group-1' created: {group1['_id']}")

        # Wait for node to appear in registry
        def check_node_registered():
            nodes, _ = node_helper.list_nodes(token, size=100)
            return any(n.get("name") == worker1_name for n in nodes)

        if not wait_for_condition(check_node_registered, timeout=30, check_interval=2):
            logger.error(f"Timeout waiting for worker node {worker1_name} to register")
            return 1

        # Verify node assignment
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker1_node = next((n for n in nodes if n.get("name") == worker1_name), None)
        worker1_id = worker1_node["_id"]

        if worker1_id not in group1.get("node_ids", []):
            logger.error(f"Worker {worker1_id} not assigned to group {group1['_id']}")
            logger.error(f"Current node_ids: {group1.get('node_ids')}")
            return 1
        logger.info(f"✓ Worker {worker1_name} correctly assigned to group")

        # Step 3: Auto-Registration with Multiple Groups
        print_step(3, "Auto-Registration with Multiple Groups")

        worker2_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        if not worker_manager.start_worker(worker2_name, "auto-group-2,auto-group-3"):
            return 1

        # Wait for both groups to be created
        logger.info("Waiting for multiple groups to be created...")

        def check_groups_created():
            groups, _ = node_group_helper.list_node_groups(token, size=100)
            has_group2 = any(g["name"] == "auto-group-2" for g in groups)
            has_group3 = any(g["name"] == "auto-group-3" for g in groups)
            return has_group2 and has_group3

        if not wait_for_condition(check_groups_created, timeout=30, check_interval=2):
            logger.error("Timeout waiting for groups 'auto-group-2' and 'auto-group-3' to be created")
            return 1

        # Verify multiple groups creation
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        group2 = next((g for g in groups if g["name"] == "auto-group-2"), None)
        group3 = next((g for g in groups if g["name"] == "auto-group-3"), None)
        logger.info("✓ Both groups 'auto-group-2' and 'auto-group-3' created")

        # Wait for node to register
        def check_worker2_registered():
            nodes, _ = node_helper.list_nodes(token, size=100)
            return any(n.get("name") == worker2_name for n in nodes)

        if not wait_for_condition(check_worker2_registered, timeout=30, check_interval=2):
            logger.error(f"Timeout waiting for worker node {worker2_name} to register")
            return 1

        # Verify node assignment to all groups
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker2_node = next((n for n in nodes if n.get("name") == worker2_name), None)
        worker2_id = worker2_node["_id"]

        if worker2_id not in group2.get("node_ids", []) or worker2_id not in group3.get("node_ids", []):
            logger.error(f"Worker {worker2_id} not assigned to both groups")
            return 1
        logger.info(f"✓ Worker {worker2_name} correctly assigned to both groups")

        # Step 4: Case-Insensitive Matching
        print_step(4, "Case-Insensitive Matching")

        worker3_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        # Use different case for existing group
        if not worker_manager.start_worker(worker3_name, "AUTO-GROUP-1"):
            return 1

        # Wait for node to register (group should already exist)
        logger.info("Waiting for node to register with existing group...")

        def check_worker3_registered():
            nodes, _ = node_helper.list_nodes(token, size=100)
            return any(n.get("name") == worker3_name for n in nodes)

        if not wait_for_condition(check_worker3_registered, timeout=30, check_interval=2):
            logger.error(f"Timeout waiting for worker node {worker3_name} to register")
            return 1

        # Verify no duplicate group created
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        matching_groups = [g for g in groups if g["name"].lower() == "auto-group-1"]

        if len(matching_groups) > 1:
            logger.error(f"Duplicate groups found for 'auto-group-1': {[g['name'] for g in matching_groups]}")
            return 1

        group1_updated = matching_groups[0]
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker3_node = next((n for n in nodes if n.get("name") == worker3_name), None)
        worker3_id = worker3_node["_id"]

        if worker3_id not in group1_updated.get("node_ids", []):
            logger.error(f"Worker {worker3_id} not assigned to existing group (case-insensitive)")
            return 1
        logger.info("✓ Case-insensitive matching worked, no duplicate group created")

        # Step 5: Idempotency on Restart
        print_step(5, "Idempotency on Restart")

        logger.info(f"Restarting worker {worker1_name}...")
        if not worker_manager.docker.restart_container(worker1_name):
            logger.error(f"Failed to restart worker {worker1_name}")
            return 1

        # Wait for node to re-register (with small delay for restart)
        logger.info("Waiting for node to re-register...")
        time.sleep(5)  # Brief wait for container to fully start

        def check_node_stable():
            """Check that node is registered and group membership is correct"""
            try:
                group_check, _ = node_group_helper.get_node_group(token, group1["_id"])
                node_ids = group_check.get("node_ids", [])
                return worker1_id in node_ids and node_ids.count(worker1_id) == 1
            except:
                return False

        if not wait_for_condition(check_node_stable, timeout=30, check_interval=2):
            logger.error(f"Timeout waiting for worker {worker1_name} to re-register correctly")
            return 1

        # Verify group membership remains and no duplicates
        group1_final, _ = node_group_helper.get_node_group(token, group1["_id"])
        node_ids = group1_final.get("node_ids", [])

        if node_ids.count(worker1_id) != 1:
            logger.error(
                f"Worker {worker1_id} should appear exactly once in group, found {node_ids.count(worker1_id)} times"
            )
            return 1
        logger.info("✓ Registration is idempotent, no duplicate assignments on restart")

        logger.info("\n" + "=" * 80)
        logger.info("✅ INT-005 Auto Node Group Registration Test PASSED")
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error(f"\nTest failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        logger.info("\n" + "=" * 80)
        logger.info("Cleanup Phase")
        logger.info("=" * 80)

        worker_manager.cleanup()

        if token:
            groups, _ = node_group_helper.list_node_groups(token, size=100)
            if groups:
                for g in groups:
                    if g["name"].lower() in [n.lower() for n in test_group_names]:
                        node_group_helper.delete_node_group(token, g["_id"])
                        logger.info(f"✓ Cleaned up node group: {g['name']}")


if __name__ == "__main__":
    sys.exit(main())
