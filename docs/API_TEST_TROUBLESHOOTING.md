# API Test Troubleshooting Checklist

## When API Tests Fail - DO THIS FIRST ⚡

### Step 1: Check OpenAPI Spec (< 30 seconds)

```bash
# Check endpoint definition
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/databases/{id}/connection/test"'

# Check request body schema
curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Create_database_tableInput'

# Search for endpoint
curl -s http://localhost:8080/api/openapi.json | jq '.paths | keys | map(select(. | contains("database")))'
```

### Step 2: Compare with Helper Code

- Does helper match OpenAPI request format?
- Does helper parse response correctly?
- Are field names case-sensitive correct?
- Is HTTP method correct (GET/POST/PUT/DELETE)?

### Step 3: Check Infrastructure

```bash
# Are required services running?
docker ps | grep -E "mysql|postgres|mongo|elasticsearch"

# Can backend reach them?
docker exec crawlab_master ping -c 1 mysql
```

### Step 4: Only If Still Unclear - Read Backend Code

```bash
# Find controller
rg "func.*TestConnection" --type go

# Read implementation
vim core/controllers/database.go +182
```

## Common API Patterns in Crawlab

### Response Formats

| Pattern | Example Endpoints | Format |
|---------|------------------|---------|
| Standard | Most endpoints | `{status: "ok", message: "success", data: {...}}` |
| Void Response | Connection test, mutations | `{status: "ok", message: "success"}` or `{error: "..."}` |
| List Response | GET /databases | `{status: "ok", data: [...], total: N}` |

### Request Patterns

| Operation | Body Structure | Notes |
|-----------|---------------|-------|
| Create | `{"data": {...}}` | Wrapped in data field |
| Batch Update | `{"ids": [...], "update": {...}}` | Field is "update" not "data" |
| Batch Delete | `{"ids": [...]}` | DELETE with JSON body |
| Batch Insert | `{"rows": [{"status": "new", "row": {...}}]}` | Row-based operations |

## Red Flags 🚩

If you see these, CHECK OPENAPI FIRST:
- "Unknown error" → Response format mismatch
- 400 Bad Request → Wrong request body structure
- 404 Not Found → Wrong endpoint or HTTP method
- Field validation errors → Case-sensitive or missing required fields

## Time Saved

- ✅ Check OpenAPI first: **1 minute**
- ❌ Trial and error: **10-30 minutes**
- ❌ Reading Go code first: **5-10 minutes**

**Always start with OpenAPI!**
