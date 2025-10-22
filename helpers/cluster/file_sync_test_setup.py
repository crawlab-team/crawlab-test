#!/usr/bin/env python3
"""
CLS-003 Test Setup - Get or create test spider

Finds or creates a real spider for file sync testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
TESTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from helpers.libs.docker_utils import docker_utils
from helpers.libs.api_client import CrawlabAPIClient


def get_test_data_path():
    """Create a simple test directory with files for testing"""
    # Find master container
    containers = docker_utils.find_crawlab_containers()
    master = None
    for c in containers:
        if 'master' in c.get('Names', '').lower():
            master = c.get('Names') or c.get('ID')
            break
    
    if not master:
        raise RuntimeError("Master container not found")
    
    # Create test directory inside the container's actual crawlab workspace
    # Note: Python test runs on HOST but uses docker exec to create files INSIDE container
    # The gRPC server (running inside container) uses utils.GetWorkspace() 
    # which returns /root/crawlab_workspace by default
    test_spider_id = 'cls003-test'
    workspace_base = '/root/crawlab_workspace'  # Must match server's workspace path
    test_path = f'{workspace_base}/{test_spider_id}'
    
    # Create workspace and test files (increased to 1000 for stress testing)
    result = docker_utils.exec_command(
        master,
        f'''
        mkdir -p {test_path} && 
        for i in {{1..1000}}; do 
            echo "test file content $i" > {test_path}/test_file_$i.py
        done &&
        echo "1000"
        ''',
        timeout=30
    )
    
    if result['exit_code'] != 0:
        raise RuntimeError(f"Failed to create test workspace: {result.get('output')}")
    
    return {
        'spider_id': test_spider_id,
        'workspace_path': test_path,
        'workspace_base': workspace_base,
        'file_count': 1000
    }


if __name__ == "__main__":
    try:
        result = get_test_data_path()
        print(f"Spider ID: {result['spider_id']}")
        print(f"Path: {result['workspace_path']}")
        print(f"Files: {result['file_count']}")
        
        # Save for automation
        with open('/tmp/cls003_test_data.txt', 'w') as f:
            f.write(result['spider_id'])
        print(f"\nSaved to: /tmp/cls003_test_data.txt")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
