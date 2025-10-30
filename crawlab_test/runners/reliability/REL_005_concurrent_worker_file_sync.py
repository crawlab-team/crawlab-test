#!/usr/bin/env python3
"""
REL-005 - Concurrent Worker File Sync Reliability Test Runner

Validates that file synchronization works correctly when multiple worker nodes
request files simultaneously. Tests gRPC sync under concurrent load.
"""

import sys
import time
from typing import Dict, List

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.spider import SpiderHelper
from crawlab_test.helpers.api.task import TaskHelper
from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.utils import setup_logging


def verify_multi_worker_setup(token: str, node_helper: NodeHelper, logger) -> Dict:
    """Verify at least 2 worker nodes are available"""
    logger.info("Step 1: Verifying Multi-Worker Setup")

    nodes, _ = node_helper.list_nodes(token, size=100)
    if not nodes:
        nodes = []
    workers = [node for node in nodes if not node.get("is_master", False)]

    worker_count = len(workers)
    logger.info(f"  Found {worker_count} worker nodes")

    for worker in workers:
        status = worker.get("status", "unknown")
        key = worker.get("key", "unknown")
        logger.info(f"    - {key}: {status}")

    if worker_count < 2:
        logger.warning(f"  ⚠️  Only {worker_count} worker(s) available, test requires 2+ for full validation")
        logger.warning("  Test will proceed but won't fully test concurrent scenarios")

    return {"worker_count": worker_count, "workers": workers, "sufficient": worker_count >= 2}


def create_spider_with_multiple_files(token: str, spider_helper: SpiderHelper, logger) -> str:
    """Create spider with multiple files for concurrent sync testing"""
    logger.info("\nStep 2-4: Creating Spider with Multiple Files")

    # Create spider (omit project_id as it must be a valid ObjectID or empty)
    spider_id, response = spider_helper.create_spider(
        token,
        name="rel-005-concurrent-sync-test",
        cmd="python main.py",
        description="REL-005: Tests concurrent file sync to multiple workers",
    )

    if not spider_id:
        raise RuntimeError(f"Failed to create spider: {response}")

    logger.info(f"  ✓ Created spider: {spider_id}")

    # Upload 10 module files
    for i in range(1, 11):
        content = f'# Module {i}\ndef function_{i}():\n    return "{i}"\n'
        success, _ = spider_helper.save_file(token, spider_id, f"module_{i}.py", content)
        if not success:
            raise RuntimeError(f"Failed to upload module_{i}.py")

    logger.info("  ✓ Uploaded 10 module files (module_1.py to module_10.py)")

    # Main validation script
    main_py_content = """#!/usr/bin/env python
import os
import sys
import socket

print(f"=== REL-005: Concurrent File Sync Test ===")
print(f"Worker: {socket.gethostname()}")
print(f"Working directory: {os.getcwd()}")

expected_files = ["main.py"] + [f"module_{i}.py" for i in range(1, 11)]
missing_files = []
all_files = sorted(os.listdir(os.getcwd()))

print(f"\\nExpected {len(expected_files)} files")
print(f"Found {len(all_files)} files: {all_files}")

for filename in expected_files:
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"✓ {filename} ({size} bytes)")
    else:
        print(f"✗ MISSING: {filename}")
        missing_files.append(filename)

if missing_files:
    print(f"\\n❌ FAIL: {len(missing_files)} files missing: {missing_files}")
    sys.exit(1)
else:
    print(f"\\n✅ SUCCESS: All {len(expected_files)} files synced correctly on {socket.gethostname()}")
"""

    success, _ = spider_helper.save_file(token, spider_id, "main.py", main_py_content)
    if not success:
        raise RuntimeError("Failed to upload main.py")
    logger.info("  ✓ Uploaded main.py")
    logger.info("  ✓ Total: 11 files")

    return spider_id


