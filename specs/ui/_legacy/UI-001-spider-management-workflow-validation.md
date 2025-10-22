````markdown
# UI-001 - Spider Management (Complete Lifecycle)

## Metadata
- **Category**: ui
- **Priority**: critical
- **Complexity**: medium
- **Duration**: 15-20 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser

## Scenario
This test validates the complete spider lifecycle through the web interface, including creation, configuration, file management, task execution, scheduling, data collection, dependencies, and deletion. This consolidated spec covers all spider management functionality.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080
- Valid user credentials (admin/admin)
- At least one worker node available
- Browser with JavaScript enabled
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-003**: Task Management (for task execution validation)
- **UI-006**: Project Management (for project assignment)
- **UI-007**: Schedule Management (for spider scheduling)
- **UI-010**: Dependencies Management (for dependency installation)

## Test Steps

### Step 1: Login to Crawlab
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080
2. Take a snapshot to understand the login page structure
3. Identify and fill the username field with "admin"
4. Identify and fill the password field with "admin"
5. Find and click the sign-in/login button
6. Wait for page to load and verify successful login

**Expected**: Successfully authenticated and redirected to dashboard
**Validation**: 
- URL changes to contain `/#/home` or similar dashboard route
- Main navigation/sidebar becomes visible
- User is logged in (no login form visible)

---

### Step 2: Navigate to Spider List
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot to see available navigation options
2. Find and click on the "Spiders" menu item in the sidebar/navigation
3. Wait for the spiders page to load
4. Take a snapshot to verify the spider list interface

**Expected**: Spider management page displays with list/table of spiders
**Validation**: 
- URL changes to contain `spiders`
- Spider list or table is visible with columns (Name, Project, Git Repo, Last Status, Last Run At, Stats, Description, Actions)
- Action buttons (like "Create" or "New Spider") are present
- Search/filter controls available

---

### Step 3: Create New Spider
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot to locate the create/new spider button
2. Click the button to open the spider creation dialog/form
3. Wait for the form to appear and take a snapshot
4. **Fill all mandatory fields** (marked with asterisk or labeled as required):
   - **Name**: "test-spider-lifecycle-ui-001"
   - **Command**: "python main.py" (or any valid command)
   - **Project**: Select from dropdown or create new
   - **Programming Language**: Select "Python" 
   - **Framework**: Select "Scrapy" or appropriate framework
   - **Description**: "Automated test spider for UI-001 lifecycle testing"
5. Fill any other required fields as indicated by the form
6. Find and click the confirm/submit button
7. Wait for the dialog to close

**Expected**: Spider creation succeeds
**Validation**: 
- Creation dialog closes after submission
- Page redirects to spider detail page OR returns to spider list
- No error messages appear
- Success notification may be displayed

---

### Step 4: Verify Spider in List
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Navigate back to the spiders list page (if currently on spider detail page)
2. Take a snapshot of the spider list/table
3. Search for "test-spider-lifecycle-ui-001" in the visible content or use search box
4. Verify the spider appears with correct name and metadata

**Expected**: Newly created spider is visible in the list
**Validation**:
- Spider name "test-spider-lifecycle-ui-001" is present in the table/list
- Spider row shows status, project assignment, and description
- Spider is selectable/clickable
- Action buttons (View/Run/More) are available

---

### Step 5: Open Spider Details and Explore Overview
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Click on the "test-spider-lifecycle-ui-001" spider name or row
2. Wait for the spider detail page to load
3. Take a snapshot to verify the interface
4. Verify Overview tab shows:
   - Spider metadata display (name, creation date, last modified)
   - Basic statistics (runs, success rate if any)
   - Configuration summary
   - Quick action buttons (Run, Edit, Delete)

**Expected**: Spider detail page loads with tabs and information
**Validation**:
- URL changes to include the spider ID or detail route
- Spider name "test-spider-lifecycle-ui-001" is displayed
- Multiple tabs are visible (Overview, Files, Tasks, Schedules, Data, Dependencies, Settings)
- Spider metadata is accurate
- Edit functionality is accessible

---

### Step 6: File Management - Upload and Edit Files
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Click on "Files" tab in spider detail page
2. Take a snapshot to see file tree structure
3. Verify file tree shows:
   - Root folder "~" or similar
   - Existing files if any (e.g., main.py, requirements.txt)
   - File tree toolbar with "Upload Files", "Export Files", "Settings" buttons

4. **Create a new Python file**:
   - Use right-click context menu or toolbar button to create new file
   - Name the file "spider_script.py"
   - Open the file in the code editor (double-click or use open action)

5. **Edit file content**:
   - Verify code editor opens with syntax highlighting
   - Add sample spider code (use text appropriate for selected framework)
   - Look for save button or use Ctrl+S keyboard shortcut
   - Verify save confirmation

6. **Upload additional file** (if upload functionality available):
   - Click "Upload Files" button in toolbar
   - Select a test file to upload
   - Verify file appears in file tree

