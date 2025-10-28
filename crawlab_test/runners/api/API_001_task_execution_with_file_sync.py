#!/usr/bin/env python3
"""
API-001 - Task Execution with File Sync Validation

Fast API-based test for validating gRPC file sync in task execution.
Tests the complete workflow: spider creation → file upload → task execution → file sync validation.
"""

import sys
import time
from pathlib import Path

import requests

# Add parent directory to path
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from crawlab_test.helpers.infrastructure.utils import setup_logging

# Configuration
API_URL = "http://localhost:8080/api"
USERNAME = "admin"
PASSWORD = "admin"


def test_task_execution_with_file_sync():
    """Main test function"""
    logger = setup_logging()

    logger.info("=" * 70)
    logger.info("API-001: Task Execution with File Sync Validation")
    logger.info("=" * 70)
    logger.info("")

    token = None
    spider_id = None

    try:
        # Step 1: Authenticate
        logger.info("Step 1: Authenticating...")
        response = requests.post(f"{API_URL}/login", json={"username": USERNAME, "password": PASSWORD}, timeout=10)
        response.raise_for_status()
        token = response.json().get("data")

        if not token:
            logger.error("✗ Authentication failed - no token received")
            return False

        logger.info("✓ Authenticated successfully")
        logger.info("")

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create Test Spider
        logger.info("Step 2: Creating test spider...")
        response = requests.post(
            f"{API_URL}/spiders",
            headers=headers,
            json={
                "data": {
                    "name": "api-test-grpc-sync",
                    "cmd": "python main.py",
                    "description": "API test for gRPC file sync validation",
                }
            },
            timeout=10,
        )
        response.raise_for_status()
        spider_id = response.json().get("data", {}).get("_id")

        if not spider_id:
            logger.error("✗ Spider creation failed - no ID received")
            return False

        logger.info(f"✓ Spider created: {spider_id}")
        logger.info("")

        # Step 3: Upload Spider Files
        logger.info("Step 3: Uploading spider files...")

        files = {
            "main.py": """#!/usr/bin/env python
import os
import sys

print("Spider starting...")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir(os.getcwd())}")

# Verify files were synced
expected_files = ["main.py", "config.json", "utils.py"]
for f in expected_files:
    if os.path.exists(f):
        print(f"✓ File synced: {f}")
    else:
        print(f"✗ File missing: {f}")
        sys.exit(1)

print("All files synced successfully!")
print("Spider execution complete.")""",
            "config.json": '{"test": true, "version": "1.0.0"}',
            "utils.py": 'def helper():\n    return "Helper function"',
        }

        for filename, content in files.items():
            response = requests.post(
                f"{API_URL}/spiders/{spider_id}/files/save",
                headers=headers,
                json={"path": filename, "data": content},
                timeout=10,
            )
            if response.status_code == 200:
                logger.info(f"✓ Uploaded {filename}")
            else:
                logger.error(f"✗ Failed to upload {filename}: {response.status_code} - {response.text}")
                return False

        logger.info("")

        # Step 4: Verify Files on Master
        logger.info("Step 4: Verifying files on master...")
        response = requests.get(
            f"{API_URL}/spiders/{spider_id}/files/list", headers=headers, params={"path": "/"}, timeout=10
        )
        response.raise_for_status()

        file_list = response.json().get("data", [])
        file_names = [f.get("name") for f in file_list]

        logger.info(f"Files on master: {', '.join(file_names)}")

        if all(f in file_names for f in ["main.py", "config.json", "utils.py"]):
            logger.info("✓ All files present on master")
        else:
            logger.error("✗ Some files missing on master")
            return False

        logger.info("")

        # Step 5: Create and Execute Task
        logger.info("Step 5: Creating and executing task...")
        response = requests.post(
            f"{API_URL}/tasks/run", headers=headers, json={"spider_id": spider_id, "cmd": "python main.py"}, timeout=10
        )
        response.raise_for_status()
        task_ids = response.json().get("data", [])
        task_id = task_ids[0] if isinstance(task_ids, list) and task_ids else None

        if not task_id:
            logger.error("✗ Task creation failed - no ID received")
            return False

        logger.info(f"✓ Task created: {task_id}")
        logger.info("")

        # Step 6: Monitor Task Execution
        logger.info("Step 6: Monitoring task execution...")
        timeout = 30
        status = None

        for i in range(timeout):
            response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers, timeout=10)
            response.raise_for_status()
            status = response.json().get("data", {}).get("status")

            if status == "finished":
                logger.info("\n✓ Task completed successfully")
                break
            elif status == "error":
                logger.error("\n✗ Task failed with error status")
                break

            if i < timeout - 1:
                print(".", end="", flush=True)
                time.sleep(1)
        else:
            logger.warning(f"\n⚠ Task timeout after {timeout} seconds (status: {status})")

        logger.info("")

        # Step 7: Verify File Sync in Task Logs
        logger.info("Step 7: Verifying file sync in task logs...")

        # Wait a moment for logs to be available
        time.sleep(2)

        response = requests.get(f"{API_URL}/tasks/{task_id}/logs", headers=headers, timeout=10)
        response.raise_for_status()

        logs_data = response.json().get("data", "")
        # Handle different API response formats
        if isinstance(logs_data, dict):
            logs = logs_data.get("content", "")
        elif isinstance(logs_data, list):
            logs = "\n".join(logs_data)
        else:
            logs = str(logs_data) if logs_data else ""

        logger.info("Task logs:")
        logger.info("---")
        logger.info(logs or "(empty)")
        logger.info("---")
        logger.info("")

        # Check for file sync validation
        validation_passed = True

        checks = [
            ("✓ File synced: main.py", "main.py synced"),
            ("✓ File synced: config.json", "config.json synced"),
            ("✓ File synced: utils.py", "utils.py synced"),
            ("All files synced successfully", "File sync validation passed"),
        ]

        for check_string, description in checks:
            if check_string in logs:
                logger.info(f"✓ {description}")
            else:
                logger.error(f"✗ {description} FAILED")
                validation_passed = False

        logger.info("")

        # Step 8: Check gRPC Activity (optional)
        logger.info("Step 8: Checking gRPC activity in master logs...")
        try:
            import subprocess

            result = subprocess.run(
                ["docker", "logs", "crawlab_master", "--since", "2m"], capture_output=True, text=True, timeout=5
            )

            grpc_logs = [
                line
                for line in result.stdout.split("\n") + result.stderr.split("\n")
                if "sync" in line.lower() or "grpc" in line.lower()
            ]

            if grpc_logs:
                logger.info("Recent gRPC/sync activity:")
                for line in grpc_logs[-10:]:  # Last 10 lines
                    logger.info(f"  {line}")
                logger.info("✓ gRPC activity detected")
            else:
                logger.warning("⚠ No obvious gRPC activity in logs (may be normal if verbose logging disabled)")
        except Exception as e:
            logger.warning(f"⚠ Could not check Docker logs: {e}")

        logger.info("")

        # Step 9: Final Status Check
        logger.info("Step 9: Final validation...")
        response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers, timeout=10)
        response.raise_for_status()
        final_status = response.json().get("data", {}).get("status")

        logger.info(f"Final task status: {final_status}")
        logger.info("")

        # Determine test result
        test_passed = final_status == "finished" and validation_passed

        # Cleanup
        logger.info("Cleanup: Deleting test spider...")
        if spider_id:
            requests.delete(f"{API_URL}/spiders/{spider_id}", headers=headers, timeout=10)
            logger.info("✓ Test spider deleted")
        logger.info("")

        # Final result
        logger.info("=" * 70)
        if test_passed:
            logger.info("✓ API-001 TEST PASSED")
            logger.info("  • Spider created and files uploaded")
            logger.info("  • Task executed successfully")
            logger.info("  • All files synced to worker via gRPC")
            logger.info("  • Task completed in < 30 seconds")
        else:
            logger.error("✗ API-001 TEST FAILED")
            logger.error(f"  • Task status: {final_status}")
            logger.error(f"  • File sync validation: {validation_passed}")
        logger.info("=" * 70)

        return test_passed

    except requests.exceptions.RequestException as e:
        logger.error(f"✗ API request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Test error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_task_execution_with_file_sync()
    sys.exit(0 if success else 1)
