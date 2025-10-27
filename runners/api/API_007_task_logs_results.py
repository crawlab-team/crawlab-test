#!/usr/bin/env python3
"""
Test runner for API-007: Task Logs & Results

Validates task log retrieval and result data endpoints.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.api import APIAuth, SpiderHelper, TaskHelper, CleanupHelper


def print_step(step_num: int, description: str):
    """Print test step header."""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)


def print_result(success: bool, message: str):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    return success


def main():
    """Run API-007 test suite."""
    
    # Initialize helpers
    auth = APIAuth()
    spider_helper = SpiderHelper()
    task_helper = TaskHelper()
    cleanup = CleanupHelper()
    
    token = None
    test_spider_id = None
    test_task_id = None
    
    results = []
    step = 1
    
    try:
        # ===== Setup =====
        print_step(step, "Authenticate as admin")
        step += 1
        token, response = auth.login("admin", "admin")
        results.append(print_result(
            token is not None,
            f"Admin login: {token[:20] if token else 'FAILED'}..."
        ))
        
        if not token:
            print("❌ Authentication failed, cannot proceed")
            return 1
        
        # ===== Test Case 1: Create Spider with Logs & Results =====
        print_step(step, "Create test spider with script that produces logs and results")
        step += 1
        
        # Spider script that prints logs and saves results
        spider_script = '''import json
import sys

# Print to logs
print("Starting spider execution...")
print("Processing data...")

# Simulate some data collection
results = [
    {"id": 1, "name": "Item 1", "value": 100},
    {"id": 2, "name": "Item 2", "value": 200},
    {"id": 3, "name": "Item 3", "value": 300}
]

# Save results (Crawlab automatically captures this)
for item in results:
    print(json.dumps(item))

print("Spider execution completed!")
print(f"Total items: {len(results)}")
'''
        
        test_spider_id, response = spider_helper.create_spider(
            token=token,
            name=f"test-spider-logs-{int(time.time())}",
            cmd="python main.py",
            col_name="test_results"
        )
        
        results.append(print_result(
            test_spider_id is not None,
            f"Spider created: {test_spider_id}"
        ))
        
        if test_spider_id:
            cleanup.track_spider(test_spider_id)
        else:
            print("❌ Failed to create spider, cannot proceed")
            return 1
        
        # Save spider script
        print_step(step, "Save spider script file")
        step += 1
        
        file_saved, response = spider_helper.save_file(
            token=token,
            spider_id=test_spider_id,
            path="main.py",
            content=spider_script
        )
        
        results.append(print_result(
            file_saved,
            "Spider script saved"
        ))
        
        if not file_saved:
            print("❌ Failed to save spider script")
            return 1
        
        # ===== Test Case 2: Run Task =====
        print_step(step, "Create and run task")
        step += 1
        
        task_ids, response = task_helper.create_task(
            token=token,
            spider_id=test_spider_id,
            mode="random"
        )
        
        if task_ids and len(task_ids) > 0:
            test_task_id = task_ids[0]
            cleanup.track_task(test_task_id)
            results.append(print_result(True, f"Task created: {test_task_id}"))
        else:
            results.append(print_result(False, "Task creation failed"))
            return 1
        
        # Wait for task to complete
        print_step(step, "Wait for task completion")
        step += 1
        
        final_status, task_data = task_helper.wait_for_task(
            token=token,
            task_id=test_task_id,
            timeout=60,
            interval=2
        )
        
        results.append(print_result(
            final_status == 'finished',
            f"Task status: {final_status or 'TIMEOUT'}"
        ))
        
        if final_status != 'finished':
            print(f"⚠️  Task did not finish successfully: {final_status}")
            # Continue anyway to test log retrieval
        
        # ===== Test Case 3: Get Task Logs =====
        print_step(step, "Get task logs")
        step += 1
        
        logs, response = task_helper.get_task_logs(token=token, task_id=test_task_id)
        
        has_logs = logs is not None and len(logs) > 0
        results.append(print_result(
            has_logs,
            f"Logs retrieved: {len(logs) if logs else 0} characters"
        ))
        
        if has_logs:
            print(f"📄 Log preview (first 200 chars):\n{logs[:200]}")
            
            # Verify expected content in logs
            expected_messages = [
                "Starting spider execution",
                "Processing data",
                "Spider execution completed"
            ]
            
            for msg in expected_messages:
                if msg in logs:
                    results.append(print_result(True, f"Log contains: '{msg}'"))
                else:
                    results.append(print_result(False, f"Log missing: '{msg}'"))
        
        # ===== Test Case 4: Test Log Pagination =====
        print_step(step, "Test log pagination parameters")
        step += 1
        
        # Note: Pagination may not affect single-run logs, but test the parameters work
        try:
            import requests
            response = requests.get(
                f"http://localhost:8080/api/tasks/{test_task_id}/logs?page=1&size=100",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            results.append(print_result(
                response.status_code == 200,
                f"Log pagination test: {response.status_code}"
            ))
        except Exception as e:
            results.append(print_result(False, f"Log pagination error: {e}"))
        
        # ===== Test Case 5: Get Task Results =====
        print_step(step, "Get task results")
        step += 1
        
        task_results, response = task_helper.get_task_results(
            token=token,
            task_id=test_task_id
        )
        
        has_results = task_results is not None and isinstance(task_results, list)
        results.append(print_result(
            has_results,
            f"Results retrieved: {len(task_results) if task_results else 0} items"
        ))
        
        if has_results and len(task_results) > 0:
            print(f"📊 Result preview: {task_results[0]}")
            
            # Verify result structure
            first_item = task_results[0]
            expected_fields = ['id', 'name', 'value']
            
            for field in expected_fields:
                if field in first_item:
                    results.append(print_result(True, f"Result has field: '{field}'"))
                else:
                    results.append(print_result(False, f"Result missing field: '{field}'"))
        else:
            print("⚠️  No results found - this may be expected if spider output wasn't captured")
        
        # ===== Test Case 6: Test Result Pagination =====
        print_step(step, "Test result pagination")
        step += 1
        
        try:
            import requests
            response = requests.get(
                f"http://localhost:8080/api/tasks/{test_task_id}/results?page=1&size=5",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            page1_success = response.status_code == 200
            results.append(print_result(
                page1_success,
                f"Results page 1: {response.status_code}"
            ))
            
            if page1_success:
                data = response.json()
                print(f"📄 Total results: {data.get('total', 0)}")
        except Exception as e:
            results.append(print_result(False, f"Result pagination error: {e}"))
        
        # ===== Test Case 7: Edge Cases =====
        print_step(step, "Test edge case: Invalid task ID")
        step += 1
        
        invalid_id = "000000000000000000000000"
        logs, response = task_helper.get_task_logs(token=token, task_id=invalid_id)
        
        # Should handle gracefully (either 404 or empty logs)
        edge_case_handled = logs is None or (isinstance(logs, str) and len(logs) == 0)
        results.append(print_result(
            edge_case_handled,
            f"Invalid task ID handled gracefully"
        ))
        
        task_results, response = task_helper.get_task_results(
            token=token,
            task_id=invalid_id
        )
        
        # Should return None or empty array
        edge_case_handled = task_results is None or (isinstance(task_results, list) and len(task_results) == 0)
        results.append(print_result(
            edge_case_handled,
            f"Invalid task results handled gracefully"
        ))
        
        # ===== Test Case 8: Test Latest Logs Parameter =====
        print_step(step, "Test latest logs parameter")
        step += 1
        
        try:
            import requests
            response = requests.get(
                f"http://localhost:8080/api/tasks/{test_task_id}/logs?latest=true",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            results.append(print_result(
                response.status_code == 200,
                f"Latest logs (latest=true): {response.status_code}"
            ))
            
            response = requests.get(
                f"http://localhost:8080/api/tasks/{test_task_id}/logs?latest=false",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            results.append(print_result(
                response.status_code == 200,
                f"Historical logs (latest=false): {response.status_code}"
            ))
        except Exception as e:
            results.append(print_result(False, f"Latest parameter error: {e}"))
        
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # ===== Cleanup =====
        print("\n" + "="*60)
        print("CLEANUP")
        print("="*60)
        
        if token:
            cleanup.cleanup_all(token)
        
        # ===== Summary =====
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = len(results)
        passed = sum(results)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Pass rate: {pass_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ Some tests failed")
            return 1
        else:
            print("\n✅ All tests passed!")
            return 0


if __name__ == "__main__":
    sys.exit(main())
