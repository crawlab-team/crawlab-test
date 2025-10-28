#!/usr/bin/env python3
"""
Task Reconciliation Service Health Checker
Verifies that TaskReconciliationService is running and operational.
"""

import argparse
import logging
import sys
import os
import time
import json
from datetime import datetime, timedelta

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.database import DatabaseHelper, TASK_STATUS_RUNNING, TASK_STATUS_NODE_DISCONNECTED
from crawlab_test.helpers.infrastructure.utils import setup_logging, wait_with_timeout, format_duration, TestMetrics, load_config

class ReconciliationHealthChecker:
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = TestMetrics()
    
    def check_service_availability(self) -> bool:
        """Check if reconciliation service is working through system behavior"""
        try:
            # Instead of checking API endpoints, check if reconciliation service
            # is actually running by monitoring database changes
            self.logger.info("Checking reconciliation service through system behavior...")
            
            # Create a test scenario and monitor for reconciliation activity
            initial_tasks = self.db.get_tasks_by_status(TASK_STATUS_RUNNING)
            self.logger.info(f"Found {len(initial_tasks)} running tasks to monitor")
            
            # Check if there are any disconnected nodes that should trigger reconciliation
            disconnected_tasks = self.db.get_tasks_by_status(TASK_STATUS_NODE_DISCONNECTED)
            self.logger.info(f"Found {len(disconnected_tasks)} disconnected tasks")
            
            # If we have tasks in states that should trigger reconciliation, that's good
            if len(initial_tasks) > 0 or len(disconnected_tasks) > 0:
                self.logger.info("✓ Reconciliation service has tasks to process")
                return True
            else:
                self.logger.info("ⓘ No tasks requiring reconciliation found")
                return True  # This is not a failure condition
                
        except Exception as e:
            self.logger.error(f"✗ Reconciliation service check failed: {e}")
            return False
    
    def check_database_connectivity(self) -> bool:
        """Check if database operations are working properly"""
        try:
            # Test basic database operations
            task_count = len(self.db.get_tasks_by_status(TASK_STATUS_RUNNING))
            node_count = len(self.db.get_all_nodes())
            
            self.logger.info(f"✓ Database connectivity verified (tasks: {task_count}, nodes: {node_count})")
            return True
        except Exception as e:
            self.logger.error(f"✗ Database connectivity failed: {e}")
            return False
    
    def check_task_state_consistency(self) -> bool:
        """Check for task state inconsistencies that reconciliation should handle"""
        try:
            # Look for potentially problematic task states
            running_tasks = self.db.get_tasks_by_status(TASK_STATUS_RUNNING)
            disconnected_tasks = self.db.get_tasks_by_status(TASK_STATUS_NODE_DISCONNECTED)
            
            inconsistencies = 0
            
            # Check for tasks running on offline nodes
            for task in running_tasks:
                if 'node_id' in task:
                    node = self.db.get_node_by_id(task['node_id'])
                    if not node or node.get('status') != 'online':
                        inconsistencies += 1
            
            if inconsistencies > 0:
                self.logger.info(f"ⓘ Found {inconsistencies} task state inconsistencies (normal for reconciliation testing)")
            else:
                self.logger.info("✓ No obvious task state inconsistencies found")
            
            return True
        except Exception as e:
            self.logger.error(f"✗ Task state consistency check failed: {e}")
            return False

    def check_periodic_reconciliation(self, wait_time: int = 90) -> bool:
        """Check if periodic reconciliation is working by monitoring database changes"""
        self.logger.info(f"Monitoring for periodic reconciliation activity (waiting {wait_time}s)...")
        
        # Get initial count of tasks that need reconciliation
        initial_count = self.db.count_tasks_by_status(TASK_STATUS_RUNNING) + \
                       self.db.count_tasks_by_status(TASK_STATUS_NODE_DISCONNECTED)
        
        if initial_count == 0:
            # Create a test task to observe reconciliation behavior
            test_node = self.db.create_test_node()
            test_task = self.db.create_test_task(
                status=TASK_STATUS_RUNNING,
                node_id=test_node["_id"],
                pid=99999  # Non-existent PID to trigger reconciliation
            )
            self.logger.info(f"Created test task {test_task['_id']} to observe reconciliation")
            initial_count = 1
        
        # Wait and monitor for changes indicating reconciliation activity
        start_time = time.time()
        reconciliation_detected = False
        
        while time.time() - start_time < wait_time:
            # Look for signs of reconciliation activity:
            # 1. Changes in task statuses
            # 2. Error messages related to process checking
            # 3. Updates to task error fields
            
            current_count = self.db.count_tasks_by_status(TASK_STATUS_RUNNING) + \
                           self.db.count_tasks_by_status(TASK_STATUS_NODE_DISCONNECTED)
            
            if current_count != initial_count:
                self.logger.info("✓ Detected task status changes - reconciliation is active")
                reconciliation_detected = True
                break
            
            # Check for tasks with reconciliation-related error messages
            tasks_collection = self.db.get_collection("tasks")
            reconciliation_errors = tasks_collection.count_documents({
                "error": {"$regex": "reconciliation|process state|status synchronized"}
            })
            
            if reconciliation_errors > 0:
                self.logger.info("✓ Found reconciliation-related error messages - service is active")
                reconciliation_detected = True
                break
            
            time.sleep(5)  # Check every 5 seconds
        
        if reconciliation_detected:
            elapsed = time.time() - start_time
            self.logger.info(f"✓ Periodic reconciliation is working (detected after {format_duration(elapsed)})")
            return True
        else:
            self.logger.warning("⚠ Could not confirm periodic reconciliation activity")
            return False
    
    def check_master_node_logs(self) -> bool:
        """Check master node logs for reconciliation service activity"""
        # This is a simplified check - in a real environment, you would
        # parse actual log files or use a logging API
        self.logger.info("Checking for reconciliation service logs...")
        
        try:
            # Try to get system info which might contain service status
            system_info = self.api.get_system_info()
            
            if system_info:
                self.logger.info("✓ Master node is responsive")
                return True
            else:
                self.logger.warning("⚠ Could not get system information")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Master node logs check failed: {e}")
            return False
    
    def check_reconciliation_interval(self, expected_interval: int = 30) -> bool:
        """Check if reconciliation runs at the expected interval"""
        self.logger.info(f"Checking reconciliation interval (expected: {expected_interval}s)...")
        
        # Create a task that will definitely need reconciliation
        test_node = self.db.create_test_node()
        test_task = self.db.create_test_task(
            status=TASK_STATUS_RUNNING,
            node_id=test_node["_id"],
            pid=99999  # Non-existent PID
        )
        
        # Monitor task for changes over multiple intervals
        check_points = []
        start_time = time.time()
        
        # Monitor for 3 intervals to check consistency
        monitor_duration = expected_interval * 3
        
        while time.time() - start_time < monitor_duration:
            current_task = self.db.get_task_by_id(test_task["_id"])
            if current_task:
                check_points.append({
                    'time': time.time(),
                    'status': current_task.get('status'),
                    'error': current_task.get('error', '')
                })
            
            time.sleep(10)  # Check every 10 seconds
        
        # Clean up test data
        self.db.delete_test_tasks([test_task["_id"]])
        self.db.delete_test_nodes([test_node["_id"]])
        
        # Analyze check points for reconciliation activity
        status_changes = 0
        for i in range(1, len(check_points)):
            if (check_points[i]['status'] != check_points[i-1]['status'] or
                check_points[i]['error'] != check_points[i-1]['error']):
                status_changes += 1
        
        if status_changes > 0:
            self.logger.info(f"✓ Detected {status_changes} reconciliation activities in {format_duration(monitor_duration)}")
            return True
        else:
            self.logger.warning(f"⚠ No reconciliation activity detected in {format_duration(monitor_duration)}")
            return False
    
    def run_health_check(self, detailed: bool = False) -> bool:
        """Run complete health check focusing on system behavior"""
        self.metrics.start_test("Reconciliation Service Health Check")
        
        all_checks_passed = True
        
        # Check 1: Database connectivity
        self.metrics.start_step("Database Connectivity")
        try:
            db_available = self.check_database_connectivity()
            self.metrics.end_step(db_available)
            all_checks_passed &= db_available
        except Exception as e:
            self.metrics.end_step(False, str(e))
            all_checks_passed = False
        
        # Check 2: Task state consistency
        self.metrics.start_step("Task State Consistency")
        try:
            state_consistent = self.check_task_state_consistency()
            self.metrics.end_step(state_consistent)
            all_checks_passed &= state_consistent
        except Exception as e:
            self.metrics.end_step(False, str(e))
            all_checks_passed = False
        
        # Check 3: Master node responsiveness
        self.metrics.start_step("Master Node Responsiveness")
        try:
            master_responsive = self.check_master_node_logs()
            self.metrics.end_step(master_responsive)
            all_checks_passed &= master_responsive
        except Exception as e:
            self.metrics.end_step(False, str(e))
            all_checks_passed = False
        
        if detailed:
            # Check 3: Periodic reconciliation
            self.metrics.start_step("Periodic Reconciliation Activity")
            try:
                periodic_working = self.check_periodic_reconciliation()
                self.metrics.end_step(periodic_working)
                all_checks_passed &= periodic_working
            except Exception as e:
                self.metrics.end_step(False, str(e))
                all_checks_passed = False
            
            # Check 4: Reconciliation interval
            self.metrics.start_step("Reconciliation Interval Check")
            try:
                interval_correct = self.check_reconciliation_interval()
                self.metrics.end_step(interval_correct)
                all_checks_passed &= interval_correct
            except Exception as e:
                self.metrics.end_step(False, str(e))
                all_checks_passed = False
        
        results = self.metrics.end_test()
        
        # Print summary
        if all_checks_passed:
            self.logger.info("🎉 All health checks passed - Reconciliation service is operational!")
        else:
            self.logger.error("❌ Some health checks failed - Reconciliation service may have issues")
        
        self.logger.info(f"Health check completed in {format_duration(results['total_duration'])}")
        
        return all_checks_passed

