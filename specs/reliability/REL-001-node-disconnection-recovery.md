# REL-001 - Master/Worker Node Disconnection and Reconnection Stability

## Metadata
- **Category**: reliability
- **Priority**: critical
- **Complexity**: moderate
- **Duration**: 15-20 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, mongodb, redis

## Scenario
This test validates that the Crawlab cluster can handle worker node disconnections gracefully and that reconnection works properly without data loss or zombie tasks. This is critical for production stability where network issues or node restarts are common.

## Prerequisites
- Crawlab master node running and accessible
- At least 2 worker nodes connected and active
- Some test spiders/tasks available for execution
- Network access to simulate disconnections
- MongoDB and Redis accessible

## Test Steps

### Step 1: Verify Initial Cluster State
**Method**: script
**Command**: `./helpers/infrastructure/cluster-health.py --check-initial`
**Expected**: All nodes healthy, tasks can be scheduled
**Validation**: 
- All worker nodes show as "online" in UI
- Can create and run a test task successfully

### Step 2: Start Background Task Load
**Method**: script  
**Command**: `./helpers/infrastructure/task-generator.py --start --count 5 --duration 300`
**Expected**: Multiple tasks running across different workers
**Validation**: Tasks distributed across worker nodes

### Step 3: Simulate Worker Disconnection
**Method**: script
**Command**: `./helpers/infrastructure/node-manager.py --disconnect worker-1 --method network`
**Expected**: Worker-1 becomes unreachable but master continues
**Validation**: 
- Worker-1 shows as "offline" in master UI
- Running tasks on worker-1 are marked as failed or reassigned
- No new tasks scheduled to worker-1

### Step 4: Verify Task Redistribution
**Method**: script
**Command**: `./helpers/infrastructure/task-monitor.py --verify-redistribution --timeout 60`
**Expected**: Tasks reassigned to healthy workers
**Validation**: 
- No tasks stuck in "running" state on disconnected worker
- New tasks only go to healthy workers
- Task queue continues processing

### Step 5: Reconnect Worker Node  
**Method**: script
**Command**: `./helpers/infrastructure/node-manager.py --reconnect worker-1`
**Expected**: Worker-1 rejoins cluster successfully
**Validation**:
- Worker-1 shows as "online" in master UI
- Worker-1 starts receiving new tasks
- No duplicate task executions

### Step 6: Verify Data Consistency
**Method**: script
**Command**: `./helpers/infrastructure/data-validator.py --check-consistency`
**Expected**: No data corruption or inconsistencies
**Validation**:
- Task status in database matches reality
- No orphaned tasks or processes
- Task results properly recorded

### Step 7: Stress Test Recovery
**Method**: script
**Command**: `./helpers/infrastructure/task-generator.py --burst --count 20`
**Expected**: Cluster handles burst load after reconnection
**Validation**: All tasks complete successfully

## Success Criteria
- [ ] Worker disconnection detected within 40-60 seconds (master checks every 20s, requires 2 consecutive failures)
- [ ] Running tasks on disconnected worker handled gracefully (failed or reassigned)
- [ ] No new tasks assigned to disconnected worker
- [ ] Task queue continues processing on healthy workers
- [ ] Worker reconnection successful within 60 seconds of network restoration
- [ ] Reconnected worker achieves stable online status within 60 seconds (3 monitoring cycles in CI)
- [ ] Reconnected worker starts receiving tasks normally after stabilization
- [ ] No data inconsistencies or corruption
- [ ] No zombie processes or orphaned tasks
- [ ] System performance returns to baseline after reconnection

## Monitoring Behavior (Updated)
**Master Node Monitoring:**
- Monitor interval: 20 seconds
- Grace period: 2 consecutive failures required before marking node offline  
- Total grace time: ~40 seconds before node marked offline
- Reason: Prevents flapping during brief reconnection windows (3-5s for gRPC re-subscription)

**Test Stability Requirements:**
- Stability period: 60 seconds (3 full monitoring cycles) in CI, 50 seconds locally
- Flap tolerance: Up to 5 brief offline transitions in CI, 3 locally
- Rationale: Must wait for at least 3 monitoring cycles (3 × 20s = 60s) to confirm stable recovery
- CI considerations: Resource constraints can cause brief offline moments, requiring higher tolerance

## Failure Scenarios
- **Scenario**: Tasks stuck in "running" state on disconnected worker
- **Symptoms**: Tasks never complete or fail, task count doesn't decrease
- **Action**: Check task timeout mechanisms and cleanup processes

- **Scenario**: Worker cannot reconnect
- **Symptoms**: Worker stays offline even after network restoration
- **Action**: Check authentication, registration process, logs

- **Scenario**: Duplicate task execution
- **Symptoms**: Same task runs on multiple workers after reconnection  
- **Action**: Verify task assignment and locking mechanisms

## Execution

### Automated
```bash
# Run the complete test suite
./helpers/infrastructure/node-disconnection-test.py --full-test

# Or run individual steps
./helpers/infrastructure/cluster-health.py --check-initial
./helpers/infrastructure/node-manager.py --disconnect worker-1
# ... etc
```

### GitHub Copilot CLI
```bash
# Run with Copilot (prompts for tool approval locally, auto-approved in CI)
./run-with-copilot.py specs/infrastructure/INF-001-master-worker-node-disconnection-and-reconnection-stability.md

# Via test-runner (auto-detects method)
./test-runner.py --spec specs/infrastructure/INF-001-master-worker-node-disconnection-and-reconnection-stability.md --method copilot
```

**What Copilot CLI will do:**
1. Verify prerequisites and cluster health
2. Execute helper scripts for node disconnection
3. Monitor cluster status and task reassignment
4. Validate success criteria automatically
5. Reconnect nodes and verify recovery
6. Generate detailed execution report

### Manual
1. Open Crawlab UI in browser
2. Navigate to nodes page  
3. Start some test tasks
4. Use docker/systemctl to stop worker node
5. Verify UI shows worker as offline
6. Check that tasks are handled properly
7. Restart worker and verify reconnection

## Cleanup
- Stop any remaining test tasks: `./helpers/infrastructure/task-generator.py --stop`
- Ensure all workers reconnected: `./helpers/infrastructure/cluster-health.py --restore`
- Clear test data: `./helpers/common/cleanup.py --test-data`

## Notes
- Network disconnection is preferred over process killing to better simulate real scenarios
- Monitor logs during test execution for error patterns
- Test should work with different numbers of worker nodes
- Consider testing with different types of tasks (CPU vs I/O intensive)

## History
- **Created**: 2025-09-17, Assistant
- **Modified**: -
- **Last Run**: -