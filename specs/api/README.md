# API Testing Guide

## Quick Start

**ALWAYS check OpenAPI spec first before creating API tests!**

```bash
# Fetch and save the API spec
curl -s http://localhost:8080/api/openapi.json | jq . > /tmp/crawlab-api-spec.json

# Or explore interactively
curl -s http://localhost:8080/api/openapi.json | jq '.paths | keys'  # List all endpoints
```

## Common API Patterns

### 1. Spider Management

#### Create Spider
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders".post'

# Payload format - REQUIRES "data" wrapper
POST /api/spiders
{
  "data": {
    "name": "my-spider",
    "cmd": "python main.py",
    "description": "Spider description"
  }
}

# Response
{
  "data": {
    "_id": "68f7a0205323ee5e692a9984",
    "name": "my-spider",
    ...
  }
}
```

#### Save Spider File
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders/{id}/files/save".post'

# Payload format - Direct, no wrapper
POST /api/spiders/:id/files/save
{
  "path": "main.py",
  "data": "#!/usr/bin/env python\nprint('hello')"
}

# Response
{
  "data": null  # Void response on success
}
```

#### List Spider Files
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders/{id}/files/list".get'

# Request
GET /api/spiders/:id/files/list?path=/

# Response
{
  "data": [
    {
      "name": "main.py",
      "path": "main.py",
      "is_dir": false,
      ...
    }
  ]
}
```

### 2. Task Management

#### Run Task
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks/run".post'

# Payload format - Direct, no wrapper
POST /api/tasks/run
{
  "spider_id": "68f7a0205323ee5e692a9984",
  "cmd": "python main.py",
  "mode": "random",  # optional: random, all-nodes, selected-nodes
  "priority": 5      # optional
}

# Response - Returns ARRAY of task IDs
{
  "data": ["68f7a0205323ee5e692a9985"]
}
```

#### Get Task Status
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks/{id}".get'

# Request
GET /api/tasks/:id

# Response
{
  "data": {
    "_id": "68f7a0205323ee5e692a9985",
    "status": "finished",  # pending, running, finished, error, cancelled
    "spider_id": "68f7a0205323ee5e692a9984",
    ...
  }
}
```

#### Get Task Logs
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks/{id}/logs".get'

# Request
GET /api/tasks/:id/logs

# Response - Returns ARRAY of log lines
{
  "data": [
    "DEBUG [2025-10-21 23:04:39] [Crawlab] task started",
    "Spider starting...",
    "✓ File synced: main.py",
    ...
  ]
}
```

#### Batch Update Tasks
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks".patch'

# Check schema - NOTE: field name is "update" not "data"!
curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Batch_update_task_listInput'

# Request
PATCH /api/tasks
{
  "ids": ["task_id_1", "task_id_2"],
  "update": {               # ← Field name is "update" not "data"!
    "priority": 7,
    "description": "Updated description"
  }
}

# Response
{
  "data": {...}
}
```

#### Delete Multiple Tasks
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks".delete'

# Important: DELETE uses JSON body, not query params!
DELETE /api/tasks
{
  "ids": ["task_id_1", "task_id_2"]
}

# Response
{
  "data": null  # Void response on success
}
```

#### Restart Task
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks/{id}/restart".post'

# Request
POST /api/tasks/:id/restart

# Response - Returns ARRAY of new task IDs (not single object!)
{
  "data": ["new_task_id"]
}
```

### 3. Authentication

#### Login
```bash
# Check endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/login".post'

# Request
POST /api/login
{
  "username": "admin",
  "password": "admin"
}

