# UI-006 - Schedule Management

## Metadata
- **Category**: ui
- **Priority**: high
- **Complexity**: medium
- **Duration**: 10-12 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser, at least one spider

## Scenario
This test validates spider scheduling functionality through the web interface, including creating schedules with cron expressions, managing schedule states, viewing execution history, and handling schedule conflicts.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080
- Valid user credentials (admin/admin)
- At least one spider exists in the system
- Browser with JavaScript enabled
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-001**: Spider Management (for spider-schedule relationship)
- **UI-003**: Task Management (for scheduled task execution)

## Test Steps

### Step 1: Navigate to Spider Schedules Tab
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080 and log in if needed
2. Navigate to the Spiders page
3. Click on any spider name to open spider detail page
4. Take a snapshot to see available tabs
5. Find and click the "Schedules" or "Schedule" tab
6. Wait for schedules interface to load
7. Take a snapshot to verify schedules view

**Expected**: Spider schedules tab displays schedule management interface
**Validation**: 
- URL contains spider detail route
- Schedules tab is active
- Schedule list or table is visible (may show "No schedules" if empty)
- "Create Schedule" or "Add Schedule" button is present
- Interface is ready for schedule management

---

### Step 2: Create Basic Schedule with Simple Cron
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From spider schedules tab, find and click "Create Schedule" or "Add Schedule" button
2. Wait for schedule creation form/dialog to appear
3. Take a snapshot to see form structure
4. Fill out the schedule creation form:
   - **Name**: "test-daily-schedule-ui-006"
   - **Cron Expression**: "0 9 * * *" (daily at 9 AM)
   - **Description**: "Automated test schedule"
   - **Enabled**: Ensure toggle is enabled/checked
5. Look for cron expression preview or description
6. Verify preview shows something like "At 09:00 AM" or "Daily at 9:00"
7. Find and click save/create button
8. Wait for form to close and schedule to appear in list

**Expected**: Basic schedule is created with cron expression
**Validation**: 
- Schedule creation form appears
- Cron expression field accepts the value
- Cron preview/description displays correctly
- Form saves successfully
- Schedule "test-daily-schedule-ui-006" appears in schedules list
- Schedule shows as enabled/active
- No validation errors appear

---

### Step 3: Create Complex Cron Expression
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Click "Create Schedule" again to add another schedule
2. Take a snapshot
3. Fill out form for complex schedule:
   - **Name**: "test-complex-schedule-ui-006"
   - **Cron Expression**: "0 */2 8-18 * 1-5" (every 2 hours, 8AM-6PM, weekdays)
   - **Description**: "Complex cron test"
   - **Enabled**: Toggle enabled
4. Verify cron preview shows appropriate description (e.g., "Every 2 hours between 08:00 and 18:00, Monday through Friday")
5. Save the schedule
6. Verify it appears in the schedules list
7. Check that both schedules are now visible

**Expected**: Complex cron expression is accepted and parsed correctly
**Validation**: 
- Complex cron expression is accepted
- Preview accurately describes the schedule timing
- Schedule saves successfully
- Both schedules appear in list
- Each schedule shows correct name and description

---

### Step 4: Test Invalid Cron Expression
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Click "Create Schedule" to test validation
2. Fill out form with invalid cron:
   - **Name**: "test-invalid"
   - **Cron Expression**: "* * * * * *" (6 fields, should be 5)
3. Try to save the form
4. Take a snapshot to see validation error
5. Verify error message appears indicating invalid cron expression
6. Change to another invalid format: "invalid cron"
7. Verify validation prevents saving
8. Cancel or close the form without saving

**Expected**: Invalid cron expressions are rejected with clear error messages
**Validation**: 
- Form validation detects invalid cron syntax
- Error message is displayed clearly
- Form cannot be saved with invalid expression
- Error describes the problem (e.g., "Invalid cron expression format")
- Form can be cancelled without side effects

---

### Step 5: Edit Existing Schedule
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From schedules list, find "test-daily-schedule-ui-006"
2. Take a snapshot to locate edit functionality
3. Find edit button/action (may be in actions column or more options menu)
4. Click edit to open schedule editing form
5. Modify the schedule:
   - Change cron expression to "0 10 * * *" (10 AM instead of 9 AM)
   - Update description to "Updated test schedule"
6. Verify cron preview updates to show new time
7. Save the changes
8. Verify schedule updates in the list
9. Check that updated cron and description are displayed

