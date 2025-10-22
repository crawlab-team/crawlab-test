# API-001 - Task Execution with File Sync Validation

## Metadata
- **Category**: api
- **Priority**: critical
- **Complexity**: medium
- **Duration**: 2-3 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, MongoDB

## Scenario
This test validates the complete task execution workflow via API, including spider creation, file upload, task execution, and file synchronization to workers. This is a fast, reliable alternative to UI-based testing for validating core backend functionality including gRPC file sync.

**Why API Testing**:
- **Fast**: 2-3 minutes vs 10-15 minutes for UI tests
- **Reliable**: No browser, no UI interactions, no element discovery
- **Focused**: Tests backend logic directly
- **CI-friendly**: Easy to run in pipelines

**Development Note**: This test was created by first checking the OpenAPI specification at `http://localhost:8080/api/openapi.json` to understand exact payload formats. See [API Testing Guide](./README.md) for best practices.

## Prerequisites
- Crawlab API accessible at http://localhost:8080/api
- Master and at least one worker node running
- MongoDB accessible
- Valid admin credentials

## Test Steps

### Step 1: Authenticate and Get Token
**Method**: script
**Command**: 
```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | jq -r '.data')
```

**Expected**: Authentication successful, token received
**Validation**: 
- HTTP 200 status
- Response contains token
- Token is non-empty string

---

### Step 2: Create Test Spider
**Method**: script
**Command**:
```bash
SPIDER_ID=$(curl -s -X POST http://localhost:8080/api/spiders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api-test-grpc-sync",
    "cmd": "python main.py",
    "project_id": "default"
  }' | jq -r '.data._id')
```

**Expected**: Spider created successfully
**Validation**:
- HTTP 200 status
- Response contains spider ID
- Spider appears in database

---

### Step 3: Upload Spider Files
**Method**: script
**Command**:
```bash
# Create main.py
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "main.py",
    "content": "#!/usr/bin/env python\nimport os\nimport sys\n\nprint(\"Spider starting...\")\nprint(f\"Working directory: {os.getcwd()}\")\nprint(f\"Files in directory: {os.listdir(os.getcwd())}\")\n\n# Verify files were synced\nexpected_files = [\"main.py\", \"config.json\", \"utils.py\"]\nfor f in expected_files:\n    if os.path.exists(f):\n        print(f\"✓ File synced: {f}\")\n    else:\n        print(f\"✗ File missing: {f}\")\n        sys.exit(1)\n\nprint(\"All files synced successfully!\")\nprint(\"Spider execution complete.\")"
  }'

# Create config.json
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "config.json",
    "content": "{\"test\": true, \"version\": \"1.0.0\"}"
  }'

# Create utils.py
curl -X POST http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "utils.py",
    "content": "def helper():\n    return \"Helper function\""
  }'
```

**Expected**: Files uploaded successfully
**Validation**:
- All 3 file uploads return HTTP 200
- Files stored on master node
- Files visible via API

---

### Step 4: Verify Files on Master
**Method**: script
**Command**:
```bash
FILES=$(curl -s http://localhost:8080/api/spiders/$SPIDER_ID/files \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data[].name')

echo "Files on master:"
echo "$FILES"
```

**Expected**: All 3 files present on master
**Validation**:
- main.py exists
- config.json exists
- utils.py exists

---

### Step 5: Create and Execute Task
**Method**: script
**Command**:
```bash
TASK_ID=$(curl -s -X POST http://localhost:8080/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"spider_id\": \"$SPIDER_ID\",
    \"cmd\": \"python main.py\"
  }" | jq -r '.data._id')

echo "Task ID: $TASK_ID"
```

**Expected**: Task created and starts execution
**Validation**:
- HTTP 200 status
- Task ID received
- Task starts running

---

### Step 6: Monitor Task Execution
**Method**: script
**Command**:
```bash
# Wait for task to complete (max 30 seconds)
for i in {1..30}; do
  STATUS=$(curl -s http://localhost:8080/api/tasks/$TASK_ID \
    -H "Authorization: Bearer $TOKEN" | jq -r '.data.status')
  
  echo "Task status: $STATUS"
  
  if [ "$STATUS" = "finished" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  
  sleep 1
done
```

**Expected**: Task completes successfully
**Validation**:
- Task transitions to "finished" status
- Task completes within 30 seconds

---