# Response - Returns token string
{
  "data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Use token in subsequent requests
Authorization: Bearer <token>
```

## Common Pitfalls

### ❌ Wrong: Assuming payload format
```python
# Don't guess!
response = requests.post(f"{API_URL}/spiders", json={
    "name": "my-spider",  # Missing "data" wrapper - will fail!
    "cmd": "python main.py"
})
```

### ✅ Right: Check OpenAPI spec first
```python
# Check spec first:
# curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Create_spiderInput'
# Shows: {"data": {...}} wrapper required

response = requests.post(f"{API_URL}/spiders", json={
    "data": {
        "name": "my-spider",
        "cmd": "python main.py"
    }
})
```

### ❌ Wrong: Expecting single object when API returns array
```python
task_id = response.json().get('data', {}).get('_id')  # Fails if data is array!
```

### ✅ Right: Check response format in spec
```python
# /tasks/run returns array of IDs
task_ids = response.json().get('data', [])
task_id = task_ids[0] if task_ids else None
```

### ❌ Wrong: Treating logs as string when it's an array
```python
logs = response.json().get('data', '')
if "✓ File synced" in logs:  # Fails if logs is array!
```

### ✅ Right: Handle different log formats
```python
logs_data = response.json().get('data', '')
if isinstance(logs_data, list):
    logs = '\n'.join(logs_data)
else:
    logs = str(logs_data) if logs_data else ''
```

### ❌ Wrong: Guessing batch operation field names
```python
# Wrong field name - will fail!
response = requests.patch(f"{API_URL}/tasks", json={
    "ids": task_ids,
    "data": {"priority": 7}  # Should be "update" not "data"!
})
```

### ✅ Right: Check schema for exact field names
```python
# Check spec first:
# curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Batch_update_task_listInput'
# Shows: {"ids": [...], "update": {...}}

response = requests.patch(f"{API_URL}/tasks", json={
    "ids": task_ids,
    "update": {"priority": 7}  # Correct field name
})
```

### ❌ Wrong: Using query params for DELETE
```python
# Wrong - sends as "?ids=id1,id2" which MongoDB can't parse as array
response = requests.delete(f"{API_URL}/tasks", params={"ids": ",".join(task_ids)})
# Error: "$in needs an array"
```

### ✅ Right: DELETE endpoints can use JSON body
```python
# Correct - sends JSON body with array
response = requests.delete(f"{API_URL}/tasks", 
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"ids": task_ids}
)
```

## Workflow for Creating API Tests

1. **Identify endpoints needed**
   ```bash
   # List all endpoints
   curl -s http://localhost:8080/api/openapi.json | jq '.paths | keys'
   ```

2. **Check each endpoint schema**
   ```bash
   # Check specific endpoint
   curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders".post'
   
   # Check request body schema
   curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Create_spiderInput'
   ```

3. **Document findings in test spec**
   - Include endpoint paths
   - Include example payloads
   - Note wrapper requirements
   - Note response format (object vs array)

4. **Write test implementation**
   - Use documented payloads
   - Handle response formats correctly
   - Add error handling

5. **Test against live API**
   ```bash
   cd tests
   ./cli.py --spec API-XXX
   ```

## Tips

- **Save the spec locally** for quick reference: `curl -s http://localhost:8080/api/openapi.json > /tmp/api-spec.json`
- **Use jq for filtering**: Much faster than reading whole spec
- **Check for "required" fields**: `jq '.components.schemas.Create_spiderInput.required'`
- **Look for examples**: Some schemas include example payloads
- **Test incrementally**: Test each API call separately before combining
- **Check HTTP status codes**: Not all errors return 4xx/5xx (some return 200 with error in body)

## Example: Complete API Test Flow

```python
import requests

API_URL = "http://localhost:8080/api"

# 1. Login (checked spec: returns token string)
response = requests.post(f"{API_URL}/login", json={
    "username": "admin",
    "password": "admin"
})
token = response.json().get('data')
headers = {"Authorization": f"Bearer {token}"}

# 2. Create spider (checked spec: requires "data" wrapper)
response = requests.post(f"{API_URL}/spiders", 
    headers=headers,
    json={"data": {
        "name": "test-spider",
        "cmd": "python main.py"
    }}
)
spider_id = response.json().get('data', {}).get('_id')

# 3. Save file (checked spec: direct payload, no wrapper)
response = requests.post(f"{API_URL}/spiders/{spider_id}/files/save",
    headers=headers,
    json={
        "path": "main.py",
        "data": "print('hello')"
    }
)

# 4. Run task (checked spec: returns array of IDs)
response = requests.post(f"{API_URL}/tasks/run",
    headers=headers,
    json={
        "spider_id": spider_id,
        "cmd": "python main.py"
    }
)
task_ids = response.json().get('data', [])
task_id = task_ids[0] if task_ids else None

# 5. Get logs (checked spec: returns array of strings)
response = requests.get(f"{API_URL}/tasks/{task_id}/logs",
    headers=headers
)
logs_data = response.json().get('data', [])
logs = '\n'.join(logs_data) if isinstance(logs_data, list) else str(logs_data)
```

## Reference

- **Live API**: http://localhost:8080/api
- **OpenAPI Spec**: http://localhost:8080/api/openapi.json
- **API Test Example**: [API-001](./API-001-task-execution-with-file-sync.md)
- **Test Runner**: `./cli.py --spec API-XXX`

---

**Remember**: The OpenAPI spec is the source of truth. Always check it before writing API tests! 🎯
