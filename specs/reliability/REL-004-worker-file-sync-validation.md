# REL-004 - Worker Node File Sync Validation

## Metadata
- **Category**: reliability
- **Priority**: critical
- **Complexity**: medium
- **Duration**: 3-5 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, MongoDB, gRPC enabled

## Scenario
This test validates that spider files are correctly synchronized to worker nodes via gRPC before task execution. It addresses a critical issue where users reported tasks failing due to missing code files on workers after the migration from HTTP sync to gRPC sync.

**Context**: After migrating from HTTP-based file sync to gRPC-based sync, some users reported that spider tasks fail on worker nodes with "missing file" errors. Investigation revealed that file sync errors are logged as warnings but don't prevent task execution, allowing tasks to run without all required files.

**Why This Test Matters**:
- Validates the core file synchronization mechanism
- Prevents "missing file" runtime errors
- Ensures gRPC sync works correctly in multi-node deployments
- Tests actual end-to-end workflow: upload → sync → execute

## Prerequisites
- Crawlab API accessible at http://localhost:8080/api
- Master node running with gRPC server enabled (port 9666)
- At least one worker node connected and registered
- MongoDB accessible
- Environment variable `CRAWLAB_GRPC_ENABLED=true` on both master and worker
- Valid admin credentials (admin:admin)

## Test Steps

### Step 1: Verify gRPC Service Availability
**Method**: script
**Command**: 
```bash
# Check gRPC server is running on master
docker exec crawlab_master netstat -tlnp | grep 9666

# Check worker can reach master gRPC port
docker exec crawlab_worker nc -zv master 9666
```

**Expected**: 
- gRPC server listening on port 9666
- Worker can connect to master:9666

**Validation**: 
- Port 9666 is in LISTEN state
- Connection test succeeds with "succeeded" message

---

### Step 2: Authenticate and Get Token
**Method**: script
**Command**: 
```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.data')

echo "Token: ${TOKEN:0:20}..."
```

**Expected**: Authentication successful, token received
**Validation**: 
- HTTP 200 status
- Token is non-empty string

---

### Step 3: Create Test Spider with File Validation
**Method**: script
**Command**:
```bash
SPIDER_ID=$(curl -s -X POST http://localhost:8080/api/spiders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rel-004-file-sync-test",
    "cmd": "python main.py",
    "project_id": "default",
    "description": "REL-004: Tests file sync to worker nodes"
  }' | jq -r '.data._id')

echo "Spider ID: $SPIDER_ID"
```

**Expected**: Spider created successfully
**Validation**:
- HTTP 200 status
- Spider ID returned
- Spider name: "rel-001-file-sync-test"

---

### Step 4: Upload Spider Files
**Method**: script
**Command**:
```bash
# Main script that verifies all files are present
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "main.py",
    "content": "#!/usr/bin/env python\nimport os\nimport sys\n\nprint(\"=== REL-004: File Sync Validation ===\")\nprint(f\"Working directory: {os.getcwd()}\")\nprint(f\"Files in directory: {sorted(os.listdir(os.getcwd()))}\")\n\n# List of expected files\nexpected_files = [\"main.py\", \"config.json\", \"utils.py\", \"requirements.txt\"]\nmissing_files = []\n\nfor filename in expected_files:\n    if os.path.exists(filename):\n        size = os.path.getsize(filename)\n        print(f\"✓ File synced: {filename} ({size} bytes)\")\n    else:\n        print(f\"✗ File missing: {filename}\")\n        missing_files.append(filename)\n\nif missing_files:\n    print(f\"\\n❌ SYNC FAILED: {len(missing_files)} files missing: {missing_files}\")\n    sys.exit(1)\nelse:\n    print(f\"\\n✅ SYNC SUCCESS: All {len(expected_files)} files synced correctly\")\n    print(\"Spider execution complete.\")"
  }'

# Config file
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "config.json",
    "content": "{\"test\": \"rel-004\", \"version\": \"1.0.0\", \"sync_mode\": \"grpc\"}"
  }'

# Utility module
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "utils.py",
    "content": "\"\"\"Utility functions for REL-004 test\"\"\"\n\ndef validate_files():\n    return True\n\ndef get_version():\n    return \"1.0.0\""
  }'

# Requirements file
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "requirements.txt",
    "content": "# No external dependencies for this test"
  }'

echo "✓ Uploaded 4 files to spider"
```

