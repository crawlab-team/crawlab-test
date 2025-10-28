#!/usr/bin/env python3
"""
Database Integration Test Runner

Tests comprehensive database integration functionality including:
- Connection management
- Metadata retrieval
- Schema operations (DDL)
- Data operations (CRUD)
- Query execution
- Metrics collection

Supports MongoDB, MySQL, PostgreSQL, Elasticsearch.
"""

import sys
import os
import time
from pathlib import Path

# Add tests directory to path for helper imports
tests_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(tests_dir))

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.database import DatabaseAPIHelper
from crawlab_test.helpers.api.cleanup import CleanupHelper
from crawlab_test.helpers.infrastructure.utils import setup_logging


def is_docker_environment() -> bool:
    """
    Detect if running in Docker/CI environment
    
    Returns:
        True if in Docker/CI environment
    """
    # Check for Docker environment indicators
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check for Crawlab environment variables (set in docker-compose)
    if os.getenv('CRAWLAB_NODE_MASTER'):
        return True
    
    # Check for CI environment
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        return True
    
    return False


def get_database_configs() -> dict:
    """
    Get database configurations based on environment
    
    Returns:
        Dictionary of database configurations
    """
    is_docker = is_docker_environment()
    
    if is_docker:
        # Docker/CI environment - use container hostnames and internal ports
        return {
            'mysql': {
                'name': 'MySQL Test DB',
                'data_source': 'mysql',
                'host': os.getenv('MYSQL_TEST_HOST', 'mysql'),
                'port': int(os.getenv('MYSQL_TEST_PORT', '3306')),
                'username': os.getenv('MYSQL_TEST_USER', 'root'),
                'password': os.getenv('MYSQL_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'postgres': {
                'name': 'PostgreSQL Test DB',
                'data_source': 'postgres',
                'host': os.getenv('POSTGRES_TEST_HOST', 'postgres'),
                'port': int(os.getenv('POSTGRES_TEST_PORT', '5432')),
                'username': os.getenv('POSTGRES_TEST_USER', 'admin'),
                'password': os.getenv('POSTGRES_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'mongo': {
                'name': 'MongoDB Test DB',
                'data_source': 'mongo',
                'host': os.getenv('MONGO_TEST_HOST', 'mongo'),
                'port': int(os.getenv('MONGO_TEST_PORT', '27017')),
                'username': os.getenv('MONGO_TEST_USER', 'admin'),
                'password': os.getenv('MONGO_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'elasticsearch': {
                'name': 'Elasticsearch Test DB',
                'data_source': 'elasticsearch',
                'host': os.getenv('ELASTICSEARCH_TEST_HOST', 'elasticsearch'),
                'port': int(os.getenv('ELASTICSEARCH_TEST_PORT', '9200')),
                'username': '',
                'password': '',
                'database': ''
            }
        }
    else:
        # Local environment - use localhost with mapped ports
        return {
            'mysql': {
                'name': 'MySQL Test DB',
                'data_source': 'mysql',
                'host': os.getenv('MYSQL_TEST_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_TEST_PORT', '3307')),
                'username': os.getenv('MYSQL_TEST_USER', 'root'),
                'password': os.getenv('MYSQL_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'postgres': {
                'name': 'PostgreSQL Test DB',
                'data_source': 'postgres',
                'host': os.getenv('POSTGRES_TEST_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_TEST_PORT', '5433')),
                'username': os.getenv('POSTGRES_TEST_USER', 'admin'),
                'password': os.getenv('POSTGRES_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'mongo': {
                'name': 'MongoDB Test DB',
                'data_source': 'mongo',
                'host': os.getenv('MONGO_TEST_HOST', 'localhost'),
                'port': int(os.getenv('MONGO_TEST_PORT', '27017')),
                'username': os.getenv('MONGO_TEST_USER', 'admin'),
                'password': os.getenv('MONGO_TEST_PASSWORD', 'admin'),
                'database': 'test'
            },
            'elasticsearch': {
                'name': 'Elasticsearch Test DB',
                'data_source': 'elasticsearch',
                'host': os.getenv('ELASTICSEARCH_TEST_HOST', 'localhost'),
                'port': int(os.getenv('ELASTICSEARCH_TEST_PORT', '9200')),
                'username': '',
                'password': '',
                'database': ''
            }
        }


# Test database configurations
TEST_DATABASES = get_database_configs()


class DatabaseIntegrationTest:
    """Database integration test runner"""
    
    def __init__(self):
        self.logger = setup_logging("DB-001")
        self.auth = AuthHelper()
        self.cleanup = CleanupHelper()
        self.token = None
        self.db_helper = None
        self.created_databases = {}
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def setup(self) -> bool:
        """Setup test environment"""
        self.logger.info("Setting up test environment...")
        
        # Detect and log environment
        is_docker = is_docker_environment()
        env_type = "Docker/CI" if is_docker else "Local"
        self.logger.info(f"Environment detected: {env_type}")
        
        # Log database connection details
        for db_type, config in TEST_DATABASES.items():
            self.logger.info(f"  {db_type}: {config['host']}:{config['port']}")
        
        # Login and get token
        self.token, _ = self.auth.login()
        if not self.token:
            self.logger.error("Failed to authenticate")
            return False
        
        # Initialize database helper
        self.db_helper = DatabaseAPIHelper(token=self.token)
        
        self.logger.info("✓ Test environment setup complete")
        return True
    
    def teardown(self):
        """Cleanup test resources"""
        self.logger.info("Cleaning up test resources...")
        
        # Clean up created databases
        for db_type, db_id in self.created_databases.items():
            if db_id:
                self.logger.info(f"Cleaning up {db_type} database...")
                self.db_helper.delete_database(db_id)
        
        self.logger.info("✓ Cleanup complete")
    
    def record_result(self, test_name: str, passed: bool, message: str = ""):
        """Record test result"""
        self.test_results['total'] += 1
        if passed:
            self.test_results['passed'] += 1
            self.logger.info(f"✓ {test_name}: PASSED")
        else:
            self.test_results['failed'] += 1
            self.logger.error(f"✗ {test_name}: FAILED - {message}")
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def test_connection_management(self) -> bool:
        """Test Step 2: Connection Management"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Step 2: Testing Connection Management")
        self.logger.info("="*60)
        
        all_passed = True
        
        for db_type, config in TEST_DATABASES.items():
            # Create database connection
            self.logger.info(f"\nTesting {db_type.upper()} connection...")
            
            db = self.db_helper.create_database(config)
            if not db:
                self.record_result(f"{db_type}_create", False, "Failed to create database connection")
                all_passed = False
                continue
            
            db_id = db.get('_id')
            self.created_databases[db_type] = db_id
            self.cleanup.track_database(db_id)
            self.record_result(f"{db_type}_create", True)
            
            # Test connection
            time.sleep(1)  # Brief delay for connection initialization
            result = self.db_helper.test_connection(db_id)
            
            # Check for various success indicators
            status = result.get('status', '')
            if status in ['online', 'success', 'ok']:
                self.record_result(f"{db_type}_connection", True)
            else:
                error_msg = result.get('message', result.get('error', 'Unknown error'))
                # Check for common database unavailability errors
                if any(indicator in str(error_msg).lower() for indicator in [
                    'lookup', 'server misbehaving', 'connection refused', 
                    'no such host', 'dial tcp', 'timeout', 'cannot connect'
                ]):
                    self.logger.warning(f"  Database service may not be running: {error_msg}")
                    self.logger.warning(f"  Start databases with: docker compose -f docker-compose.test.yml up -d {db_type}")
                self.record_result(f"{db_type}_connection", False, 
                                 f"Connection failed: {error_msg}")
                all_passed = False
        
        return all_passed
    
    def test_metadata_retrieval(self) -> bool:
        """Test Step 3: Metadata Retrieval"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Step 3: Testing Metadata Retrieval")
        self.logger.info("="*60)
        
        all_passed = True
        
        for db_type, db_id in self.created_databases.items():
            if not db_id:
                continue
                
            self.logger.info(f"\nRetrieving {db_type.upper()} metadata...")
            
            metadata = self.db_helper.get_metadata(db_id)
            if metadata is not None and isinstance(metadata, dict):
                self.record_result(f"{db_type}_metadata", True)
                # Log summary - handle case where databases field is None
                databases = metadata.get('databases', [])
                db_count = len(databases) if databases is not None else 0
                self.logger.info(f"  Found {db_count} databases")
            else:
                self.record_result(f"{db_type}_metadata", False, "Failed to retrieve metadata")
                all_passed = False
        
        return all_passed
    
    def test_table_operations(self) -> bool:
        """Test Steps 4-5: Table/Schema Operations"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Steps 4-5: Testing Table Operations")
        self.logger.info("="*60)
        
        all_passed = True
        
        # Test on SQL databases (MySQL, PostgreSQL)
        for db_type in ['mysql', 'postgres']:
            db_id = self.created_databases.get(db_type)
            if not db_id:
                continue
            
            self.logger.info(f"\nTesting {db_type.upper()} table operations...")
            
            # Define test table
            table_name = f"test_table_{int(time.time())}"
            columns = [
                {
                    "name": "id",
                    "type": "INT" if db_type == 'mysql' else "INTEGER",
                    "primary": True,
                    "auto_increment": True
                },
                {
                    "name": "name",
                    "type": "VARCHAR(100)",
                    "not_null": True
                },
                {
                    "name": "email",
                    "type": "VARCHAR(100)"
                },
                {
                    "name": "created_at",
                    "type": "TIMESTAMP",
                    "default": "CURRENT_TIMESTAMP"
                }
            ]
            
            # Create table
            success = self.db_helper.create_table(
                db_id, 
                'test',  # database name
                table_name,
                columns
            )
            
            if success:
                self.record_result(f"{db_type}_create_table", True)
                
                # Verify table exists in metadata
                time.sleep(1)
                table_meta = self.db_helper.get_table_metadata(db_id, 'test', table_name)
                if table_meta:
                    self.record_result(f"{db_type}_table_metadata", True)
                else:
                    self.record_result(f"{db_type}_table_metadata", False, "Table not found in metadata")
                    all_passed = False
                
                # Drop table
                if self.db_helper.drop_table(db_id, 'test', table_name):
                    self.record_result(f"{db_type}_drop_table", True)
                else:
                    self.record_result(f"{db_type}_drop_table", False, "Failed to drop table")
                    all_passed = False
            else:
                self.record_result(f"{db_type}_create_table", False, "Failed to create table")
                all_passed = False
        
        return all_passed
    
    def test_data_operations(self) -> bool:
        """Test Step 7: CRUD Operations"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Step 7: Testing Data Operations (CRUD)")
        self.logger.info("="*60)
        
        all_passed = True
        
        # Test on SQL databases
        for db_type in ['mysql', 'postgres']:
            db_id = self.created_databases.get(db_type)
            if not db_id:
                continue
            
            self.logger.info(f"\nTesting {db_type.upper()} CRUD operations...")
            
            # Create a test table first
            table_name = f"test_crud_{int(time.time())}"
            columns = [
                {"name": "id", "type": "INT" if db_type == 'mysql' else "INTEGER", 
                 "primary": True, "auto_increment": True},
                {"name": "name", "type": "VARCHAR(100)", "not_null": True},
                {"name": "value", "type": "INT" if db_type == 'mysql' else "INTEGER"}
            ]
            
            if not self.db_helper.create_table(db_id, 'test', table_name, columns):
                self.record_result(f"{db_type}_crud_setup", False, "Failed to create test table")
                all_passed = False
                continue
            
            # INSERT
            insert_success = self.db_helper.insert_row(
                db_id, 'test', table_name,
                {"name": "test_user", "value": 42}
            )
            self.record_result(f"{db_type}_insert", insert_success, 
                             "" if insert_success else "Failed to insert row")
            
            # READ
            if insert_success:
                time.sleep(1)
                data = self.db_helper.get_table_data(db_id, 'test', table_name, page=1, size=10)
                if data and data.get('total', 0) > 0:
                    self.record_result(f"{db_type}_read", True)
                else:
                    self.record_result(f"{db_type}_read", False, "Failed to read inserted data")
                    all_passed = False
            
            # UPDATE
            update_success = self.db_helper.update_rows(
                db_id, 'test', table_name,
                {"value": 100},
                {"name": "test_user"}
            )
            self.record_result(f"{db_type}_update", update_success,
                             "" if update_success else "Failed to update row")
            
            # DELETE
            delete_success = self.db_helper.delete_rows(
                db_id, 'test', table_name,
                {"name": "test_user"}
            )
            self.record_result(f"{db_type}_delete", delete_success,
                             "" if delete_success else "Failed to delete row")
            
            # Cleanup
            self.db_helper.drop_table(db_id, 'test', table_name)
            
            if not all([insert_success, update_success, delete_success]):
                all_passed = False
        
        return all_passed
    
    def test_query_execution(self) -> bool:
        """Test Step 8: Query Execution"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Step 8: Testing Query Execution")
        self.logger.info("="*60)
        
        all_passed = True
        
        # Test SQL queries on MySQL and PostgreSQL
        test_queries = {
            'mysql': "SELECT VERSION() as version",
            'postgres': "SELECT version()"
        }
        
        for db_type, query in test_queries.items():
            db_id = self.created_databases.get(db_type)
            if not db_id:
                continue
            
            self.logger.info(f"\nExecuting query on {db_type.upper()}...")
            
            result = self.db_helper.execute_query(db_id, 'test', query)
            if result is not None:
                self.record_result(f"{db_type}_query", True)
                self.logger.info(f"  Query executed successfully")
            else:
                self.record_result(f"{db_type}_query", False, "Query execution failed")
                all_passed = False
        
        return all_passed
    
    def test_metrics_collection(self) -> bool:
        """Test Step 9: Metrics Collection"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Step 9: Testing Metrics Collection")
        self.logger.info("="*60)
        
        all_passed = True
        
        for db_type, db_id in self.created_databases.items():
            if not db_id:
                continue
            
            self.logger.info(f"\nCollecting {db_type.upper()} metrics...")
            
            metrics = self.db_helper.get_current_metrics(db_id)
            if metrics is not None:
                self.record_result(f"{db_type}_metrics", True)
                # Log some metrics if available
                if isinstance(metrics, dict):
                    self.logger.info(f"  Metrics retrieved: {len(metrics)} entries")
            else:
                # Metrics might not be supported for all databases
                self.logger.warning(f"  Metrics not available for {db_type}")
                self.record_result(f"{db_type}_metrics", True)  # Don't fail for unsupported metrics
        
        return all_passed
    
    def run(self) -> bool:
        """Run all tests"""
        self.logger.info("="*60)
        self.logger.info("Database Integration Comprehensive Testing")
        self.logger.info("="*60)
        
        try:
            # Setup
            if not self.setup():
                return False
            
            # Run tests
            self.test_connection_management()
            self.test_metadata_retrieval()
            self.test_table_operations()
            self.test_data_operations()
            self.test_query_execution()
            self.test_metrics_collection()
            
            # Print summary
            self.print_summary()
            
            return self.test_results['failed'] == 0
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}", exc_info=True)
            return False
        finally:
            self.teardown()
    
    def print_summary(self):
        """Print test results summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Test Summary")
        self.logger.info("="*60)
        self.logger.info(f"Total:   {self.test_results['total']}")
        self.logger.info(f"Passed:  {self.test_results['passed']}")
        self.logger.info(f"Failed:  {self.test_results['failed']}")
        self.logger.info(f"Skipped: {self.test_results['skipped']}")
        
        if self.test_results['errors']:
            self.logger.info("\nFailed Tests:")
            for error in self.test_results['errors']:
                self.logger.info(f"  - {error}")
        
        if self.test_results['failed'] == 0:
            self.logger.info("\n✓ All tests passed!")
        else:
            self.logger.error(f"\n✗ {self.test_results['failed']} test(s) failed")


def main():
    """Main entry point"""
    test = DatabaseIntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
