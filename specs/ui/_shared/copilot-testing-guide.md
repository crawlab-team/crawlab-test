# Copilot UI Testing Guide

## Overview
All Crawlab UI tests are designed for execution by GitHub Copilot using MCP Playwright tools. This approach provides adaptive, maintainable tests that don't break when UI implementation details change.

## Core Principles

### 1. High-Level Instructions, Not Hard-Coded Selectors
❌ **Don't**: `await page.click('#submit-btn-123')`  
✅ **Do**: "Find and click the submit button"

### 2. Snapshot-Based Discovery
- Take snapshots before interactions to understand current UI state
- Let Copilot discover elements dynamically
- Adapt to actual rendered interface

### 3. Semantic Element Finding
- Describe elements by their purpose and visible text
- Use aria labels, button text, and human-readable descriptions
- Don't rely on CSS classes or IDs

### 4. Validation Through Observation
- Verify outcomes by checking visible changes
- Look for success messages, state transitions, URL changes
- Take snapshots to confirm expected UI state

## Standard Test Structure

### Metadata Section
```markdown
## Metadata
- **Category**: ui
- **Priority**: critical|high|medium|low
- **Complexity**: simple|medium|complex
- **Duration**: X-Y minutes (realistic estimate)
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser
```

### Scenario Description
Brief description of what functionality is being tested and the execution approach statement:

> **Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete workflows without hard-coded selectors.

### Prerequisites
- Application URL and access requirements
- Test data requirements
- Required features/licenses
- MCP Playwright availability statement
- Framework notes (Vue.js + Element Plus)
- Routing pattern (hash routing)

### Related Specs
List other specs that are related or depend on this functionality.

### Test Steps Format
Each step follows this pattern:

```markdown
### Step N: [Action Name]
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. High-level instruction (e.g., "Navigate to the spiders page")
2. Take a snapshot to understand current UI
3. Specific actions in user terms (click, fill, verify)
4. Wait for outcomes and state changes

**Expected**: Brief description of successful outcome
**Validation**: 
- Bullet points of specific things to verify
- Observable changes in UI
- State transitions
- No error conditions
```

### Success Criteria
Comprehensive checklist of all functionality that should work:
```markdown
## Success Criteria
- [ ] Feature A works correctly
- [ ] Feature B handles errors properly
- [ ] No JavaScript console errors
- [ ] UI remains responsive
```

### Failure Scenarios
Document common failure modes and debugging approaches:
```markdown
## Failure Scenarios
- **Scenario**: [What goes wrong]
- **Symptoms**: [How to recognize it]
- **Action**: [How to debug/fix]
```

### Execution Section
Standard execution instructions:
```markdown
## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
./cli.py --spec UI-XXX --backend copilot
```

[Include standard description of how Copilot executes tests]

**MCP Playwright Tools Used:**
- List relevant tools

**Reporting Test Results:**
```bash
./tests/tools/report_test_result.py --status [passed|failed|skipped] [options]
```
```

### Cleanup Section
What cleanup is automatic vs manual.

### Notes Section
Important details about the test:
- High-level instructions reminder
- Adaptation capabilities
- Implementation variations
- Related features or edge cases

### History Section
Track creation and modification dates.

## Common UI Patterns

### Navigation
```markdown
1. Take a snapshot to see navigation options
2. Find and click the "[Menu Item]" in the sidebar/navigation
3. Wait for the page to load
4. Verify URL contains expected route
```

### Form Filling
```markdown
1. Take a snapshot to see the form structure
2. Fill all mandatory fields (marked with asterisk or required label):
   - **Text fields**: Use type or fill_form
   - **Dropdowns (Element Plus)**: Click combobox → Click option from listbox
   - **Checkboxes/Radio**: Click directly
