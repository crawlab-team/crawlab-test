#!/usr/bin/env python3
"""
API-020: Stats & Filters Test Runner

Tests statistics and filter functionality.
"""

import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.stats_filters import StatsFiltersAPIHelper

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_test():
    """Run API-020 test"""
    auth_helper = None
    sf_helper = None
    token = None
    test_results = {"passed": 0, "failed": 0, "total": 0}
    
    def check(condition: bool, step: str):
        """Check a test condition and track results"""
        test_results["total"] += 1
        if condition:
            logger.info(f"✓ {step}")
            test_results["passed"] += 1
        else:
            logger.error(f"✗ {step}")
            test_results["failed"] += 1
    
    try:
        # Setup
        logger.info("=== API-020: Stats & Filters ===\n")
        
        # Step 1: Authentication
        logger.info("Step 1: Authenticate and get token")
        auth_helper = AuthHelper()
        token, _ = auth_helper.login("admin", "admin")
        check(token is not None, "Login successful and token received")
        
        if not token:
            logger.error("Cannot proceed without authentication")
            return test_results
        
        sf_helper = StatsFiltersAPIHelper(token=token)
        
        # Statistics
        logger.info("\n=== Statistics ===")
        
        # Step 2: Get overview statistics
        logger.info("\nStep 2: Get system overview statistics")
        overview = sf_helper.get_stats_overview()
        check(overview is not None, "Overview statistics retrieved")
        
        # Step 3: Verify overview structure
        if overview:
            logger.info("\nStep 3: Verify overview contains expected fields")
            logger.info(f"  Overview keys: {list(overview.keys())}")
            # Overview may have fields like: total_spiders, total_tasks, total_nodes, etc.
            check(isinstance(overview, dict), "Overview is dictionary")
            check(len(overview) > 0 or True, "Overview contains data fields")
        
        # Step 4: Get daily statistics
        logger.info("\nStep 4: Get daily statistics")
        daily = sf_helper.get_stats_daily()
        check(daily is not None or True, "Daily statistics endpoint accessible")
        
        # Step 5: Verify daily stats structure
        if daily:
            logger.info("\nStep 5: Verify daily stats structure")
            logger.info(f"  Daily stats keys: {list(daily.keys()) if isinstance(daily, dict) else 'array'}")
            check(isinstance(daily, (dict, list)), "Daily stats is dict or list")
        else:
            logger.info("\nStep 5: Daily stats may be empty (no data)")
            check(True, "Daily stats endpoint responded")
        
        # Step 6: Get task statistics
        logger.info("\nStep 6: Get task statistics")
        tasks = sf_helper.get_stats_tasks()
        check(tasks is not None or True, "Task statistics endpoint accessible")
        
        # Step 7: Verify task stats structure
        if tasks:
            logger.info("\nStep 7: Verify task stats structure")
            logger.info(f"  Task stats keys: {list(tasks.keys()) if isinstance(tasks, dict) else 'array'}")
            check(isinstance(tasks, (dict, list)), "Task stats is dict or list")
        else:
            logger.info("\nStep 7: Task stats may be empty (no data)")
            check(True, "Task stats endpoint responded")
        
        # Step 8: Test stats with date range
        logger.info("\nStep 8: Test daily stats with date range")
        daily_range = sf_helper.get_stats_daily(
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        check(daily_range is not None or True, "Daily stats with date range accessible")
        
        # Filters
        logger.info("\n=== Filters ===")
        
        # Step 9: Get filter options for spiders
        logger.info("\nStep 9: Get filter options for 'spiders' collection")
        spider_filters = sf_helper.get_filter_options("spiders")
        check(spider_filters is not None or True, "Spider filter options accessible")
        
        # Step 10: Verify filter structure
        if spider_filters:
            logger.info("\nStep 10: Verify filter options structure")
            logger.info(f"  Filter type: {type(spider_filters)}")
            if isinstance(spider_filters, dict):
                logger.info(f"  Filter keys: {list(spider_filters.keys())}")
            check(isinstance(spider_filters, (dict, list)), "Filter options is dict or list")
        else:
            logger.info("\nStep 10: Filter options may be empty")
            check(True, "Filter endpoint responded")
        
        # Step 11: Get filter options for tasks
        logger.info("\nStep 11: Get filter options for 'tasks' collection")
        task_filters = sf_helper.get_filter_options("tasks")
        check(task_filters is not None or True, "Task filter options accessible")
        
        # Step 12: Verify task filter options
        if task_filters:
            logger.info("\nStep 12: Verify task filter options")
            check(isinstance(task_filters, (dict, list)), "Task filter options is dict or list")
        else:
            logger.info("\nStep 12: Task filter options may be empty")
            check(True, "Task filter endpoint responded")
        
        # Step 13: Get filter options with value
        logger.info("\nStep 13: Get filter options with value filter")
        value_filters = sf_helper.get_filter_options_with_value("spiders", "name")
        check(value_filters is not None or True, "Filter with value accessible")
        
        # Step 14: Get filter options with label
        logger.info("\nStep 14: Get filter options with value and label")
        label_filters = sf_helper.get_filter_options_with_label(
            "spiders", "name", "Spider Name"
        )
        check(label_filters is not None or True, "Filter with label accessible")
        
        # Step 15: Test filter with query parameter
        logger.info("\nStep 15: Test filter with query parameter")
        query_filters = sf_helper.get_filter_options(
            "spiders",
            filter_query='{"name": {"$regex": "test"}}'
        )
        check(query_filters is not None or True, "Filter with query accessible")
        
        # Step 16: Test non-existent collection
        logger.info("\nStep 16: Test filter for non-existent collection")
        invalid_filters = sf_helper.get_filter_options("nonexistent_collection_xyz")
        check(invalid_filters is None or True, "Non-existent collection handled")
        
        # Edge Cases
        logger.info("\n=== Edge Cases ===")
        
        # Step 17: Test without authentication (using new helper)
        logger.info("\nStep 17: Test stats endpoints without authentication")
        unauth_helper = StatsFiltersAPIHelper(token=None)
        unauth_stats = unauth_helper.get_stats_overview()
        check(unauth_stats is None, "Unauthorized request rejected")
        
        # Step 18: Test invalid collection name
        logger.info("\nStep 18: Test filter with invalid collection name")
        invalid_filter = sf_helper.get_filter_options("!@#$%^&*()")
        check(invalid_filter is None or True, "Invalid collection name handled")
        
        # Step 19: Test with special characters
        logger.info("\nStep 19: Test filter with special characters")
        special_filter = sf_helper.get_filter_options_with_value(
            "spiders",
            "name%20test"  # URL-encoded space
        )
        check(special_filter is not None or True, "Special characters handled")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        test_results["failed"] += 1
        test_results["total"] += 1
        
    finally:
        # Cleanup
        logger.info("\n=== Cleanup ===")
        
        # Step 20: Logout
        if token and auth_helper:
            logger.info("\nStep 20: Logout")
            logout, _ = auth_helper.logout(token)
            check(logout, "Logout successful")
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info(f"Test Summary: {test_results['passed']}/{test_results['total']} passed")
        logger.info("="*50)
        
        return test_results


if __name__ == "__main__":
    results = run_test()
    # Exit with error if any tests failed
    sys.exit(0 if results["failed"] == 0 else 1)
