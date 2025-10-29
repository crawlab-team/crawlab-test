"""
Parallel Test Executor Module

This module provides functionality to execute multiple test specifications in parallel
using Python's multiprocessing for improved test execution speed.
"""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _execute_single_spec(spec_info: Tuple[Path, Dict, Path, Optional[Path]]) -> Dict:
    """
    Execute a single test specification (worker function)

    This function runs in a separate process and must be pickleable.

    Args:
        spec_info: Tuple of (spec_path, config, base_dir, runners_dir)

    Returns:
        Result dictionary with test execution details
    """
    spec_path, config, base_dir, runners_dir = spec_info

    # Import here to avoid pickling issues
    from crawlab_test.backends import CopilotBackend, PlaywrightBackend, ScriptBackend

    result = {
        "spec_path": str(spec_path),
        "start_time": datetime.now().isoformat(),
        "status": "unknown",
        "worker_pid": multiprocessing.current_process().pid,
    }

    try:
        # Determine backend
        backend_name = config.get("backend", "auto")
        backend = None

        if backend_name == "script" or backend_name == "auto":
            script_backend = ScriptBackend(base_dir, runners_dir=runners_dir)
            if script_backend.supports_spec(spec_path):
                backend = script_backend

        if backend is None and (backend_name == "playwright" or backend_name == "auto"):
            playwright_backend = PlaywrightBackend(base_dir)
            if playwright_backend.supports_spec(spec_path) and playwright_backend.check_prerequisites():
                backend = playwright_backend

        if backend is None and (backend_name == "copilot" or backend_name == "auto"):
            copilot_backend = CopilotBackend(base_dir)
            if copilot_backend.check_prerequisites():
                backend = copilot_backend

        if backend is None:
            result["status"] = "error"
            result["error"] = "No suitable backend found"
            result["end_time"] = datetime.now().isoformat()
            return result

        # Execute test
        exec_result = backend.execute(spec_path, config)

        # Merge results
        result.update(exec_result)
        result["backend"] = backend.get_name()

    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Execution failed: {e!s}"
        import traceback

        result["traceback"] = traceback.format_exc()

    result["end_time"] = datetime.now().isoformat()
    return result


