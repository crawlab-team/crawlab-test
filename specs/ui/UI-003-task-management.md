# UI-003 - Task Management

## Metadata
- **Category**: ui
- **Priority**: critical
- **Complexity**: medium
- **Duration**: 12-15 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser, at least one spider

## Scenario
This test validates task execution, monitoring, and management functionality through the web interface. It covers task list views, task creation, status monitoring, filtering, log viewing, and task lifecycle operations.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080
- Valid user credentials (admin/admin)
- At least one spider exists in the system
- Worker node available for task execution
- Browser with JavaScript enabled
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-001**: Spider Management (for spider-task relationship)
- **UI-004**: Node Management (for node-task assignment)
- **UI-006**: Schedule Management (for scheduled tasks)

## Test Steps

### Step 0: Setup - Ensure Test Spider Exists
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080
2. Log in if not already authenticated (username: admin, password: admin)
3. Navigate to Spiders page
4. Check if any spiders exist in the list
5. If no spiders exist, create a simple test spider:
   - Name: "test-spider-ui003"
   - Command: "echo 'Test spider for task management'"
   - Fill other required fields
6. Verify spider was created successfully

**Expected**: At least one spider exists for task creation
**Validation**: 
- Spider list shows at least one spider
- Spider can be selected in dropdowns
**Notes**: This step ensures prerequisite is met. Skip if spiders already exist.

---

### Step 1: Navigate to Task List
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080 (or continue from Step 0)
2. Ensure already authenticated (from Step 0)
3. Take a snapshot to see available navigation
4. Find and click the "Tasks" menu item in the sidebar/navigation
5. Wait for the task list page to load
6. Take a snapshot to verify the task list interface

**Expected**: Task list page displays with all task history
**Validation**: 
- URL changes to contain `tasks` or `/#/tasks`
- Page shows breadcrumb "Task List"
- Task table/list is visible with multiple columns
- Filter controls are present at the top
- Action buttons available (New Task, filters)

---

### Step 2: Verify Task List Structure
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot of the task list table
2. Verify table columns are present:
   - Node (shows node name with icon)
   - Spider (shows spider name, clickable)
   - Schedule (shows schedule if task was scheduled)
   - Priority (shows priority level like "Medium")
   - Execute Command (shows truncated command like "python main...")
   - Status (shows colored badge: Finished/Error/Running)
   - Started At (shows relative time like "59 minutes ago")
   - Finished At (shows relative time)
   - Total Duration (shows readable duration like "4 seconds")
   - Results (shows count with database icon)
   - Actions (shows View/View Logs buttons)
3. Verify filter controls at top:
   - Status filter dropdown
   - Node filter dropdown
   - Spider filter dropdown
   - Schedule filter dropdown
4. Verify list controls:
   - Selection checkboxes for each task row
   - "Delete Selected" button (may be disabled initially)
   - Pagination controls showing total task count

**Expected**: Task list displays comprehensive task information
**Validation**: 
- All expected columns are visible
- Tasks show with color-coded status badges (green for Finished, red for Error)
- Time displays use relative format consistently
- Filter dropdowns are functional
- Selection and bulk operation controls work

---

### Step 3: Create New Task from Task List
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From task list page, take a snapshot to find the "New Task" button
2. Click the "New Task" button (usually has a plus icon)
3. Wait for task creation form/dialog to appear
4. Take a snapshot to see form structure
5. Fill out the task creation form:
   - **Spider**: Select a spider from dropdown
   - **Node**: Choose execution node (if options available)
   - **Priority**: Set priority level (if available)
   - **Parameters**: Add any required parameters (if applicable)
6. Find and click the create/submit button
7. Wait for task creation to complete
8. Verify task appears in the task list

**Expected**: New task is created and starts execution
**Validation**: 
- Task creation form appears with all necessary fields
- Spider dropdown shows available spiders
- Form validates required fields
- Task appears in task list immediately after creation
- Task shows initial status (Running/Pending)
- No error messages appear

