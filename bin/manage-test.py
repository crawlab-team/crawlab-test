#!/usr/bin/env python3
"""
Test Spec and Runner Management Tool

This script helps create and manage test specifications and their corresponding
runner scripts with proper formatting, numbering, and structure control.

Usage:
    # Create new test spec
    ./bin/manage-test.py create --category api --title "User Management" --priority high

    # Create spec with specific ID
    ./bin/manage-test.py create --category api --id 025 --title "Data Export"

    # List existing tests
    ./bin/manage-test.py list --category api

    # Find next available ID
    ./bin/manage-test.py next-id --category api

    # Validate spec format
    ./bin/manage-test.py validate specs/api/API-001-task-execution.md

    # Create runner from spec
    ./bin/manage-test.py create-runner specs/api/API-010-database.md
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Tuple


class TestManager:
    """Manages test specifications and runners."""

    # Category prefixes
    CATEGORY_PREFIXES: ClassVar[Dict[str, str]] = {
        "api": "API",
        "cluster": "CLS",
        "database": "DB",
        "integration": "INT",
        "performance": "PERF",
        "reliability": "REL",
        "system": "SYS",
        "ui": "UI",
    }

    # Priority levels
    PRIORITIES: ClassVar[List[str]] = ["critical", "high", "medium", "low"]

    # Complexity levels
    COMPLEXITIES: ClassVar[List[str]] = ["simple", "moderate", "complex"]

    # Backend types
    BACKENDS: ClassVar[List[str]] = ["script", "copilot", "playwright"]

    def __init__(self, root_dir: Optional[str] = None):
        """Initialize with repository root directory."""
        if root_dir:
            self.root = Path(root_dir)
        else:
            # Auto-detect: script is in bin/, root is parent
            self.root = Path(__file__).parent.parent

        self.specs_dir = self.root / "specs"
        self.runners_dir = self.root / "crawlab_test" / "runners"
        self.template_file = self.root / "SPEC_TEMPLATE.md"

    def get_category_prefix(self, category: str) -> str:
        """Get prefix for category (e.g., 'api' -> 'API')."""
        prefix = self.CATEGORY_PREFIXES.get(category.lower())
        if not prefix:
            raise ValueError(f"Unknown category: {category}. Valid: {', '.join(self.CATEGORY_PREFIXES.keys())}")
        return prefix

    def parse_test_id(self, filename: str) -> Optional[Tuple[str, int, str]]:
        """
        Parse test ID from filename.

        Returns: (prefix, number, title) or None
        Example: "API-001-task-execution.md" -> ("API", 1, "task-execution")
        """
        # Match pattern: PREFIX-NNN-title.md
        match = re.match(r"([A-Z]+)-(\d+)-(.+)\.md$", filename)
        if match:
            prefix, num, title = match.groups()
            return prefix, int(num), title
        return None

    def find_existing_tests(self, category: str) -> List[Tuple[int, str, Path]]:
        """
        Find all existing tests in a category.

        Returns: List of (number, title, path) tuples, sorted by number
        """
        prefix = self.get_category_prefix(category)
        category_dir = self.specs_dir / category

        if not category_dir.exists():
            return []

        tests = []
        for file in category_dir.glob("*.md"):
            if file.name == "README.md":
                continue

            parsed = self.parse_test_id(file.name)
            if parsed and parsed[0] == prefix:
                _, number, title = parsed
                tests.append((number, title, file))

        return sorted(tests, key=lambda x: x[0])

    def get_next_id(self, category: str) -> int:
        """Get next available ID number for category."""
        existing = self.find_existing_tests(category)
        if not existing:
            return 1

        # Find first gap, or use max + 1
        numbers = sorted([num for num, _, _ in existing])

        # Check for gaps
        for i, num in enumerate(numbers, start=1):
            if i != num:
                return i

        # No gaps, use next number
        return numbers[-1] + 1

    def format_test_id(self, category: str, number: int) -> str:
        """Format test ID (e.g., 'API-001')."""
        prefix = self.get_category_prefix(category)
        return f"{prefix}-{number:03d}"

    def format_filename(self, category: str, number: int, title: str) -> str:
        """Format test spec filename."""
        test_id = self.format_test_id(category, number)
        slug = self._slugify(title)
        return f"{test_id}-{slug}.md"

    def format_runner_filename(self, category: str, number: int, title: str) -> str:
        """Format runner script filename (e.g., API_001_title_slug.py)."""
        test_id = self.format_test_id(category, number).replace("-", "_")  # API-001 -> API_001
        slug = self._slugify(title).replace("-", "_")
        return f"{test_id}_{slug}.py"

    def _slugify(self, text: str) -> str:
        """Convert text to slug (lowercase, hyphens)."""
        # Remove special chars, convert to lowercase
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        # Replace spaces/underscores with hyphens
        slug = re.sub(r"[-\s_]+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        return slug

    def create_spec(
        self,
        category: str,
        title: str,
        number: Optional[int] = None,
        priority: str = "medium",
        complexity: str = "moderate",
        backend: str = "script",
        duration: str = "5-10 minutes",
    ) -> Path:
        """
        Create a new test specification file.

        Returns: Path to created spec file
        """
        # Validate inputs
        if priority not in self.PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}. Valid: {', '.join(self.PRIORITIES)}")

        if complexity not in self.COMPLEXITIES:
            raise ValueError(f"Invalid complexity: {complexity}. Valid: {', '.join(self.COMPLEXITIES)}")

        if backend not in self.BACKENDS:
            raise ValueError(f"Invalid backend: {backend}. Valid: {', '.join(self.BACKENDS)}")

        # Get or auto-assign number
        if number is None:
            number = self.get_next_id(category)
        else:
            # Check if number already exists
            existing = self.find_existing_tests(category)
            if any(num == number for num, _, _ in existing):
                raise ValueError(f"Test ID {self.format_test_id(category, number)} already exists")

        # Format names
        test_id = self.format_test_id(category, number)
        filename = self.format_filename(category, number, title)

        # Create directory if needed
        category_dir = self.specs_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Create spec file
        spec_path = category_dir / filename
        if spec_path.exists():
            raise FileExistsError(f"Spec already exists: {spec_path}")

        # Generate content
        content = self._generate_spec_content(
            test_id=test_id,
            title=title,
            category=category,
            priority=priority,
            complexity=complexity,
            backend=backend,
            duration=duration,
        )

        spec_path.write_text(content)
        print(f"✓ Created spec: {spec_path.relative_to(self.root)}")

        return spec_path

    def _generate_spec_content(
        self,
        test_id: str,
        title: str,
        category: str,
        priority: str,
        complexity: str,
        backend: str,
        duration: str,
    ) -> str:
        """Generate spec file content from template."""
        now = datetime.now().strftime("%Y-%m-%d")

        return f"""# {test_id} - {title}

