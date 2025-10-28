#!/usr/bin/env python3
"""
Cleanup utility for test data and temporary files
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Add tests directory to path for imports
TESTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

from helpers.infrastructure.database import DatabaseHelper
from helpers.infrastructure.utils import setup_logging
from helpers.infrastructure.system import process_manager, filesystem_manager

def cleanup_reconciliation_test_data():
    """Clean up data specific to reconciliation tests"""
    logger = logging.getLogger('cleanup')
    
    try:
        # Database cleanup
        db = DatabaseHelper()
        db.connect()
        
        # Remove test tasks, nodes, and spiders
        tasks_removed = db.delete_test_tasks()
        nodes_removed = db.delete_test_nodes()
        spiders_removed = db.delete_test_spiders()
        
        logger.info(f"Database cleanup: {tasks_removed} tasks, {nodes_removed} nodes, {spiders_removed} spiders")
        
        db.disconnect()
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")

def cleanup_temp_files():
    """Clean up temporary files created during testing"""
    logger = logging.getLogger('cleanup')
    
    patterns = [
        '/tmp/crawlab_test_*',
        '/tmp/task_reconciliation_*',
        '/tmp/test_spider_*',
        './test_results_*.json',
        './reconciliation_logs_*.txt'
    ]
    
    try:
        filesystem_manager.cleanup_temp_files(patterns)
        logger.info("Temporary files cleaned up")
    except Exception as e:
        logger.error(f"Temp file cleanup failed: {e}")

def cleanup_test_processes():
    """Clean up any test processes that might be running"""
    logger = logging.getLogger('cleanup')
    
    patterns = [
        'test_spider',
        'crawlab_test',
        'reconciliation_test'
    ]
    
    total_killed = 0
    for pattern in patterns:
        try:
            killed = process_manager.kill_processes_by_pattern(pattern, force=True)
            total_killed += killed
        except Exception as e:
            logger.error(f"Failed to kill processes matching '{pattern}': {e}")
    
    if total_killed > 0:
        logger.info(f"Killed {total_killed} test processes")

def cleanup_all_resources():
    """Clean up all test resources (wrapper for backward compatibility)"""
    cleanup_reconciliation_test_data()
    cleanup_temp_files()
    cleanup_test_processes()

def main():
    parser = argparse.ArgumentParser(description='Clean up test data and resources')
    parser.add_argument('--reconciliation-test-data', action='store_true',
                       help='Clean up reconciliation test data')
    parser.add_argument('--temp-files', action='store_true',
                       help='Clean up temporary files')
    parser.add_argument('--processes', action='store_true',
                       help='Clean up test processes')
    parser.add_argument('--all', action='store_true',
                       help='Clean up everything')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('cleanup')
    
    if not any([args.reconciliation_test_data, args.temp_files, args.processes, args.all]):
        parser.print_help()
        return
    
    logger.info("Starting cleanup operations...")
    
    if args.all or args.reconciliation_test_data:
        cleanup_reconciliation_test_data()
    
    if args.all or args.temp_files:
        cleanup_temp_files()
    
    if args.all or args.processes:
        cleanup_test_processes()
    
    logger.info("Cleanup completed")

if __name__ == '__main__':
    main()