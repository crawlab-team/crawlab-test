# REL-006 - Graceful Shutdown and Process Termination

## Metadata
- **Category**: reliability
- **Priority**: critical
- **Complexity**: moderate
- **Duration**: 10-15 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, mongodb, redis

## Scenario
This test validates that Crawlab components (master and worker nodes) shut down gracefully without hanging processes, and that task cancellation properly terminates running processes. This addresses critical bugs #1609 (tasks not properly killed on cancellation) and #1584 (master can't stop cleanly). Proper shutdown is essential for production deployments, container orchestration, and preventing resource leaks.

## Prerequisites
- Crawlab master node running and accessible
- At least 1 worker node connected and active
- MongoDB and Redis accessible
- Test spiders available for execution
- Ability to send signals (SIGTERM) to processes
- Process monitoring tools available (ps, pgrep, or equivalent)

## Test Steps

### Step 1: Verify Initial System State
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step verify-initial`
**Expected**: All components healthy and responsive
**Validation**: 
- Master API returns 200 on health endpoint
- Worker nodes show as "online"
- No zombie processes from previous runs
- Process tree clean (master, workers identifiable)

### Step 2: Task Cancellation - Process Termination
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step task-cancellation`
**Expected**: Task cancellation kills process within 5 seconds
**Validation**: 
- Create long-running task (60+ seconds)
- Record task process PID
- Call cancel API: `POST /api/tasks/{id}/cancel`
- Verify API returns success (200/204)
- Verify task status changes to "cancelled" within 2s
- **Critical**: Verify process PID no longer exists within 5s
- Verify no child processes remain
- Verify worker resources released

**Steps Detail**:
1. Create spider with long-running script (sleep 60s)
2. Start task execution via API
3. Wait 5s for task to be running
4. Get task process PID (via API or worker inspection)
5. Send cancel request
6. Poll process existence every 500ms for up to 5s
7. Confirm PID gone and no children

### Step 3: Worker Graceful Shutdown
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step worker-shutdown`
**Expected**: Worker stops cleanly within 20 seconds
**Validation**: 
- Start worker with 2 running tasks (one short, one medium)
- Record worker process PID
- Send SIGTERM to worker process
- Verify worker:
  - Stops accepting new tasks immediately
  - Allows running tasks to finish (short task) or terminates them (medium task)
  - Updates task statuses correctly in database
  - Closes gRPC connection gracefully
  - Exits within 20 seconds
- Verify no zombie processes remain
- Verify master detects worker offline within 60s

**Steps Detail**:
1. Start 2 tasks on worker (10s and 30s duration)
2. Wait 3s for tasks to be running
3. Get worker PID
4. Send SIGTERM signal
5. Monitor: Task status updates, process exit, gRPC disconnection
6. Verify clean exit and no orphaned processes

### Step 4: Master Graceful Shutdown
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step master-shutdown`
**Expected**: Master stops cleanly within 30 seconds
**Validation**: 
- Start master with active API requests and tasks
- Record master process PID and component PIDs
- Send SIGTERM to master process
- Verify shutdown sequence (order critical):
  1. HTTP server stops accepting new requests (within 1s)
  2. In-flight API requests complete (up to 10s grace)
  3. Task services finish current operations (up to 10s)
  4. Database connections closed properly
  5. gRPC server stops last (after dependent services)
  6. Process exits within 30s total
- Verify no "connection refused" errors in logs
- Verify no hanging processes
- Verify database state consistent

**Steps Detail**:
1. Start master with 1-2 active tasks
2. Make long API request (async, 5s duration)
3. Get master PID
4. Send SIGTERM
5. Monitor shutdown sequence timing and order
6. Check logs for errors
7. Verify all components stopped

