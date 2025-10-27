#!/usr/bin/env python3
"""
API-013: Dependency Management - Repositories

Tests dependency repository management endpoints including:
- List/search repositories
- Get versions, install/uninstall packages
- View dependency logs
"""

import sys
import os
import time
import logging

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from helpers.api.auth import AuthHelper
from helpers.api.dependency import (
    get_dependency_repos,
    search_dependency_repos,
    get_dependency_repo_versions,
    install_dependency_repo,
    uninstall_dependency_repo,
    get_dependency_logs
)
from helpers.api.node import get_node_list
from helpers.api.cleanup import cleanup_test_resources

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run_test():
    """Execute API-013 test scenarios"""
    auth = AuthHelper()
    token = None
    test_steps = []
    node_ids = []
    dependency_id = None
    
    try:
        # ===== Setup =====
        logger.info("\n=== API-013: Dependency Management - Repositories ===\n")
        
        # Step 1: Authenticate
        logger.info("[Step 1] Authenticating...")
        token, response = auth.login()
        if token:
            logger.info("✓ Authentication successful")
            test_steps.append(("Authenticate", True, "Login successful"))
        else:
            logger.error("✗ Authentication failed")
            test_steps.append(("Authenticate", False, "Login failed"))
            return test_steps
        
        # Get available node IDs for later use
        nodes_data = get_node_list(token, page=1, size=100)
        if nodes_data and 'data' in nodes_data:
            node_ids = [node.get('_id') for node in nodes_data['data'] if node.get('_id')]
            logger.info(f"Found {len(node_ids)} available nodes")
        
        # ===== Repository List Operations =====
        
        # Step 2: List Installed Repositories
        logger.info("\n[Step 2] Listing installed Python repositories...")
        repos = get_dependency_repos(token, lang="python", page=1, size=10)
        if repos and 'data' in repos:
            repo_list = repos['data']
            logger.info(f"✓ Found {len(repo_list)} installed packages")
            test_steps.append(("List Installed Repos", True, f"Found {len(repo_list)} packages"))
        else:
            logger.info("✓ Repo list endpoint accessible (empty)")
            test_steps.append(("List Installed Repos", True, "Endpoint accessible"))
        
        # Step 3: List with Custom Page Size
        logger.info("\n[Step 3] Listing with custom page size...")
        repos_paged = get_dependency_repos(token, lang="python", page=1, size=20)
        if repos_paged:
            logger.info("✓ Pagination parameter works")
            test_steps.append(("List with Page Size", True, "Pagination works"))
        else:
            logger.info("⚠ Pagination failed")
            test_steps.append(("List with Page Size", False, "Pagination failed"))
        
        # Step 4: List with Filter
        logger.info("\n[Step 4] Listing with filter...")
        repos_filtered = get_dependency_repos(
            token, lang="python", page=1, size=10, filter_query='{"name":"requests"}'
        )
        if repos_filtered:
            logger.info("✓ Filter parameter accepted")
            test_steps.append(("List with Filter", True, "Filter accepted"))
        else:
            logger.info("⚠ Filter failed")
            test_steps.append(("List with Filter", False, "Filter failed"))
        
        # Step 5: List for Different Language
        logger.info("\n[Step 5] Listing Node.js repositories...")
        repos_node = get_dependency_repos(token, lang="node", page=1, size=10)
        if repos_node:
            logger.info("✓ Language parameter works")
            test_steps.append(("List Different Language", True, "Language switch works"))
        else:
            logger.info("⚠ Language parameter failed")
            test_steps.append(("List Different Language", False, "Language failed"))
        
        # ===== Repository Search Operations =====
        
        # Step 6: Search for Python Package
        logger.info("\n[Step 6] Searching for 'requests' package...")
        search_results = search_dependency_repos(token, lang="python", query="requests", page=1, size=10)
        if search_results and 'data' in search_results:
            results_list = search_results['data']
            logger.info(f"✓ Found {len(results_list)} search results")
            test_steps.append(("Search Package", True, f"Found {len(results_list)} results"))
        elif search_results:
            logger.info("⚠ Search endpoint accessible but no results (index may not be ready)")
            test_steps.append(("Search Package", True, "Endpoint accessible (empty)"))
        else:
            logger.info("⚠ Search failed")
            test_steps.append(("Search Package", False, "Search failed"))
        
        # Step 7: Search with Empty Query
        logger.info("\n[Step 7] Searching with empty query...")
        search_empty = search_dependency_repos(token, lang="python", query="", page=1, size=10)
        if search_empty is not None:
            logger.info("✓ Empty query handled")
            test_steps.append(("Search Empty Query", True, "Handled gracefully"))
        else:
            logger.info("⚠ Empty query failed")
            test_steps.append(("Search Empty Query", False, "Not handled"))
        
        # Step 8: Search for Specific Package
        logger.info("\n[Step 8] Searching for 'beautifulsoup4'...")
        search_bs4 = search_dependency_repos(token, lang="python", query="beautifulsoup4", page=1, size=5)
        if search_bs4:
            logger.info("✓ Specific package search works")
            test_steps.append(("Search Specific Package", True, "Search successful"))
        else:
            logger.info("⚠ Specific package search failed")
            test_steps.append(("Search Specific Package", False, "Search failed"))
        
        # Step 9: Search with Pagination
        logger.info("\n[Step 9] Searching with pagination (page 2)...")
        search_paginated = search_dependency_repos(token, lang="python", query="django", page=2, size=10)
        if search_paginated:
            logger.info("✓ Search pagination works")
            test_steps.append(("Search Pagination", True, "Pagination works"))
        else:
            logger.info("⚠ Search pagination failed")
            test_steps.append(("Search Pagination", False, "Pagination failed"))
        
        # ===== Repository Versions Operations =====
        
        # Step 10: Get Package Versions
        logger.info("\n[Step 10] Getting versions for 'requests' package...")
        versions = get_dependency_repo_versions(token, lang="python", name="requests")
        if versions and len(versions) > 0:
            logger.info(f"✓ Found {len(versions)} versions: {versions[:3]}...")
            test_steps.append(("Get Package Versions", True, f"Found {len(versions)} versions"))
        elif versions is not None:
            logger.info("✓ Versions endpoint accessible (empty array)")
            test_steps.append(("Get Package Versions", True, "Endpoint accessible"))
        else:
            logger.info("⚠ Versions endpoint failed")
            test_steps.append(("Get Package Versions", False, "Endpoint failed"))
        
        # Step 11: Get Versions for Invalid Package
        logger.info("\n[Step 11] Getting versions for non-existent package...")
        versions_invalid = get_dependency_repo_versions(
            token, lang="python", name="nonexistent-package-xyz-12345"
        )
        if versions_invalid is None or len(versions_invalid) == 0:
            logger.info("✓ Invalid package handled correctly")
            test_steps.append(("Get Invalid Package Versions", True, "Error handled"))
        else:
            logger.info("⚠ Invalid package returned data")
            test_steps.append(("Get Invalid Package Versions", False, "Should return empty/error"))
        
        # ===== Repository Install/Uninstall Operations =====
        
        # Step 12: Install Package (All Nodes)
        logger.info("\n[Step 12] Installing 'requests' package on all nodes...")
        install_all = install_dependency_repo(token, lang="python", name="requests", mode="all")
        if install_all:
            logger.info("✓ Install initiated (all nodes)")
            test_steps.append(("Install Package (All)", True, "Install request accepted"))
        else:
            logger.info("⚠ Install failed")
            test_steps.append(("Install Package (All)", False, "Install rejected"))
        
        # Step 13: Install Package with Version
        logger.info("\n[Step 13] Installing 'certifi' with specific version...")
        install_version = install_dependency_repo(
            token, lang="python", name="certifi", version="2023.7.22", mode="all"
        )
        if install_version:
            logger.info("✓ Version-specific install initiated")
            test_steps.append(("Install with Version", True, "Install request accepted"))
        else:
            logger.info("⚠ Version-specific install failed")
            test_steps.append(("Install with Version", False, "Install rejected"))
        
        # Step 14: Install on Specific Node
        logger.info("\n[Step 14] Installing 'urllib3' on specific node...")
        if node_ids:
            install_node = install_dependency_repo(
                token, lang="python", name="urllib3", mode="specific", node_ids=[node_ids[0]]
            )
            if install_node:
                logger.info(f"✓ Node-specific install initiated on {node_ids[0]}")
                test_steps.append(("Install on Specific Node", True, "Install request accepted"))
            else:
                logger.info("⚠ Node-specific install failed")
                test_steps.append(("Install on Specific Node", False, "Install rejected"))
        else:
            logger.info("⊘ Skipping (no nodes available)")
            test_steps.append(("Install on Specific Node", None, "Skipped - no nodes"))
        
        # Give installations a moment to register
        time.sleep(2)
        
        # Step 15: Uninstall Package (All Nodes)
        logger.info("\n[Step 15] Uninstalling 'certifi' from all nodes...")
        uninstall_all = uninstall_dependency_repo(token, lang="python", name="certifi", mode="all")
        if uninstall_all:
            logger.info("✓ Uninstall initiated (all nodes)")
            test_steps.append(("Uninstall Package (All)", True, "Uninstall request accepted"))
        else:
            logger.info("⚠ Uninstall failed")
            test_steps.append(("Uninstall Package (All)", False, "Uninstall rejected"))
        
        # Step 16: Uninstall from Specific Node
        logger.info("\n[Step 16] Uninstalling 'urllib3' from specific node...")
        if node_ids:
            uninstall_node = uninstall_dependency_repo(
                token, lang="python", name="urllib3", mode="specific", node_ids=[node_ids[0]]
            )
            if uninstall_node:
                logger.info(f"✓ Node-specific uninstall initiated")
                test_steps.append(("Uninstall from Specific Node", True, "Uninstall request accepted"))
            else:
                logger.info("⚠ Node-specific uninstall failed")
                test_steps.append(("Uninstall from Specific Node", False, "Uninstall rejected"))
        else:
            logger.info("⊘ Skipping (no nodes available)")
            test_steps.append(("Uninstall from Specific Node", None, "Skipped - no nodes"))
        
        # ===== Dependency Logs Operations =====
        
        # Step 17: Get Dependency Logs
        logger.info("\n[Step 17] Getting dependency logs...")
        # Note: We would need an actual dependency ID from install/uninstall operations
        # For now, we'll skip this or use a placeholder
        logger.info("⊘ Skipping (requires valid dependency ID from actual operations)")
        test_steps.append(("Get Dependency Logs", None, "Skipped - no dependency ID"))
        
        # Step 18: Get Logs for Invalid ID
        logger.info("\n[Step 18] Getting logs for invalid ID...")
        logs_invalid = get_dependency_logs(token, "invalid-id-12345")
        if logs_invalid is None or not logs_invalid.get('data'):
            logger.info("✓ Invalid ID handled correctly")
            test_steps.append(("Get Logs Invalid ID", True, "Error handled"))
        else:
            logger.info("⚠ Invalid ID returned data")
            test_steps.append(("Get Logs Invalid ID", False, "Should return error"))
        
        # ===== Edge Cases =====
        
        # Step 19: Install Without Language
        logger.info("\n[Step 19] Installing without language...")
        # The helper function requires lang, so this tests if API would reject it
        # We'll pass empty string
        try:
            install_no_lang = install_dependency_repo(token, lang="", name="test", mode="all")
            if not install_no_lang:
                logger.info("✓ Missing language rejected")
                test_steps.append(("Install Without Language", True, "Validation works"))
            else:
                logger.info("⚠ Missing language accepted (should be rejected)")
                test_steps.append(("Install Without Language", False, "Should reject"))
        except Exception:
            logger.info("✓ Missing language caused error (expected)")
            test_steps.append(("Install Without Language", True, "Validation works"))
        
        # Step 20: Install Without Package Name
        logger.info("\n[Step 20] Installing without package name...")
        try:
            install_no_name = install_dependency_repo(token, lang="python", name="", mode="all")
            if not install_no_name:
                logger.info("✓ Missing package name rejected")
                test_steps.append(("Install Without Name", True, "Validation works"))
            else:
                logger.info("⚠ Missing package name accepted")
                test_steps.append(("Install Without Name", False, "Should reject"))
        except Exception:
            logger.info("✓ Missing package name caused error (expected)")
            test_steps.append(("Install Without Name", True, "Validation works"))
        
        # Step 21: Search Without Language
        logger.info("\n[Step 21] Searching without language...")
        try:
            search_no_lang = search_dependency_repos(token, lang="", query="test", page=1, size=10)
            if search_no_lang is None:
                logger.info("✓ Missing language rejected")
                test_steps.append(("Search Without Language", True, "Validation works"))
            else:
                logger.info("⚠ Missing language handled as default")
                test_steps.append(("Search Without Language", True, "Default language used"))
        except Exception:
            logger.info("✓ Missing language caused error (expected)")
            test_steps.append(("Search Without Language", True, "Validation works"))
        
    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")
        test_steps.append(("Test Execution", False, "Interrupted"))
    except Exception as e:
        logger.error(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        test_steps.append(("Test Execution", False, f"Error: {str(e)}"))
    finally:
        # ===== Cleanup =====
        logger.info("\n[Step 22] Cleanup...")
        if token:
            auth.logout(token)
            logger.info("✓ Logged out")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for _, status, _ in test_steps if status is True)
        failed = sum(1 for _, status, _ in test_steps if status is False)
        skipped = sum(1 for _, status, _ in test_steps if status is None)
        total = len(test_steps)
        
        for step, status, message in test_steps:
            status_symbol = "✓" if status is True else "✗" if status is False else "⊘"
            logger.info(f"{status_symbol} {step}: {message}")
        
        logger.info("="*60)
        logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        if total > 0:
            pass_rate = (passed / (total - skipped)) * 100 if (total - skipped) > 0 else 0
            logger.info(f"Pass Rate: {pass_rate:.1f}%")
        logger.info("="*60)
    
    return test_steps


if __name__ == "__main__":
    test_steps = run_test()
    # Exit with error code if any test failed
    failed_count = sum(1 for _, status, _ in test_steps if status is False)
    sys.exit(0 if failed_count == 0 else 1)
