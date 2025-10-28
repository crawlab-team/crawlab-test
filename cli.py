#!/usr/bin/env python3
"""
Unified Test Runner CLI - Entry Point

This is a thin wrapper that imports and executes the main CLI from the crawlab_test package.
The actual CLI implementation is in crawlab_test.cli module.

Usage:
    ./cli.py --spec UI-001
    ./cli.py --spec "spider management"
    ./cli.py --list-specs
    ./cli.py --search docker
"""

from crawlab_test.cli import main

if __name__ == "__main__":
    main()
