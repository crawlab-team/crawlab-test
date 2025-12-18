# INT-005: Auto Node Group Registration on Startup

**Category**: Integration Testing  
**Priority**: P1 (Critical Feature)  
**Estimated Time**: 10-15 minutes  
**Backend**: script

## Objective

Validate that worker nodes can automatically register themselves into node groups upon startup using the `CRAWLAB_NODE_GROUPS` environment variable. This integration test ensures that the complete workflow—from environment configuration through node registration to database state—works correctly in dynamic environments like Kubernetes.

**Endpoints Covered**:
- `GET /api/nodes` - List nodes
- `GET /api/node-groups` - List node groups
- `GET /api/node-groups/{id}` - Get node group details

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- Docker available to start/stop worker nodes
- `crawlabteam/crawlab-pro:develop` image available

## Test Steps

### Setup
1. Authenticate as admin and get JWT token
2. Identify the master node and its gRPC address
3. Ensure no existing node groups with test names exist

### Test Case 1: Auto-Registration with Single Group

**1.1 Start worker with single group**
- Start a new worker container with `CRAWLAB_NODE_GROUPS=auto-group-1`
- Wait for node to register (approx. 10-20 seconds)

**1.2 Verify node group creation**
- Call `GET /api/node-groups`
- Verify a group named "auto-group-1" exists
- Verify the group description contains "Auto-created"

**1.3 Verify node assignment**
- Get the ID of the new worker node
- Call `GET /api/node-groups/{id}` for "auto-group-1"
- Verify the worker node ID is in the `node_ids` array

### Test Case 2: Auto-Registration with Multiple Groups

**2.1 Start worker with multiple groups**
- Start a new worker container with `CRAWLAB_NODE_GROUPS=auto-group-2,auto-group-3`
- Wait for node to register

**2.2 Verify multiple groups creation**
- Call `GET /api/node-groups`
- Verify both "auto-group-2" and "auto-group-3" exist

**2.3 Verify node assignment to all groups**
- Get the ID of the new worker node
- Verify the node ID is present in both groups' `node_ids` arrays

### Test Case 3: Case-Insensitive Matching

**3.1 Start worker with existing group name (different case)**
- Start a new worker container with `CRAWLAB_NODE_GROUPS=AUTO-GROUP-1`
- Wait for node to register

**3.2 Verify no duplicate group created**
- Call `GET /api/node-groups`
- Verify only one "auto-group-1" (or "AUTO-GROUP-1") exists
- Verify both workers are now in this group

### Test Case 4: Idempotency on Restart

**4.1 Restart worker node**
- Restart the worker container from Test Case 1
- Wait for it to re-register

**4.2 Verify group membership remains**
- Verify the node is still in "auto-group-1"
- Verify no duplicate entries in `node_ids`

### Test Case 5: Concurrent Registration (Duplicate Prevention)

**5.1 Start multiple workers simultaneously with same group name**
- Start 3 worker containers at the same time with `CRAWLAB_NODE_GROUPS=concurrent-test`
- Use background process execution to simulate race condition
- Wait for all nodes to register (approx. 20-30 seconds)

**5.2 Verify no duplicate groups created**
- Call `GET /api/node-groups`
- Filter for groups with name matching "concurrent-test" (case-insensitive)
- **Assert**: Exactly 1 group exists (not 2 or 3)
- **Assert**: Group has description containing "Auto-created"

**5.3 Verify all nodes in single group**
- Get all 3 worker node IDs
- Call `GET /api/node-groups/{id}` for the "concurrent-test" group
- **Assert**: All 3 node IDs are in the `node_ids` array
- **Assert**: No duplicate node IDs in the array

**5.4 Check for orphaned duplicate groups**
- List all node groups
- Count how many groups have names matching "concurrent-test" (case-insensitive)
- **Assert**: Count equals 1 (no duplicates even with case variations)

**Note**: This test validates the fix for spec 045 (Node Group Duplicate Prevention). If this test fails with multiple groups created, it indicates a race condition bug that needs fixing with database unique constraints and upsert operations.

### Cleanup
1. Stop and remove all test worker containers
2. Delete all auto-created node groups
3. Verify cluster returns to initial state

## Success Criteria

- [ ] Node groups are automatically created if they don't exist
- [ ] Nodes are correctly assigned to specified groups on registration
- [ ] Multiple groups are supported (comma-separated)
- [ ] Group name matching is case-insensitive
- [ ] Registration is idempotent (no duplicate assignments on restart)
- [ ] **Concurrent registrations do not create duplicate groups** (spec 045)
- [ ] All nodes from concurrent registrations are properly assigned to single group
- [ ] System remains stable during auto-registration
