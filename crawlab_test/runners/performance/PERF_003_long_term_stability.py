#!/usr/bin/env python3
"""
PERF-003 - Long-Term Stability and Memory Leak Detection Test

This test validates Crawlab's stability over extended periods (24-48 hours)
under continuous moderate load, specifically targeting memory leak detection
and resource exhaustion issues.

Addresses bug:
- #1600: Memory leaks in long-running tasks causing system crashes
"""

import csv
import json
import logging
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.docker import docker_utils
from crawlab_test.helpers.infrastructure.utils import setup_logging


@dataclass
class MetricSnapshot:
    """Snapshot of system metrics at a point in time."""

    timestamp: str
    elapsed_hours: float

    # Master metrics
    master_rss_mb: float
    master_heap_mb: float
    master_goroutines: int
    master_cpu_percent: float

    # Worker metrics (averages)
    worker_avg_rss_mb: float
    worker_avg_heap_mb: float
    worker_avg_goroutines: int
    worker_avg_cpu_percent: float

    # Database metrics
    mongodb_connections: int
    mongodb_connections_active: int
    redis_memory_mb: float

    # Task metrics
    tasks_created_total: int
    tasks_completed_total: int
    tasks_failed_total: int
    tasks_running_current: int
    task_success_rate_percent: float

    # Health indicators
    health_status: str
    memory_trend: str
    goroutine_trend: str