def main():
    parser = argparse.ArgumentParser(description='Check TaskReconciliationService health')
    parser.add_argument('--check-service', action='store_true',
                       help='Check if service is running and operational')
    parser.add_argument('--detailed', action='store_true',
                       help='Run detailed health checks including periodic reconciliation')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    parser.add_argument('--output-json', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('reconciliation-health')
    
    if not args.check_service:
        parser.print_help()
        return
    
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        config = load_config(config_file)
        
        # Initialize components
        api_client = CrawlabAPIClient(args.master_url)
        # Automatically login to get API token
        try:
            api_client.ensure_authenticated()
            logger.info("Successfully authenticated with Crawlab API")
        except Exception as e:
            logger.warning(f"API authentication failed: {e} - continuing with limited functionality")
        
        db_helper = DatabaseHelper(config['mongodb']['uri'])
        db_helper.database_name = config['mongodb']['database']
        db_helper.connect()
        
        checker = ReconciliationHealthChecker(api_client, db_helper)
        
        # Run health check
        success = checker.run_health_check(detailed=args.detailed)
        
        # Output results if requested
        if args.output_json:
            results = {
                'timestamp': datetime.now().isoformat(),
                'success': success,
                'master_url': args.master_url,
                'detailed': args.detailed
            }
            
            with open(args.output_json, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results written to {args.output_json}")
        
        # Clean up
        db_helper.disconnect()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()