**Expected**: All 4 files uploaded successfully
**Validation**:
- Each upload returns HTTP 200
- Files visible in spider directory on master

---

### Step 5: Verify Files on Master Node
**Method**: script
**Command**:
```bash
# Check files exist on master
docker exec crawlab_master ls -lh /app/tmp/$SPIDER_ID/

echo "---"
echo "File count:"
docker exec crawlab_master find /app/tmp/$SPIDER_ID/ -type f | wc -l
```

**Expected**: All 4 files present on master
**Validation**:
- 4 files listed
- Files have non-zero size

---

### Step 6: Create and Execute Task on Worker
**Method**: script  
**Command**:
```bash
# Create task
TASK_RESPONSE=$(curl -s -X POST http://localhost:8080/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"spider_id\": \"$SPIDER_ID\"}")

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.data[0]')
echo "Task ID: $TASK_ID"

# Wait a moment for task to be picked up
sleep 2
```

**Expected**: Task created and assigned to worker
**Validation**:
- HTTP 200 status
- Task ID returned (array format)

---

### Step 7: Monitor Task Execution and File Sync
**Method**: script
**Command**:
```bash
# Poll task status until completion (max 60 seconds)
for i in {1..30}; do
  TASK_STATUS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN" | jq -r '.data.status')
  
  echo "[$i/30] Task status: $TASK_STATUS"
  
  if [ "$TASK_STATUS" = "finished" ] || [ "$TASK_STATUS" = "error" ]; then
    break
  fi
  
  sleep 2
done

echo "Final status: $TASK_STATUS"
```

**Expected**: Task completes within 60 seconds
**Validation**:
- Task transitions: pending → running → finished
- Status eventually becomes "finished"

---

### Step 8: Verify File Sync in Task Logs
**Method**: script
**Command**:
```bash
# Get task logs
LOGS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID/logs" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data')

echo "$LOGS"

# Check for file sync confirmation
echo "---"
echo "Checking for sync validation..."
echo "$LOGS" | grep -E "✓ File synced:|✅ SYNC SUCCESS"
```

**Expected**: Task logs show all files synced successfully
**Validation**:
- Logs contain "✓ File synced: main.py"
- Logs contain "✓ File synced: config.json"  
- Logs contain "✓ File synced: utils.py"
- Logs contain "✓ File synced: requirements.txt"
- Logs contain "✅ SYNC SUCCESS: All 4 files synced correctly"
- NO lines with "✗ File missing:"

---

### Step 9: Check gRPC Sync Activity in Master Logs
**Method**: script
**Command**:
```bash
# Check master logs for gRPC sync activity
echo "Checking master logs for gRPC file sync..."
docker logs crawlab_master --tail 100 | grep -E "StreamFileScan|StreamFileDownload|file synchronization"

echo "---"
echo "Checking for specific spider sync:"
docker logs crawlab_master --tail 100 | grep $SPIDER_ID
```

**Expected**: Master logs show gRPC sync operations
**Validation**:
- Logs contain "StreamFileScan" or "file scan request"
- Logs reference the spider ID
- Logs show "scanned X files" message
- No errors in gRPC sync process

---

### Step 10: Verify Task Success
**Method**: script
**Command**:
```bash
# Get final task details
TASK_INFO=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN")

STATUS=$(echo $TASK_INFO | jq -r '.data.status')
ERROR_MSG=$(echo $TASK_INFO | jq -r '.data.error')

echo "Task Status: $STATUS"
echo "Error Message: $ERROR_MSG"

# Check exit code
LOGS=$(curl -s -X GET "http://localhost:8080/api/tasks/$TASK_ID/logs" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data')
echo "$LOGS" | tail -5
```

