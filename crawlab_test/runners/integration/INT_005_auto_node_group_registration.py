#!/usr/bin/env python3
"""
INT-005: Auto Node Group Registration on Startup Test Runner

Integration test that validates the complete workflow of worker nodes automatically
registering themselves into node groups upon startup using the CRAWLAB_NODE_GROUPS
environment variable. Tests node registration, group auto-creation, and cluster state.
"""

import subprocess
import sys
import time
import uuid

from crawlab_test.helpers.api import APIAssertions, AuthHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.node_group import NodeGroupHelper


def print_step(step_num: int, description: str):
    """Print test step header."""
    print(f"\n{'=' * 80}")
    print(f"Step {step_num}: {description}")
    print("=" * 80)


class WorkerManager:
    """Manages test worker containers."""

    def __init__(self, network: str = "dev_default", image: str = "crawlabteam/crawlab-pro:develop"):
        self.network = network
        self.image = image
        self.containers = []

    def start_worker(self, name: str, groups: str) -> bool:
        """Start a worker container with specified node groups."""
        print(f"Starting worker {name} with groups: {groups}")
        
        # Get master container env to replicate mongo settings
        try:
            cmd = [
                "docker", "run", "-d",
                "--name", name,
                "--network", self.network,
                "-e", "CRAWLAB_NODE_MASTER=N",
                "-e", "CRAWLAB_NODE_MASTER_ADDRESS=crawlab_dev_master:9666",
                "-e", "CRAWLAB_MONGO_HOST=crawlab_dev_mongo",
                "-e", "CRAWLAB_MONGO_PORT=27017",
                "-e", "CRAWLAB_MONGO_DB=crawlab",
                "-e", "CRAWLAB_MONGO_USERNAME=dev_user",
                "-e", "CRAWLAB_MONGO_PASSWORD=dev_password",
                "-e", "CRAWLAB_MONGO_AUTHSOURCE=admin",
                "-e", f"CRAWLAB_NODE_GROUPS={groups}",
                "-e", f"CRAWLAB_NODE_NAME={name}",
                self.image
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.containers.append(name)
                return True
            else:
                print(f"Error starting worker: {result.stderr}")
                return False
        except Exception as e:
            print(f"Exception starting worker: {e}")
            return False

    def stop_worker(self, name: str):
        """Stop and remove a worker container."""
        print(f"Stopping worker {name}")
        subprocess.run(["docker", "stop", name], capture_output=True)
        subprocess.run(["docker", "rm", name], capture_output=True)
        if name in self.containers:
            self.containers.remove(name)

    def cleanup(self):
        """Cleanup all started containers."""
        for name in list(self.containers):
            self.stop_worker(name)


def main():
    """Run auto node group registration test."""
    auth = AuthHelper()
    assertions = APIAssertions()
    node_group_helper = NodeGroupHelper()
    node_helper = NodeHelper()
    worker_manager = WorkerManager()

    print("INT-005: Auto Node Group Registration Test")
    print("=" * 80)

    token = None
    test_group_names = ["auto-group-1", "auto-group-2", "auto-group-3", "AUTO-GROUP-1"]

    try:
        # Step 1: Authenticate
        print_step(1, "Authenticate and Setup")
        token, response = auth.login()
        if not token:
            print(f"❌ Authentication failed: {response}")
            return 1
        print("✓ Authenticated successfully")

        # Cleanup any existing groups with our test names
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        if groups:
            for g in groups:
                if g["name"].lower() in [n.lower() for n in test_group_names]:
                    print(f"Cleaning up existing group: {g['name']}")
                    node_group_helper.delete_node_group(token, g["_id"])

        # Step 2: Auto-Registration with Single Group
        print_step(2, "Auto-Registration with Single Group")
        
        worker1_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        if not worker_manager.start_worker(worker1_name, "auto-group-1"):
            return 1
        
        print("Waiting for node to register (20s)...")
        time.sleep(20)
        
        # Verify node group creation
        groups, _ = node_group_helper.list_node_groups(token, filter_str="auto-group-1")
        group1 = next((g for g in groups if g["name"] == "auto-group-1"), None)
        if not group1:
            print("❌ Group 'auto-group-1' was not created")
            return 1
        print(f"✓ Group 'auto-group-1' created: {group1['_id']}")
        
        # Verify node assignment
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker1_node = next((n for n in nodes if n.get("name") == worker1_name), None)
        if not worker1_node:
            print(f"❌ Worker node {worker1_name} not found in registry")
            return 1
        
        worker1_id = worker1_node["_id"]
        if worker1_id not in group1.get("node_ids", []):
            print(f"❌ Worker {worker1_id} not assigned to group {group1['_id']}")
            print(f"Current node_ids: {group1.get('node_ids')}")
            return 1
        print(f"✓ Worker {worker1_name} correctly assigned to group")

        # Step 3: Auto-Registration with Multiple Groups
        print_step(3, "Auto-Registration with Multiple Groups")
        
        worker2_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        if not worker_manager.start_worker(worker2_name, "auto-group-2,auto-group-3"):
            return 1
        
        print("Waiting for node to register (20s)...")
        time.sleep(20)
        
        # Verify multiple groups creation
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        group2 = next((g for g in groups if g["name"] == "auto-group-2"), None)
        group3 = next((g for g in groups if g["name"] == "auto-group-3"), None)
        
        if not group2 or not group3:
            print(f"❌ Groups not created. group2: {bool(group2)}, group3: {bool(group3)}")
            return 1
        print("✓ Both groups 'auto-group-2' and 'auto-group-3' created")
        
        # Verify node assignment to all groups
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker2_node = next((n for n in nodes if n.get("name") == worker2_name), None)
        if not worker2_node:
            print(f"❌ Worker node {worker2_name} not found")
            return 1
        
        worker2_id = worker2_node["_id"]
        if worker2_id not in group2.get("node_ids", []) or worker2_id not in group3.get("node_ids", []):
            print(f"❌ Worker {worker2_id} not assigned to both groups")
            return 1
        print(f"✓ Worker {worker2_name} correctly assigned to both groups")

        # Step 4: Case-Insensitive Matching
        print_step(4, "Case-Insensitive Matching")
        
        worker3_name = f"test-worker-{uuid.uuid4().hex[:8]}"
        # Use different case for existing group
        if not worker_manager.start_worker(worker3_name, "AUTO-GROUP-1"):
            return 1
        
        print("Waiting for node to register (20s)...")
        time.sleep(20)
        
        # Verify no duplicate group created
        groups, _ = node_group_helper.list_node_groups(token, size=100)
        matching_groups = [g for g in groups if g["name"].lower() == "auto-group-1"]
        
        if len(matching_groups) > 1:
            print(f"❌ Duplicate groups found for 'auto-group-1': {[g['name'] for g in matching_groups]}")
            return 1
        
        group1_updated = matching_groups[0]
        nodes, _ = node_helper.list_nodes(token, size=100)
        worker3_node = next((n for n in nodes if n.get("name") == worker3_name), None)
        worker3_id = worker3_node["_id"]
        
        if worker3_id not in group1_updated.get("node_ids", []):
            print(f"❌ Worker {worker3_id} not assigned to existing group (case-insensitive)")
            return 1
        print("✓ Case-insensitive matching worked, no duplicate group created")

        # Step 5: Idempotency on Restart
        print_step(5, "Idempotency on Restart")
        
        print(f"Restarting worker {worker1_name}...")
        subprocess.run(["docker", "restart", worker1_name], capture_output=True)
        
        print("Waiting for node to re-register (20s)...")
        time.sleep(20)
        
        # Verify group membership remains and no duplicates
        group1_final, _ = node_group_helper.get_node_group(token, group1["_id"])
        node_ids = group1_final.get("node_ids", [])
        
        if node_ids.count(worker1_id) != 1:
            print(f"❌ Worker {worker1_id} should appear exactly once in group, found {node_ids.count(worker1_id)} times")
            return 1
        print("✓ Registration is idempotent, no duplicate assignments on restart")

        print("\n" + "=" * 80)
        print("✅ INT-005 Auto Node Group Registration Test PASSED")
        print("=" * 80)
        return 0

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        print("\n" + "=" * 80)
        print("Cleanup Phase")
        print("=" * 80)
        
        worker_manager.cleanup()
        
        if token:
            groups, _ = node_group_helper.list_node_groups(token, size=100)
            if groups:
                for g in groups:
                    if g["name"].lower() in [n.lower() for n in test_group_names]:
                        node_group_helper.delete_node_group(token, g["_id"])
                        print(f"✓ Cleaned up node group: {g['name']}")

if __name__ == "__main__":
    sys.exit(main())