---

### Step 4: Execute Task from Spider Page
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to the Spiders page (use sidebar navigation)
2. Take a snapshot to see spider list
3. Click on any spider name to open spider detail page
4. Take a snapshot to find the "Run" button
5. Click the "Run" button (usually has a play icon)
6. If run configuration dialog appears, verify options and submit
7. Wait for task creation confirmation
8. Navigate back to Tasks page
9. Take a snapshot to find the newly created task
10. Verify the new task appears at the top of the list
11. Check task status shows "Running" or "Pending"

**Expected**: Task execution starts from spider page
**Validation**: 
- Run button is accessible on spider detail page
- Task is created immediately after clicking Run
- Task appears in task list with current timestamp
- Task shows correct spider association
- Status indicates task is running or pending

---

### Step 5: Monitor Task Status and View Logs
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From task list, find a running or completed task
2. Take a snapshot to locate the "View Logs" button
3. Click "View Logs" button for the task
4. Wait for log viewer to open
5. Take a snapshot of the log viewer interface
6. Verify log display features:
   - Log entries display in chronological order
   - Timestamps are visible for log entries
   - Auto-scroll behavior (for running tasks)
   - Search functionality (if available)
7. Test log navigation:
   - Scroll through log entries
   - Test search within logs (if available)
   - Check for log level indicators (info, warning, error)
8. Close log viewer or navigate back

**Expected**: Task logs are accessible and display correctly
**Validation**: 
- Log viewer opens without errors
- Logs display in readable format
- Timestamps are accurate
- For running tasks, logs update in real-time
- For completed tasks, full historical logs are available
- Log viewer is responsive and functional

---

### Step 6: View Task Details
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From task list, find the "View" button for any task
2. Click the "View" button (usually has an eye icon)
3. Wait for task detail page to load
4. Take a snapshot to see task detail interface
5. Verify task metadata displays:
   - Task ID or identifier
   - Spider name (clickable link)
   - Node name (clickable link)
   - Status with colored badge
   - Priority level
   - Started timestamp
   - Finished timestamp (if completed)
   - Duration
   - Results count
   - Execute command
6. Check for additional task information:
   - Task parameters or configuration
   - Error messages (if task failed)
   - Task logs section
   - Task results section (if data collected)

**Expected**: Task detail page shows comprehensive information
**Validation**: 
- Task detail page loads successfully
- All task metadata is accurate
- Status is displayed with appropriate visual indicator
- Timestamps show correct times
- Links to spider and node are functional
- All task information is presented clearly

---

### Step 7: Test Task Filtering
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Return to task list page
2. Take a snapshot to see filter controls
3. **Test Status Filter**:
   - Click Status filter dropdown
   - Select "Finished" option
   - Verify only finished tasks display (green status badges)
   - Take a snapshot to confirm filtering
   - Change to "Error" option
   - Verify only error tasks display (red status badges)
   - Reset filter to "All" or default
4. **Test Node Filter**:
   - Click Node filter dropdown
   - Select a specific node (e.g., "Master Node")
   - Verify only tasks from that node display
   - Reset filter
5. **Test Spider Filter**:
   - Click Spider filter dropdown
   - Select a specific spider
   - Verify only tasks from that spider display
   - Reset filter
6. **Test Combined Filters**:
   - Apply multiple filters simultaneously (e.g., Status=Finished, specific Spider)
   - Verify results match all filter criteria
   - Check task count updates appropriately

**Expected**: All filters work correctly individually and combined
**Validation**: 
- Each filter dropdown opens and shows options
- Filtering updates the task list immediately
- Task count reflects filtered results
- Multiple filters can be applied together
- Filter reset functionality works
- No errors when filtering

---

### Step 8: Test Task Search and Pagination
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. If a search box is available on task list:
   - Take a snapshot to locate search field
   - Enter search terms (task ID, spider name, etc.)
   - Verify search results update
   - Clear search to see all tasks
