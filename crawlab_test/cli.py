#!/usr/bin/env python3
"""
Unified Test Runner CLI

Main entry point for executing Crawlab test specifications.
Supports multiple backends: script, copilot, and playwright.

Usage:
    ./cli.py --spec UI-001
    ./cli.py --spec "spider management"
    ./cli.py --list-specs
    ./cli.py --search docker
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from .backends import CopilotBackend, PlaywrightBackend, ScriptBackend
from .core import Config, DockerDetector, ParallelTestExecutor, ResultHandler, SpecFinder


def get_base_dir() -> Path:
    """
    Get the base directory for the test framework.

    Checks in order:
    1. Current working directory (for development/repo use)
    2. Package directory (for bundled specs in pip install)
    """
    # First, check if current working directory has specs/ directory
    # This handles development mode and running from repo root
    cwd = Path.cwd()
    if (cwd / "specs").exists():
        return cwd

    # Check package location for bundled specs
    # When installed via pip, specs/ is bundled into crawlab_test/specs/
    package_dir = Path(__file__).parent
    if (package_dir / "specs").exists():
        return package_dir

    # Fall back to CWD if neither location has specs
    return cwd


def select_backend(spec_path: Path, backend_arg: str, config: Config, docker_detector: DockerDetector):
    """
    Select appropriate backend for test execution

    Args:
        spec_path: Path to test specification
        backend_arg: Backend argument from CLI (auto, script, copilot, playwright)
        config: Configuration object
        docker_detector: Docker detector object

    Returns:
        TestBackend instance
    """
    base_dir = get_base_dir()

    # If user specified a backend explicitly, use it
    if backend_arg != "auto":
        if backend_arg == "script":
            return ScriptBackend(base_dir)
        elif backend_arg == "copilot":
            return CopilotBackend(base_dir)
        elif backend_arg == "playwright":
            return PlaywrightBackend(base_dir)
        else:
            print(f"Error: Unknown backend '{backend_arg}'")
            sys.exit(1)

    # Auto-detect based on spec and environment

    # Get category from spec path
    category = None
    try:
        parts = spec_path.parts
        specs_index = parts.index("specs")
        if specs_index + 1 < len(parts):
            category = parts[specs_index + 1]
    except (ValueError, IndexError):
        pass

    # For UI tests, prefer Copilot backend if available (more flexible and autonomous)
    if category == "ui":
        copilot_backend = CopilotBackend()
        if copilot_backend.check_prerequisites():
            print("Auto-selected backend: copilot (preferred for UI tests)")
            return copilot_backend

    # 1. Check for script backend (runner scripts)
    script_backend = ScriptBackend()
    if script_backend.supports_spec(spec_path):
        print("Auto-selected backend: script")
        return script_backend

    # 2. Check for UI/Playwright specs
    playwright_backend = PlaywrightBackend()
    if playwright_backend.supports_spec(spec_path) and playwright_backend.check_prerequisites():
        print("Auto-selected backend: playwright")
        return playwright_backend

    # 3. Default to Copilot if available
    copilot_backend = CopilotBackend()
    if copilot_backend.check_prerequisites():
        print("Auto-selected backend: copilot")
        return copilot_backend

    # 4. Fail if no backend available
    print("Error: No suitable backend found for this test")
    print("Consider:")
    print("  - Adding a runner script in runners/")
    print("  - Installing Copilot CLI: npm install -g @github/copilot")
    print("  - Specifying a backend explicitly: --backend script")
    sys.exit(1)


def list_specs_command(args):
    """Handle --list-specs command"""
    spec_finder = SpecFinder(get_base_dir())
    specs = spec_finder.list_specs(categories=args.category)

    if not specs:
        if args.category:
            print(f"No specifications found for categories: {', '.join(args.category)}")
        else:
            print("No specifications found")
        return

    # Show filter info if categories specified
    if args.category:
        print(f"\nFiltered by categories: {', '.join(args.category)}")

    print(f"\nAvailable Test Specifications ({len(specs)}):")
    print("=" * 80)

    current_category = None
    for spec in specs:
        if spec["category"] != current_category:
            current_category = spec["category"]
            print(f"\n{current_category.upper()}:")

        spec_id = spec.get("id", "N/A")
        title = spec["title"]
        priority = spec.get("priority", "unknown")
        duration = spec.get("duration", "unknown")

        print(f"  [{spec_id}] {title}")
        print(f"      Priority: {priority}, Duration: {duration}")
        print(f"      File: {spec['file']}")


def search_specs_command(args):
    """Handle --search command"""
    spec_finder = SpecFinder(get_base_dir())
    specs = spec_finder.find_spec_by_query(args.search)

    if not specs:
        print(f"No specifications found matching: {args.search}")
        return

    print(f"\nSearch Results for '{args.search}' ({len(specs)}):")
    print("=" * 80)

    for i, spec in enumerate(specs[:10], 1):
        spec_id = spec.get("id", "N/A")
        title = spec["title"]
        category = spec["category"]

        print(f"{i}. [{spec_id}] {title}")
        print(f"   Category: {category}, File: {spec['file']}")

    if len(specs) > 10:
        print(f"\n... and {len(specs) - 10} more matches")


def run_parallel_command(args):
    """Handle running all specs in a category with parallel execution"""
    base_dir = get_base_dir()

    # Initialize core modules
    spec_finder = SpecFinder(get_base_dir())
    config = Config(base_dir)
    docker_detector = DockerDetector()
    result_handler = ResultHandler(base_dir)

    # Detect environment
    is_docker = docker_detector.is_docker_environment()
    if is_docker:
        result_handler.log_info("✓ Docker environment detected")
    else:
        result_handler.log_info("Local environment detected")

    # Get category
    if not args.category or len(args.category) != 1:
        result_handler.log_error("--parallel requires exactly one category")
        print("Usage: ./cli.py --category api --parallel [N]")
        sys.exit(1)

    category = args.category[0]

    # Find all specs in category
    all_specs = spec_finder.list_specs(categories=[category])

    if not all_specs:
        result_handler.log_error(f"No specs found for category: {category}")
        sys.exit(1)

    result_handler.log_info(f"Found {len(all_specs)} specs in category '{category}'")

    # Convert to paths
    spec_paths = [base_dir / spec["file"] for spec in all_specs]

    # Determine worker count
    if args.parallel and args.parallel > 0:
        max_workers = args.parallel
    else:
        # Auto-detect based on category (when --parallel used without number)
        worker_defaults = {
            "api": 5,  # 15 tests, I/O bound (HTTP requests) - SAFE for parallel
            "ui": 4,  # 19 tests, CPU/memory intensive (browsers) - SAFE for parallel
            "cluster": 1,  # 4 tests, Docker manipulation - UNSAFE, must be sequential
            "database": 2,  # 1 test, but can be parallelized if more added
            "dependencies": 2,
            "scheduler": 3,  # Task execution tests - generally safe
            "system": 2,
        }
        max_workers = worker_defaults.get(category, 3)

    result_handler.log_info(f"Using {max_workers} parallel workers")

    # Build configuration
    test_config = {
        "timeout_minutes": args.timeout or config.get_timeout_for_category(category),
        "retry_count": args.retry or config.get_retry_count_for_category(category),
        "is_ci": args.ci or config.is_ci,
        "category": category,
        "docker_environment": is_docker,
        "backend": args.backend,
        "model": args.model,
    }

    # Execute in parallel
    executor = ParallelTestExecutor(base_dir, max_workers=max_workers)
    results = executor.execute_specs(spec_paths, test_config)

    # Print summary
    executor.print_summary(results)

    # Save results and generate summaries
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)

    for i, result in enumerate(results):
        result["category"] = category
        result["docker_info"] = docker_detector.get_docker_info() if is_docker else None

        # Generate unique timestamp for each result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{i:03d}"

        # Save result JSON
        result_handler.save_result(result, timestamp)

        # Generate summary markdown for CI workflow to display
        spec_path = Path(result.get("spec_path", "unknown"))
        result_handler.generate_summary(result, spec_path, category, timestamp)

    # Calculate overall status
    stats = executor.get_stats(results)

    # Write tracking files for CI workflow (same format as per-spec tracking)
    (results_dir / ".total_tests").write_text(str(stats["total"]))
    (results_dir / ".passed_tests").write_text(str(stats["passed"]))
    (results_dir / ".failed_tests").write_text(str(stats["failed"] + stats["error"]))

    # Write detailed test results in workflow-compatible format
    test_results_list = []
    for result in results:
        spec_path = Path(result.get("spec_path", "unknown"))
        # Extract spec ID from filename (e.g., "API-001-authentication.md" -> "API-001")
        spec_filename = spec_path.stem  # Remove .md extension
        # Match pattern: CATEGORY-NUMBER (e.g., API-001, UI-002, CLS-001)
        match = re.match(r"^([A-Z]+-\d+)", spec_filename)
        spec_id = match.group(1) if match else spec_filename

        status = result.get("status", "unknown")

        # Calculate duration if available
        duration = "N/A"
        if "start_time" in result and "end_time" in result:
            try:
                start = datetime.fromisoformat(result["start_time"])
                end = datetime.fromisoformat(result["end_time"])
                duration_sec = (end - start).total_seconds()
                duration = f"{duration_sec:.2f}s"
            except (ValueError, TypeError):
                pass

        # Map status to display format
        status_map = {
            "passed": "✅ PASSED",
            "failed": "❌ FAILED",
            "timeout": "⏱️ TIMEOUT",
            "error": "⚠️ ERROR",
            "skipped": "⏭️ SKIPPED",
            "unknown": "❔ UNKNOWN",
        }
        status_display = status_map.get(status, f"❔ {status.upper()}")

        test_results_list.append({"spec": spec_id, "status": status_display, "duration": duration})

    (results_dir / ".test_results.json").write_text(json.dumps(test_results_list, indent=2))

    if stats["failed"] > 0 or stats["error"] > 0:
        result_handler.log_error(f"✗ {stats['failed'] + stats['error']} tests FAILED")
        sys.exit(1)
    else:
        result_handler.log_info(f"✓ All {stats['passed']} tests PASSED")
        sys.exit(0)


def run_spec_command(args):
    """Handle test execution"""
    base_dir = get_base_dir()

    # Initialize core modules
    spec_finder = SpecFinder(get_base_dir())
    config = Config(base_dir)
    docker_detector = DockerDetector()
    result_handler = ResultHandler(base_dir)

    # Detect environment
    is_docker = docker_detector.is_docker_environment()
    if is_docker:
        result_handler.log_info("✓ Docker environment detected")
    else:
        result_handler.log_info("Local environment detected")

    # Find spec
    spec_path = None

    # Try as direct path first
    if Path(args.spec).exists():
        spec_path = Path(args.spec)
    elif (base_dir / args.spec).exists():
        spec_path = base_dir / args.spec
    else:
        # Try spec finder
        matching_specs = spec_finder.find_spec_by_query(args.spec)

        if not matching_specs:
            result_handler.log_error(f"No specifications found matching: {args.spec}")
            sys.exit(1)

        if len(matching_specs) > 1:
            result_handler.log_warning(f"Multiple specs found for '{args.spec}':")
            for i, spec in enumerate(matching_specs[:5], 1):
                spec_id = spec.get("id", "N/A")
                print(f"  {i}. [{spec_id}] {spec['title']} ({spec['file']})")

            if len(matching_specs) > 5:
                print(f"  ... and {len(matching_specs) - 5} more")

        # Use best match
        spec_path = base_dir / matching_specs[0]["file"]
        spec_id = matching_specs[0].get("id", "N/A")
        result_handler.log_info(f"Found spec [{spec_id}]: {spec_path}")

    # Get category
    try:
        parts = spec_path.parts
        specs_index = parts.index("specs")
        category = parts[specs_index + 1] if specs_index + 1 < len(parts) else spec_path.parent.name
    except (ValueError, IndexError):
        category = spec_path.parent.name

    # Dry run mode
    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print(f"Spec: {spec_path}")
        print(f"Category: {category}")
        print(f"Backend: {args.backend}")
        print(f"Docker: {is_docker}")
        print("\nWould execute test here")
        return

    # Build configuration
    test_config = {
        "timeout_minutes": args.timeout or config.get_timeout_for_category(category),
        "retry_count": args.retry or config.get_retry_count_for_category(category),
        "is_ci": args.ci or config.is_ci,
        "category": category,
        "docker_environment": is_docker,
        "model": args.model,
    }

    # Select backend
    backend = select_backend(spec_path, args.backend, config, docker_detector)

    # Check prerequisites
    if not backend.check_prerequisites():
        result_handler.log_error(f"Backend '{backend.get_name()}' prerequisites not met")
        sys.exit(1)

    result_handler.log_info(f"Using backend: {backend.get_name()}")
    result_handler.log_info(f"Executing spec: {spec_path}")

    # Execute test
    result = backend.execute(spec_path, test_config)

    # Add metadata
    result["category"] = category
    result["docker_info"] = docker_detector.get_docker_info() if is_docker else None

    # Save result
    result_handler.save_result(result)

    # Generate summary if not CI
    if not config.is_ci:
        result_handler.generate_summary(result, spec_path, category)

    # Write GitHub Actions summary if in CI
    if config.is_github_actions:
        result_handler.write_github_actions_summary(result, spec_path, category)

    # Determine exit code
    status = result.get("status", "unknown")
    exit_code = result.get("exit_code", 1)

    if status == "passed" or exit_code == 0:
        result_handler.log_info("✓ Test PASSED")
        sys.exit(0)
    elif status == "skipped":
        result_handler.log_warning("⚠ Test SKIPPED")
        sys.exit(0)
    else:
        result_handler.log_error("✗ Test FAILED")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Crawlab Unified Test Runner",
        epilog="""
