# DEP-002 - Dependency Handler Network Reconnection Resilience

## Metadata
- **Category**: dependencies
- **Priority**: critical
- **Complexity**: moderate
- **Duration**: 10-15 minutes
- **Environment**: docker/staging
- **Dependencies**: crawlab-master, crawlab-worker, docker network, package managers

## Scenario
This test validates that Crawlab's dependency handler can recover gracefully from network disconnections and maintain dependency synchronization functionality. This specifically tests the fixes made to handle worker node network disturbances that previously caused dependency installation failures.

## Prerequisites
- Crawlab cluster running in Docker containers
- At least 1 worker node connected and active
- Docker network controls available for disconnection simulation
- Package managers (pip, npm) available in worker containers
- Network access to package repositories
- Sufficient privileges to manipulate Docker networks

## Test Steps

### Step 1: Execute Network Reconnection Test
**Method**: script
**Command**: Test dependency handler resilience through network disruptions
**Expected**: Dependency handler maintains resilience through network disruptions
**Validation**: 
- No dependency installation failures during network recovery
- Package installations resume properly after reconnection
- System handles timeouts gracefully
- No corrupted package states

### Step 2: Install Test Dependencies
**Method**: script  
**Command**: Included in main test script
**Expected**: Test packages install successfully
**Validation**: 
- Python packages (requests, beautifulsoup4) install correctly
- Node packages (lodash) install correctly
- Dependencies appear in system dependency list

### Step 3: Verify Dependency Synchronization
**Method**: script
**Command**: Included in main test script
**Expected**: Dependencies properly synchronized between worker and master
**Validation**: 
- Installed dependencies visible in master UI/API
- Dependency counts match expected values
- Sync status shows as current

### Step 4: Simulate Network Disconnection  
**Method**: script
**Command**: Uses docker network disconnect
**Expected**: Worker node becomes unreachable
**Validation**: 
- Worker status changes to "offline" in master
- Disconnection detected within 60 seconds
- Master remains responsive

### Step 5: Verify Graceful Disconnection Handling
**Method**: script
**Command**: Attempts dependency operations during disconnection
**Expected**: System handles disconnection gracefully
**Validation**: 
- Dependency operations fail gracefully (no crashes)
- Master continues to operate normally
- No corruption in dependency state

### Step 6: Restore Network Connection
**Method**: script
**Command**: Uses docker network reconnect  
**Expected**: Worker rejoins cluster successfully
**Validation**: 
- Worker status returns to "online"
- Reconnection detected within 120 seconds
- No duplicate worker registrations

### Step 7: Verify Dependency Handler Reconnection
**Method**: script
**Command**: Checks dependency sync restoration
**Expected**: Dependency handler reconnects and syncs automatically  
**Validation**: 
- Dependency stream reconnects (no manual intervention)
- Previous dependencies still show as installed
- Sync status updates correctly

### Step 8: Test Post-Reconnection Operations
**Method**: script
**Command**: Installs new dependency after reconnection
**Expected**: New dependency operations work correctly
**Validation**: 
- New package (click) installs successfully
- Installation appears in dependency sync
- No issues with dependency operations

## Success Criteria
- [ ] Worker disconnection detected and handled gracefully
- [ ] Dependency handler survives network disconnection
- [ ] Worker reconnection successful without manual intervention
- [ ] Dependency handler automatically reconnects after network restoration
- [ ] Post-reconnection dependency operations work correctly
- [ ] No dependency state corruption during disconnection/reconnection
- [ ] Dependency synchronization restored automatically
- [ ] No orphaned dependency processes or streams
- [ ] System performance returns to baseline after reconnection

## Failure Scenarios

### Scenario: Dependency handler exits after reconnection failures
- **Symptoms**: Handler stops attempting to reconnect after network restoration
- **Root Cause**: Previous implementation exited after 5 failed reconnection attempts  
- **Fix**: Persistent reconnection with exponential backoff (no giving up)
- **Validation**: Handler continues attempting reconnection indefinitely

### Scenario: Dependencies don't sync after reconnection
- **Symptoms**: Dependency operations fail even after worker comes back online
- **Root Cause**: No automatic sync trigger after successful reconnection
- **Fix**: Added post-reconnection sync trigger to restore consistency
- **Validation**: Dependency sync works immediately after reconnection

### Scenario: GRPC connection issues prevent operations
- **Symptoms**: Dependency operations fail with GRPC client errors
- **Root Cause**: Insufficient retry logic for connection setup and operations
- **Fix**: Added comprehensive retry logic with backoff for all dependency operations
- **Validation**: Operations succeed even with temporary connection issues

### Scenario: Worker appears online but dependency handler stuck
- **Symptoms**: Worker shows as connected but dependencies don't work  
- **Root Cause**: Missing GRPC client readiness checks before operations
- **Fix**: Added comprehensive client readiness verification similar to WorkerService
- **Validation**: Dependency operations only proceed when GRPC client is fully ready

## Execution

### Automated (Recommended)
```bash
# Run the complete dependency reconnection test
./helpers/dependencies/dependency-reconnection-test.py --verbose

# Run via test runner framework
./test-runner.py --spec specs/dependencies/dependency-reconnection.md --method script

# Run with specific configuration
./helpers/dependencies/dependency-reconnection-test.py --master-url http://localhost:8080 --verbose
```

### Docker Environment Setup
```bash
# Ensure proper Docker network setup for testing
docker network ls | grep bridge

# Verify containers are running
docker ps | grep crawlab

# Check container network connections
docker network inspect bridge
```

### Manual Verification
1. Open Crawlab UI and monitor worker nodes page
2. Check dependency management interface
3. Monitor logs during test execution:
   ```bash
   docker logs -f crawlab-worker-1
   docker logs -f crawlab-master
   ```
4. Verify dependency installation works before/after test

## Logs to Monitor

### Master Logs
- `[DependencyHandler] failed to reconnect after X attempts, exiting` (should NOT appear)
- `[DependencyHandler] successfully reconnected after X attempts` (should appear)
- `[DependencyHandler] gRPC client is ready and registered` (should appear after reconnection)

### Worker Logs  
- `gRPC client is in SHUTDOWN state, forcing reset` (may appear during reconnection)
- `worker subscription stopped due to context cancellation` (during disconnection)
- `successfully subscribed to master` (after reconnection)

### Dependency Operation Logs
- `failed to get dependency client after retries: %v` (should NOT appear after reconnection)
- `successfully reconnected after %d attempts` (should appear in dependency handler)

## Cleanup
- Restore network connections: Test runner handles automatic network restoration
- Clean up test packages: Remove any test packages installed during the test
- Reset dependency handler state: Ensure handler returns to normal operation
- Remove test packages: Clean dependency environments if needed
- Reset worker state: Ensure all workers show as online
- Clear test logs: `docker logs --since 1h crawlab-worker-1 > /dev/null`

## Notes
- This test specifically validates fixes made to dependency handler reconnection logic
- Uses Docker network manipulation for reliable disconnection simulation
- Tests both the connection management and dependency operation retry logic
- Designed to run in containerized environments where network control is available
- Should be run after any changes to dependency handler or GRPC client code

## History
- **Created**: 2025-09-17, Assistant (for dependency handler reconnection fixes)
- **Modified**: -
- **Last Run**: -