2. Test pagination controls:
   - Verify total task count is displayed (e.g., "Total 10")
   - If multiple pages exist:
     - Click next page button
     - Verify task list updates to show next page
     - Click previous page button
     - Test page number direct navigation (if available)
   - Verify page size selector (if available)

**Expected**: Search and pagination function properly
**Validation**: 
- Search filters tasks in real-time (if available)
- Pagination controls are accessible
- Page navigation works smoothly
- Task count is accurate
- Page size changes update display correctly

---

### Step 9: Test Bulk Task Operations
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From task list, take a snapshot to see selection controls
2. Select multiple tasks using checkboxes in rows
3. Verify "Delete Selected" button becomes enabled
4. Click "Delete Selected" button
5. If confirmation dialog appears:
   - Read the confirmation message
   - Verify it mentions the number of tasks to delete
   - Confirm deletion or cancel to test dialog
6. If deletion confirmed, verify tasks are removed from list
7. Check that task count updates
8. Test deselecting tasks:
   - Select tasks again
   - Deselect all or individual tasks
   - Verify "Delete Selected" button disables when none selected

**Expected**: Bulk operations work safely with confirmation
**Validation**: 
- Task selection checkboxes are functional
- Multiple tasks can be selected
- "Delete Selected" button state reflects selection
- Confirmation dialog prevents accidental deletion
- Selected tasks are removed after confirmation
- Task count updates after bulk deletion

---

### Step 10: Monitor Task Status Transitions
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Start a new task (use spider Run button or New Task)
2. Immediately navigate to task list
3. Find the newly created task
4. Take snapshots periodically to monitor status changes:
   - Initial status: "Running" or "Pending"
   - Monitor for status transitions
   - Check duration counter updates
5. Verify status indicators:
   - Running: Loading/progress indicator (blue or animated)
   - Finished: Green check icon
   - Error: Red X icon or error indicator
6. Monitor real-time updates:
   - Check if status updates automatically without page refresh
   - Verify duration increases while task runs
   - Check if results count updates when task completes
7. If task completes, verify final status and metadata

**Expected**: Task status updates reflect real-time execution state
**Validation**: 
- Status transitions from Pending → Running → Finished/Error
- Status badges change colors appropriately
- Visual indicators are clear and intuitive
- Duration counter updates in real-time
- Results count populates on completion
- Page updates without manual refresh (if real-time updates enabled)

---

### Step 11: Test Task Control Operations
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. If task control features are available, test them:
2. **Cancel Running Task** (if available):
   - Find a running task in the list
   - Look for cancel/stop button (may be in actions menu)
   - Click cancel button
   - Verify task status changes to "Cancelled" or "Stopped"
3. **Restart Failed Task** (if available):
   - Find a task with "Error" status
   - Look for restart/retry button
   - Click restart button
   - Verify new task is created or task status resets to "Running"
4. **View Task Details During Execution**:
   - Open task detail page while task is running
   - Verify live log updates
   - Check real-time status information

**Expected**: Task control operations work as expected
**Validation**: 
- Cancel/stop functionality halts task execution
- Restart/retry creates new task or restarts existing task
- Task controls are accessible and clearly labeled
- Status reflects control actions immediately
- No errors when using task controls

---

