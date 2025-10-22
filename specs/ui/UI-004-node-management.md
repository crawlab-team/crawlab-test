# UI-004 - Node Management

## Metadata
- **Category**: ui
- **Priority**: high
- **Complexity**: medium
- **Duration**: 10-12 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser

## Scenario
This test validates node management functionality through the web interface, including viewing node lists, managing node configurations, monitoring node status, viewing node-specific tasks, and controlling node operations.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080
- Valid user credentials (admin/admin)
- At least one node exists (master and/or worker nodes)
- Browser with JavaScript enabled
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-003**: Task Management (for node-task relationship)
- **UI-001**: Spider Management (for node-spider execution)
- **UI-013**: System Settings (for system-wide node configuration)

## Test Steps

### Step 1: Navigate to Node List
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Navigate to http://localhost:8080
2. Log in if not already authenticated (username: admin, password: admin)
3. Take a snapshot to see available navigation
4. Find and click the "Nodes" menu item in the sidebar/navigation
5. Wait for the node list page to load
6. Take a snapshot to verify the node list interface

**Expected**: Node list page displays with all registered nodes
**Validation**: 
- URL changes to contain `nodes` or `/#/nodes`
- Page shows breadcrumb "Node List"
- Node table/list is visible
- At least one node (Master Node) is displayed
- Control buttons are present (New Node, filters)

---

### Step 2: Verify Node List Structure
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot of the node list table
2. Verify table columns are present:
   - Name (clickable node names)
   - Node Type (Master/Worker with badges)
   - Status (Online/Offline with colored indicators)
   - Runners (current/max format like "0 / ∞")
   - Enabled (toggle switches)
   - Current Metrics (CPU/Memory/Disk percentages with colored badges)
   - Description
   - Actions (View button and more options)
3. Verify filter controls at top:
   - Search nodes textbox
   - Node Type filter dropdown
   - Status filter dropdown
   - Enabled filter dropdown
4. Verify list controls:
   - "New Node" button with plus icon
   - Selection checkboxes for each node row
   - "Delete Selected" button (may be disabled initially)
   - Pagination controls showing total node count

**Expected**: Node list displays comprehensive node information
**Validation**: 
- All expected columns are visible
- Node types show with appropriate badges (Master with server icon, Worker with worker icon)
- Status indicators are color-coded (green for Online)
- Enabled toggles are functional
- Current metrics display as percentage badges (e.g., "24%", "45%", "28%" for CPU/Memory/Disk)
- Action buttons are accessible

---

### Step 3: View Node Detail - Overview Tab
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node list, take a snapshot to identify nodes
2. Click on a node name (e.g., "Master Node") to open detail page
3. Wait for node detail page to load
4. Take a snapshot to verify the interface
5. Check breadcrumb navigation shows: "Node List / Node Detail / Overview"
6. Verify tabs are visible:
   - Overview (currently active)
   - Tasks
   - Monitoring
7. In Overview tab, verify form fields display:
   - **Name**: Editable textbox showing node name
   - **Unique Identity Key**: Read-only UUID field
   - **Type**: Badge display (Master/Worker with icon)
   - **IP**: Editable textbox showing IP address
   - **MAC Address**: Editable textbox
   - **Hostname**: Editable textbox
   - **Enabled**: Toggle switch
   - **Max Runners**: Number input with +/- buttons and "Unlimited" checkbox
   - **Description**: Editable textarea
8. Verify top controls:
   - "Back" button to return to node list
   - "Save" button for changes
   - Current metrics display (CPU/Memory/Disk percentages in colored badges)
   - Node selector dropdown (if available)

**Expected**: Node detail page loads with complete information
**Validation**: 
- Node detail page displays all metadata
- Form fields are pre-populated with actual node data
- Unique Identity Key shows real UUID and is not editable
- Type badge shows correct node type (Master/Worker)
- Enabled toggle reflects current node state
- Max Runners shows current configuration with unlimited option
- Real-time metrics display in colored badges
- All fields render correctly without errors

