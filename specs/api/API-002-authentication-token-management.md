# API-002 - Authentication & Token Management

## Metadata
- **Category**: api
- **Priority**: critical
- **Complexity**: medium
- **Duration**: 2-3 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, MongoDB
- **Backend**: script

## Scenario
This test validates the complete authentication workflow including login, logout, token management (CRUD operations), and token validation. These are fundamental operations that all other API tests depend on.

**Coverage**:
- `/api/login` - POST
- `/api/logout` - POST
- `/api/tokens` - GET, POST
- `/api/tokens/{id}` - GET, DELETE
- `/api/users/me` - GET (for token validation)

## Prerequisites
- Crawlab API accessible at http://localhost:8080/api
- MongoDB accessible
- Default admin credentials (admin/admin)

## Test Steps

### Step 1: Login with Valid Credentials
**Method**: script
**Objective**: Verify successful login with admin credentials

**Actions**:
```python
from helpers.api import APIAuth, APIAssertions

auth = APIAuth()
assertions = APIAssertions()

# Login
token, response = auth.login("admin", "admin")
```

**Validation**:
- HTTP 200 status
- Token is non-empty string
- Token is JWT format (contains dots)
- Response contains 'data' field with token

**Success Criteria**:
- [ ] Login successful
- [ ] Valid token received
- [ ] Token format is correct

---

### Step 2: Verify Token by Getting Current User
**Method**: script
**Objective**: Verify token is valid by using it

**Actions**:
```python
from helpers.api import UserHelper

user_helper = UserHelper()

# Get current user with token
user_data, response = user_helper.get_me(token)
```

**Validation**:
- HTTP 200 status
- User data contains username 'admin'
- User data contains '_id' field

**Success Criteria**:
- [ ] Token is valid
- [ ] Current user retrieved
- [ ] Username matches 'admin'

---

### Step 3: Create API Token
**Method**: script
**Objective**: Create a new API token

**Actions**:
```python
# Create token
token_name = "api-test-token-" + str(int(time.time()))
token_id, response = auth.create_token(token, token_name)
```

**Validation**:
- HTTP 200 status
- Token ID returned
- Token ID is non-empty string

**Success Criteria**:
- [ ] Token created successfully
- [ ] Token ID received

---

### Step 4: Get Token Details
**Method**: script
**Objective**: Retrieve token details by ID

**Actions**:
```python
# Get token
token_data, response = auth.get_token(token, token_id)
```

**Validation**:
- HTTP 200 status
- Token data contains '_id' field
- Token data contains 'name' field matching created name
- Token name matches what was created

**Success Criteria**:
- [ ] Token retrieved successfully
- [ ] Token data is correct

---

### Step 5: List All Tokens
**Method**: script
**Objective**: List all tokens and verify created token is present

**Actions**:
```python
# List tokens
tokens_list, response = auth.list_tokens(token)
```

**Validation**:
- HTTP 200 status
- Response is a list
- Created token is in the list
- List length > 0

**Success Criteria**:
- [ ] Tokens listed successfully
- [ ] Created token found in list

---

### Step 6: Delete API Token
**Method**: script
**Objective**: Delete the created token

**Actions**:
```python
# Delete token
success, response = auth.delete_token(token, token_id)
```

**Validation**:
- HTTP 200 status
- Operation successful

**Success Criteria**:
- [ ] Token deleted successfully

---

### Step 7: Verify Token Was Deleted
**Method**: script
**Objective**: Confirm token no longer exists

**Actions**:
```python
# Try to get deleted token
token_data, response = auth.get_token(token, token_id)
```

**Validation**:
- HTTP 404 status (or similar error)
- Token not found

**Success Criteria**:
- [ ] Token no longer exists
- [ ] Appropriate error returned

---

### Step 8: Login with Invalid Credentials
**Method**: script
**Objective**: Verify login fails with wrong password

**Actions**:
```python
# Try login with wrong password
invalid_token, response = auth.login("admin", "wrongpassword")
```

**Validation**:
- HTTP 401 or 403 status
- No token returned (None)
- Error message in response

**Success Criteria**:
- [ ] Login fails appropriately
- [ ] No token issued
- [ ] Error message received

---

### Step 9: Use Invalid Token
**Method**: script
**Objective**: Verify invalid token is rejected

**Actions**:
```python
# Try to use invalid token
invalid_token = "invalid.jwt.token"
user_data, response = user_helper.get_me(invalid_token)
```

**Validation**:
- HTTP 401 status
- No user data returned
- Error indicates authentication failure

**Success Criteria**:
- [ ] Invalid token rejected
- [ ] Proper error response

---

### Step 10: Logout
**Method**: script
**Objective**: Logout and invalidate token

**Actions**:
```python
# Logout
success, response = auth.logout(token)
```

**Validation**:
- HTTP 200 status
- Operation successful

**Success Criteria**:
- [ ] Logout successful

---

### Step 11: Verify Token Invalidated After Logout
**Method**: script
**Objective**: Confirm token no longer works after logout

**Actions**:
```python
# Try to use token after logout
user_data, response = user_helper.get_me(token)
```

**Validation**:
- HTTP 401 status
- Token rejected
- Must login again

**Success Criteria**:
- [ ] Token no longer valid after logout
- [ ] Proper authentication error

## Success Criteria Summary
- [ ] Login successful with valid credentials
- [ ] Token validation works
- [ ] Token CRUD operations work (Create, Read, List, Delete)
- [ ] Invalid credentials rejected
- [ ] Invalid token rejected
- [ ] Logout invalidates token
- [ ] All endpoints return proper status codes
- [ ] No unexpected errors

## Failure Scenarios

### Scenario: Login Fails
- **Symptoms**: Cannot get token
- **Action**: 
  1. Verify API is accessible
  2. Check credentials are correct
  3. Review master logs for auth errors

### Scenario: Token Operations Fail
- **Symptoms**: Cannot create/get/delete tokens
- **Action**:
  1. Verify token has admin privileges
  2. Check database connection
  3. Review permissions

## Execution

### Automated
```bash
cd /home/marvin/projects/crawlab-team/crawlab-pro/crawlab-test
uv run ./cli.py --spec API-002
```

### Manual
```bash
cd runners/api
python API_002_auth_token.py
```

## Cleanup
All created tokens are deleted as part of the test flow.

## Notes
- This test is foundational - all other API tests depend on authentication
- Token format validation ensures JWT standard compliance
- Tests both positive and negative cases for robustness
- Helper modules make this test maintainable and reusable

## History
- **Created**: 2024-10-24, Assistant
- **Purpose**: Comprehensive authentication and token management validation
