#!/usr/bin/env python3
"""
File Sync gRPC Streaming Test Helper

This script tests the gRPC streaming file synchronization implementation
and compares it against the HTTP/JSON fallback mode.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

from helpers.infrastructure.api_client import CrawlabAPIClient
from helpers.infrastructure.docker import docker_utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class FileSyncTester:
    """Test harness for gRPC file sync functionality"""

    def __init__(self, api_url: Optional[str] = None):
        # Auto-detect Docker environment if no URL provided
        self.client = CrawlabAPIClient(base_url=api_url, auto_detect_docker=True)
        self.docker = docker_utils
        self.test_spider_id = None
        self.master_container = self._find_master_container()

    def _find_master_container(self) -> Optional[str]:
        """Find the master container name/id"""
        if not self.docker or not self.docker.is_available():
            return None

        containers = self.docker.find_crawlab_containers()
        for container in containers:
            name = container.get("Names", "")
            if "master" in name.lower():
                return container.get("ID") or name
        return None

    def measure_baseline_http(self, concurrent_tasks: int = 10) -> Dict:
        """Run baseline test with HTTP mode"""
        logger.info(f"=== HTTP MODE BASELINE TEST ({concurrent_tasks} concurrent tasks) ===")

        # Ensure HTTP mode is enabled
        self._set_sync_mode("http")

        # Create and run tasks
        task_ids = []
        start_time = time.time()

        for i in range(concurrent_tasks):
            task_id = self.client.create_task(self.test_spider_id)
            task_ids.append(task_id)
            logger.info(f"Created task {i+1}/{concurrent_tasks}: {task_id}")

        # Wait for completion
        results = self._wait_for_tasks(task_ids, timeout=300)
        end_time = time.time()

        # Analyze results
        success_count = sum(1 for r in results if r["status"] == "success")
        success_rate = (success_count / len(results)) * 100
        avg_duration = sum(r["duration"] for r in results) / len(results)

        # Check for JSON errors in logs
        json_errors = self._count_json_errors_in_logs()

        report = {
            "mode": "http",
            "concurrent_tasks": concurrent_tasks,
            "success_rate": success_rate,
            "success_count": success_count,
            "total_count": len(results),
            "avg_duration_sec": round(avg_duration, 2),
            "total_time_sec": round(end_time - start_time, 2),
            "json_errors": json_errors,
        }

        logger.info(f"HTTP Baseline Results: {json.dumps(report, indent=2)}")
        return report

    def test_grpc_basic(self) -> bool:
        """Test basic gRPC functionality"""
        logger.info("=== GRPC BASIC FUNCTIONALITY TEST ===")

        self._set_sync_mode("grpc")

        # Create single task
        task_id = self.client.create_task(self.test_spider_id)
        logger.info(f"Created test task: {task_id}")

        # Wait for completion
        results = self._wait_for_tasks([task_id], timeout=120)

        if results[0]["status"] == "success":
            logger.info("✅ Basic gRPC test PASSED")
            return True
        else:
            logger.error(f"❌ Basic gRPC test FAILED: {results[0].get('error')}")
            return False

    def test_grpc_deduplication(self, concurrent_tasks: int = 10) -> Dict:
        """Test request deduplication in gRPC mode"""
        logger.info(f"=== GRPC DEDUPLICATION TEST ({concurrent_tasks} concurrent tasks) ===")

        self._set_sync_mode("grpc")

        # Clear master logs to get clean count
        self.docker.clear_logs("crawlab-master")

        # Create tasks simultaneously
        task_ids = []
        start_time = time.time()

        for _i in range(concurrent_tasks):
            task_id = self.client.create_task(self.test_spider_id)
            task_ids.append(task_id)

        logger.info(f"Created {concurrent_tasks} tasks simultaneously")

        # Wait for completion
        results = self._wait_for_tasks(task_ids, timeout=300)
        end_time = time.time()

        # Analyze logs for deduplication evidence
        scan_count = self._count_directory_scans()
        subscriber_notifications = self._count_subscriber_notifications()

        success_count = sum(1 for r in results if r["status"] == "success")
        success_rate = (success_count / len(results)) * 100

        report = {
            "mode": "grpc",
            "concurrent_tasks": concurrent_tasks,
            "success_rate": success_rate,
            "directory_scans": scan_count,
            "expected_scans": 1,
            "deduplication_working": scan_count == 1,
            "subscriber_notifications": subscriber_notifications,
            "total_time_sec": round(end_time - start_time, 2),
        }

        if scan_count == 1:
            logger.info(f"✅ Deduplication WORKING: {concurrent_tasks} tasks = 1 scan")
        else:
            logger.warning(f"⚠️  Deduplication PARTIAL: {concurrent_tasks} tasks = {scan_count} scans")

        logger.info(f"Deduplication Results: {json.dumps(report, indent=2)}")
        return report

    def test_cache_effectiveness(self, interval_sec: int = 5, tasks: int = 20) -> Dict:
        """Test cache hit rate"""
        logger.info(f"=== CACHE EFFECTIVENESS TEST ({tasks} tasks over {interval_sec}s) ===")

        self._set_sync_mode("grpc")
        self.docker.clear_logs("crawlab-master")

        task_ids = []
        for i in range(tasks):
            task_id = self.client.create_task(self.test_spider_id)
            task_ids.append(task_id)
            if (i + 1) % 5 == 0:
                time.sleep(interval_sec)  # Stagger tasks

        # Wait for completion
        self._wait_for_tasks(task_ids, timeout=300)

        # Count cache hits vs scans
        scan_count = self._count_directory_scans()
        cache_hits = self._count_cache_hits()
        total_requests = scan_count + cache_hits
        cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0

        report = {
            "mode": "grpc",
            "total_requests": total_requests,
            "scans": scan_count,
            "cache_hits": cache_hits,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "target_cache_hit_rate": 90.0,
        }

        if cache_hit_rate >= 90:
            logger.info(f"✅ Cache effectiveness EXCELLENT: {cache_hit_rate:.1f}% hit rate")
        elif cache_hit_rate >= 70:
            logger.info(f"⚠️  Cache effectiveness GOOD: {cache_hit_rate:.1f}% hit rate")
        else:
            logger.warning(f"❌ Cache effectiveness LOW: {cache_hit_rate:.1f}% hit rate")

        logger.info(f"Cache Results: {json.dumps(report, indent=2)}")
        return report

    def compare_modes(self, concurrent_tasks: int = 10, iterations: int = 3) -> Dict:
        """Compare HTTP vs gRPC performance"""
        logger.info(f"=== MODE COMPARISON TEST ({concurrent_tasks} tasks × {iterations} iterations) ===")

        http_results = []
        grpc_results = []

        for i in range(iterations):
            logger.info(f"\n--- Iteration {i+1}/{iterations} ---")

            # Test HTTP mode
            logger.info("Testing HTTP mode...")
            http_result = self.measure_baseline_http(concurrent_tasks)
            http_results.append(http_result)
            time.sleep(10)  # Cool down

            # Test gRPC mode
            logger.info("Testing gRPC mode...")
            grpc_result = self.test_grpc_deduplication(concurrent_tasks)
            grpc_results.append(grpc_result)
            time.sleep(10)  # Cool down

        # Calculate averages
        http_avg = self._average_results(http_results)
        grpc_avg = self._average_results(grpc_results)

        # Calculate improvements
        improvements = {
            "success_rate_increase_percent": round(grpc_avg["success_rate"] - http_avg["success_rate"], 2),
            "latency_reduction_percent": round(
                (1 - grpc_avg.get("avg_duration_sec", 0) / http_avg.get("avg_duration_sec", 1)) * 100, 2
            ),
            "deduplication_ratio": f"1:{concurrent_tasks}" if grpc_avg.get("deduplication_working") else "none",
        }

        report = {"http_average": http_avg, "grpc_average": grpc_avg, "improvements": improvements}

        logger.info("\n" + "=" * 60)
        logger.info("COMPARISON SUMMARY")
        logger.info("=" * 60)
        logger.info(json.dumps(report, indent=2))
        logger.info("=" * 60)

        return report

    def run_full_suite(self) -> Dict:
        """Run complete test suite"""
        logger.info("\n" + "=" * 60)
        logger.info("RUNNING FULL TEST SUITE")
        logger.info("=" * 60 + "\n")

        results = {"timestamp": datetime.now().isoformat(), "tests": {}}

        # Test 1: Basic gRPC
        results["tests"]["basic_grpc"] = {"passed": self.test_grpc_basic()}
        time.sleep(5)

        # Test 2: Deduplication
        results["tests"]["deduplication"] = self.test_grpc_deduplication(10)
        time.sleep(5)

        # Test 3: Cache effectiveness
        results["tests"]["cache"] = self.test_cache_effectiveness(5, 20)
        time.sleep(5)

        # Test 4: Performance comparison
        results["tests"]["comparison"] = self.compare_modes(10, 2)

        # Save results
        output_file = f"results/file_sync_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("results", exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n✅ Full test suite completed. Results saved to: {output_file}")
        return results

    # Helper methods

    def _set_sync_mode(self, mode: str):
        """Set file sync mode (http or grpc)"""
        use_grpc = "true" if mode == "grpc" else "false"

        if self.master_container:
            # Set via Docker exec
            try:
                self.docker.exec_in_container(
                    self.master_container, ["sh", "-c", f"export CRAWLAB_SYNC_USEGRPC={use_grpc}"]
                )
                logger.info(f"Set sync mode to: {mode.upper()} in container {self.master_container}")
            except Exception as e:
                logger.warning(f"Could not set env var in container, will rely on config file: {e}")
        else:
            logger.warning("Master container not found, sync mode may need manual configuration")

        time.sleep(2)  # Let config reload

    def _wait_for_tasks(self, task_ids: List[str], timeout: int = 300) -> List[Dict]:
        """Wait for tasks to complete"""
        start_time = time.time()
        results = []

        for task_id in task_ids:
            elapsed = time.time() - start_time
            remaining = max(1, timeout - int(elapsed))

            status = self.client.wait_for_task(task_id, timeout=remaining)
            duration = time.time() - start_time

            results.append({"task_id": task_id, "status": status, "duration": duration})

        return results

    def _get_master_logs(self, tail: int = 1000) -> str:
        """Get master container logs"""
        if not self.master_container or not self.docker:
            logger.warning("Master container not available, cannot get logs")
            return ""

        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), self.master_container],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout + result.stderr
        except Exception as e:
            logger.warning(f"Failed to get logs: {e}")
            return ""

    def _count_json_errors_in_logs(self) -> int:
        """Count JSON parsing errors in master logs"""
        logs = self._get_master_logs(tail=1000)
        return logs.count("error unmarshaling JSON")

    def _count_directory_scans(self) -> int:
        """Count directory scans in master logs"""
        logs = self._get_master_logs(tail=1000)
        return logs.count("performing directory scan")

    def _count_subscriber_notifications(self) -> int:
        """Count subscriber notifications in logs"""
        logs = self._get_master_logs(tail=1000)
        # Look for "notified N subscribers" pattern
        import re

        matches = re.findall(r"notified (\d+) subscribers", logs)
        return sum(int(m) for m in matches)

    def _count_cache_hits(self) -> int:
        """Count cache hits in master logs"""
        logs = self._get_master_logs(tail=1000)
        return logs.count("returning cached scan")

    def _average_results(self, results: List[Dict]) -> Dict:
        """Calculate average of multiple test results"""
        if not results:
            return {}

        avg = {}
        keys = results[0].keys()

        for key in keys:
            values = [r.get(key) for r in results if isinstance(r.get(key), (int, float))]
            if values:
                avg[key] = round(sum(values) / len(values), 2)

        return avg


def main():
    parser = argparse.ArgumentParser(description="File Sync gRPC Test Helper")
    parser.add_argument("--api-url", default=None, help="Crawlab API URL (auto-detected if not provided)")
    parser.add_argument("--spider-id", help="Test spider ID (required)")

    # Test modes
    parser.add_argument("--smoke-test", action="store_true", help="Run quick smoke test")
    parser.add_argument("--run-full-suite", action="store_true", help="Run complete test suite")
    parser.add_argument("--mode", choices=["http", "grpc"], help="Specific mode to test")
    parser.add_argument("--concurrent-tasks", type=int, default=10, help="Number of concurrent tasks")

    # Specific tests
    parser.add_argument("--measure-baseline", action="store_true", help="Measure HTTP baseline")
    parser.add_argument("--verify-deduplication", action="store_true", help="Test deduplication")
    parser.add_argument("--test-cache", action="store_true", help="Test cache effectiveness")
    parser.add_argument("--compare-modes", action="store_true", help="Compare HTTP vs gRPC")

    args = parser.parse_args()

    if not args.spider_id:
        logger.error("--spider-id is required")
        sys.exit(1)

    tester = FileSyncTester(args.api_url)
    tester.test_spider_id = args.spider_id

    try:
        if args.run_full_suite:
            tester.run_full_suite()
        elif args.smoke_test:
            tester.test_grpc_basic()
        elif args.measure_baseline:
            tester.measure_baseline_http(args.concurrent_tasks)
        elif args.verify_deduplication:
            tester.test_grpc_deduplication(args.concurrent_tasks)
        elif args.test_cache:
            tester.test_cache_effectiveness()
        elif args.compare_modes:
            tester.compare_modes(args.concurrent_tasks)
        else:
            logger.error("Please specify a test action")
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
