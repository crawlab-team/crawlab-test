# UI-005 - Project Management

## Metadata
- **Category**: ui
- **Priority**: medium
- **Complexity**: simple
- **Duration**: 8-10 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser

## Scenario
This test validates project management functionality through the web interface, including creating projects, managing project details, assigning spiders to projects, searching/filtering projects, and project deletion operations.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080
- Valid user credentials (admin/admin)
- At least one spider exists (for spider assignment testing)
- Browser with JavaScript enabled
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-001**: Spider Management (for spider-project relationship)
- **UI-003**: Task Management (for project task organization)

## Test Steps

### Step 1: Navigate to Project List
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080
2. Log in if not already authenticated (username: admin, password: admin)
3. Take a snapshot to see available navigation
4. Find and click the "Projects" menu item in the sidebar/navigation
5. Wait for the project list page to load
6. Take a snapshot to verify the project list interface

**Expected**: Project list page displays
**Validation**: 
- URL changes to contain `projects` or `/#/projects`
- Page shows breadcrumb "Project List"
- Project table/list is visible
- Control buttons are present (New Project, search)

---

### Step 2: Verify Project List Structure
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot of the project list table
2. Verify table columns are present:
   - Name (clickable project names)
   - Spiders (count of assigned spiders)
   - Description (project description text)
   - Actions (action buttons for operations)
3. Verify page controls:
   - "New Project" button with plus icon
   - "Search projects" textbox
   - Selection checkboxes for each project row
   - "Delete Selected" button (may be disabled initially)
   - Pagination controls showing total project count
4. Check existing projects display correctly
5. Verify project names are clickable links

**Expected**: Project list displays with all necessary controls
**Validation**: 
- All expected columns are visible
- Project names are clickable
- Spider count shows accurate numbers
- Descriptions display properly
- Search textbox is functional
- Action buttons are accessible

---

### Step 3: Create New Project
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project list, take a snapshot to find "New Project" button
2. Click the "New Project" button (usually has a plus icon)
3. Wait for project creation form/dialog to appear
4. Take a snapshot to see form structure
5. Fill out the project creation form:
   - **Project Name**: "test-project-ui-005" (required field, may be marked with asterisk)
   - **Description**: "Automated test project for UI-005 validation"
   - **Additional fields**: Fill any other fields present (tags, settings, etc.)
6. Find and click the create/save/submit button
7. Wait for project creation to complete
8. Verify project appears in the project list

**Expected**: New project is created successfully
**Validation**: 
- Project creation form appears
- All fields are properly labeled
- Form validates required fields (Name is required)
- Success message or notification appears
- New project "test-project-ui-005" appears in project list
- Project shows 0 spiders initially
- No error messages appear

---

### Step 4: View Project Detail Page
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project list, find "test-project-ui-005" project
2. Click on the project name to open detail page
3. Wait for project detail page to load
4. Take a snapshot to see project detail interface
5. Verify project detail elements:
   - Project name displays correctly
   - Project description is shown
   - Spider assignment section is present
   - Project statistics/metrics (if available)
   - Edit/configuration controls
6. Check for tabs (if applicable):
   - Overview/Details tab
   - Spiders tab
   - Statistics tab (if available)
   - Settings tab (if available)
7. Verify breadcrumb navigation shows proper path

**Expected**: Project detail page loads with complete information
**Validation**: 
- Project detail page displays correctly
- All project metadata is accurate
- Spider assignment interface is accessible
- Project information can be viewed
- Navigation breadcrumbs show path
- No loading or display errors

---

### Step 5: Edit Project Information
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project detail page, find edit functionality
2. Take a snapshot to locate edit controls (may be edit button or direct form editing)
3. Modify project information:
   - **Description**: Change to "Updated description for testing"
   - **Name**: Optionally verify name can be changed
   - **Additional fields**: Modify any other editable fields
4. Find and click the save button
5. Wait for save confirmation
6. Verify changes persist:
   - Take a snapshot to confirm updates
   - Check for success notification
   - Verify updated description displays
7. Navigate back to project list
8. Verify updated information shows in list view

**Expected**: Project information can be edited and saved
**Validation**: 
- Edit functionality is accessible
- Form fields update correctly
- Save operation succeeds
- Success notification appears (if implemented)
- Changes persist after save
- Updated information displays in both detail and list views

---

### Step 6: Assign Spiders to Project
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project detail page, find spider assignment section
2. Take a snapshot to see assignment interface
3. Look for "Assign Spider" or similar button/control
4. Click to open spider assignment interface
5. View available spiders:
   - Take a snapshot to see spider selection options
   - May be dropdown, multi-select list, or dialog with spider list
