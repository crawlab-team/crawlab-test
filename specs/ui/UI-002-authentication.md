````markdown
# UI-002 - Authentication and Session Management

## Metadata
- **Category**: ui
- **Priority**: critical
- **Complexity**: simple
- **Duration**: 8-12 minutes
- **Environment**: staging/local
- **Dependencies**: crawlab-frontend, crawlab-master, browser

## Scenario
This test validates the complete authentication lifecycle including login, session management, and logout. It ensures secure user authentication, proper session handling, and correct redirect behavior.

**Execution Approach**: This test is designed for Copilot execution using MCP Playwright tools. Copilot will interactively explore the UI, discover elements dynamically, and complete authentication workflows without hard-coded selectors.

## Prerequisites
- Crawlab web interface accessible at http://localhost:8080 or http://localhost:5173
- Valid user credentials (admin/admin)
- Browser with JavaScript enabled and cookies allowed
- **MCP Playwright server available** for interactive UI exploration
- **Application uses Vue.js with Element Plus** UI framework
- **Hash routing**: Application uses `/#/` URL patterns

## Related Specs
- **UI-001**: Spider Management (requires authenticated session)
- **UI-013**: Permissions Management (for role-based access testing)

## Test Steps

### Step 1: Verify Auto-Redirect to Login
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Clear browser cookies and local storage to ensure clean state
2. Navigate to http://localhost:8080 (or configured URL)
3. Take a snapshot to observe initial page state
4. Verify automatic redirect occurs to login page

**Expected**: Unauthenticated users redirect to login
**Validation**: 
- URL changes to contain `/login` route (e.g., `/#/login`)
- Login form is displayed
- No dashboard or protected content is visible

---

### Step 2: Examine Login Form Elements
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Take a snapshot of the login page
2. Identify and verify presence of login form elements:
   - Username/email textbox
   - Password textbox (masked input)
   - Sign In button (not "Login" - verify actual button text)
   - Language toggle option (中文/English)
   - "Forgot Password" link (if available)
   - Initial credentials hint (e.g., "Initial Username/Password: admin/admin")
3. Verify form is interactive and ready for input

**Expected**: Login form displays all required elements
**Validation**:
- Username field is visible and editable
- Password field is visible, editable, and masked
- Sign In button is enabled and clickable
- Language selector is functional
- Visual design matches application theme

---

### Step 3: Test Login with Valid Credentials
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Locate the username field and fill with "admin"
2. Locate the password field and fill with "admin"
3. Find and click the "Sign In" button
4. Wait for authentication response and page transition
5. Take a snapshot after successful login

**Expected**: Successful authentication and dashboard access
**Validation**: 
- No error messages displayed
- URL changes to dashboard route (e.g., `/#/home`)
- User avatar/menu appears in header (typically shows "AD" or user initials)
- Main navigation sidebar is visible and accessible
- Dashboard content loads successfully
- Session token is stored (check browser storage if needed)

---

### Step 4: Verify Session Persistence
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. After successful login, navigate to different pages within the application
2. Navigate to spider management page
3. Navigate to task management page
4. Refresh the browser page
5. Verify user remains logged in after refresh
6. Check URL remains on protected route
7. Verify user menu/avatar still visible

**Expected**: Session persists across navigation and refresh
**Validation**:
- User remains authenticated after browser refresh
- No redirect to login page occurs
- All navigation functions normally
- User state is maintained
- Protected routes remain accessible

---

### Step 5: Test Logout Functionality
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. From authenticated state, locate user avatar/menu in header
2. Click to open user dropdown menu
3. Take a snapshot to see menu options
4. Find and click "Logout" or "Sign Out" option
5. Wait for logout process to complete
6. Take a snapshot after logout