3. Find and click the submit button (may be labeled "Create", "Save", "Submit")
4. Wait for success indication
```

### Element Plus Dropdown Interaction (IMPORTANT)
⚠️ **Element Plus uses custom dropdowns, NOT native HTML `<select>` elements**

❌ **Don't use**: `.selectOption()` - This only works on native `<select>` elements
✅ **Correct approach**:
```markdown
1. Take a snapshot to locate the combobox
2. Click the combobox (has role="combobox", usually shows "Select" placeholder)
3. Wait for listbox to appear with options
4. Click the desired option from the listbox
```

**Example - Selecting a spider:**
```markdown
1. Take snapshot to see the form
2. Click the "*Spider" combobox (opens dropdown)
3. Take snapshot to see available options
4. Click "test-spider-ui003" option from the list
5. Verify the combobox now displays "test-spider-ui003"
```

**Technical details for reference:**
- Element Plus dropdowns render as: `<input role="combobox">` + floating `<div role="listbox">` with `<div role="option">` items
- Clicking the combobox triggers `aria-expanded="true"` and shows the listbox
- Selecting an option updates the combobox display value and closes the listbox
- This pattern applies to: Spider, Node, Status, Priority, Mode, and all other dropdown selectors

### Table/List Interaction
```markdown
1. Take a snapshot of the table/list
2. Verify table columns are present: [list columns]
3. Look for the target item by name/identifier
4. Click on the item to view details OR use action buttons
```

### Deletion Pattern
```markdown
1. Find the item in the list
2. Select the item (click checkbox in row)
3. Find and click the delete button (may be enabled after selection)
4. If confirmation dialog appears, confirm the action
5. Verify item is removed from list
```

## MCP Playwright Tool Reference

### Navigation
- `mcp_playwright_browser_navigate` - Go to URL
- `mcp_playwright_browser_navigate_back` - Go back

### Inspection
- `mcp_playwright_browser_snapshot` - Get accessibility tree (preferred over screenshot)
- `mcp_playwright_browser_take_screenshot` - Visual capture

### Interaction
- `mcp_playwright_browser_click` - Click elements (use for buttons, links, **Element Plus dropdowns**)
- `mcp_playwright_browser_type` - Type text
- `mcp_playwright_browser_fill_form` - Fill multiple form fields
- `mcp_playwright_browser_hover` - Hover for tooltips/menus
- `mcp_playwright_browser_select_option` - Select from **native HTML** `<select>` only (NOT for Element Plus dropdowns)

### Waiting
- `mcp_playwright_browser_wait_for` - Wait for text/time

### Advanced
- `mcp_playwright_browser_evaluate` - Execute JavaScript
- `mcp_playwright_browser_tabs` - Manage browser tabs
- `mcp_playwright_browser_console_messages` - Check console output

## Application-Specific Details

### Crawlab Frontend
- **Framework**: Vue.js 3 with Element Plus UI library
- **Routing**: Hash routing (`/#/route`)
- **Common URL Patterns**:
  - Login: `/#/login`
  - Dashboard: `/#/home`
  - Spiders: `/#/spiders`
  - Tasks: `/#/tasks`
  - Nodes: `/#/nodes`
  - Projects: `/#/projects`

### Common UI Elements
- **Tables**: Element Plus `el-table` with columns, filters, pagination
- **Forms**: Element Plus `el-form` with validation
- **Buttons**: Element Plus `el-button` with icons
- **Dialogs**: Element Plus `el-dialog` for modals
- **Navigation**: Sidebar with menu items

### Standard Table Columns
Most list views follow similar patterns:
- Name (clickable)
- Status (with colored badges)
- Actions (View/Edit/Delete buttons)
- Timestamps (relative format like "5 minutes ago")
- Metadata columns specific to entity type

### Standard Controls
- "New [Entity]" button with plus icon (top of list)
- Search textbox (top of list)
- Filter dropdowns (top of list)
- Selection checkboxes (bulk operations)
- "Delete Selected" button (bulk action)
- Pagination (bottom of list)

## Best Practices

### 1. Always Take Snapshots Before Actions
Snapshots help Copilot understand current UI state and make intelligent decisions.

### 2. Use Descriptive Element References
Instead of technical identifiers, describe elements as users see them:
- "the sign in button"
- "the username textbox"
- "the spider named 'test-spider'"

### 3. Verify State Transitions
Don't just perform actions - verify they succeeded:
- Check URL changes
- Look for success messages
- Verify new UI state
- Confirm data appears/disappears

### 4. Handle Dynamic Content
- Wait for loading indicators to disappear
- Check for empty states vs populated data
- Handle conditional UI elements gracefully

### 5. Expect Variations
- Button text may vary ("Sign In" vs "Login")
- Forms may have different field layouts
- Table columns may be reordered
- Features may be disabled (Pro features)

### 6. Document What's Observable
Focus validation on what users can see:
- Visible text and messages
- UI element presence/absence
- Color-coded status indicators
- Navigation breadcrumbs

## Troubleshooting

### Element Not Found
1. Take a snapshot to see current UI
2. Check if page has fully loaded
3. Verify you're on the expected route
4. Look for alternative element descriptions
5. Check if feature requires specific permissions/license

### Action Doesn't Work
1. Verify element is clickable (not disabled)
2. Check for loading states
3. Look for validation errors
4. Check browser console for JavaScript errors
5. Verify prerequisites are met

### Unexpected State
1. Take snapshot to understand current state
2. Check URL to verify correct page
3. Look for error messages in UI
4. Review previous step outcomes
5. Check if data/configuration is as expected

## Spec Maintenance

### When to Update Specs
- Major UI restructuring
- New features added
- Workflow changes
- Bug fixes that affect user flow

### What to Update
- Test steps if workflow changes
- Expected outcomes if UI changes
- Success criteria if new functionality added
- Failure scenarios if new issues discovered

### What NOT to Update
- Element selectors (we don't use them)
- Specific CSS classes or IDs
- Implementation details
- JavaScript framework specifics

The beauty of Copilot testing is that minor UI changes don't require spec updates - Copilot adapts automatically!
