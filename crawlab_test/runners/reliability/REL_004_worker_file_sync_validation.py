#!/usr/bin/env python3
"""
REL-004 - Worker Node File Sync Validation Test Runner

Validates that spider files are correctly synchronized to worker nodes via gRPC
before task execution. Tests the core file sync mechanism to prevent missing file errors.
"""

import sys
import time
from typing import Dict

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.spider import SpiderHelper
from crawlab_test.helpers.api.task import TaskHelper
from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.utils import setup_logging


def verify_grpc_available(logger) -> bool:
    """Verify gRPC service is accessible"""
    logger.info("Step 1: Verifying gRPC Service Availability")

    # Check gRPC port on master
    master = "crawlab_master"
    # Try multiple methods to check if port 9666 is listening
    port_check = docker_utils.exec_command(
        master, "(netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null || true) | grep ':9666'", timeout=5
    )

    if port_check["exit_code"] == 0 and "9666" in port_check["output"]:
        logger.info("  ✓ gRPC server listening on port 9666")
    else:
        # Fallback: try direct connection test
        logger.warning("  ⚠️  Could not detect port via netstat/ss, trying connection test...")
        conn_test = docker_utils.exec_command(
            master,
            "timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/9666' 2>&1 && echo 'open' || echo 'closed'",
            timeout=5,
        )
        if "open" in conn_test["output"]:
            logger.info("  ✓ gRPC server accessible on port 9666 (connection test)")
        else:
            logger.error("  ✗ gRPC server not accessible on port 9666")
            return False

    # Check worker can reach master
    worker = "crawlab_worker"
    conn_check = docker_utils.exec_command(
        worker, "nc -zv master 9666 2>&1 || timeout 2 bash -c 'cat < /dev/null > /dev/tcp/master/9666' 2>&1", timeout=5
    )

    if conn_check["exit_code"] == 0:
        logger.info("  ✓ Worker can connect to master:9666")
        return True
    else:
        logger.error(f"  ✗ Worker cannot connect to master:9666: {conn_check['output']}")
        return False


def create_test_spider_with_files(token: str, spider_helper: SpiderHelper, logger) -> str:
    """Create spider and upload test files"""
    logger.info("\nStep 2-4: Creating Spider and Uploading Files")

    # Create spider (omit project_id as it must be a valid ObjectID or empty)
    spider_id, response = spider_helper.create_spider(
        token,
        name="rel-004-file-sync-test",
        cmd="python main.py",
        description="REL-004: Tests file sync to worker nodes",
    )

    if not spider_id:
        raise RuntimeError(f"Failed to create spider: {response}")

    logger.info(f"  ✓ Created spider: {spider_id}")

    # File 1: main.py - validation script
    main_py_content = """#!/usr/bin/env python
import os
import sys

print("=== REL-004: File Sync Validation ===")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {sorted(os.listdir(os.getcwd()))}")

# List of expected files
expected_files = ["main.py", "config.json", "utils.py", "requirements.txt"]
missing_files = []

for filename in expected_files:
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"✓ File synced: {filename} ({size} bytes)")
    else:
        print(f"✗ File missing: {filename}")
        missing_files.append(filename)

if missing_files:
    print(f"\\n❌ SYNC FAILED: {len(missing_files)} files missing: {missing_files}")
    sys.exit(1)
else:
    print(f"\\n✅ SYNC SUCCESS: All {len(expected_files)} files synced correctly")
    print("Spider execution complete.")
"""

    success, _ = spider_helper.save_file(token, spider_id, "main.py", main_py_content)
    if not success:
        raise RuntimeError("Failed to upload main.py")
    logger.info("  ✓ Uploaded main.py")

    # File 2: config.json
    config_content = '{"test": "rel-004", "version": "1.0.0", "sync_mode": "grpc"}'
    success, _ = spider_helper.save_file(token, spider_id, "config.json", config_content)
    if not success:
        raise RuntimeError("Failed to upload config.json")
    logger.info("  ✓ Uploaded config.json")

    # File 3: utils.py
    utils_content = '''"""Utility functions for REL-004 test"""

def validate_files():
    return True

def get_version():
    return "1.0.0"
'''
    success, _ = spider_helper.save_file(token, spider_id, "utils.py", utils_content)
    if not success:
        raise RuntimeError("Failed to upload utils.py")
    logger.info("  ✓ Uploaded utils.py")

    # File 4: requirements.txt
    requirements_content = "# No external dependencies for this test"
    success, _ = spider_helper.save_file(token, spider_id, "requirements.txt", requirements_content)
    if not success:
        raise RuntimeError("Failed to upload requirements.txt")
    logger.info("  ✓ Uploaded requirements.txt")

    logger.info("  ✓ Total: 4 files uploaded")

    return spider_id


def verify_files_on_master(spider_id: str, logger) -> bool:
    """Verify files exist on master node"""
    logger.info("\nStep 5: Verifying Files on Master Node")

    master = "crawlab_master"
    ls_result = docker_utils.exec_command(
        master,
        f"ls -lh /app/tmp/{spider_id}/ 2>/dev/null || ls -lh /app/.crawlab/tmp/{spider_id}/ 2>/dev/null",
        timeout=5,
    )

    if ls_result["exit_code"] != 0:
        logger.error("  ✗ Spider directory not found on master")
        return False

    # Count files
    count_result = docker_utils.exec_command(
        master,
        f"find /app/tmp/{spider_id}/ -type f 2>/dev/null | wc -l || find /app/.crawlab/tmp/{spider_id}/ -type f 2>/dev/null | wc -l",
        timeout=5,
    )

    file_count = int(count_result["output"].strip()) if count_result["exit_code"] == 0 else 0

    if file_count == 4:
        logger.info("  ✓ All 4 files present on master")
        logger.debug(f"\n{ls_result['output']}")
        return True
    else:
        logger.error(f"  ✗ Expected 4 files, found {file_count}")
        return False


