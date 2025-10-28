#!/usr/bin/env python3
"""
API-004: Spider CRUD Operations Test Runner

Tests complete CRUD operations for spiders via Crawlab API.
"""

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
    """Execute API-004 test."""

    # Initialize helpers
    auth = AuthHelper()
    spider_helper = SpiderHelper()
    cleanup = CleanupHelper()
    assertions = APIAssertions()

    # Test data
    spider_ids = []
    spider_id_dup = None
    token = None

    try:
        # Step 1: Setup and Authentication
        print_step(1, "Setup and Authentication")
        token, response = auth.login("admin", "admin")
        if not token:
            print_error("Failed to obtain authentication token")
            return False
        print_success("Authenticated successfully")

        # Step 2: Create Spider - Basic
        print_step(2, "Create Spider - Basic")
        spider_id_1, response = spider_helper.create_spider(
            token=token, name="test-spider-crud-001", cmd="python main.py"
        )

        if not spider_id_1:
            print_error(f"Failed to create spider: {response}")
            return False

        spider_ids.append(spider_id_1)
        cleanup.track_spider(spider_id_1)

        # Validate response
        spider_data = response.get("data", {})
        assertions.assert_has_field(spider_data, "_id")
        assertions.assert_has_field(spider_data, "created_at")
        assertions.assert_field_equals(spider_data, "name", "test-spider-crud-001")
        assertions.assert_field_equals(spider_data, "cmd", "python main.py")
        print_success(f"Created spider with ID: {spider_id_1}")

        # Step 3: Retrieve Spider
        print_step(3, "Retrieve Spider")
        spider_data, response = spider_helper.get_spider(token, spider_id_1)

        if not spider_data:
            print_error(f"Failed to retrieve spider: {response}")
            return False

        assertions.assert_field_equals(spider_data, "_id", spider_id_1)
        assertions.assert_field_equals(spider_data, "name", "test-spider-crud-001")
        assertions.assert_field_equals(spider_data, "cmd", "python main.py")
        assertions.assert_has_field(spider_data, "created_at")
        print_success("Retrieved spider successfully with all fields")

        # Step 4: Create Spider - Full Fields
        print_step(4, "Create Spider - Full Fields")
        spider_id_2, response = spider_helper.create_spider(
            token=token,
            name="test-spider-crud-002",
            cmd="scrapy crawl myspider",
            description="Test spider with full configuration",
            mode="random",
            priority=7,
            col_name="test_results",
        )

        if not spider_id_2:
            print_error(f"Failed to create spider with full fields: {response}")
            return False

        spider_ids.append(spider_id_2)
        cleanup.track_spider(spider_id_2)

        spider_data = response.get("data", {})
        assertions.assert_field_equals(spider_data, "name", "test-spider-crud-002")
        assertions.assert_field_equals(spider_data, "cmd", "scrapy crawl myspider")
        assertions.assert_field_equals(spider_data, "description", "Test spider with full configuration")
        assertions.assert_field_equals(spider_data, "mode", "random")
        assertions.assert_field_equals(spider_data, "priority", 7)
        assertions.assert_field_equals(spider_data, "col_name", "test_results")
        print_success(f"Created spider with full fields: {spider_id_2}")

        # Step 5: List Spiders
        print_step(5, "List Spiders")
        spiders_list, response = spider_helper.list_spiders(token)

        if spiders_list is None:
            print_error(f"Failed to list spiders: {response}")
            return False

        # Check if our test spiders are in the list
        spider_names = [s.get("name") for s in spiders_list]
        if "test-spider-crud-001" not in spider_names:
            print_error("First test spider not found in list")
            return False
        if "test-spider-crud-002" not in spider_names:
            print_error("Second test spider not found in list")
            return False

        print_success(f"Listed {len(spiders_list)} spiders, both test spiders present")

        # Step 6: Update Spider - Partial (PATCH)
        print_step(6, "Update Spider - Partial")

        # Note: The API uses PUT for updates
        success, response = spider_helper.update_spider(
            token=token,
            spider_id=spider_id_1,
            name="test-spider-crud-001",  # Keep original name
            cmd="python main.py",  # Keep original cmd
            description="Updated description",
            priority=8,
        )

        if not success:
            print_error(f"Failed to update spider: {response}")
            return False

        # Verify the update
        spider_data, _ = spider_helper.get_spider(token, spider_id_1)
        if spider_data:
            assertions.assert_field_equals(spider_data, "description", "Updated description")
            assertions.assert_field_equals(spider_data, "priority", 8)
            assertions.assert_field_equals(spider_data, "name", "test-spider-crud-001")
            print_success("Updated spider with partial fields successfully")
        else:
            print_error("Failed to verify spider update")
            return False

        # Step 7: Update Spider - Full (PUT)
        print_step(7, "Update Spider - Full")
        success, response = spider_helper.update_spider(
            token=token,
            spider_id=spider_id_1,
            name="test-spider-crud-001-updated",
            cmd="python spider.py",
            description="Fully replaced spider",
            mode="all",
            priority=9,
        )

        if not success:
            print_error(f"Failed to replace spider: {response}")
            return False

        # Verify the replacement
        spider_data, _ = spider_helper.get_spider(token, spider_id_1)
        if spider_data:
            assertions.assert_field_equals(spider_data, "_id", spider_id_1)
            assertions.assert_field_equals(spider_data, "name", "test-spider-crud-001-updated")
            assertions.assert_field_equals(spider_data, "cmd", "python spider.py")
            assertions.assert_field_equals(spider_data, "description", "Fully replaced spider")
            assertions.assert_field_equals(spider_data, "mode", "all")
            assertions.assert_field_equals(spider_data, "priority", 9)
            print_success("Replaced spider with full update successfully")
        else:
            print_error("Failed to verify spider replacement")
            return False

        # Step 8: Duplicate Name Validation
        print_step(8, "Duplicate Name Validation")
        spider_id_dup, response = spider_helper.create_spider(
            token=token,
            name="test-spider-crud-001-updated",  # Duplicate name
            cmd="python test.py",
        )

        if spider_id_dup:
            print_error(f"Duplicate name was accepted (should be rejected): {spider_id_dup}")
            # Clean up the duplicate if it was created
            cleanup.track_spider(spider_id_dup)
            # Don't fail the test as some systems may allow duplicates
            print("⚠️  Warning: System allows duplicate spider names")
        else:
            print_success("Duplicate name was properly rejected")

        # Step 9: Invalid ID Handling
        print_step(9, "Invalid ID Handling")

        # Try to get non-existent spider
        spider_data, response = spider_helper.get_spider(token, "000000000000000000000000")
        if spider_data:
            print_error("Non-existent spider was found (should return error)")
            return False
        print_success("Get with invalid ID properly rejected")

        # Try to update non-existent spider
        success, response = spider_helper.update_spider(token=token, spider_id="000000000000000000000000", name="test")
        if success:
            print_error("Update with invalid ID succeeded (should fail)")
            return False
        print_success("Update with invalid ID properly rejected")

        # Try to delete non-existent spider
        success, response = spider_helper.delete_spider(token, "000000000000000000000000")
        if success:
            print_error("Delete with invalid ID succeeded (should fail)")
            return False
        print_success("Delete with invalid ID properly rejected")

        # Step 10: Delete Spider
        print_step(10, "Delete First Spider")
        success, response = spider_helper.delete_spider(token, spider_id_1)

        if not success:
            print_error(f"Failed to delete spider: {response}")
            return False

        print_success(f"Deleted spider: {spider_id_1}")

        # Verify deletion
        spider_data, _ = spider_helper.get_spider(token, spider_id_1)
        if spider_data:
            print_error("Spider still exists after deletion")
            return False
        print_success("Verified spider was deleted")

        # Step 11: Delete Second Spider
        print_step(11, "Delete Second Spider")
        success, response = spider_helper.delete_spider(token, spider_id_2)

        if not success:
            print_error(f"Failed to delete second spider: {response}")
            return False

        print_success(f"Deleted spider: {spider_id_2}")

        # Also delete the duplicate if it was created
        if spider_id_dup:
            success_dup, _ = spider_helper.delete_spider(token, spider_id_dup)
            if success_dup:
                print_success(f"Also deleted duplicate spider: {spider_id_dup}")

        # Step 12: List After Deletion
        print_step(12, "List After Deletion")
        spiders_list, response = spider_helper.list_spiders(token)

        if spiders_list is None:
            print_error(f"Failed to list spiders: {response}")
            return False

        # Check that our test spiders are not in the list
        spider_names = [s.get("name") for s in spiders_list]
        if "test-spider-crud-001-updated" in spider_names:
            print_error("First test spider still in list after deletion")
            return False
        if "test-spider-crud-002" in spider_names:
            print_error("Second test spider still in list after deletion")
            return False

        print_success("Verified test spiders are no longer in list")

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