6. Select one or more spiders to assign to the project
7. Confirm spider assignment
8. Verify spiders appear in project's spider list
9. Check that spider count updates in project list
10. Navigate to a spider detail page (from project or spider list)
11. Verify the spider shows project association

**Expected**: Spiders can be assigned to the project
**Validation**: 
- Spider assignment interface is accessible
- Available spiders are displayed
- Multiple spiders can be selected (if supported)
- Assignment operation succeeds
- Assigned spiders appear in project view
- Spider count increases in project list (e.g., "0" becomes "1" or "2")
- Spiders show project assignment in their detail pages
- Assignment is bidirectional and consistent

---

### Step 7: Remove Spiders from Project
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project detail page with assigned spiders
2. Take a snapshot to see assigned spiders
3. Find remove/unassign functionality for spiders:
   - May be remove button, unassign button, or checkbox + bulk action
4. Remove one spider from the project
5. Verify spider is removed from project's spider list
6. Check that spider count decreases
7. Navigate to the spider detail page
8. Verify spider no longer shows this project assignment
9. Verify spider is available for reassignment to other projects

**Expected**: Spiders can be removed from projects
**Validation**: 
- Remove/unassign functionality works
- Spider is removed from project view
- Spider count updates correctly
- Spider-project association is removed
- Spider remains in system (not deleted, just unassigned)
- Spider can be reassigned to another project

---

### Step 8: Test Project Search
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to project list page
2. Take a snapshot to locate search textbox
3. Use "Search projects" textbox to search:
   - Enter partial project name "test-project"
   - Verify search results update to show matching projects
   - Check that non-matching projects are filtered out
4. Test search variations:
   - Try exact project name "test-project-ui-005"
   - Try case variations (uppercase, lowercase)
   - Try partial matches from middle of name
5. Clear search:
   - Clear the search textbox
   - Verify all projects reappear
6. Test search with non-existent name:
   - Enter "nonexistent-project-xyz"
   - Verify empty results or "No projects found" message

**Expected**: Project search filters results correctly
**Validation**: 
- Search textbox is functional
- Search results update as you type or after submit
- Case-insensitive search works
- Partial name matching works
- Search result count updates
- Clear search restores all projects
- Empty search results handled gracefully

---

### Step 9: Test Project Filtering and Sorting
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project list, look for additional filtering options:
   - Take a snapshot to see available filters
   - May have filters for spider count, active/inactive, tags, etc.
2. If sorting is available, test sorting:
   - Click column headers to sort (Name, Spiders, etc.)
   - Verify ascending/descending sort
   - Check sort indicator icons
3. If filters are available, test filtering:
   - Filter by spider count ranges
   - Filter by project tags (if applicable)
   - Filter by active/inactive status
4. Test combined search and filters:
   - Apply search term with filters
   - Verify results match all criteria

**Expected**: Filtering and sorting work correctly
**Validation**: 
- Sorting changes project order appropriately
- Sort indicators show current sort state
- Filters reduce project list correctly
- Combined filters work together
- Project count updates with filtering

---

### Step 10: View Project Statistics (if available)
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project detail page, look for statistics/overview section
2. Take a snapshot to see statistics display
3. Verify project statistics show (if implemented):
   - Total spider count
   - Active vs inactive spider breakdown
   - Recent task statistics
   - Success/failure rates
   - Activity timeline or recent changes
4. Check if statistics refresh:
   - Look for refresh button
   - Check for automatic updates
5. Verify statistics accuracy:
   - Compare spider count with actual assigned spiders
   - Check if numbers make sense

**Expected**: Project statistics provide useful insights
**Validation**: 
- Statistics section is accessible
- Data displays correctly
- Numbers are accurate
- Charts/graphs render properly (if present)
- Statistics provide meaningful information

---

### Step 11: Test Project Bulk Operations
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From project list, create an additional test project (or use existing)
2. Take a snapshot to see selection controls
3. Select multiple projects using checkboxes:
   - Click checkbox for "test-project-ui-005"
   - Click checkbox for another project (if safe to delete)
4. Verify "Delete Selected" button becomes enabled
5. **Test with caution**: Either:
   - Cancel the operation before confirming deletion, OR
   - Only proceed if in isolated test environment
6. If proceeding with deletion:
   - Click "Delete Selected" button
   - Verify confirmation dialog appears
   - Read warning message carefully
   - Confirm deletion or cancel
7. Test selection/deselection:
   - Select all projects
   - Deselect individual projects
   - Verify button state changes

**Expected**: Bulk operations work with safety confirmations
**Validation**: 
- Project selection checkboxes work
- Multiple projects can be selected
- "Delete Selected" button state reflects selection
- Confirmation dialog prevents accidental deletion
- Warning about spider reassignment (if projects have spiders)
- Bulk delete works correctly (if confirmed)

