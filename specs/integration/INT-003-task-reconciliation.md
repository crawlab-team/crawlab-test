# INT-003 - Task Status Reconciliation and Process Verification

## Metadata
- **Category**: integration
- **Priority**: critical
- **Complexity**: complex
- **Duration**: 25-30 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, mongodb, redis, task-reconciliation-service

## Scenario
This test validates the Task Reconciliation Service's ability to maintain accurate task status by synchronizing database state with actual process status on worker nodes. It ensures that tasks marked as "running" in the database actually correspond to running processes, and that orphaned or zombie tasks are properly detected and cleaned up. This prevents inconsistent task states that could lead to resource leaks, incorrect scheduling decisions, or misleading monitoring data.

## Prerequisites
- Crawlab master node with TaskReconciliationService enabled
- At least 2 worker nodes connected and active
- gRPC process status checking functionality available
- Test spiders with varying execution times (short, long-running)
- Ability to simulate process crashes and network issues
- MongoDB accessible for direct database queries
- Proper logging configuration for debugging

## Test Steps

### Step 1: Verify Reconciliation Service Status
**Method**: script
**Command**: `./helpers/infrastructure/reconciliation-health.py --check-service`
**Expected**: TaskReconciliationService is running and operational
**Validation**: 
- Periodic reconciliation is active (every 30 seconds)
- Service responds to health checks
- No error logs in master node

### Step 2: Establish Baseline Task State
**Method**: script
**Command**: `./helpers/infrastructure/task-baseline.py --create --count 10 --types mixed`
**Expected**: Mix of pending, running, and completed tasks
**Validation**: 
- Database task statuses are accurate
- All running tasks have active processes
- No orphaned database entries

### Step 3: Simulate Process Crashes (Zombie Tasks)
**Method**: script
**Command**: `./helpers/infrastructure/process-killer.py --target running-tasks --method SIGKILL --count 3`
**Expected**: Some task processes terminated but database still shows "running"
**Validation**: 
- Process PIDs no longer exist on worker nodes
- Database still shows tasks as "running" (before reconciliation)
- Task streams may still be active

### Step 4: Wait for Reconciliation Cycle
**Method**: script
**Command**: `./helpers/infrastructure/reconciliation-monitor.py --wait-cycle --timeout 90`
**Expected**: Reconciliation service detects and fixes inconsistencies
**Validation**: 
- Killed task processes detected as "not found"
- Database task statuses updated to "error" or "finished"
- Reconciliation logs show proper detection and updates

### Step 5: Simulate Worker Node Disconnection
**Method**: script
**Command**: `./helpers/infrastructure/node-manager.py --disconnect worker-1 --method graceful`
**Expected**: Tasks on disconnected worker marked as "node_disconnected"
**Validation**: 
- Running tasks on worker-1 marked as "node_disconnected"
- No false positives (tasks on other workers unaffected)
- Error messages indicate disconnection reason

### Step 6: Verify Conservative Status Handling
**Method**: script
**Command**: `./helpers/infrastructure/status-validator.py --check-conservative-logic`
**Expected**: Uncertain statuses kept rather than assumed as errors
**Validation**: 
- Tasks with unclear status remain "node_disconnected" 
- No false "abnormal" status assignments
- Reconciliation doesn't make unfounded assumptions

### Step 7: Test Worker Reconnection Reconciliation
**Method**: script
**Command**: `./helpers/infrastructure/node-manager.py --reconnect worker-1`
**Expected**: Disconnected tasks properly reconciled on reconnection
**Validation**: 
- Reconnection triggers task status verification
- Actually running processes restored to "running" status
- Finished processes marked appropriately
- No duplicate executions

### Step 8: Verify Process Status Query Protocol
**Method**: script
**Command**: `./helpers/infrastructure/grpc-tester.py --test-process-queries --worker worker-1`
**Expected**: gRPC CheckProcess calls work correctly
**Validation**: 
- Worker responds to ProcessStatusRequest messages
- ProcessStatus enum values mapped correctly
- Timeout handling works properly
- Process details (PID, exit codes) accurate

### Step 9: Test Periodic Reconciliation Under Load
**Method**: script
**Command**: `./helpers/infrastructure/load-generator.py --reconciliation-stress --duration 300`
**Expected**: Reconciliation performs well with many tasks
**Validation**: 
- Reconciliation cycles complete within reasonable time
- High task volume doesn't cause timeouts
- Database updates are atomic and consistent
- No performance degradation

### Step 10: Validate Manual Reconciliation API
**Method**: script
**Command**: `./helpers/infrastructure/manual-reconcile.py --test-api --task-id specific-task`
**Expected**: ForceReconcileTask API works correctly
**Validation**: 
- Manual reconciliation triggers immediately
- Specific task status verified and updated
- API returns appropriate error codes
- Logging shows manual reconciliation events

