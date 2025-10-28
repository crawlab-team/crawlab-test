#!/usr/bin/env python3
"""
SCH-002: Task Execution Pressure Test Runner

Tests Crawlab's robustness under heavy concurrent task execution.
Validates system performance, stability, and error handling under various load levels.
"""

import argparse
import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add helpers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from crawlab_test.helpers.api.auth import AuthHelper
from crawlab_test.helpers.api.node import NodeHelper
from crawlab_test.helpers.api.spider import SpiderHelper
from crawlab_test.helpers.api.task import TaskHelper


class PressureTestRunner:
    """Runner for task execution pressure tests."""

    # Load level configurations
    LOAD_CONFIGS = {
        "light": {"tasks": 100, "workers": 5, "batch_size": 20},
        "medium": {"tasks": 500, "workers": 10, "batch_size": 50},
        "heavy": {"tasks": 1000, "workers": 20, "batch_size": 100},
        "extreme": {"tasks": 5000, "workers": 50, "batch_size": 100},
    }

    def __init__(self, base_url: str = "http://localhost:8080/api", verbose: bool = False):
        """Initialize test runner."""
        self.base_url = base_url
        self.verbose = verbose
        self.auth = AuthHelper(base_url)
        self.spider_helper = SpiderHelper(base_url)
        self.task_helper = TaskHelper(base_url)
        self.node_helper = NodeHelper(base_url)
        self.token = None
        self.test_spider_id = None
        self.created_task_ids = []

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "PROGRESS": "📊"}
        print(f"[{timestamp}] {emoji.get(level, '')} {message}")

    def verify_environment(self) -> bool:
        """Verify test environment is ready."""
        self.log("Verifying test environment...")

        try:
            # Test API connectivity
            response = self.auth.login("admin", "admin")
            if not response[0]:
                self.log("API authentication failed", "ERROR")
                return False

            self.token = response[0]
            self.log("API authentication successful", "SUCCESS")

            # Check worker nodes
            nodes, _ = self.node_helper.list_nodes(self.token)
            if not nodes:
                self.log("No worker nodes found", "WARNING")
            else:
                worker_count = len([n for n in nodes if n.get("is_master") is False])
                self.log(f"Found {worker_count} worker node(s)", "SUCCESS")

            return True

        except Exception as e:
            self.log(f"Environment verification failed: {e}", "ERROR")
            return False

    def create_test_spider(self, cmd: Optional[str] = None) -> Optional[str]:
        """Create a test spider for load testing."""
        if not cmd:
            # Default: simple 5-second task
            cmd = 'python -c \'import time; print("Task started"); time.sleep(5); print("Task completed")\''

        spider_name = f"LoadTest-{int(time.time())}"
        self.log(f"Creating test spider: {spider_name}")

        spider_id, response = self.spider_helper.create_spider(
            self.token, name=spider_name, cmd=cmd, description="Automated pressure test spider"
        )

        if spider_id:
            self.test_spider_id = spider_id
            self.log(f"Spider created: {spider_id}", "SUCCESS")
            return spider_id
        else:
            self.log(f"Spider creation failed: {response}", "ERROR")
            return None

    def create_task_batch(self, batch_num: int, batch_size: int) -> Tuple[List[str], List[str], float]:
        """Create a batch of tasks and measure performance."""
        batch_task_ids = []
        batch_errors = []
        start_time = time.time()

        for _i in range(batch_size):
            try:
                ids, response = self.task_helper.create_task(self.token, self.test_spider_id, priority=5)
                if ids:
                    batch_task_ids.extend(ids)
                else:
                    error_msg = response.get("error", "Unknown error")
                    batch_errors.append(error_msg)
                    if self.verbose:
                        self.log(f"Task creation error: {error_msg}", "ERROR")
            except Exception as e:
                batch_errors.append(str(e))
                if self.verbose:
                    self.log(f"Exception creating task: {e}", "ERROR")

        duration = time.time() - start_time
        return batch_task_ids, batch_errors, duration

    def run_load_test(self, num_tasks: int, num_workers: int, batch_size: int) -> Dict:
        """Run load test with specified parameters."""
        self.log(f"Starting load test: {num_tasks} tasks, {num_workers} workers, batch size {batch_size}")

        # Track metrics
        all_task_ids = []
        all_errors = []
        batch_durations = []

        start_time = time.time()
        num_batches = (num_tasks + batch_size - 1) // batch_size

        # Progress bar
        self.log(f"Creating {num_tasks} tasks in {num_batches} batches...")

        # Create tasks in parallel batches
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(self.create_task_batch, i, batch_size) for i in range(num_batches)]

            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                try:
                    batch_ids, batch_errors, duration = future.result()
                    all_task_ids.extend(batch_ids)
                    all_errors.extend(batch_errors)
                    batch_durations.append(duration)

                    # Calculate progress
                    (i / num_batches) * 100
                    len(all_task_ids)

                    if batch_errors:
                        self.log(
                            f"Batch {i}/{num_batches}: {len(batch_ids)}/{batch_size} tasks "
                            f"({duration:.1f}s) ⚠️ {len(batch_errors)} errors",
                            "WARNING",
                        )
                    else:
                        self.log(
                            f"Batch {i}/{num_batches}: {len(batch_ids)}/{batch_size} tasks ({duration:.1f}s)",
                            "PROGRESS",
                        )

                except Exception as e:
                    self.log(f"Batch execution error: {e}", "ERROR")
                    all_errors.append(str(e))

        creation_time = time.time() - start_time

        # Store created task IDs for cleanup
        self.created_task_ids.extend(all_task_ids)

        # Calculate metrics
        success_rate = (len(all_task_ids) / num_tasks) * 100 if num_tasks > 0 else 0
        tasks_per_second = len(all_task_ids) / creation_time if creation_time > 0 else 0
        avg_batch_duration = sum(batch_durations) / len(batch_durations) if batch_durations else 0

        # Display results
        self.log("=" * 60)
        self.log("📊 Task Creation Results:", "PROGRESS")
        self.log(f"  Target tasks: {num_tasks}")
        self.log(
            f"  Tasks created: {len(all_task_ids)} ({success_rate:.1f}%)",
            "SUCCESS" if success_rate >= 95 else "WARNING",
        )
        self.log(f"  Errors: {len(all_errors)}", "ERROR" if all_errors else "INFO")
        self.log(f"  Total time: {creation_time:.1f}s")
        self.log(f"  Tasks/second: {tasks_per_second:.1f}")
        self.log(f"  Avg batch duration: {avg_batch_duration:.1f}s")
        self.log("=" * 60)

        return {
            "total_tasks": num_tasks,
            "created": len(all_task_ids),
            "creation_success_rate": success_rate,
            "creation_time_sec": creation_time,
            "tasks_per_second": tasks_per_second,
            "avg_batch_duration": avg_batch_duration,
            "errors": all_errors,
            "task_ids": all_task_ids,
        }

    def monitor_task_execution(
        self, task_ids: List[str], timeout: int = 600, sample_size: int = 50, check_interval: int = 10
    ) -> Dict:
        """Monitor task execution and collect metrics."""
        if not task_ids:
            return {"error": "No tasks to monitor"}

        self.log(f"Monitoring {len(task_ids)} tasks (sampling {sample_size})...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Sample subset of tasks for efficiency
            sample_ids = task_ids[: min(sample_size, len(task_ids))]

            status_counts = {"finished": 0, "error": 0, "running": 0, "pending": 0, "cancelled": 0, "other": 0}

            for task_id in sample_ids:
                try:
                    status = self.task_helper.get_task_status(self.token, task_id)
                    if status == "finished":
                        status_counts["finished"] += 1
                    elif status == "error":
                        status_counts["error"] += 1
                    elif status == "running":
                        status_counts["running"] += 1
                    elif status in ["pending", "assigned"]:
                        status_counts["pending"] += 1
                    elif status == "cancelled":
                        status_counts["cancelled"] += 1
                    else:
                        status_counts["other"] += 1
                except Exception as e:
                    if self.verbose:
                        self.log(f"Error checking task {task_id}: {e}", "ERROR")

            # Calculate percentages based on sample
            total_sampled = sum(status_counts.values())
            elapsed = time.time() - start_time

            # Display progress
            if total_sampled > 0:
                finished_pct = (status_counts["finished"] / total_sampled) * 100
                progress_bar = self._generate_progress_bar(finished_pct)

                self.log(
                    f"Progress: {progress_bar} {finished_pct:.0f}% "
                    f"({status_counts['finished']}/{total_sampled} finished) | "
                    f"Running: {status_counts['running']} | "
                    f"Pending: {status_counts['pending']} | "
                    f"Errors: {status_counts['error']} | "
                    f"Elapsed: {elapsed:.0f}s",
                    "PROGRESS",
                )

            # Check if all tasks completed (based on sample)
            if status_counts["finished"] + status_counts["error"] + status_counts["cancelled"] == total_sampled:
                self.log("All sampled tasks completed", "SUCCESS")
                break

            time.sleep(check_interval)

        execution_time = time.time() - start_time

        # Calculate final metrics (extrapolate from sample)
        if total_sampled > 0:
            scale_factor = len(task_ids) / total_sampled
            estimated_finished = int(status_counts["finished"] * scale_factor)
            estimated_errors = int(status_counts["error"] * scale_factor)
            execution_success_rate = (status_counts["finished"] / total_sampled) * 100
        else:
            estimated_finished = 0
            estimated_errors = 0
            execution_success_rate = 0

        return {
            "execution_time_sec": execution_time,
            "execution_success_rate": execution_success_rate,
            "estimated_finished": estimated_finished,
            "estimated_errors": estimated_errors,
            "status_counts": status_counts,
        }

    def _generate_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Generate a simple progress bar."""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def cleanup(self):
        """Clean up test resources."""
        self.log("Cleaning up test resources...")

        # Delete tasks
        if self.created_task_ids:
            self.log(f"Deleting {len(self.created_task_ids)} test tasks...")
            success, _ = self.task_helper.delete_tasks(self.token, self.created_task_ids)
            if success:
                self.log(f"Deleted {len(self.created_task_ids)} tasks", "SUCCESS")
            else:
                self.log("Failed to delete some tasks", "WARNING")

        # Delete spider
        if self.test_spider_id:
            self.log(f"Deleting test spider {self.test_spider_id}...")
            success, _ = self.spider_helper.delete_spider(self.token, self.test_spider_id)
            if success:
                self.log("Spider deleted", "SUCCESS")
            else:
                self.log("Failed to delete spider", "WARNING")

    def run_full_test(self, load_level: str = "heavy", monitor: bool = True) -> Dict:
        """Run complete pressure test."""
        if load_level not in self.LOAD_CONFIGS:
            self.log(f"Invalid load level: {load_level}. Choose from: {list(self.LOAD_CONFIGS.keys())}", "ERROR")
            return {"error": "Invalid load level"}

        config = self.LOAD_CONFIGS[load_level]

        self.log(f"🔥 Crawlab Pressure Test - {load_level.upper()} Load")
        self.log("=" * 60)

        # Verify environment
        if not self.verify_environment():
            return {"error": "Environment verification failed"}

        # Create test spider
        if not self.create_test_spider():
            return {"error": "Spider creation failed"}

        try:
            # Run load test
            creation_results = self.run_load_test(
                num_tasks=config["tasks"], num_workers=config["workers"], batch_size=config["batch_size"]
            )

            # Monitor execution if requested
            execution_results = {}
            if monitor and creation_results["task_ids"]:
                self.log("\n⏳ Monitoring task execution...")
                execution_results = self.monitor_task_execution(creation_results["task_ids"], timeout=600)

            # Combine results
            results = {
                "load_level": load_level,
                "timestamp": datetime.now().isoformat(),
                "creation": creation_results,
                "execution": execution_results,
            }

            # Evaluate results
            self._evaluate_results(results, load_level)

            return results

        finally:
            # Always cleanup
            self.cleanup()

    def _evaluate_results(self, results: Dict, load_level: str):
        """Evaluate test results against success criteria."""
        self.log("\n" + "=" * 60)
        self.log("📊 Test Evaluation", "PROGRESS")
        self.log("=" * 60)

        # Define thresholds based on load level
        thresholds = {
            "light": {"creation": 100, "execution": 95, "response_ms": 500},
            "medium": {"creation": 98, "execution": 90, "response_ms": 1000},
            "heavy": {"creation": 95, "execution": 85, "response_ms": 2000},
            "extreme": {"creation": 90, "execution": 80, "response_ms": 3000},
        }

        threshold = thresholds.get(load_level, thresholds["heavy"])

        creation = results.get("creation", {})
        execution = results.get("execution", {})

        # Check creation success rate
        creation_rate = creation.get("creation_success_rate", 0)
        if creation_rate >= threshold["creation"]:
            self.log(f"✅ Creation success rate: {creation_rate:.1f}% (threshold: {threshold['creation']}%)", "SUCCESS")
        else:
            self.log(f"❌ Creation success rate: {creation_rate:.1f}% (threshold: {threshold['creation']}%)", "ERROR")

        # Check execution success rate
        if execution:
            execution_rate = execution.get("execution_success_rate", 0)
            if execution_rate >= threshold["execution"]:
                self.log(
                    f"✅ Execution success rate: {execution_rate:.1f}% (threshold: {threshold['execution']}%)",
                    "SUCCESS",
                )
            else:
                self.log(
                    f"❌ Execution success rate: {execution_rate:.1f}% (threshold: {threshold['execution']}%)", "ERROR"
                )

        # Overall result
        passed = creation_rate >= threshold["creation"]
        if execution:
            passed = passed and execution.get("execution_success_rate", 0) >= threshold["execution"]

        self.log("=" * 60)
        if passed:
            self.log("✅ TEST PASSED: All criteria met", "SUCCESS")
        else:
            self.log("❌ TEST FAILED: Some criteria not met", "ERROR")
        self.log("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SCH-002: Task Execution Pressure Test")
    parser.add_argument(
        "--load", choices=["light", "medium", "heavy", "extreme"], default="heavy", help="Load level to test"
    )
    parser.add_argument("--verify", action="store_true", help="Only verify environment")
    parser.add_argument("--cleanup", action="store_true", help="Only run cleanup")
    parser.add_argument("--monitor", action="store_true", default=True, help="Monitor task execution")
    parser.add_argument("--no-monitor", action="store_false", dest="monitor", help="Skip execution monitoring")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--base-url", default="http://localhost:8080/api", help="API base URL")
    parser.add_argument("--output", help="Save results to JSON file")
    parser.add_argument("--ci", action="store_true", help="CI mode (minimal output, strict validation)")

    args = parser.parse_args()

    runner = PressureTestRunner(base_url=args.base_url, verbose=args.verbose)

    if args.verify:
        success = runner.verify_environment()
        sys.exit(0 if success else 1)

    if args.cleanup:
        runner.cleanup()
        sys.exit(0)

    # Run full test
    results = runner.run_full_test(load_level=args.load, monitor=args.monitor)

    # Save results if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        runner.log(f"Results saved to {args.output}", "SUCCESS")

    # Exit with appropriate code
    if results.get("error"):
        sys.exit(1)

    # Check if test passed
    creation_rate = results.get("creation", {}).get("creation_success_rate", 0)
    if creation_rate >= 90:  # Minimum threshold
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
