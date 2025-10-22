# Node Management Test Specification

## Test Suite: Node Management & Monitoring

*Based on actual application exploration using Playwright MCP*

### Test Case NODE-001: Node List View

**Priority**: Critical
**Estimated Time**: 2 minutes

**Pre-conditions**:
- User is authenticated
- At least one node exists in the system (Master and/or Worker nodes)

**Test Steps**:
1. Navigate to `/nodes`
2. Verify node list page loads completely
3. Check table structure and columns:
   - Name (clickable node names)
   - Node Type (Master/Worker with badges)
   - Status (Online/Offline with status indicators)
   - Runners (current/max format like "0 / ∞")
   - Enabled (toggle switches)
   - Current Metrics (CPU/Memory/Disk percentages with colored badges)
   - Description
   - Actions (View/More buttons)
4. Test filtering functionality:
   - Search nodes textbox
   - Node Type filter dropdown (Select)
   - Status filter dropdown (Select)
   - Enabled filter dropdown (Select)
5. Verify node controls:
   - "New Node" button available
   - Selection checkboxes work
   - "Delete Selected" button (disabled when none selected)
   - Pagination controls

**Expected Results**:
- Page loads with breadcrumb "Node List"
- Table shows actual nodes (e.g., "Master Node", "Worker Node")
- Node types display with appropriate badges (Master = blue server icon, Worker = blue worker icon)
- Status shows "Online" with green indicators
- Enabled toggles are functional
- Current metrics show percentages (CPU%, Memory%, Disk%) with color coding
- Pagination shows "Total 2" (or actual count)

**Actual Interface Elements Observed**:
- "New Node" button with plus icon
- Filter dropdowns with "Select" placeholder
- Node names are clickable links
- Status badges are color-coded (green for Online)
- Metrics show as percentage badges (e.g., "24%", "45%", "28%")
- Action buttons include "View" with eye icon

---

### Test Case NODE-002: Node Detail Overview

**Priority**: High
**Estimated Time**: 3 minutes

**Test Steps**:
1. Click on a node name from the node list (e.g., "Master Node")
2. Verify navigation to node detail page
3. Check breadcrumb navigation: "Node List / Node Detail / Overview"
4. Verify tab structure:
   - Overview (active)
   - Tasks 
   - Monitoring
5. In Overview tab, verify form fields:
   - **Name**: editable textbox (e.g., "Master Node")
   - **Unique Identity Key**: read-only UUID field
   - **Type**: read-only badge (Master/Worker)
   - **IP**: editable textbox
   - **MAC Address**: editable textbox
   - **Hostname**: editable textbox
   - **Enabled**: toggle switch (functional)
   - **Max Runners**: number input with +/- buttons and "Unlimited" checkbox
   - **Description**: editable textarea
6. Verify top controls:
   - "Back" button
   - "Save" button
   - Current metrics display (CPU/Memory/Disk percentages)

**Expected Results**:
- Node detail page loads with correct node information
- All form fields populate with actual node data
- Unique Identity Key shows real UUID (non-editable)
- Type shows appropriate badge with icon
- Enabled toggle reflects actual node state
- Max Runners shows current configuration with "Unlimited" option
- Current metrics display real-time percentages

**Actual Interface Elements Observed**:
- Breadcrumb shows proper navigation path
- Node selector dropdown in top right
- Real-time metrics in colored badges (32%, 47%, 28%)
- Form fields properly labeled and functional
- "Unlimited" checkbox controls Max Runners field

---

### Test Case NODE-003: Node Tasks View

**Priority**: High  
**Estimated Time**: 4 minutes

**Test Steps**:
1. From node detail page, click "Tasks" tab
2. Verify task list loads for the specific node
3. Check task table columns:
   - Node (shows current node name with icon)
   - Spider (clickable spider names)
   - Schedule (if task was scheduled)
   - Priority (e.g., "Medium")
   - Execute Command (truncated command like "python main....")
   - Status (with status badges: Finished/Error/Running)
   - Started At (time ago format)
   - Finished At (time ago format)
   - Total Duration (duration in human format)
   - Results (count with icon)
   - Actions (View/View Logs/More buttons)
4. Test task interactions:
   - Click on spider name to navigate to spider
   - Click on task status to see details
   - Click "View" button to see task details
   - Click "View Logs" button to see task logs
5. Verify task filtering and controls:
   - Selection checkboxes for bulk operations
   - "Delete Selected" button
   - Pagination controls

