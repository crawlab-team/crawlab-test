# gRPC Server Debugging Utilities

## Overview

Enhanced debugging utilities for diagnosing gRPC server connectivity issues in CLS-003 and other cluster tests.

## New Functions in `grpc_sync_client.py`

### 1. `verify_grpc_server_accessible()`

Checks if the gRPC server port is accessible via TCP socket connection.

```python
from helpers.cluster.grpc_sync_client import verify_grpc_server_accessible

result = verify_grpc_server_accessible(
    host='localhost',
    port=9666,
    max_retries=10,
    logger=logger
)

if result['accessible']:
    print(f"Connected in {result['latency_ms']}ms")
else:
    print(f"Failed: {result['error']}")
```

**Returns:**
```python
{
    'accessible': bool,      # True if port is reachable
    'attempts': int,         # Number of attempts made
    'error': Optional[str],  # Error message if failed
    'latency_ms': Optional[float]  # Connection latency
}
```

### 2. `test_grpc_connection()`

Tests actual gRPC RPC call to verify the server is functional.

```python
from helpers.cluster.grpc_sync_client import test_grpc_connection

result = test_grpc_connection(
    host='localhost',
    port=9666,
    spider_id='test',
    logger=logger
)

if result['success']:
    print("gRPC server is operational")
else:
    print(f"RPC failed: {result['error_code']}: {result['error_details']}")
```

**Returns:**
```python
{
    'success': bool,             # True if RPC succeeded
    'error': Optional[str],      # Human-readable error
    'error_code': Optional[str], # gRPC status code name
    'error_details': Optional[str]  # Detailed error message
}
```

### 3. Enhanced `GrpcSyncClient`

**Improvements:**
- Better error messages with gRPC status code names
- Distinguishes between connection errors and RPC errors
- Returns `error_code` in scan results for easier debugging

```python
client = GrpcSyncClient()
client.connect()
result = client.scan_files_full('spider-id', '')

# Now includes error_code
if not result['success']:
    print(f"Error: {result['error_code']}: {result['error']}")
```

## CLS-003 Test Improvements

### Pre-Test Verification

The test now includes comprehensive pre-flight checks:

```
🔍 Verifying gRPC Server Availability
   Checking gRPC port binding inside container...
   ✓ Port 9666 is bound and listening inside container
   
   Checking for gRPC server process...
   ✓ Crawlab process running
   
   Testing gRPC connectivity from host...
   ✓ gRPC server accessible on localhost:9666 (latency: 2.45ms)
   
   Testing gRPC RPC call...
   ✓ gRPC RPC call successful
   ✓ gRPC server is fully operational
```

### Enhanced Error Reporting

When gRPC calls fail, you now get detailed diagnostics:

```
⚠️  gRPC Error Summary:
   UNAVAILABLE: 85 occurrences
   DEADLINE_EXCEEDED: 10 occurrences
   UNAUTHENTICATED: 5 occurrences
```

### Container Diagnostics

Automatic diagnostics when connectivity fails:

```
🔍 Additional Diagnostics:
   ✓ Container is reachable via Docker

⚠️  WARNING: gRPC server connectivity issues detected!
   Tests may fail. Possible causes:
   1. gRPC server not started (check CRAWLAB_GRPC_ENABLED env)
   2. Port not properly bound (check server logs)
   3. Network connectivity issue
   4. Server startup delay (may succeed after retry)
```

## Common Error Codes

### gRPC Status Codes

| Code | Meaning | Likely Cause |
|------|---------|--------------|
| `UNAVAILABLE` | Server not reachable | Port not bound, server not started |
| `UNAUTHENTICATED` | Auth failed | Wrong auth key or missing credentials |
| `DEADLINE_EXCEEDED` | Timeout | Server overloaded or network slow |
| `UNIMPLEMENTED` | RPC not found | Protobuf mismatch or wrong endpoint |
| `INVALID_ARGUMENT` | Bad request | Missing required fields |
| `INTERNAL` | Server error | Server crash or bug |

### Connection Errors

| Error | Meaning | Likely Cause |
|-------|---------|--------------|
| `Connection refused` | Port not listening | Server not started or wrong port |
| `Connection timeout` | No response | Network issue or firewall |
| `RuntimeError` | gRPC library error | Protobuf or library issue |

## Debugging Workflow

### 1. Check Port Accessibility
```bash
# From host machine
nc -zv localhost 9666

# Expected: "Connection to localhost 9666 port [tcp/*] succeeded!"
```

### 2. Check Inside Container
```bash
docker exec <container> netstat -tlnp | grep 9666
# Should show: "LISTEN" on 0.0.0.0:9666 or :::9666
```

### 3. Check Server Logs
```bash
docker logs <container> | grep -i grpc
# Look for: "gRPC server started on :9666"
```

### 4. Test Connection
```python
from helpers.cluster.grpc_sync_client import verify_grpc_server_accessible

result = verify_grpc_server_accessible(host='localhost', port=9666)
print(result)
```

### 5. Test RPC Call
```python
from helpers.cluster.grpc_sync_client import test_grpc_connection

result = test_grpc_connection(host='localhost', port=9666)
print(result)
```

## GitHub Actions Integration

The enhanced diagnostics work automatically in CI/CD:

```yaml
- name: Run CLS-003
  run: |
    cd tests
    ./cli.py --spec CLS-003 --ci
```

If connectivity fails, the test output will include:
- Port binding status inside container
- Process information
- Connection test results
- Detailed error codes
- Diagnostic suggestions

## Environment Variables

### gRPC Server Configuration

```bash
# Enable gRPC server (if disabled by default)
CRAWLAB_GRPC_ENABLED=true

# Custom port (default: 9666)
CRAWLAB_GRPC_PORT=9666

# Auth key (default: Crawlab2024!)
CRAWLAB_GRPC_AUTH_KEY=your-secret-key
```

### Test Configuration

```bash
# Skip gRPC verification (not recommended)
CLS003_SKIP_VERIFICATION=true

# Custom gRPC timeout
CLS003_GRPC_TIMEOUT=30
```

## Troubleshooting

### Issue: "Connection refused"

**Symptoms:** Port check fails, no connection

**Solutions:**
1. Check if master container is running: `docker ps`
2. Verify port mapping: `docker port <container> 9666`
3. Check server logs: `docker logs <container> | grep grpc`
4. Ensure `CRAWLAB_GRPC_ENABLED=true` is set

### Issue: "UNAUTHENTICATED"

**Symptoms:** Port accessible, but RPC calls fail with auth error

**Solutions:**
1. Check if auth key matches server configuration
2. Update `GrpcSyncClient` auth_key parameter
3. Check for environment variable overrides

### Issue: "UNAVAILABLE" 

**Symptoms:** Intermittent failures, some calls succeed

**Solutions:**
1. Check server resource usage (CPU/memory)
2. Increase connection timeout
3. Reduce concurrent request count
4. Check for server rate limiting

### Issue: Test fails in GitHub Actions but works locally

**Differences to consider:**
1. GitHub Actions may have stricter timeouts
2. Network latency may be higher
3. Resource limits may be tighter
4. Multiple tests may run concurrently

**Solutions:**
1. Check GitHub Actions logs for specific errors
2. Increase timeouts for CI environment
3. Add retry logic for flaky connections
4. Use the pre-test verification to catch issues early

## Future Enhancements

- [ ] Add metrics collection for gRPC performance
- [ ] Implement automatic retry with exponential backoff
- [ ] Add health check endpoint for continuous monitoring
- [ ] Support for TLS/SSL connections
- [ ] Connection pooling for better performance
