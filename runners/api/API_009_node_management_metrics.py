#!/usr/bin/env python3
"""
Test runner for API-009: Node Management & Metrics

Validates node listing, details, updates, and metrics endpoints.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.api import APIAuth, NodeHelper


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
    """Run API-009 test suite."""
    
    # Initialize helpers
    auth = APIAuth()
    node_helper = NodeHelper()
    
    token = None
    master_node_id = None
    original_description = None
    
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
        
        # ===== Test Case 1: List Nodes =====
        print_step(step, "List all nodes")
        step += 1
        
        nodes, response = node_helper.list_nodes(token)
        
        has_nodes = nodes is not None and isinstance(nodes, list) and len(nodes) > 0
        results.append(print_result(
            has_nodes,
            f"Nodes listed: {len(nodes) if nodes else 0} found"
        ))
        
        if not has_nodes:
            print("❌ No nodes found, cannot proceed with tests")
            return 1
        
        # Check for master node
        print_step(step, "Check master node")
        step += 1
        
        master_nodes = [n for n in nodes if n.get('is_master')]
        
        results.append(print_result(
            len(master_nodes) > 0,
            f"Master node(s) found: {len(master_nodes)}"
        ))
        
        if master_nodes:
            master_node = master_nodes[0]
            master_node_id = master_node.get('_id')
            
            print(f"📋 Master Node: {master_node.get('name')} ({master_node_id})")
            
            required_fields = ['_id', 'name', 'hostname', 'ip', 'status', 'enabled']
            for field in required_fields:
                has_field = field in master_node
                results.append(print_result(
                    has_field,
                    f"Master node has '{field}': {master_node.get(field) if has_field else 'MISSING'}"
                ))
        else:
            print("❌ No master node found, some tests will be skipped")
        
        # Test pagination
        print_step(step, "Test pagination")
        step += 1
        
        nodes_page1, response = node_helper.list_nodes(token, page=1, size=5)
        
        results.append(print_result(
            nodes_page1 is not None,
            f"Pagination works: {len(nodes_page1) if nodes_page1 else 0} items"
        ))
        
        # Test filtering
        print_step(step, "Filter nodes by is_master")
        step += 1
        
        master_filter, response = node_helper.list_nodes(
            token, 
            filter_dict={"is_master": True}
        )
        
        if master_filter is not None:
            all_master = all(n.get('is_master') for n in master_filter)
            results.append(print_result(
                all_master,
                f"Master filter works: {len(master_filter)} master node(s)"
            ))
        else:
            results.append(print_result(False, "Master filter failed"))
        
        # ===== Test Case 2: Get Node Details =====
        if master_node_id:
            print_step(step, "Get master node details")
            step += 1
            
            node_details, response = node_helper.get_node(token, master_node_id)
            
            if node_details:
                results.append(print_result(True, "Node details retrieved"))
                
                # Verify detailed fields
                detail_fields = {
                    'name': node_details.get('name'),
                    'hostname': node_details.get('hostname'),
                    'ip': node_details.get('ip'),
                    'status': node_details.get('status'),
                    'enabled': node_details.get('enabled'),
                    'is_master': node_details.get('is_master')
                }
                
                print(f"📊 Node Details:")
                for field, value in detail_fields.items():
                    print(f"  - {field}: {value}")
                    results.append(print_result(
                        value is not None,
                        f"Node has {field}"
                    ))
                
                original_description = node_details.get('description', '')
            else:
                results.append(print_result(False, "Failed to get node details"))
        
        # ===== Test Case 3: Update Node =====
        if master_node_id:
            print_step(step, "Update node description")
            step += 1
            
            updated_node, response = node_helper.update_node(
                token=token,
                node_id=master_node_id,
                updates={"description": "Updated test description"}
            )
            
            if updated_node:
                results.append(print_result(True, "Node description updated"))
                results.append(print_result(
                    updated_node.get('description') == "Updated test description",
                    f"Description verified: {updated_node.get('description')}"
                ))
            else:
                results.append(print_result(False, "Update failed"))
            
            print_step(step, "Update max_runners")
            step += 1
            
            updated_node, response = node_helper.update_node(
                token=token,
                node_id=master_node_id,
                updates={"max_runners": 10}
            )
            
            if updated_node:
                results.append(print_result(True, "Max runners updated"))
                results.append(print_result(
                    updated_node.get('max_runners') == 10,
                    f"Max runners verified: {updated_node.get('max_runners')}"
                ))
            else:
                results.append(print_result(False, "Update failed"))
            
            # Restore original description
            if original_description is not None:
                node_helper.update_node(
                    token=token,
                    node_id=master_node_id,
                    updates={"description": original_description}
                )
        
        # ===== Test Case 4: Node Metrics - All Nodes =====
        print_step(step, "Get metrics for all nodes")
        step += 1
        
        all_metrics, response = node_helper.get_node_metrics(token)
        
        has_metrics = all_metrics is not None and isinstance(all_metrics, dict)
        results.append(print_result(
            has_metrics,
            f"All node metrics: {len(all_metrics) if has_metrics else 0} nodes"
        ))
        
        if has_metrics and master_node_id:
            has_master_metrics = master_node_id in all_metrics
            results.append(print_result(
                has_master_metrics,
                "Master node has metrics"
            ))
            
            if has_master_metrics:
                master_metrics = all_metrics[master_node_id]
                print(f"📊 Master Node Metrics Keys: {list(master_metrics.keys())}")
        
        # ===== Test Case 5: Node Current Metrics =====
        if master_node_id:
            print_step(step, "Get current metrics for master node")
            step += 1
            
            current_metrics, response = node_helper.get_node_current_metrics(
                token, master_node_id
            )
            
            if current_metrics:
                results.append(print_result(True, "Current metrics retrieved"))
                
                # Check for common metric fields
                metric_fields = ['cpu_usage_percent', 'memory_used', 'memory_total', 
                               'disk_used', 'disk_total', 'timestamp']
                
                print(f"📊 Current Metrics:")
                for field in metric_fields:
                    if field in current_metrics:
                        value = current_metrics[field]
                        print(f"  - {field}: {value}")
                        results.append(print_result(True, f"Has {field}"))
                
                # If no standard fields, just show what we got
                if not any(field in current_metrics for field in metric_fields):
                    print(f"  Available fields: {list(current_metrics.keys())}")
                    results.append(print_result(
                        len(current_metrics) > 0,
                        f"Metrics data present: {len(current_metrics)} fields"
                    ))
            else:
                results.append(print_result(False, "Failed to get current metrics"))
        
        # ===== Test Case 6: Node Time-Range Metrics =====
        if master_node_id:
            print_step(step, "Get time-range metrics")
            step += 1
            
            time_metrics, response = node_helper.get_node_time_range_metrics(
                token, master_node_id
            )
            
            if time_metrics is not None:
                results.append(print_result(
                    True,
                    f"Time-range metrics retrieved: {len(time_metrics)} snapshots"
                ))
                
                if len(time_metrics) > 0:
                    print(f"📊 Sample metric snapshot: {list(time_metrics[0].keys())}")
            else:
                results.append(print_result(False, "Failed to get time-range metrics"))
            
            # Test with time range parameters
            print_step(step, "Test time-range with parameters")
            step += 1
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            time_metrics, response = node_helper.get_node_time_range_metrics(
                token=token,
                node_id=master_node_id,
                start_time=start_time.isoformat() + 'Z',
                end_time=end_time.isoformat() + 'Z'
            )
            
            results.append(print_result(
                time_metrics is not None,
                f"Time-range with params: {len(time_metrics) if time_metrics else 0} snapshots"
            ))
        
        # ===== Test Case 7: Edge Cases =====
        print_step(step, "Test edge case: Invalid node ID")
        step += 1
        
        invalid_id = "000000000000000000000000"
        node_data, response = node_helper.get_node(token, invalid_id)
        
        results.append(print_result(
            node_data is None,
            "Invalid node ID handled"
        ))
        
        print_step(step, "Test edge case: Metrics for invalid node")
        step += 1
        
        metrics, response = node_helper.get_node_current_metrics(token, invalid_id)
        
        results.append(print_result(
            metrics is None,
            "Invalid node metrics handled"
        ))
        
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
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
