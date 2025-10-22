# Git Integration Test Specification

## Overview
Test Git repository integration features including repository connection, synchronization, branch management, and version control for spiders.

## Test Environment
- **Target URL**: `http://localhost:5173`
- **Test Database**: `mongodb://dev_user:dev_password@localhost:27018/crawlab_test?authSource=admin`
- **Prerequisites**: Authenticated user, Git repository access, Pro license
- **Test Repository**: Use a dedicated test repository with sample spider code

---

## Test Cases

### TC-07-01: Connect Git Repository
**Objective**: Verify connecting a Git repository to Crawlab
**Priority**: High
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to Git Integration section
2. Click "Add Repository" button
3. Enter repository details:
   - Name: "Test Spider Repository"
   - URL: Git repository URL
   - Branch: "main"
   - Authentication method
4. Test connection to repository
5. Verify repository is successfully connected
6. Check repository status shows "Connected"
7. Verify repository appears in the list
8. Test repository details view

**Expected Results**:
- Repository connection form validates inputs
- Authentication methods work correctly
- Connection test provides clear feedback
- Repository is listed with correct status
- Repository details are accessible

### TC-07-02: Repository Synchronization
**Objective**: Test synchronizing repository content with Crawlab
**Priority**: High
**Estimated Duration**: 5 minutes

**Steps**:
1. Select connected repository
2. Click "Sync" button to pull latest changes
3. Verify sync progress indicator
4. Check sync logs for detailed information
5. Verify spider files are imported correctly
6. Check file structure matches repository
7. Test automatic sync configuration
8. Verify sync status and timestamp

**Expected Results**:
- Synchronization completes successfully
- Progress is clearly indicated
- Spider files are correctly imported
- File structure is preserved
- Sync logs provide useful information

### TC-07-03: Branch Management
**Objective**: Test Git branch switching and management
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. View current branch information
2. Click "Switch Branch" option
3. Select different branch from dropdown
4. Verify branch switch confirmation
5. Confirm branch switch operation
6. Verify spiders update to new branch content
7. Test switching back to original branch
8. Check branch history and changes

**Expected Results**:
- Available branches are listed correctly
- Branch switching works smoothly
- Spider content updates appropriately
- Branch changes are tracked
- Switch operations are reversible

### TC-07-04: Commit and Version Tracking
**Objective**: Verify commit tracking and version history
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to repository commit history
2. View list of recent commits
3. Click on specific commit to view details
4. Verify commit information:
   - Commit hash
   - Author
   - Date
   - Message
   - Changed files
5. Test filtering commits by date range
6. Compare different commit versions
7. View file changes in specific commits

**Expected Results**:
- Commit history is complete and accurate
- Commit details are comprehensive
- File changes are clearly displayed
- Filtering options work correctly
- Version comparison is functional

### TC-07-05: Spider Import from Repository
**Objective**: Test importing spiders from Git repository
**Priority**: High
**Estimated Duration**: 5 minutes

**Steps**:
1. Navigate to Spider Import section
2. Select Git repository as source
3. Choose specific folder/files to import
4. Configure import settings:
   - Spider name
   - Project assignment
   - Execution environment
5. Preview import changes
6. Execute spider import
7. Verify imported spiders appear in spider list
8. Test running imported spider

**Expected Results**:
- Import wizard guides user clearly
- File selection works intuitively
- Import preview is accurate
- Spiders are imported correctly
- Imported spiders execute successfully

### TC-07-06: Repository Authentication
**Objective**: Test different Git authentication methods
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Test SSH key authentication:
   - Add SSH private key
   - Verify key validation
   - Test repository connection
2. Test username/password authentication:
   - Enter credentials
   - Test with wrong credentials
   - Verify error handling
3. Test token-based authentication:
   - Add personal access token
   - Verify token permissions
   - Test repository access
4. Update authentication credentials

**Expected Results**:
- All authentication methods work correctly
- Invalid credentials show appropriate errors
- Credential updates are applied immediately
- Security is maintained for stored credentials

### TC-07-07: Conflict Resolution
**Objective**: Test handling Git conflicts and resolution
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Create conflicting changes scenario
2. Attempt repository synchronization
3. Verify conflict detection and notification
4. View conflict details and affected files
5. Choose conflict resolution strategy:
   - Keep repository version
   - Keep local version
   - Manual resolution
6. Resolve conflicts and complete sync
7. Verify resolution is successful

**Expected Results**:
- Conflicts are detected automatically
- Clear conflict information is provided
- Resolution options are available
- Manual resolution is possible
- Conflicts are resolved successfully

### TC-07-08: Webhook Integration
**Objective**: Test Git webhook integration for automatic updates
**Priority**: Low
**Estimated Duration**: 4 minutes

**Steps**:
1. Configure webhook URL in repository settings
2. Set up webhook events to listen for
3. Make changes to repository
4. Verify webhook triggers automatic sync
5. Check webhook delivery logs
6. Test webhook authentication
7. Verify sync happens without manual intervention
8. Test webhook failure handling

**Expected Results**:
- Webhook setup is straightforward
- Automatic sync works reliably
- Webhook logs provide useful information
- Authentication is secure
- Failures are handled gracefully

---

## Test Data Requirements

### Test Repository Structure
```
test-spider-repo/
├── spiders/
│   ├── example_spider.py
│   ├── data_collector.py
│   └── web_scraper.js
├── requirements.txt
├── package.json
└── README.md
```

### Repository Scenarios
- **Public repository**: For basic connectivity testing
- **Private repository**: For authentication testing
- **Multi-branch repository**: For branch management testing
- **Repository with conflicts**: For conflict resolution testing

### Authentication Test Data
- Valid SSH keys
- Invalid SSH keys
- Valid username/password combinations
- Invalid credentials
- Valid access tokens
- Expired/invalid tokens

## Success Criteria
- Git repositories connect successfully
- Synchronization works reliably
- Branch switching is smooth
- Authentication methods are secure
- Conflict resolution is effective
- Webhook integration functions properly

## Performance Benchmarks
- Repository connection: < 10 seconds
- Synchronization: < 30 seconds for typical repository
- Branch switching: < 15 seconds
- Import operation: < 45 seconds for 10 spiders
- Webhook response: < 5 seconds

## Security Considerations
- Credentials are stored securely
- SSH keys are properly managed
- Access tokens have appropriate permissions
- Webhook endpoints are authenticated
- Repository access is properly authorized
