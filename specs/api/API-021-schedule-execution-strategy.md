# API-021: Schedule Execution Strategy

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Time**: 20-25 minutes  
**Backend**: script

## Objective

Validate schedule execution strategy behavior (override, ignore, always) when schedules trigger while tasks are already running.

**Endpoints Covered**:
- `POST /api/schedules` - Create schedule with execution_strategy
- `POST /api/schedules/{id}/run` - Manually trigger schedule
- `GET /api/tasks` - Check running tasks
- `DELETE /api/tasks/{id}` - Cancel running task

**Feature Spec**: [specs/042-schedule-execution-strategy](../../specs/042-schedule-execution-strategy/README.md)

## Prerequisites

- Crawlab instance running at http://localhost:8080
- Valid admin credentials (admin/admin)
- Scheduler service running
- At least one worker node available

## Test Steps

### Setup
1. Authenticate as admin and get JWT token
2. Create a test spider with long-running task (sleep/delay script)

### Test Case 1: Default Strategy (Backward Compatibility)

**1.1 Create schedule without execution_strategy**
- Call `POST /api/schedules` without specifying `execution_strategy`
- Verify schedule created successfully
- Get schedule details
- Verify `execution_strategy` defaults to "always"

**1.2 Test default behavior**
- Run schedule to create first task
- While first task is running, run schedule again
- Verify both tasks run concurrently (always strategy)

### Test Case 2: Override Strategy

**2.1 Create schedule with override strategy**
- Create schedule with:
  - `spider_id`: Test spider ID
  - `name`: "Override Strategy Schedule"
  - `cron`: "0 0 * * *"
  - `enabled`: true
  - `execution_strategy`: "override"
- Verify schedule created with correct strategy

**2.2 Test override behavior - no running tasks**
- Trigger schedule (POST /schedules/{id}/run)
- Verify task created successfully
- Wait for task to start running

**2.3 Test override behavior - with running task**
- While first task is still running, trigger schedule again
- Expected behavior:
  - Old task should be cancelled
  - New task should be created after cancellation
- Verify:
  - Old task status becomes "cancelled" or "pending-cancel"
  - New task is created
  - New task eventually starts running
- List tasks and verify only one task is running at the end

**2.4 Test override with multiple running tasks**
- Start multiple tasks for the schedule
- Trigger schedule again
- Verify all old tasks are cancelled
- Verify new task is created

### Test Case 3: Ignore Strategy

**3.1 Create schedule with ignore strategy**
- Create schedule with:
  - `spider_id`: Test spider ID
  - `name`: "Ignore Strategy Schedule"
  - `cron`: "0 0 * * *"
  - `enabled`: true
  - `execution_strategy`: "ignore"
- Verify schedule created with correct strategy

**3.2 Test ignore behavior - no running tasks**
- Trigger schedule
- Verify task created successfully
- Task should start normally

**3.3 Test ignore behavior - with running task**
- While first task is still running, trigger schedule again
- Expected behavior:
  - Schedule should be skipped (no new task created)
  - Old task continues running
- Verify:
  - Task count for this schedule remains 1
  - Old task is not cancelled
  - No new task appears in task list
- Check logs for "skip schedule execution" message (if accessible)

**3.4 Test ignore strategy after task completes**
- Wait for first task to complete
- Trigger schedule again
- Verify new task is created (no running tasks blocking)

### Test Case 4: Always Strategy

**4.1 Create schedule with always strategy**
- Create schedule with:
  - `spider_id`: Test spider ID
  - `name`: "Always Strategy Schedule"
  - `cron`: "0 0 * * *"
  - `enabled`: true
  - `execution_strategy`: "always"
- Verify schedule created with correct strategy

**4.2 Test always behavior - concurrent execution**
- Trigger schedule to create first task
- While first task is running, trigger schedule again
- While both tasks are running, trigger schedule a third time
- Expected behavior:
  - All tasks run concurrently
  - No cancellation occurs
  - No skipping occurs
- Verify:
  - All 3 tasks exist in task list
  - All tasks have running or pending status
  - Task count for schedule increases with each trigger

### Test Case 5: Strategy Persistence

**5.1 Verify strategy after update**
- Create schedule with "always" strategy
- Update schedule to "ignore" strategy (PATCH)
- Get schedule details
- Verify `execution_strategy` changed to "ignore"
- Test ignore behavior works correctly

