#!/usr/bin/env python3
"""Test spec finder functionality for CI smoke tests."""

import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.spec_finder import find_spec, search_specs


def main():
    """Run spec finder smoke tests."""
    print("Testing spec finder...")
    
    # Test finding a spec
    try:
        spec = find_spec('specs')
        if spec:
            print(f'✅ Found spec: {spec}')
        else:
            print('✅ Spec finder works (no specs found is OK)')
    except Exception as e:
        print(f'❌ Spec finder error: {e}')
        return 1
    
    # Test searching
    try:
        results = search_specs('docker', 'specs')
        print(f'✅ Search returned {len(results)} results')
    except Exception as e:
        print(f'❌ Search error: {e}')
        return 1
    
    print('✅ All spec finder tests passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
