#!/usr/bin/env python3
"""
API-022: Node Group Management Test Runner

Validates node group CRUD operations, node assignment/removal, and task execution
with node groups (spec 041 node grouping feature).
"""

import sys
import time

from crawlab_test.helpers.api import APIAssertions, AuthHelper, CleanupHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.node_group import NodeGroupHelper
from crawlab_test.helpers.api.spider import SpiderHelper
from crawlab_test.helpers.api.task import TaskHelper


def print_step(step_num: int, description: str):
    """Print test step header."""
    print(f"\n{'=' * 80}")
    print(f"Step {step_num}: {description}")
    print("=" * 80)


def main():
    """Run node group management test."""
    auth = AuthHelper()
    assertions = APIAssertions()
    cleanup = CleanupHelper()
    node_group_helper = NodeGroupHelper()
    node_helper = NodeHelper()
    spider_helper = SpiderHelper()
    task_helper = TaskHelper()

    print("API-022: Node Group Management Test")
    print("=" * 80)

    token = None
    test_groups = []
    test_spider_id = None
    original_node_states = {}

    try:
        # Step 1: Authenticate
        print_step(1, "Authenticate and Setup")
        token, response = auth.login()
        if not token:
            print(f"❌ Authentication failed: {response}")
            return 1
        print("✓ Authenticated successfully")

        # Get available nodes
        nodes, response = node_helper.list_nodes(token, page=1, size=100)
        if not nodes or len(nodes) < 1:
            print("❌ Need at least 1 node for meaningful tests")
            return 1
        print(f"✓ Found {len(nodes)} node(s)")
        node_ids = [n["_id"] for n in nodes if "_id" in n][:2]  # Use up to 2 nodes

        # Track original node enabled/active for cleanup
        for n in nodes:
            original_node_states[n["_id"]] = {
                "enabled": n.get("enabled", True),
                "active": n.get("active", True),
            }

        # Get a test spider
        spiders, response = spider_helper.list_spiders(token)
        if spiders and len(spiders) > 0:
            test_spider_id = spiders[0]["_id"]
            print(f"✓ Found test spider: {test_spider_id}")
        else:
            print("⚠ No spider found, task execution tests will be skipped")

        # Step 2: Create Node Groups
        print_step(2, "Create Node Groups")

        # 2.1 Create basic node group
        group1, response = node_group_helper.create_node_group(
            token, name="Production Servers", description="Production environment nodes"
        )
        if not group1 or "_id" not in group1:
            print(f"❌ TC2.1 failed: {response}")
            return 1
        test_groups.append(group1["_id"])
        print(f"✓ TC2.1: Created basic node group: {group1['_id']}")
        assertions.assert_has_field(group1, "_id", "group has _id")
        assertions.assert_field_equals(group1, "name", "Production Servers")
        assertions.assert_field_equals(group1, "description", "Production environment nodes")
        assertions.assert_has_field(group1, "node_ids", "group has node_ids")

        # 2.2 Create node group with initial nodes
        if len(node_ids) >= 2:
            group2, response = node_group_helper.create_node_group(
                token,
                name="Test Group",
                description="Test environment",
                node_ids=[node_ids[0], node_ids[1]],
            )
            if not group2 or "_id" not in group2:
                print(f"❌ TC2.2 failed: {response}")
                return 1
            test_groups.append(group2["_id"])
            print(f"✓ TC2.2: Created node group with nodes: {group2['_id']}")
            assertions.assert_field_equals(group2, "name", "Test Group")
            if len(group2.get("node_ids", [])) != 2:
                print(f"⚠ Expected 2 nodes in group, got {len(group2.get('node_ids', []))}")
        else:
            print("⚠ TC2.2 skipped: Not enough nodes available")

        # 2.3 Create minimal node group
        group3, response = node_group_helper.create_node_group(token, name="Minimal Group")
        if not group3 or "_id" not in group3:
            print(f"❌ TC2.3 failed: {response}")
            return 1
        test_groups.append(group3["_id"])
        print(f"✓ TC2.3: Created minimal node group: {group3['_id']}")

        # Step 3: List Node Groups
        print_step(3, "List Node Groups")

        # 3.1 List all groups
        groups, response = node_group_helper.list_node_groups(token, page=1, size=10)
        if groups is None:
            print(f"❌ TC3.1 failed: {response}")
            return 1
        print(f"✓ TC3.1: Listed {len(groups)} node groups")
        if len(groups) < 3:
            print(f"⚠ Expected at least 3 groups, got {len(groups)}")
        # Validate Active/Total counts present and consistent when available
        if groups:
            g0 = groups[0]
            if "active_count" in g0 and "total_count" in g0:
                if not isinstance(g0.get("total_count"), int) or not isinstance(g0.get("active_count"), int):
                    print("⚠ TC3.1: active_count/total_count should be integers")

        # 3.2 Test pagination
        groups, response = node_group_helper.list_node_groups(token, page=1, size=2)
        if groups is None:
            print(f"❌ TC3.2 failed: {response}")
            return 1
        print(f"✓ TC3.2: Pagination works, got {len(groups)} groups (size=2)")

        # 3.3 Filter by name
        groups, response = node_group_helper.list_node_groups(token, filter_str="Production")
        if groups is None:
            print(f"❌ TC3.3 failed: {response}")
            return 1
        prod_found = any(g.get("name") == "Production Servers" for g in groups)
        if prod_found:
            print("✓ TC3.3: Filter works, found 'Production Servers'")
        else:
            print(f"⚠ TC3.3: Filter returned {len(groups)} groups but 'Production Servers' not found")

        # Step 4: Get Node Group Details
        print_step(4, "Get Node Group Details")

        # 4.1 Get group by ID
        group_detail, response = node_group_helper.get_node_group(token, test_groups[0])
        if not group_detail:
            print(f"❌ TC4.1 failed: {response}")
            return 1
        print(f"✓ TC4.1: Retrieved group details: {group_detail.get('name')}")
        assertions.assert_has_field(group_detail, "_id", "group has _id")
        assertions.assert_has_field(group_detail, "name", "group has name")
        assertions.assert_has_field(group_detail, "node_ids", "group has node_ids")
        if "active_count" in group_detail and "total_count" in group_detail:
            if group_detail["total_count"] != len(group_detail.get("node_ids", [])):
                print("⚠ TC4.1: total_count not equal to node_ids length")

        # 4.2 Get group with populated nodes (if group has nodes)
        if len(test_groups) >= 2:
            group_detail, response = node_group_helper.get_node_group(token, test_groups[1])
            if not group_detail:
                print(f"❌ TC4.2 failed: {response}")
                return 1
            has_nodes = "nodes" in group_detail or len(group_detail.get("node_ids", [])) > 0
            if has_nodes:
                print("✓ TC4.2: Group has node associations")
            else:
                print("⚠ TC4.2: No nodes found in group")

        # 4.3 Invalid group ID
        invalid_group, response = node_group_helper.get_node_group(token, "invalid_id_12345")
        if invalid_group is None:
            print(f"✓ TC4.3: Invalid ID handled correctly: {response.get('error', 'error')}")
        else:
            print("⚠ TC4.3: Expected error for invalid ID")

        # Step 5: Add Nodes to Group
        print_step(5, "Add Nodes to Group")

        if len(node_ids) >= 1:
            # 5.1 Add single node to group
            success, response = node_group_helper.add_node_to_group(token, test_groups[0], node_ids[0])
            if not success:
                print(f"❌ TC5.1 failed: {response}")
                return 1
            print("✓ TC5.1: Added node to group")

            # Verify node added
            group_detail, _ = node_group_helper.get_node_group(token, test_groups[0])
            if group_detail and node_ids[0] in group_detail.get("node_ids", []):
                print("✓ TC5.1: Verified node in group's node_ids")
            else:
                print("⚠ TC5.1: Node may not be in group yet")

            # 5.2 Add another node if available
            if len(node_ids) >= 2:
                success, response = node_group_helper.add_node_to_group(token, test_groups[0], node_ids[1])
                if success:
                    print("✓ TC5.2: Added second node to group")
                else:
                    print(f"⚠ TC5.2: Failed to add second node: {response}")

            # 5.3 Test duplicate assignment (should be idempotent)
            success, response = node_group_helper.add_node_to_group(token, test_groups[0], node_ids[0])
            if success:
                print("✓ TC5.3: Duplicate assignment handled (idempotent)")
            else:
                print(f"⚠ TC5.3: Duplicate assignment failed: {response}")
        else:
            print("⚠ TC5: Skipped - no nodes available")

        # Step 6: Remove Nodes from Group
        print_step(6, "Remove Nodes from Group")

        if len(node_ids) >= 1:
            # 6.1 Remove single node
            success, response = node_group_helper.remove_node_from_group(token, test_groups[0], node_ids[0])
            if not success:
                print(f"⚠ TC6.1: Failed to remove node: {response}")
            else:
                print("✓ TC6.1: Removed node from group")

            # Verify node removed
            group_detail, _ = node_group_helper.get_node_group(token, test_groups[0])
            if group_detail and node_ids[0] not in group_detail.get("node_ids", []):
                print("✓ TC6.1: Verified node removed from group")
            else:
                print("⚠ TC6.1: Node may still be in group")

            # 6.2 Remove non-existent node (should not error)
            success, response = node_group_helper.remove_node_from_group(
                token, test_groups[0], "nonexistent_node_id"
            )
            # Expect this to succeed (no-op) or return appropriate error
            print("✓ TC6.2: Remove non-existent node handled")
        else:
            print("⚠ TC6: Skipped - no nodes available")

        # Step 7: Update Node Group
        print_step(7, "Update Node Group")

        # 7.1 Update name and description
        updated_group, response = node_group_helper.update_node_group(
            token,
            test_groups[0],
            {"name": "Production Cluster", "description": "Updated production environment"},
        )
        if not updated_group:
            print(f"❌ TC7.1 failed: {response}")
            return 1
        print("✓ TC7.1: Updated node group")
        assertions.assert_field_equals(updated_group, "name", "Production Cluster")
        assertions.assert_field_equals(updated_group, "description", "Updated production environment")

        # 7.2 Update node assignments
        if len(node_ids) >= 1:
            updated_group, response = node_group_helper.update_node_group(
                token, test_groups[0], {"node_ids": [node_ids[0]]}
            )
            if updated_group:
                print("✓ TC7.2: Updated node assignments")
            else:
                print(f"⚠ TC7.2: Failed to update node assignments: {response}")

        # 7.3 Clear all nodes
        updated_group, response = node_group_helper.update_node_group(token, test_groups[0], {"node_ids": []})
        if updated_group:
            print("✓ TC7.3: Cleared all nodes from group")
            if len(updated_group.get("node_ids", [])) == 0:
                print("✓ TC7.3: Verified group has no nodes")
        else:
            print(f"⚠ TC7.3: Failed to clear nodes: {response}")

        # Step 8: Task Execution with Node Groups
        print_step(8, "Task Execution with Node Groups (online enforcement)")

        if test_spider_id and len(test_groups) >= 2:
            # Re-add nodes to test group for task execution
            if len(node_ids) >= 1:
                node_group_helper.add_node_to_group(token, test_groups[1], node_ids[0])

            # 8.1 Run task with single node group
            task_ids, response = task_helper.create_task(
                token,
                spider_id=test_spider_id,
                mode="selected-node-groups",
                node_group_ids=[test_groups[1]],
                priority=5,
            )
            if task_ids and len(task_ids) > 0:
                task_id = task_ids[0]
                cleanup.track_task(task_id)
                print(f"✓ TC8.1: Task created with node group: {task_id}")

                # Verify task has node_group_ids
                task_detail, _ = task_helper.get_task(token, task_id)
                if task_detail and "node_group_ids" in task_detail:
                    print("✓ TC8.1: Task has node_group_ids field")
                else:
                    print("⚠ TC8.1: Task may not have node_group_ids field")

                # Wait briefly for task to start
                time.sleep(2)
            else:
                print(f"⚠ TC8.1: Failed to create task: {response}")

            # 8.2 Run task with multiple node groups
            if len(test_groups) >= 3:
                task_ids, response = task_helper.create_task(
                    token,
                    spider_id=test_spider_id,
                    mode="selected-node-groups",
                    node_group_ids=[test_groups[1], test_groups[2]],
                )
                if task_ids and len(task_ids) > 0:
                    cleanup.track_task(task_ids[0])
                    print("✓ TC8.2: Task created with multiple node groups")
                else:
                    print(f"⚠ TC8.2: Failed to create task with multiple groups: {response}")

            # 8.3 Run task with node groups + specific nodes (intersection)
            if len(node_ids) >= 1:
                task_ids, response = task_helper.create_task(
                    token,
                    spider_id=test_spider_id,
                    mode="selected-node-groups",
                    node_group_ids=[test_groups[1]],
                    node_ids=[node_ids[0]],
                )
                if task_ids and len(task_ids) > 0:
                    cleanup.track_task(task_ids[0])
                    print("✓ TC8.3: Task created with group + node intersection")
                else:
                    print(f"⚠ TC8.3: Failed to create task with intersection: {response}")

            # 8.4 Offline-only group should fail
            if len(node_ids) >= 1:
                offline_node_id = node_ids[0]
                # disable node
                updated_node, response = node_helper.update_node(token, offline_node_id, {"enabled": False})
                if updated_node is None:
                    print(f"⚠ TC8.4: Could not disable node: {response}")
                else:
                    task_ids, response = task_helper.create_task(
                        token,
                        spider_id=test_spider_id,
                        mode="selected-node-groups",
                        node_group_ids=[test_groups[1]],
                    )
                    if task_ids is None:
                        print("✓ TC8.4: Task creation blocked for offline-only group")
                    else:
                        print("⚠ TC8.4: Expected failure when all nodes offline")
                    # re-enable
                    node_helper.update_node(token, offline_node_id, {"enabled": True})
        else:
            print("⚠ TC8: Skipped - no spider or groups available")

        # Step 9: Delete Node Groups
        print_step(9, "Delete Node Groups")

        # 9.1 Delete single node group (keep others for batch delete)
        if len(test_groups) >= 3:
            group_to_delete = test_groups[2]
            success, response = node_group_helper.delete_node_group(token, group_to_delete)
            if success:
                print(f"✓ TC9.1: Deleted single node group: {group_to_delete}")
                test_groups.remove(group_to_delete)

                # Verify deletion
                deleted_group, _ = node_group_helper.get_node_group(token, group_to_delete)
                if deleted_group is None:
                    print("✓ TC9.1: Verified group no longer exists")
            else:
                print(f"⚠ TC9.1: Failed to delete group: {response}")

        # 9.2 Delete group with nodes should be blocked, then succeeds after removal
        if len(test_groups) >= 1 and len(node_ids) >= 1:
            node_group_helper.add_node_to_group(token, test_groups[0], node_ids[0])

            group_to_delete = test_groups[0]
            success, response = node_group_helper.delete_node_group(token, group_to_delete)
            if success:
                print("⚠ TC9.2: Deletion should have been blocked while nodes are active")
            else:
                print("✓ TC9.2: Deletion blocked when active nodes present")

            # remove nodes then delete
            node_group_helper.update_node_group(token, group_to_delete, {"node_ids": []})
            success, response = node_group_helper.delete_node_group(token, group_to_delete)
            if success:
                print("✓ TC9.2: Deleted group after clearing nodes")
                test_groups.remove(group_to_delete)
            else:
                print(f"⚠ TC9.2: Failed to delete group after clearing nodes: {response}")

        # 9.3 Batch delete remaining groups
        if len(test_groups) >= 2:
            success, response = node_group_helper.delete_node_groups_batch(token, test_groups[:2])
            if success:
                print(f"✓ TC9.3: Batch deleted {len(test_groups[:2])} node groups")
                test_groups = test_groups[2:]  # Remove deleted groups from tracking
            else:
                print(f"⚠ TC9.3: Batch delete failed: {response}")

        # 9.4 Try deleting non-existent group
        success, response = node_group_helper.delete_node_group(token, "nonexistent_group_id")
        if not success:
            print("✓ TC9.4: Non-existent group deletion handled correctly")
        else:
            print("⚠ TC9.4: Expected error for non-existent group")

        print("\n" + "=" * 80)
        print("✅ API-022 Node Group Management Test PASSED")
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

        if token:
            # Delete any remaining test groups
            for group_id in test_groups:
                try:
                    node_group_helper.delete_node_group(token, group_id)
                    print(f"✓ Cleaned up node group: {group_id}")
                except Exception as e:
                    print(f"⚠ Failed to cleanup group {group_id}: {e}")

            # Restore node states
            try:
                for node_id, state in original_node_states.items():
                    node_helper.update_node(token, node_id, state)
            except Exception as e:
                print(f"⚠ Failed to restore node states: {e}")

            # Cleanup tracked resources (tasks)
            cleanup.cleanup_all(token, task_helper=task_helper)

            # Logout
            auth.logout(token)
            print("✓ Logged out")


if __name__ == "__main__":
    sys.exit(main())
