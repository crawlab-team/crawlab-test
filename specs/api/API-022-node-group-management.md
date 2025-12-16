````markdown
# API-022: Node Group Management

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Time**: 15-20 minutes  
**Backend**: script

## Objective

Validate node group CRUD operations, node assignment/removal, and task execution with node groups. This tests the node grouping feature (spec 041) that allows organizing nodes into logical groups and scheduling tasks to specific groups.

**Endpoints Covered**:
- `POST /api/node-groups` - Create node group
- `GET /api/node-groups` - List node groups (with pagination, filtering)
- `GET /api/node-groups/{id}` - Get node group details
- `PUT /api/node-groups/{id}` - Update node group
- `DELETE /api/node-groups/{id}` - Delete node group
- `DELETE /api/node-groups` - Delete multiple node groups
- `POST /api/node-groups/{id}/nodes` - Add node to group
- `DELETE /api/node-groups/{id}/nodes/{nodeId}` - Remove node from group
- `POST /api/tasks/run` - Run task with node group filtering

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- At least two worker nodes registered (for testing group assignments)
- A spider available for task execution tests

## Test Steps

### Setup
1. Authenticate as admin and get JWT token
2. Get list of available nodes (need at least 2 for meaningful tests)
3. Identify a test spider for task execution tests

### Test Case 1: Create Node Groups

**1.1 Create basic node group**
- Call `POST /api/node-groups` with:
  ```json
  {
    "data": {
      "name": "Production Servers",
      "description": "Production environment nodes"
    }
  }
  ```
- Verify response status code is 200
- Verify response contains created node group with:
  - `_id` field
  - `name`: "Production Servers"
  - `description`: "Production environment nodes"
  - `node_ids`: empty array
  - `created_at`, `updated_at` timestamps

**1.2 Create node group with initial nodes**
- Get IDs of 2 test nodes
- Call `POST /api/node-groups` with:
  ```json
  {
    "data": {
      "name": "Test Group",
      "description": "Test environment",
      "node_ids": ["node_id_1", "node_id_2"]
    }
  }
  ```
- Verify group created with nodes assigned
- Store group ID for later tests

**1.3 Create minimal node group**
- Call `POST /api/node-groups` with only name:
  ```json
  {
    "data": {
      "name": "Minimal Group"
    }
  }
  ```
- Verify creation succeeds with default values

### Test Case 2: List Node Groups

**2.1 List all node groups**
- Call `GET /api/node-groups`
- Verify response status code is 200
- Verify response contains data array
- Verify at least 3 groups exist (from TC1)
- Verify each group has required fields

**2.2 Test pagination**
- Call `GET /api/node-groups?page=1&size=2`
- Verify pagination works correctly
- Verify page size is respected
- Verify total count is returned

**2.3 Filter by name**
- Call `GET /api/node-groups?filter=Production`
- Verify only matching groups returned
- Verify "Production Servers" group is in results

### Test Case 3: Get Node Group Details

**3.1 Get group by ID**
- Get ID of "Production Servers" group from TC1
- Call `GET /api/node-groups/{id}`
- Verify response status code is 200
- Verify complete group details returned:
  - Basic info: `_id`, `name`, `description`
  - Node associations: `node_ids` array
  - Timestamps: `created_at`, `updated_at`

**3.2 Get group with populated nodes**
- Get ID of "Test Group" (has nodes assigned)
- Call `GET /api/node-groups/{id}`
- Verify response includes `nodes` array with full node details
- Verify each node in `nodes` array has:
  - `_id`, `name`, `hostname`, `ip`, `status`

**3.3 Invalid group ID**
- Call `GET /api/node-groups/invalid_id_12345`
- Verify appropriate error response (404 or 400)
- Verify error message indicates group not found

### Test Case 4: Add Nodes to Group

**4.1 Add single node to group**
- Get ID of "Production Servers" group (empty group)
- Get ID of first test node
- Call `POST /api/node-groups/{group_id}/nodes` with:
  ```json
  {
    "data": {
      "node_id": "node_id_1"
    }
  }
  ```