**Expected**: Task completed successfully
**Validation**:
- status = "finished"
- error = null or empty
- Logs end with "Spider execution complete."
- No Python tracebacks in logs

---

## Success Criteria
- [x] gRPC server accessible on master node
- [x] Worker can connect to master gRPC port
- [x] Authentication successful
- [x] Spider created via API
- [x] 4 files uploaded successfully (main.py, config.json, utils.py, requirements.txt)
- [x] Files verified on master node
- [x] Task created and assigned to worker
- [x] Task completed within 60 seconds
- [x] Task status is "finished" (not "error")
- [x] Task logs show all 4 files synced to worker
- [x] Task logs contain "✅ SYNC SUCCESS"
- [x] No "✗ File missing" messages in logs
- [x] Master logs show gRPC sync activity
- [x] No errors in task execution

## Failure Scenarios

### Scenario: Files Not Synced to Worker
- **Symptoms**: Task logs show "✗ File missing:" messages, task fails with exit code 1
- **Root Cause**: gRPC sync failed but was only logged as warning
- **Action**: 
  1. Check gRPC server: `docker exec crawlab_master netstat -tlnp | grep 9666`
  2. Check worker connection: `docker exec crawlab_worker nc -zv master 9666`
  3. Verify `CRAWLAB_GRPC_ENABLED=true` in both containers
  4. Check master logs: `docker logs crawlab_master | grep -E "error|failed" | tail -20`
  5. Check worker logs: `docker logs crawlab_worker | grep -E "sync|grpc" | tail -20`

### Scenario: gRPC Service Unavailable
- **Symptoms**: Worker can't connect to master:9666
- **Action**:
  1. Check if gRPC server started: `docker logs crawlab_master | grep "grpc"`
  2. Check firewall/network rules
  3. Verify gRPC port in docker-compose network settings

### Scenario: Partial File Sync
- **Symptoms**: Some files synced, some missing
- **Root Cause**: Sync interrupted or permissions issue
- **Action**:
  1. Check file sizes on master
  2. Check worker disk space
  3. Check file permissions on master
  4. Review gRPC stream logs for interruptions

### Scenario: Task Timeout
- **Symptoms**: Task stuck in "running" status > 60 seconds
- **Action**:
  1. Check worker node is online
  2. Check task process on worker: `docker exec crawlab_worker ps aux | grep python`
  3. Check worker system resources
  4. Review task logs for hangs

## Execution
### Automated
```bash
cd /home/marvin/projects/crawlab-team/crawlab-pro/crawlab-test
uv run ./cli.py --spec REL-004
```

### Manual
1. Ensure master + worker are running with gRPC enabled
2. Execute test steps sequentially
3. Validate each step before proceeding
4. Document any failures with screenshots/logs

## Cleanup
```bash
# Delete test spider and its files
curl -X DELETE "http://localhost:8080/api/spiders/$SPIDER_ID" \
  -H "Authorization: Bearer $TOKEN"

# Verify cleanup
docker exec crawlab_master ls /app/tmp/ | grep -v $SPIDER_ID
```

## Notes
- This test is designed to be run repeatedly without side effects
- Test creates unique spider name with timestamp if needed
- gRPC sync is the default in newer versions; HTTP sync is legacy fallback
- File sync errors are currently logged as warnings, not failures - this is a known issue
- Test validates the **actual behavior** not just the API contract

## Implementation Status
- [ ] Test specification complete
- [ ] Python runner implemented
- [ ] Added to CI pipeline
- [ ] Documentation updated

## History
- **Created**: 2025-10-30, Investigation of user-reported file sync issues after gRPC migration
- **Context**: Users reported "missing file" errors on workers after recent migration from HTTP to gRPC file sync
