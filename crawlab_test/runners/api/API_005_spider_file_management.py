#!/usr/bin/env python3
"""
API-005: Spider File Management Test Runner

Tests file operations for spiders via Crawlab API.
"""

import json
import sys

from crawlab_test.helpers.api import APIAssertions, AuthHelper, CleanupHelper, SpiderHelper


def print_step(step_num: int, description: str):
    """Print formatted test step."""
    print(f"\n{'='*80}")
    print(f"Step {step_num}: {description}")
    print("=" * 80)


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def main():
    """Execute API-005 test."""

    # Initialize helpers
    auth = AuthHelper()
    spider_helper = SpiderHelper()
    cleanup = CleanupHelper()
    assertions = APIAssertions()

    # Test data
    spider_id = None
    token = None

    # Test file contents
    main_py_content = """#!/usr/bin/env python3
print("Hello from Crawlab spider!")
"""

    config_json_content = json.dumps({"spider_name": "test-spider", "timeout": 300, "max_retries": 3}, indent=2)

    helper_py_content = """def helper_function():
    return "Helper utility"
"""

    try:
        # Step 1: Setup and Authentication
        print_step(1, "Setup and Authentication")
        token, response = auth.login("admin", "admin")
        if not token:
            print_error("Failed to obtain authentication token")
            return False
        print_success("Authenticated successfully")

        # Step 2: Create Test Spider
        print_step(2, "Create Test Spider")
        spider_id, response = spider_helper.create_spider(
            token=token, name="test-spider-files-001", cmd="python main.py"
        )

        if not spider_id:
            print_error(f"Failed to create spider: {response}")
            return False

        cleanup.track_spider(spider_id)
        print_success(f"Created spider with ID: {spider_id}")

        # Step 3: Save File - Create Main Script
        print_step(3, "Save File - Create Main Script")
        success, response = spider_helper.save_file(
            token=token, spider_id=spider_id, path="main.py", content=main_py_content
        )

        if not success:
            print_error(f"Failed to save main.py: {response}")
            return False
        print_success("Created main.py successfully")

        # Step 4: Get File Content
        print_step(4, "Get File Content")
        file_content, response = spider_helper.get_file(token=token, spider_id=spider_id, path="main.py")

        if not file_content:
            print_error(f"Failed to get file content: {response}")
            return False

        if file_content != main_py_content:
            print_error("File content mismatch")
            print(f"Expected: {main_py_content!r}")
            print(f"Got: {file_content!r}")
            return False
        print_success("Retrieved file content matches saved content")

        # Step 5: Get File Info (Metadata)
        print_step(5, "Get File Info (Metadata)")
        file_info, response = spider_helper.get_file_info(token=token, spider_id=spider_id, path="main.py")

        if not file_info:
            print_error(f"Failed to get file info: {response}")
            return False

        assertions.assert_has_field(file_info, "name")
        assertions.assert_has_field(file_info, "is_dir")
        if file_info.get("is_dir"):
            print_error("File incorrectly identified as directory")
            return False
        print_success(f"File info retrieved: {file_info.get('name')}, is_dir={file_info.get('is_dir')}")

        # Step 6: Save File - Create Config
        print_step(6, "Save File - Create Config")
        success, response = spider_helper.save_file(
            token=token, spider_id=spider_id, path="config.json", content=config_json_content
        )

        if not success:
            print_error(f"Failed to save config.json: {response}")
            return False
        print_success("Created config.json successfully")

        # Step 7: Create Directory (implicit via save in subdirectory)
        print_step(7, "Create Directory")
        # Note: Most systems create directories implicitly when saving files
        # We'll create it by saving a file in it
        print_success("Directory will be created implicitly via file save")

        # Step 8: Save File in Subdirectory
        print_step(8, "Save File in Subdirectory")
        success, response = spider_helper.save_file(
            token=token, spider_id=spider_id, path="utils/helper.py", content=helper_py_content
        )

        if not success:
            print_error(f"Failed to save utils/helper.py: {response}")
            return False
        print_success("Created utils/helper.py in subdirectory")

        # Step 9: List Root Directory Files
        print_step(9, "List Root Directory Files")
        files_list, response = spider_helper.list_files(token=token, spider_id=spider_id, path="/")

        if files_list is None:
            print_error(f"Failed to list files: {response}")
            return False

        file_names = [f.get("name") for f in files_list if f.get("name")]
        print(f"Files found: {file_names}")

        if "main.py" not in file_names:
            print_error("main.py not found in root directory")
            return False
        if "config.json" not in file_names:
            print_error("config.json not found in root directory")
            return False
        if "utils" not in file_names:
            print_error("utils directory not found in root")
            return False

        print_success(f"Listed {len(files_list)} items in root directory")

        # Step 10: List Subdirectory Files
        print_step(10, "List Subdirectory Files")
        utils_files, response = spider_helper.list_files(token=token, spider_id=spider_id, path="/utils")

        if utils_files is None:
            print_error(f"Failed to list utils directory: {response}")
            return False

        utils_file_names = [f.get("name") for f in utils_files if f.get("name")]
        print(f"Files in utils: {utils_file_names}")

        if "helper.py" not in utils_file_names:
            print_error("helper.py not found in utils directory")
            return False

        print_success(f"Listed {len(utils_files)} items in utils directory")

        # Step 11: Get Directory Info
        print_step(11, "Get Directory Info")
        dir_info, response = spider_helper.get_file_info(token=token, spider_id=spider_id, path="utils")

        if not dir_info:
            print_error(f"Failed to get directory info: {response}")
            return False

        if not dir_info.get("is_dir"):
            print_error("Directory not identified as is_dir=true")
            return False
        print_success(f"Directory info retrieved: {dir_info.get('name')}, is_dir={dir_info.get('is_dir')}")

        # Step 12: Copy File
        print_step(12, "Copy File")
        success, response = spider_helper.copy_file(
            token=token, spider_id=spider_id, src_path="main.py", dest_path="main_backup.py"
        )

        if not success:
            print_error(f"Failed to copy file: {response}")
            return False
        print_success("Copied main.py to main_backup.py")

        # Step 13: Verify Copied File
        print_step(13, "Verify Copied File")
        copied_content, response = spider_helper.get_file(token=token, spider_id=spider_id, path="main_backup.py")

        if not copied_content:
            print_error(f"Failed to get copied file: {response}")
            return False

        if copied_content != main_py_content:
            print_error("Copied file content doesn't match original")
            return False
        print_success("Copied file content matches original")

        # Step 14: Rename File
        print_step(14, "Rename File")
        success, response = spider_helper.rename_file(
            token=token, spider_id=spider_id, old_path="main_backup.py", new_path="main_copy.py"
        )

        if not success:
            print_error(f"Failed to rename file: {response}")
            return False
        print_success("Renamed main_backup.py to main_copy.py")

        # Step 15: Verify Renamed File
        print_step(15, "Verify Renamed File")
        renamed_content, response = spider_helper.get_file(token=token, spider_id=spider_id, path="main_copy.py")

        if not renamed_content:
            print_error(f"Failed to get renamed file: {response}")
            return False

        if renamed_content != main_py_content:
            print_error("Renamed file content doesn't match original")
            return False

        # Verify old name doesn't exist
        old_file, _ = spider_helper.get_file(token, spider_id, "main_backup.py")
        if old_file:
            print_error("Old file name still exists after rename")
            return False

        print_success("Renamed file verified, old name removed")

        # Step 16: Delete File
        print_step(16, "Delete File")

        # First check the delete endpoint signature
        # Based on OpenAPI, it uses query params or request body
        # Let's use the helper's delete method (which uses DELETE with params)
        import os

        import requests

        os.environ["NO_PROXY"] = "localhost,127.0.0.1"

        response = requests.delete(
            f"http://localhost:8080/api/spiders/{spider_id}/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"path": "main_copy.py"},
            timeout=10,
        )

        success = response.status_code == 200
        if not success:
            print_error(f"Failed to delete file: {response.status_code} - {response.text}")
            return False

        print_success("Deleted main_copy.py")

        # Verify file is deleted
        deleted_file, _ = spider_helper.get_file(token, spider_id, "main_copy.py")
        if deleted_file:
            print_error("File still exists after deletion")
            return False
        print_success("Verified file is deleted")

        # Step 17: Delete File in Subdirectory
        print_step(17, "Delete File in Subdirectory")

        response = requests.delete(
            f"http://localhost:8080/api/spiders/{spider_id}/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"path": "utils/helper.py"},
            timeout=10,
        )

        success = response.status_code == 200
        if not success:
            print_error(f"Failed to delete subdirectory file: {response.status_code}")
            return False

        print_success("Deleted utils/helper.py")

        # List utils directory to verify it's empty
        utils_files_after, _ = spider_helper.list_files(token, spider_id, "/utils")
        if utils_files_after and len(utils_files_after) > 0:
            print_error(f"Utils directory not empty after deletion: {utils_files_after}")
            # This might be acceptable if directory itself is listed
            print("⚠️  Warning: Directory may contain entries after file deletion")
        else:
            print_success("Utils directory is empty after file deletion")

        # Step 18: Invalid Path Handling
        print_step(18, "Invalid Path Handling")

        # Try to get non-existent file
        nonexistent, response = spider_helper.get_file(token, spider_id, "nonexistent.py")
        if nonexistent:
            print_error("Non-existent file was retrieved (should fail)")
            return False
        print_success("Get non-existent file properly rejected")

        # Try to delete non-existent file
        response = requests.delete(
            f"http://localhost:8080/api/spiders/{spider_id}/files",
            headers={"Authorization": f"Bearer {token}"},
            params={"path": "nonexistent.py"},
            timeout=10,
        )

        # This might succeed or fail depending on implementation
        if response.status_code == 200:
            print("⚠️  Warning: Deleting non-existent file returns success")
        else:
            print_success("Delete non-existent file properly rejected")

        # Step 19: Cleanup Spider
        print_step(19, "Cleanup Spider")
        success, response = spider_helper.delete_spider(token, spider_id)

        if not success:
            print_error(f"Failed to delete spider: {response}")
            return False

        print_success(f"Deleted spider: {spider_id}")

        # All tests passed
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return True

    except Exception as e:
        print_error(f"Test failed with exception: {e!s}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if token:
            print("\n" + "=" * 80)
            print("Cleanup: Removing test resources")
            print("=" * 80)
            cleanup.cleanup_all(token)
            auth.logout(token)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
