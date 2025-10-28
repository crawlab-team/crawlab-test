#!/usr/bin/env python3
"""
Process Killer Utility
Simulates zombie tasks by killing processes while preserving database state.
This creates a mismatch between database status and actual process state for testing reconciliation.
"""

import argparse
import logging
import sys
import os
import time
import json
import signal
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.infrastructure.api_client import CrawlabAPIClient
from helpers.infrastructure.database import DatabaseHelper, TASK_STATUS_RUNNING
from helpers.infrastructure.utils import setup_logging, TestMetrics, load_config
from helpers.infrastructure.system import process_manager, ProcessManager

class ProcessKiller:
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.process_manager = ProcessManager()
        self.killed_processes = []
    
    def find_running_tasks_with_processes(self) -> List[Dict[str, Any]]:
        """Find running tasks that have associated processes"""
        running_tasks = self.db.get_tasks_by_status(TASK_STATUS_RUNNING)
        tasks_with_processes = []
        
        for task in running_tasks:
            pid = task.get('pid', 0)
            if pid and pid > 0:
                # Check if process actually exists
                if self.process_manager.is_process_running(pid):
                    tasks_with_processes.append(task)
                    self.logger.debug(f"Found running task {task['_id']} with PID {pid}")
        
        return tasks_with_processes
    
    def find_crawlab_processes(self, pattern: str = "crawlab") -> List[Tuple[int, str]]:
        """Find Crawlab-related processes by pattern"""
        processes = self.process_manager.find_processes_by_pattern(pattern)
        process_info = []
        
        for proc in processes:
            try:
                cmdline = ' '.join(proc.cmdline())
                process_info.append((proc.pid, cmdline))
                self.logger.debug(f"Found Crawlab process: PID {proc.pid} - {cmdline}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return process_info
    
    def create_test_processes(self, count: int = 3) -> List[Dict[str, Any]]:
        """Create test processes that simulate running tasks"""
        import subprocess
        created_processes = []
        
        for i in range(count):
            # Create a long-running test process
            try:
                # Use a simple sleep command that can be easily identified
                cmd = ['python3', '-c', f'import time; print("Test process {i} started"); time.sleep(3600)']
                proc = subprocess.Popen(cmd)
                
                # Create corresponding database task
                test_node = self.db.create_test_node(key=f"test-node-{i}")
                test_task = self.db.create_test_task(
                    status=TASK_STATUS_RUNNING,
                    node_id=test_node["_id"],
                    pid=proc.pid,
                    cmd=' '.join(cmd)
                )
                
                created_processes.append({
                    'task_id': test_task['_id'],
                    'node_id': test_node['_id'],
                    'pid': proc.pid,
                    'process': proc,
                    'cmd': ' '.join(cmd)
                })
                
                self.logger.info(f"Created test process: PID {proc.pid} for task {test_task['_id']}")
                
            except Exception as e:
                self.logger.error(f"Failed to create test process {i}: {e}")
        
        return created_processes
    
    def kill_specific_processes(self, pids: List[int], method: str = "SIGKILL") -> List[Dict[str, Any]]:
        """Kill specific processes by PID"""
        kill_results = []
        
        for pid in pids:
            try:
                # Get task info before killing
                tasks_collection = self.db.get_collection("tasks")
                task = tasks_collection.find_one({"pid": pid})
                
                result = {
                    'pid': pid,
                    'task_id': str(task['_id']) if task else None,
                    'method': method,
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': None
                }
                
                # Kill the process
                if method == "SIGKILL":
                    success = self.process_manager.kill_process(pid, force=True)
                elif method == "SIGTERM":
                    success = self.process_manager.kill_process(pid, force=False)
                else:
                    # Custom signal
                    try:
                        os.kill(pid, getattr(signal, method, signal.SIGTERM))
                        time.sleep(0.5)  # Give it time to die
                        success = not self.process_manager.is_process_running(pid)
                    except ProcessLookupError:
                        success = True  # Process already dead
                    except Exception as e:
                        result['error'] = str(e)
                        success = False
                
                result['success'] = success
                
                if success:
                    self.logger.info(f"✓ Killed process PID {pid} using {method}")
                    self.killed_processes.append(result)
                else:
                    self.logger.error(f"✗ Failed to kill process PID {pid}: {result.get('error', 'Unknown error')}")
                
                kill_results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error killing PID {pid}: {e}")
                kill_results.append({
                    'pid': pid,
                    'success': False,
                    'error': str(e),
                    'method': method,
                    'timestamp': datetime.now().isoformat()
                })
        
        return kill_results
    
    def kill_running_task_processes(self, count: int = 3, method: str = "SIGKILL") -> List[Dict[str, Any]]:
        """Kill processes for running tasks to create zombie tasks"""
        self.logger.info(f"Looking for {count} running task processes to kill...")
        
        running_tasks = self.find_running_tasks_with_processes()
        
        if len(running_tasks) < count:
            self.logger.warning(f"Only found {len(running_tasks)} running tasks with processes, requested {count}")
            # Create additional test processes if needed
            needed = count - len(running_tasks)
            if needed > 0:
                self.logger.info(f"Creating {needed} additional test processes...")
                test_processes = self.create_test_processes(needed)
                # Add the new test tasks to running_tasks
                for proc_info in test_processes:
                    task = self.db.get_task_by_id(proc_info['task_id'])
                    if task:
                        running_tasks.append(task)
        
        # Select tasks to kill
        tasks_to_kill = random.sample(running_tasks, min(count, len(running_tasks)))
        pids_to_kill = [task['pid'] for task in tasks_to_kill if task.get('pid', 0) > 0]
        
        self.logger.info(f"Killing {len(pids_to_kill)} processes: {pids_to_kill}")
        
        # Kill the processes (but leave database unchanged!)
        results = self.kill_specific_processes(pids_to_kill, method)
        
        # Verify zombie state
        zombie_count = 0
        for result in results:
            if result['success'] and result['task_id']:
                # Check that task is still marked as running in database
                task = self.db.get_task_by_id(result['task_id'])
                if task and task.get('status') == TASK_STATUS_RUNNING:
                    zombie_count += 1
                    self.logger.info(f"✓ Created zombie task: {result['task_id']} (DB: running, Process: dead)")
        
        self.logger.info(f"Successfully created {zombie_count} zombie tasks")
        return results
    
    def kill_processes_by_pattern(self, pattern: str, count: int = None, method: str = "SIGKILL") -> List[Dict[str, Any]]:
        """Kill processes matching a pattern"""
        self.logger.info(f"Finding processes matching pattern: {pattern}")
        
        processes = self.find_crawlab_processes(pattern)
        
        if not processes:
            self.logger.warning(f"No processes found matching pattern: {pattern}")
            return []
        
        # Limit to requested count
        if count and count < len(processes):
            processes = random.sample(processes, count)
        
        pids_to_kill = [pid for pid, cmdline in processes]
        self.logger.info(f"Killing {len(pids_to_kill)} processes matching '{pattern}': {pids_to_kill}")
        
        return self.kill_specific_processes(pids_to_kill, method)
    
    def simulate_process_crashes(self, crash_scenarios: List[str] = None) -> Dict[str, Any]:
        """Simulate various process crash scenarios"""
        if not crash_scenarios:
            crash_scenarios = ["SIGKILL", "SIGTERM", "SIGSEGV"]
        
        self.logger.info(f"Simulating process crashes with scenarios: {crash_scenarios}")
        
        results = {
            'scenarios': {},
            'total_killed': 0,
            'zombie_tasks_created': 0
        }
        
        for scenario in crash_scenarios:
            self.logger.info(f"Running crash scenario: {scenario}")
            scenario_results = self.kill_running_task_processes(count=2, method=scenario)
            
            results['scenarios'][scenario] = scenario_results
            successful_kills = sum(1 for r in scenario_results if r['success'])
            results['total_killed'] += successful_kills
            
            # Count zombie tasks (tasks still running in DB but process dead)
            for result in scenario_results:
                if result['success'] and result['task_id']:
                    task = self.db.get_task_by_id(result['task_id'])
                    if task and task.get('status') == TASK_STATUS_RUNNING:
                        results['zombie_tasks_created'] += 1
        
        return results
    
    def verify_zombie_state(self) -> Dict[str, Any]:
        """Verify that zombie tasks exist (DB shows running but process is dead)"""
        running_tasks = self.db.get_tasks_by_status(TASK_STATUS_RUNNING)
        zombie_tasks = []
        
        for task in running_tasks:
            pid = task.get('pid', 0)
            if pid and pid > 0:
                if not self.process_manager.is_process_running(pid):
                    zombie_tasks.append({
                        'task_id': str(task['_id']),
                        'pid': pid,
                        'node_id': str(task.get('node_id', '')),
                        'status_in_db': task.get('status'),
                        'process_exists': False
                    })
        
        verification = {
            'total_running_tasks': len(running_tasks),
            'zombie_tasks': len(zombie_tasks),
            'zombie_task_details': zombie_tasks,
            'verification_time': datetime.now().isoformat()
        }
        
        self.logger.info(f"Verification: {len(zombie_tasks)} zombie tasks out of {len(running_tasks)} running tasks")
        
        return verification
    
    def cleanup_killed_processes(self) -> bool:
        """Clean up any remaining test processes"""
        cleanup_count = 0
        
        # Kill any remaining test processes
        test_processes = self.process_manager.find_processes_by_pattern("Test process")
        for proc in test_processes:
            try:
                self.process_manager.kill_process(proc.pid, force=True)
                cleanup_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to cleanup process {proc.pid}: {e}")
        
        if cleanup_count > 0:
            self.logger.info(f"Cleaned up {cleanup_count} test processes")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Kill processes to simulate zombie tasks')
    parser.add_argument('--target', choices=['running-tasks', 'pattern', 'pids', 'simulate-crashes'],
                       default='running-tasks', help='Target for process killing')
    parser.add_argument('--method', choices=['SIGKILL', 'SIGTERM', 'SIGSEGV', 'SIGINT'],
                       default='SIGKILL', help='Method to kill processes')
    parser.add_argument('--count', type=int, default=3,
                       help='Number of processes to kill')
    parser.add_argument('--pattern', default='crawlab',
                       help='Process pattern to match (for pattern target)')
    parser.add_argument('--pids', nargs='+', type=int,
                       help='Specific PIDs to kill (for pids target)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify zombie state after killing')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up test processes')
    parser.add_argument('--output-json', help='Output results to JSON file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('process-killer')
    
    try:
        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        config = load_config(config_file)
        
        # Initialize components
        api_client = CrawlabAPIClient(args.master_url)
        db_helper = DatabaseHelper(config['mongodb']['uri'])
        db_helper.database_name = config['mongodb']['database']
        db_helper.connect()
        
        killer = ProcessKiller(api_client, db_helper)
        
        results = None
        
        if args.target == 'running-tasks':
            results = killer.kill_running_task_processes(args.count, args.method)
            logger.info(f"Killed {len([r for r in results if r['success']])} running task processes")
            
        elif args.target == 'pattern':
            results = killer.kill_processes_by_pattern(args.pattern, args.count, args.method)
            logger.info(f"Killed {len([r for r in results if r['success']])} processes matching '{args.pattern}'")
            
        elif args.target == 'pids':
            if not args.pids:
                logger.error("No PIDs specified for 'pids' target")
                sys.exit(1)
            results = killer.kill_specific_processes(args.pids, args.method)
            logger.info(f"Killed {len([r for r in results if r['success']])} specific processes")
            
        elif args.target == 'simulate-crashes':
            results = killer.simulate_process_crashes()
            logger.info(f"Simulated crashes: {results['total_killed']} processes killed, "
                       f"{results['zombie_tasks_created']} zombie tasks created")
        
        # Verify zombie state if requested
        if args.verify:
            verification = killer.verify_zombie_state()
            logger.info(f"Verification: {verification['zombie_tasks']} zombie tasks detected")
            if results:
                results['verification'] = verification
            else:
                results = verification
        
        # Cleanup if requested
        if args.cleanup:
            killer.cleanup_killed_processes()
        
        # Output results if requested
        if args.output_json and results:
            with open(args.output_json, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results written to {args.output_json}")
        
        # Clean up
        db_helper.disconnect()
        
    except Exception as e:
        logger.error(f"Process killing operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()