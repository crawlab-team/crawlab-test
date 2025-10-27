# API-009: Node Management & Metrics

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Time**: 10-15 minutes  
**Backend**: script

## Objective

Validate node listing, details retrieval, and metrics endpoints for monitoring cluster health.

**Endpoints Covered**:
- `GET /api/nodes` - List nodes (with pagination, filtering)
- `GET /api/nodes/{id}` - Get node details
- `PATCH /api/nodes/{id}` - Update node
- `GET /api/nodes/metrics` - Get metrics for all nodes
- `GET /api/nodes/{id}/metrics/current` - Get current metrics for specific node
- `GET /api/nodes/{id}/metrics/time-range` - Get time-range metrics for specific node

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- At least one node registered (master node minimum)

## Test Steps

### Setup
1. Authenticate as admin and get JWT token

### Test Case 1: List Nodes

**1.1 List all nodes**
- Call `GET /api/nodes`
- Verify response status code is 200
- Verify response contains data array
- Verify at least one node exists (master node)

**1.2 Check master node**
- Verify one node has `is_master: true`
- Verify master node has required fields:
  - `_id`, `name`, `hostname`, `ip`, `status`, `enabled`

**1.3 Test pagination**
- Call `GET /api/nodes?page=1&size=5`
- Verify pagination works correctly
- Verify total count is returned

**1.4 Filter nodes**
- Filter by `is_master: true`
- Verify only master node(s) returned
- Filter by `enabled: true`
- Verify only enabled nodes returned

### Test Case 2: Get Node Details

**2.1 Get master node details**
- Get master node ID from list
- Call `GET /api/nodes/{id}`
- Verify response status code is 200
- Verify node details are complete:
  - Basic info: name, hostname, IP, MAC address
  - Status: status, enabled, active
  - Resources: max_runners, current_runners
  - Timestamps: created_at, updated_at

**2.2 Verify node status**
- Check `status` field (online, offline, unknown)
- Check `active` field (boolean)
- Check `enabled` field (boolean)

### Test Case 3: Update Node

**3.1 Update node description**
- Call `PATCH /api/nodes/{id}` with:
  - `description`: "Updated test description"
- Verify update succeeds
- Verify description is updated

**3.2 Update max_runners**
- Call `PATCH /api/nodes/{id}` with:
  - `max_runners`: 10
- Verify update succeeds
- Verify max_runners is updated

**3.3 Verify other fields unchanged**
- Confirm name, hostname, IP remain unchanged
- Confirm only updated fields were modified

### Test Case 4: Node Metrics - All Nodes

**4.1 Get metrics for all nodes**
- Call `GET /api/nodes/metrics`
- Verify response status code is 200
- Verify response is a map/dict of node_id -> metrics
- Verify metrics exist for master node

**4.2 Verify metrics structure**
- Check metrics contain expected fields:
  - CPU usage
  - Memory usage
  - Disk usage
  - Timestamp

### Test Case 5: Node Current Metrics

**5.1 Get current metrics for master node**
- Call `GET /api/nodes/{id}/metrics/current`
- Verify response status code is 200
- Verify metrics data is returned

**5.2 Verify current metrics fields**
- Check for system resource metrics:
  - CPU: usage percentage, cores
  - Memory: used, available, total
  - Disk: used, available, total
  - Network: optional
- Verify timestamp is recent

### Test Case 6: Node Time-Range Metrics

**6.1 Get historical metrics**
- Call `GET /api/nodes/{id}/metrics/time-range`
- Verify response status code is 200
- Verify response is an array of metric snapshots

**6.2 Test with time range parameters**
- Calculate time range (last hour)
- Call endpoint with `start_time` and `end_time`
- Verify filtered metrics returned
- Verify metrics within specified time range

### Test Case 7: Edge Cases

**7.1 Invalid node ID**
- Call `GET /api/nodes/{invalid_id}`
- Verify appropriate error response

**7.2 Metrics for non-existent node**
- Call `GET /api/nodes/{invalid_id}/metrics/current`
- Verify appropriate error response

**7.3 Empty time range**
- Call time-range metrics with future dates
- Verify empty array or appropriate response

### Cleanup
- No cleanup needed (read-only operations)
- Note: Node updates made during test are non-critical

## Success Criteria

- All nodes listed correctly
- Master node identified and accessible
- Node details complete and accurate
- Updates to node properties work
- Metrics endpoints return valid data
- Current metrics reflect system state
- Time-range metrics support historical queries
- Edge cases handled appropriately

## Expected Results

**Node Response Format**:
```json
{
  "data": {
    "_id": "node_id",
    "name": "Master Node",
    "hostname": "localhost",
    "ip": "127.0.0.1",
    "mac": "00:00:00:00:00:00",
    "is_master": true,
    "status": "online",
    "enabled": true,
    "active": true,
    "max_runners": 8,
    "current_runners": 2,
    "created_at": "2024-10-27T00:00:00Z"
  }
}
```

**Metrics Response Format**:
```json
{
  "data": {
    "cpu_usage_percent": 45.2,
    "memory_used": 4294967296,
    "memory_total": 17179869184,
    "disk_used": 107374182400,
    "disk_total": 536870912000,
    "timestamp": "2024-10-27T10:30:00Z"
  }
}
```

## Notes

- Node CRUD operations (create, delete) are typically not exposed via API
- Nodes register automatically when Crawlab services start
- Master node is critical and should not be disabled/deleted
- Metrics collection depends on node being online and active
- Historical metrics may have retention limits
- Node updates should be careful not to break cluster connectivity
