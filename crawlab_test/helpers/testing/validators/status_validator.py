#!/usr/bin/env python3
"""
Status Validator
Verifies conservative status handling logic in the reconciliation service.
Ensures that uncertain statuses are kept rather than assumed as errors.
"""

import argparse
import logging
import sys
import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bson import ObjectId

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.database import (DatabaseHelper, TASK_STATUS_RUNNING, TASK_STATUS_NODE_DISCONNECTED,
                           TASK_STATUS_ERROR, TASK_STATUS_ABNORMAL, TASK_STATUS_FINISHED)
from crawlab_test.helpers.infrastructure.utils import setup_logging, TestMetrics

class StatusValidator:
    def __init__(self, api_client: CrawlabAPIClient, db_helper: DatabaseHelper):
        self.api = api_client
        self.db = db_helper
        self.logger = logging.getLogger(self.__class__.__name__)
        self.test_scenarios = []
    
    def create_uncertain_status_scenario(self, scenario_type: str) -> Dict[str, Any]:
        """Create a scenario where task status is uncertain"""
        test_node = self.db.create_test_node()
        
        scenario_configs = {
            'unreachable_worker': {
                'initial_status': TASK_STATUS_RUNNING,
                'node_status': 'offline',
                'expected_status': TASK_STATUS_NODE_DISCONNECTED,
                'should_not_be': [TASK_STATUS_ERROR, TASK_STATUS_ABNORMAL],
                'description': 'Worker node becomes unreachable during task execution'
            },
            'missing_process': {
                'initial_status': TASK_STATUS_RUNNING,
                'pid': 99999,  # Non-existent PID
                'expected_behavior': 'conservative',
                'should_not_assume': 'error_without_evidence',
                'description': 'Task process not found, but no clear error indication'
            },
            'network_timeout': {
                'initial_status': TASK_STATUS_RUNNING,
                'communication_issue': True,
                'expected_behavior': 'maintain_current_status',
                'should_not_be': [TASK_STATUS_ERROR],
                'description': 'Network timeout prevents status verification'
            }
        }
        
        config = scenario_configs.get(scenario_type)
        if not config:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        # Create test task based on scenario
        task_data = {
            'status': config['initial_status'],
            'node_id': test_node["_id"],
            'pid': config.get('pid', 12345)
        }
        
        test_task = self.db.create_test_task(**task_data)
        
        scenario = {
            'type': scenario_type,
            'config': config,
            'task_id': test_task['_id'],
            'node_id': test_node['_id'],
            'initial_task_data': test_task,
            'created_at': datetime.now().isoformat()
        }
        
        self.test_scenarios.append(scenario)
        self.logger.info(f"Created uncertain status scenario: {scenario_type}")
        
        return scenario
    
    def simulate_worker_disconnection(self, node_id: ObjectId) -> bool:
        """Simulate worker node disconnection"""
        try:
            # Update node status to offline
            success = self.db.update_node_status(node_id, 'offline')
            if success:
                self.logger.info(f"Simulated node {node_id} disconnection")
                return True
            else:
                self.logger.error(f"Failed to update node {node_id} status")
                return False
        except Exception as e:
            self.logger.error(f"Error simulating disconnection: {e}")
            return False
    
    def validate_conservative_behavior(self, scenario: Dict[str, Any], 
                                     wait_time: int = 60) -> Dict[str, Any]:
        """Validate that reconciliation behaves conservatively for uncertain status"""
        self.logger.info(f"Validating conservative behavior for scenario: {scenario['type']}")
        
        task_id = scenario['task_id']
        config = scenario['config']
        
        # Simulate the uncertainty condition
        if scenario['type'] == 'unreachable_worker':
            self.simulate_worker_disconnection(scenario['node_id'])
        
        # Wait for reconciliation to potentially act
        self.logger.info(f"Waiting {wait_time}s for reconciliation to process uncertain status...")
        time.sleep(wait_time)
        
        # Check final task status
        final_task = self.db.get_task_by_id(task_id)
        if not final_task:
            return {
                'valid': False,
                'error': 'Task not found after reconciliation',
                'scenario': scenario['type']
            }
        
        validation_result = {
            'scenario': scenario['type'],
            'initial_status': scenario['initial_task_data']['status'],
            'final_status': final_task['status'],
            'final_error': final_task.get('error', ''),
            'valid': True,
            'issues': [],
            'conservative_behavior': True
        }
        
        # Check for conservative behavior violations
        should_not_be = config.get('should_not_be', [])
        for forbidden_status in should_not_be:
            if final_task['status'] == forbidden_status:
                validation_result['valid'] = False
                validation_result['conservative_behavior'] = False
                validation_result['issues'].append(
                    f"Task incorrectly changed to forbidden status: {forbidden_status}"
                )
        
        # Check for specific expected behavior
        if 'expected_status' in config:
            expected = config['expected_status']
            if final_task['status'] != expected:
                # This might be acceptable if the system is being extra conservative
                if final_task['status'] not in should_not_be:
                    validation_result['issues'].append(
                        f"Status '{final_task['status']}' differs from expected '{expected}' but is acceptable"
                    )
                else:
                    validation_result['valid'] = False
                    validation_result['issues'].append(
                        f"Status '{final_task['status']}' differs from expected '{expected}'"
                    )
        
        # Check for appropriate error messages
        error_msg = final_task.get('error', '')
        if scenario['type'] == 'unreachable_worker':
            if error_msg and 'disconnected' not in error_msg.lower():
                validation_result['issues'].append(
                    "Error message should indicate disconnection for unreachable worker"
                )
        
        # Log validation results
        if validation_result['valid'] and validation_result['conservative_behavior']:
            self.logger.info(f"✓ Conservative behavior validated for {scenario['type']}")
        else:
            self.logger.error(f"✗ Conservative behavior violation in {scenario['type']}: "
                            f"{validation_result['issues']}")
        
        return validation_result
    
    def check_no_false_abnormal_assignments(self) -> Dict[str, Any]:
        """Check that tasks are not falsely marked as abnormal"""
        self.logger.info("Checking for false abnormal status assignments...")
        
        # Find all tasks marked as abnormal
        abnormal_tasks = self.db.get_tasks_by_status(TASK_STATUS_ABNORMAL)
        
        validation_results = {
            'total_abnormal_tasks': len(abnormal_tasks),
            'potentially_false_abnormal': [],
            'valid_abnormal': [],
            'issues_found': 0
        }
        
        for task in abnormal_tasks:
            task_analysis = {
                'task_id': str(task['_id']),
                'error_message': task.get('error', ''),
                'node_id': str(task.get('node_id', '')),
                'last_updated': task.get('updated_at', 0),
                'legitimate_abnormal': True,
                'reasoning': []
            }
            
            # Check if abnormal status is justified
            error_msg = task.get('error', '').lower()
            
            # Look for legitimate reasons for abnormal status
            legitimate_indicators = [
                'worker node offline',
                'process crashed',
                'system error',
                'resource exhaustion',
                'timeout exceeded'
            ]
            
            # Look for potentially false abnormal indicators
            false_indicators = [
                'communication timeout',
                'temporary network issue',
                'process not found',  # Could be legitimate completion
                'status uncertain'
            ]
            
            has_legitimate_reason = any(indicator in error_msg for indicator in legitimate_indicators)
            has_false_indicator = any(indicator in error_msg for indicator in false_indicators)
            
            if has_false_indicator and not has_legitimate_reason:
                task_analysis['legitimate_abnormal'] = False
                task_analysis['reasoning'].append(
                    f"Marked abnormal for potentially temporary issue: {task.get('error', '')}"
                )
                validation_results['potentially_false_abnormal'].append(task_analysis)
                validation_results['issues_found'] += 1
            else:
                task_analysis['reasoning'].append("Abnormal status appears justified")
                validation_results['valid_abnormal'].append(task_analysis)
        
        # Check for tasks that should be abnormal but aren't
        # (This is harder to detect automatically, but we can look for patterns)
        
        self.logger.info(f"Abnormal status analysis: {len(abnormal_tasks)} total, "
                        f"{validation_results['issues_found']} potentially false")
        
        return validation_results
    
    def validate_status_transition_logic(self) -> Dict[str, Any]:
        """Validate that status transitions follow conservative logic"""
        self.logger.info("Validating status transition logic...")
        
        # Get recent task updates (tasks updated in last hour)
        one_hour_ago = time.time() - 3600
        tasks_collection = self.db.get_collection("tasks")
        recent_tasks = list(tasks_collection.find({
            "updated_at": {"$gte": one_hour_ago}
        }))
        
        validation_results = {
            'total_recent_updates': len(recent_tasks),
            'suspicious_transitions': [],
            'conservative_transitions': [],
            'issues_found': 0
        }
        
        # Define suspicious transition patterns
        suspicious_patterns = [
            # Transitions that might indicate non-conservative behavior
            (TASK_STATUS_RUNNING, TASK_STATUS_ABNORMAL, "running_to_abnormal_without_clear_cause"),
            (TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_ERROR, "disconnected_to_error_too_quickly"),
        ]
        
        # Define conservative transition patterns
        conservative_patterns = [
            (TASK_STATUS_RUNNING, TASK_STATUS_NODE_DISCONNECTED, "running_to_disconnected"),
            (TASK_STATUS_NODE_DISCONNECTED, TASK_STATUS_RUNNING, "disconnected_restored"),
        ]
        
        for task in recent_tasks:
            # We can't easily track historical status without a log,
            # but we can check error messages for clues about transitions
            error_msg = task.get('error', '').lower()
            current_status = task.get('status')
            
            # Look for reconciliation-related error messages
            if 'reconciliation' in error_msg or 'status synchronized' in error_msg:
                transition_info = {
                    'task_id': str(task['_id']),
                    'current_status': current_status,
                    'error_message': task.get('error', ''),
                    'analysis': 'reconciliation_related'
                }
                
                # Check if this looks like conservative behavior
                conservative_keywords = ['temporarily', 'disconnected', 'uncertain', 'cannot determine']
                aggressive_keywords = ['failed', 'error', 'abnormal', 'crashed']
                
                if any(keyword in error_msg for keyword in conservative_keywords):
                    validation_results['conservative_transitions'].append(transition_info)
                elif any(keyword in error_msg for keyword in aggressive_keywords):
                    # Check if the aggressive action is justified
                    if current_status in [TASK_STATUS_ERROR, TASK_STATUS_ABNORMAL]:
                        transition_info['analysis'] = 'potentially_aggressive'
                        validation_results['suspicious_transitions'].append(transition_info)
                        validation_results['issues_found'] += 1
        
        self.logger.info(f"Transition analysis: {validation_results['issues_found']} suspicious transitions found")
        
        return validation_results
    
    def run_conservative_logic_check(self) -> Dict[str, Any]:
        """Run comprehensive conservative logic validation"""
        self.logger.info("Running comprehensive conservative logic check...")
        
        check_results = {
            'timestamp': datetime.now().isoformat(),
            'scenarios_tested': [],
            'abnormal_status_check': {},
            'transition_logic_check': {},
            'overall_conservative_score': 0.0,
            'issues_found': 0,
            'recommendations': []
        }
        
        # Test uncertain status scenarios
        scenario_types = ['unreachable_worker', 'missing_process', 'network_timeout']
        
        for scenario_type in scenario_types:
            try:
                scenario = self.create_uncertain_status_scenario(scenario_type)
                validation = self.validate_conservative_behavior(scenario)
                
                check_results['scenarios_tested'].append(validation)
                
                if not validation['conservative_behavior']:
                    check_results['issues_found'] += len(validation['issues'])
                
            except Exception as e:
                self.logger.error(f"Failed to test scenario {scenario_type}: {e}")
        
        # Check abnormal status assignments
        check_results['abnormal_status_check'] = self.check_no_false_abnormal_assignments()
        check_results['issues_found'] += check_results['abnormal_status_check']['issues_found']
        
        # Check transition logic
        check_results['transition_logic_check'] = self.validate_status_transition_logic()
        check_results['issues_found'] += check_results['transition_logic_check']['issues_found']
        
        # Calculate conservative score
        total_checks = len(scenario_types) + 2  # scenarios + abnormal check + transition check
        issues = check_results['issues_found']
        check_results['overall_conservative_score'] = max(0, (total_checks - issues) / total_checks * 100)
        
        # Generate recommendations
        if check_results['issues_found'] > 0:
            check_results['recommendations'].extend([
                "Review reconciliation logic for overly aggressive status changes",
                "Implement additional uncertainty handling in status determination",
                "Add more conservative timeouts before marking tasks as abnormal"
            ])
        
        # Cleanup test scenarios
        self.cleanup_test_scenarios()
        
        return check_results
    
    def cleanup_test_scenarios(self):
        """Clean up test scenarios and resources"""
        for scenario in self.test_scenarios:
            try:
                self.db.delete_test_tasks([scenario['task_id']])
                self.db.delete_test_nodes([scenario['node_id']])
            except Exception as e:
                self.logger.warning(f"Failed to cleanup scenario {scenario['type']}: {e}")
        
        self.test_scenarios.clear()
        self.logger.info("Test scenarios cleaned up")

