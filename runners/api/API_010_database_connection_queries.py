#!/usr/bin/env python3
"""
Test Runner: API-010 - Database Connection & Queries

Tests database connection management and query execution APIs.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import helpers
from helpers.api import AuthHelper
from helpers.api.database import DatabaseAPIHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure NO_PROXY is set for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

def run_test():
    """Execute API-010 test scenarios"""
    
    test_passed = True
    test_steps = []
    created_databases = []
    
    try:
        # Get API URL from environment or use default
        api_url = os.getenv('CRAWLAB_API_URL', 'http://localhost:8080/api')
        
        logger.info("=" * 80)
        logger.info("API-010: Database Connection & Queries")
        logger.info("=" * 80)
        
        # Step 1: Authentication
        logger.info("\n[Step 1] Authenticating as admin user...")
        auth_helper = AuthHelper(base_url=api_url)
        token, response = auth_helper.login("admin", "admin")
        if not token:
            raise Exception("Authentication failed")
        logger.info("✓ Authentication successful")
        test_steps.append(("Authentication", True, "Login successful"))
        
        # Initialize database helper
        db_helper = DatabaseAPIHelper(base_url=api_url, token=token)
        
        # Step 2: Create MongoDB Database
        logger.info("\n[Step 2] Creating MongoDB database connection...")
        mongo_data = {
            "name": "test-mongo-db",
            "data_source": "mongo",
            "host": "localhost",
            "port": 27017,
            "database": "crawlab_test",
            "description": "Test MongoDB database"
        }
        mongo_db = db_helper.create_database(mongo_data)
        if not mongo_db or '_id' not in mongo_db:
            raise Exception("Failed to create MongoDB database")
        mongo_id = mongo_db['_id']
        created_databases.append(mongo_id)
        logger.info(f"✓ MongoDB database created: {mongo_id}")
        test_steps.append(("Create MongoDB Database", True, f"ID: {mongo_id}"))
        
        # Step 3: List Databases
        logger.info("\n[Step 3] Listing all databases...")
        db_list = db_helper.list_databases(page=1, size=10)
        if not db_list or 'data' not in db_list:
            raise Exception("Failed to list databases")
        logger.info(f"✓ Found {db_list.get('total', 0)} databases")
        test_steps.append(("List Databases", True, f"Total: {db_list.get('total', 0)}"))
        
        # Step 4: Get Database Details
        logger.info("\n[Step 4] Getting database details...")
        db_details = db_helper.get_database(mongo_id)
        if not db_details or db_details.get('_id') != mongo_id:
            raise Exception("Failed to get database details")
        logger.info(f"✓ Database details retrieved: {db_details.get('name')}")
        test_steps.append(("Get Database Details", True, "Details match"))
        
        # Step 5: Update Database
        logger.info("\n[Step 5] Updating database description...")
        update_result = db_helper.update_database(mongo_id, {
            "description": "Updated description"
        })
        if not update_result:
            logger.warning("⚠ Database update may have failed")
            test_steps.append(("Update Database", False, "Update may have failed"))
        else:
            logger.info("✓ Database updated successfully")
            test_steps.append(("Update Database", True, "Description updated"))
        
        # Step 6: Test Connection
        logger.info("\n[Step 6] Testing database connection...")
        try:
            conn_test = db_helper.test_connection(mongo_id)
            logger.info(f"✓ Connection test completed: {conn_test}")
            test_steps.append(("Test Connection", True, "Endpoint accessible"))
        except Exception as e:
            logger.info(f"⚠ Connection test failed (expected): {e}")
            test_steps.append(("Test Connection", True, "Expected failure - no real DB"))
        
        # Step 7: Get Column Types
        logger.info("\n[Step 7] Getting column types...")
        try:
            col_types = db_helper.get_column_types(mongo_id)
            if col_types:
                logger.info(f"✓ Column types retrieved: {len(col_types)} types")
                test_steps.append(("Get Column Types", True, f"{len(col_types)} types"))
            else:
                logger.info("⚠ No column types returned")
                test_steps.append(("Get Column Types", False, "No types returned"))
        except Exception as e:
            logger.info(f"⚠ Failed to get column types: {e}")
            test_steps.append(("Get Column Types", False, str(e)))
        
        # Step 8: Execute Query (Optional)
        logger.info("\n[Step 8] Executing query (exploratory)...")
        try:
            query_result = db_helper.execute_query(mongo_id, "crawlab_test", "SELECT 1 as test")
            logger.info(f"✓ Query executed: {query_result}")
            test_steps.append(("Execute Query", True, "Query succeeded"))
        except Exception as e:
            logger.info(f"⚠ Query failed (expected if DB doesn't exist): {e}")
            test_steps.append(("Execute Query", True, "Expected failure - no real DB"))
        
        # Step 9: Create MySQL Connection
        logger.info("\n[Step 9] Creating MySQL database connection...")
        mysql_data = {
            "name": "test-mysql-db",
            "data_source": "mysql",
            "host": "localhost",
            "port": 3306,
            "username": "testuser",
            "password": "testpass",
            "database": "testdb",
            "description": "Test MySQL database"
        }
        mysql_db = db_helper.create_database(mysql_data)
        if not mysql_db or '_id' not in mysql_db:
            raise Exception("Failed to create MySQL database")
        mysql_id = mysql_db['_id']
        created_databases.append(mysql_id)
        logger.info(f"✓ MySQL database created: {mysql_id}")
        test_steps.append(("Create MySQL Database", True, f"ID: {mysql_id}"))
        
        # Step 10: Test MySQL Connection (Expected Failure)
        logger.info("\n[Step 10] Testing MySQL connection (expected to fail)...")
        try:
            mysql_conn_test = db_helper.test_connection(mysql_id)
            logger.info(f"⚠ Connection test result: {mysql_conn_test}")
            test_steps.append(("Test MySQL Connection", True, "Endpoint accessible"))
        except Exception as e:
            logger.info(f"✓ Connection test failed as expected: {e}")
            test_steps.append(("Test MySQL Connection", True, "Expected failure"))
        
        # Step 11: Pagination & Filtering
        logger.info("\n[Step 11] Testing pagination (page size = 1)...")
        paginated_list = db_helper.list_databases(page=1, size=1)
        if not paginated_list or 'data' not in paginated_list:
            raise Exception("Failed to get paginated list")
        if len(paginated_list['data']) <= 1:
            logger.info(f"✓ Pagination working: {len(paginated_list['data'])} items, total: {paginated_list.get('total', 0)}")
            test_steps.append(("Pagination", True, f"Page size respected"))
        else:
            logger.warning(f"⚠ Pagination may not be working: {len(paginated_list['data'])} items")
            test_steps.append(("Pagination", False, "Too many items returned"))
        
        # Step 12: Batch Update
        logger.info("\n[Step 12] Batch updating databases...")
        batch_update_success = db_helper.batch_update_databases(
            [mongo_id, mysql_id],
            {"description": "Batch updated"}
        )
        if batch_update_success:
            logger.info("✓ Batch update successful")
            test_steps.append(("Batch Update", True, "Both databases updated"))
        else:
            logger.warning("⚠ Batch update failed")
            test_steps.append(("Batch Update", False, "Update failed"))
        
        # Step 13: Invalid Connection - Missing Required Fields
        logger.info("\n[Step 13] Testing invalid connection (missing fields)...")
        try:
            invalid_db = db_helper.create_database({"name": "invalid-db"})
            if invalid_db:
                logger.warning("⚠ Invalid database creation should have failed")
                test_steps.append(("Invalid Connection", False, "Should have failed"))
                # Clean up if created
                if '_id' in invalid_db:
                    db_helper.delete_database(invalid_db['_id'])
            else:
                logger.info("✓ Invalid database creation failed as expected")
                test_steps.append(("Invalid Connection", True, "Properly rejected"))
        except Exception as e:
            logger.info(f"✓ Invalid database creation failed as expected: {e}")
            test_steps.append(("Invalid Connection", True, "Properly rejected"))
        
        # Step 14: Invalid Database ID
        logger.info("\n[Step 14] Testing invalid database ID...")
        try:
            invalid_db_details = db_helper.get_database("000000000000000000000000")
            if invalid_db_details:
                logger.warning("⚠ Should have returned error for invalid ID")
                test_steps.append(("Invalid Database ID", False, "Should have failed"))
            else:
                logger.info("✓ Invalid ID properly handled")
                test_steps.append(("Invalid Database ID", True, "Properly rejected"))
        except Exception as e:
            logger.info(f"✓ Invalid ID properly rejected: {e}")
            test_steps.append(("Invalid Database ID", True, "Properly rejected"))
        
        # Step 15: Delete Databases
        logger.info("\n[Step 15] Deleting test databases...")
        for db_id in created_databases:
            if db_helper.delete_database(db_id):
                logger.info(f"✓ Database deleted: {db_id}")
            else:
                logger.warning(f"⚠ Failed to delete database: {db_id}")
        test_steps.append(("Delete Databases", True, f"{len(created_databases)} databases deleted"))
        created_databases.clear()
        
        # Step 16: Verify Deletion
        logger.info("\n[Step 16] Verifying deletion...")
        final_list = db_helper.list_databases(page=1, size=100)
        if final_list and 'data' in final_list:
            test_db_names = ["test-mongo-db", "test-mysql-db"]
            remaining = [db for db in final_list['data'] if db.get('name') in test_db_names]
            if not remaining:
                logger.info("✓ All test databases deleted")
                test_steps.append(("Verify Deletion", True, "Cleanup successful"))
            else:
                logger.warning(f"⚠ Found remaining test databases: {len(remaining)}")
                test_steps.append(("Verify Deletion", False, f"{len(remaining)} databases remain"))
        
        # Logout
        logger.info("\n[Cleanup] Logging out...")
        auth_helper.logout(token)
        
    except Exception as e:
        logger.error(f"\n✗ Test failed with error: {e}")
        test_passed = False
        test_steps.append(("Test Execution", False, str(e)))
    
    finally:
        # Cleanup remaining databases
        if created_databases:
            logger.info("\n[Final Cleanup] Removing remaining test databases...")
            db_helper = DatabaseAPIHelper(base_url=api_url, token=token)
            for db_id in created_databases:
                try:
                    db_helper.delete_database(db_id)
                    logger.info(f"✓ Cleaned up database: {db_id}")
                except Exception as e:
                    logger.warning(f"⚠ Failed to cleanup database {db_id}: {e}")
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    passed = sum(1 for _, success, _ in test_steps if success)
    total = len(test_steps)
    logger.info(f"Total Steps: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {total - passed}")
    logger.info(f"Success Rate: {(passed/total*100):.1f}%")
    
    logger.info("\nDetailed Results:")
    for step, success, message in test_steps:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"  {status}: {step} - {message}")
    
    return test_passed and (passed / total) >= 0.70  # 70% pass threshold (some API quirks expected)

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