## Metadata
- **Category**: {category}
- **Priority**: {priority}
- **Complexity**: {complexity}
- **Duration**: {duration}
- **Backend**: {backend}
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, MongoDB

## Scenario
[Brief description of what this test validates and why it's important]

## Prerequisites
- Crawlab API accessible at http://localhost:8080/api
- Master and at least one worker node running
- MongoDB accessible
- Valid admin credentials

## Test Steps

### Step 1: [Action Description]
**Method**: {backend}
**Command**:
```bash
# Command or code to execute
```

**Expected**: [What should happen]
**Validation**:
- [ ] Success criterion 1
- [ ] Success criterion 2

---

### Step 2: [Next Action]
**Method**: {backend}
**Expected**: [Expected outcome]
**Validation**: [How to verify]

---

## Success Criteria
- [ ] Overall criterion 1
- [ ] Overall criterion 2
- [ ] Test completes without errors

## Cleanup
- Clean up test data
- Remove temporary files
- Reset state

## Notes
- Additional context
- Known limitations
- Related tests

## History
- **Created**: {now}, Auto-generated
"""

    def create_runner(self, spec_path: Path) -> Path:
        """
        Create a runner script from a spec file.

        Returns: Path to created runner file
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        # Parse spec filename
        parsed = self.parse_test_id(spec_path.name)
        if not parsed:
            raise ValueError(f"Invalid spec filename: {spec_path.name}")

        prefix, number, title_slug = parsed

        # Find category from prefix
        category = None
        for cat, pre in self.CATEGORY_PREFIXES.items():
            if pre == prefix:
                category = cat
                break

        if not category:
            raise ValueError(f"Unknown prefix: {prefix}")

        # Format runner filename
        test_id = self.format_test_id(category, number)
        runner_filename = self.format_runner_filename(category, number, title_slug)

        # Create runner directory
        runner_dir = self.runners_dir / category
        runner_dir.mkdir(parents=True, exist_ok=True)

        runner_path = runner_dir / runner_filename
        if runner_path.exists():
            raise FileExistsError(f"Runner already exists: {runner_path}")

        # Read spec to extract title
        spec_content = spec_path.read_text()
        title_match = re.search(r"^# [A-Z]+-\d+ - (.+)$", spec_content, re.MULTILINE)
        title = title_match.group(1) if title_match else title_slug.replace("-", " ").title()

        # Generate runner content
        content = self._generate_runner_content(test_id, title, category)

        runner_path.write_text(content)
        runner_path.chmod(0o755)  # Make executable

        print(f"✓ Created runner: {runner_path.relative_to(self.root)}")

        return runner_path

    def _generate_runner_content(self, test_id: str, title: str, category: str) -> str:
        """Generate runner script content."""
        return f'''#!/usr/bin/env python3
"""
{test_id}: {title} Test Runner

[Description of what this test validates]
"""

import sys
import time

from crawlab_test.helpers.api import APIAssertions, AuthHelper, CleanupHelper


def print_step(step_num: int, description: str):
    """Print test step header."""
    print(f"\\n{{'='*80}}")
    print(f"Step {{step_num}}: {{description}}")
    print("=" * 80)


def main():
    """Run {title.lower()} test."""
    auth = AuthHelper()
    assertions = APIAssertions()
    cleanup = CleanupHelper()

    print("{test_id}: {title} Test")
    print("=" * 80)

    try:
        # Step 1: Authenticate
        print_step(1, "Authenticate")
        token, response = auth.login("admin", "admin")

        assertions.assert_success(response, "Login failed")
        print("✓ Authenticated successfully")

        # TODO: Add test steps here

        print("\\n" + "=" * 80)
        print("✓ All tests passed")
        print("=" * 80)

        return 0

    except AssertionError as e:
        print(f"\\n✗ Test failed: {{e}}")
        return 1

    except Exception as e:
        print(f"\\n✗ Error: {{e}}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        print("\\nCleaning up...")
        cleanup.cleanup_all(token)


if __name__ == "__main__":
    sys.exit(main())
'''

    def list_tests(self, category: Optional[str] = None) -> Dict[str, List[Tuple[int, str, Path]]]:
        """List all tests, optionally filtered by category."""
        if category:
            categories = [category]
        else:
            categories = list(self.CATEGORY_PREFIXES.keys())

        results = {}
        for cat in categories:
            tests = self.find_existing_tests(cat)
            if tests:
                results[cat] = tests

        return results

    def validate_spec(self, spec_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a spec file format.

        Returns: (is_valid, list of issues)
        """
        if not spec_path.exists():
            return False, [f"File not found: {spec_path}"]

        content = spec_path.read_text()
        issues = []

        # Check filename format
        if not self.parse_test_id(spec_path.name):
            issues.append(f"Invalid filename format: {spec_path.name}")

        # Check required sections
        required_sections = [
            "## Metadata",
            "## Scenario",
            "## Prerequisites",
            "## Test Steps",
            "## Success Criteria",
            "## Cleanup",
        ]

        for section in required_sections:
            if section not in content:
                issues.append(f"Missing required section: {section}")

        # Check metadata fields
        metadata_fields = [
            "**Category**:",
            "**Priority**:",
            "**Complexity**:",
            "**Duration**:",
        ]

        for field in metadata_fields:
            if f"- {field}" not in content:
                issues.append(f"Missing metadata field: {field}")

        # Check title format
        if not re.search(r"^# [A-Z]+-\d+ - .+$", content, re.MULTILINE):
            issues.append("Invalid title format (should be: # PREFIX-NNN - Title)")

        return len(issues) == 0, issues

    def print_test_list(self, tests: Dict[str, List[Tuple[int, str, Path]]]):
        """Pretty print test list."""
        if not tests:
            print("No tests found.")
            return

        for category in sorted(tests.keys()):
            prefix = self.get_category_prefix(category)
            print(f"\n{category.upper()} Tests ({prefix}-XXX):")
            print("-" * 80)

            for number, title, _path in tests[category]:
                test_id = self.format_test_id(category, number)
                # Check if runner exists (runner format: API_001_title_slug.py)
                runner_slug = title.replace("-", "_")
                runner_id = test_id.replace("-", "_")  # API-001 -> API_001
                runner_file = self.runners_dir / category / f"{runner_id}_{runner_slug}.py"
                runner_status = "✓" if runner_file.exists() else "✗"

                print(f"  {test_id}: {title:<50} [Runner: {runner_status}]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage test specifications and runners",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create new test spec")
    create_parser.add_argument("--category", required=True, choices=list(TestManager.CATEGORY_PREFIXES.keys()))
    create_parser.add_argument("--title", required=True, help="Test title")
    create_parser.add_argument("--id", type=int, help="Specific test number (auto-assigned if not provided)")
    create_parser.add_argument("--priority", default="medium", choices=TestManager.PRIORITIES)
    create_parser.add_argument("--complexity", default="moderate", choices=TestManager.COMPLEXITIES)
    create_parser.add_argument("--backend", default="script", choices=TestManager.BACKENDS)
    create_parser.add_argument("--duration", default="5-10 minutes")
    create_parser.add_argument("--with-runner", action="store_true", help="Also create runner script")

    # List command
    list_parser = subparsers.add_parser("list", help="List existing tests")
    list_parser.add_argument("--category", choices=list(TestManager.CATEGORY_PREFIXES.keys()))

    # Next ID command
    next_id_parser = subparsers.add_parser("next-id", help="Get next available ID")
    next_id_parser.add_argument("--category", required=True, choices=list(TestManager.CATEGORY_PREFIXES.keys()))

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate spec format")
    validate_parser.add_argument("spec_file", type=Path, help="Path to spec file")

    # Create runner command
    runner_parser = subparsers.add_parser("create-runner", help="Create runner from spec")
    runner_parser.add_argument("spec_file", type=Path, help="Path to spec file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize manager
    manager = TestManager()

    try:
        if args.command == "create":
            spec_path = manager.create_spec(
                category=args.category,
                title=args.title,
                number=args.id,
                priority=args.priority,
                complexity=args.complexity,
                backend=args.backend,
                duration=args.duration,
            )

            if args.with_runner:
                manager.create_runner(spec_path)

        elif args.command == "list":
            tests = manager.list_tests(args.category)
            manager.print_test_list(tests)

        elif args.command == "next-id":
            next_num = manager.get_next_id(args.category)
            test_id = manager.format_test_id(args.category, next_num)
            print(f"Next available ID: {test_id}")

        elif args.command == "validate":
            is_valid, issues = manager.validate_spec(args.spec_file)

            if is_valid:
                print(f"✓ Valid spec: {args.spec_file}")
                return 0
            else:
                print(f"✗ Invalid spec: {args.spec_file}")
                for issue in issues:
                    print(f"  - {issue}")
                return 1

        elif args.command == "create-runner":
            manager.create_runner(args.spec_file)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
