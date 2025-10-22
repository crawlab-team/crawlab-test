#!/usr/bin/env python3
"""
Reconciliation Monitor
Observes and validates reconciliation cycles and their effects on task statuses.
"""

import argparse
import logging
import sys
import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from bson import ObjectId

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.libs.api_client import CrawlabAPIClient
from helpers.libs.database import (DatabaseHelper, TASK_STATUS_RUNNING, TASK_STATUS_FINISHED,
                           TASK_STATUS_ERROR, TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_ABNORMAL)
from helpers.libs.utils import setup_logging, wait_with_timeout, format_duration, TestMetrics, load_config

class ReconciliationMonitor:
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitoring_data = []
        self.task_history = defaultdict(list)
        self.reconciliation_events = []
    
    def capture_initial_state(self) -> Dict[str, Any]:
        """Capture initial state of tasks before monitoring"""
        tasks_by_status = {}
        all_statuses = [TASK_STATUS_RUNNING, TASK_STATUS_NODE_DISCONNECTED, 
                       TASK_STATUS_FINISHED, TASK_STATUS_ERROR, TASK_STATUS_ABNORMAL]
        
        for status in all_statuses:
            tasks = self.db.get_tasks_by_status(status)
            tasks_by_status[status] = len(tasks)
            
            # Store individual task details for tracking
            for task in tasks:
                self.task_history[str(task['_id'])].append({
                    'timestamp': datetime.now(),
                    'status': task.get('status'),
                    'error': task.get('error', ''),
                    'pid': task.get('pid', 0),
                    'node_id': str(task.get('node_id', ''))
                })
        
        initial_state = {
            'timestamp': datetime.now().isoformat(),
            'tasks_by_status': tasks_by_status,
            'total_tasks': sum(tasks_by_status.values()),
            'reconciliation_candidates': tasks_by_status.get(TASK_STATUS_RUNNING, 0) + 
                                       tasks_by_status.get(TASK_STATUS_NODE_DISCONNECTED, 0)
        }
        
        self.logger.info(f"Initial state captured: {initial_state['total_tasks']} tasks, "
                        f"{initial_state['reconciliation_candidates']} candidates for reconciliation")
        
        return initial_state
    
    def monitor_single_cycle(self, expected_interval: int = 30) -> Dict[str, Any]:
        """Monitor a single reconciliation cycle"""
        self.logger.info(f"Monitoring reconciliation cycle (expected interval: {expected_interval}s)...")
        
        # Capture state before cycle
        pre_cycle_state = self.capture_task_snapshot()
        
        # Wait for reconciliation cycle to complete
        cycle_wait_time = expected_interval + 10  # Add buffer
        self.logger.info(f"Waiting {cycle_wait_time}s for reconciliation cycle...")
        time.sleep(cycle_wait_time)
        
        # Capture state after cycle
        post_cycle_state = self.capture_task_snapshot()
        
        # Analyze changes
        changes = self.analyze_state_changes(pre_cycle_state, post_cycle_state)
        
        cycle_result = {
            'pre_cycle': pre_cycle_state,
            'post_cycle': post_cycle_state,
            'changes': changes,
            'cycle_duration': cycle_wait_time,
            'reconciliation_detected': changes['total_changes'] > 0
        }
        
        if changes['total_changes'] > 0:
            self.logger.info(f"✓ Reconciliation cycle detected: {changes['total_changes']} changes")
            self.reconciliation_events.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'cycle_detected',
                'changes': changes
            })
        else:
            self.logger.info("No changes detected in this cycle")
        
        return cycle_result
    
    def capture_task_snapshot(self) -> Dict[str, Any]:
        """Capture current snapshot of all tasks"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'tasks': {},
            'status_counts': defaultdict(int)
        }
        
        # Get all tasks
        tasks_collection = self.db.get_collection("tasks")
        all_tasks = list(tasks_collection.find({}))
        
        for task in all_tasks:
            task_id = str(task['_id'])
            task_data = {
                'status': task.get('status'),
                'error': task.get('error', ''),
                'pid': task.get('pid', 0),
                'node_id': str(task.get('node_id', '')),
                'updated_at': task.get('updated_at', 0)
            }
            
            snapshot['tasks'][task_id] = task_data
            snapshot['status_counts'][task_data['status']] += 1
        
        return snapshot
    
    def analyze_state_changes(self, before: Dict, after: Dict) -> Dict[str, Any]:
        """Analyze changes between two snapshots"""
        changes = {
            'status_changes': [],
            'error_changes': [],
            'new_errors': [],
            'reconciliation_signatures': [],
            'total_changes': 0
        }
        
        # Compare task states
        for task_id in before['tasks']:
            if task_id not in after['tasks']:
                continue  # Task was deleted
            
            before_task = before['tasks'][task_id]
            after_task = after['tasks'][task_id]
            
            # Check for status changes
            if before_task['status'] != after_task['status']:
                change = {
                    'task_id': task_id,
                    'from_status': before_task['status'],
                    'to_status': after_task['status'],
                    'likely_reconciliation': self.is_likely_reconciliation_change(
                        before_task['status'], after_task['status']
                    )
                }
                changes['status_changes'].append(change)
                changes['total_changes'] += 1
                
                if change['likely_reconciliation']:
                    changes['reconciliation_signatures'].append(change)
            
            # Check for error message changes
            if before_task['error'] != after_task['error']:
                error_change = {
                    'task_id': task_id,
                    'old_error': before_task['error'],
                    'new_error': after_task['error'],
                    'reconciliation_related': self.is_reconciliation_error(after_task['error'])
                }
                changes['error_changes'].append(error_change)
                
                if error_change['reconciliation_related']:
                    changes['reconciliation_signatures'].append(error_change)
                    changes['total_changes'] += 1
        
        # Analyze status distribution changes
        changes['status_distribution_changes'] = {}
        for status in set(list(before['status_counts'].keys()) + list(after['status_counts'].keys())):
            before_count = before['status_counts'].get(status, 0)
            after_count = after['status_counts'].get(status, 0)
            if before_count != after_count:
                changes['status_distribution_changes'][status] = {
                    'before': before_count,
                    'after': after_count,
                    'change': after_count - before_count
                }
        
        return changes
    
    def is_likely_reconciliation_change(self, from_status: str, to_status: str) -> bool:
        """Determine if a status change is likely due to reconciliation"""
        reconciliation_patterns = [
            # Running task found to be finished/error
            (TASK_STATUS_RUNNING, TASK_STATUS_FINISHED),
            (TASK_STATUS_RUNNING, TASK_STATUS_ERROR),
            (TASK_STATUS_RUNNING, TASK_STATUS_ABNORMAL),
            # Disconnected task restored or marked as error
            (TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_RUNNING),
            (TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_FINISHED),
            (TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_ERROR),
            # Running task marked as disconnected
            (TASK_STATUS_RUNNING, TASK_STATUS_NODE_DISCONNECTED),
        ]
        
        return (from_status, to_status) in reconciliation_patterns
    
    def is_reconciliation_error(self, error_message: str) -> bool:
        """Determine if an error message is reconciliation-related"""
        reconciliation_keywords = [
            'reconciliation',
            'process state',
            'status synchronized',
            'worker node offline',
            'process not found',
            'zombie task',
            'actual process status'
        ]
        
        if not error_message:
            return False
        
        error_lower = error_message.lower()
        return any(keyword in error_lower for keyword in reconciliation_keywords)
    
    def wait_for_reconciliation(self, timeout: int = 90) -> bool:
        """Wait for reconciliation activity to occur"""
        self.logger.info(f"Waiting for reconciliation activity (timeout: {timeout}s)...")
        
        start_time = time.time()
        initial_snapshot = self.capture_task_snapshot()
        
        while time.time() - start_time < timeout:
            time.sleep(5)  # Check every 5 seconds
            
            current_snapshot = self.capture_task_snapshot()
            changes = self.analyze_state_changes(initial_snapshot, current_snapshot)
            
            if changes['total_changes'] > 0:
                elapsed = time.time() - start_time
                self.logger.info(f"✓ Reconciliation activity detected after {format_duration(elapsed)}")
                self.logger.info(f"Changes: {changes['total_changes']} total, "
                               f"{len(changes['reconciliation_signatures'])} reconciliation signatures")
                return True
        
        self.logger.warning(f"No reconciliation activity detected within {timeout}s")
        return False
    
    def monitor_continuous(self, duration: int = 300, check_interval: int = 30) -> Dict[str, Any]:
        """Monitor reconciliation continuously for a period"""
        self.logger.info(f"Starting continuous monitoring for {format_duration(duration)}")
        
        start_time = time.time()
        monitoring_results = {
            'start_time': datetime.now().isoformat(),
            'duration': duration,
            'cycles': [],
            'total_cycles': 0,
            'cycles_with_activity': 0,
            'total_changes': 0,
            'reconciliation_effectiveness': 0.0
        }
        
        # Capture initial state
        initial_state = self.capture_initial_state()
        monitoring_results['initial_state'] = initial_state
        
        cycle_count = 0
        while time.time() - start_time < duration:
            cycle_count += 1
            self.logger.info(f"Monitoring cycle {cycle_count}")
            
            cycle_result = self.monitor_single_cycle(check_interval)
            monitoring_results['cycles'].append(cycle_result)
            
            if cycle_result['reconciliation_detected']:
                monitoring_results['cycles_with_activity'] += 1
                monitoring_results['total_changes'] += cycle_result['changes']['total_changes']
        
        # Capture final state
        final_state = self.capture_task_snapshot()
        monitoring_results['final_state'] = final_state
        monitoring_results['total_cycles'] = cycle_count
        
        # Calculate effectiveness
        if monitoring_results['total_cycles'] > 0:
            monitoring_results['reconciliation_effectiveness'] = \
                monitoring_results['cycles_with_activity'] / monitoring_results['total_cycles'] * 100
        
        # Overall analysis
        overall_changes = self.analyze_state_changes(initial_state, final_state)
        monitoring_results['overall_changes'] = overall_changes
        
        elapsed = time.time() - start_time
        monitoring_results['actual_duration'] = elapsed
        
        self.logger.info(f"Continuous monitoring completed:")
        self.logger.info(f"  Duration: {format_duration(elapsed)}")
        self.logger.info(f"  Cycles: {cycle_count}")
        self.logger.info(f"  Active cycles: {monitoring_results['cycles_with_activity']}")
        self.logger.info(f"  Effectiveness: {monitoring_results['reconciliation_effectiveness']:.1f}%")
        self.logger.info(f"  Total changes: {monitoring_results['total_changes']}")
        
        return monitoring_results
    
    def detect_reconciliation_patterns(self) -> Dict[str, Any]:
        """Analyze collected data for reconciliation patterns"""
        patterns = {
            'common_status_transitions': defaultdict(int),
            'reconciliation_intervals': [],
            'error_patterns': defaultdict(int),
            'node_specific_patterns': defaultdict(list)
        }
        
        # Analyze status transitions
        for cycle in getattr(self, 'monitoring_results', {}).get('cycles', []):
            for change in cycle.get('changes', {}).get('status_changes', []):
                transition = f"{change['from_status']} -> {change['to_status']}"
                patterns['common_status_transitions'][transition] += 1
        
        # Analyze error patterns
        for event in self.reconciliation_events:
            if 'changes' in event:
                for error_change in event['changes'].get('error_changes', []):
                    if error_change.get('reconciliation_related'):
                        patterns['error_patterns'][error_change['new_error']] += 1
        
        return patterns

def main():
    parser = argparse.ArgumentParser(description='Monitor reconciliation cycles and validate their effects')
    parser.add_argument('--wait-cycle', action='store_true',
                       help='Wait for a single reconciliation cycle')
    parser.add_argument('--continuous', action='store_true',
                       help='Monitor continuously for specified duration')
    parser.add_argument('--timeout', type=int, default=90,
                       help='Timeout for waiting operations (seconds)')
    parser.add_argument('--duration', type=int, default=300,
                       help='Duration for continuous monitoring (seconds)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Expected reconciliation interval (seconds)')
    parser.add_argument('--output-json', help='Output monitoring results to JSON file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('reconciliation-monitor')
    
    if not any([args.wait_cycle, args.continuous]):
        parser.print_help()
        return
    
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        config = load_config(config_file)
        
        # Initialize components
        api_client = CrawlabAPIClient(args.master_url)
        db_helper = DatabaseHelper(config['mongodb']['uri'])
        db_helper.database_name = config['mongodb']['database']
        db_helper.connect()
        
        monitor = ReconciliationMonitor(api_client, db_helper)
        
        results = None
        
        if args.wait_cycle:
            # Wait for a single reconciliation cycle
            reconciliation_detected = monitor.wait_for_reconciliation(args.timeout)
            results = {
                'operation': 'wait_cycle',
                'reconciliation_detected': reconciliation_detected,
                'timeout': args.timeout
            }
            
            if reconciliation_detected:
                logger.info("✓ Reconciliation cycle detected successfully")
            else:
                logger.error("✗ No reconciliation activity detected within timeout")
                sys.exit(1)
        
        if args.continuous:
            # Continuous monitoring
            results = monitor.monitor_continuous(args.duration, args.interval)
            monitor.monitoring_results = results  # Store for pattern analysis
            
            # Analyze patterns
            patterns = monitor.detect_reconciliation_patterns()
            results['patterns'] = patterns
            
            effectiveness = results.get('reconciliation_effectiveness', 0)
            if effectiveness > 50:
                logger.info(f"✓ Reconciliation service is working effectively ({effectiveness:.1f}%)")
            else:
                logger.warning(f"⚠ Low reconciliation effectiveness ({effectiveness:.1f}%)")
        
        # Output results if requested
        if args.output_json and results:
            # Convert datetime objects to strings for JSON serialization
            json_results = json.loads(json.dumps(results, default=str))
            
            with open(args.output_json, 'w') as f:
                json.dump(json_results, f, indent=2)
            logger.info(f"Results written to {args.output_json}")
        
        # Clean up
        db_helper.disconnect()
        
    except Exception as e:
        logger.error(f"Reconciliation monitoring failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()