### Step 7: Verify File Sync in Task Logs
**Method**: script
**Command**:
```bash
LOGS=$(curl -s http://localhost:8080/api/tasks/$TASK_ID/logs \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data')

echo "Task logs:"
echo "$LOGS"

# Check for file sync success messages
echo "$LOGS" | grep -q "✓ File synced: main.py" && echo "✓ main.py synced" || echo "✗ main.py NOT synced"
echo "$LOGS" | grep -q "✓ File synced: config.json" && echo "✓ config.json synced" || echo "✗ config.json NOT synced"
echo "$LOGS" | grep -q "✓ File synced: utils.py" && echo "✓ utils.py synced" || echo "✗ utils.py NOT synced"
echo "$LOGS" | grep -q "All files synced successfully" && echo "✓ File sync validation passed" || echo "✗ File sync validation FAILED"
```

**Expected**: Task logs show all files were synced
**Validation**:
- Log contains "✓ File synced: main.py"
- Log contains "✓ File synced: config.json"
- Log contains "✓ File synced: utils.py"
- Log contains "All files synced successfully"
- Task status is "finished" (not "error")

---

### Step 8: Check gRPC Activity in Master Logs
**Method**: script
**Command**:
```bash
# Check Docker logs for gRPC file sync activity
docker logs crawlab_master --since 2m 2>&1 | grep -i "sync\|grpc" | tail -20

# Look for:
# - "performing directory scan for"
# - "scanned N files from"
# - "streaming" or "stream"
```

**Expected**: Master logs show gRPC sync activity
**Validation**:
- Logs contain sync service activity
- Logs show directory scan
- Logs indicate file streaming (if verbose logging enabled)

---

### Step 9: Verify Task Success
**Method**: script
**Command**:
```bash
FINAL_STATUS=$(curl -s http://localhost:8080/api/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data.status')

if [ "$FINAL_STATUS" = "finished" ]; then
  echo "✓ Task completed successfully"
  exit 0
else
  echo "✗ Task failed with status: $FINAL_STATUS"
  exit 1
fi
```

**Expected**: Task status is "finished"
**Validation**:
- Task status = "finished"
- No error status
- Exit code 0

## Success Criteria
- [ ] Authentication successful
- [ ] Spider created via API
- [ ] 3 files uploaded successfully
- [ ] Files verified on master
- [ ] Task created and executed
- [ ] Task completed within 30 seconds
- [ ] Task logs show all files synced to worker
- [ ] Task status is "finished"
- [ ] gRPC sync activity visible in master logs
- [ ] No errors in task execution

## Failure Scenarios

### Scenario: Files Not Synced to Worker
- **Symptoms**: Task logs show "File missing" errors
- **Action**: 
  1. Check gRPC server is running: `docker exec crawlab_master netstat -tlnp | grep 9666`
  2. Check worker can reach master: `docker exec crawlab_worker nc -zv master 9666`
  3. Verify `CRAWLAB_GRPC_ENABLED=true` in both containers
  4. Check master logs for sync errors

### Scenario: Task Timeout
- **Symptoms**: Task stuck in "running" status > 30 seconds
- **Action**:
  1. Check worker node is online
  2. Check task process on worker
  3. Review task logs for errors
  4. Check worker resource availability

### Scenario: Authentication Failed
- **Symptoms**: HTTP 401 or empty token
- **Action**:
  1. Verify credentials are correct
  2. Check if API is accessible
  3. Review master startup logs

## Execution

### Automated
```bash
cd tests/runners/api
./API_001_task_execution_with_file_sync.sh
```

### Manual (Step by Step)
Execute each step's command in sequence, verifying outputs.

## Cleanup
```bash
# Delete test spider (cascades to tasks)
curl -X DELETE http://localhost:8080/api/spiders/$SPIDER_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Notes
- **Fast execution**: 2-3 minutes vs 10-15 minutes for UI tests
- **Validates gRPC file sync**: Task execution requires worker to sync files from master
- **No UI dependencies**: Pure API testing
- **CI-friendly**: Easy to automate and integrate
- **Deterministic**: No browser timing issues or element discovery problems
- **Direct validation**: Checks actual file presence on worker, not just UI display

## Performance Comparison
| Test Type | Duration | Reliability | Coverage |
|-----------|----------|-------------|----------|
| UI-003 (full) | 10-15 min | Medium (browser deps) | UI + Backend |
| API-001 | 2-3 min | High (no browser) | Backend only |
| CLS-003 (stress) | 1-2 min | High (direct gRPC) | gRPC performance |

**Recommendation**: 
- Use **API-001** for fast, reliable task execution validation
- Use **CLS-003** for gRPC performance/stress testing
- Use **UI-003** only for end-to-end user workflow validation

## History
- **Created**: 2025-10-21, Assistant
- **Purpose**: Fast API-based alternative to slow UI tests for backend validation
