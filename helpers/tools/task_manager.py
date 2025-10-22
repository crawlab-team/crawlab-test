#!/usr/bin/env python3
"""
Task Baseline Manager
Creates and manages baseline task states for testing reconciliation scenarios.
"""

import argparse
import logging
import sys
import os
import time
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.libs.api_client import CrawlabAPIClient
from helpers.libs.database import (DatabaseHelper, TASK_STATUS_PENDING, TASK_STATUS_ASSIGNED, 
                           TASK_STATUS_RUNNING, TASK_STATUS_FINISHED, TASK_STATUS_ERROR,
                           TASK_STATUS_CANCELLED, NODE_STATUS_ONLINE)
from helpers.libs.utils import setup_logging, TestMetrics, load_config
from helpers.libs.system import process_manager

class TaskBaselineManager:
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.created_resources = {
            'tasks': [],
            'nodes': [],
            'spiders': []
        }
    
    def create_test_nodes(self, count: int = 2) -> List[Dict[str, Any]]:
        """Create test worker nodes"""
        nodes = []
        for i in range(count):
            node = self.db.create_test_node(
                key=f"test-worker-{i+1}",
                name=f"Test Worker {i+1}",
                status=NODE_STATUS_ONLINE,
                available_runners=4,
                max_runners=4
            )
            nodes.append(node)
            self.created_resources['nodes'].append(node["_id"])
            self.logger.info(f"Created test node: {node['key']}")
        
        return nodes
    
    def create_test_spiders(self, count: int = 3) -> List[Dict[str, Any]]:
        """Create test spiders with varying characteristics"""
        spiders = []
        spider_types = [
            {
                'name': 'quick-spider',
                'cmd': 'python3 -c "import time; time.sleep(5); print(\\"Quick task completed\\")"',
                'description': 'Quick completing spider (5 seconds)'
            },
            {
                'name': 'long-spider', 
                'cmd': 'python3 -c "import time; time.sleep(300); print(\\"Long task completed\\")"',
                'description': 'Long running spider (5 minutes)'
            },
            {
                'name': 'error-spider',
                'cmd': 'python3 -c "import sys; print(\\"Error task\\"); sys.exit(1)"',
                'description': 'Spider that fails immediately'
            }
        ]
        
        for i, spider_type in enumerate(spider_types[:count]):
            spider = self.db.create_test_spider(
                name=f"{spider_type['name']}-{int(time.time())}",
                display_name=spider_type['description'],
                cmd=spider_type['cmd']
            )
            spiders.append(spider)
            self.created_resources['spiders'].append(spider["_id"])
            self.logger.info(f"Created test spider: {spider['name']}")
        
        return spiders
    
    def create_pending_tasks(self, nodes: List[Dict], spiders: List[Dict], count: int = 3) -> List[Dict[str, Any]]:
        """Create pending tasks"""
        tasks = []
        for i in range(count):
            node = random.choice(nodes)
            spider = random.choice(spiders)
            
            task = self.db.create_test_task(
                status=TASK_STATUS_PENDING,
                spider_id=spider["_id"],
                node_id=node["_id"],
                cmd=spider["cmd"],
                priority=random.randint(1, 10)
            )
            tasks.append(task)
            self.created_resources['tasks'].append(task["_id"])
            self.logger.debug(f"Created pending task: {task['_id']}")
        
        return tasks
    
    def create_running_tasks(self, nodes: List[Dict], spiders: List[Dict], count: int = 4) -> List[Dict[str, Any]]:
        """Create running tasks with mock PIDs"""
        tasks = []
        for i in range(count):
            node = random.choice(nodes)
            spider = random.choice(spiders)
            
            # Create task with fake PID to simulate running process
            fake_pid = random.randint(10000, 99999)
            task = self.db.create_test_task(
                status=TASK_STATUS_RUNNING,
                spider_id=spider["_id"],
                node_id=node["_id"],
                cmd=spider["cmd"],
                pid=fake_pid,
                priority=random.randint(1, 10)
            )
            tasks.append(task)
            self.created_resources['tasks'].append(task["_id"])
            self.logger.debug(f"Created running task: {task['_id']} (PID: {fake_pid})")
        
        return tasks
    
    def create_completed_tasks(self, nodes: List[Dict], spiders: List[Dict], count: int = 3) -> List[Dict[str, Any]]:
        """Create completed tasks (finished/error)"""
        tasks = []
        statuses = [TASK_STATUS_FINISHED, TASK_STATUS_ERROR, TASK_STATUS_CANCELLED]
        
        for i in range(count):
            node = random.choice(nodes)
            spider = random.choice(spiders)
            status = random.choice(statuses)
            
            task_data = {
                'status': status,
                'spider_id': spider["_id"],
                'node_id': node["_id"],
                'cmd': spider["cmd"],
                'priority': random.randint(1, 10)
            }
            
            if status == TASK_STATUS_ERROR:
                task_data['error'] = "Simulated task error for testing"
            
            task = self.db.create_test_task(**task_data)
            tasks.append(task)
            self.created_resources['tasks'].append(task["_id"])
            self.logger.debug(f"Created {status} task: {task['_id']}")
        
        return tasks
    
    def create_mixed_baseline(self, count: int = 10, task_types: str = "mixed") -> Dict[str, Any]:
        """Create a mixed baseline of various task states"""
        self.logger.info(f"Creating mixed baseline with {count} tasks ({task_types} types)")
        
        # Create supporting infrastructure
        nodes = self.create_test_nodes(2)
        spiders = self.create_test_spiders(3)
        
        all_tasks = []
        
        if task_types == "mixed":
            # Distribute tasks across different states
            pending_count = max(1, count // 4)
            running_count = max(2, count // 3)
            completed_count = count - pending_count - running_count
            
            pending_tasks = self.create_pending_tasks(nodes, spiders, pending_count)
            running_tasks = self.create_running_tasks(nodes, spiders, running_count)
            completed_tasks = self.create_completed_tasks(nodes, spiders, completed_count)
            
            all_tasks.extend(pending_tasks)
            all_tasks.extend(running_tasks)
            all_tasks.extend(completed_tasks)
            
        elif task_types == "running":
            # Only create running tasks for reconciliation testing
            all_tasks = self.create_running_tasks(nodes, spiders, count)
            
        elif task_types == "pending":
            # Only create pending tasks
            all_tasks = self.create_pending_tasks(nodes, spiders, count)
            
        elif task_types == "completed":
            # Only create completed tasks
            all_tasks = self.create_completed_tasks(nodes, spiders, count)
        
        # Create summary
        baseline_summary = {
            'created_at': datetime.now().isoformat(),
            'total_tasks': len(all_tasks),
            'nodes': len(nodes),
            'spiders': len(spiders),
            'task_distribution': self._get_task_distribution(all_tasks),
            'node_distribution': self._get_node_distribution(all_tasks, nodes),
            'resources': self.created_resources
        }
        
        self.logger.info(f"✓ Baseline created: {len(all_tasks)} tasks across {len(nodes)} nodes")
        self.logger.info(f"Task distribution: {baseline_summary['task_distribution']}")
        
        return baseline_summary
    
    def _get_task_distribution(self, tasks: List[Dict]) -> Dict[str, int]:
        """Get distribution of tasks by status"""
        distribution = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            distribution[status] = distribution.get(status, 0) + 1
        return distribution
    
    def _get_node_distribution(self, tasks: List[Dict], nodes: List[Dict]) -> Dict[str, int]:
        """Get distribution of tasks by node"""
        distribution = {}
        node_map = {str(node["_id"]): node["key"] for node in nodes}
        
        for task in tasks:
            node_id = str(task.get('node_id', ''))
            node_key = node_map.get(node_id, 'unknown')
            distribution[node_key] = distribution.get(node_key, 0) + 1
        
        return distribution
    
    def validate_baseline(self) -> bool:
        """Validate that baseline was created correctly"""
        self.logger.info("Validating baseline...")
        
        # Check tasks
        for task_id in self.created_resources['tasks']:
            task = self.db.get_task_by_id(task_id)
            if not task:
                self.logger.error(f"Task {task_id} not found in database")
                return False
        
        # Check nodes  
        for node_id in self.created_resources['nodes']:
            node = self.db.get_node_by_id(node_id)
            if not node:
                self.logger.error(f"Node {node_id} not found in database")
                return False
        
        # Check spiders
        for spider_id in self.created_resources['spiders']:
            spiders_collection = self.db.get_collection("spiders")
            spider = spiders_collection.find_one({"_id": spider_id})
            if not spider:
                self.logger.error(f"Spider {spider_id} not found in database")
                return False
        
        self.logger.info("✓ Baseline validation passed")
        return True
    
    def cleanup_baseline(self) -> bool:
        """Clean up created baseline resources"""
        self.logger.info("Cleaning up baseline resources...")
        
        try:
            # Clean up tasks
            if self.created_resources['tasks']:
                tasks_removed = self.db.delete_test_tasks(self.created_resources['tasks'])
                self.logger.info(f"Removed {tasks_removed} test tasks")
            
            # Clean up nodes
            if self.created_resources['nodes']:
                nodes_removed = self.db.delete_test_nodes(self.created_resources['nodes'])
                self.logger.info(f"Removed {nodes_removed} test nodes")
            
            # Clean up spiders
            if self.created_resources['spiders']:
                spiders_removed = self.db.delete_test_spiders(self.created_resources['spiders'])
                self.logger.info(f"Removed {spiders_removed} test spiders")
            
            # Clear tracking
            self.created_resources = {'tasks': [], 'nodes': [], 'spiders': []}
            
            self.logger.info("✓ Baseline cleanup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Baseline cleanup failed: {e}")
            return False
    
    def get_baseline_status(self) -> Dict[str, Any]:
        """Get current status of baseline"""
        status = {
            'total_resources': sum(len(resources) for resources in self.created_resources.values()),
            'tasks': len(self.created_resources['tasks']),
            'nodes': len(self.created_resources['nodes']),
            'spiders': len(self.created_resources['spiders'])
        }
        
        # Get current task distribution
        if self.created_resources['tasks']:
            current_tasks = []
            for task_id in self.created_resources['tasks']:
                task = self.db.get_task_by_id(task_id)
                if task:
                    current_tasks.append(task)
            
            status['current_distribution'] = self._get_task_distribution(current_tasks)
        
        return status

def main():
    parser = argparse.ArgumentParser(description='Manage task baseline for reconciliation testing')
    parser.add_argument('--create', action='store_true',
                       help='Create a new baseline')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up existing baseline')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing baseline')
    parser.add_argument('--status', action='store_true',
                       help='Show baseline status')
    parser.add_argument('--count', type=int, default=10,
                       help='Number of tasks to create')
    parser.add_argument('--types', choices=['mixed', 'running', 'pending', 'completed'],
                       default='mixed', help='Types of tasks to create')
    parser.add_argument('--output-json', help='Output baseline info to JSON file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('task-baseline')
    
    if not any([args.create, args.cleanup, args.validate, args.status]):
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
            logger.warning(f"API authentication failed: {e} - continuing with database-only operations")
        
        db_helper = DatabaseHelper(config['mongodb']['uri'])
        db_helper.database_name = config['mongodb']['database']
        db_helper.connect()
        
        manager = TaskBaselineManager(api_client, db_helper)
        
        result = None
        
        if args.create:
            result = manager.create_mixed_baseline(args.count, args.types)
            logger.info("Baseline created successfully")
            
            # Validate after creation
            if not manager.validate_baseline():
                logger.error("Baseline validation failed")
                sys.exit(1)
        
        if args.validate:
            if manager.validate_baseline():
                logger.info("Baseline validation passed")
            else:
                logger.error("Baseline validation failed")
                sys.exit(1)
        
        if args.status:
            status = manager.get_baseline_status()
            logger.info(f"Baseline status: {json.dumps(status, indent=2)}")
            result = status
        
        if args.cleanup:
            if manager.cleanup_baseline():
                logger.info("Baseline cleanup completed")
            else:
                logger.error("Baseline cleanup failed")
                sys.exit(1)
        
        # Output results if requested
        if args.output_json and result:
            with open(args.output_json, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Results written to {args.output_json}")
        
        # Clean up
        db_helper.disconnect()
        
    except Exception as e:
        logger.error(f"Task baseline operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()