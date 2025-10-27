# API-007: Task Logs & Results

**Category**: API Testing  
**Priority**: P1 (Critical Foundation)  
**Estimated Time**: 10-15 minutes  
**Backend**: script

## Objective

Validate task log retrieval and result data endpoints.

**Endpoints Covered**:
- `GET /api/tasks/{id}/logs` - Get task execution logs
- `GET /api/tasks/{id}/results` - Get task scraped/crawled data

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- API accessible without proxy interference

## Test Steps

### Setup
1. Authenticate as admin and get JWT token
2. Create a test spider with a simple Python script that:
   - Prints logs to stdout
   - Saves data using Crawlab's result API

### Test Case 1: Task Logs Retrieval

**1.1 Create and run task**
- Create task for test spider
- Wait for task to complete
- Verify task reached 'finished' status

**1.2 Get task logs**
- Call `GET /api/tasks/{id}/logs`
- Verify response status code is 200
- Verify response contains 'data' field
- Verify logs contain expected output from spider script

**1.3 Test pagination parameters**
- Call logs endpoint with `page=1&size=100`
- Verify pagination works correctly
- Verify logs are returned in expected format (string or array)

**1.4 Test latest logs parameter**
- Call logs endpoint with `latest=true`
- Verify latest logs are returned
- Call with `latest=false`
- Verify historical logs are accessible

### Test Case 2: Task Results Retrieval

**2.1 Get task results**
- Call `GET /api/tasks/{id}/results`
- Verify response status code is 200
- Verify response contains 'data' field
- Verify data array contains saved results

**2.2 Verify result data structure**
- Check that results contain expected fields
- Verify data matches what spider saved
- Confirm result count matches expected

**2.3 Test pagination parameters**
- Call results endpoint with `page=1&size=5`
- Verify pagination works correctly
- Call with `page=2&size=5`
- Verify next page returns different results

### Test Case 3: Edge Cases

**3.1 Task without logs**
- Get logs for task that hasn't run yet (pending)
- Verify endpoint handles gracefully (empty logs or appropriate message)

**3.2 Task without results**
- Get results for task that saved no data
- Verify endpoint returns empty array
- Verify response structure is valid

**3.3 Invalid task ID**
- Call logs endpoint with non-existent task ID
- Verify appropriate error response
- Call results endpoint with invalid task ID
- Verify appropriate error response

### Cleanup
- Delete test task
- Delete test spider
- Verify cleanup successful

## Success Criteria

- All API calls return expected status codes
- Logs endpoint returns task execution output correctly
- Results endpoint returns scraped data correctly
- Pagination parameters work as expected
- Edge cases handled appropriately
- No data leaks or orphaned resources

## Expected Results

**Logs Response Format**:
```json
{
  "data": "string or array of log lines",
  "total": 100
}
```

**Results Response Format**:
```json
{
  "data": [
    {"field1": "value1", "field2": "value2"},
    ...
  ],
  "total": 10
}
```

## Notes

- Logs may be returned as string or array depending on backend implementation
- Results are always an array of objects
- Empty results/logs should return valid response structure
- Large log files may require pagination
- Results pagination is essential for tasks with many records
