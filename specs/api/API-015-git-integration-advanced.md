# API-015: Git Integration - Advanced

**Category**: api  
**Priority**: P3 (Advanced Features)  
**Estimated Time**: 15 minutes  
**Automation**: script

## Objective

Validate Crawlab's advanced git integration features including pull, commit, push, branch management, and remote operations.

## Prerequisites

- Crawlab API server running at http://localhost:8080
- Valid admin credentials (username: admin, password: admin)
- Git repository already connected and cloned (from API-014 or existing)
- Write access to git repository (for commit/push operations)

## Test Coverage

### Endpoints Tested
- `POST /api/gits/{id}/pull` - Pull git repository changes
- `POST /api/gits/{id}/commit` - Commit changes to git repository
- `POST /api/gits/{id}/push` - Push git repository changes
- `GET /api/gits/{id}/branches` - Get git repository branches
- `GET /api/gits/{id}/remotes` - Get git repository remotes
- `GET /api/gits/{id}/logs` - Get git commit logs

### Test Scenarios
1. Authentication and setup
2. Pull git repository
3. Get git branches
4. Get git remotes
5. Get git commit logs
6. Commit changes (if writable)
7. Push changes (if writable)
8. Error handling
9. Cleanup

## Execution Steps

### Setup Phase
1. Login as admin user
2. Create or use existing git repository connection
3. Clone repository if not already cloned

### Test Phase

#### 1. Pull Git Repository
**Request**: `POST /api/gits/{id}/pull`
**Validation**:
- Status code: 200 (if cloned and has remote)
- Or appropriate error if not cloned
- Response indicates pull operation status

#### 2. Get Git Branches
**Request**: `GET /api/gits/{id}/branches`
**Validation**:
- Status code: 200 (if cloned)
- Response contains branches list
- At least one branch (e.g., main or master)

#### 3. Get Git Remotes
**Request**: `GET /api/gits/{id}/remotes`
**Validation**:
- Status code: 200 (if cloned)
- Response contains remotes list
- Contains origin remote

#### 4. Get Git Commit Logs
**Request**: `GET /api/gits/{id}/logs?page=1&size=10`
**Validation**:
- Status code: 200 (if cloned)
- Response contains commit history
- Pagination works correctly

#### 5. Commit Changes (Optional - requires write access)
**Request**: `POST /api/gits/{id}/commit`
```json
{
  "message": "Test commit from API"
}
```
**Validation**:
- Status code: 200 (if has changes and write access)
- Or appropriate error if no changes
- Commit created successfully

#### 6. Commit Specific Files (Optional)
**Request**: `POST /api/gits/{id}/commit`
```json
{
  "message": "Test commit specific files",
  "files": ["test.txt", "README.md"]
}
```
**Validation**:
- Status code: 200 (if files exist and changed)
- Or appropriate error if files not changed
- Only specified files committed

#### 7. Push Changes (Optional - requires write access)
**Request**: `POST /api/gits/{id}/push`
**Validation**:
- Status code: 200 (if has commits to push and write access)
- Or appropriate error if nothing to push or no access
- Push operation completed

#### 8. Error Handling Tests

**Pull without Clone**:
**Request**: `POST /api/gits/{id}/pull` on non-cloned repo
**Validation**:
- Appropriate error indicating repo not cloned
- Error message is clear

**Get Branches without Clone**:
**Request**: `GET /api/gits/{id}/branches` on non-cloned repo
**Validation**:
- Appropriate error or empty list
- Handles uncloned state gracefully

**Invalid Git ID**:
**Request**: `POST /api/gits/invalid-id-12345/pull`
**Validation**:
- Handles invalid ID gracefully
- Returns error response

**Commit without Changes**:
**Request**: `POST /api/gits/{id}/commit` with no changes
**Validation**:
- Appropriate error indicating nothing to commit
- Error message is clear

### Cleanup Phase
1. No cleanup needed (git operations are non-destructive for testing)
2. Optionally reset git repository to initial state

## Success Criteria

- Pull operation accessible (functionality depends on environment)
- Branch listing works correctly for cloned repos
- Remote listing works correctly for cloned repos
- Commit logs can be retrieved with pagination
- Commit operation accessible (actual commit depends on changes)
- Push operation accessible (actual push depends on permissions)
- Error cases handled gracefully
- Test completes in < 5 minutes

## Expected Results

### Success Indicators
- ✅ Pull endpoint accessible
- ✅ Branches retrieved successfully (if cloned)
- ✅ Remotes retrieved successfully (if cloned)
- ✅ Commit logs retrieved with pagination (if cloned)
- ✅ Commit endpoint accessible (functionality depends on changes)
- ✅ Push endpoint accessible (functionality depends on permissions)
- ✅ Error cases return appropriate responses
- ✅ Operations don't corrupt repository state

### Known Limitations
- Pull/commit/push operations require cloned repository
- Commit operations require actual file changes
- Push operations require write access to remote
- Some operations may timeout in slow network conditions
- Test focuses on API contract validation, not full git functionality
- Operations depend on git repository state and permissions

## Notes

- Most advanced git operations require repository to be cloned first
- Commit operations are read-only tests unless actual changes exist
- Push operations may be skipped in read-only test environments
- Network issues may cause operation timeouts
- Git operations can be time-consuming (pull, push)
- Test validates API contract rather than full git integration functionality
- Some endpoints may require specific permissions or repository state

## Related Tests

- API-014: Git Integration - Basic (CRUD, clone, checkout)
- API-004: Spider CRUD Operations (spiders can link to git repositories)