def verify_files_on_master(spider_id: str, logger) -> bool:
    """Verify all files exist on master node"""
    logger.info("\nStep 5: Verifying Files on Master")

    # Detect container name dynamically
    master_result = docker_utils.exec_command("crawlab_master", "echo test", timeout=2)
    if master_result["exit_code"] != 0:
        master_result = docker_utils.exec_command("crawlab_dev_master", "echo test", timeout=2)
        master = "crawlab_dev_master" if master_result["exit_code"] == 0 else "crawlab_master"
    else:
        master = "crawlab_master"

    # Spider files are stored in ~/crawlab_workspace/{spider_id}/
    # Try multiple possible paths
    paths_to_check = [
        f"/root/crawlab_workspace/{spider_id}/",
        f"~/crawlab_workspace/{spider_id}/",
        f"/app/tmp/{spider_id}/",
        f"/app/.crawlab/tmp/{spider_id}/",
    ]

    spider_dir = None
    for path in paths_to_check:
        test_result = docker_utils.exec_command(
            master,
            f"test -d {path} && echo 'exists' || echo 'not found'",
            timeout=5,
        )
        if "exists" in test_result["output"]:
            spider_dir = path
            logger.debug(f"  Found spider directory: {spider_dir}")
            break

    if not spider_dir:
        logger.error("  ✗ Spider directory not found on master")
        logger.debug(f"  Tried paths: {paths_to_check}")
        return False

    count_result = docker_utils.exec_command(
        master,
        f"find {spider_dir} -type f 2>/dev/null | wc -l",
        timeout=5,
    )

    file_count = int(count_result["output"].strip()) if count_result["exit_code"] == 0 else 0

    if file_count == 11:
        logger.info("  ✓ All 11 files present on master")
        # List files for debugging
        ls_result = docker_utils.exec_command(master, f"ls -1 {spider_dir}", timeout=5)
        logger.debug(f"  Files: {ls_result['output'].strip()}")
        return True
    else:
        logger.error(f"  ✗ Expected 11 files, found {file_count}")
        # Show what's in the directory
        ls_result = docker_utils.exec_command(master, f"ls -lha {spider_dir}", timeout=5)
        logger.debug(f"  Directory contents:\n{ls_result['output']}")
        return False


def create_concurrent_tasks(token: str, spider_id: str, task_count: int, task_helper: TaskHelper, logger) -> List[str]:
    """Create multiple tasks simultaneously"""
    logger.info(f"\nStep 6: Creating {task_count} Tasks Simultaneously")

    task_ids = []

    for i in range(task_count):
        try:
            ids, response = task_helper.create_task(token, spider_id)
            if ids and len(ids) > 0:
                task_id = ids[0]
                task_ids.append(task_id)
                logger.info(f"  ✓ Task {i + 1}: {task_id}")
            else:
                logger.warning(f"  ⚠️  Task {i + 1}: Failed to get task ID: {response}")
        except Exception as e:
            logger.error(f"  ✗ Task {i + 1}: Failed to create - {e}")

    logger.info(f"  Created {len(task_ids)}/{task_count} tasks")
    return task_ids


def monitor_tasks_completion(
    token: str, task_ids: List[str], task_helper: TaskHelper, logger, timeout: int = 120
) -> Dict:
    """Monitor all tasks until completion"""
    logger.info(f"\nStep 7: Monitoring {len(task_ids)} Tasks (timeout: {timeout}s)")

    start_time = time.time()
    max_attempts = timeout // 2
    completed_tasks = set()

    for attempt in range(1, max_attempts + 1):
        time.sleep(2)

        all_done = True
        for task_id in task_ids:
            if task_id in completed_tasks:
                continue

            try:
                task_data, _ = task_helper.get_task(token, task_id)
                if not task_data:
                    all_done = False
                    continue
                status = task_data.get("status", "unknown")

                if status in ["finished", "error"]:
                    completed_tasks.add(task_id)
                else:
                    all_done = False
            except Exception as e:
                logger.debug(f"  Error checking task {task_id}: {e}")
                all_done = False

        if all_done:
            duration = time.time() - start_time
            logger.info(f"  ✓ All tasks completed in {duration:.1f}s (attempt {attempt}/{max_attempts})")
            return {"success": True, "duration": duration, "completed": len(task_ids)}

        if attempt % 10 == 0:
            logger.info(f"  [{attempt}/{max_attempts}] {len(completed_tasks)}/{len(task_ids)} completed...")

    duration = time.time() - start_time
    logger.error(f"  ✗ Timeout: {len(completed_tasks)}/{len(task_ids)} completed after {duration:.1f}s")
    return {"success": False, "duration": duration, "completed": len(completed_tasks), "timeout": True}


def validate_all_tasks(token: str, task_ids: List[str], task_helper: TaskHelper, logger) -> Dict:
    """Validate all tasks succeeded with complete file sync"""
    logger.info(f"\nStep 8-9: Validating {len(task_ids)} Task Results")

    results = {"success_count": 0, "fail_count": 0, "missing_files": [], "tasks": []}

    for i, task_id in enumerate(task_ids, 1):
        try:
            task_data, _ = task_helper.get_task(token, task_id)
            if not task_data:
                logger.error(f"  ✗ Task {i}: Could not fetch task info")
                results["fail_count"] += 1
                continue

            status = task_data.get("status", "unknown")
            node = task_data.get("node_key", "unknown")

            logs, _ = task_helper.get_task_logs(token, task_id)

            task_result = {
                "task_id": task_id,
                "status": status,
                "node": node,
                "success": False,
                "has_logs": bool(logs),
            }

            if logs and "✅ SUCCESS" in logs:
                logger.info(f"  ✓ Task {i} ({node}): SUCCESS")
                results["success_count"] += 1
                task_result["success"] = True
            else:
                logger.error(f"  ✗ Task {i} ({node}): FAILED (status: {status})")
                results["fail_count"] += 1

                if logs:
                    # Check for missing files
                    if "✗ MISSING:" in logs:
                        missing = [line.strip() for line in logs.split("\n") if "✗ MISSING:" in line]
                        logger.error(f"      Missing files: {missing[:3]}")
                        task_result["missing_files"] = missing
                        results["missing_files"].extend(missing)

            results["tasks"].append(task_result)

        except Exception as e:
            logger.error(f"  ✗ Task {i}: Error validating - {e}")
            results["fail_count"] += 1

    logger.info(f"\n  Results: {results['success_count']} succeeded, {results['fail_count']} failed")

    return results