**Expected**: Schedule editing works correctly
**Validation**: 
- Edit functionality is accessible
- Form pre-populates with current schedule values
- Cron expression can be modified
- Preview updates with new cron
- Changes save successfully
- Updated schedule displays new values
- No errors during edit operation

---

### Step 6: Test Schedule Enable/Disable
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From schedules list, locate enabled toggle or status for "test-daily-schedule-ui-006"
2. Take a snapshot to see current state
3. If toggle switch is available:
   - Click the toggle to disable the schedule
   - Verify toggle state changes
   - Verify schedule status shows as "Disabled" or "Inactive"
4. Toggle again to re-enable:
   - Click toggle to enable
   - Verify status changes to "Enabled" or "Active"
5. If toggle is in edit form:
   - Edit the schedule
   - Change enabled state
   - Save and verify status change

**Expected**: Schedule can be enabled and disabled
**Validation**: 
- Enable/disable toggle is accessible
- Toggle state changes visually
- Schedule status reflects enabled/disabled state
- Disabled schedules don't execute (indicated by status)
- Enable/disable changes persist

---

### Step 7: View Schedule Execution History
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. If schedules have executed, find execution history section
2. Take a snapshot to locate history interface
3. Look for:
   - History table or list of past executions
   - Execution timestamps
   - Execution status (Success/Failed)
   - Duration of each execution
4. If history is available, verify it shows:
   - Chronological listing of executions
   - Status indicators with colors
   - Links to task details or logs
5. Click on a history item to view execution details
6. Verify navigation to task detail page
7. Return to schedules view

**Expected**: Execution history is accessible (if executions have occurred)
**Validation**: 
- Execution history section exists
- Past executions are listed chronologically
- Status shows with appropriate indicators
- Execution details are accessible
- Links to related tasks work correctly

---

### Step 8: Test Schedule Search/Filter
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. If multiple schedules exist, test search/filter functionality
2. Take a snapshot to find search controls
3. If search box is available:
   - Enter "test-daily" in search
   - Verify filtered results show matching schedule
   - Clear search to show all schedules
4. If filter options are available (status, enabled):
   - Filter by enabled status
   - Verify only enabled schedules show
   - Filter by disabled status
   - Clear filters

**Expected**: Search and filter work correctly (if implemented)
**Validation**: 
- Search filters schedules by name
- Filter options reduce schedule list appropriately
- Cleared search/filters restore full list
- Schedule count updates with filtering

---

### Step 9: Test Manual Schedule Trigger
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From schedules list, look for manual trigger functionality
2. Find "Run Now" or "Execute" button for a schedule (may be in actions menu)
3. Take a snapshot to locate trigger control
4. Click to manually trigger the schedule
5. Verify task creation:
   - Navigation to tasks or confirmation message
   - New task appears with schedule association
6. Check that manual trigger doesn't affect schedule timing
7. Verify task shows it was triggered from schedule

**Expected**: Schedules can be manually triggered (if feature available)
**Validation**: 
- Manual trigger button is accessible
- Trigger creates a new task immediately
- Task shows association with schedule
- Schedule's next automatic run time is unaffected
- Task executes successfully

---

### Step 10: Verify Next Execution Time Display
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From schedules list, locate next execution time display
2. Take a snapshot to see timing information
3. Verify each enabled schedule shows:
   - Next scheduled execution time
   - Time format (absolute time or relative like "in 2 hours")
4. Check that disabled schedules don't show next execution time or show "N/A"
5. Wait or refresh and verify time updates appropriately
6. Compare next execution time with cron expression to verify accuracy

**Expected**: Next execution time is displayed and accurate
**Validation**: 
- Next execution time is visible for enabled schedules
- Time calculation matches cron expression
- Disabled schedules don't show execution time
- Time format is clear and user-friendly
- Times update when page is refreshed

---

### Step 11: Test Bulk Schedule Operations
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Create another test schedule if needed to have multiple schedules
2. Take a snapshot to see selection controls
3. If checkboxes are available:
   - Select multiple schedules using checkboxes
   - Look for bulk action buttons (Enable All, Disable All, Delete Selected)
   - Test bulk enable/disable if available
   - Test bulk delete with confirmation
4. If bulk operations available:
   - Verify confirmation dialog for destructive operations
   - Verify only selected schedules are affected