### Step 11: Test Edge Cases and Error Conditions
**Method**: script
**Command**: `./helpers/infrastructure/edge-case-tester.py --run-all`
**Expected**: Service handles edge cases gracefully
**Validation**: 
- Invalid PIDs handled without crashes
- Corrupted task data doesn't break reconciliation
- Worker communication failures handled gracefully
- Service remains stable during error conditions

### Step 12: Verify Final System Consistency
**Method**: script
**Command**: `./helpers/infrastructure/consistency-validator.py --comprehensive-check`
**Expected**: All task statuses accurately reflect reality
**Validation**: 
- No orphaned processes without database entries
- No database "running" tasks without active processes
- Task timing information is consistent
- Error messages provide useful debugging info

## Success Criteria
- [ ] Zombie task detection: 95% of orphaned processes detected within 60 seconds
- [ ] Database synchronization: Task statuses updated within 30 seconds of process state changes
- [ ] Conservative handling: No false "abnormal" status assignments when status is uncertain
- [ ] Reconnection handling: 100% of disconnected tasks properly reconciled on worker reconnection
- [ ] Process query protocol: gRPC CheckProcess succeeds with <5 second timeout
- [ ] Performance: Reconciliation completes for 1000+ tasks within 2 minutes
- [ ] Error resilience: Service continues operating during worker communication failures
- [ ] Manual API: ForceReconcileTask completes within 10 seconds
- [ ] Data integrity: No task state corruption or race conditions
- [ ] Logging quality: All reconciliation actions properly logged with context

## Failure Scenarios

- **Scenario**: Reconciliation service doesn't detect zombie tasks
- **Symptoms**: Database shows "running" but no corresponding process exists
- **Action**: Check periodic reconciliation frequency, process existence checking, and gRPC communication

- **Scenario**: False positive task failures
- **Symptoms**: Running tasks incorrectly marked as "error" or "abnormal"
- **Action**: Verify conservative status logic, check worker communication timeouts, validate heuristic detection

- **Scenario**: Worker reconnection doesn't trigger reconciliation
- **Symptoms**: Tasks stay "node_disconnected" even after worker comes online
- **Action**: Check HandleNodeReconnection integration, worker registration events, subscription stream management

- **Scenario**: gRPC process queries fail or timeout
- **Symptoms**: Reconciliation falls back to heuristics, no direct process status
- **Action**: Verify worker gRPC server, network connectivity, protocol implementation, timeout configuration

- **Scenario**: Database corruption during concurrent updates
- **Symptoms**: Task status inconsistencies, partial updates, deadlocks
- **Action**: Check transaction handling, update retry logic, database isolation levels

## Execution

### Automated
```bash
# Run the complete reconciliation test suite
./helpers/infrastructure/task-reconciliation-test.py --full-suite

# Run specific test categories
./helpers/infrastructure/task-reconciliation-test.py --test zombie-detection
./helpers/infrastructure/task-reconciliation-test.py --test worker-reconnection
./helpers/infrastructure/task-reconciliation-test.py --test grpc-protocol

# Performance and stress testing
./helpers/infrastructure/reconciliation-stress.py --duration 600 --concurrent-tasks 2000
```

### AI-Assisted
```bash
# Use AI to execute reconciliation tests with intelligent validation
ai-test-runner --spec specs/infrastructure/task-reconciliation.md --executor hybrid
ai-test-runner --scenario zombie-detection --validate-heuristics
```

### Manual
1. Open Crawlab UI and task monitoring dashboard
2. Start several long-running test tasks
3. Manually kill task processes via SSH/docker exec
4. Monitor reconciliation service logs
5. Verify database task statuses are updated correctly
6. Test worker disconnection scenarios
7. Validate manual reconciliation API via curl/Postman

## Cleanup
- Stop reconciliation stress tests: `./helpers/infrastructure/load-generator.py --stop`
- Ensure all test tasks terminated: `./helpers/infrastructure/task-cleanup.py --force`
- Reset worker node states: `./helpers/infrastructure/node-manager.py --reset-all`
- Clear test data and logs: `./helpers/common/cleanup.py --reconciliation-test-data`
- Verify service health: `./helpers/infrastructure/reconciliation-health.py --final-check`

## Notes
- This test requires the new gRPC CheckProcess protocol to be fully implemented
- Monitor CPU and memory usage during high-load scenarios
- Test with different task types (CPU-intensive, I/O-bound, long-running, short)
- Consider testing with various worker node configurations (single-core, multi-core)
- Pay attention to edge cases with very short-lived tasks
- Database query performance may impact reconciliation speed with large task volumes
- Network latency between master and workers affects reconciliation accuracy

## Dependencies on Implementation
- **Current Status**: Core reconciliation logic implemented with conservative status handling
- **Missing**: Direct worker gRPC communication infrastructure (worker discovery, connection pooling)
- **Fallback**: Heuristic-based detection using task streams and update timestamps
- **Future**: Full process status verification once worker discovery is implemented

## History
- **Created**: 2025-09-17, Assistant - Initial specification for Task Reconciliation Service testing
- **Modified**: -
- **Last Run**: -