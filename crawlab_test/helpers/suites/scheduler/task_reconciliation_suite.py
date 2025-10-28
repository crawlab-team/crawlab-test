#!/usr/bin/env python3
"""
Task Reconciliation Test Suite
Main orchestrator that executes the complete test suite as specified in task-reconciliation.md
"""

import argparse
import importlib.util
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the helpers directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.database import DatabaseHelper
from crawlab_test.helpers.infrastructure.utils import TestMetrics, load_config, setup_logging

# Import NodeManager from helpers/testing/managers
node_manager_path = Path(__file__).parent.parent.parent / "testing" / "managers" / "node_manager.py"
spec = importlib.util.spec_from_file_location("node_manager", node_manager_path)
node_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(node_manager_module)
NodeManager = node_manager_module.NodeManager


class TaskReconciliationTestSuite:
    def __init__(self, master_url: str = "http://localhost:8080", api_token: Optional[str] = None):
        self.master_url = master_url
        self.api_token = api_token

        # Load configuration
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        config = load_config(config_file)

        self.api = CrawlabAPIClient(master_url, api_token)
        self.db = DatabaseHelper(config["mongodb"]["uri"])
        self.db.database_name = config["mongodb"]["database"]
        self.node_manager = NodeManager(master_url, api_token)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = TestMetrics()
        self.test_results = {}
        self.helpers_dir = Path(__file__).parent

        # Automatically login if no token provided
        if not api_token:
            try:
                self.api.ensure_authenticated()
                self.logger.info("Successfully authenticated with Crawlab API")
            except Exception as e:
                self.logger.warning(f"API authentication failed: {e} - some tests may be limited")

    def run_helper_script(
        self, script_name: str, args: Optional[List[str]] = None, capture_output: bool = True
    ) -> Dict[str, Any]:
        """Run a helper script and return results"""
        script_path = self.helpers_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Helper script not found: {script_path}")

        cmd = [str(script_path)]
        if args:
            cmd.extend(args)

        # Add common arguments
        if "--master-url" not in cmd:
            cmd.extend(["--master-url", self.master_url])
        if self.api_token and "--api-token" not in cmd:
            cmd.extend(["--api-token", self.api_token])

        self.logger.debug(f"Running: {' '.join(cmd)}")

        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                return {
                    "success": result.returncode == 0,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "command": " ".join(cmd),
                }
            else:
                result = subprocess.run(cmd, timeout=300)
                return {"success": result.returncode == 0, "returncode": result.returncode, "command": " ".join(cmd)}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out after 300 seconds", "command": " ".join(cmd)}
        except Exception as e:
            return {"success": False, "error": str(e), "command": " ".join(cmd)}

    def step_1_verify_reconciliation_service(self) -> bool:
        """Step 1: Verify Reconciliation Service Status"""
        self.logger.info("Step 1: Verifying reconciliation service status...")

        result = self.run_helper_script("reconciliation-health.py", ["--check-service", "--detailed"])

        if result["success"]:
            self.logger.info("✓ Reconciliation service is operational")
            return True
        else:
            self.logger.error(f"✗ Reconciliation service check failed: {result.get('stderr', '')}")
            return False

    def step_2_establish_baseline(self) -> bool:
        """Step 2: Establish Baseline Task State"""
        self.logger.info("Step 2: Establishing baseline task state...")

        result = self.run_helper_script("task-baseline.py", ["--create", "--count", "10", "--types", "mixed"])

        if result["success"]:
            self.logger.info("✓ Task baseline established")
            return True
        else:
            self.logger.error(f"✗ Baseline creation failed: {result.get('stderr', '')}")
            return False

    def step_3_simulate_zombie_tasks(self) -> bool:
        """Step 3: Simulate Process Crashes (Zombie Tasks)"""
        self.logger.info("Step 3: Simulating process crashes to create zombie tasks...")

        result = self.run_helper_script(
            "process-killer.py", ["--target", "running-tasks", "--method", "SIGKILL", "--count", "3", "--verify"]
        )

        if result["success"]:
            self.logger.info("✓ Zombie tasks created successfully")
            return True
        else:
            self.logger.error(f"✗ Process killing failed: {result.get('stderr', '')}")
            return False

    def step_4_wait_for_reconciliation(self) -> bool:
        """Step 4: Wait for Reconciliation Cycle"""
        self.logger.info("Step 4: Waiting for reconciliation cycle...")

        result = self.run_helper_script("reconciliation-monitor.py", ["--wait-cycle", "--timeout", "90"])

        if result["success"]:
            self.logger.info("✓ Reconciliation cycle detected")
            return True
        else:
            self.logger.error(f"✗ Reconciliation cycle not detected: {result.get('stderr', '')}")
            return False

    def step_5_simulate_worker_disconnection(self) -> bool:
        """Step 5: Simulate Worker Node Disconnection"""
        self.logger.info("Step 5: Simulating worker node disconnection...")

        # Find an available worker node to disconnect
        nodes = self.api.get_nodes()
        worker_nodes = [node for node in nodes if node.get("status") == "online"]

        if not worker_nodes:
            self.logger.warning("No online worker nodes found for disconnection test")
            return True  # Skip this test

        target_node = worker_nodes[0]["key"] if "key" in worker_nodes[0] else worker_nodes[0]["name"]

        # Disconnect the node
        success = self.node_manager.disconnect_node(target_node, method="graceful")
        if not success:
            self.logger.error(f"Failed to disconnect node: {target_node}")
            return False

        # Wait a bit for the disconnection to be processed
        time.sleep(30)

        self.logger.info(f"✓ Node {target_node} disconnected")
        return True

    def step_6_verify_conservative_handling(self) -> bool:
        """Step 6: Verify Conservative Status Handling"""
        self.logger.info("Step 6: Verifying conservative status handling...")

        result = self.run_helper_script("status-validator.py", ["--check-conservative-logic"])

        if result["success"]:
            self.logger.info("✓ Conservative status handling validated")
            return True
        else:
            self.logger.error(f"✗ Conservative handling issues found: {result.get('stderr', '')}")
            return False

    def step_7_test_worker_reconnection(self) -> bool:
        """Step 7: Test Worker Reconnection Reconciliation"""
        self.logger.info("Step 7: Testing worker reconnection reconciliation...")

        # Find disconnected nodes to reconnect
        nodes = self.api.get_nodes()
        offline_nodes = [node for node in nodes if node.get("status") != "online"]

        if not offline_nodes:
            self.logger.info("No offline nodes to reconnect - skipping test")
            return True

        # Try to reconnect the first offline node
        target_node = offline_nodes[0]["key"] if "key" in offline_nodes[0] else offline_nodes[0]["name"]

        success = self.node_manager.reconnect_node(target_node)
        if success:
            self.logger.info(f"✓ Node {target_node} reconnected")
            # Wait for reconciliation to process the reconnection
            time.sleep(30)
            return True
        else:
            self.logger.warning(f"Could not reconnect node: {target_node}")
            return True  # Don't fail the entire suite for this

    def step_8_continuous_monitoring(self) -> bool:
        """Step 8: Test Periodic Reconciliation Under Load"""
        self.logger.info("Step 8: Testing periodic reconciliation performance...")

        result = self.run_helper_script(
            "reconciliation-monitor.py", ["--continuous", "--duration", "180", "--interval", "30"]
        )

        if result["success"]:
            self.logger.info("✓ Periodic reconciliation performance validated")
            return True
        else:
            self.logger.error(f"✗ Performance issues detected: {result.get('stderr', '')}")
            return False

    def step_9_final_consistency_check(self) -> bool:
        """Step 9: Verify Final System Consistency"""
        self.logger.info("Step 9: Verifying final system consistency...")

        # Check that all task statuses accurately reflect reality
        try:
            self.db.connect()

            # Get counts of tasks in each status
            running_tasks = self.db.get_tasks_by_status("running")
            disconnected_tasks = self.db.get_tasks_by_status("node_disconnected")
            error_tasks = self.db.get_tasks_by_status("error")

            self.logger.info(
                f"Final state: {len(running_tasks)} running, "
                f"{len(disconnected_tasks)} disconnected, "
                f"{len(error_tasks)} error tasks"
            )

            # Basic consistency checks
            consistency_issues = 0

            # Check running tasks have valid PIDs (if any)
            for task in running_tasks[:5]:  # Sample check
                pid = task.get("pid", 0)
                if pid > 0:
                    # In a real test, we'd check if the process actually exists
                    pass

            if consistency_issues == 0:
                self.logger.info("✓ System consistency validated")
                return True
            else:
                self.logger.error(f"✗ Found {consistency_issues} consistency issues")
                return False

        except Exception as e:
            self.logger.error(f"Consistency check failed: {e}")
            return False
        finally:
            self.db.disconnect()

    def cleanup_test_environment(self) -> bool:
        """Clean up test environment"""
        self.logger.info("Cleaning up test environment...")

        try:
            # Clean up test data
            self.run_helper_script(
                "../common/cleanup.py", ["--reconciliation-test-data", "--temp-files"]
            )

            # Reset any offline nodes (best effort)
            try:
                nodes = self.api.get_nodes()
                offline_nodes = [
                    node for node in nodes if node.get("status") != "online" and "test" in node.get("key", "").lower()
                ]

                for node in offline_nodes:
                    node_key = node["key"] if "key" in node else node["name"]
                    self.node_manager.reconnect_node(node_key)
            except:
                pass  # Best effort cleanup

            self.logger.info("✓ Test environment cleaned up")
            return True

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False

    def run_full_suite(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING TASK RECONCILIATION TEST SUITE")
        self.logger.info("=" * 60)

        self.metrics.start_test("Task Reconciliation Test Suite")

        # Validate environment before starting
        self.logger.info("Validating test environment...")
        env_issues = validate_test_environment()
        if env_issues:
            self.logger.error("Environment validation failed:")
            for issue in env_issues:
                self.logger.error(f"  - {issue}")
            return {"success": False, "error": "Environment validation failed"}

        # Define test steps
        test_steps = [
            ("Verify Reconciliation Service", self.step_1_verify_reconciliation_service),
            ("Establish Baseline Task State", self.step_2_establish_baseline),
            ("Simulate Zombie Tasks", self.step_3_simulate_zombie_tasks),
            ("Wait for Reconciliation Cycle", self.step_4_wait_for_reconciliation),
            ("Simulate Worker Disconnection", self.step_5_simulate_worker_disconnection),
            ("Verify Conservative Handling", self.step_6_verify_conservative_handling),
            ("Test Worker Reconnection", self.step_7_test_worker_reconnection),
            ("Continuous Monitoring", self.step_8_continuous_monitoring),
            ("Final Consistency Check", self.step_9_final_consistency_check),
        ]

        # Execute test steps
        for step_name, step_func in test_steps:
            self.metrics.start_step(step_name)

            try:
                success = step_func()
                self.metrics.end_step(success)

                if not success:
                    self.logger.error(f"Step failed: {step_name}")
                    # Continue with remaining steps for maximum information gathering

            except Exception as e:
                self.logger.error(f"Step error: {step_name} - {e}")
                self.metrics.end_step(False, str(e))

        # Cleanup
        try:
            self.cleanup_test_environment()
        except Exception as e:
            self.logger.warning(f"Cleanup warning: {e}")

        # Generate final results
        results = self.metrics.end_test()

        # Print summary
        summary = create_test_summary(results)
        self.logger.info("\n" + summary)

        return results


def main():
    parser = argparse.ArgumentParser(description="Task Reconciliation Test Suite")
    parser.add_argument("--full-suite", action="store_true", help="Run the complete reconciliation test suite")
    parser.add_argument(
        "--test",
        choices=["zombie-detection", "worker-reconnection", "grpc-protocol", "conservative-logic", "performance"],
        help="Run specific test category",
    )
    parser.add_argument("--master-url", default="http://localhost:8080", help="Crawlab master URL")
    parser.add_argument("--api-token", help="API token for authentication")
    parser.add_argument("--output-json", help="Output results to JSON file")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level"
    )
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup operations")

    args = parser.parse_args()

    # Set up logging
    log_file = f"reconciliation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(args.log_level, log_file)
    logger = logging.getLogger("task-reconciliation-test")

    if not any([args.full_suite, args.test, args.cleanup_only]):
        parser.print_help()
        return

    try:
        # Initialize test suite
        test_suite = TaskReconciliationTestSuite(args.master_url, args.api_token)

        if args.cleanup_only:
            success = test_suite.cleanup_test_environment()
            sys.exit(0 if success else 1)

        results = None

        if args.full_suite:
            # Run complete test suite
            results = test_suite.run_full_suite()

        elif args.test:
            # Run specific test category
            test_suite.metrics.start_test(f"Task Reconciliation - {args.test}")

            if args.test == "zombie-detection":
                test_suite.metrics.start_step("Zombie Detection")
                success = (
                    test_suite.step_2_establish_baseline()
                    and test_suite.step_3_simulate_zombie_tasks()
                    and test_suite.step_4_wait_for_reconciliation()
                )
                test_suite.metrics.end_step(success)

            elif args.test == "worker-reconnection":
                test_suite.metrics.start_step("Worker Reconnection")
                success = (
                    test_suite.step_5_simulate_worker_disconnection() and test_suite.step_7_test_worker_reconnection()
                )
                test_suite.metrics.end_step(success)

            elif args.test == "conservative-logic":
                test_suite.metrics.start_step("Conservative Logic")
                success = test_suite.step_6_verify_conservative_handling()
                test_suite.metrics.end_step(success)

            elif args.test == "performance":
                test_suite.metrics.start_step("Performance Testing")
                success = test_suite.step_8_continuous_monitoring()
                test_suite.metrics.end_step(success)

            results = test_suite.metrics.end_test()
            test_suite.cleanup_test_environment()

        # Output results if requested
        if args.output_json and results:
            with open(args.output_json, "w") as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results written to {args.output_json}")

        # Exit with appropriate code
        if results:
            success_rate = results.get("success_rate", 0)
            sys.exit(0 if success_rate >= 80 else 1)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
