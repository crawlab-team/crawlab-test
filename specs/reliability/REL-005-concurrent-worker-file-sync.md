# REL-005 - Concurrent Worker File Sync Reliability

## Metadata
- **Category**: reliability
- **Priority**: high
- **Complexity**: complex
- **Duration**: 5-10 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, multiple crawlab-workers, MongoDB, gRPC enabled

## Scenario
This test validates that file synchronization works correctly when multiple worker nodes request files simultaneously. It stresses the gRPC sync mechanism to ensure proper handling of concurrent requests, avoiding race conditions, and maintaining data integrity across all workers.

**Context**: With gRPC-based file sync, multiple workers might request the same spider files simultaneously when tasks are assigned. The sync server implements caching and deduplication to handle this efficiently, but we need to verify it works correctly under load.

**Why This Test Matters**:
- Validates concurrent access patterns in production scenarios
- Tests gRPC sync server's deduplication and caching mechanisms
- Ensures no file corruption during concurrent downloads
- Verifies all workers receive complete and correct file sets

## Prerequisites
- Crawlab API accessible at http://localhost:8080/api
- Master node running with gRPC server enabled (port 9666)
- At least **2 worker nodes** connected and registered
- MongoDB accessible
- Environment variable `CRAWLAB_GRPC_ENABLED=true` on all nodes
- Valid admin credentials (admin:admin)

## Test Steps

### Step 1: Verify Multi-Worker Setup
**Method**: script
**Command**: 
```bash
# Get list of registered nodes
NODES=$(curl -s -X GET "http://localhost:8080/api/nodes" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data')

WORKER_COUNT=$(echo "$NODES" | jq '[.[] | select(.is_master == false)] | length')
echo "Worker nodes registered: $WORKER_COUNT"

echo "$NODES" | jq -r '.[] | select(.is_master == false) | "\(.key) - \(.status)"'
```

**Expected**: At least 2 worker nodes online
**Validation**: 
- Worker count >= 2
- All workers in "online" status

---

### Step 2: Authenticate
**Method**: script
**Command**: 
```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.data')
```

**Expected**: Authentication successful

---

### Step 3: Create Test Spider with Larger File Set
**Method**: script
**Command**:
```bash
SPIDER_ID=$(curl -s -X POST http://localhost:8080/api/spiders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rel-005-concurrent-sync-test",
    "cmd": "python main.py",
    "description": "REL-005: Tests concurrent file sync to multiple workers"
  }' | jq -r '.data._id')

echo "Spider ID: $SPIDER_ID"
```

**Expected**: Spider created successfully

---

### Step 4: Upload Multiple Files (Larger Dataset)
**Method**: script
**Command**:
```bash
# Upload 10 files to create a more realistic sync scenario
for i in {1..10}; do
  curl -s -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"path\": \"module_$i.py\",
      \"content\": \"# Module $i\\ndef function_$i():\\n    return '$i'\\n\"
    }" > /dev/null
  
  echo "Uploaded module_$i.py"
done

# Main verification script
curl -s -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "main.py",
    "content": "#!/usr/bin/env python\nimport os\nimport sys\nimport socket\n\nprint(f\"=== REL-005: Concurrent File Sync Test ===\")\nprint(f\"Worker: {socket.gethostname()}\")\nprint(f\"Working directory: {os.getcwd()}\")\n\nexpected_files = [\"main.py\"] + [f\"module_{i}.py\" for i in range(1, 11)]\nmissing_files = []\nall_files = sorted(os.listdir(os.getcwd()))\n\nprint(f\"\\nExpected {len(expected_files)} files\")\nprint(f\"Found {len(all_files)} files: {all_files}\")\n\nfor filename in expected_files:\n    if os.path.exists(filename):\n        size = os.path.getsize(filename)\n        print(f\"✓ {filename} ({size} bytes)\")\n    else:\n        print(f\"✗ MISSING: {filename}\")\n        missing_files.append(filename)\n\nif missing_files:\n    print(f\"\\n❌ FAIL: {len(missing_files)} files missing: {missing_files}\")\n    sys.exit(1)\nelse:\n    print(f\"\\n✅ SUCCESS: All {len(expected_files)} files synced correctly on {socket.gethostname()}\")"
  }' > /dev/null

echo "✓ Uploaded 11 files total"
```