def check_grpc_activity(spider_id: str, logger):
    """Check master logs for gRPC sync activity"""
    logger.info("\nStep 10: Checking gRPC Sync Server Activity")

    # Detect container name dynamically
    master_result = docker_utils.exec_command("crawlab_master", "echo test", timeout=2)
    if master_result["exit_code"] != 0:
        master_result = docker_utils.exec_command("crawlab_dev_master", "echo test", timeout=2)
        master = "crawlab_dev_master" if master_result["exit_code"] == 0 else "crawlab_master"
    else:
        master = "crawlab_master"

    logs_cmd = (
        "tail -200 /proc/1/fd/1 2>/dev/null | "
        f"grep -E 'StreamFileScan|file scan request|cached|deduplication|{spider_id}' | "
        "tail -20"
    )

    result = docker_utils.exec_command(master, logs_cmd, timeout=5)

    if result["exit_code"] == 0 and result["output"].strip():
        logger.info("  ✓ Master logs show gRPC sync activity")
        logger.debug(f"\n{result['output'][:500]}")
    else:
        logger.warning("  ⚠️  Could not confirm gRPC sync activity in master logs")


def run() -> bool:
    """Main test execution"""
    logger = setup_logging("REL-005")
    logger.info("=" * 60)
    logger.info("REL-005: Concurrent Worker File Sync Reliability")
    logger.info("=" * 60)

    # Initialize helpers
    auth_helper = AuthHelper()
    node_helper = NodeHelper()
    spider_helper = SpiderHelper()
    task_helper = TaskHelper()

    token = None
    spider_id = None

    try:
        # Authenticate
        logger.info("\nAuthenticating...")
        token, response = auth_helper.login("admin", "admin")
        if not token:
            logger.error(f"  ✗ Authentication failed: {response}")
            return False
        logger.info("  ✓ Authentication successful")

        # Step 1: Verify multi-worker setup
        worker_info = verify_multi_worker_setup(token, node_helper, logger)

        # Steps 2-4: Create spider with multiple files
        spider_id = create_spider_with_multiple_files(token, spider_helper, logger)

        # Step 5: Verify files on master
        if not verify_files_on_master(spider_id, logger):
            logger.error("\n❌ TEST FAILED: Files not present on master")
            return False

        # Step 6: Create concurrent tasks
        task_count = 4 if worker_info["sufficient"] else 2
        task_ids = create_concurrent_tasks(token, spider_id, task_count, task_helper, logger)

        if len(task_ids) == 0:
            logger.error("\n❌ TEST FAILED: Could not create any tasks")
            return False

        # Step 7: Monitor completion
        completion = monitor_tasks_completion(token, task_ids, task_helper, logger)

        if not completion["success"]:
            logger.error("\n❌ TEST FAILED: Tasks did not complete in time")
            return False

        # Steps 8-9: Validate all tasks
        validation = validate_all_tasks(token, task_ids, task_helper, logger)

        # Step 10: Check gRPC activity
        check_grpc_activity(spider_id, logger)

        # Determine test success
        if validation["fail_count"] == 0 and validation["success_count"] == len(task_ids):
            logger.info("\n" + "=" * 60)
            logger.info(f"✅ TEST PASSED: All {len(task_ids)} tasks synced files successfully")
            logger.info("=" * 60)
            return True
        else:
            logger.error("\n" + "=" * 60)
            logger.error(f"❌ TEST FAILED: {validation['fail_count']}/{len(task_ids)} tasks failed file sync")
            logger.error("=" * 60)
            return False

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: Unexpected error: {e}", exc_info=True)
        return False

    finally:
        # Cleanup
        if token and spider_id and "spider_helper" in locals():
            try:
                logger.info("\nCleaning up...")
                success, _ = spider_helper.delete_spider(token, spider_id)
                if success:
                    logger.info("  ✓ Deleted test spider")
                else:
                    logger.warning("  ⚠️  Failed to delete test spider")
            except Exception as e:
                logger.warning(f"  ⚠️  Cleanup failed: {e}")


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
