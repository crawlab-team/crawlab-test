# Quick Start Guide: Testing gRPC File Sync

## Prerequisites

1. **Docker environment running**:
   ```bash
   cd /home/marvin/projects/crawlab-team/crawlab-pro
   docker compose -f docker/dev/docker-compose.yml up -d
   ```

2. **Create test spider with many files**:
   - Option A: Use UI to create spider with 1000+ files
   - Option B: Copy existing large project into a spider directory

## Quick Tests

### 1. Smoke Test (2 minutes)
```bash
cd tests
python3 helpers/cluster/file_sync_test.py \
  --spider-id YOUR_SPIDER_ID \
  --smoke-test
```

### 2. Test Request Deduplication (5 minutes)
```bash
python3 helpers/cluster/file_sync_test.py \
  --spider-id YOUR_SPIDER_ID \
  --verify-deduplication \
  --concurrent-tasks 10
```

### 3. Compare HTTP vs gRPC (10 minutes)
```bash
python3 helpers/cluster/file_sync_test.py \
  --spider-id YOUR_SPIDER_ID \
  --compare-modes \
  --concurrent-tasks 10
```

### 4. Full Test Suite (20 minutes)
```bash
python3 helpers/cluster/file_sync_test.py \
  --spider-id YOUR_SPIDER_ID \
  --run-full-suite
```

## Manual Verification

### Check if gRPC is enabled:
```bash
# Check master logs for gRPC mode
docker logs crawlab_dev_master --tail 50 | grep -i "grpc\|sync"

# Should see:
# - "starting gRPC file synchronization" (worker)
# - "file scan request from node" (master gRPC)
# - "performing directory scan" (once for many tasks)
# - "notified N subscribers" (deduplication working)
```

### Monitor during test:
```bash
# Terminal 1: Watch master logs
docker logs -f crawlab_dev_master | grep sync

# Terminal 2: Watch master CPU
docker stats crawlab_dev_master

# Terminal 3: Run test
python3 helpers/cluster/file_sync_test.py --spider-id XXX --verify-deduplication
```

## Expected Results

### HTTP Mode (Baseline):
- Success rate: ~85% (15% failures with concurrent tasks)
- Master CPU: 80-100% during sync
- Logs show: "error unmarshaling JSON" 
- Multiple "performing directory scan" per spider

### gRPC Mode (Improved):
- Success rate: 100%
- Master CPU: <30% during sync
- No JSON errors
- Single "performing directory scan" per spider
- "notified N subscribers" showing deduplication

## Troubleshooting

### Container not found:
```bash
# List containers
docker ps | grep crawlab

# Update container name in script if different
# Default looks for: crawlab_dev_master, crawlab-master, etc.
```

### API connection failed:
```bash
# Check master is accessible
curl http://localhost:8080/api/health

# Or find container IP
docker inspect crawlab_dev_master | grep IPAddress
```

### gRPC not working:
```bash
# Check if feature flag is set
docker exec crawlab_dev_master env | grep CRAWLAB_SYNC_USEGRPC

# Set manually if needed
docker exec crawlab_dev_master sh -c 'export CRAWLAB_SYNC_USEGRPC=true'

# Or edit config.yml and restart
```

## Interpreting Results

### Good Signs (gRPC working):
- ✅ All tasks succeed (100% success rate)
- ✅ Single directory scan for 10 concurrent tasks
- ✅ "notified N subscribers" in logs
- ✅ Master CPU stays low (<30%)
- ✅ No JSON parsing errors

### Problems (needs investigation):
- ❌ Tasks failing with sync errors
- ❌ Multiple directory scans (deduplication not working)
- ❌ High master CPU (>50%)
- ❌ JSON errors still appearing
- ❌ gRPC connection errors

## Creating Test Spider

```bash
# Option 1: Via API
curl -X POST http://localhost:8080/api/spiders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-large-spider",
    "type": "customized"
  }'

# Option 2: Copy large project
docker exec crawlab_dev_master sh -c '
  mkdir -p /app/crawlab_workspace/YOUR_SPIDER_ID
  # Copy or generate 1000 files here
'
```

## See Also

- Full test spec: `tests/specs/cluster/CLS-003-file-sync-grpc-streaming-performance.md`
- Implementation doc: `docs/dev/20251020-file-sync-grpc-streaming/IMPLEMENTATION_COMPLETE.md`
- Testing SOP: `tests/TESTING_SOP.md`