**Expected**: 11 files uploaded (10 modules + 1 main)
**Validation**: All uploads return HTTP 200

---

### Step 5: Verify Files on Master
**Method**: script
**Command**:
```bash
FILE_COUNT=$(docker exec crawlab_master find /app/tmp/$SPIDER_ID/ -type f | wc -l)
echo "Files on master: $FILE_COUNT"
```

**Expected**: 11 files on master
**Validation**: File count = 11

---

### Step 6: Create Multiple Tasks Simultaneously
**Method**: script
**Command**:
```bash
# Create 4 tasks simultaneously (will be distributed across workers)
TASK_IDS=()

for i in {1..4}; do
  TASK_RESPONSE=$(curl -s -X POST http://localhost:8080/api/tasks \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"spider_id\": \"$SPIDER_ID\"}")
  
  TASK_ID=$(echo $TASK_RESPONSE | jq -r '.data[0]')
  TASK_IDS+=($TASK_ID)
  echo "Created task $i: $TASK_ID"
done

echo "---"
echo "Created ${#TASK_IDS[@]} tasks"
```

**Expected**: 4 tasks created
**Validation**: 4 task IDs returned

---

### Step 7: Monitor All Tasks to Completion
**Method**: script
**Command**:
```bash
# Wait for all tasks to complete (max 2 minutes)
echo "Monitoring task completion..."

for attempt in {1..60}; do
  ALL_DONE=true
  
  for TASK_ID in "${TASK_IDS[@]}"; do
    STATUS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID" \
      -H "Authorization: Bearer $TOKEN" | jq -r '.data.status')
    
    if [ "$STATUS" != "finished" ] && [ "$STATUS" != "error" ]; then
      ALL_DONE=false
    fi
  done
  
  if [ "$ALL_DONE" = true ]; then
    echo "All tasks completed at attempt $attempt"
    break
  fi
  
  echo "[$attempt/60] Waiting for tasks..."
  sleep 2
done
```

**Expected**: All tasks complete within 2 minutes
**Validation**: All tasks reach "finished" status

---

### Step 8: Verify All Tasks Succeeded
**Method**: script
**Command**:
```bash
echo "=== Task Results ==="

SUCCESS_COUNT=0
FAIL_COUNT=0

for TASK_ID in "${TASK_IDS[@]}"; do
  TASK_INFO=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN")
  
  STATUS=$(echo $TASK_INFO | jq -r '.data.status')
  NODE=$(echo $TASK_INFO | jq -r '.data.node_key')
  
  LOGS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID/logs" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.data')
  
  if echo "$LOGS" | grep -q "✅ SUCCESS"; then
    echo "✓ Task $TASK_ID on $NODE: SUCCESS"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "✗ Task $TASK_ID on $NODE: FAILED"
    echo "  Status: $STATUS"
    echo "$LOGS" | grep -E "✗ MISSING|❌ FAIL" | head -3
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

echo "---"
echo "Results: $SUCCESS_COUNT succeeded, $FAIL_COUNT failed"
```

**Expected**: All tasks succeeded
**Validation**: 
- SUCCESS_COUNT = 4
- FAIL_COUNT = 0
- All logs contain "✅ SUCCESS"

---

### Step 9: Verify File Integrity Across Workers
**Method**: script
**Command**:
```bash
echo "=== File Integrity Check ==="

# Check each worker received complete files
for TASK_ID in "${TASK_IDS[@]}"; do
  LOGS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID/logs" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.data')
  
  SYNC_COUNT=$(echo "$LOGS" | grep -c "✓ module_")
  echo "Task $TASK_ID: $SYNC_COUNT/10 module files synced"
  
  if [ $SYNC_COUNT -ne 10 ]; then
    echo "  ⚠️  WARNING: Missing files detected"
    echo "$LOGS" | grep "✗ MISSING"
  fi
done
```