**Expected**: Successful logout and redirect to login
**Validation**: 
- User menu closes after clicking logout
- URL changes back to login page (/#/login)
- Session is cleared (check browser storage if needed)
- User avatar/menu disappears from header
- Login form is displayed again
- No protected content is visible

---

### Step 6: Verify Protected Route Access After Logout
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. After logout, attempt to navigate directly to a protected route
2. Type URL with protected route in address bar (e.g., /#/spiders)
3. Press Enter to navigate
4. Observe application behavior

**Expected**: Redirect to login for unauthenticated access
**Validation**: 
- Direct access to protected routes is blocked
- User is redirected to login page
- No protected content is visible
- Login page displays with appropriate message (if any)

---

### Step 7: Test Login with Invalid Credentials
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. On login page, fill username field with "invalid_user"
2. Fill password field with "wrong_password"
3. Click "Sign In" button
4. Take a snapshot to observe error handling
5. Look for error message in UI

**Expected**: Login fails with appropriate error message
**Validation**: 
- Login attempt is rejected
- Error message is displayed (e.g., "Invalid username or password", "Authentication failed")
- User remains on login page
- No redirect to dashboard occurs
- Form fields may be cleared or highlighted
- Button becomes clickable again after error

---

### Step 8: Test Form Validation
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Test empty form submission:
   - Leave both username and password fields empty
   - Click Sign In button
   - Observe validation behavior

2. Test partial form submission:
   - Fill only username field
   - Leave password empty
   - Click Sign In button
   - Observe validation

3. Test password visibility toggle (if available):
   - Fill password field
   - Look for show/hide password icon
   - Click to toggle password visibility
   - Verify password becomes visible/hidden

**Expected**: Form validation prevents invalid submissions
**Validation**: 
- Required field validation works
- Validation messages are clear and helpful
- Form submission is blocked for invalid input
- Password visibility toggle functions (if present)
- Client-side validation occurs before server request

---

### Step 9: Test Session Timeout (Optional)
**Method**: automated (Copilot with MCP Playwright)
**Action**: 
1. Login successfully
2. Note the configured session timeout duration (check documentation or system settings)
3. Leave application idle for timeout period
4. After timeout, attempt to perform an action (e.g., navigate to a page)
5. Observe session timeout handling

**Expected**: Session expires and requires re-authentication
**Validation**: 
- After timeout, user is redirected to login
- Appropriate timeout message may be displayed
- Session data is cleared
- Re-authentication is required to continue

**Note**: This step may be skipped if session timeout is very long (hours) or disabled in test environment.

---

## Success Criteria
- [ ] Unauthenticated users redirect to login page
- [ ] Login form displays all required elements correctly
- [ ] Valid credentials authenticate successfully
- [ ] Dashboard loads after successful login
- [ ] Session persists across page navigation
- [ ] Session persists across browser refresh
- [ ] Logout functionality works correctly
- [ ] Protected routes require authentication
- [ ] Invalid credentials show appropriate error
- [ ] Form validation prevents empty submissions
- [ ] Password field masks input properly
- [ ] No JavaScript errors in browser console
- [ ] Session security is maintained
- [ ] All state transitions are smooth

## Failure Scenarios
- **Scenario**: Login button doesn't respond
- **Symptoms**: Click Sign In but nothing happens, no error shown
- **Action**: Check browser console for errors, verify API endpoint is accessible, check network tab for request

- **Scenario**: Successful login but no redirect
- **Symptoms**: Authentication succeeds but stays on login page
- **Action**: Check routing configuration, verify dashboard route exists, check for JavaScript errors

- **Scenario**: Session lost immediately after login
- **Symptoms**: User redirected to login right after successful authentication
- **Action**: Check session storage mechanism, verify cookie settings, check for conflicting auth logic

- **Scenario**: Logout doesn't clear session
- **Symptoms**: After logout, user can still access protected routes
- **Action**: Verify logout API call succeeds, check session cleanup logic, verify token removal

- **Scenario**: Error message not displayed for invalid credentials
- **Symptoms**: Login fails silently without user feedback
- **Action**: Check error handling in frontend, verify API returns proper error codes, check message display logic

## Execution

### Automated Execution with Copilot

Execute this test using Copilot with MCP Playwright support:

```bash
# From tests directory
./cli.py --spec UI-002 --backend copilot
```

**How Copilot Executes This Test:**
1. Copilot reads the high-level test steps from this specification
2. Uses MCP Playwright tools (`#mcp_playwright_browser_*`) to:
   - Navigate pages and handle redirects
   - Take snapshots to discover UI structure dynamically
   - Find form elements without hard-coded selectors
   - Fill fields, click buttons, and interact with the UI
   - Verify expected outcomes and state transitions
3. Adapts to UI changes automatically by exploring the actual rendered interface
4. Reports results using the reporting tool

**Reporting Test Results:**
After completing the test execution, Copilot should call the reporting tool:

```bash
# All tests passed
./tests/tools/report_test_result.py --status passed --total-steps 9 --completed-steps 9

# Test failed
./tests/tools/report_test_result.py --status failed --total-steps 9 --completed-steps 4 --failed-steps 1 --reason "Step 5: Logout button not found in user menu"
```

**MCP Playwright Tools Used:**
- `mcp_playwright_browser_navigate` - Navigate to URLs and handle redirects
- `mcp_playwright_browser_snapshot` - Inspect page structure and state
- `mcp_playwright_browser_fill_form` - Fill login form fields
- `mcp_playwright_browser_click` - Click buttons and menu items
- `mcp_playwright_browser_type` - Type into input fields
- `mcp_playwright_browser_screenshot` - Capture visual evidence

**Advantages over Hard-Coded Scripts:**
- No brittle selectors that break when UI changes
- Adapts to different button text ("Sign In" vs "Login")
- Works across different language settings
- Discovers form validation dynamically
- Self-healing when element structure changes

### Manual Testing (Fallback)
If automated testing is unavailable:
1. Follow test steps manually in browser
2. Document any differences or issues encountered
3. Take screenshots for evidence
4. Note actual vs expected behavior

## Cleanup
- Browser state: Automatic cleanup via MCP Playwright
- Session data: Cleared by logout step
- Test results: Reported by Copilot
- No manual cleanup required

## Notes
- **This test uses high-level instructions, not hard-coded selectors**
- Copilot dynamically discovers authentication UI elements
- Test adapts to different login form implementations
- Button text may vary ("Sign In", "Login", "Submit") - test discovers actual text
- Session timeout testing is optional due to time requirements
- Password visibility toggle may not be present in all implementations
- "Remember me" functionality not currently tested but can be added
- Multi-factor authentication not covered in this spec
- SSO integration covered in separate spec (UI-013)

## History
- **Created**: 2025-10-20, Assistant
- **Modified**: 2025-10-20, Converted to Copilot execution approach with comprehensive authentication flow
- **Last Run**: -
````