def main():
    parser = argparse.ArgumentParser(description='Validate conservative status handling logic')
    parser.add_argument('--check-conservative-logic', action='store_true',
                       help='Run comprehensive conservative logic check')
    parser.add_argument('--check-abnormal-assignments', action='store_true',
                       help='Check for false abnormal status assignments')
    parser.add_argument('--check-transitions', action='store_true',
                       help='Validate status transition logic')
    parser.add_argument('--output-json', help='Output validation results to JSON file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--master-url', default='http://localhost:8080',
                       help='Crawlab master URL')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger('status-validator')
    
    if not any([args.check_conservative_logic, args.check_abnormal_assignments, args.check_transitions]):
        parser.print_help()
        return
    
    try:
        # Initialize components
        api_client = CrawlabAPIClient(args.master_url)
        db_helper = DatabaseHelper()
        db_helper.connect()
        
        validator = StatusValidator(api_client, db_helper)
        
        results = {}
        
        if args.check_conservative_logic:
            results = validator.run_conservative_logic_check()
            
            score = results.get('overall_conservative_score', 0)
            issues = results.get('issues_found', 0)
            
            if score >= 80:
                logger.info(f"✓ Conservative logic validation passed (score: {score:.1f}%)")
            elif score >= 60:
                logger.warning(f"⚠ Conservative logic needs improvement (score: {score:.1f}%, {issues} issues)")
            else:
                logger.error(f"✗ Conservative logic validation failed (score: {score:.1f}%, {issues} issues)")
                if results.get('recommendations'):
                    logger.info("Recommendations:")
                    for rec in results['recommendations']:
                        logger.info(f"  - {rec}")
        
        elif args.check_abnormal_assignments:
            results['abnormal_check'] = validator.check_no_false_abnormal_assignments()
            issues = results['abnormal_check']['issues_found']
            
            if issues == 0:
                logger.info("✓ No false abnormal assignments detected")
            else:
                logger.warning(f"⚠ Found {issues} potentially false abnormal assignments")
        
        elif args.check_transitions:
            results['transition_check'] = validator.validate_status_transition_logic()
            issues = results['transition_check']['issues_found']
            
            if issues == 0:
                logger.info("✓ Status transition logic appears conservative")
            else:
                logger.warning(f"⚠ Found {issues} suspicious status transitions")
        
        # Output results if requested
        if args.output_json and results:
            with open(args.output_json, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results written to {args.output_json}")
        
        # Clean up
        db_helper.disconnect()
        
        # Exit with error code if issues found
        total_issues = results.get('issues_found', 0)
        if 'abnormal_check' in results:
            total_issues += results['abnormal_check']['issues_found']
        if 'transition_check' in results:
            total_issues += results['transition_check']['issues_found']
        
        sys.exit(1 if total_issues > 0 else 0)
        
    except Exception as e:
        logger.error(f"Status validation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()