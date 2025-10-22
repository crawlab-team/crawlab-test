# Project Management Test Specification

## Test Suite: Project Organization & Spider Assignment

*Based on actual application exploration using Playwright MCP*

### Test Case PROJECT-001: Project List View

**Priority**: Medium
**Estimated Time**: 2 minutes

**Pre-conditions**:
- User is authenticated
- At least one project exists in the system

**Test Steps**:
1. Navigate to `/projects`
2. Verify project list page loads with breadcrumb "Project List"
3. Check page controls:
   - "New Project" button with plus icon
   - "Search projects" textbox
4. Check table structure and columns:
   - Name (clickable project names)
   - Spiders (count of assigned spiders)
   - Description (project description text)
   - Actions (action buttons)
5. Verify project data display:
   - Project names are clickable
   - Spider count is accurate
   - Descriptions show properly
6. Test table controls:
   - Selection checkboxes for bulk operations
   - "Delete Selected" button (disabled when none selected)
   - Pagination controls showing total count

**Expected Results**:
- Project list loads without errors
- All projects are displayed correctly
- Search functionality works
- Action buttons are accessible

**Actual Interface Elements Observed**:
- One project "Test" with "0" spiders
- "New Project" button clearly visible
- Table shows: Name, Spiders, Description, Actions columns
- Pagination shows "Total 1" with proper controls

---

### Test Case PROJECT-002: Create New Project

**Priority**: High
**Estimated Time**: 3 minutes

**Test Steps**:
1. From project list, click "New Project" button
2. Verify project creation form appears
3. Fill out project creation form:
   - **Project Name**: Enter unique project name (required)
   - **Description**: Enter project description (optional)
   - **Tags**: Add project tags (if available)
   - **Settings**: Configure project settings (if available)
4. Submit project creation:
   - Click "Create" or "Save" button
   - Verify form validation for required fields
   - Check for duplicate name validation
5. Verify project creation success:
   - Project appears in project list
   - Navigation to project detail page
   - Success message displayed

**Form Validation to Test**:
- [ ] Required field validation (Project Name)
- [ ] Duplicate name prevention
- [ ] Description length limits (if any)
- [ ] Special character handling in names
- [ ] Form submission handling

**Expected Results**:
- Project creation form is user-friendly
- Validation works correctly
- New project appears immediately in list
- Project detail page loads after creation

---

### Test Case PROJECT-003: Project Detail View

**Priority**: High
**Estimated Time**: 4 minutes

**Test Steps**:
1. Click on a project name from project list (e.g., "Test")
2. Verify navigation to project detail page
3. Check project detail interface:
   - Project name and description display
   - Spider assignment section
   - Project statistics/metrics
   - Project settings/configuration
4. Verify project tabs (if available):
   - Overview
   - Spiders
   - Statistics
   - Settings
5. Test project management features:
   - Edit project name and description
   - Save project changes
   - View assigned spiders
   - Manage spider assignments

**Project Detail Elements to Verify**:
- [ ] Project metadata display
- [ ] Spider assignment interface
- [ ] Project statistics
- [ ] Edit/Save functionality
- [ ] Navigation breadcrumbs

**Expected Results**:
- Project detail page loads correctly
- All project information is accurate
- Edit functionality works properly
- Spider assignment is accessible

---

### Test Case PROJECT-004: Spider Assignment to Project

**Priority**: High
**Estimated Time**: 4 minutes

**Test Steps**:
1. From project detail page, test spider assignment:
   - Find spider assignment section
   - Click "Assign Spider" or similar button
   - Select spiders from available list
   - Confirm spider assignment
2. Verify spider assignment success:
   - Assigned spiders appear in project
   - Spider count updates in project list
   - Spiders show project association
3. Test spider unassignment:
   - Remove spiders from project
   - Verify spider count decreases
   - Check spiders return to unassigned state
4. Test from spider side:
   - Navigate to spider detail page
   - Verify project assignment dropdown
   - Change spider project assignment
   - Verify project lists update

**Spider Assignment Features**:
- [ ] Multi-select spider assignment
- [ ] Search/filter available spiders
- [ ] Bulk assignment operations
- [ ] Assignment confirmation
- [ ] Real-time count updates

**Expected Results**:
- Spider assignment works seamlessly
- Project counts update immediately
- Both project and spider views stay synchronized
- Assignment changes are persistent

---

### Test Case PROJECT-005: Project Search and Filtering

