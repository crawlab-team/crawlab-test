#!/usr/bin/env python3
"""Test spec finder functionality for CI smoke tests."""

import sys

from crawlab_test.core.spec_finder import SpecFinder


def main():
    """Run spec finder smoke tests."""
    print("Testing spec finder...")

    # Initialize SpecFinder
    try:
        finder = SpecFinder()
        print("✅ SpecFinder initialized")
    except Exception as e:
        print(f"❌ SpecFinder initialization error: {e}")
        return 1

    # Test listing specs
    try:
        specs = finder.list_specs()
        print(f"✅ Listed {len(specs)} spec(s)")
    except Exception as e:
        print(f"❌ List specs error: {e}")
        return 1

    # Test searching
    try:
        results = finder.find_spec_by_query("docker")
        print(f"✅ Search returned {len(results)} result(s)")
    except Exception as e:
        print(f"❌ Search error: {e}")
        return 1

    print("✅ All spec finder tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
