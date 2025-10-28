# SCH-002 - Task Execution Pressure Test

## Metadata
- **Category**: scheduler
- **Priority**: high
- **Complexity**: moderate
- **Duration**: 15-60 minutes (depends on load level)
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker(s), mongodb, redis

## Scenario
This test validates Crawlab's robustness and performance under heavy concurrent task execution. It measures system behavior when creating and executing large numbers of tasks simultaneously, identifying bottlenecks in task scheduling, resource management, and overall system stability. This is critical for production deployments that need to handle high task volumes and ensures the system can scale horizontally without degradation.

The test creates configurable task loads (100 to 5000+ tasks) and monitors:
- Task creation throughput and API response times
- Task scheduling and assignment efficiency
- Worker node resource utilization
- Database performance under concurrent writes/reads
- Error rates and failure recovery
- System stability over sustained load

## Prerequisites
- Crawlab master node running and accessible at http://localhost:8080
- At least 1 worker node connected (multiple workers recommended for distributed testing)
- MongoDB accessible and properly configured
- Redis accessible for task queue management
- Sufficient system resources (CPU, memory, disk I/O)
- Python environment with test dependencies installed
- Valid admin credentials (admin:admin default)

## Test Steps

### Step 1: Environment Verification
**Method**: script
**Command**: `cd crawlab-test && python runners/scheduler/SCH-002_task_execution_pressure_test.py --verify`
**Expected**: 
- Master node is running and responsive
- Worker nodes are connected and active
- Database connections are healthy
- Test environment is ready

**Validation**: 
- API health check returns 200 OK
- At least 1 worker node listed
- MongoDB connection successful
- Redis accessible

### Step 2: Light Load Test (Baseline)
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --load light`
**Expected**: 
- Create 100 tasks successfully
- All tasks execute without errors
- Normal system resource usage
- Establish performance baseline

**Validation**:
- Task creation success rate: 100%
- Task execution success rate: >95%
- Average API response time: <500ms
- No system errors or panics

### Step 3: Medium Load Test
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --load medium`
**Expected**: 
- Create 500 tasks successfully
- High concurrent execution (based on worker count)
- Acceptable system resource usage
- Stable performance

**Validation**:
- Task creation success rate: >98%
- Task execution success rate: >90%
- Average API response time: <1s
- Worker CPU usage: <80%
- Master node stable

### Step 4: Heavy Load Test
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy`
**Expected**: 
- Create 1000 tasks successfully
- System handles high concurrency
- Task queue processes efficiently
- No critical failures

**Validation**:
- Task creation success rate: >95%
- Task execution success rate: >85%
- Average API response time: <2s
- Database connection pool stable
- No task queue overflow

### Step 5: Extreme Load Test (Optional)
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --load extreme`
**Expected**: 
- Create 5000+ tasks successfully
- System reaches capacity limits
- Identify bottlenecks
- Graceful degradation

**Validation**:
- Task creation success rate: >90%
- Task execution success rate: >80%
- System remains responsive
- Error handling works correctly
- Recovery after load completes

