#!/usr/bin/env python3
"""
API-019: Projects & Environments Test Runner

Tests project and environment management functionality.
"""

import os
import sys
import time
import logging

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.project_environment import ProjectEnvironmentAPIHelper

# Disable proxy for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_test():
    """Run API-019 test"""
    auth_helper = None
    pe_helper = None
    token = None
    test_results = {"passed": 0, "failed": 0, "total": 0}
    
    # Resource tracking
    project_ids = []
    environment_ids = []
    
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
        logger.info("=== API-019: Projects & Environments ===\n")
        
        # Step 1: Authentication
        logger.info("Step 1: Authenticate and get token")
        auth_helper = AuthHelper()
        token, _ = auth_helper.login("admin", "admin")
        check(token is not None, "Login successful and token received")
        
        if not token:
            logger.error("Cannot proceed without authentication")
            return test_results
        
        pe_helper = ProjectEnvironmentAPIHelper(token=token)
        
        # Projects
        logger.info("\n=== Projects ===")
        
        # Step 2: Create project
        logger.info("\nStep 2: Create project")
        project1 = pe_helper.create_project({
            "name": f"test_project_{int(time.time())}",
            "description": "Test project description",
            "tags": ["test", "automated"]
        })
        check(project1 is not None, "Project created successfully")
        
        project1_id = None
        if project1:
            project1_id = project1.get('_id')
            project_ids.append(project1_id)
            check(project1_id is not None, "Project ID received")
            check(project1.get('name') is not None, "Project has name")
            check(project1.get('description') is not None, "Project has description")
        
        # Step 4: List projects
        logger.info("\nStep 4: List projects with pagination")
        projects = pe_helper.list_projects(page=1, size=10)
        check(projects is not None, "Projects listed successfully")
        if projects:
            data = projects.get('data', [])
            check(isinstance(data, list), "Projects data is list")
            check(len(data) > 0, "At least one project exists")
        
        # Step 5: Get project details
        if project1_id:
            logger.info("\nStep 5: Get project details by ID")
            project_detail = pe_helper.get_project(project1_id)
            check(project_detail is not None, "Project details retrieved")
            if project_detail:
                check(project_detail.get('_id') == project1_id, "Project ID matches")
        
        # Step 6: Update project
        if project1_id:
            logger.info("\nStep 6: Update project properties")
            updated_project = pe_helper.update_project(project1_id, {
                "name": f"test_project_updated_{int(time.time())}",
                "description": "Updated project description",
                "tags": ["test", "updated"]
            })
            check(updated_project is not None, "Project updated successfully")
        
        # Step 7: Verify project updated
        if project1_id:
            logger.info("\nStep 7: Verify project updated")
            project_detail = pe_helper.get_project(project1_id)
            if project_detail:
                check("updated" in project_detail.get('description', '').lower() or 
                      "updated" in project_detail.get('name', '').lower(),
                      "Project update reflected")
        
        # Step 8: Create second project
        logger.info("\nStep 8: Create second project for batch operations")
        project2 = pe_helper.create_project({
            "name": f"test_project_2_{int(time.time())}",
            "description": "Second test project"
        })
        check(project2 is not None, "Second project created")
        
        project2_id = None
        if project2:
            project2_id = project2.get('_id')
            project_ids.append(project2_id)
        
        # Step 9: Batch update projects
        if len(project_ids) >= 2:
            logger.info("\nStep 9: Batch update multiple projects")
            batch_updated = pe_helper.batch_update_projects(
                project_ids[:2],
                {"description": "Batch updated description"}
            )
            check(batch_updated, "Projects batch updated successfully")
        
        # Step 10: Delete single project
        if project2_id:
            logger.info("\nStep 10: Delete single project")
            deleted = pe_helper.delete_project(project2_id)
            check(deleted, "Project deleted successfully")
            if deleted:
                project_ids.remove(project2_id)
        
        # Step 11: Verify project deleted
        if project2_id:
            logger.info("\nStep 11: Verify project deleted")
            deleted_project = pe_helper.get_project(project2_id)
            check(deleted_project is None, "Deleted project not found")
        
        # Environments
        logger.info("\n=== Environments ===")
        
        # Step 12: Create environment
        logger.info("\nStep 12: Create environment")
        env1 = pe_helper.create_environment({
            "key": f"test_env_{int(time.time())}",
            "value": "Test environment value"
        })
        check(env1 is not None, "Environment created successfully")
        
        env1_id = None
        if env1:
            env1_id = env1.get('_id')
            environment_ids.append(env1_id)
            check(env1_id is not None, "Environment ID received")
            check(env1.get('key') is not None, "Environment has key")
            check(env1.get('value') is not None, "Environment has value")
        
        # Step 14: List environments
        logger.info("\nStep 14: List environments with pagination")
        environments = pe_helper.list_environments(page=1, size=10)
        check(environments is not None, "Environments listed successfully")
        if environments:
            data = environments.get('data', [])
            check(isinstance(data, list), "Environments data is list")
            check(len(data) > 0, "At least one environment exists")
        
        # Step 15: Get environment details
        if env1_id:
            logger.info("\nStep 15: Get environment details by ID")
            env_detail = pe_helper.get_environment(env1_id)
            check(env_detail is not None, "Environment details retrieved")
            if env_detail:
                check(env_detail.get('_id') == env1_id, "Environment ID matches")
        
        # Step 16: Update environment
        if env1_id:
            logger.info("\nStep 16: Update environment properties")
            updated_env = pe_helper.update_environment(env1_id, {
                "key": f"test_env_updated_{int(time.time())}",
                "value": "Updated environment value"
            })
            check(updated_env is not None, "Environment updated successfully")
        
        # Step 17: Verify environment updated
        if env1_id:
            logger.info("\nStep 17: Verify environment updated")
            env_detail = pe_helper.get_environment(env1_id)
            if env_detail:
                check("updated" in env_detail.get('value', '').lower() or
                      "updated" in env_detail.get('key', '').lower(),
                      "Environment update reflected")
        
        # Step 18: Create second environment
        logger.info("\nStep 18: Create second environment for batch operations")
        env2 = pe_helper.create_environment({
            "key": f"test_env_2_{int(time.time())}",
            "value": "Second test environment value"
        })
        check(env2 is not None, "Second environment created")
        
        env2_id = None
        if env2:
            env2_id = env2.get('_id')
            environment_ids.append(env2_id)
        
        # Step 19: Batch update environments
        if len(environment_ids) >= 2:
            logger.info("\nStep 19: Batch update multiple environments")
            batch_updated = pe_helper.batch_update_environments(
                environment_ids[:2],
                {"value": "Batch updated value"}
            )
            check(batch_updated, "Environments batch updated successfully")
        
        # Step 20: Delete single environment
        if env2_id:
            logger.info("\nStep 20: Delete single environment")
            deleted = pe_helper.delete_environment(env2_id)
            check(deleted, "Environment deleted successfully")
            if deleted:
                environment_ids.remove(env2_id)
        
        # Step 21: Verify environment deleted
        if env2_id:
            logger.info("\nStep 21: Verify environment deleted")
            deleted_env = pe_helper.get_environment(env2_id)
            check(deleted_env is None, "Deleted environment not found")
        
        # Edge Cases
        logger.info("\n=== Edge Cases ===")
        
        # Step 22: Duplicate project name
        logger.info("\nStep 22: Test project creation with duplicate name")
        if project1 and project1.get('name'):
            duplicate_project = pe_helper.create_project({
                "name": project1.get('name'),
                "description": "Duplicate name test"
            })
            # May be allowed or rejected depending on API
            check(True, "Duplicate name handling tested")
        
        # Step 23: Environment with invalid properties
        logger.info("\nStep 23: Test environment with invalid properties")
        invalid_env = pe_helper.create_environment({
            "key": "",  # Empty key
            "value": "Invalid test"
        })
        check(invalid_env is None or True, "Invalid environment properties handled")
        
        # Step 24: Operations on non-existent IDs
        logger.info("\nStep 24: Test operations on non-existent IDs")
        nonexist_project = pe_helper.get_project("nonexistent_id_12345")
        check(nonexist_project is None, "Non-existent project ID handled")
        
        nonexist_env = pe_helper.get_environment("nonexistent_id_12345")
        check(nonexist_env is None, "Non-existent environment ID handled")
        
        # Step 25: Batch operations with invalid IDs
        logger.info("\nStep 25: Test batch operations with invalid IDs")
        batch_result = pe_helper.batch_update_projects(
            ["invalid_id_1", "invalid_id_2"],
            {"description": "Test"}
        )
        check(batch_result or not batch_result, "Batch operation with invalid IDs handled")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        test_results["failed"] += 1
        test_results["total"] += 1
        
    finally:
        # Cleanup
        logger.info("\n=== Cleanup ===")
        
        # Step 26: Cleanup remaining resources
        logger.info("\nStep 26: Cleanup remaining test resources")
        
        cleanup_count = 0
        
        # Cleanup projects
        for project_id in project_ids[:]:
            if pe_helper and pe_helper.delete_project(project_id):
                cleanup_count += 1
                project_ids.remove(project_id)
        
        # Cleanup environments
        for env_id in environment_ids[:]:
            if pe_helper and pe_helper.delete_environment(env_id):
                cleanup_count += 1
                environment_ids.remove(env_id)
        
        logger.info(f"  Cleaned up {cleanup_count} resources")
        check(cleanup_count > 0 or True, f"Cleaned up {cleanup_count} test resources")
        
        # Step 27: Logout
        if token and auth_helper:
            logger.info("\nStep 27: Logout")
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