---

### Step 4: Edit Node Configuration
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node detail Overview tab, take a snapshot
2. Modify editable fields:
   - **Description**: Change or add description text
   - **Max Runners**: Adjust the value using +/- buttons or input
   - Toggle "Unlimited" checkbox to test behavior
   - **IP/MAC/Hostname**: Update if editable (optional based on node type)
3. Verify field validations:
   - Test invalid inputs (if applicable)
   - Check required field indicators
4. Click the "Save" button
5. Wait for save confirmation
6. Take a snapshot to verify changes persisted
7. Verify success message appears (if shown)
8. Check that updated values display correctly

**Expected**: Node configuration changes save successfully
**Validation**: 
- Form fields accept valid input
- Validation errors show for invalid input
- Save button triggers save operation
- Success notification appears (if implemented)
- Changes persist after save
- Page updates to show new values
- No JavaScript errors occur

---

### Step 5: Test Node Enable/Disable Toggle
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node detail page or node list, locate the Enabled toggle
2. Take a snapshot to see current toggle state
3. Click the Enabled toggle switch to change state
4. Verify toggle animation and state change
5. Check if confirmation dialog appears (if implemented)
6. If on detail page, save changes
7. Navigate to node list to verify status
8. Take a snapshot to confirm status change
9. Toggle back to original state
10. Verify node functionality reflects enabled/disabled state

**Expected**: Node enable/disable works immediately
**Validation**: 
- Toggle switch responds to clicks
- Toggle state changes visually
- If on list page, change reflects immediately
- If on detail page, save persists the change
- Node status updates in list view
- Disabled nodes may show different behavior (no task execution)

---

### Step 6: View Node Tasks Tab
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node detail page, click on "Tasks" tab
2. Wait for tasks list to load
3. Take a snapshot to see tasks interface
4. Verify task table displays with columns:
   - Node (shows current node name)
   - Spider (clickable spider names)
   - Schedule (if task was scheduled)
   - Priority
   - Execute Command
   - Status (with colored badges)
   - Started At (relative time)
   - Finished At (relative time)
   - Total Duration
   - Results (count with icon)
   - Actions (View/View Logs buttons)
5. Verify tasks shown are specific to this node
6. Test task interactions from node context:
   - Click on spider name to navigate
   - Click "View" to see task details
   - Click "View Logs" to see task logs
7. Check task filtering and controls work in node context

**Expected**: Node-specific task list displays correctly
**Validation**: 
- Tasks tab loads without errors
- Task table shows only tasks executed on this node
- All task columns display properly
- Status badges are color-coded correctly
- Task actions are functional
- Links to spiders and task details work
- Task count reflects node-specific tasks

---

### Step 7: View Node Monitoring Tab
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node detail page, click on "Monitoring" tab
2. Wait for monitoring interface to load
3. Take a snapshot to see monitoring features
4. Verify monitoring elements (if available):
   - Real-time metrics displays (CPU, Memory, Disk, Network)
   - Resource usage charts or graphs
   - Historical performance data
   - System metrics visualization
   - Time range selector (if available)
5. Test monitoring features:
   - Check if data updates automatically
   - Test time range selection (if available)
   - Verify metric accuracy against current metrics shown in overview
6. Look for additional monitoring information:
   - Node health indicators
   - Performance alerts (if any)
   - Resource trends

**Expected**: Monitoring tab provides node performance insights
**Validation**: 
- Monitoring tab loads successfully
- Real-time metrics are displayed
- Charts/graphs render correctly (if present)
- Data updates automatically or has refresh option
- Monitoring data is meaningful and accurate
- No errors in console or display

---

### Step 8: Test Node List Filtering
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Return to node list page
2. Take a snapshot to see filter controls
3. **Test Search**:
   - Use "Search nodes" textbox
   - Enter partial node name
   - Verify filtered results
   - Clear search
