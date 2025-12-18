#!/usr/bin/env python3
"""
INT-006: Node Group Duplicate Prevention on Worker Registration

Integration test to ensure worker nodes registering with the same node-group name do
not create duplicate node-group records, covering sequential, concurrent, case-variant,
and restart scenarios.
"""

import subprocess
import sys
import time
import uuid

from crawlab_test.helpers.api import AuthHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.node_group import NodeGroupHelper
from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.utils import setup_logging, wait_for_condition


def print_step(num: int, desc: str) -> None:
    """Pretty-print step headers for clarity."""
    line = "=" * 80
    print(f"\n{line}\nStep {num}: {desc}\n{line}")


class WorkerManager:
    """Manage lifecycle of temporary worker containers for tests."""

    def __init__(self, logger):
        if not docker_utils.is_available():
            raise RuntimeError("Docker is not available. Start Docker before running this test.")

        master = docker_utils.find_master_container()
        if not master:
            raise RuntimeError("No Crawlab master container found. Start the Crawlab cluster before running this test.")

        self.logger = logger
        self.master = master
        self.network = self._detect_network(master)
        self.image = master.get("Image", "crawlabteam/crawlab-pro:develop")
        self.master_name = master["Names"].lstrip("/")
        self.master_env = self._collect_master_env(master)
        self.containers: list[str] = []

    def _detect_network(self, master: dict) -> str:
        inspect = docker_utils.get_container_inspect(master["Names"])
        networks = inspect.get("NetworkSettings", {}).get("Networks", {}) if inspect else {}
        if not networks:
            raise RuntimeError("Could not detect Docker network from master container")
        network = next(iter(networks.keys()))
        self.logger.info(f"Auto-detected network: {network}")
        return network

    def _collect_master_env(self, master: dict) -> dict[str, str]:
        inspect = docker_utils.get_container_inspect(master["Names"])
        env_list = inspect.get("Config", {}).get("Env", []) if inspect else []
        env: dict[str, str] = {}
        for item in env_list:
            key, _, value = item.partition("=")
            env[key] = value
        return env

    def _build_base_env(self, name: str, groups: str) -> list[str]:
        master_host = self.master_env.get("CRAWLAB_MASTER_HOST", self.master_name)
        grpc_port = self.master_env.get("CRAWLAB_GRPC_PORT", self.master_env.get("CRAWLAB_MASTER_PORT", "9666"))
        auth_key = self.master_env.get("CRAWLAB_AUTH_KEY", "Crawlab2024!")

        mongo_defaults = {
            "CRAWLAB_MONGO_HOST": self.master_env.get("CRAWLAB_MONGO_HOST", "crawlab_dev_mongo"),
            "CRAWLAB_MONGO_PORT": self.master_env.get("CRAWLAB_MONGO_PORT", "27017"),
            "CRAWLAB_MONGO_DB": self.master_env.get("CRAWLAB_MONGO_DB", "crawlab"),
            "CRAWLAB_MONGO_USERNAME": self.master_env.get("CRAWLAB_MONGO_USERNAME", "dev_user"),
            "CRAWLAB_MONGO_PASSWORD": self.master_env.get("CRAWLAB_MONGO_PASSWORD", "dev_password"),
            "CRAWLAB_MONGO_AUTHSOURCE": self.master_env.get("CRAWLAB_MONGO_AUTHSOURCE", "admin"),
        }

        env = [
            "-e",
            "CRAWLAB_NODE_MASTER=N",
            "-e",
            f"CRAWLAB_NODE_MASTER_ADDRESS={self.master_name}:9666",
            "-e",
            f"CRAWLAB_MASTER_HOST={master_host}",
            "-e",
            f"CRAWLAB_MASTER_PORT={grpc_port}",
            "-e",
            f"CRAWLAB_GRPC_HOST={master_host}",
            "-e",
            f"CRAWLAB_GRPC_PORT={grpc_port}",
            "-e",
            f"CRAWLAB_AUTH_KEY={auth_key}",
            "-e",
            f"CRAWLAB_NODE_GROUPS={groups}",
            "-e",
            f"CRAWLAB_NODE_NAME={name}",
        ]

        if "CRAWLAB_LICENSE" in self.master_env:
            env.extend(["-e", f"CRAWLAB_LICENSE={self.master_env['CRAWLAB_LICENSE']}"])

        for key, value in mongo_defaults.items():
            env.extend(["-e", f"{key}={value}"])

        return env

    def start_worker(self, name: str, groups: str) -> bool:
        cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            name,
            "--network",
            self.network,
        ]
        cmd.extend(self._build_base_env(name, groups))
        cmd.append(self.image)

        self.logger.info(f"Starting worker {name} with groups '{groups}'")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if result.returncode == 0:
            self.containers.append(name)
            self.logger.info(f"✓ Worker {name} started")
            return True

        self.logger.error(f"Failed to start worker {name}: {result.stderr}")
        return False

    def start_workers_concurrent(self, names: list[str], groups: str) -> None:
        for name in names:
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "--network",
                self.network,
            ]
            cmd.extend(self._build_base_env(name, groups))
            cmd.append(self.image)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.containers.append(name)
        time.sleep(2)

    def restart_worker(self, name: str) -> bool:
        return docker_utils.restart_container(name)

    def stop_and_remove(self, name: str) -> None:
        docker_utils.stop_container(name, timeout=10)
        docker_utils.remove_container(name, force=True)
        if name in self.containers:
            self.containers.remove(name)

    def cleanup(self) -> None:
        self.logger.info("Cleaning up worker containers...")
        for name in list(self.containers):
            self.stop_and_remove(name)