**Expected Results**:
- Tasks table loads with node-specific tasks
- All historical tasks for the node are displayed
- Status badges are color-coded (green for Finished, red for Error)
- Time displays use relative format ("58 minutes ago", "1 hour ago")
- Duration shows in readable format ("4 seconds", "15 seconds")
- Action buttons are functional and properly labeled

**Actual Interface Elements Observed**:
- Task table shows real task data from the node
- Status badges: Finished (green check), Error (red X)
- Priority shows as text: "Medium"
- Execute command truncated: "python main...."
- Results count clickable with icon
- Actions include "View", "View Logs", and more options

---

### Test Case NODE-004: Node Monitoring Tab

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. From node detail page, click "Monitoring" tab
2. Verify monitoring interface loads
3. Check for monitoring elements:
   - Real-time metrics displays
   - Resource usage charts/graphs
   - Historical performance data
   - System metrics (CPU, Memory, Disk, Network)
4. Test monitoring features:
   - Real-time updates
   - Time range selection
   - Metric filtering
   - Performance alerts (if any)

**Expected Results**:
- Monitoring tab loads without errors
- Real-time system metrics are displayed
- Charts and graphs render properly
- Data updates automatically
- Historical data is available

*Note: This tab structure exists based on observed tab navigation, but requires actual testing to document specific monitoring features.*

---

### Test Case NODE-005: Create New Node

**Priority**: Medium
**Estimated Time**: 3 minutes

**Test Steps**:
1. From node list page, click "New Node" button
2. Verify node creation form appears
3. Fill out node creation form:
   - Node Name (required)
   - Node Type selection (Master/Worker)
   - IP address
   - MAC address
   - Hostname
   - Description
4. Configure node settings:
   - Enable/disable node
   - Set max runners (or unlimited)
5. Submit form and verify node creation

**Expected Results**:
- Node creation form appears
- All fields are properly labeled
- Validation works for required fields
- Node appears in list after creation
- Node can be immediately configured

*Note: Based on "New Node" button presence, but requires actual interaction to document complete form structure.*

---

### Test Case NODE-006: Node Status Management

**Priority**: High
**Estimated Time**: 2 minutes

**Test Steps**:
1. From node list, test node enable/disable toggles
2. Verify status changes reflect immediately
3. Test bulk node operations:
   - Select multiple nodes
   - Use "Delete Selected" button
   - Confirm deletion dialog
4. Monitor node status indicators:
   - Online/Offline status updates
   - Metric updates (CPU/Memory/Disk)
   - Heartbeat monitoring

**Expected Results**:
- Enable/disable toggles work immediately
- Status changes reflect in UI
- Bulk operations work correctly
- Confirmation dialogs prevent accidental deletions
- Real-time status monitoring works

---

## Interface Elements Reference

### Node List Table Columns (Observed)
- **Name**: Clickable node names
- **Node Type**: Badge with icon (Master/Worker)
- **Status**: Colored status badge (Online/Offline)
- **Runners**: Format "current / max" (e.g., "0 / ∞")
- **Enabled**: Toggle switch
- **Current Metrics**: Three percentage badges (CPU/Memory/Disk)
- **Description**: Text field
- **Actions**: "View" button and more options

### Node Detail Form Fields (Observed)
- **Name**: Text input (required, marked with *)
- **Unique Identity Key**: Read-only UUID
- **Type**: Badge display (Master/Worker with icon)
- **IP**: Text input
- **MAC Address**: Text input  
- **Hostname**: Text input
- **Enabled**: Toggle switch
- **Max Runners**: Number input with +/- controls and "Unlimited" checkbox
- **Description**: Textarea

### Task Table Columns (Observed)
- **Node**: Node name with icon
- **Spider**: Clickable spider name
- **Schedule**: Schedule information (if applicable)
- **Priority**: Text priority level
- **Execute Command**: Truncated command
- **Status**: Colored status badge
- **Started At**: Relative time format
- **Finished At**: Relative time format
- **Total Duration**: Human-readable duration
- **Results**: Count with icon
- **Actions**: "View", "View Logs", more options

## Performance Benchmarks
- Node list load time: < 2 seconds
- Node detail load time: < 1 second
- Task list load time: < 2 seconds
- Real-time metric updates: Every 5-10 seconds
- Status toggle response: < 500ms

## Integration Points
- [ ] Node-Task assignment relationship
- [ ] Node-Spider execution relationship  
- [ ] Node status monitoring system
- [ ] Node resource management
- [ ] Node authentication and authorization