4. **Test Node Type Filter**:
   - Click Node Type dropdown
   - Select "Master" option
   - Verify only master nodes display
   - Select "Worker" option
   - Verify only worker nodes display (if any exist)
   - Reset to "All" or default
5. **Test Status Filter**:
   - Click Status dropdown
   - Select "Online" option
   - Verify only online nodes display
   - Select "Offline" option (if applicable)
   - Reset filter
6. **Test Enabled Filter**:
   - Click Enabled dropdown
   - Select "Enabled" option
   - Verify only enabled nodes display
   - Select "Disabled" option
   - Reset filter
7. Test combined filters with multiple criteria

**Expected**: All filters work correctly individually and combined
**Validation**: 
- Each filter dropdown opens and shows options
- Filtering updates the node list immediately
- Node count reflects filtered results
- Multiple filters can be applied together
- Search is case-insensitive and matches partial names
- Filter reset functionality works
- No errors when filtering

---

### Step 9: Test Node Metrics Monitoring
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node list, observe current metrics columns
2. Take multiple snapshots over time to check metric updates
3. Verify metric displays:
   - CPU percentage with colored badge (e.g., green <50%, yellow 50-80%, red >80%)
   - Memory percentage with similar color coding
   - Disk percentage with similar color coding
4. Click on a node to view details
5. Compare metrics in list view vs detail view
6. Check if metrics update automatically without refresh
7. Verify metric accuracy and consistency

**Expected**: Node metrics display and update correctly
**Validation**: 
- Metrics show as percentage values
- Color coding reflects resource usage levels
- Metrics update periodically (real-time or near real-time)
- Metrics are consistent across list and detail views
- High resource usage shows warning colors
- Metrics provide useful monitoring information

---

### Step 10: Test Node Creation (Optional)
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node list, click "New Node" button
2. Wait for node creation form/dialog to appear
3. Take a snapshot to see form structure
4. Fill out node creation form (if applicable):
   - Node Name (required)
   - Node Type selection (Master/Worker)
   - IP address
   - MAC address
   - Hostname
   - Description
   - Enable/disable toggle
   - Max runners configuration
5. Submit form
6. Handle any connection/registration process
7. Verify node appears in list

**Expected**: New node creation process works (if applicable)
**Validation**: 
- Node creation form appears
- All fields are properly labeled
- Form validates required fields
- Node creation process is clear
- New node appears in list after creation

**Note**: Node creation may involve agent installation and registration, which might not be fully testable via UI alone.

---

### Step 11: Test Bulk Node Operations
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node list, take a snapshot to see selection controls
2. Select multiple nodes using checkboxes
3. Verify "Delete Selected" button becomes enabled
4. Test bulk operations (carefully, or in test environment):
   - Click "Delete Selected" button
   - Verify confirmation dialog appears
   - Read warning message about node deletion
   - Cancel deletion to avoid removing active nodes
5. Test selecting/deselecting nodes:
   - Select all nodes
   - Deselect specific nodes
   - Deselect all nodes
   - Verify button state changes accordingly

**Expected**: Bulk operations work with safety confirmations
**Validation**: 
- Node selection checkboxes work
- Multiple nodes can be selected
- "Delete Selected" button state reflects selection
- Confirmation dialog prevents accidental deletion
- Warning about master node deletion (if applicable)
- Deselection works properly

---

### Step 12: Verify Node-Task-Spider Relationships
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From node detail Tasks tab, click on a spider name link
2. Verify navigation to spider detail page
3. Navigate back to node detail
4. From spider detail page (if accessible), run a task
5. Verify task is assigned to a node
6. Navigate to node list
7. Check that node shows task execution in progress (runners count increases)
8. Test navigation paths:
   - Node → Tasks → Spider
   - Spider → Run Task → Check Node assignment
   - Task → Node detail
9. Verify runner count updates when tasks execute