5. Test select all / deselect all functionality

**Expected**: Bulk operations work with safety confirmations (if implemented)
**Validation**: 
- Schedule selection checkboxes work
- Multiple schedules can be selected
- Bulk action buttons appear when schedules selected
- Bulk operations affect only selected schedules
- Confirmation prevents accidental bulk deletions

---

### Step 12: Delete Test Schedules
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From schedules list, find "test-daily-schedule-ui-006"
2. Take a snapshot to locate delete action
3. Find and click delete button (may be in actions menu or as icon)
4. If confirmation dialog appears:
   - Read confirmation message
   - Confirm deletion
5. Verify schedule is removed from list
6. Repeat for "test-complex-schedule-ui-006"
7. Verify all test schedules are deleted
8. Check that schedule count updates
9. Verify no errors during deletion

**Expected**: Schedules can be deleted successfully
**Validation**: 
- Delete functionality is accessible
- Confirmation dialog prevents accidental deletion
- Schedule is removed from list after confirmation
- Schedule count updates appropriately
- Deleted schedules don't execute
- No errors occur during deletion

## Success Criteria
- [ ] Schedules tab is accessible from spider detail page
- [ ] Schedule creation form works correctly
- [ ] Simple cron expressions are accepted (e.g., "0 9 * * *")
- [ ] Complex cron expressions are accepted (e.g., "0 */2 8-18 * 1-5")
- [ ] Cron expression preview displays correctly
- [ ] Invalid cron expressions are rejected with error messages
- [ ] Schedules can be edited and changes save
- [ ] Schedule enable/disable functionality works
- [ ] Enabled schedules show next execution time
- [ ] Disabled schedules don't execute
- [ ] Execution history is accessible (if executions occurred)
- [ ] Manual schedule triggering works (if available)
- [ ] Search/filter functionality works (if available)
- [ ] Bulk operations work safely (if available)
- [ ] Schedule deletion works with confirmation
- [ ] Schedule-spider association is maintained
- [ ] No JavaScript errors in browser console
- [ ] UI remains responsive throughout operations

## Failure Scenarios
- **Scenario**: Cron expression validation doesn't work
- **Symptoms**: Invalid cron is accepted or valid cron is rejected
- **Action**: Check console for errors, verify cron parser library, test different expressions

- **Scenario**: Schedule doesn't execute at expected time
- **Symptoms**: Enabled schedule passes execution time without creating task
- **Action**: Check scheduler service status, verify timezone settings, check system time

- **Scenario**: Edit schedule doesn't save changes
- **Symptoms**: Form submits but changes don't persist
- **Action**: Check API response, verify permissions, check for validation errors

- **Scenario**: Enable/disable toggle doesn't work
- **Symptoms**: Toggle changes but schedule status doesn't update
- **Action**: Check if save is required, verify API calls, check permissions

- **Scenario**: Schedule deletion fails
- **Symptoms**: Confirmation accepted but schedule remains
- **Action**: Check for running tasks, verify permissions, check API errors

## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
./cli.py --spec UI-006 --backend copilot
```

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs
- `mcp_playwright_browser_snapshot` - Inspect page structure
- `mcp_playwright_browser_click` - Click buttons, tabs, toggles
- `mcp_playwright_browser_type` - Fill input fields
- `mcp_playwright_browser_fill_form` - Fill multiple form fields
- `mcp_playwright_browser_wait_for` - Wait for state changes

**Reporting Test Results:**
```bash
./tests/tools/report_test_result.py --status passed --total-steps 12 --completed-steps 12
```

## Cleanup
- Test schedules: Deleted in Step 12
- Browser state: Automatic cleanup via MCP Playwright
- Scheduled tasks: Any tasks created during testing remain (can be cleaned up manually)
- No special cleanup required if test completes successfully

## Notes
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers UI elements using MCP Playwright tools
- Cron expression format: 5 fields (minute hour day month weekday)
- Cron preview depends on implementation (may vary in detail)
- Schedule execution requires scheduler service to be running
- Timezone handling may affect displayed times
- Next execution time calculation may be cached or real-time
- Manual trigger may require Pro license
- Bulk operations may require Pro license
- Schedule conflicts (overlapping executions) handled by task queue
- Historical execution data depends on past schedule executions

## History
- **Created**: 2025-10-20, Assistant (converted from UI-007)
- **Modified**: -