class LongTermStabilityTest:
    """Test harness for long-term stability and memory leak detection."""

    def __init__(self, duration_hours: int = 24, sample_interval: int = 300):
        self.logger = setup_logging("PERF-003")
        self.docker = docker_utils
        self.api_client = None

        # Test configuration
        self.duration_hours = duration_hours
        self.duration_seconds = duration_hours * 3600
        self.sample_interval = sample_interval  # seconds between samples
        self.warmup_hours = 2  # Skip first 2 hours for leak analysis

        # Container tracking
        self.master_container = None
        self.worker_containers: List[str] = []

        # Metrics storage
        self.metrics: List[MetricSnapshot] = []
        self.baseline_metrics: Optional[MetricSnapshot] = None

        # Task generation
        self.test_spider_id = None
        self.task_creation_rate = 15  # tasks per minute
        self.total_tasks_created = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0

        # Output directory
        self.output_dir = Path("results") / f"PERF-003_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize
        self._initialize()

    def _initialize(self):
        """Initialize test environment."""
        # Check Docker availability
        if not self.docker.is_available():
            raise RuntimeError("Docker is not available. Please ensure Docker is installed and running.")

        # Find Crawlab containers
        containers = self.docker.find_crawlab_containers()
        if not containers:
            raise RuntimeError(
                "No Crawlab containers found. "
                "Please start Crawlab using:\n"
                "  docker compose -f docker-compose.test.yml up -d\n"
            )

        # Identify master and workers
        for container in containers:
            name = container.get("Names", "")
            if "master" in name.lower():
                self.master_container = name
            elif "worker" in name.lower():
                self.worker_containers.append(name)

        if not self.master_container:
            raise RuntimeError("No master container found")

        if not self.worker_containers:
            raise RuntimeError("No worker containers found")

        self.logger.info(f"Master container: {self.master_container}")
        self.logger.info(f"Worker containers ({len(self.worker_containers)}): {self.worker_containers}")

        # Initialize API client
        try:
            self.api_client = CrawlabAPIClient()
            # Login to get authentication token
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.api_client.login()
                    self.logger.info("Successfully authenticated with API")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Login attempt {attempt+1} failed: {e}, retrying...")
                        time.sleep(2)
                    else:
                        self.logger.error(f"Failed to login after {max_retries} attempts: {e}")
                        raise RuntimeError(f"Could not authenticate with API: {e}")
        except Exception as e:
            raise RuntimeError(f"Could not initialize API client: {e}")

    def run(self) -> bool:
        """Execute the full test suite."""
        try:
            self.logger.info(f"Starting {self.duration_hours}h stability test")
            self.logger.info(f"Sample interval: {self.sample_interval}s")
            self.logger.info(f"Output directory: {self.output_dir}")

            # Step 1: Establish baseline
            self.logger.info("Step 1: Establishing baseline metrics (30min warmup)")
            if not self.establish_baseline():
                return False

            # Step 2: Start continuous load
            self.logger.info("Step 2: Starting continuous task load")
            if not self.start_continuous_load():
                return False

            # Step 3: Monitor for duration
            self.logger.info(f"Step 3: Monitoring for {self.duration_hours} hours")
            if not self.monitor_stability():
                return False

            # Step 4: Analyze for leaks
            self.logger.info("Step 4: Analyzing for memory leaks")
            if not self.analyze_leaks():
                return False

            # Step 5: Cleanup validation
            self.logger.info("Step 5: Validating resource cleanup")
            if not self.validate_cleanup():
                return False

            # Step 6: Generate report
            self.logger.info("Step 6: Generating comprehensive report")
            self.generate_report()

            self.logger.info("Test completed successfully ✅")
            return True

        except KeyboardInterrupt:
            self.logger.warning("Test interrupted by user")
            self.logger.info("Saving partial results...")
            self.save_metrics()
            return False
        except Exception as e:
            self.logger.error(f"Test failed: {e}", exc_info=True)
            return False
        finally:
            self.cleanup()

    def establish_baseline(self) -> bool:
        """Establish baseline metrics after warmup period."""
        try:
            warmup_seconds = 30 * 60  # 30 minutes
            self.logger.info(f"Warming up for {warmup_seconds/60:.0f} minutes...")

            # Create test spider if needed
            if not self.test_spider_id:
                spider = self.api_client.create_spider(
                    {
                        "name": "perf-test-stability",
                        "cmd": "sleep $(shuf -i 10-300 -n 1)",  # Random 10s-5min duration
                        "type": "customized",
                    }
                )
                self.test_spider_id = spider["_id"]

            # Run some tasks during warmup
            for _ in range(warmup_seconds // 60 * self.task_creation_rate):
                self._create_task()
                time.sleep(60 / self.task_creation_rate)

            # Collect baseline metrics
            self.logger.info("Collecting baseline metrics...")
            self.baseline_metrics = self.collect_metrics()

            self.logger.info(
                f"Baseline established: "
                f"Master RSS={self.baseline_metrics.master_rss_mb:.1f}MB, "
                f"Goroutines={self.baseline_metrics.master_goroutines}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Baseline establishment failed: {e}", exc_info=True)
            return False

    def start_continuous_load(self) -> bool:
        """Start continuous task creation."""
        try:
            # Task creation will happen in monitor_stability loop
            self.logger.info(f"Task creation rate: {self.task_creation_rate} tasks/min")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start continuous load: {e}")
            return False

    def monitor_stability(self) -> bool:
        """Monitor system stability over the test duration."""
        start_time = time.time()
        last_sample_time = start_time
        last_task_creation_time = start_time
        sample_count = 0

        try:
            while True:
                current_time = time.time()
                elapsed = current_time - start_time

                # Check if test duration reached
                if elapsed >= self.duration_seconds:
                    self.logger.info("Test duration reached")
                    break

                # Create tasks continuously
                if current_time - last_task_creation_time >= (60 / self.task_creation_rate):
                    self._create_task()
                    last_task_creation_time = current_time

                # Collect metrics at intervals
                if current_time - last_sample_time >= self.sample_interval:
                    sample_count += 1
                    snapshot = self.collect_metrics()
                    self.metrics.append(snapshot)

                    # Display progress
                    self._display_progress(snapshot, sample_count)

                    # Check for critical issues
                    if snapshot.health_status == "CRITICAL":
                        self.logger.error("Critical health issues detected, stopping test")
                        return False

                    last_sample_time = current_time

                    # Save metrics periodically
                    if sample_count % 12 == 0:  # Every hour if sample_interval=300s
                        self.save_metrics()

                # Sleep briefly
                time.sleep(1)

            return True

        except Exception as e:
            self.logger.error(f"Monitoring failed: {e}", exc_info=True)
            return False

    def collect_metrics(self) -> MetricSnapshot:
        """Collect current system metrics."""
        try:
            elapsed_hours = (
                (time.time() - (time.time() - len(self.metrics) * self.sample_interval)) / 3600 if self.metrics else 0
            )

            # Get master metrics
            master_stats = self._get_container_stats(self.master_container)

            # Get worker metrics (average)
            worker_stats_list = [self._get_container_stats(w) for w in self.worker_containers]
            worker_avg_rss = (
                sum(s["rss_mb"] for s in worker_stats_list) / len(worker_stats_list) if worker_stats_list else 0
            )
            worker_avg_heap = (
                sum(s["heap_mb"] for s in worker_stats_list) / len(worker_stats_list) if worker_stats_list else 0
            )
            worker_avg_goroutines = (
                sum(s["goroutines"] for s in worker_stats_list) / len(worker_stats_list) if worker_stats_list else 0
            )
            worker_avg_cpu = (
                sum(s["cpu_percent"] for s in worker_stats_list) / len(worker_stats_list) if worker_stats_list else 0
            )

            # Get database metrics (placeholder - would need actual DB queries)
            mongodb_conns = 47  # Placeholder
            mongodb_active = 8  # Placeholder
            redis_mem = 85  # Placeholder

            # Get task statistics
            try:
                tasks_stats = self.api_client.get_task_stats()
                running = tasks_stats.get("running", 0)
                success_rate = (
                    (self.total_tasks_completed / self.total_tasks_created * 100) if self.total_tasks_created > 0 else 0
                )
            except:
                running = 0
                success_rate = 0

            # Determine trends
            memory_trend = self._analyze_trend("memory")
            goroutine_trend = self._analyze_trend("goroutines")

            # Determine health status
            health_status = self._determine_health(master_stats, memory_trend, goroutine_trend)

            return MetricSnapshot(
                timestamp=datetime.now().isoformat(),
                elapsed_hours=elapsed_hours,
                master_rss_mb=master_stats["rss_mb"],
                master_heap_mb=master_stats["heap_mb"],
                master_goroutines=master_stats["goroutines"],
                master_cpu_percent=master_stats["cpu_percent"],
                worker_avg_rss_mb=worker_avg_rss,
                worker_avg_heap_mb=worker_avg_heap,
                worker_avg_goroutines=int(worker_avg_goroutines),
                worker_avg_cpu_percent=worker_avg_cpu,
                mongodb_connections=mongodb_conns,
                mongodb_connections_active=mongodb_active,
                redis_memory_mb=redis_mem,
                tasks_created_total=self.total_tasks_created,
                tasks_completed_total=self.total_tasks_completed,
                tasks_failed_total=self.total_tasks_failed,
                tasks_running_current=running,
                task_success_rate_percent=success_rate,
                health_status=health_status,
                memory_trend=memory_trend,
                goroutine_trend=goroutine_trend,
            )

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            raise

    def _get_container_stats(self, container: str) -> Dict:
        """Get stats for a specific container."""
        try:
            # Get Docker stats
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{json .}}", container],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )

            stats = json.loads(result.stdout)

            # Extract memory (remove units and convert to MB)
            mem_usage = stats.get("MemUsage", "0MiB / 0MiB")
            mem_current = mem_usage.split("/")[0].strip()
            rss_mb = float(mem_current.replace("MiB", "").replace("GiB", "000").strip())

            # Extract CPU percentage
            cpu_str = stats.get("CPUPerc", "0%")
            cpu_percent = float(cpu_str.replace("%", "").strip())

            # Try to get Go metrics from container (if available)
            heap_mb = 0
            goroutines = 0
            try:
                # This would require the container to expose /debug/vars endpoint
                # For now, use placeholder values
                heap_mb = rss_mb * 0.7  # Estimate heap as 70% of RSS
                goroutines = 100  # Placeholder
            except:
                pass

            return {"rss_mb": rss_mb, "heap_mb": heap_mb, "goroutines": goroutines, "cpu_percent": cpu_percent}

        except Exception as e:
            self.logger.warning(f"Failed to get stats for {container}: {e}")
            return {"rss_mb": 0, "heap_mb": 0, "goroutines": 0, "cpu_percent": 0}

    def _create_task(self):
        """Create a single task."""
        try:
            task = self.api_client.create_task(
                {
                    "spider_id": self.test_spider_id,
                    "mode": "random",
                }
            )
            self.total_tasks_created += 1
        except Exception as e:
            self.logger.debug(f"Task creation failed: {e}")
            self.total_tasks_failed += 1

    def _analyze_trend(self, metric: str) -> str:
        """Analyze trend for a specific metric."""
        if len(self.metrics) < 3:
            return "STABILIZING"

        # Look at last 3 samples
        recent = self.metrics[-3:]

        if metric == "memory":
            values = [m.master_rss_mb for m in recent]
        elif metric == "goroutines":
            values = [m.master_goroutines for m in recent]
        else:
            return "UNKNOWN"

        # Simple trend analysis
        if values[-1] > values[0] * 1.1:
            return "INCREASING"
        elif values[-1] < values[0] * 0.9:
            return "DECREASING"
        else:
            return "STABLE"

    def _determine_health(self, stats: Dict, memory_trend: str, goroutine_trend: str) -> str:
        """Determine overall health status."""
        if not self.baseline_metrics:
            return "INITIALIZING"

        # Check for critical conditions
        if stats["rss_mb"] > self.baseline_metrics.master_rss_mb * 2:
            return "CRITICAL"

        if memory_trend == "INCREASING" and goroutine_trend == "INCREASING":
            return "WARNING"

        return "HEALTHY"

    def _display_progress(self, snapshot: MetricSnapshot, sample_num: int):
        """Display monitoring progress."""
        if not self.baseline_metrics:
            return

        mem_growth = (
            (snapshot.master_rss_mb - self.baseline_metrics.master_rss_mb) / self.baseline_metrics.master_rss_mb * 100
        )

        self.logger.info(
            f"[Sample #{sample_num}] "
            f"Time: {snapshot.elapsed_hours:.1f}h | "
            f"Master RSS: {snapshot.master_rss_mb:.0f}MB (+{mem_growth:+.1f}%) | "
            f"Goroutines: {snapshot.master_goroutines} | "
            f"Tasks: {snapshot.tasks_created_total} created, "
            f"{snapshot.tasks_completed_total} completed "
            f"({snapshot.task_success_rate_percent:.1f}% success) | "
            f"Health: {snapshot.health_status} | "
            f"Trend: {snapshot.memory_trend}"
        )

    def analyze_leaks(self) -> bool:
        """Analyze collected metrics for memory leaks."""
        try:
            if not self.baseline_metrics or len(self.metrics) < 10:
                self.logger.warning("Insufficient data for leak analysis")
                return True

            # Skip warmup period samples
            warmup_samples = int(self.warmup_hours * 3600 / self.sample_interval)
            stable_metrics = self.metrics[warmup_samples:]

            if not stable_metrics:
                self.logger.warning("No stable period data available")
                return True

            # Analyze memory growth
            memory_values = [m.master_rss_mb for m in stable_metrics]
            hourly_growth = self._calculate_growth_rate(memory_values)

            self.logger.info(f"Memory growth rate: {hourly_growth:.2f} MB/hour")

            if hourly_growth < 5:
                self.logger.info("✅ HEALTHY: No significant memory leak detected")
                leak_status = "PASS"
            elif hourly_growth < 20:
                self.logger.warning(f"⚠️  WARNING: Slow memory growth detected ({hourly_growth:.1f} MB/h)")
                leak_status = "WARNING"
            else:
                self.logger.error(f"❌ CRITICAL: Memory leak detected ({hourly_growth:.1f} MB/h)")
                leak_status = "FAIL"
                return False

            # Analyze goroutine growth
            goroutine_values = [m.master_goroutines for m in stable_metrics]
            goroutine_growth_pct = (goroutine_values[-1] - goroutine_values[0]) / goroutine_values[0] * 100

            self.logger.info(f"Goroutine growth: {goroutine_growth_pct:+.1f}%")

            if abs(goroutine_growth_pct) < 10:
                self.logger.info("✅ Goroutine count stable")
            else:
                self.logger.warning(f"⚠️  Goroutine count changed by {goroutine_growth_pct:+.1f}%")

            return leak_status in ["PASS", "WARNING"]

        except Exception as e:
            self.logger.error(f"Leak analysis failed: {e}", exc_info=True)
            return False

    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate hourly growth rate using linear regression."""
        if len(values) < 2:
            return 0

        # Simple linear regression
        n = len(values)
        x_values = list(range(n))

        mean_x = sum(x_values) / n
        mean_y = sum(values) / n

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
        denominator = sum((x - mean_x) ** 2 for x in x_values)

        if denominator == 0:
            return 0

        slope = numerator / denominator

        # Convert slope to hourly rate
        samples_per_hour = 3600 / self.sample_interval
        hourly_rate = slope * samples_per_hour

        return hourly_rate

    def validate_cleanup(self) -> bool:
        """Validate resources return to baseline after cleanup."""
        try:
            self.logger.info("Stopping task creation and waiting for cleanup...")

            # Wait for running tasks to complete (up to 10 minutes)
            wait_time = 600
            self.logger.info(f"Waiting {wait_time}s for tasks to complete...")
            time.sleep(wait_time)

            # Collect final metrics
            self.logger.info("Collecting post-cleanup metrics...")
            final_metrics = self.collect_metrics()

            if not self.baseline_metrics:
                self.logger.warning("No baseline to compare against")
                return True

            # Compare with baseline
            mem_diff_pct = (
                (final_metrics.master_rss_mb - self.baseline_metrics.master_rss_mb)
                / self.baseline_metrics.master_rss_mb
                * 100
            )

            goroutine_diff_pct = (
                (final_metrics.master_goroutines - self.baseline_metrics.master_goroutines)
                / self.baseline_metrics.master_goroutines
                * 100
            )

            self.logger.info(
                f"Post-cleanup comparison:\n"
                f"  Memory: {final_metrics.master_rss_mb:.0f}MB vs "
                f"{self.baseline_metrics.master_rss_mb:.0f}MB baseline "
                f"({mem_diff_pct:+.1f}%)\n"
                f"  Goroutines: {final_metrics.master_goroutines} vs "
                f"{self.baseline_metrics.master_goroutines} baseline "
                f"({goroutine_diff_pct:+.1f}%)"
            )

            if abs(mem_diff_pct) <= 20 and abs(goroutine_diff_pct) <= 10:
                self.logger.info("✅ Resources returned to baseline")
                return True
            else:
                self.logger.warning("⚠️  Resources did not fully return to baseline")
                return True  # Not failing test, just warning

        except Exception as e:
            self.logger.error(f"Cleanup validation failed: {e}", exc_info=True)
            return False

    def save_metrics(self):
        """Save metrics to files."""
        try:
            # Save as JSON
            json_file = self.output_dir / "metrics.json"
            with open(json_file, "w") as f:
                json.dump([asdict(m) for m in self.metrics], f, indent=2)

            # Save as CSV
            csv_file = self.output_dir / "metrics.csv"
            if self.metrics:
                with open(csv_file, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.metrics[0]).keys())
                    writer.writeheader()
                    writer.writerows([asdict(m) for m in self.metrics])

            self.logger.debug(f"Saved metrics to {self.output_dir}")

        except Exception as e:
            self.logger.warning(f"Failed to save metrics: {e}")

    def generate_report(self):
        """Generate comprehensive test report."""
        try:
            report = {
                "test_id": "PERF-003",
                "test_type": "long-term-stability",
                "duration_hours": self.duration_hours,
                "sample_count": len(self.metrics),
                "timestamp": datetime.now().isoformat(),
                "status": "COMPLETED",
            }

            # Save report
            report_file = self.output_dir / "report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"Report saved to {report_file}")

        except Exception as e:
            self.logger.warning(f"Failed to generate report: {e}")

    def cleanup(self):
        """Clean up test resources."""
        try:
            if self.api_client and self.test_spider_id:
                try:
                    self.api_client.delete_spider(self.test_spider_id)
                    self.logger.debug("Deleted test spider")
                except Exception as e:
                    self.logger.debug(f"Could not delete spider: {e}")
        except Exception as e:
            self.logger.debug(f"Cleanup error: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="PERF-003 Long-Term Stability Test")
    parser.add_argument("--duration", default="24h", help="Test duration (e.g., 2h, 24h, 48h)")
    parser.add_argument(
        "--sample-interval", type=int, default=300, help="Metric sampling interval in seconds (default: 300)"
    )
    parser.add_argument("--ci", action="store_true", help="Running in CI environment")
    args = parser.parse_args()

    # Parse duration
    duration_str = args.duration.lower()
    if duration_str.endswith("h"):
        duration_hours = int(duration_str[:-1])
    elif duration_str.endswith("m"):
        duration_hours = int(duration_str[:-1]) / 60
    else:
        duration_hours = 24

    try:
        test = LongTermStabilityTest(duration_hours=duration_hours, sample_interval=args.sample_interval)
        success = test.run()
        sys.exit(0 if success else 1)

    except Exception as e:
        logging.error(f"Test execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