---

### Step 12: Delete Test Project
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to project list
2. Find "test-project-ui-005" project
3. Take a snapshot to locate delete action:
   - May be delete button in Actions column
   - May be in more options menu
   - May require selection + Delete Selected button
4. Initiate project deletion
5. Verify confirmation dialog appears:
   - Read confirmation message
   - Check for warnings about assigned spiders
6. If project has assigned spiders:
   - Note warning about spider reassignment
   - Verify options for handling spiders (reassign or unassign)
7. Confirm deletion
8. Wait for deletion to complete
9. Take a snapshot to verify project removed
10. Verify "test-project-ui-005" no longer appears in list
11. Check that spider count updates (spiders are unassigned, not deleted)

**Expected**: Project is deleted successfully
**Validation**: 
- Delete functionality is accessible
- Confirmation dialog appears
- Warning shown if project has assigned spiders
- Deletion completes successfully
- Project removed from list
- Associated spiders are unassigned (not deleted)
- No errors during deletion
- Success notification appears (if implemented)

## Success Criteria
- [ ] Project list page loads correctly
- [ ] All table columns display information properly
- [ ] New project creation works
- [ ] Project detail page is accessible
- [ ] Project information can be edited and saved
- [ ] Spiders can be assigned to projects
- [ ] Spiders can be removed from projects
- [ ] Spider count updates correctly with assignments
- [ ] Project search works with partial names
- [ ] Case-insensitive search functions properly
- [ ] Filtering and sorting work (if available)
- [ ] Project statistics display correctly (if available)
- [ ] Bulk operations work with confirmation
- [ ] Project selection/deselection works
- [ ] Project deletion works with confirmations
- [ ] Spiders are unassigned when project is deleted
- [ ] Spider-project relationships are bidirectional
- [ ] No JavaScript errors in browser console
- [ ] UI remains responsive throughout operations

## Failure Scenarios
- **Scenario**: Project creation fails with validation error
- **Symptoms**: Form shows error about duplicate name or invalid input
- **Action**: Use unique project name, check required fields, verify input format

- **Scenario**: Spider assignment doesn't update count
- **Symptoms**: Spiders assigned but count remains 0
- **Action**: Refresh page, check API response, verify assignment completed

- **Scenario**: Project deletion fails silently
- **Symptoms**: Confirmation accepted but project remains in list
- **Action**: Check console for errors, verify permissions, check if project has dependencies

- **Scenario**: Search doesn't filter results
- **Symptoms**: Entering search term doesn't reduce visible projects
- **Action**: Check console for JavaScript errors, verify search API, test with different terms

- **Scenario**: Project detail page doesn't load
- **Symptoms**: Clicking project name doesn't navigate or shows error
- **Action**: Check project ID, verify route, check console errors, verify data exists

## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
./cli.py --spec UI-005 --backend copilot
```

**How Copilot Executes This Test:**
1. Copilot reads the high-level test steps from this specification
2. Uses MCP Playwright tools to:
   - Navigate pages and discover UI structure dynamically
   - Take snapshots before interactions to understand current state
   - Find elements semantically without hard-coded selectors
   - Interact with forms, buttons, and selection controls
   - Verify expected outcomes through observable changes
3. Adapts to UI variations automatically
4. Reports results using the reporting tool

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs
- `mcp_playwright_browser_snapshot` - Inspect page structure
- `mcp_playwright_browser_click` - Click buttons, links, checkboxes
- `mcp_playwright_browser_type` - Fill input fields
- `mcp_playwright_browser_fill_form` - Fill multiple form fields
- `mcp_playwright_browser_wait_for` - Wait for state changes

**Reporting Test Results:**
```bash
./tests/tools/report_test_result.py --status passed --total-steps 12 --completed-steps 12
```

## Cleanup
- Test project "test-project-ui-005": Deleted in Step 12
- Browser state: Automatic cleanup via MCP Playwright
- Assigned spiders: Automatically unassigned when project deleted
- No manual cleanup required if test completes successfully

## Notes
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers UI elements using MCP Playwright tools
- Test adapts automatically to UI changes (element IDs, classes, styling)
- Projects serve primarily as organizational containers for spiders
- Spider assignment to projects helps organize and filter spider lists
- Project deletion should not delete spiders, only unassign them
- Project names must be unique within the system
- Some features (like advanced statistics) may require Pro license
- Spider-project relationship is many-to-one (spider belongs to one project)
- Project management is relatively simple compared to other features

## History
- **Created**: 2025-10-20, Assistant (converted from UI-006)
- **Modified**: -