**Expected**: Node relationships are properly linked
**Validation**: 
- Spider links in node tasks navigate correctly
- Task execution affects node runner count
- Runner count shows format "current / max" or "current / ∞"
- Node assignment is visible in task details
- All relationship links work bidirectionally
- Data stays consistent across views

## Success Criteria
- [ ] Node list page loads with all registered nodes
- [ ] All table columns display correct information
- [ ] Node types display with appropriate badges
- [ ] Status indicators are color-coded appropriately
- [ ] Filter controls work individually and combined
- [ ] Search functionality works
- [ ] Node detail page shows comprehensive information
- [ ] Overview tab displays all configuration fields
- [ ] Node configuration can be edited and saved
- [ ] Enable/disable toggle works correctly
- [ ] Tasks tab shows node-specific tasks
- [ ] Monitoring tab loads and displays metrics
- [ ] Current metrics display correctly with color coding
- [ ] Metrics update automatically or near real-time
- [ ] Max runners configuration works with unlimited option
- [ ] Bulk node operations work with confirmation
- [ ] Node selection/deselection works correctly
- [ ] Node-task-spider relationships are properly linked
- [ ] No JavaScript errors in browser console
- [ ] UI remains responsive throughout operations

## Failure Scenarios
- **Scenario**: Node metrics don't update
- **Symptoms**: Metrics show stale data or zeros
- **Action**: Check node heartbeat, verify monitoring service, check API connections

- **Scenario**: Node configuration save fails
- **Symptoms**: Save button doesn't respond or error appears
- **Action**: Check browser console, verify permissions, check validation errors

- **Scenario**: Tasks tab shows all tasks, not node-specific
- **Symptoms**: Tasks from other nodes appear in node's task list
- **Action**: Check filtering logic, verify API response, check node identifier

- **Scenario**: Enable/disable toggle doesn't work
- **Symptoms**: Toggle changes but node state doesn't change
- **Action**: Check if save is required, verify permissions, check API response

- **Scenario**: Node creation fails or hangs
- **Symptoms**: Form submits but node doesn't appear or times out
- **Action**: Check agent installation, verify network connectivity, check registration process

## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
./cli.py --spec UI-004 --backend copilot
```

**How Copilot Executes This Test:**
1. Copilot reads the high-level test steps from this specification
2. Uses MCP Playwright tools to:
   - Navigate pages and discover UI structure dynamically
   - Take snapshots before interactions to understand current state
   - Find elements semantically without hard-coded selectors
   - Interact with forms, toggles, filters, and tabs
   - Verify expected outcomes through observable changes
3. Adapts to UI variations automatically
4. Reports results using the reporting tool

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs
- `mcp_playwright_browser_snapshot` - Inspect page structure
- `mcp_playwright_browser_click` - Click buttons, links, tabs, toggles
- `mcp_playwright_browser_type` - Fill input fields
- `mcp_playwright_browser_fill_form` - Fill multiple form fields
- `mcp_playwright_browser_select_option` - Use dropdown filters
- `mcp_playwright_browser_wait_for` - Wait for state changes

**Reporting Test Results:**
```bash
./tests/tools/report_test_result.py --status passed --total-steps 12 --completed-steps 12
```

## Cleanup
- Node configuration changes: Should be reverted if modified during testing
- Browser state: Automatic cleanup via MCP Playwright
- No nodes should be deleted during testing (use caution with bulk delete tests)
- Test in isolated environment if testing destructive operations

## Notes
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers UI elements using MCP Playwright tools
- Test adapts automatically to UI changes (element IDs, classes, styling)
- Master node deletion may be prevented or require special confirmation
- Node monitoring depends on agent heartbeat and metrics collection
- Metrics color coding may vary by implementation
- Max runners "Unlimited" typically means no limit on concurrent tasks
- Worker nodes may have different configuration options than master nodes
- Node creation process may involve external agent installation
- Real-time metric updates depend on WebSocket or polling implementation

## History
- **Created**: 2025-10-20, Assistant (converted from UI-005)
- **Modified**: -