**Expected**: File management operations succeed
**Validation**:
- File tree displays correctly with hierarchical structure
- New files can be created
- Code editor provides syntax highlighting
- Files can be saved successfully
- Upload functionality works (if available)
- File tree updates after operations

---

### Step 7: Task Execution - Run Spider
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. From spider detail page, locate and click "Run" button (usually has play icon)
2. If a run configuration dialog appears, verify options and submit
3. Take a snapshot to confirm task creation
4. Navigate to "Tasks" tab in spider detail page
5. Verify new task appears in task list
6. Check task status (should be "Running" or "Pending" initially)
7. Monitor task until completion or timeout
8. Click "View Logs" button to see task execution logs
9. Verify logs display properly

**Expected**: Task execution starts successfully
**Validation**:
- Task is created immediately after clicking Run
- Task appears in Tasks tab with current timestamp
- Status shows appropriate state (Running/Pending/Finished/Error)
- Task logs are accessible and display execution output
- Task metadata shows node assignment, duration, status

---

### Step 8: Schedule Management - Create Schedule
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Click on "Schedules" tab in spider detail page
2. Take a snapshot to see schedule interface
3. Click "Create Schedule" or "Add Schedule" button
4. Fill out schedule form:
   - **Name**: "nightly-crawl-ui-001"
   - **Cron Expression**: "0 2 * * *" (2 AM daily)
   - **Description**: "Automated nightly crawl for testing"
   - **Enabled**: Toggle to enabled state
5. If cron expression builder/helper is available, verify it shows preview
6. Submit schedule creation
7. Verify schedule appears in schedules list
8. Check schedule status shows as "Active" or "Enabled"

**Expected**: Schedule creation succeeds
**Validation**:
- Schedule form accepts valid cron expressions
- Cron expression preview/description is accurate
- Schedule saves successfully
- Schedule appears in list with correct configuration
- Enable/disable toggle functions properly

---

### Step 9: Data Collection View
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Click on "Data" tab in spider detail page
2. Take a snapshot to see data collection interface
3. If tasks have completed and collected data:
   - Verify data table displays with columns
   - Check pagination controls
   - Test data search/filter if available
   - Verify data export functionality (CSV, JSON, Excel buttons)
4. If no data exists:
   - Verify "No Data" message displays appropriately
   - Note that data collection depends on spider execution

**Expected**: Data collection interface loads
**Validation**:
- Data tab is accessible
- If data exists: table displays with proper formatting
- If no data: appropriate empty state message
- Export functionality is available
- Data integrity is maintained

---

### Step 10: Dependencies Management (if Pro features available)
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Click on "Dependencies" tab in spider detail page
2. Take a snapshot to see dependency interface
3. If dependency management is available:
   - View current dependencies list
   - Click "Add Dependency" or similar button
   - Add a test dependency (e.g., "requests" for Python)
   - Verify dependency appears in list
   - Check installation status
4. If feature not available, note for documentation

**Expected**: Dependency interface is accessible
**Validation**:
- Dependencies tab loads (may require Pro license)
- Current dependencies display correctly
- New dependencies can be added
- Installation status is tracked
- Dependency types supported (pip, npm, etc.)

---

### Step 11: Spider Configuration and Settings
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Navigate back to "Overview" tab or find "Settings" tab
2. Test editing spider configuration:
   - Click edit button to enter edit mode
   - Modify spider description
   - Update spider command if editable
   - Change project assignment (select different project from dropdown)
   - Save changes
3. Verify changes persist and display correctly
4. Take a snapshot to confirm updated information

**Expected**: Spider settings can be modified
**Validation**:
- Edit mode is accessible
- Form fields are pre-populated with current values
- Changes save successfully
- Updated values display immediately
- No data loss during updates

---

### Step 12: Delete Test Spider
**Method**: automated (Copilot with MCP Playwright)
**Action**:
1. Navigate back to the spider list page
2. Take a snapshot to understand the delete mechanism
3. Find the "test-spider-lifecycle-ui-001" spider in the list
4. **Select the spider** (click checkbox in the row)
5. Look for and click the delete button (may be enabled only after selection, or use action menu)
6. If a confirmation dialog appears, read the warning and confirm the deletion
7. Wait for the operation to complete
8. Take a snapshot to verify spider is removed

**Expected**: Spider is deleted and removed from list
**Validation**: 
- Spider "test-spider-lifecycle-ui-001" no longer appears in the list
- A success message or notification may appear
- The table/list updates to reflect the deletion
- Associated resources are handled appropriately (tasks, schedules, etc.)
- Page count updates if pagination is present