Examples:
  # Run by spec ID
  %(prog)s --spec UI-001

  # Run by fuzzy search
  %(prog)s --spec "spider management"

  # Run with specific backend
  %(prog)s --spec UI-001 --backend copilot

  # Run with specific model (Copilot backend)
  %(prog)s --spec UI-001 --backend copilot --model gpt-4o
  %(prog)s --spec UI-001 --backend copilot --model claude-3.5-sonnet
  %(prog)s --spec UI-001 --backend copilot --model o1-preview

  # Search for specs
  %(prog)s --search docker

  # List all specs
  %(prog)s --list-specs

  # List specs by category
  %(prog)s --list-specs --category ui

  # List specs for multiple categories
  %(prog)s --list-specs --category api ui cluster

  # Run all specs in a category in parallel (auto-detect workers)
  %(prog)s --category api --parallel

  # Run all specs in a category with specific worker count
  %(prog)s --category api --parallel 4

  # Run all UI tests with 2 parallel workers
  %(prog)s --category ui --parallel 2
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Main arguments
    parser.add_argument("--spec", help="Specification to run (ID, search query, or path)")

    parser.add_argument(
        "--backend",
        choices=["auto", "script", "copilot", "playwright"],
        default="auto",
        help="Backend to use for test execution (default: auto)",
    )

    parser.add_argument("--list-specs", action="store_true", help="List all available test specifications")

    parser.add_argument("--search", help="Search for specifications by keywords")

    parser.add_argument(
        "--category",
        nargs="+",
        help="Filter specs by category (use with --list-specs or --parallel). Can specify multiple: --category api ui cluster",
    )

    parser.add_argument(
        "--parallel",
        type=int,
        metavar="N",
        nargs="?",
        const=0,
        help="Run all specs in specified category in parallel with N workers. If N is omitted, auto-detect optimal workers. Requires --category with single value.",
    )

    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without actually running")

    parser.add_argument("--ci", action="store_true", help="Run in CI mode")

    parser.add_argument("--timeout", type=int, help="Test timeout in minutes")

    parser.add_argument("--retry", type=int, help="Number of retry attempts")

    parser.add_argument(
        "--model", help="Model to use for Copilot backend (e.g., gpt-4, gpt-4o, claude-3.5-sonnet, o1-preview)"
    )

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Handle commands
    if args.list_specs:
        list_specs_command(args)
    elif args.search:
        search_specs_command(args)
    elif args.parallel is not None:
        run_parallel_command(args)
    elif args.spec:
        run_spec_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
