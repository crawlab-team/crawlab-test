# API-006: Task CRUD & Execution

**Category**: API Testing  
**Priority**: P1 (Critical Foundation)  
**Estimated Time**: 10 minutes  
**Backend**: script

## Objective

Validate task lifecycle management including:
- Task creation (CRUD operations)
- Task execution (run, cancel, restart)
- Task status tracking
- Task list operations (filter, pagination, batch operations)

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin:admin)
- At least one spider created for testing

## Test Steps

### Setup
1. Login and get authentication token
2. Create a test spider for task operations
3. Initialize cleanup tracking

### Task Execution Operations

#### 1. Run Task via /tasks/run
- POST to `/api/tasks/run` with spider_id
- Verify response contains task ID
- Validate task is created and in pending/running status
- GET task details to confirm creation

#### 2. Run Task with Parameters
- POST to `/api/tasks/run` with spider_id, cmd, mode, param, priority
- Verify all parameters are stored correctly
- Check task has correct priority value

#### 3. Run Task on Specific Nodes
- POST to `/api/tasks/run` with spider_id and node_ids array
- Verify node assignment is correct
- Note: May need actual worker nodes for full validation

#### 4. Cancel Running Task
- Create a long-running task
- POST to `/api/tasks/{id}/cancel`
- Verify task status changes to cancelled
- Test force cancel with `force: true`

#### 5. Restart Completed Task
- Wait for a task to complete
- POST to `/api/tasks/{id}/restart`
- Verify new task ID is returned
- Check new task has same spider_id and parameters

### Task CRUD Operations

#### 6. Get Task List
- GET `/api/tasks` without parameters
- Verify response contains task array and total count
- Check default sorting (descending by _id)

#### 7. Get Task List with Pagination
- GET `/api/tasks?page=1&size=5`
- Verify only 5 tasks returned
- GET `/api/tasks?page=2&size=5`
- Verify different set of tasks returned

#### 8. Get Task List with Filtering
- GET `/api/tasks?filter={"spider_id":"<spider_id>"}`
- Verify only tasks for that spider returned
- Test status filter: `filter={"status":"finished"}`

#### 9. Get Task List with Sorting
- GET `/api/tasks?sort=created_at` (ascending)
- GET `/api/tasks?sort=-created_at` (descending)
- Verify sort order is correct

#### 10. Get Task by ID
- GET `/api/tasks/{id}` for a specific task
- Verify full task details returned
- Check spider relationship is populated

#### 11. Update Task by ID (PATCH)
- PATCH `/api/tasks/{id}` with partial update (e.g., `{"priority": 5}`)
- Verify only specified fields updated
- GET task to confirm changes

#### 12. Replace Task by ID (PUT)
- PUT `/api/tasks/{id}` with full task object
- Verify all fields replaced
- Note: May have limitations on what can be updated

#### 13. Delete Task by ID
- Create a test task
- DELETE `/api/tasks/{id}`
- Verify task deleted (404 on subsequent GET)

#### 14. Batch Update Tasks
- Create multiple test tasks
- PATCH `/api/tasks` with array of IDs and updates
- Verify all tasks updated correctly

#### 15. Delete Multiple Tasks
- Create multiple test tasks
- DELETE `/api/tasks` with IDs in query or body
- Verify all tasks deleted

### Cleanup
1. Delete all test tasks created
2. Delete test spider
3. Logout

## Success Criteria

- ✅ Task execution works (run, cancel, restart)
- ✅ Task CRUD operations succeed
- ✅ Pagination and filtering work correctly
- ✅ Batch operations handle multiple tasks
- ✅ Task status tracking is accurate
- ✅ All test resources cleaned up

## Expected Behavior

### Task Statuses
- `pending`: Task created, waiting for execution
- `assigned`: Task assigned to a node
- `running`: Task currently executing
- `finished`: Task completed successfully
- `error`: Task failed with error
- `cancelled`: Task cancelled by user
- `abnormal`: Task terminated abnormally

### Task Lifecycle
1. Create task via `/tasks/run` → status: pending
2. Scheduler assigns to node → status: assigned
3. Node starts execution → status: running
4. Task completes → status: finished/error
5. Can restart finished/error tasks → new task created

### API Response Formats
- Single task: `{"data": {...}}`
- Task list: `{"data": [...], "total": N}`
- Task ID on creation: `{"data": "ObjectID string"}`

## Known Issues

- None identified yet

## Notes

- Task execution requires running worker nodes
- Long-running tasks may timeout in tests (use simple spiders)
- Batch operations may have size limits
- Some task fields may be read-only after creation
- Task logs/results tested separately in API-007
