# PERF-003 - Long-Term Stability and Memory Leak Detection

## Metadata
- **Category**: performance
- **Priority**: critical
- **Complexity**: complex
- **Duration**: 24-48 hours
- **CI Skip**: true
- **Environment**: local/staging (production-like)
- **Dependencies**: crawlab-master, crawlab-worker(s), mongodb, redis, monitoring tools

## Scenario
This test validates Crawlab's stability over extended periods (24-48 hours) under continuous moderate load, specifically targeting memory leak detection and resource exhaustion issues. This addresses critical bug #1600 (memory leaks in long-running tasks causing system crashes after hours/days). The test monitors memory usage, goroutine counts, database connections, and other resources to detect slow leaks that only manifest during extended operation.

This is essential for production deployments where systems must run continuously for days/weeks without manual intervention. Slow memory leaks can cause:
- Gradual performance degradation
- Eventual OOM (Out Of Memory) kills
- Task execution failures after hours of operation
- Database connection pool exhaustion
- Worker node crashes

## Prerequisites
- Crawlab master node running with monitoring enabled
- At least 2 worker nodes for distributed testing
- MongoDB with connection pool monitoring enabled
- Redis with memory tracking enabled
- System monitoring tools available (Docker stats, pprof, etc.)
- Sufficient disk space for logs and metrics (5GB+)
- Stable network environment (avoid disconnections during test)
- Python environment with monitoring dependencies (psutil, matplotlib for visualization)
- Test should run unattended for 24-48 hours

## Test Steps

### Step 1: Establish Baseline Metrics
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step baseline`
**Expected**: Capture initial resource usage after system warmup
**Validation**: 
- System running for 30 minutes (warmup period)
- All components healthy and responsive
- Resource metrics collected:
  - Process RSS memory (master, workers)
  - Go heap memory (Alloc, Sys, TotalAlloc)
  - Goroutine count per process
  - MongoDB active connections
  - Redis memory usage
  - Open file descriptors
  - CPU usage (idle baseline)

**Baseline Thresholds** (reference):
```
Master:
  - RSS Memory: 200-400 MB
  - Goroutines: 50-150
  - MongoDB Connections: 10-30
  
Worker (per node):
  - RSS Memory: 150-300 MB
  - Goroutines: 30-100
  - MongoDB Connections: 5-15
```

### Step 2: Start Continuous Task Load
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step start-load`
**Expected**: Moderate task load running continuously
**Validation**: 
- Task creation rate: 10-20 tasks/minute (moderate, sustainable)
- Task duration: Mix of short (10s), medium (60s), long (5min)
- Task types: Mix of CPU-bound and I/O-bound tasks
- Distribution: Tasks evenly distributed across workers
- No task queue overflow (pending tasks < 100)

**Load Configuration**:
```yaml
task_creation_rate: 15/minute
task_duration_distribution:
  short_10s: 60%
  medium_60s: 30%
  long_300s: 10%
task_types:
  cpu_bound: 40%
  io_bound: 40%
  mixed: 20%
workers: 2
target_concurrent_tasks: 20-30
```

### Step 3: 24-Hour Monitoring (Primary Test)
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step monitor-24h`
**Expected**: System remains stable with no resource leaks
**Validation**: 
- **Sampling interval**: Every 5 minutes (288 samples over 24h)
- **Metrics tracked**:
  - Process RSS memory (trend analysis)
  - Go runtime metrics (heap, goroutines, GC stats)
  - Database connection counts (active, idle, total)
  - Redis memory usage and connection count
  - Open file descriptors
  - CPU usage (average, spikes)
  - Task success/failure rates
  - API response times
  
- **Alert conditions**:
  - Memory growth > 5% per hour after 2-hour warmup
  - Goroutine count increases > 10% per hour
  - Database connections grow beyond pool limits
  - File descriptor leaks (gradual increase)
  - Task failure rate > 5%
  - API response time degrades > 50% from baseline

**Monitoring Script Output** (every 5 minutes):
```
[2025-10-31 10:00:00] Monitoring Checkpoint #1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Master:
  RSS: 285 MB (+0.5% from baseline)
  Heap: 198 MB
  Goroutines: 127 (+2 from last check)
  MongoDB Conn: 24 (active: 8, idle: 16)
  
