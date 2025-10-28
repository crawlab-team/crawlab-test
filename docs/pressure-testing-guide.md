# Pressure Testing Guide

Quick reference for running pressure tests on Crawlab.

## Test Specification

**Spec ID**: SCH-002  
**Location**: `specs/scheduler/SCH-002-task-execution-pressure-test.md`  
**Runner**: `runners/scheduler/SCH-002_task_execution_pressure_test.py`

## Quick Start

```bash
# Navigate to test directory
cd crawlab-test

# Activate virtual environment
source .venv/bin/activate

# Run light load test (100 tasks)
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load light

# Run heavy load test (1000 tasks)
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy

# Run via CLI
./cli.py --spec SCH-002
```

## Load Levels

| Level    | Tasks | Workers | Batch Size | Duration | Use Case                  |
|----------|-------|---------|------------|----------|---------------------------|
| light    | 100   | 5       | 20         | ~2 min   | Quick smoke test          |
| medium   | 500   | 10      | 50         | ~5 min   | Moderate load validation  |
| heavy    | 1000  | 20      | 100        | ~10 min  | Production capacity test  |
| extreme  | 5000  | 50      | 100        | ~30 min  | Stress test/limit finding |

## Usage Examples

```bash
# Verify environment only
python runners/scheduler/SCH-002_task_execution_pressure_test.py --verify

# Run without monitoring (faster)
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load medium --no-monitor

# Verbose output with results saved
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy --verbose --output results.json

# Custom API endpoint
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load light --base-url http://production:8080/api
```

## Monitoring During Tests

```bash
# Terminal 1: Run test
python runners/scheduler/SCH-002_task_execution_pressure_test.py --load heavy

# Terminal 2: Monitor resources
docker stats crawlab-master crawlab-worker-1

# Terminal 3: Watch logs
docker logs -f crawlab-master | grep -E "task|error"

# Terminal 4: MongoDB stats
docker exec crawlab-mongo mongosh --eval "db.tasks.countDocuments({})"
```

## Success Criteria

### Light Load (100 tasks)
- ✅ Creation success: 100%
- ✅ Execution success: >95%
- ✅ Response time: <500ms

### Heavy Load (1000 tasks)
- ✅ Creation success: >95%
- ✅ Execution success: >85%
- ✅ Response time: <2s

### Extreme Load (5000 tasks)
- ✅ Creation success: >90%
- ✅ Execution success: >80%
- ✅ System recovers gracefully

## Common Issues

### Issue: "Authentication failed"
**Solution**: Verify Crawlab is running and credentials are correct
```bash
curl http://localhost:8080/api/login -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'
```

### Issue: "No worker nodes found"
**Solution**: Start worker nodes
```bash
docker-compose up -d crawlab-worker-1
```

### Issue: Tasks stuck in pending
**Solution**: Check worker connectivity and capacity
```bash
docker logs crawlab-worker-1
```

### Issue: Database connection errors
**Solution**: Check MongoDB connection pool settings
```bash
# Increase connection pool in config.yml
database:
  max_pool_size: 200
```

## Performance Tuning

### Increase Throughput
- Add more worker nodes
- Increase batch size
- Optimize spider execution time
- Tune database connection pool

### Reduce Resource Usage
- Decrease concurrent workers
- Use smaller batch sizes
- Add delays between batches
- Limit task duration

### Database Optimization
```bash
# Create indexes for better query performance
docker exec crawlab-mongo mongosh crawlab --eval "
  db.tasks.createIndex({spider_id: 1, created_at: -1});
  db.tasks.createIndex({status: 1, created_at: -1});
"
```

## CI/CD Integration

```yaml
# .github/workflows/pressure-test.yml
- name: Run Pressure Test
  run: |
    cd crawlab-test
    python runners/scheduler/SCH-002_task_execution_pressure_test.py \
      --load medium \
      --output test-results.json
      
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: pressure-test-results
    path: test-results.json
```

## Analyzing Results

Results are saved in JSON format:

```json
{
  "load_level": "heavy",
  "timestamp": "2025-10-28T10:30:00Z",
  "creation": {
    "total_tasks": 1000,
    "created": 982,
    "creation_success_rate": 98.2,
    "tasks_per_second": 7.8
  },
  "execution": {
    "execution_success_rate": 89.5,
    "execution_time_sec": 375.2
  }
}
```

Key metrics to review:
- **Creation success rate**: Task creation API reliability
- **Tasks/second**: System throughput capacity
- **Execution success rate**: Worker stability and reliability
- **Execution time**: Overall system performance

## Best Practices

1. **Start small**: Always run light load first
2. **Monitor continuously**: Watch resources during tests
3. **Establish baseline**: Run tests in controlled environment
4. **Test incrementally**: Gradually increase load
5. **Clean up**: Verify cleanup after each test
6. **Document results**: Keep records for capacity planning
7. **Test regularly**: Include in CI/CD pipeline

## Related Documentation

- Test Specification: `specs/scheduler/SCH-002-task-execution-pressure-test.md`
- Testing SOP: `TESTING_SOP.md`
- API Documentation: `specs/api/README.md`
- Cluster Testing: `specs/cluster/CLS-003-file-sync-grpc-streaming-performance.md`