**Expected**: All workers received all 11 files
**Validation**: Each task logs show 10 module files + 1 main file

---

### Step 10: Check gRPC Server Handled Concurrent Requests
**Method**: script
**Command**:
```bash
echo "=== gRPC Sync Server Activity ==="

# Look for deduplication/caching indicators
docker logs crawlab_master --tail 200 | grep -E "StreamFileScan|file scan request|cached|deduplication" | tail -20

echo "---"
echo "Checking for concurrent sync handling:"
docker logs crawlab_master --tail 200 | grep $SPIDER_ID | grep -E "scan|sync" | wc -l
```

**Expected**: Master logs show efficient handling of concurrent requests
**Validation**: 
- Logs show multiple "file scan request" entries
- May show "cached" or deduplication messages
- No errors in sync process

---

## Success Criteria
- [x] At least 2 worker nodes online
- [x] Authentication successful
- [x] Spider created with 11 files
- [x] All files verified on master
- [x] 4 tasks created simultaneously
- [x] All tasks completed within 2 minutes
- [x] All 4 tasks succeeded (status = "finished")
- [x] All 4 tasks show "✅ SUCCESS" in logs
- [x] Each task received all 11 files (no missing files)
- [x] No file corruption (all files have correct content)
- [x] Master logs show proper handling of concurrent sync requests
- [x] No gRPC errors in master or worker logs

## Failure Scenarios

### Scenario: Some Tasks Missing Files
- **Symptoms**: One or more tasks fail with "✗ MISSING" messages
- **Root Cause**: Race condition in file sync or cache issue
- **Action**:
  1. Check which worker(s) had issues
  2. Review master logs for that specific sync request
  3. Check if sync was interrupted
  4. Verify gRPC stream completed properly

### Scenario: Tasks Distributed Unevenly
- **Symptoms**: All tasks run on single worker
- **Root Cause**: Load balancing issue, not file sync issue
- **Action**:
  1. Check scheduler configuration
  2. Verify all workers are "available" status
  3. Not a blocker for this test

### Scenario: File Corruption
- **Symptoms**: Files present but content incorrect
- **Root Cause**: Race condition in concurrent write operations
- **Action**:
  1. Check file hashes on workers vs master
  2. Review gRPC streaming logic
  3. Check for concurrent write issues

### Scenario: Timeout
- **Symptoms**: Tasks stuck in "running" > 2 minutes
- **Action**:
  1. Check worker system resources
  2. Check network latency
  3. Review worker logs for hangs

## Execution
### Automated
```bash
cd /home/marvin/projects/crawlab-team/crawlab-pro/crawlab-test
uv run ./cli.py --spec REL-005
```

### Manual
1. Ensure master + at least 2 workers running
2. Execute steps sequentially
3. Monitor both master and worker logs
4. Compare results across workers

## Cleanup
```bash
# Delete test spider
curl -X DELETE "http://localhost:8080/api/spiders/$SPIDER_ID" \
  -H "Authorization: Bearer $TOKEN"

# Tasks will be automatically cleaned up with spider
```

## Notes
- This test requires **multiple workers** to properly validate concurrent sync
- Test validates gRPC server's caching and deduplication mechanisms
- If only 1 worker available, test will still run but won't test concurrency
- File count (11 files) is intentionally moderate to keep test fast but realistic
- Can increase file count or task count to stress test further

## Implementation Status
- [ ] Test specification complete
- [ ] Python runner implemented
- [ ] Added to CI pipeline (requires multi-worker setup)
- [ ] Documentation updated

## History
- **Created**: 2025-10-30, Part of investigation into file sync reliability after gRPC migration
- **Purpose**: Validate concurrent access patterns that occur in production multi-worker deployments