### Step 12: Verify Task-Spider-Node Relationships
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From task list, click on a spider name link in a task row
2. Verify navigation to spider detail page
3. Navigate back to task list
4. Click on a node name link in a task row
5. Verify navigation to node detail page
6. From node detail page, check if tasks tab exists
7. Verify tasks filtered by that node appear
8. Test bidirectional navigation:
   - Spider → Tasks (shows spider's tasks)
   - Node → Tasks (shows node's tasks)
   - Task → Spider (links to spider)
   - Task → Node (links to node)

**Expected**: Task relationships are properly linked
**Validation**: 
- Spider name in task list is clickable and navigates correctly
- Node name in task list is clickable and navigates correctly
- Spider detail page shows associated tasks
- Node detail page shows associated tasks
- Navigation maintains context and filters
- All links work in both directions

## Success Criteria
- [ ] **Setup**: At least one spider exists or is created for testing
- [ ] Task list page loads with all task history
- [ ] All table columns display correct information
- [ ] Filter controls work individually and combined
- [ ] Task creation from task list works
- [ ] Task execution from spider page works
- [ ] Task logs are accessible and readable
- [ ] Task detail page shows comprehensive information
- [ ] Status badges are color-coded appropriately
- [ ] Status transitions update in real-time
- [ ] Time displays use consistent relative format
- [ ] Duration calculations are accurate
- [ ] Search functionality works (if available)
- [ ] Pagination controls function properly
- [ ] Bulk task operations work with confirmation
- [ ] Task selection/deselection works correctly
- [ ] Task control operations function (cancel, restart)
- [ ] Spider-task-node relationships are properly linked
- [ ] No JavaScript errors in browser console
- [ ] UI remains responsive throughout operations

## Failure Scenarios
- **Scenario**: Task creation fails silently
- **Symptoms**: Form submits but no task appears in list
- **Action**: Check browser console, verify API endpoints, check spider configuration

- **Scenario**: Task logs don't load
- **Symptoms**: Log viewer opens but shows empty or loading forever
- **Action**: Check task execution status, verify log collection, check API response

- **Scenario**: Status doesn't update automatically
- **Symptoms**: Task status stuck on "Running" even after completion
- **Action**: Manually refresh page, check WebSocket connections, verify real-time update mechanism

- **Scenario**: Filters don't work
- **Symptoms**: Selecting filter options doesn't change displayed tasks
- **Action**: Check browser console for JavaScript errors, verify filter API calls

- **Scenario**: Bulk delete fails
- **Symptoms**: Confirmation dialog appears but tasks remain after deletion
- **Action**: Check permissions, verify task dependencies, check API response

## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
./cli.py --spec UI-003 --backend copilot
```

**How Copilot Executes This Test:**
1. Copilot reads the high-level test steps from this specification
2. Uses MCP Playwright tools to:
   - Navigate pages and discover UI structure dynamically
   - Take snapshots before interactions to understand current state
   - Find elements semantically without hard-coded selectors
   - Interact with forms, buttons, filters, and tables
   - Verify expected outcomes through observable changes
3. Adapts to UI variations automatically
4. Reports results using the reporting tool

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs
- `mcp_playwright_browser_snapshot` - Inspect page structure  
- `mcp_playwright_browser_click` - Click buttons and links
- `mcp_playwright_browser_type` - Fill input fields
- `mcp_playwright_browser_fill_form` - Fill multiple form fields
- `mcp_playwright_browser_select_option` - Use dropdown filters
- `mcp_playwright_browser_wait_for` - Wait for state changes

**Reporting Test Results:**
```bash
# After test completion
./tests/tools/report_test_result.py --status passed --total-steps 12 --completed-steps 12
```

## Cleanup
- Test tasks created during execution: Can be deleted via bulk operations
- Browser state: Automatic cleanup via MCP Playwright
- Test data: Tasks can be cleaned up manually if needed
- No special cleanup required

## Notes
- **This test includes automatic prerequisite setup (Step 0)**
- If no spiders exist, test will create a simple test spider automatically
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers UI elements using MCP Playwright tools
- Test adapts automatically to UI changes (element IDs, classes, styling)
- Task execution requires active worker nodes
- **Task execution validates gRPC file sync**: When tasks run, workers sync spider files via gRPC streaming
- Real-time status updates depend on WebSocket or polling implementation
- Log streaming may behave differently for running vs completed tasks
- Some features (cancel, restart) may require Pro license
- Task retention policies may affect historical task availability
- For comprehensive spider file sync validation, see **CLS-003** (gRPC performance test)
- Filter options populate based on available data (nodes, spiders, schedules)
- Performance may vary based on task history volume

## History
- **Created**: 2025-10-20, Assistant (converted from UI-004)
- **Modified**: -