### Step 6: Sustained Load Test (Stability)
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --sustained --duration 3600`
**Expected**: 
- Maintain constant task creation rate for 1 hour
- System remains stable over time
- No memory leaks or resource exhaustion
- Consistent performance

**Validation**:
- Task throughput remains stable (±10%)
- Memory usage plateaus (no leaks)
- Database performance consistent
- No gradual degradation

### Step 7: Results Analysis and Reporting
**Method**: script
**Command**: `python runners/scheduler/SCH-002_task_execution_pressure_test.py --analyze`
**Expected**: 
- Generate comprehensive performance report
- Identify bottlenecks and failure patterns
- Compare results across load levels
- Provide recommendations

**Validation**:
- Report includes all key metrics
- Bottlenecks clearly identified
- Recommendations are actionable
- Results saved for historical comparison

## Success Criteria

### Light Load (100 tasks)
- [x] Task creation success rate: 100%
- [x] Task execution success rate: >95%
- [x] Average API response time: <500ms
- [x] No system errors

### Medium Load (500 tasks)
- [x] Task creation success rate: >98%
- [x] Task execution success rate: >90%
- [x] Average API response time: <1s
- [x] System stable throughout

### Heavy Load (1000 tasks)
- [x] Task creation success rate: >95%
- [x] Task execution success rate: >85%
- [x] Average API response time: <2s
- [x] No critical failures

### Extreme Load (5000+ tasks)
- [x] Task creation success rate: >90%
- [x] Task execution success rate: >80%
- [x] System recovers after load
- [x] Graceful error handling

### Sustained Load (1 hour)
- [x] Throughput remains stable (±10%)
- [x] No memory leaks detected
- [x] Database performance consistent
- [x] System remains responsive

## Failure Scenarios

### Scenario: Database Connection Pool Exhaustion
- **Symptoms**: "Too many connections" errors, task creation timeouts, 500 errors from API
- **Action**: Check MongoDB connection pool settings, increase max connections, optimize query patterns
- **Recovery**: Reduce concurrent task creation rate, scale database resources

### Scenario: Task Queue Overflow
- **Symptoms**: Tasks stuck in pending state, scheduler lag increases, Redis memory pressure
- **Action**: Verify worker node capacity, check task queue depth, review scheduling algorithm
- **Recovery**: Add more worker nodes, optimize task priority distribution

### Scenario: Worker Node Resource Exhaustion
- **Symptoms**: Workers crash or become unresponsive, tasks fail with timeout errors, high CPU/memory
- **Action**: Monitor worker resource usage, adjust concurrent task limits per worker, scale horizontally
- **Recovery**: Restart affected workers, add capacity, tune worker configuration

### Scenario: Master Node CPU Saturation
- **Symptoms**: API response times increase dramatically, task scheduling slows, system becomes sluggish
- **Action**: Profile master node performance, identify hot code paths, optimize database queries
- **Recovery**: Scale master node resources, optimize critical paths, reduce unnecessary processing

### Scenario: Memory Leak Under Sustained Load
- **Symptoms**: Memory usage grows continuously, eventual OOM kills, performance degrades over time
- **Action**: Profile memory usage, identify leak sources, check goroutine leaks, review resource cleanup
- **Recovery**: Restart affected components, fix memory leaks, implement proper cleanup

### Scenario: API Rate Limiting or Timeout
- **Symptoms**: 429 Too Many Requests, connection timeouts, task creation fails intermittently
- **Action**: Check rate limit configuration, review timeout settings, adjust concurrent request limits
- **Recovery**: Reduce request rate, increase timeout values, implement exponential backoff

## Execution

### Automated (Recommended)
```bash
# Full pressure test suite with all load levels
cd crawlab-test
python runners/scheduler/SCH-002_task_execution_pressure_test.py --full-suite

# Specific load level
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy

# Sustained stability test (1 hour)
python runners/scheduler/SCH-002_task_execution_pressure_test.py --sustained --duration 3600

# Custom configuration
python runners/scheduler/SCH-002_task_execution_pressure_test.py --tasks 2000 --workers 20 --batch-size 50

# With monitoring and detailed logging
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy --monitor --verbose

# CI mode with timeout
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load medium --ci --timeout 1800
```

### Via Test CLI
```bash
# Using the unified test CLI
./cli.py --spec SCH-002 --backend script

# With custom parameters
./cli.py --spec SCH-002 --params load=heavy,monitor=true
```

### Manual
1. Open Crawlab UI in browser
2. Navigate to Tasks page
3. Monitor system resources (Docker stats, database metrics)
4. Manually create large batch of tasks via UI
5. Observe task scheduling and execution patterns
6. Verify system stability and error handling
7. Check logs for errors or performance issues

## Cleanup
```bash
# Automatic cleanup after test
python runners/scheduler/SCH-002_task_execution_pressure_test.py --cleanup

# Manual cleanup if needed
# Delete test tasks
curl -X DELETE http://localhost:8080/api/tasks -H "Authorization: Bearer $TOKEN" -d '{"ids": [...]}'

