# INT-006: Node Group Duplicate Prevention on Worker Registration

**Category**: Integration Testing  
**Priority**: P1 (Regression)  
**Estimated Time**: 12-18 minutes  
**Backend**: script

## Objective

Validate that multiple worker nodes registering with the same node-group name do not create duplicate node-group records. This covers sequential, concurrent, and case-variant registrations to ensure node-group uniqueness and correct node membership assignments.

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
1. Authenticate as admin and get JWT token.
2. Identify the master node and its gRPC address.
3. Ensure no existing node groups named `dup-group-*` (delete if present).

### Test Case 1: Sequential Registration, Same Group Name

**1.1 Start first worker**
- Start worker container `worker-seq-1` with `CRAWLAB_NODE_GROUPS=dup-group-1`.
- Wait for node to register (10-20 seconds).

**1.2 Start second worker with same group**
- Start worker container `worker-seq-2` with `CRAWLAB_NODE_GROUPS=dup-group-1`.
- Wait for registration.

**1.3 Verify single group and membership**
- Call `GET /api/node-groups` and filter by `name=dup-group-1` (case-insensitive).
- **Assert**: Exactly 1 group exists.
- Get the group ID and call `GET /api/node-groups/{id}`.
- **Assert**: Both worker node IDs are present in `node_ids` (no duplicates).

### Test Case 2: Concurrent Registration, Same Group Name

**2.1 Launch workers concurrently**
- Start 3 worker containers (`worker-con-1..3`) in parallel with `CRAWLAB_NODE_GROUPS=dup-group-2`.
- Wait for all nodes to register (20-30 seconds).

**2.2 Verify no duplicate groups created**
- Call `GET /api/node-groups` with filter `dup-group-2`.
- **Assert**: Exactly 1 group exists (not 2-3).

**2.3 Verify membership aggregation**
- Call `GET /api/node-groups/{id}` for `dup-group-2`.
- **Assert**: All 3 worker node IDs exist in `node_ids` with no duplicates.

### Test Case 3: Case-Variant Registration

**3.1 Start worker with uppercase name**
- Start worker container `worker-case-1` with `CRAWLAB_NODE_GROUPS=DUP-GROUP-1`.
- Wait for registration.

**3.2 Verify reused group**
- Call `GET /api/node-groups` filter `dup-group-1`.
- **Assert**: Still only 1 group for `dup-group-1`/`DUP-GROUP-1`.
- **Assert**: `worker-case-1` node ID added to the existing group (no new group ID created).

### Test Case 4: Idempotent Re-registration

**4.1 Restart existing worker**
- Restart `worker-seq-1` (from TC1) with same env `CRAWLAB_NODE_GROUPS=dup-group-1`.
- Wait for re-registration.

**4.2 Verify stability**
- Call `GET /api/node-groups` filter `dup-group-1`.
- **Assert**: Exactly 1 group persists.
- **Assert**: Group `node_ids` contains all relevant worker IDs without duplication.

### Cleanup
1. Stop and remove all test worker containers (`worker-seq-*`, `worker-con-*`, `worker-case-*`).
2. Delete node groups `dup-group-1` and `dup-group-2` if they exist.
3. Verify cluster returns to initial state (no `dup-group-*` groups, no test workers).

## Success Criteria

- [ ] Sequential registrations with identical group name reuse the same node group.
- [ ] Concurrent registrations with identical group name do not create duplicate node groups.
- [ ] Case-variant registrations reuse the existing group (case-insensitive matching).
- [ ] Group membership contains all worker nodes without duplicate IDs.
- [ ] Cleanups remove all test artifacts and restore initial cluster state.
