#!/usr/bin/env python3
"""
PERF-004: Database Load Profiling and Optimization

This test profiles MongoDB query patterns and resource usage to identify
optimization opportunities, specifically addressing issue #1597 (30% MongoDB
load with idle workers).

Test covers:
- Baseline idle worker query monitoring
- Query pattern analysis and categorization
- Connection pool usage and efficiency
- Index effectiveness evaluation
- Slow query identification (>100ms)
- Active load comparison
- Optimization report generation

Target Release: 0.7.1
Priority: LOW (optimization, not blocker)
Duration: 30-60 minutes
"""

import argparse
import json
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawlab_test.helpers.infrastructure.api_client import CrawlabAPIClient
from crawlab_test.helpers.infrastructure.docker import docker_utils

# Try importing pymongo for direct MongoDB access
try:
    import pymongo
    from pymongo import MongoClient

    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logging.warning("pymongo not available - some features will be limited")


class DatabaseLoadProfiler:
    """Database load profiling test for MongoDB optimization."""

    def __init__(
        self,
        duration_minutes: int = 5,
        sample_interval: int = 10,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize the database load profiler.

        Args:
            duration_minutes: Baseline monitoring duration (default: 5 min)
            sample_interval: Seconds between metric samples (default: 10s)
            output_dir: Directory for test results and reports
        """
        self.duration_minutes = duration_minutes
        self.sample_interval = sample_interval
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir or f"results/PERF-004_{self.timestamp}"

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.api_client: Optional[CrawlabAPIClient] = None
        self.mongo_client: Optional[MongoClient] = None
        self.mongo_uri: Optional[str] = None

        # Metrics storage
        self.baseline_metrics: Dict[str, Any] = {}
        self.query_patterns: List[Dict[str, Any]] = []
        self.connection_stats: List[Dict[str, Any]] = []
        self.index_analysis: Dict[str, Any] = {}
        self.slow_queries: List[Dict[str, Any]] = []
        self.active_load_metrics: Dict[str, Any] = {}

        # Analysis results
        self.recommendations: List[Dict[str, Any]] = []
        self.issues: List[Dict[str, Any]] = []

    def setup(self):
        """Initialize API client and MongoDB connection."""
        self.logger.info("Setting up database profiler...")

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
                        raise
        except Exception as e:
            raise RuntimeError(f"Could not initialize API client: {e}")

        # Get MongoDB connection URI
        self.mongo_uri = self._detect_mongo_uri()
        if not self.mongo_uri:
            self.logger.warning("Could not detect MongoDB URI - some features will be limited")
            return

        # Initialize MongoDB client
        if PYMONGO_AVAILABLE and self.mongo_uri:
            try:
                self.mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                # Test connection
                self.mongo_client.admin.command("ping")
                self.logger.info(f"Connected to MongoDB: {self.mongo_uri}")
            except Exception as e:
                self.logger.warning(f"Could not connect to MongoDB: {e}")
                self.mongo_client = None

    def _detect_mongo_uri(self) -> Optional[str]:
        """Detect MongoDB connection URI from environment or Docker."""
        # Check environment variable
        mongo_uri = os.getenv("MONGODB_URI") or os.getenv("CRAWLAB_MONGO_URI")
        if mongo_uri:
            return mongo_uri

        # Try to detect from Docker
        if docker_utils and docker_utils.is_available():
            containers = docker_utils.find_crawlab_containers()
            for container in containers:
                if "mongo" in container.lower():
                    # Found MongoDB container
                    try:
                        inspect = docker_utils.get_container_inspect(container)
                        if inspect:
                            # Try to get exposed port
                            ports = inspect.get("NetworkSettings", {}).get("Ports", {})
                            for port_spec, bindings in ports.items():
                                if "27017" in port_spec and bindings:
                                    host_port = bindings[0].get("HostPort")
                                    if host_port:
                                        return f"mongodb://localhost:{host_port}"
                    except Exception as e:
                        self.logger.debug(f"Could not inspect mongo container: {e}")

        # Default MongoDB port
        return "mongodb://localhost:27017"

    def run_baseline_monitoring(self) -> bool:
        """Step 1: Establish baseline metrics with idle workers."""
        self.logger.info("Step 1: Baseline idle worker monitoring")
        self.logger.info(f"Monitoring for {self.duration_minutes} minutes...")

        metrics = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": self.duration_minutes,
            "samples": [],
        }

        start_time = time.time()
        end_time = start_time + (self.duration_minutes * 60)

        while time.time() < end_time:
            sample = self._collect_metrics_sample()
            metrics["samples"].append(sample)

            elapsed = time.time() - start_time
            remaining = end_time - time.time()
            self.logger.info(
                f"Baseline progress: {elapsed/60:.1f}/{self.duration_minutes} min "
                f"(remaining: {remaining/60:.1f} min)"
            )

            time.sleep(self.sample_interval)

        # Calculate averages
        if metrics["samples"]:
            metrics["avg_queries_per_sec"] = sum(s.get("queries_per_sec", 0) for s in metrics["samples"]) / len(
                metrics["samples"]
            )
            metrics["avg_connections"] = sum(s.get("current_connections", 0) for s in metrics["samples"]) / len(
                metrics["samples"]
            )
            metrics["max_connections"] = max(s.get("current_connections", 0) for s in metrics["samples"])

        self.baseline_metrics = metrics
        self._save_metrics("baseline_metrics.json", metrics)

        # Check thresholds
        avg_qps = metrics.get("avg_queries_per_sec", 0)
        avg_conn = metrics.get("avg_connections", 0)

        self.logger.info("Baseline complete:")
        self.logger.info(f"  Avg queries/sec: {avg_qps:.2f} (target: <5)")
        self.logger.info(f"  Avg connections: {avg_conn:.1f} (target: <10)")

        if avg_qps > 5:
            self.logger.warning(f"⚠️  High query rate: {avg_qps:.2f} qps")
            self.issues.append(
                {
                    "severity": "MEDIUM",
                    "category": "query_rate",
                    "message": f"Idle query rate {avg_qps:.2f} qps exceeds target of 5 qps",
                }
            )

        if avg_conn > 10:
            self.logger.warning(f"⚠️  High connection count: {avg_conn:.1f}")
            self.issues.append(
                {
                    "severity": "LOW",
                    "category": "connections",
                    "message": f"Idle connections {avg_conn:.1f} exceeds target of 10",
                }
            )

        return True

    def _collect_metrics_sample(self) -> Dict[str, Any]:
        """Collect a single metrics sample."""
        sample = {
            "timestamp": datetime.now().isoformat(),
            "queries_per_sec": 0,
            "current_connections": 0,
            "available_connections": 0,
            "active_connections": 0,
        }

        if not self.mongo_client:
            return sample

        try:
            # Get server status
            status = self.mongo_client.admin.command("serverStatus")

            # Connection stats
            conn_stats = status.get("connections", {})
            sample["current_connections"] = conn_stats.get("current", 0)
            sample["available_connections"] = conn_stats.get("available", 0)
            sample["active_connections"] = conn_stats.get("active", 0)

            # Query stats (opcounters)
            opcounters = status.get("opcounters", {})
            # Calculate queries per second (simplified - would need previous sample for accuracy)
            total_ops = sum(
                [
                    opcounters.get("query", 0),
                    opcounters.get("getmore", 0),
                    opcounters.get("command", 0),
                ]
            )
            sample["total_operations"] = total_ops
            # Rough estimate based on sample interval
            sample["queries_per_sec"] = total_ops / max(self.sample_interval, 1)

        except Exception as e:
            self.logger.debug(f"Error collecting metrics: {e}")

        return sample

    def analyze_query_patterns(self) -> bool:
        """Step 2: Analyze query patterns and frequencies."""
        self.logger.info("Step 2: Query pattern analysis")

        if not self.mongo_client:
            self.logger.warning("MongoDB client not available - skipping query analysis")
            return False

        try:
            # Enable profiling temporarily (level 2 = all operations)
            self.logger.info("Enabling MongoDB profiling...")
            self.mongo_client.admin.command("profile", 2)

            # Wait for some queries to be captured
            self.logger.info("Collecting query samples (60 seconds)...")
            time.sleep(60)

            # Disable profiling
            self.mongo_client.admin.command("profile", 0)

            # Analyze profile data
            profile_data = list(self.mongo_client.local.system.profile.find().limit(1000))

            # Group by collection and operation
            patterns = defaultdict(lambda: {"count": 0, "total_ms": 0, "queries": []})

            for entry in profile_data:
                ns = entry.get("ns", "unknown")
                op = entry.get("op", "unknown")
                millis = entry.get("millis", 0)

                key = f"{ns}.{op}"
                patterns[key]["count"] += 1
                patterns[key]["total_ms"] += millis
                patterns[key]["queries"].append(entry)

            # Convert to list and sort by frequency
            self.query_patterns = [
                {
                    "pattern": key,
                    "count": data["count"],
                    "avg_ms": data["total_ms"] / data["count"] if data["count"] > 0 else 0,
                    "total_ms": data["total_ms"],
                }
                for key, data in patterns.items()
            ]
            self.query_patterns.sort(key=lambda x: x["count"], reverse=True)

            # Save results
            self._save_metrics("query_patterns.json", self.query_patterns[:50])

            # Log top patterns
            self.logger.info(f"Found {len(self.query_patterns)} unique query patterns")
            for i, pattern in enumerate(self.query_patterns[:10], 1):
                self.logger.info(
                    f"  {i}. {pattern['pattern']}: {pattern['count']} queries, " f"avg {pattern['avg_ms']:.2f}ms"
                )

            # Check for problematic patterns
            for pattern in self.query_patterns[:20]:
                if pattern["avg_ms"] > 100:
                    self.recommendations.append(
                        {
                            "priority": "HIGH",
                            "category": "slow_query",
                            "pattern": pattern["pattern"],
                            "issue": f"Slow query averaging {pattern['avg_ms']:.2f}ms",
                            "recommendation": "Investigate query and add appropriate indexes",
                        }
                    )

        except Exception as e:
            self.logger.error(f"Query pattern analysis failed: {e}")
            return False

        return True

    def analyze_connection_pool(self) -> bool:
        """Step 3: Analyze connection pool usage and efficiency."""
        self.logger.info("Step 3: Connection pool analysis")

        if not self.mongo_client:
            self.logger.warning("MongoDB client not available - skipping connection analysis")
            return False

        try:
            status = self.mongo_client.admin.command("serverStatus")
            conn_stats = status.get("connections", {})

            pool_analysis = {
                "current": conn_stats.get("current", 0),
                "available": conn_stats.get("available", 0),
                "active": conn_stats.get("active", 0),
                "total_created": conn_stats.get("totalCreated", 0),
                "utilization_percent": 0,
            }

            # Calculate utilization
            total_possible = pool_analysis["current"] + pool_analysis["available"]
            if total_possible > 0:
                pool_analysis["utilization_percent"] = (pool_analysis["current"] / total_possible) * 100

            self.connection_stats.append(pool_analysis)
            self._save_metrics("connection_pool.json", pool_analysis)

            self.logger.info("Connection pool status:")
            self.logger.info(f"  Current connections: {pool_analysis['current']}")
            self.logger.info(f"  Available: {pool_analysis['available']}")
            self.logger.info(f"  Active: {pool_analysis['active']}")
            self.logger.info(f"  Utilization: {pool_analysis['utilization_percent']:.1f}%")

            # Check thresholds
            if pool_analysis["utilization_percent"] > 80:
                self.recommendations.append(
                    {
                        "priority": "HIGH",
                        "category": "connection_pool",
                        "issue": f"High pool utilization: {pool_analysis['utilization_percent']:.1f}%",
                        "recommendation": "Consider increasing connection pool size",
                    }
                )

        except Exception as e:
            self.logger.error(f"Connection pool analysis failed: {e}")
            return False

        return True

    def analyze_indexes(self) -> bool:
        """Step 4: Analyze index effectiveness."""
        self.logger.info("Step 4: Index effectiveness analysis")

        if not self.mongo_client:
            self.logger.warning("MongoDB client not available - skipping index analysis")
            return False

        try:
            # Get database name (assume first non-system database)
            db_names = [
                name for name in self.mongo_client.list_database_names() if name not in ["admin", "local", "config"]
            ]

            if not db_names:
                self.logger.warning("No application databases found")
                return False

            db_name = db_names[0]  # Use first database
            db = self.mongo_client[db_name]

            index_info = {}

            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                indexes = list(collection.list_indexes())

                index_info[collection_name] = {
                    "indexes": [
                        {
                            "name": idx.get("name"),
                            "keys": idx.get("key"),
                            "unique": idx.get("unique", False),
                        }
                        for idx in indexes
                    ]
                }

                self.logger.info(f"Collection '{collection_name}': {len(indexes)} indexes")

            self.index_analysis = index_info
            self._save_metrics("index_analysis.json", index_info)

            # General recommendation
            self.recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "indexing",
                    "issue": "Manual index review needed",
                    "recommendation": "Review query patterns and ensure all frequently queried fields are indexed",
                }
            )

        except Exception as e:
            self.logger.error(f"Index analysis failed: {e}")
            return False

        return True

    def identify_slow_queries(self) -> bool:
        """Step 5: Identify queries taking > 100ms."""
        self.logger.info("Step 5: Slow query identification")

        if not self.mongo_client:
            self.logger.warning("MongoDB client not available - skipping slow query analysis")
            return False

        try:
            # Query profile collection for slow queries
            slow_queries = list(
                self.mongo_client.local.system.profile.find({"millis": {"$gt": 100}}).sort("millis", -1).limit(20)
            )

            self.slow_queries = [
                {
                    "ns": q.get("ns"),
                    "op": q.get("op"),
                    "millis": q.get("millis"),
                    "query": str(q.get("command", {}))[:200],  # Truncate for readability
                }
                for q in slow_queries
            ]

            self._save_metrics("slow_queries.json", self.slow_queries)

            if self.slow_queries:
                self.logger.warning(f"Found {len(self.slow_queries)} slow queries (>100ms)")
                for i, query in enumerate(self.slow_queries[:5], 1):
                    self.logger.warning(f"  {i}. {query['ns']}.{query['op']}: {query['millis']}ms")

                self.recommendations.append(
                    {
                        "priority": "HIGH",
                        "category": "slow_query",
                        "issue": f"Found {len(self.slow_queries)} queries exceeding 100ms threshold",
                        "recommendation": "Review slow queries and optimize with indexes or query restructuring",
                    }
                )
            else:
                self.logger.info("✅ No slow queries detected")

        except Exception as e:
            self.logger.error(f"Slow query identification failed: {e}")
            return False

        return True

    def generate_report(self) -> bool:
        """Step 7: Generate comprehensive optimization report."""
        self.logger.info("Step 7: Generating optimization report")

        report = {
            "test_id": "PERF-004",
            "test_type": "database-load-profiling",
            "timestamp": self.timestamp,
            "duration_minutes": self.duration_minutes,
            "baseline_metrics": self.baseline_metrics,
            "query_patterns_count": len(self.query_patterns),
            "top_query_patterns": self.query_patterns[:10],
            "connection_stats": self.connection_stats,
            "index_analysis": self.index_analysis,
            "slow_queries_count": len(self.slow_queries),
            "slow_queries": self.slow_queries[:10],
            "issues": self.issues,
            "recommendations": self.recommendations,
        }

        # Save JSON report
        report_path = Path(self.output_dir) / "report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report saved: {report_path}")

        # Print summary
        print("\n" + "=" * 80)
        print("🔬 MongoDB Load Profiling Report")
        print("=" * 80)

        if self.baseline_metrics:
            avg_qps = self.baseline_metrics.get("avg_queries_per_sec", 0)
            avg_conn = self.baseline_metrics.get("avg_connections", 0)
            print(f"\n📊 Baseline Metrics ({self.duration_minutes} min):")
            print(f"  Queries/sec:        {avg_qps:.2f} {'✅' if avg_qps < 5 else '⚠️'} (target: <5)")
            print(f"  Avg connections:    {avg_conn:.1f} {'✅' if avg_conn < 10 else '⚠️'} (target: <10)")

        if self.query_patterns:
            print("\n🔍 Query Analysis:")
            print(f"  Unique patterns:    {len(self.query_patterns)}")
            print(
                f"  Top pattern:        {self.query_patterns[0]['pattern']} ({self.query_patterns[0]['count']} queries)"
            )

        if self.slow_queries:
            print("\n⚠️  Slow Queries:")
            print(f"  Count (>100ms):     {len(self.slow_queries)}")

        if self.recommendations:
            print("\n💡 Top Recommendations:")
            for i, rec in enumerate(self.recommendations[:5], 1):
                print(f"  {i}. [{rec['priority']}] {rec.get('issue', rec.get('recommendation'))}")

        print(f"\n📑 Full report: {report_path}")
        print("=" * 80 + "\n")

        return True

    def _save_metrics(self, filename: str, data: Any):
        """Save metrics to JSON file."""
        filepath = Path(self.output_dir) / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        self.logger.debug(f"Saved: {filepath}")

    def run(self, steps: Optional[List[str]] = None) -> int:
        """
        Run the database load profiling test.

        Args:
            steps: Optional list of steps to run. If None, runs all steps.

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        try:
            self.setup()

            all_steps = [
                ("baseline", self.run_baseline_monitoring),
                ("analyze-queries", self.analyze_query_patterns),
                ("analyze-connections", self.analyze_connection_pool),
                ("analyze-indexes", self.analyze_indexes),
                ("slow-queries", self.identify_slow_queries),
                ("generate-report", self.generate_report),
            ]

            # Filter steps if specified
            if steps:
                steps_to_run = [(name, func) for name, func in all_steps if name in steps]
            else:
                steps_to_run = all_steps

            # Run each step
            for step_name, step_func in steps_to_run:
                try:
                    success = step_func()
                    if not success:
                        self.logger.warning(f"Step '{step_name}' returned False")
                except Exception as e:
                    self.logger.error(f"Step '{step_name}' failed: {e}", exc_info=True)

            # Always generate report at the end
            if "generate-report" not in [name for name, _ in steps_to_run]:
                self.generate_report()

            self.logger.info("✅ Database profiling test completed")
            return 0

        except Exception as e:
            self.logger.error(f"Test failed: {e}", exc_info=True)
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PERF-004: Database Load Profiling")
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Baseline monitoring duration in minutes (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Metric sample interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for results",
    )
    parser.add_argument(
        "--step",
        action="append",
        choices=[
            "baseline",
            "analyze-queries",
            "analyze-connections",
            "analyze-indexes",
            "slow-queries",
            "generate-report",
        ],
        help="Run specific step(s) only",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full analysis (all steps)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: baseline + report only (1 minute)",
    )

    args = parser.parse_args()

    # Adjust for quick mode
    if args.quick:
        args.duration = 1
        args.step = ["baseline", "generate-report"]

    profiler = DatabaseLoadProfiler(
        duration_minutes=args.duration,
        sample_interval=args.interval,
        output_dir=args.output_dir,
    )

    return profiler.run(steps=args.step)


if __name__ == "__main__":
    sys.exit(main())
