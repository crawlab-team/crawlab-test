# Task Management Test Specification

## Test Suite: Task Execution & Monitoring

*Based on actual application exploration using Playwright MCP*

### Test Case TASK-001: Task List View

**Priority**: Critical
**Estimated Time**: 3 minutes

**Pre-conditions**:
- User is authenticated
- At least one spider exists with some task history
- Tasks exist in various states (finished, running, error)

**Test Steps**:
1. Navigate to `/tasks`
2. Verify task list page loads completely with breadcrumb "Task List"
3. Check filter controls at top:
   - "New Task" button with plus icon
   - Status filter dropdown (Select)
   - Node filter dropdown (Select)
   - Spider filter dropdown (Select)
   - Schedule filter dropdown (Select)
4. Check table structure and columns:
   - Node (clickable node names with icons)
   - Spider (clickable spider names)
   - Schedule (if task was scheduled)
   - Priority (e.g., "Medium")
   - Execute Command (truncated commands like "python main....")
   - Status (with colored badges: Finished/Error/Running)
   - Started At (relative time format like "59 minutes ago")
   - Finished At (relative time format like "59 minutes ago")
   - Total Duration (human format like "4 seconds", "15 seconds")
   - Results (count with clickable icon)
   - Actions (View/View Logs/More buttons)
5. Test table functionality:
   - Selection checkboxes for bulk operations
   - "Delete Selected" button (disabled when none selected)
   - Pagination controls showing "Total 2" (or actual count)

**Expected Results**:
- Task list loads with all historical tasks
- Status badges are color-coded (green check for Finished, red X for Error)
- Time displays use relative format consistently
- All filter dropdowns work correctly
- Action buttons are properly labeled and functional

**Actual Interface Elements Observed**:
- Tasks show: Master Node, test_cn spider, Medium priority
- Execute commands shown as: "python main...."
- Status badges: "Finished" (green), "Error" (red)
- Duration examples: "4 seconds", "15 seconds"
- Results show count "0" with database icon
- Actions: "View", "View Logs", and more options button

---

### Test Case TASK-002: Task Execution from Spider

**Priority**: Critical
**Estimated Time**: 5 minutes

**Test Steps**:
1. Navigate to a spider detail page (e.g., test_cn spider)
2. Click "Run" button with play icon
3. Verify task execution:
   - Task appears in task list immediately
   - Status shows as "Running" initially
   - Node assignment is shown
   - Started At timestamp is current
4. Monitor task execution:
   - Navigate to `/tasks` to see new task
   - Verify task status updates (Running → Finished/Error)
   - Check duration calculation
   - Verify results count updates
5. Test task completion:
   - Wait for task to finish
   - Verify final status (Finished/Error)
   - Check Finished At timestamp
   - Verify Total Duration calculation

**Expected Behavior**:
- Task starts immediately after clicking Run
- Task appears in task list with current timestamp
- Status transitions properly
- All task metadata is recorded correctly

---

### Test Case TASK-003: Task Detail View and Logs

**Priority**: High
**Estimated Time**: 4 minutes

**Test Steps**:
1. From task list, click "View Logs" button on any task
2. Verify log viewer interface:
   - Real-time log streaming (for running tasks)
   - Historical logs (for completed tasks)
   - Log level indicators (if available)
   - Log search functionality
   - Auto-scroll behavior
3. Test log features:
   - Scroll through log entries
   - Search within logs
   - Copy log content
   - Download logs (if available)
4. Test "View" button functionality:
   - Click "View" button instead of "View Logs"
   - Verify task detail page loads
   - Check task metadata display
   - Verify all task information is accurate

**Expected Results**:
- Log viewer loads without errors
- Logs display in chronological order
- Search functionality works within logs
- Task details show all relevant information
- All timestamps are accurate

---

### Test Case TASK-004: Task Filtering and Search

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. From task list, test each filter:

   **Status Filter**:
   - Click Status dropdown
   - Select "Finished" option
   - Verify only finished tasks show
   - Select "Error" option  
   - Verify only error tasks show
   - Reset to "All" or "Select"

   **Node Filter**:
   - Click Node dropdown
   - Select "Master Node"
   - Verify only tasks from that node show
   - Test with other nodes if available

   **Spider Filter**:
   - Click Spider dropdown
   - Select specific spider (e.g., "test_cn")
   - Verify only tasks from that spider show

   **Schedule Filter**:
   - Click Schedule dropdown
   - Test schedule-based filtering
   - Verify scheduled vs manual tasks

2. Test combined filters:
   - Apply multiple filters simultaneously
   - Verify results match all filter criteria
   - Clear filters one by one

**Expected Results**:
- Each filter works independently
- Combined filters work together properly
- Filter reset functionality works
- Task count updates with filtering

---

### Test Case TASK-005: Task Status Monitoring

**Priority**: High
**Estimated Time**: 3 minutes

**Test Steps**:
1. Start a task and monitor status transitions:
   - Initial status: "Running"
   - Progress updates (if available)
   - Real-time status changes
2. Verify status indicators:
   - Finished: Green check icon
   - Error: Red X icon
   - Running: Loading/play icon
3. Test task control operations (if available):
   - Cancel running task
   - Restart failed task
   - View task details during execution
4. Monitor task metrics:
   - Duration counter updates
   - Results count updates
   - Status badge changes

**Expected Results**:
- Status changes reflect immediately in UI
- Visual indicators are clear and intuitive
- Task controls work correctly
- Real-time updates function properly

---

### Test Case TASK-006: New Task Creation

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. From task list, click "New Task" button
2. Verify task creation form:
   - Spider selection dropdown
   - Node selection options
   - Priority settings
   - Parameter configuration
   - Schedule options (if available)
3. Fill out task creation form:
   - Select a spider
   - Choose execution node
   - Set priority level
   - Add parameters if needed
4. Submit task creation:
   - Click create/submit button
   - Verify task appears in list
   - Check task starts execution

**Expected Results**:
- Task creation form is user-friendly
- All required fields are properly validated
- Task executes immediately after creation
- New task appears in task list

---

## Interface Elements Reference

### Task List Table Columns (Observed)
- **Node**: Clickable node name with server icon
- **Spider**: Clickable spider name
- **Schedule**: Schedule information (empty for manual tasks)
- **Priority**: Text priority level ("Medium")
- **Execute Command**: Truncated command ("python main....")
- **Status**: Colored badge with icon (Finished/Error)
- **Started At**: Relative time ("59 minutes ago")
- **Finished At**: Relative time ("59 minutes ago")
- **Total Duration**: Human readable ("4 seconds")
- **Results**: Count with database icon ("0")
- **Actions**: "View", "View Logs", more options

### Filter Controls (Observed)
- **Status**: Dropdown with "Select" placeholder
- **Node**: Dropdown with "Select" placeholder
- **Spider**: Dropdown with "Select" placeholder
- **Schedule**: Dropdown with "Select" placeholder

### Task Status Badges (Observed)
- **Finished**: Green background with check icon
- **Error**: Red background with X icon
- **Running**: Blue/progress indicator (not currently visible but implied)

## Performance Benchmarks
- Task list load time: < 2 seconds
- Task creation response: < 1 second
- Status update frequency: Real-time
- Log streaming latency: < 500ms
- Task detail load time: < 1 second

## Integration Points
- [ ] Spider-Task execution relationship
- [ ] Node-Task assignment relationship
- [ ] Schedule-Task trigger relationship
- [ ] Task-Result collection relationship
- [ ] Task-Log generation relationship
- [ ] User permissions on task operations