Worker-1:
  RSS: 223 MB (+1.2% from baseline)
  Heap: 145 MB
  Goroutines: 87 (+1 from last check)
  MongoDB Conn: 12 (active: 5, idle: 7)

Worker-2:
  RSS: 215 MB (+0.8% from baseline)
  Heap: 138 MB
  Goroutines: 82 (no change)
  MongoDB Conn: 11 (active: 4, idle: 7)

Tasks (last 5 min):
  Created: 75 | Completed: 73 | Failed: 2
  Success rate: 97.3%
  Avg duration: 48s

Database:
  MongoDB connections: 47/200 (23.5%)
  Redis memory: 85 MB
  Slow queries: 0

Health: ✅ HEALTHY | Trend: ⚠️ Monitor (slight goroutine increase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Memory Leak Detection Analysis
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step analyze-leaks`
**Expected**: Identify any memory leaks or resource growth
**Validation**: 
- **Linear regression** on memory usage over time
  - Slope < 5 MB/hour = acceptable (GC variance)
  - Slope 5-20 MB/hour = warning (slow leak)
  - Slope > 20 MB/hour = critical leak
  
- **Goroutine leak detection**
  - Stable goroutine count (±10%) = healthy
  - Gradual increase > 10%/hour = leak
  - Identify goroutine types using pprof dumps
  
- **Connection leak detection**
  - Database connections should remain stable
  - No gradual pool exhaustion
  - Check for unclosed connections
  
- **Pattern analysis**
  - Identify correlation with task types
  - Check if leaks occur during specific operations
  - Compare master vs worker leak patterns

**Leak Detection Algorithm**:
```python
def detect_memory_leak(samples):
    # Skip first 2 hours (warmup)
    stable_samples = samples[24:]  # 24 samples = 2 hours
    
    # Linear regression
    slope, intercept, r_value = linear_regression(stable_samples)
    
    # Calculate hourly growth rate
    hourly_growth_mb = slope * 12  # 12 samples per hour
    
    # Determine severity
    if hourly_growth_mb < 5:
        return "HEALTHY", hourly_growth_mb
    elif hourly_growth_mb < 20:
        return "WARNING", hourly_growth_mb
    else:
        return "CRITICAL", hourly_growth_mb
```

### Step 5: Resource Cleanup Validation
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step cleanup-validation`
**Expected**: Memory returns to baseline after stopping tasks
**Validation**: 
- Stop all task creation
- Wait for running tasks to complete (up to 10 minutes)
- Force GC collection (send SIGUSR1 or API call if available)
- Wait 10 minutes for cleanup
- Capture final metrics
- Compare with baseline:
  - Memory should return to baseline ±20%
  - Goroutines should drop to idle levels (±10% of baseline)
  - All connections released to pool
  - No resource accumulation

**Cleanup Success Criteria**:
```
After 10-minute idle period:
  - RSS Memory: Within 20% of baseline
  - Goroutines: Within 10% of baseline
  - DB Connections: Active = 0-2, total within pool
  - File Descriptors: Within 5% of baseline
  - No lingering task processes
```

### Step 6: 48-Hour Extended Test (Optional)
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step monitor-48h`
**Expected**: Extended validation for slower leaks
**Validation**: 
- Same as 24-hour test but double duration
- Catches very slow leaks (e.g., 2-5 MB/hour)
- Validates multi-day stability
- Recommended for pre-release validation
- Can be run in CI as nightly job

### Step 7: Generate Comprehensive Report
**Method**: script
**Command**: `uv run python runners/performance/PERF_003_long_term_stability.py --step generate-report`
**Expected**: Detailed analysis with visualizations
**Validation**: 
- **Report includes**:
  - Executive summary (pass/fail, key findings)
  - Memory growth analysis (graphs, regression)
  - Goroutine trend analysis
  - Connection pool stability
  - Task execution statistics
  - Identified bottlenecks or leaks
  - Comparison with previous runs
  - Actionable recommendations
  
- **Visualizations** (PNG/SVG):
  - Memory usage over time (all processes)
  - Goroutine count trends
  - Database connection pool usage
  - Task throughput over time
  - CPU usage heatmap
  
- **Export formats**:
  - JSON (raw metrics for analysis)
  - CSV (time-series data)
  - HTML (interactive report)
  - PDF (executive summary)

## Success Criteria

### 24-Hour Test
- [ ] System runs continuously for 24 hours without crashes
- [ ] Memory growth < 5% per hour after 2-hour warmup period
- [ ] RSS memory increase < 120 MB total over 24 hours
- [ ] Goroutine count stable (±10%) after warmup
- [ ] No goroutine leaks detected (no unbounded growth)
- [ ] Database connection count stable (no pool exhaustion)
- [ ] MongoDB connections < 80% of pool limit at all times
- [ ] Redis memory growth < 50 MB over 24 hours
- [ ] No "out of memory" errors in logs
- [ ] No task execution failures due to resource exhaustion
- [ ] Task success rate > 95% throughout test
- [ ] API remains responsive (p95 latency < 2s)
- [ ] No file descriptor leaks detected
- [ ] System responsive after 24 hours (health check < 1s)

### Cleanup Validation
- [ ] Memory returns to baseline ±20% after 10-minute idle
- [ ] Goroutine count drops to idle level ±10%
- [ ] All database connections returned to pool
- [ ] Active connections < 3 after cleanup
- [ ] No zombie processes or orphaned tasks
- [ ] File descriptors released properly

### 48-Hour Test (Optional)
- [ ] Same criteria as 24-hour test
- [ ] Validates slower leaks (< 5 MB/hour)
- [ ] Multi-day stability confirmed
- [ ] No degradation in second 24-hour period

### Report Quality
- [ ] All metrics collected successfully (>95% samples)
- [ ] Visualizations generated correctly
- [ ] Leak detection algorithm runs without errors
- [ ] Recommendations are actionable
- [ ] Report exported in all formats

## Failure Scenarios

### Scenario: Memory Leak Detected
- **Symptoms**: Linear memory growth > 20 MB/hour, eventual OOM kill
- **Action**: 
  1. Stop test and capture pprof heap dump
  2. Analyze heap profile to identify leak source
  3. Check for unclosed resources (files, connections, channels)
  4. Review goroutine dumps for stuck routines
  5. File bug report with pprof data
- **Recovery**: Fix leak, restart test from baseline

### Scenario: Goroutine Leak
- **Symptoms**: Goroutine count increases unbounded, CPU usage rises
- **Action**:
  1. Capture goroutine pprof dump
  2. Identify stuck or leaked goroutines
  3. Check for missing context cancellation
  4. Review channel operations (blocked sends/receives)
  5. Check for missing WaitGroup.Done() calls
- **Recovery**: Fix goroutine management, restart test

### Scenario: Database Connection Pool Exhaustion
- **Symptoms**: "too many connections" errors, task failures, API timeouts
- **Action**:
  1. Check MongoDB connection logs
  2. Identify unclosed connections
  3. Review connection lifecycle in code
  4. Check for connection leaks in error paths
  5. Verify proper defer statements for cleanup
- **Recovery**: Increase pool size temporarily, fix leaks, restart

### Scenario: Test Interruption (Crash, Network)
- **Symptoms**: Process crash, network disconnection, system reboot
- **Action**:
  1. Capture all available metrics before restart
  2. Analyze crash logs/core dumps
  3. Resume from checkpoint if possible
  4. Otherwise, restart test (document interruption)
- **Recovery**: Fix underlying issue, restart full test

### Scenario: Slow Performance Degradation
- **Symptoms**: API latency increases over time, task throughput drops
- **Action**:
  1. Check database query performance over time
  2. Analyze database index efficiency
  3. Review disk I/O and fragmentation
  4. Check for memory pressure causing swapping
  5. Profile hot code paths for optimization
- **Recovery**: Optimize queries, rebuild indexes, increase resources

### Scenario: False Positive Memory "Leak"
- **Symptoms**: Memory increases but plateaus, normal GC behavior
- **Action**:
  1. Check if memory stabilizes after warmup
  2. Force GC and observe if memory drops
  3. Compare heap vs RSS (may be fragmentation)
  4. Review Go GC settings (GOGC, GOMEMLIMIT)
  5. Differentiate leak vs working set growth
- **Recovery**: Adjust thresholds, continue monitoring

## Execution

### Automated (Recommended)
```bash
# Full 24-hour test with monitoring
cd crawlab-test
uv run python runners/performance/PERF_003_long_term_stability.py --duration 24h --full

# Quick validation run (2 hours for development)
uv run python runners/performance/PERF_003_long_term_stability.py --duration 2h --quick-test

# 48-hour extended test
uv run python runners/performance/PERF_003_long_term_stability.py --duration 48h --extended

# Resume interrupted test from checkpoint
uv run python runners/performance/PERF_003_long_term_stability.py --resume --checkpoint /path/to/checkpoint.json

# Custom monitoring intervals
uv run python runners/performance/PERF_003_long_term_stability.py --duration 24h --sample-interval 300

# CI mode (nightly run)
uv run ./cli.py --spec PERF-003 --ci --timeout 86400  # 24 hours
```

### Via Test CLI
```bash
# Standard 24-hour test
./cli.py --spec PERF-003

# With custom duration
./cli.py --spec PERF-003 --params duration=48h
```

### Manual Monitoring
```bash
# For manual monitoring during test
# Terminal 1: Monitor master
watch -n 300 'docker stats crawlab-master --no-stream; echo "---"; curl -s http://localhost:8080/debug/vars | jq .runtime'

# Terminal 2: Monitor workers
watch -n 300 'docker stats crawlab-worker-1 crawlab-worker-2 --no-stream'

# Terminal 3: Monitor database
watch -n 300 'mongo admin --eval "db.serverStatus().connections"'

# Terminal 4: Monitor tasks
watch -n 60 'curl -s http://localhost:8080/api/tasks/stats | jq'
```

## Cleanup
```bash
# Stop monitoring and task creation
uv run python runners/performance/PERF_003_long_term_stability.py --stop

# Wait for running tasks to complete
uv run python runners/performance/PERF_003_long_term_stability.py --wait-tasks --timeout 600

# Clean up test data
uv run python crawlab_test/helpers/infrastructure/cleanup.py --test-data --preserve-metrics

# Archive metrics for historical comparison
uv run python runners/performance/PERF_003_long_term_stability.py --archive-metrics

# Reset environment
docker-compose restart
```

## Expected Test Outputs

### Monitoring Dashboard (Real-time)
```
🔬 Crawlab Long-Term Stability Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Test Status: RUNNING (12h 35m / 24h)
🎯 Health: ✅ HEALTHY | Trend: ✅ STABLE

📈 Memory Trends:
  Master:   285 MB → 298 MB (+4.6% | +1.03 MB/h) ✅
  Worker-1: 223 MB → 235 MB (+5.4% | +0.95 MB/h) ✅
  Worker-2: 215 MB → 228 MB (+6.0% | +1.03 MB/h) ✅
  
🧵 Goroutines:
  Master:   127 → 132 (+3.9%) ✅ STABLE
  Worker-1: 87 → 89 (+2.3%) ✅ STABLE
  Worker-2: 82 → 85 (+3.7%) ✅ STABLE

💾 Connections:
  MongoDB: 47/200 (23.5%) ✅ HEALTHY
  Redis: 18/100 (18.0%) ✅ HEALTHY

📊 Task Statistics:
  Total: 10,785 | Success: 10,512 (97.5%) ✅
  Running: 28 | Pending: 12 | Failed: 273
  Avg Success Rate (last hour): 98.2%

⏱️  Performance:
  API p50: 145ms | p95: 1.2s | p99: 2.3s ✅
  Task Throughput: 14.3 tasks/min (target: 15)

🔔 Alerts: None
📸 Next Checkpoint: 5 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Final Report (Summary)
```json
{
  "test_id": "PERF-003",
  "test_type": "long-term-stability",
  "duration_hours": 24,
  "start_time": "2025-10-31T00:00:00Z",
  "end_time": "2025-11-01T00:00:00Z",
  "test_result": "PASS",
  "overall_health": "HEALTHY",
  
  "memory_analysis": {
    "master": {
      "baseline_mb": 285,
      "final_mb": 305,
      "growth_mb": 20,
      "growth_percent": 7.0,
      "hourly_rate_mb": 0.83,
      "status": "PASS",
      "leak_detected": false
    },
    "workers": {
      "avg_baseline_mb": 219,
      "avg_final_mb": 238,
      "avg_growth_mb": 19,
      "avg_hourly_rate_mb": 0.79,
      "status": "PASS",
      "leak_detected": false
    }
  },
  
  "goroutine_analysis": {
    "master": {
      "baseline": 127,
      "final": 135,
      "growth_percent": 6.3,
      "status": "PASS",
      "leak_detected": false
    },
    "workers": {
      "avg_baseline": 84.5,
      "avg_final": 89,
      "avg_growth_percent": 5.3,
      "status": "PASS",
      "leak_detected": false
    }
  },
  
  "connection_analysis": {
    "mongodb": {
      "avg_connections": 48,
      "max_connections": 63,
      "pool_limit": 200,
      "pool_utilization_percent": 31.5,
      "status": "PASS",
      "leak_detected": false
    },
    "redis": {
      "avg_memory_mb": 87,
      "max_memory_mb": 112,
      "growth_mb": 12,
      "status": "PASS"
    }
  },
  
  "task_statistics": {
    "total_created": 21580,
    "total_completed": 21045,
    "total_failed": 535,
    "success_rate_percent": 97.5,
    "avg_tasks_per_minute": 14.9,
    "status": "PASS"
  },
  
  "performance_metrics": {
    "api_latency_p95_ms": 1250,
    "api_latency_p99_ms": 2340,
    "degradation_percent": 8.5,
    "status": "PASS"
  },
  
  "cleanup_validation": {
    "memory_returned_to_baseline": true,
    "goroutines_returned_to_baseline": true,
    "connections_released": true,
    "status": "PASS"
  },
  
  "issues_found": [],
  
  "recommendations": [
    "System is stable for 24+ hour operation",
    "Memory growth is within acceptable limits (GC variance)",
    "No resource leaks detected",
    "Production deployment approved"
  ]
}
```

## Notes

### Test Philosophy
- **Patience is key**: Slow leaks only appear over hours/days
- **Moderate load**: Not stress testing, but realistic usage
- **Continuous monitoring**: Regular sampling critical for trend detection
- **Baseline matters**: Must establish stable baseline before analysis
- **Cleanup validation**: Ensures leaks vs normal working set growth

### Resource Monitoring Tools
- **Go pprof**: Memory and goroutine profiling
- **Docker stats**: Container resource usage
- **psutil (Python)**: Cross-platform process monitoring
- **MongoDB profiling**: Slow query and connection tracking
- **Custom metrics**: Exposed via debug/vars endpoint

### Leak Detection Science
Memory can grow for legitimate reasons:
1. **Working set growth**: More data in caches (acceptable)
2. **GC variance**: Memory fluctuates between GC cycles (normal)
3. **Warmup period**: Initial allocation stabilizes (expected)
4. **Actual leaks**: Unbounded growth over time (critical)

**Differentiation**:
- Leaks show **linear unbounded growth**
- Working set growth **plateaus**
- Use regression analysis to distinguish

### Go-Specific Considerations
- **GOGC**: Default 100 (GC when heap doubles)
- **GOMEMLIMIT**: Soft memory limit (Go 1.19+)
- **Heap vs RSS**: RSS includes stack, fragmentation
- **Goroutine leaks**: Check for missing context cancellation
- **Channel leaks**: Unbuffered sends/receives can block

### Production Correlation
Test conditions should match production:
- Task types and durations
- Concurrent task count
- Database query patterns
- API request rates
- Worker node count

### Historical Comparison
Track metrics over time:
- Compare with previous releases
- Detect regressions early
- Establish performance baselines
- Guide optimization efforts

## Implementation Status
- **Specification**: ✅ Complete (2025-10-31)
- **Test Runner**: ⏳ Pending
- **Monitoring Infrastructure**: ⏳ Pending
- **Visualization Tools**: ⏳ Pending
- **CI Integration**: ⏳ Pending

## History
- **Created**: 2025-10-31, AI Agent (based on test-coverage-gaps.md analysis)
- **Modified**: -
- **Last Run**: -
