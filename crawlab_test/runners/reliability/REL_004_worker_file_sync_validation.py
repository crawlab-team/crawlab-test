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
    """Verify gRPC service is accessible using container-friendly methods"""
    logger.info("Step 1: Verifying gRPC Service Availability")

    # Use docker_utils to find containers dynamically
    docker_helper = docker_utils.DockerHelper()

    master_container = docker_helper.find_master_container()
    if not master_container:
        logger.error("  ✗ Could not find crawlab master container")
        return False

    master = master_container["Names"]
    logger.debug(f"  Using master container: {master}")

    # Find worker container
    containers = docker_helper.find_crawlab_containers()
    worker = None
    for container in containers:
        names = container.get("Names", "")
        if "worker" in names.lower():
            worker = names
            break

    if not worker:
        logger.error("  ✗ Could not find crawlab worker container")
        return False

    logger.debug(f"  Using worker container: {worker}")

    # Method 1: Use Python to check port (works in sh and bash)
    # The crawlab containers have Python installed
    python_check = docker_utils.exec_command(
        master,
        "python3 -c 'import socket; s=socket.socket(); s.settimeout(2); s.connect((\"localhost\",9666)); s.close(); print(\"open\")' 2>/dev/null || echo 'closed'",
        timeout=5,
    )

    if "open" in python_check["output"]:
        logger.info("  ✓ gRPC server accessible on port 9666")
    else:
        # Method 2: Try bash if available (for systems with bash)
        bash_check = docker_utils.exec_command(
            master,
            "bash -c 'timeout 2 cat < /dev/null > /dev/tcp/localhost/9666 2>&1' && echo 'open' || echo 'closed'",
            timeout=5,
        )

        if "open" in bash_check["output"]:
            logger.info("  ✓ gRPC server accessible on port 9666 (bash test)")
        else:
            # Method 3: Check process list for port 9666
            ps_check = docker_utils.exec_command(
                master,
                "ps aux | grep -E 'server.*9666|:9666' | grep -v grep",
                timeout=5,
            )

            if "9666" in ps_check["output"]:
                logger.info("  ✓ gRPC server process found (port 9666)")
            else:
                logger.error("  ✗ gRPC server not accessible on port 9666")
                logger.debug(f"    Python check: {python_check['output']}")
                logger.debug(f"    Bash check: {bash_check['output']}")
                logger.debug(f"    Process check: {ps_check['output']}")
                return False

    # Check worker can reach master
    logger.debug(f"  Using worker container: {worker}")

    # Method 1: Python socket test (most reliable across containers)
    worker_python = docker_utils.exec_command(
        worker,
        "python3 -c 'import socket; s=socket.socket(); s.settimeout(2); s.connect((\"master\",9666)); s.close(); print(\"connected\")' 2>/dev/null || echo 'failed'",
        timeout=5,
    )

    if "connected" in worker_python["output"]:
        logger.info("  ✓ Worker can connect to master:9666")
        return True
    else:
        # Method 2: Try bash TCP test if available
        worker_bash = docker_utils.exec_command(
            worker,
            "bash -c 'timeout 2 cat < /dev/null > /dev/tcp/master/9666 2>&1' && echo 'connected' || echo 'failed'",
            timeout=5,
        )

        if "connected" in worker_bash["output"] or worker_bash["exit_code"] == 0:
            logger.info("  ✓ Worker can connect to master:9666 (bash test)")
            return True
        else:
            # Method 3: Try netcat if available
            nc_check = docker_utils.exec_command(
                worker, "nc -zv master 9666 2>&1 || echo 'netcat not available'", timeout=5
            )

            if "succeeded" in nc_check["output"] or ("open" in nc_check["output"] and nc_check["exit_code"] == 0):
                logger.info("  ✓ Worker can connect to master:9666 (netcat)")
                return True
            else:
                logger.error("  ✗ Worker cannot connect to master:9666")
                logger.debug(f"    Python test: {worker_python['output']}")
                logger.debug(f"    Bash test: {worker_bash['output']}")
                logger.debug(f"    Netcat test: {nc_check['output']}")
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

    # Use docker_utils to find master container dynamically
    docker_helper = docker_utils.DockerHelper()
    master_container = docker_helper.find_master_container()

    if not master_container:
        logger.error("  ✗ Could not find crawlab master container")
        return False

    master = master_container["Names"]
    logger.debug(f"  Using master container: {master}")

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
        ls_result = docker_utils.exec_command(
            master,
            f"ls -lh {path} 2>/dev/null",
            timeout=5,
        )
        if ls_result["exit_code"] == 0:
            spider_dir = path
            logger.debug(f"  Found spider directory: {spider_dir}")
            break

    if not spider_dir:
        logger.error("  ✗ Spider directory not found on master")
        logger.debug(f"  Tried paths: {paths_to_check}")
        return False

    # Count files
    count_result = docker_utils.exec_command(
        master,
        f"find {spider_dir} -type f 2>/dev/null | wc -l",
        timeout=5,
    )

    file_count = int(count_result["output"].strip()) if count_result["exit_code"] == 0 else 0

    if file_count == 4:
        logger.info("  ✓ All 4 files present on master")
        # List files for debugging
        ls_result = docker_utils.exec_command(master, f"ls -lh {spider_dir}", timeout=5)
        logger.debug(f"\n{ls_result['output']}")
        return True
    else:
        logger.error(f"  ✗ Expected 4 files, found {file_count}")
        # Show what's in the directory
        ls_result = docker_utils.exec_command(master, f"ls -lha {spider_dir}", timeout=5)
        logger.debug(f"  Directory contents:\n{ls_result['output']}")
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

    # Use docker_utils to find master container dynamically
    docker_helper = docker_utils.DockerHelper()
    master_container = docker_helper.find_master_container()

    if not master_container:
        logger.warning("  ⚠️  Could not find master container for log check")
    else:
        master = master_container["Names"]
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