## Success Criteria
- [ ] Login process works smoothly
- [ ] Spider list page loads correctly with all columns
- [ ] Spider creation form functions correctly with all fields
- [ ] New spider appears in list after creation
- [ ] Spider detail page is accessible with all tabs
- [ ] File management works (create, edit, upload files)
- [ ] Task execution starts and completes successfully
- [ ] Task logs are accessible and display properly
- [ ] Schedule creation works with cron expressions
- [ ] Schedule appears in list and can be enabled/disabled
- [ ] Data collection tab loads (shows data if available)
- [ ] Dependencies tab is accessible (if Pro features enabled)
- [ ] Spider settings can be modified and saved
- [ ] Spider deletion works properly with confirmation
- [ ] No JavaScript errors in browser console
- [ ] UI remains responsive throughout workflow
- [ ] All navigation paths work correctly
- [ ] Status indicators update in real-time

## Failure Scenarios
- **Scenario**: Form submission fails silently
- **Symptoms**: No error message, form doesn't save, page doesn't respond
- **Action**: Check browser console for JavaScript errors, verify API endpoints, check network tab

- **Scenario**: Element not found during test
- **Symptoms**: Test fails with "element not visible" or timeout errors
- **Action**: Use MCP Playwright to explore current UI, update approach, verify page loaded completely

- **Scenario**: Login redirects incorrectly
- **Symptoms**: After login, URL doesn't change to `/#/home`
- **Action**: Check authentication response, verify hash routing is working, check for API errors

- **Scenario**: File editor not loading
- **Symptoms**: Code editor doesn't appear when file is opened
- **Action**: Check browser console for Monaco editor errors, verify file size limits, check network

- **Scenario**: Task execution doesn't start
- **Symptoms**: Click Run button but no task appears
- **Action**: Check worker node status, verify spider configuration, check API response

- **Scenario**: Spider deletion fails
- **Symptoms**: Confirmation dialog appears but spider remains in list
- **Action**: Check for associated resources (running tasks, schedules), verify permissions, check API errors

## Execution

### Automated Execution with Copilot

Execute this test using Copilot CLI with MCP Playwright support:

```bash
# From project root
./tests/cli.py --spec UI-001 --backend copilot

# Or directly with copilot
cd tests
copilot -p "Execute the test specification in specs/ui/UI-001-spider-management-workflow-validation.md"
```

**How Copilot Executes This Test:**
1. Copilot reads the high-level test steps from this specification
2. Uses MCP Playwright tools (`#mcp_playwright_browser_*`) to:
   - Navigate pages programmatically
   - Take snapshots to discover UI structure dynamically
   - Find elements without hard-coded selectors
   - Click, fill, and interact with the UI
   - Verify expected outcomes
3. Adapts to UI changes automatically by exploring the actual rendered interface
4. **Reports results** using the reporting tool: `./tests/tools/report_test_result.py`

**Reporting Test Results:**
After completing the test execution, Copilot should call the reporting tool:

```bash
# All tests passed
./tests/tools/report_test_result.py --status passed --total-steps 6 --completed-steps 6

# Test failed
./tests/tools/report_test_result.py --status failed --total-steps 6 --completed-steps 3 --failed-steps 1 --reason "Step 4: Spider not found in list"

# Test skipped
./tests/tools/report_test_result.py --status skipped --reason "Prerequisites not met"
```

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs
- `mcp_playwright_browser_snapshot` - Inspect page structure
- `mcp_playwright_browser_click` - Click elements
- `mcp_playwright_browser_fill` - Fill input fields
- `mcp_playwright_browser_screenshot` - Capture visual evidence

**Advantages over Hard-Coded Scripts:**
- No brittle selectors that break when UI changes
- Adapts to internationalization (i18n) automatically
- Discovers required form fields dynamically
- Self-healing when element IDs or classes change
- More maintainable - update spec, not code

### Manual Testing (Fallback)
If automated testing is unavailable:
1. Open browser and navigate to http://localhost:8080
2. Follow test steps manually
3. Document any differences or issues encountered
4. Take screenshots for evidence

## Cleanup
- Test spider deletion: Handled in Step 6
- Browser cleanup: Automatic via MCP Playwright
- Screenshots: Captured via MCP tools during execution
- Test results: Reported by Copilot
- No manual cleanup required

## Notes
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers UI elements using MCP Playwright tools
- Test adapts automatically to UI changes (element IDs, classes, i18n)
- Focus is on workflow validation, not implementation details
- Form fields are discovered at runtime - test fills all required fields dynamically
- Delete operation requires row selection (checkbox) before clicking delete button
- File management relies on Monaco code editor (common in Vue.js apps)
- Task execution may take time - use appropriate timeouts
- Schedules use cron expression format - validation varies by implementation
- Data collection depends on spider execution and results storage
- Dependencies tab may require Pro license activation
- Test with different browsers by configuring MCP Playwright
- Spider execution and advanced features are covered in related specs

## History
- **Created**: 2025-09-17, Assistant
- **Modified**: 2025-10-10, Updated for Copilot execution with high-level instructions
- **Modified**: 2025-10-20, Merged with UI-003, expanded to cover complete spider lifecycle
- **Last Run**: -
````