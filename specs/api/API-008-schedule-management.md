# API-008: Schedule Management

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Time**: 15-20 minutes  
**Backend**: script

## Objective

Validate schedule CRUD operations and schedule control endpoints (enable/disable/run).

**Endpoints Covered**:
- `POST /api/schedules` - Create schedule
- `GET /api/schedules` - List schedules (with pagination, filtering)
- `GET /api/schedules/{id}` - Get schedule details
- `PATCH /api/schedules/{id}` - Update schedule (partial)
- `PUT /api/schedules/{id}` - Replace schedule (full)
- `DELETE /api/schedules/{id}` - Delete schedule
- `PATCH /api/schedules` - Batch update schedules
- `DELETE /api/schedules` - Batch delete schedules
- `POST /api/schedules/{id}/enable` - Enable schedule
- `POST /api/schedules/{id}/disable` - Disable schedule
- `POST /api/schedules/{id}/run` - Run schedule immediately

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- At least one spider created for testing schedules

## Test Steps

### Setup
1. Authenticate as admin and get JWT token
2. Create a test spider for schedule association

### Test Case 1: Create Schedule

**1.1 Create schedule with valid data**
- Call `POST /api/schedules` with:
  - `spider_id`: Test spider ID
  - `name`: "Test Daily Schedule"
  - `cron`: "0 0 * * *" (daily at midnight)
  - `enabled`: true
- Verify response status code is 200
- Verify response contains schedule ID
- Verify schedule has correct properties

**1.2 Verify schedule creation**
- Call `GET /api/schedules/{id}` with created schedule ID
- Verify schedule details match creation data
- Verify schedule is enabled

### Test Case 2: List Schedules

**2.1 List all schedules**
- Call `GET /api/schedules`
- Verify response status code is 200
- Verify response contains data array
- Verify created schedule is in list

**2.2 List with pagination**
- Call `GET /api/schedules?page=1&size=5`
- Verify pagination works correctly
- Verify total count is returned

**2.3 Filter by spider**
- Call `GET /api/schedules` with spider_id filter
- Verify only schedules for that spider are returned

### Test Case 3: Update Schedule

**3.1 Partial update (PATCH)**
- Call `PATCH /api/schedules/{id}` with:
  - `name`: "Updated Schedule Name"
  - `cron`: "0 12 * * *" (daily at noon)
- Verify update succeeds
- Verify updated fields are changed
- Verify other fields remain unchanged

**3.2 Full replacement (PUT)**
- Get current schedule data
- Modify multiple fields
- Call `PUT /api/schedules/{id}` with full object
- Verify replacement succeeds
- Verify all fields match new data

### Test Case 4: Schedule Control

**4.1 Disable schedule**
- Call `POST /api/schedules/{id}/disable`
- Verify response status code is 200
- Get schedule details
- Verify `enabled` field is false

**4.2 Enable schedule**
- Call `POST /api/schedules/{id}/enable`
- Verify response status code is 200
- Get schedule details
- Verify `enabled` field is true

**4.3 Run schedule immediately**
- Call `POST /api/schedules/{id}/run`
- Verify response status code is 200
- Verify response contains task ID(s)
- Verify task was created for the scheduled spider

### Test Case 5: Batch Operations

**5.1 Create additional schedules**
- Create 2 more test schedules
- Verify all created successfully

**5.2 Batch update**
- Call `PATCH /api/schedules` with:
  - `ids`: Array of schedule IDs
  - `update`: `{"priority": 10}`
- Verify batch update succeeds
- Verify all schedules have updated priority

**5.3 Batch delete**
- Call `DELETE /api/schedules` with schedule IDs
- Verify batch delete succeeds
- Verify schedules no longer exist

### Test Case 6: Delete Schedule

**6.1 Delete single schedule**
- Call `DELETE /api/schedules/{id}`
- Verify response status code is 200
- Verify schedule no longer exists

**6.2 Verify deletion**
- Try to get deleted schedule
- Verify appropriate error response

### Test Case 7: Edge Cases

**7.1 Invalid cron expression**
- Try to create schedule with invalid cron
- Verify appropriate error response

**7.2 Non-existent spider**
- Try to create schedule with invalid spider_id
- Verify appropriate error response

**7.3 Duplicate schedule name**
- Create schedule with same name as existing
- Verify system handles appropriately (allow or reject)

### Cleanup
- Delete all test schedules
- Delete test spider
- Verify cleanup successful

## Success Criteria

- All CRUD operations work correctly
- Pagination and filtering function as expected
- Enable/disable toggle works properly
- Run schedule creates tasks correctly
- Batch operations handle multiple schedules
- Edge cases handled appropriately
- No data leaks or orphaned resources

## Expected Results

**Schedule Response Format**:
```json
{
  "data": {
    "_id": "schedule_id",
    "name": "Schedule Name",
    "spider_id": "spider_id",
    "cron": "0 0 * * *",
    "enabled": true,
    "mode": "random",
    "priority": 5,
    "created_at": "2024-10-27T00:00:00Z"
  }
}
```

**List Response Format**:
```json
{
  "data": [...],
  "total": 10
}
```

## Notes

- Cron expressions follow standard cron format
- Enabled schedules will trigger automatically based on cron
- Disabled schedules can still be run manually
- Schedule names don't need to be unique (system may allow duplicates)
- Running a schedule creates a task immediately (bypasses cron timing)