# Delete test spiders
curl -X DELETE http://localhost:8080/api/spiders -H "Authorization: Bearer $TOKEN" -d '{"ids": [...]}'

# Verify cleanup
python runners/scheduler/SCH-002_task_execution_pressure_test.py --verify-cleanup
```

## Expected Test Outputs

### Performance Report
```json
{
  "test_id": "SCH-002",
  "timestamp": "2025-10-28T10:30:00Z",
  "environment": {
    "master_nodes": 1,
    "worker_nodes": 3,
    "mongodb_version": "7.0",
    "crawlab_version": "0.7.0"
  },
  "load_tests": {
    "light": {
      "total_tasks": 100,
      "created": 100,
      "creation_success_rate": 100.0,
      "creation_time_sec": 8.5,
      "tasks_per_second": 11.8,
      "execution_success_rate": 98.0,
      "avg_api_response_ms": 245,
      "max_api_response_ms": 680,
      "errors": []
    },
    "heavy": {
      "total_tasks": 1000,
      "created": 982,
      "creation_success_rate": 98.2,
      "creation_time_sec": 125.3,
      "tasks_per_second": 7.8,
      "execution_success_rate": 89.5,
      "avg_api_response_ms": 1250,
      "max_api_response_ms": 3400,
      "errors": ["timeout", "connection_reset"]
    }
  },
  "resource_metrics": {
    "master_cpu_max": 75.2,
    "master_memory_mb": 2048,
    "worker_avg_cpu": 62.5,
    "database_connections": 127
  },
  "bottlenecks_identified": [
    "Database query performance degrades above 800 concurrent tasks",
    "Master node CPU becomes saturated around 1000 tasks/min creation rate",
    "Task queue depth grows linearly above 5000 tasks"
  ],
  "recommendations": [
    "Consider horizontal scaling for loads exceeding 500 concurrent tasks",
    "Optimize database indexes for task status queries",
    "Implement task batching for bulk operations",
    "Add more worker nodes to increase execution capacity"
  ],
  "test_result": "PASS"
}
```

### Real-time Monitoring Output
```
🔥 Crawlab Pressure Test - Heavy Load
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Creating 1000 tasks in batches of 100...
  ✅ Batch 1: 100/100 tasks created (8.2s)
  ✅ Batch 2: 100/100 tasks created (9.1s)
  ✅ Batch 3: 98/100 tasks created (12.5s) ⚠️ 2 errors
  ...
  
📊 Task Creation Summary:
  ✅ Tasks created: 982/1000 (98.2%)
  ❌ Errors: 18
  ⏱️  Total time: 125.3s
  📈 Tasks/second: 7.8

⏳ Monitoring task execution...
  Progress: [████████████░░░░░░░░] 60% (589/982 completed)
  Running: 87 | Pending: 156 | Errors: 11
  Elapsed: 3:45 | Est. remaining: 2:30

📊 Final Results:
  ✅ Completed: 879 (89.5%)
  ❌ Errors: 103 (10.5%)
  ⏱️  Total execution: 6:15
  
✅ Test PASSED: Heavy load handled within acceptable thresholds
```

## Notes
- This test requires sufficient system resources; adjust load levels based on available capacity
- For distributed testing, ensure multiple worker nodes are available
- Monitor system resources (CPU, memory, disk I/O) during test execution
- Large task volumes may require adjusting MongoDB connection pool settings
- Test duration increases significantly with extreme load levels (5000+ tasks)
- Consider running sustained load tests during off-peak hours
- Results are highly dependent on hardware specifications and configuration
- Baseline performance metrics should be established in a controlled environment first
- For production capacity planning, run tests with realistic task payloads and durations

## Implementation Status
- **Specification**: ✅ Complete (2025-10-28)
- **Test Runner**: 🚧 In Progress
- **CI Integration**: ⏳ Pending
- **Monitoring Dashboard**: ⏳ Pending

## History
- **Created**: 2025-10-28, GitHub Copilot - Initial specification for task execution pressure testing
- **Modified**: -
- **Last Run**: -