- Verify response status code is 200
- Get group details and verify node is in `node_ids` array

**4.2 Add another node to same group**
- Add second test node to "Production Servers" group
- Verify both nodes now in group
- Verify `node_ids` array has 2 elements

**4.3 Add node to multiple groups**
- Add same node to "Test Group" and "Production Servers"
- Verify node appears in both groups
- Confirm a node can belong to multiple groups

**4.4 Duplicate node assignment**
- Try adding same node to same group again
- Verify operation is idempotent (no duplicate, no error)

### Test Case 5: Remove Nodes from Group

**5.1 Remove single node**
- Remove first node from "Production Servers" group
- Call `DELETE /api/node-groups/{group_id}/nodes/{node_id}`
- Verify response status code is 200
- Get group details and verify node removed from `node_ids`

**5.2 Remove last node**
- Remove remaining node from "Production Servers" group
- Verify group still exists with empty `node_ids` array

**5.3 Remove non-existent node**
- Try removing node that's not in group
- Verify appropriate handling (should succeed or return 404)

### Test Case 6: Update Node Group

**6.1 Update name and description**
- Call `PUT /api/node-groups/{id}` with:
  ```json
  {
    "data": {
      "name": "Production Cluster",
      "description": "Updated production environment"
    }
  }
  ```
- Verify update succeeds
- Get group details and verify changes applied
- Verify `updated_at` timestamp changed

**6.2 Update node assignments**
- Call `PUT /api/node-groups/{id}` with new `node_ids` array
- Verify node assignments replaced
- Confirm previous nodes removed, new nodes added

**6.3 Clear all nodes**
- Update group with empty `node_ids` array
- Verify all nodes removed from group
- Verify group still exists

### Test Case 7: Task Execution with Node Groups

**7.1 Run task with single node group**
- Create or use existing spider
- Get ID of "Test Group" (has nodes assigned)
- Call `POST /api/tasks/run` with:
  ```json
  {
    "spider_id": "spider_id",
    "mode": "selected-nodes",
    "node_group_ids": ["test_group_id"],
    "cmd": "python main.py",
    "priority": 5
  }
  ```
- Verify task created successfully
- Verify task scheduled to nodes in the group
- Verify `node_group_ids` field is populated in task

**7.2 Run task with multiple node groups**
- Call `POST /api/tasks/run` with 2 group IDs
- Verify task can run on nodes from either group (OR logic)
- Verify union of nodes from both groups is used

**7.3 Run task with node groups + specific nodes (intersection)**
- Get ID of specific node that's in "Test Group"
- Call `POST /api/tasks/run` with:
  ```json
  {
    "spider_id": "spider_id",
    "mode": "selected-nodes",
    "node_group_ids": ["test_group_id"],
    "node_ids": ["specific_node_id"],
    "cmd": "python main.py"
  }
  ```
- Verify task runs only on nodes in BOTH group AND node_ids list
- Verify intersection logic works correctly

**7.4 Empty node group handling**
- Create node group with no nodes
- Try running task with empty group
- Verify appropriate error or fallback behavior

### Test Case 8: Delete Node Groups

**8.1 Delete single node group**
- Call `DELETE /api/node-groups/{id}`
- Verify response status code is 200
- Verify group no longer in list
- Call `GET /api/node-groups/{id}` to confirm deletion

**8.2 Delete group with nodes**
- Delete "Test Group" which has nodes assigned
- Verify deletion succeeds
- Verify nodes themselves are NOT deleted
- Verify nodes still accessible via node API

**8.3 Delete multiple node groups**
- Create 2 temporary node groups
- Call `DELETE /api/node-groups` with:
  ```json
  {
    "ids": ["group_id_1", "group_id_2"]
  }
  ```
- Verify both groups deleted
- Verify batch deletion works

**8.4 Delete non-existent group**
- Try deleting already-deleted group
- Verify appropriate error response (404)

### Test Case 9: Edge Cases & Validation