### Step 5: Zombie Process Detection
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step zombie-detection`
**Expected**: No zombie processes after any shutdown
**Validation**: 
- After each shutdown test, scan for zombie processes
- Check for processes in 'Z' state (Linux/macOS)
- Verify no orphaned Crawlab processes
- Verify no orphaned task execution processes
- Report any zombies with parent PID and state

### Step 6: Rapid Shutdown Stress Test
**Method**: script
**Command**: `uv run python runners/reliability/REL_006_graceful_shutdown.py --step rapid-shutdown`
**Expected**: System handles rapid start/stop cycles
**Validation**: 
- Start master and worker
- Wait 5s for initialization
- Send SIGTERM to both
- Wait for clean exit
- Repeat 3 times
- Verify: Each cycle completes cleanly, no accumulated zombies, startup time stable

## Success Criteria
- [ ] Task cancellation API returns success within 2 seconds
- [ ] Cancelled task process terminates within 5 seconds of API call
- [ ] No child processes remain after task cancellation
- [ ] Worker shutdown completes within 20 seconds of SIGTERM
- [ ] Worker updates all task statuses before exit
- [ ] Master shutdown completes within 30 seconds of SIGTERM
- [ ] Master HTTP server stops before gRPC server
- [ ] No "connection refused" or "broken pipe" errors in logs
- [ ] No zombie processes after any shutdown operation
- [ ] Database state remains consistent after shutdown
- [ ] Rapid shutdown cycles (3x) complete without errors
- [ ] gRPC connections closed gracefully (no abrupt disconnects)

## Failure Scenarios
- **Scenario**: Process doesn't exit after SIGTERM
- **Symptoms**: Process still running after timeout, requires SIGKILL
- **Action**: Check shutdown handler registration, signal handling, blocked operations

- **Scenario**: Task process survives cancellation
- **Symptoms**: Process PID still exists 5+ seconds after cancel API
- **Action**: Check task handler kill logic, process group termination, PGID handling

- **Scenario**: Zombie processes remain
- **Symptoms**: Processes in 'Z' state, `ps aux | grep defunct`
- **Action**: Check parent process wait() calls, SIGCHLD handling, process reaping

- **Scenario**: Shutdown hangs
- **Symptoms**: Process doesn't exit, high CPU, blocked I/O
- **Action**: Check for deadlocks, blocked channels, unclosed connections

- **Scenario**: gRPC errors during shutdown
- **Symptoms**: "connection refused", "transport closing" errors
- **Action**: Verify shutdown order - gRPC must stop after dependent services

## Execution

### Automated
```bash
# Run complete test suite
uv run python runners/reliability/REL_006_graceful_shutdown.py --all

# Run individual test steps
uv run python runners/reliability/REL_006_graceful_shutdown.py --step task-cancellation
uv run python runners/reliability/REL_006_graceful_shutdown.py --step worker-shutdown
uv run python runners/reliability/REL_006_graceful_shutdown.py --step master-shutdown

# CI mode (strict timing, detailed logging)
uv run ./cli.py --spec REL-006 --ci --timeout 15
```

### Manual
1. Start Crawlab master and worker
2. Create test spider with long-running task (60s sleep)
3. Start task, get PID: `ps aux | grep [task-command]`
4. Call cancel API via curl or UI
5. Monitor process: `watch -n 0.5 'ps -p [PID]'`
6. Verify process disappears within 5s
7. Send SIGTERM to worker: `kill -TERM [worker-pid]`
8. Monitor shutdown: `time watch 'ps -p [worker-pid]'`
9. Verify clean exit within 20s
10. Repeat for master with 30s timeout

## Cleanup
```bash
# Kill any remaining processes
pkill -f crawlab-master
pkill -f crawlab-worker

# Clean zombie processes (if any)
ps aux | grep defunct | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Clear test data
uv run python crawlab_test/helpers/infrastructure/cleanup.py --test-data

# Restart clean environment
docker-compose down && docker-compose up -d
```

## Notes

### Signal Handling Best Practices
- Use SIGTERM (15) for graceful shutdown, not SIGKILL (9)
- Components should register signal handlers on startup
- Shutdown order matters: HTTP → Services → gRPC → Database
- Use context cancellation for coordinated shutdown
- Set reasonable timeouts (avoid indefinite waits)

### Process Management
- Task processes should be in their own process group (PGID)
- Use `kill -TERM -[PGID]` to kill entire process tree
- Parent processes must wait() for children to prevent zombies
- Monitor for orphaned processes (PPID = 1)

### Test Environment Considerations
- Docker containers handle signals differently (use `docker stop --time`)
- CI environments may have different signal delivery timing
- Process PID recycling can cause false positives (check start time too)
- macOS vs Linux differences in process management

### Known Issues
- Issue #1609: Task cancellation doesn't kill process (fixed, needs validation)
- Issue #1584: Master shutdown hangs due to gRPC ordering (fixed, needs validation)
- Workers may take up to 60s to be detected as offline (master monitoring interval)

### Implementation Notes
- Test runner should use Python `signal` module for SIGTERM
- Use `psutil` library for cross-platform process monitoring
- Record timestamps for all operations to verify timeouts
- Capture logs for debugging failed shutdowns
- Use `subprocess.Popen` with `preexec_fn=os.setsid` for process groups

## History
- **Created**: 2025-10-31, AI Agent (based on test-coverage-gaps.md)
- **Modified**: -
- **Last Run**: -