**5.2 Verify strategy after replacement**
- Get current schedule data
- Replace schedule (PUT) with "override" strategy
- Get schedule details
- Verify `execution_strategy` changed to "override"
- Test override behavior works correctly

### Test Case 6: Per-Schedule Isolation

**6.1 Create two schedules for same spider**
- Create schedule A with "override" strategy
- Create schedule B with "always" strategy
- Both schedules use the same spider

**6.2 Test schedule isolation**
- Trigger schedule A (creates task A1)
- While A1 is running, trigger schedule A again
- Expected: Task A1 should be cancelled, A2 created (override)
- Verify A1 cancelled, A2 running

**6.3 Test cross-schedule independence**
- Trigger schedule B while schedule A has running task
- Expected: Schedule B creates task without affecting schedule A
- Verify:
  - Schedule B task created and runs
  - Schedule A task unaffected
  - Both schedules operate independently

**6.4 Test schedule B always strategy**
- Trigger schedule B multiple times
- Verify all schedule B tasks run concurrently
- Verify no impact on schedule A tasks

### Test Case 7: Edge Cases

**7.1 Invalid execution_strategy value**
- Try to create schedule with invalid strategy "invalid_value"
- Verify appropriate error response or defaults to "always"

**7.2 Null or missing execution_strategy**
- Create schedule with `execution_strategy: null`
- Verify defaults to "always"

**7.3 Override with quickly completing tasks**
- Create schedule with override strategy
- Trigger schedule with fast-completing task
- Immediately trigger again before first completes
- Verify override behavior handles race condition

**7.4 Ignore with pending tasks**
- Create schedule with ignore strategy
- Create a pending task (not yet running)
- Trigger schedule
- Verify: Should skip if pending tasks exist for this schedule

### Cleanup
- Cancel all running tasks
- Delete all test schedules
- Delete test spider
- Verify cleanup successful

## Success Criteria

- Default strategy is "always" for backward compatibility
- Override strategy cancels running tasks before creating new ones
- Ignore strategy skips execution when tasks are running
- Always strategy allows concurrent task execution
- Strategy field persists correctly through updates
- Different schedules for same spider operate independently
- Each schedule only checks its own running tasks
- Edge cases handled appropriately
- No data leaks or orphaned resources

## Expected Results

**Schedule with execution_strategy**:
```json
{
  "data": {
    "_id": "schedule_id",
    "name": "Schedule Name",
    "spider_id": "spider_id",
    "cron": "0 0 * * *",
    "enabled": true,
    "execution_strategy": "override",
    "created_at": "2024-10-27T00:00:00Z"
  }
}
```

**Task Cancellation (Override)**:
- Task status changes to "cancelled" or "pending-cancel"
- New task created after cancellation confirmed

**Skipped Execution (Ignore)**:
- No new task in task list
- Log entry indicating skip (if available)

**Concurrent Execution (Always)**:
- Multiple tasks with same schedule_id running simultaneously

## Notes

- Execution strategy applies per-schedule, not per-spider
- Each schedule tracks only its own running tasks
- Different schedules for the same spider are independent
- Default strategy is "always" for backward compatibility
- Override strategy waits for cancellation confirmation
- Ignore strategy checks both running and pending tasks
- **Backend considers tasks with status `pending`, `assigned`, OR `running` as "running tasks"** for execution strategy purposes
- Test requires scheduler service to be running
- Long-running tasks recommended for testing (10+ seconds)
- Task cancellation may take time depending on implementation

## Implementation Notes

**Creating Long-Running Spider**:
```python
# Spider script for testing
import time
import sys

duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30
print(f"Starting long task, will run for {duration} seconds")
time.sleep(duration)
print("Task completed")
```

**Checking Running Tasks**:
```python
# List tasks filtered by schedule
tasks = task_helper.list_tasks(token, schedule_id=schedule_id, status="running")
running_count = len(tasks) if tasks else 0
```

**Verifying Task Cancellation**:
```python
# Check task status after override
task_data = task_helper.get_task(token, task_id)
assert task_data["status"] in ["cancelled", "pending-cancel"]
```

## History
- **Created**: 2025-12-16, AI Assistant
- **Modified**: -