class ParallelTestExecutor:
    """Executes test specifications in parallel using process pool"""

    def __init__(self, base_dir: Optional[Path] = None, max_workers: Optional[int] = None):
        """
        Initialize ParallelTestExecutor

        Args:
            base_dir: Base directory for tests
            max_workers: Maximum number of parallel workers (defaults to CPU count)
        """
        if base_dir is None:
            # Check CWD first (development/repo mode)
            cwd = Path.cwd()
            if (cwd / "specs").exists():
                base_dir = cwd
            else:
                # Check package location for bundled specs
                package_dir = Path(__file__).parent.parent
                if (package_dir / "specs").exists():
                    base_dir = package_dir
                else:
                    base_dir = cwd

        self.base_dir = Path(base_dir)
        # Default to CPU count but allow override for I/O-bound tests
        self.max_workers = max_workers or multiprocessing.cpu_count()

        # Calculate runners_dir in main process for reliable subprocess access
        # Always use package location for runners (they're always bundled)
        package_dir = Path(__file__).parent.parent
        self.runners_dir = package_dir / "runners"

    def execute_specs(self, spec_paths: List[Path], config: Dict) -> List[Dict]:
        """
        Execute multiple specs in parallel

        Args:
            spec_paths: List of paths to test specifications
            config: Configuration dictionary for test execution

        Returns:
            List of result dictionaries (one per spec)
        """
        if not spec_paths:
            return []

        # Single spec - no need for parallel execution
        if len(spec_paths) == 1:
            print("Single spec detected, running sequentially")
            return [_execute_single_spec((spec_paths[0], config, self.base_dir, self.runners_dir))]

        # Optimize worker count - no point having more workers than tasks
        effective_workers = min(self.max_workers, len(spec_paths))

        if effective_workers < self.max_workers:
            print(
                f"Executing {len(spec_paths)} specs with {effective_workers} parallel workers (capped from {self.max_workers} to match test count)"
            )
        else:
            print(f"Executing {len(spec_paths)} specs with {effective_workers} parallel workers")
        print("Workers will run in separate processes for isolation")
        print("")

        results = []
        completed_count = 0
        total_count = len(spec_paths)

        # Prepare work items - include runners_dir calculated in main process
        work_items = [(spec_path, config, self.base_dir, self.runners_dir) for spec_path in spec_paths]

        # Execute in parallel with optimized worker count
        with ProcessPoolExecutor(max_workers=effective_workers) as executor:
            # Submit all tasks
            future_to_spec = {
                executor.submit(_execute_single_spec, work_item): work_item[0] for work_item in work_items
            }

            # Collect results as they complete
            for future in as_completed(future_to_spec):
                spec_path = future_to_spec[future]
                completed_count += 1

                try:
                    result = future.result()
                    results.append(result)

                    # Log progress
                    status = result.get("status", "unknown")
                    if status == "passed":
                        status_symbol = "✅"
                    elif status in ["failed", "timeout"]:
                        status_symbol = "❌"
                    elif status == "error":
                        status_symbol = "⚠️"
                    elif status == "skipped":
                        status_symbol = "⏭️"
                    else:
                        status_symbol = "❔"

                    spec_name = Path(spec_path).stem
                    print(f"[{completed_count}/{total_count}] {status_symbol} {spec_name} - {status}")

                except Exception as e:
                    # Handle execution failures gracefully
                    print(f"[{completed_count}/{total_count}] ❌ {Path(spec_path).stem} - execution error")
                    results.append(
                        {
                            "spec_path": str(spec_path),
                            "status": "error",
                            "error": f"Worker execution failed: {e!s}",
                            "start_time": datetime.now().isoformat(),
                            "end_time": datetime.now().isoformat(),
                        }
                    )

        print("")
        print(f"Parallel execution complete: {len(results)} specs processed")

        # Sort results by original order
        results_map = {r["spec_path"]: r for r in results}
        ordered_results = [results_map.get(str(sp), {}) for sp in spec_paths]

        return ordered_results

    def get_stats(self, results: List[Dict]) -> Dict:
        """
        Calculate statistics from test results

        Args:
            results: List of result dictionaries

        Returns:
            Statistics dictionary with counts and percentages
        """
        total = len(results)
        if total == 0:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "error": 0,
                "skipped": 0,
                "success_rate": 0.0,
            }

        # All backends now use standardized status values:
        # passed, failed, timeout, error, skipped
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") in ["failed", "timeout"])
        error = sum(1 for r in results if r.get("status") == "error")
        skipped = sum(1 for r in results if r.get("status") == "skipped")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": error,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0.0,
        }

    def print_summary(self, results: List[Dict]):
        """
        Print a summary of test results

        Args:
            results: List of result dictionaries
        """
        stats = self.get_stats(results)

        print("\n" + "=" * 80)
        print("PARALLEL EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total tests:    {stats['total']}")
        print(f"✅ Passed:      {stats['passed']}")
        print(f"❌ Failed:      {stats['failed']}")
        print(f"⚠️  Errors:      {stats['error']}")
        print(f"⏭️  Skipped:     {stats['skipped']}")
        print(f"Success rate:  {stats['success_rate']:.1f}%")
        print("=" * 80)

        # Show failed tests
        if stats["failed"] > 0 or stats["error"] > 0:
            print("\nFailed/Error tests:")
            for result in results:
                status = result.get("status")
                if status in ["failed", "timeout", "error"]:
                    spec_path = Path(result.get("spec_path", "unknown"))
                    error = result.get("error", "No error message")
                    status_display = "❌" if status in ["failed", "timeout"] else "⚠️"
                    print(f"  {status_display} {spec_path.stem}")
                    print(f"     Status: {status}")
                    print(f"     {error}")
