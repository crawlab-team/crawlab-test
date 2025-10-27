# API-014: Git Integration - Basic

**Category**: api  
**Priority**: P3 (Advanced Features)  
**Estimated Time**: 15 minutes  
**Automation**: script

## Objective

Validate Crawlab's basic git integration features including repository connection CRUD operations, cloning, and branch checkout.

## Prerequisites

- Crawlab API server running at http://localhost:8080
- Valid admin credentials (username: admin, password: admin)
- Public git repository for testing (e.g., https://github.com/crawlab-team/crawlab-test-repo)

## Test Coverage

### Endpoints Tested
- `POST /api/gits` - Create git repository connection
- `GET /api/gits` - List git repositories
- `GET /api/gits/{id}` - Get git repository details
- `PUT /api/gits/{id}` - Update git repository
- `DELETE /api/gits/{id}` - Delete git repository
- `PATCH /api/gits` - Batch update git repositories
- `DELETE /api/gits` - Batch delete git repositories
- `POST /api/gits/{id}/clone` - Clone git repository
- `POST /api/gits/{id}/checkout` - Checkout git branch

### Test Scenarios
1. Authentication and setup
2. Create git repository connection
3. Get git repository details
4. List git repositories
5. Update git repository
6. Clone git repository
7. Checkout git branch
8. Batch operations (update, delete)
9. Error handling
10. Cleanup

## Execution Steps

### Setup Phase
1. Login as admin user
2. Store authentication token

### Test Phase

#### 1. Create Git Repository Connection
**Request**: `POST /api/gits`
```json
{
  "data": {
    "name": "test-git-repo",
    "url": "https://github.com/crawlab-team/crawlab-test-repo",
    "auth_type": "http"
  }
}
```
**Validation**:
- Status code: 200 or 201
- Response contains git ID
- Response contains name, url fields

#### 2. Get Git Repository Details
**Request**: `GET /api/gits/{id}`
**Validation**:
- Status code: 200
- Response contains git data
- Name matches created git

#### 3. List Git Repositories
**Request**: `GET /api/gits?page=1&size=10`
**Validation**:
- Status code: 200
- Response contains data array
- Created git appears in list

#### 4. Update Git Repository
**Request**: `PUT /api/gits/{id}`
```json
{
  "data": {
    "name": "test-git-repo-updated"
  }
}
```
**Validation**:
- Status code: 200
- Name updated successfully

#### 5. Clone Git Repository (Optional - requires git server access)
**Request**: `POST /api/gits/{id}/clone`
```json
{
  "branch": "main"
}
```
**Validation**:
- Status code: 200 (if git accessible)
- Or appropriate error if network restricted
- Note: Cloning may take time or fail in test environment

#### 6. Checkout Git Branch (Optional - requires cloned repo)
**Request**: `POST /api/gits/{id}/checkout`
```json
{
  "branch": "main"
}
```
**Validation**:
- Status code: 200 (if repo cloned)
- Or appropriate error if not cloned

#### 7. Pagination Test
**Request**: `GET /api/gits?page=1&size=1`
**Validation**:
- Response respects size parameter
- Pagination works correctly

#### 8. Batch Update Git Repositories
**Request**: `PATCH /api/gits`
```json
{
  "ids": ["git_id_1", "git_id_2"],
  "update": {
    "description": "Batch updated"
  }
}
```
**Validation**:
- Status code: 200
- Multiple gits updated

#### 9. Error Handling Tests

**Invalid Git ID**:
**Request**: `GET /api/gits/invalid-id-12345`
**Validation**:
- Handles invalid ID gracefully
- Returns empty data or error

**Missing Required Fields**:
**Request**: `POST /api/gits` with empty data
**Validation**:
- Status code: 400 or appropriate error
- Error message indicates missing fields

**Invalid URL**:
**Request**: `POST /api/gits` with invalid URL
**Validation**:
- Status code: 400 or accepts but fails on clone
- Appropriate error handling

### Cleanup Phase
1. Delete all test git repositories
2. Verify cleanup successful

## Success Criteria

- All CRUD operations work correctly
- Pagination and filtering function properly
- Batch operations execute successfully
- Clone operation accessible (functionality depends on environment)
- Checkout operation accessible (functionality depends on cloned state)
- Error cases handled gracefully
- No resource leaks after cleanup
- Test completes in < 5 minutes

## Expected Results

### Success Indicators
- ✅ Git repository created successfully
- ✅ Git repository retrieved by ID
- ✅ Git repositories listed with pagination
- ✅ Git repository updated successfully
- ✅ Clone endpoint accessible (actual cloning may fail)
- ✅ Checkout endpoint accessible (actual checkout may fail)
- ✅ Batch operations execute
- ✅ Error cases return appropriate responses
- ✅ All test resources cleaned up

### Known Limitations
- Clone/checkout operations may fail in isolated test environments without network access
- Clone operations require valid git credentials for private repositories
- Actual git operations (clone, checkout) may take significant time
- Test focuses on API contract validation, not full git functionality

## Notes

- Clone and checkout operations are tested for endpoint availability but may not complete successfully in all environments
- Public repositories should be used for testing to avoid authentication issues
- Git operations (clone, pull, push) can be time-consuming
- Some endpoints may require specific git repository state (e.g., cloned before checkout)
- Test validates API contract rather than full git integration functionality

## Related Tests

- API-015: Git Integration - Advanced (pull, commit, push, branches, remotes)
- API-004: Spider CRUD Operations (spiders can link to git repositories)
