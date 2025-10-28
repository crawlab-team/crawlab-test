# REL-002 - Docker Container Node Disconnection and Recovery

## Metadata
- **Category**: reliability
- **Priority**: critical
- **Complexity**: moderate
- **Duration**: 15-20 minutes
- **Environment**: docker/local
- **Dependencies**: docker, docker-compose, crawlab containers

## Scenario
This test validates that the Crawlab cluster running in Docker containers can handle worker container disconnections gracefully and that reconnection works properly without data loss or zombie tasks. This test specifically focuses on Docker-based deployments where nodes run as containers and can be managed using Docker CLI.

## Prerequisites
- Docker and Docker Compose installed and running
- Crawlab cluster running in Docker containers (master + 2+ workers)
- Docker containers accessible via docker commands
- Test data and spiders available for task execution
- Network connectivity between containers

## Environment Detection
The test automatically detects whether Crawlab is running in Docker containers and adjusts accordingly:
- **Docker Detection**: Uses Docker CLI to find running Crawlab containers
- **API Endpoint**: Automatically discovers master container and API endpoint
- **Container Names**: Dynamically identifies master and worker containers

## Test Steps

### Step 1: Initial Health Check
**Method**: script
**Command**: Verify all Docker containers are healthy and communicating
**Expected**: All containers are healthy and communicating
**Validation**: No container errors, all nodes show as active

### Step 2: Baseline Container Status
**Method**: script
**Command**: List and verify all expected containers are running and networked properly
**Expected**: All expected containers are running and networked properly
**Validation**: Container list matches expected topology

### Step 3: Create Baseline Tasks
**Method**: script
**Command**: Create test tasks for baseline performance measurement
**Expected**: Test tasks created and ready for execution
**Validation**: Tasks appear in system and are schedulable

### Step 4: Simulate Network Disconnection (Worker-1)
**Method**: script
**Command**: Simulate network disconnection for worker-1 container
**Expected**: Worker-1 loses network connectivity while container remains running
**Validation**: Container shows as disconnected in node list

### Step 5: Monitor System Response
**Method**: script
**Command**: Monitor system response to worker disconnection with timeout
**Expected**: System detects disconnection and handles gracefully
**Validation**: 
- Tasks reassigned to available workers
- No data corruption or loss
- Master remains stable

### Step 6: Verify Logs and Error Handling
**Method**: script
**Command**: Check master container logs for disconnection detection and response
**Expected**: Master logs show proper disconnection detection and response
**Validation**: Error messages are informative, no system crashes

### Step 7: Restore Network Connection
**Method**: script
**Command**: Restore network connection for worker-1 container
**Expected**: Worker-1 reconnects and rejoins the cluster
**Validation**: Node appears as active, can accept new tasks

### Step 8: Verify Recovery
**Method**: script
**Command**: Verify all containers are healthy and system is fully operational
**Expected**: All containers healthy, system fully operational
**Validation**: All nodes active, task assignment working normally

### Step 9: Test Container Pause Scenario
**Method**: script
**Command**: Pause worker-2 container to simulate container-level disconnection
**Expected**: Worker-2 pauses, tasks migrate to other workers
**Validation**: No task failures, smooth migration

### Step 10: Resume Container
**Method**: script
**Command**: Resume worker-2 container and verify cluster rejoin
**Expected**: Worker-2 resumes and rejoins cluster
**Validation**: Full system recovery, all nodes operational

## Success Criteria
- [ ] Docker environment auto-detection works correctly
- [ ] Container network disconnection detected within 40-60 seconds (master checks every 20s, requires 2 consecutive failures)
- [ ] Running tasks on disconnected container handled gracefully
- [ ] No new tasks assigned to disconnected containers
- [ ] Task reconciliation completes within 60 seconds
- [ ] Container reconnection successful within 60 seconds of network restoration
- [ ] Reconnected container achieves stable online status within 50 seconds
- [ ] Paused containers can be resumed successfully
- [ ] No data inconsistencies after container operations
- [ ] No zombie processes or orphaned tasks
- [ ] System performance returns to baseline after reconnection

## Monitoring Behavior
Same as CLS-001: Master monitors every 20s, requires 2 consecutive failures (~40s) before marking offline.

## Docker-Specific Validations
- [ ] Container health checks respond correctly
- [ ] Docker network isolation effective for testing
- [ ] Container logs accessible during and after test
- [ ] Resource usage reasonable during container operations
- [ ] No container restarts or crashes during test

## Failure Scenarios
- **Scenario**: Auto-detection fails to find containers
- **Symptoms**: Script reports no Crawlab containers found
- **Action**: Check Docker daemon, container names, and filters

- **Scenario**: Network disconnection doesn't isolate container
- **Symptoms**: Container still reachable after network disconnect
- **Action**: Verify Docker network configuration and connectivity

- **Scenario**: Container operations time out
- **Symptoms**: Docker commands hang or fail
- **Action**: Check Docker daemon health and container states

## Execution

### Automated (Docker Environment)
```bash
### Automated
```bash
# Execute via test-runner (auto-discovers runner script)
./test-runner.py --spec specs/infrastructure/INF-003-docker-container-node-disconnection-and-recovery.md

# Or specify script method explicitly
./test-runner.py --spec specs/infrastructure/INF-003-docker-container-node-disconnection-and-recovery.md --method script
```
```

### Manual Verification
```bash
# Check container status
docker ps --filter name=crawlab

# View container logs
docker logs crawlab_test_master
docker logs crawlab_test_worker_1

# Check container networks
docker network ls
docker inspect <network_name>
```

### Hybrid Execution
1. Use scripts for container management and monitoring
2. Use manual verification for Docker-specific checks
3. Use UI verification for cluster status validation

## Environment Variables
- `CRAWLAB_MASTER_URL`: Override auto-detected master URL
- `DOCKER_HOST`: Docker daemon connection (if remote)
- `CRAWLAB_API_TOKEN`: API authentication token

## Cleanup
- Ensure all containers reconnected: Verify container health status
- Stop test tasks: Clean up any remaining test tasks
- Reset container states: `docker-compose restart` (if needed)
- Clear test data: Remove test artifacts and temporary data
- Test-runner handles automatic cleanup of test environment

## Notes
- Test works with any Docker-based Crawlab deployment
- Container names are auto-discovered, no hardcoding required
- Network operations require appropriate Docker permissions
- Test can run from host or from within another container
- Supports both docker-compose and standalone container setups

## Dependencies
- **Docker CLI**: Required for container operations
- **Network permissions**: Ability to manage Docker networks
- **Container access**: Permission to pause/unpause containers
- **API access**: Network connectivity to Crawlab API

## History
- **Created**: 2025-09-17, Assistant - Docker-compatible test specification
- **Modified**: -
- **Last Run**: -