def wait_for_group(token: str, helper: NodeGroupHelper, group_name: str, timeout: int = 40) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        groups, _ = helper.list_node_groups(token, filter_str=group_name, size=200)
        match = next((g for g in groups if g.get("name", "").lower() == group_name.lower()), None)
        if match:
            return match
        time.sleep(2)
    return {}


def wait_for_nodes(token: str, node_helper: NodeHelper, names: list[str], timeout: int = 40) -> dict[str, str]:
    start = time.time()
    while time.time() - start < timeout:
        nodes, _ = node_helper.list_nodes(token, size=200)
        present = {n.get("name"): n.get("_id") for n in nodes if n.get("name") in names}
        if len(present) == len(names):
            return present
        time.sleep(2)
    return {}


def main() -> int:
    logger = setup_logging("INT-006")
    logger.info("=" * 80)
    logger.info("INT-006: Node Group Duplicate Prevention on Worker Registration")
    logger.info("=" * 80)

    try:
        wm = WorkerManager(logger)
    except RuntimeError as e:
        logger.error(e)
        return 1

    auth = AuthHelper()
    node_helper = NodeHelper()
    group_helper = NodeGroupHelper()
    token = None

    test_group_names = ["dup-group-1", "dup-group-2"]
    worker_seq1 = f"ngdup-seq1-{uuid.uuid4().hex[:6]}"
    worker_seq2 = f"ngdup-seq2-{uuid.uuid4().hex[:6]}"
    worker_case = f"ngdup-case-{uuid.uuid4().hex[:6]}"
    worker_concurrent = [f"ngdup-con{i}-{uuid.uuid4().hex[:4]}" for i in range(3)]

    try:
        # Step 1: Authenticate and cleanup
        print_step(1, "Authenticate and cleanup")
        token, resp = auth.login()
        if not token:
            logger.error(f"Authentication failed: {resp}")
            return 1

        groups, _ = group_helper.list_node_groups(token, size=200)
        for g in groups:
            if g.get("name", "").lower() in [n.lower() for n in test_group_names]:
                group_helper.delete_node_group(token, g["_id"])
                logger.info(f"Removed pre-existing test group {g['name']}")

        # Step 2: Sequential registration same group
        print_step(2, "Sequential registration with same group name")
        if not wm.start_worker(worker_seq1, "dup-group-1"):
            return 1
        group1 = wait_for_group(token, group_helper, "dup-group-1")
        if not group1:
            logger.error("Group dup-group-1 was not created")
            return 1
        seq_nodes = wait_for_nodes(token, node_helper, [worker_seq1])
        if worker_seq1 not in seq_nodes:
            logger.error("First worker not registered")
            return 1

        if not wm.start_worker(worker_seq2, "dup-group-1"):
            return 1
        seq_nodes = wait_for_nodes(token, node_helper, [worker_seq1, worker_seq2])
        if len(seq_nodes) != 2:
            logger.error("Sequential workers did not both register")
            return 1

        groups, _ = group_helper.list_node_groups(token, filter_str="dup-group-1", size=200)
        matching = [g for g in groups if g.get("name", "").lower() == "dup-group-1"]
        if len(matching) != 1:
            logger.error(f"Expected 1 group dup-group-1, found {len(matching)}")
            return 1
        group_dup1 = matching[0]
        node_ids = group_dup1.get("node_ids", [])
        if seq_nodes[worker_seq1] not in node_ids or seq_nodes[worker_seq2] not in node_ids:
            logger.error("Sequential workers not both in group")
            return 1
        if node_ids.count(seq_nodes[worker_seq1]) > 1 or node_ids.count(seq_nodes[worker_seq2]) > 1:
            logger.error("Duplicate node IDs detected in group after sequential registration")
            return 1
        logger.info("✓ Sequential registration reused single group and unique node_ids")

        # Step 3: Concurrent registration same group
        print_step(3, "Concurrent registration with same group name")
        wm.start_workers_concurrent(worker_concurrent, "dup-group-2")
        con_nodes = wait_for_nodes(token, node_helper, worker_concurrent)
        if len(con_nodes) != len(worker_concurrent):
            logger.error("Not all concurrent workers registered")
            return 1

        groups, _ = group_helper.list_node_groups(token, filter_str="dup-group-2", size=200)
        matching = [g for g in groups if g.get("name", "").lower() == "dup-group-2"]
        if len(matching) != 1:
            logger.error(f"Expected 1 group dup-group-2, found {len(matching)}")
            return 1
        node_ids = matching[0].get("node_ids", [])
        missing = [wid for wid in con_nodes.values() if wid not in node_ids]
        duplicates = [wid for wid in con_nodes.values() if node_ids.count(wid) > 1]
        if missing:
            logger.error(f"Missing concurrent workers in group: {missing}")
            return 1
        if duplicates:
            logger.error(f"Duplicate node IDs in group after concurrent registration: {duplicates}")
            return 1
        logger.info("✓ Concurrent registration created one group with all workers uniquely assigned")

        # Step 4: Case-variant registration
        print_step(4, "Case-variant registration reuses existing group")
        if not wm.start_worker(worker_case, "DUP-GROUP-1"):
            return 1
        case_nodes = wait_for_nodes(token, node_helper, [worker_case])
        if worker_case not in case_nodes:
            logger.error("Case-variant worker did not register")
            return 1
        groups, _ = group_helper.list_node_groups(token, filter_str="dup-group-1", size=200)
        matching = [g for g in groups if g.get("name", "").lower() == "dup-group-1"]
        if len(matching) != 1:
            logger.error("Case-variant registration created duplicate group")
            return 1
        group_dup1 = matching[0]
        node_ids = group_dup1.get("node_ids", [])
        if case_nodes[worker_case] not in node_ids:
            logger.error("Case-variant worker not assigned to existing group")
            return 1
        logger.info("✓ Case-insensitive matching reused existing group")

        # Step 5: Restart idempotency
        print_step(5, "Restart idempotency")
        if not wm.restart_worker(worker_seq1):
            logger.error("Failed to restart first worker")
            return 1
        time.sleep(5)

        def _stable_membership():
            group, _ = group_helper.get_node_group(token, group_dup1["_id"])
            node_ids_local = group.get("node_ids", [])
            return node_ids_local.count(seq_nodes[worker_seq1]) == 1

        if not wait_for_condition(_stable_membership, timeout=30, check_interval=2):
            logger.error("Worker restart produced duplicate or missing membership")
            return 1
        logger.info("✓ Restart preserved single membership entry")

        logger.info("=" * 80)
        logger.info("✅ INT-006 completed successfully")
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        logger.info("Cleanup phase starting...")
        wm.cleanup()
        if token:
            groups, _ = group_helper.list_node_groups(token, size=200)
            for g in groups:
                if g.get("name", "").lower() in [n.lower() for n in test_group_names]:
                    group_helper.delete_node_group(token, g["_id"])
                    logger.info(f"Removed test group {g['name']}")


if __name__ == "__main__":
    sys.exit(main())
