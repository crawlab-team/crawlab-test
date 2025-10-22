# Schedule Management Test Specification

## Overview
Test the spider scheduling system including cron expressions, schedule management, and automated execution.

## Test Environment
- **Target URL**: `http://localhost:5173`
- **Test Database**: `mongodb://dev_user:dev_password@localhost:27018/crawlab_test?authSource=admin`
- **Prerequisites**: Authenticated user, at least one spider created

---

## Test Cases

### TC-06-01: Create Basic Schedule
**Objective**: Verify creating a simple cron schedule for a spider
**Priority**: High
**Estimated Duration**: 3 minutes

**Steps**:
1. Navigate to Spider Management
2. Select an existing spider
3. Click on "Schedule" tab
4. Click "Add Schedule" button
5. Set schedule name: "Daily Execution"
6. Set cron expression: "0 9 * * *" (daily at 9 AM)
7. Verify cron expression preview shows "At 09:00 AM"
8. Save the schedule
9. Verify schedule appears in the list
10. Verify schedule status is "Active"

**Expected Results**:
- Schedule creation form accepts valid cron expressions
- Preview correctly interprets cron expression
- Schedule is saved and listed with correct details
- Schedule can be enabled/disabled

### TC-06-02: Advanced Cron Expression
**Objective**: Test complex cron expressions and validation
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Create new schedule with expression: "0 */2 8-18 * 1-5"
2. Verify preview: "Every 2 hours between 08:00 AM and 06:00 PM, Monday through Friday"
3. Test invalid expression: "* * * * * *" (6 fields instead of 5)
4. Verify error message appears
5. Test edge case: "59 23 31 12 *" (December 31st at 11:59 PM)
6. Save valid complex schedule
7. Edit existing schedule to change frequency
8. Verify changes are applied correctly

**Expected Results**:
- Complex cron expressions are correctly parsed
- Invalid expressions show appropriate error messages
- Cron preview accurately describes timing
- Schedule modifications work properly

### TC-06-03: Schedule Execution History
**Objective**: Verify schedule execution tracking and history
**Priority**: High
**Estimated Duration**: 5 minutes

**Steps**:
1. Navigate to scheduled spider
2. View "Execution History" section
3. Verify history shows:
   - Execution timestamp
   - Duration
   - Status (Success/Failed)
   - Results count
4. Click on a specific execution to view details
5. Verify execution logs are accessible
6. Check execution statistics and metrics
7. Test filtering history by date range
8. Test filtering by execution status

**Expected Results**:
- Execution history is comprehensive and accurate
- Individual execution details are accessible
- Filtering options work correctly
- Performance metrics are displayed

### TC-06-04: Schedule Conflict Management
**Objective**: Test handling of overlapping schedules
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Create schedule for spider: "0 10 * * *"
2. Create overlapping schedule: "30 9 * * *" (30 min before)
3. Set spider execution time to 2 hours (longer than interval)
4. Verify system handles overlap gracefully
5. Check queue management for scheduled tasks
6. Test concurrent execution limits
7. Verify notifications for schedule conflicts
8. Test manual execution during scheduled time

**Expected Results**:
- System prevents or manages schedule conflicts
- Queue system handles overlapping executions
- Clear notifications about conflicts
- Manual executions don't interfere with schedules

### TC-06-05: Schedule Timezone Handling
**Objective**: Verify timezone support for schedules
**Priority**: Medium
**Estimated Duration**: 3 minutes

**Steps**:
1. Check current system timezone display
2. Create schedule with specific timezone: "UTC"
3. Create another schedule with local timezone
4. Verify both schedules show correct next execution time
5. Change system timezone (if possible)
6. Verify schedules adjust appropriately
7. Test daylight saving time transitions
8. Verify execution logs show correct timestamps

**Expected Results**:
- Timezones are clearly indicated
- Schedule times are calculated correctly
- Timezone changes are handled properly
- Execution times are accurate across timezones

### TC-06-06: Bulk Schedule Operations
**Objective**: Test managing multiple schedules efficiently
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Create 5 different schedules for various spiders
2. Use bulk select to choose 3 schedules
3. Enable all selected schedules at once
4. Disable all selected schedules
5. Delete multiple schedules simultaneously
6. Verify bulk operations affect only selected items
7. Test "Select All" functionality
8. Verify bulk operation confirmations work

**Expected Results**:
- Bulk operations work correctly
- Only selected items are affected
- Confirmation dialogs prevent accidental changes
- Operations complete successfully for all selected items

### TC-06-07: Schedule Notifications
**Objective**: Test notification system for scheduled executions
**Priority**: Medium
**Estimated Duration**: 3 minutes

**Steps**:
1. Configure notification settings for schedule
2. Set up notifications for:
   - Successful execution
   - Failed execution
   - Schedule disabled
3. Trigger each notification type
4. Verify notifications are sent correctly
5. Test notification preferences per schedule
6. Check notification history and logs
7. Test notification channel preferences

**Expected Results**:
- Notifications are sent for configured events
- Notification content is accurate and helpful
- User preferences are respected
- Notification history is maintained

### TC-06-08: Schedule Performance and Monitoring
**Objective**: Verify schedule performance monitoring
**Priority**: Low
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to schedule monitoring dashboard
2. View schedule performance metrics:
   - Success rate
   - Average execution time
   - Resource usage
3. Check schedule load distribution
4. Verify performance trends over time
5. Test performance alerts and thresholds
6. Check system resource impact of schedules
7. Verify optimization recommendations

**Expected Results**:
- Performance metrics are accurate
- Trends and analytics are helpful
- System provides optimization insights
- Resource usage is monitored effectively

---

## Test Data Requirements

### Sample Cron Expressions
- **Daily**: `0 9 * * *`
- **Hourly**: `0 * * * *`
- **Weekly**: `0 9 * * 1`
- **Complex**: `0 */2 8-18 * 1-5`

### Test Spiders
- Fast execution spider (< 1 minute)
- Medium execution spider (5-10 minutes)
- Long execution spider (> 30 minutes)

## Success Criteria
- All cron expressions are correctly validated and parsed
- Schedule execution is reliable and accurate
- Performance monitoring provides useful insights
- Bulk operations work efficiently
- Timezone handling is robust

## Performance Benchmarks
- Schedule creation: < 2 seconds
- Cron validation: < 1 second
- History loading: < 3 seconds
- Bulk operations: < 5 seconds for 10 items
