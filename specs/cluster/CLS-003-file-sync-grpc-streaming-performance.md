# CLS-003 - File Sync gRPC Streaming Performance and Reliability

## Metadata
- **Category**: cluster
- **Priority**: high
- **Complexity**: moderate
- **Duration**: 20-25 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, mongodb, test spider with 1000+ files

## Scenario
This test validates the new gRPC streaming file synchronization implementation to ensure it:
1. Actually works - gRPC server is running and accepting connections
2. Eliminates JSON parsing errors under high concurrency
3. Efficiently deduplicates concurrent scan requests
4. Reduces master node CPU/network load through caching
5. Provides reliable fallback to HTTP when gRPC is disabled

This is critical because the previous HTTP/JSON implementation caused 15% failure rates when multiple tasks started simultaneously. The test runs automated verification that can be executed in CI/CD.

## Prerequisites
- Crawlab master node running with gRPC server enabled
- At least 1 worker node connected
- MongoDB accessible
- Docker environment accessible
- Test uses existing source code files (no manual setup needed)

## Test Steps

### Automated Performance Test via CLI
**Method**: script
**Command**: 
```bash
cd tests
./cli.py --spec CLS-003
```

The test runner will automatically execute the following steps:

### Step 1: Environment Setup
**Action**: Verify test environment and find test data
**Expected**: 
- Master and worker containers running
- Test spider directory identified (uses existing source code)
- gRPC server confirmed running

### Step 2: Test HTTP Mode (Baseline)
**Action**: Run tasks in HTTP sync mode and measure performance
**Steps**:
- Configure sync mode to HTTP (`useGrpc: false`)
- Create 1000 concurrent tasks for the test spider
- Measure: success rate, duration, JSON errors in logs
**Expected**:
- Some tasks may fail (known issue with HTTP mode)
- Success rate: ~80-90% (can have failures)
- JSON parsing errors may appear in logs
- Baseline metrics captured for comparison

### Step 3: Test gRPC Mode (Improved)
**Action**: Run tasks in gRPC sync mode and measure performance
**Steps**:
- Configure sync mode to gRPC (`useGrpc: true`)
- Create 1000 concurrent tasks for the same test spider
- Measure: success rate, duration, deduplication behavior
**Expected**:
- All tasks succeed (100% success rate)
- No JSON parsing errors
- Single directory scan serves all tasks (deduplication)
- Master logs show "notified N subscribers"

### Step 4: Verify Request Deduplication
**Action**: Confirm only one directory scan occurs for concurrent requests
**Expected**:
- Master logs show "performing directory scan" appears once
- Master logs show "notified 999 subscribers" (other 999 tasks wait)
- All 1000 tasks receive the same scan results

### Step 5: Check for JSON Errors
**Action**: Scan master logs for JSON parsing errors
**Expected**:
- HTTP mode: May have "error unmarshaling JSON" messages
- gRPC mode: Zero JSON errors

### Step 6: Performance Comparison
**Action**: Compare HTTP vs gRPC metrics
**Measurements**:
- Success rate improvement
- Error elimination
- Deduplication verification
**Expected**:
- gRPC success rate >= HTTP success rate + 10%
- gRPC has zero JSON errors
- gRPC shows deduplication evidence in logs

## Success Criteria
- [ ] HTTP mode: Tasks run, some may fail (establishes baseline)
- [ ] gRPC mode: 100% success rate (all tasks succeed)
- [ ] gRPC mode: Zero JSON parsing errors
- [ ] Request deduplication: One scan serves multiple tasks
- [ ] Performance: gRPC success rate >= HTTP + 10%
- [ ] Logs show evidence: "notified N subscribers" message present

## Failure Scenarios

### Scenario: gRPC Connection Failure
- **Symptoms**: Worker logs show "failed to get sync client"
- **Action**: Verify gRPC server running, check firewall, validate authentication
- **Recovery**: Should fallback to HTTP mode if configured

### Scenario: Cache Stale Data
- **Symptoms**: Worker downloads old files, doesn't detect changes
- **Action**: Check cache TTL configuration, verify file hash calculation
- **Recovery**: Clear cache or wait for TTL expiry

### Scenario: Master Overload (HTTP mode)
- **Symptoms**: HTTP 503 errors, high master CPU, slow responses
- **Action**: Enable gRPC mode or increase rate limit
- **Recovery**: Reduce concurrent tasks or scale master resources

### Scenario: Incomplete File Transfer
- **Symptoms**: Some files missing after sync, hash mismatches
- **Action**: Check network stability, gRPC connection health
- **Recovery**: Retry sync, verify stream completion

### Scenario: Memory Spike with Large Codebases
- **Symptoms**: Master/worker OOM during sync
- **Action**: Reduce chunk size configuration
- **Recovery**: Restart nodes, optimize chunking

## Execution

### Automated via CLI (Performance Test)
```bash
cd tests
./cli.py --spec CLS-003
```

This runs a fully automated performance comparison test:
1. Tests HTTP mode (baseline with known issues)
2. Tests gRPC mode (improved implementation)
3. Compares results and verifies improvements
4. Checks logs for deduplication evidence
5. Reports pass/fail based on performance criteria

## Cleanup
No cleanup needed - automated test only verifies deployment.

## Expected Test Outputs

### Performance Comparison Report
```json
{
  "http_mode": {
    "concurrent_tasks": 1000,
    "success_count": 850,
    "success_rate": 85,
    "avg_duration_sec": 12.5,
    "json_errors": 150
  },
  "grpc_mode": {
    "concurrent_tasks": 1000,
    "success_count": 1000,
    "success_rate": 100,
    "avg_duration_sec": 2.8,
    "json_errors": 0,
    "deduplication_verified": true,
    "directory_scans": 1
  },
  "improvements": {
    "success_rate_increase": "+15%",
    "json_errors_eliminated": true,
    "deduplication_working": true,
    "test_result": "PASS"
  }
}
```

## Notes
- This test requires the gRPC streaming implementation to be deployed
- Feature flag `sync.useGrpc` must be configurable via environment
- Test spider preparation may take 2-3 minutes
- Resource monitoring requires Docker stats access
- Large file tests may require adjusting Docker memory limits

## Implementation Status
- **Implementation**: ✅ Complete (2025-10-20)
- **Automated Performance Test**: ✅ Complete (runs via cli.py)
- **CI Integration**: ✅ Ready (./cli.py --spec CLS-003)
- **Test validates**: Success rate improvement, error elimination, request deduplication

## History
- **Created**: 2025-10-20, GitHub Copilot - Initial specification for gRPC file sync testing
- **Updated**: 2025-10-20, GitHub Copilot - Added automated performance testing via CLI