**Priority**: Medium
**Estimated Time**: 2 minutes

**Test Steps**:
1. From project list, test search functionality:
   - Use "Search projects" textbox
   - Enter partial project name
   - Verify filtered results
   - Test case-insensitive search
2. Test project sorting (if available):
   - Sort by project name
   - Sort by spider count
   - Sort by creation date
3. Test project filtering (if available):
   - Filter by spider count ranges
   - Filter by active/inactive projects
   - Filter by project tags

**Search Features to Test**:
- [ ] Real-time search as you type
- [ ] Case-insensitive matching
- [ ] Partial name matching
- [ ] Search result highlighting
- [ ] Search reset functionality

**Expected Results**:
- Search returns relevant results
- Filtering works correctly
- Search is responsive and fast
- Results update in real-time

---

### Test Case PROJECT-006: Project Statistics and Overview

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. Navigate to project detail page
2. Verify project statistics display:
   - Total spider count
   - Active/inactive spider breakdown
   - Recent task statistics
   - Success/failure rates
3. Check project activity timeline:
   - Recent spider additions/removals
   - Task execution history
   - Project modifications
4. Test statistics refresh:
   - Verify data is current
   - Check automatic updates
   - Test manual refresh

**Statistics to Verify**:
- [ ] Accurate spider counts
- [ ] Task execution metrics
- [ ] Success/failure rates
- [ ] Activity timeline
- [ ] Real-time updates

**Expected Results**:
- All statistics are accurate
- Data refreshes properly
- Charts/graphs render correctly
- Performance metrics are meaningful

---

### Test Case PROJECT-007: Project Deletion and Bulk Operations

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. Test single project deletion:
   - From project list, find delete action
   - Click delete button for a project
   - Verify deletion confirmation dialog
   - Confirm deletion
   - Verify project removed from list
2. Test bulk project operations:
   - Select multiple projects using checkboxes
   - Click "Delete Selected" button
   - Verify bulk deletion confirmation
   - Confirm bulk deletion
   - Verify all selected projects removed
3. Test deletion safety measures:
   - Attempt to delete project with assigned spiders
   - Verify warning about spider reassignment
   - Test forced deletion vs reassignment

**Deletion Safety Features**:
- [ ] Confirmation dialogs
- [ ] Warning for projects with spiders
- [ ] Spider reassignment options
- [ ] Undo functionality (if available)
- [ ] Bulk operation confirmations

**Expected Results**:
- Deletion requires explicit confirmation
- Projects with spiders show warnings
- Bulk operations work safely
- Spider reassignment is handled properly

---

### Test Case PROJECT-008: Project Settings and Configuration

**Priority**: Low
**Estimated Time**: 2 minutes

**Test Steps**:
1. From project detail page, access project settings
2. Test project configuration options:
   - Project visibility settings
   - Default spider settings
   - Notification settings
   - Permission settings
3. Modify project settings:
   - Change configuration values
   - Save settings changes
   - Verify changes persist
4. Test settings validation:
   - Invalid configuration values
   - Required settings
   - Settings conflicts

**Configuration Options to Test**:
- [ ] Project visibility (public/private)
- [ ] Default execution settings
- [ ] Notification preferences
- [ ] Access permissions
- [ ] Integration settings

**Expected Results**:
- Settings interface is intuitive
- Changes save correctly
- Validation works properly
- Settings affect project behavior

---

## Interface Elements Reference

### Project List Table Columns (Observed)
- **Name**: Clickable project names
- **Spiders**: Count of assigned spiders (e.g., "0")
- **Description**: Project description text
- **Actions**: Action buttons for project operations

### Project List Controls (Observed)
- **New Project**: Button with plus icon
- **Search projects**: Text input field
- **Selection**: Checkboxes for bulk operations
- **Delete Selected**: Bulk operation button
- **Pagination**: Shows total count and page controls

### Project Creation Form (Expected)
- **Project Name**: Required text field
- **Description**: Optional textarea
- **Tags**: Tag input (if available)
- **Settings**: Configuration options (if available)

## Performance Benchmarks
- Project list load time: < 2 seconds
- Project creation time: < 1 second
- Spider assignment time: < 1 second
- Search response time: < 500ms
- Project detail load time: < 1 second

## Integration Points
- [ ] Project-Spider assignment relationship
- [ ] Project-Task organization
- [ ] Project-User permissions
- [ ] Project-Statistics calculation
- [ ] Project-Notification settings