def run_task_and_wait(token: str, spider_id: str, task_helper: TaskHelper, logger) -> Dict:
    """Create task and wait for completion"""
    logger.info("\nStep 6-7: Creating and Monitoring Task")

    # Create task
    task_ids, response = task_helper.create_task(token, spider_id)
    if not task_ids or len(task_ids) == 0:
        logger.error(f"  ✗ Failed to create task: {response}")
        return {"success": False, "error": "Task creation failed"}

    task_id = task_ids[0]
    logger.info(f"  ✓ Created task: {task_id}")

    # Wait for completion (max 60 seconds)
    logger.info("  Monitoring task execution...")
    max_attempts = 30

    for attempt in range(1, max_attempts + 1):
        time.sleep(2)

        task_data, _ = task_helper.get_task(token, task_id)
        if not task_data:
            logger.warning(f"  Could not fetch task info (attempt {attempt})")
            continue

        status = task_data.get("status", "unknown")

        logger.debug(f"  [{attempt}/{max_attempts}] Task status: {status}")

        if status in ["finished", "error"]:
            duration = attempt * 2
            logger.info(f"  ✓ Task completed in {duration} seconds with status: {status}")
            return {"success": True, "task_id": task_id, "status": status, "duration": duration, "task_info": task_data}

    logger.error("  ✗ Task did not complete within 60 seconds")
    return {"success": False, "task_id": task_id, "error": "Timeout", "status": "timeout"}


def validate_task_results(token: str, task_result: Dict, task_helper: TaskHelper, logger) -> bool:
    """Validate task completed successfully with all files synced"""
    logger.info("\nStep 8-10: Validating Task Results")

    if not task_result.get("success"):
        logger.error("  ✗ Task execution failed")
        return False

    task_id = task_result["task_id"]
    status = task_result["status"]

    # Check status
    if status != "finished":
        logger.error(f"  ✗ Task status is '{status}', expected 'finished'")
        return False

    logger.info(f"  ✓ Task status: {status}")

    # Get and analyze logs
    logs, _ = task_helper.get_task_logs(token, task_id)

    if not logs:
        logger.error("  ✗ Could not retrieve task logs")
        return False

    # Check for success marker
    if "✅ SYNC SUCCESS" in logs:
        logger.info("  ✓ Task logs show sync success")
    else:
        logger.error("  ✗ Task logs missing sync success marker")
        logger.debug(f"\nLogs:\n{logs}")
        return False

    # Check for file sync confirmations
    expected_files = ["main.py", "config.json", "utils.py", "requirements.txt"]
    synced_files = []
    missing_files = []

    for filename in expected_files:
        if f"✓ File synced: {filename}" in logs:
            synced_files.append(filename)
        else:
            missing_files.append(filename)

    if missing_files:
        logger.error(f"  ✗ Missing files in logs: {missing_files}")
        return False

    logger.info(f"  ✓ All {len(expected_files)} files confirmed synced in logs")

    # Check for error markers
    if "✗ File missing:" in logs or "❌ SYNC FAILED" in logs:
        logger.error("  ✗ Task logs contain file missing errors")
        logger.debug(f"\nLogs:\n{logs}")
        return False

    # Check master logs for gRPC activity
    logger.info("  Checking master logs for gRPC sync activity...")
    master = "crawlab_master"
    master_logs = docker_utils.exec_command(
        master,
        "tail -100 /proc/1/fd/1 2>/dev/null | grep -E 'StreamFileScan|file scan request|file synchronization'",
        timeout=5,
    )

    if master_logs["exit_code"] == 0 and master_logs["output"].strip():
        logger.info("  ✓ Master logs show gRPC sync activity")
        logger.debug(f"\n{master_logs['output'][:500]}")
    else:
        logger.warning("  ⚠️  Could not confirm gRPC sync activity in master logs")

    return True


def run() -> bool:
    """Main test execution"""
    logger = setup_logging("REL-004")
    logger.info("=" * 60)
    logger.info("REL-004: Worker Node File Sync Validation")
    logger.info("=" * 60)

    # Initialize helpers
    auth_helper = AuthHelper()
    spider_helper = SpiderHelper()
    task_helper = TaskHelper()

    token = None
    spider_id = None

    try:
        # Step 1: Verify gRPC
        if not verify_grpc_available(logger):
            logger.error("\n❌ TEST FAILED: gRPC service not available")
            return False

        # Authenticate
        logger.info("\nAuthenticating...")
        token, response = auth_helper.login("admin", "admin")
        if not token:
            logger.error(f"  ✗ Authentication failed: {response}")
            return False
        logger.info("  ✓ Authentication successful")

        # Steps 2-4: Create spider and upload files
        spider_id = create_test_spider_with_files(token, spider_helper, logger)

        # Step 5: Verify files on master
        if not verify_files_on_master(spider_id, logger):
            logger.error("\n❌ TEST FAILED: Files not present on master")
            return False

        # Steps 6-7: Run task
        task_result = run_task_and_wait(token, spider_id, task_helper, logger)

        # Steps 8-10: Validate results
        if not validate_task_results(token, task_result, task_helper, logger):
            logger.error("\n❌ TEST FAILED: Task validation failed")
            return False

        logger.info("\n" + "=" * 60)
        logger.info("✅ TEST PASSED: All files synced successfully to worker")
        logger.info("=" * 60)
        return True

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