**9.1 Create group without name**
- Try creating group with empty/null name
- Verify validation error returned
- Verify appropriate error message

**9.2 Invalid node ID in node_ids**
- Try creating group with non-existent node ID
- Verify appropriate handling (error or ignore)

**9.3 Concurrent updates**
- Get group details
- Update group from two requests simultaneously
- Verify last write wins or proper conflict handling

**9.4 Special characters in name**
- Create group with name containing special chars: `Test-Group_#1 (2025)`
- Verify creation succeeds
- Verify retrieval and filtering work correctly

### Cleanup
1. Delete all test node groups created during test
2. Verify all test groups removed
3. Cancel/clean up any running test tasks
4. Confirm no side effects on actual node configuration

## Success Criteria

- All CRUD operations work correctly
- Node assignment/removal operations succeed
- A node can belong to multiple groups
- Node groups can be empty
- Task execution with node groups works:
  - Single group filtering
  - Multiple groups (OR logic)
  - Group + node IDs (AND/intersection logic)
  - Empty group handling
- Pagination and filtering work
- Edge cases handled appropriately
- Deleting group doesn't affect nodes themselves
- All cleanup operations succeed

## Expected Response Formats

**Create/Update Node Group Response**:
```json
{
  "data": {
    "_id": "group_id",
    "name": "Production Servers",
    "description": "Production environment nodes",
    "node_ids": ["node_id_1", "node_id_2"],
    "created_at": "2025-12-16T00:00:00Z",
    "updated_at": "2025-12-16T00:00:00Z"
  }
}
```

**Get Node Group with Populated Nodes**:
```json
{
  "data": {
    "_id": "group_id",
    "name": "Production Servers",
    "description": "Production environment nodes",
    "node_ids": ["node_id_1", "node_id_2"],
    "nodes": [
      {
        "_id": "node_id_1",
        "name": "Worker-1",
        "hostname": "worker-1.local",
        "ip": "192.168.1.10",
        "status": "online"
      },
      {
        "_id": "node_id_2",
        "name": "Worker-2",
        "hostname": "worker-2.local",
        "ip": "192.168.1.11",
        "status": "online"
      }
    ],
    "created_at": "2025-12-16T00:00:00Z",
    "updated_at": "2025-12-16T00:00:00Z"
  }
}
```

**List Node Groups Response**:
```json
{
  "data": [
    {
      "_id": "group_id_1",
      "name": "Production Servers",
      "description": "Production environment nodes",
      "node_ids": ["node_id_1"],
      "created_at": "2025-12-16T00:00:00Z"
    },
    {
      "_id": "group_id_2",
      "name": "Test Group",
      "description": "Test environment",
      "node_ids": ["node_id_2"],
      "created_at": "2025-12-16T00:00:00Z"
    }
  ],
  "total": 2
}
```

## API Endpoint Notes

Based on spec 041-node-grouping implementation:

**Body Format**:
- Create/Update: Wrap payload in `{"data": {...}}`
- Check OpenAPI spec at `http://localhost:8080/api/openapi.json` for exact format

**Task Run Endpoint**:
- `mode`: Should be `"selected-nodes"` when using node groups
- `node_group_ids`: Array of group IDs
- `node_ids`: Optional, for intersection filtering
- Backend resolves groups to actual node IDs before scheduling

**Node Group Resolution**:
- Groups are resolved at task creation time
- Multiple groups use OR logic (union of nodes)
- Groups + node_ids use AND logic (intersection)
- Empty groups should be handled gracefully

## Notes

- Node groups are a Pro feature (spec 041)
- Groups organize nodes logically without modifying node models
- Groups are stored in separate collection
- Deleting a group doesn't affect nodes
- Task scheduling resolves groups at controller layer
- UI integration completed in spec 043
- This test focuses on API/backend functionality

## References

- Spec: 041-node-grouping
- Implementation: `core/controllers/node_group.go`
- Task Controller: `core/controllers/task.go`
- Services: `core/spider/admin/node_group.go`

````