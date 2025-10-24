# API-003: User Management

**Category**: API Testing  
**Priority**: High  
**Estimated Duration**: 3-5 minutes  
**Backend**: script  
**Test Status**: Draft

## Overview

This test validates the user management API endpoints, including CRUD operations and password management.

## Objectives

- Verify user creation with required and optional fields
- Test user retrieval (single and list)
- Validate user updates
- Test user deletion
- Verify password change functionality
- Ensure proper error handling for invalid operations

## Prerequisites

- Crawlab instance running and accessible
- Admin credentials available for authentication
- Test environment with NO_PROXY configured for localhost
- No existing test users with conflicting usernames

## Test Steps

### Setup
1. Authenticate as admin user
2. Record initial user count for cleanup validation

### User Creation (POST /api/users)
3. Create a new user with required fields (username, password)
   - Request body: `{"data": {"username": "test_user_api003", "password": "test123"}}`
   - Verify response contains user ID and username
   - Save user ID for subsequent tests

4. Create a user with optional fields (email, role)
   - Request body: `{"data": {"username": "test_user_api003_full", "password": "test456", "email": "test@example.com"}}`
   - Verify all fields are saved correctly

5. Attempt to create duplicate username
   - Request body: `{"data": {"username": "test_user_api003", "password": "test789"}}`
   - Verify receives error response (400 or 409)

6. Attempt to create user without required fields
   - Request body: `{"data": {"email": "nouser@example.com"}}`
   - Verify receives error response (400)

### User Retrieval (GET /api/users, GET /api/users/{id})
7. Get user list
   - Verify list includes newly created users
   - Verify pagination works (if supported)

8. Get specific user by ID
   - Use user ID from step 3
   - Verify response contains correct user data
   - Verify password is not returned in response

9. Attempt to get non-existent user
   - Use invalid ID (e.g., "000000000000000000000000")
   - Verify receives 404 error

### User Update (PUT /api/users/{id})
10. Update user email
    - Request body: `{"data": {"username": "test_user_api003", "password": "test123", "email": "updated@example.com"}}`
    - Verify email is updated
    - Verify other fields remain unchanged

11. Update username
    - Change username from "test_user_api003" to "test_user_api003_updated"
    - Verify username change is successful

12. Attempt to update to duplicate username
    - Try to change username to existing user
    - Verify receives error response

### Password Management (POST /api/users/{id}/change-password)
13. Change user password
    - Request body: `{"password": "newpass123"}`
    - Verify password change succeeds (200 OK)

14. Verify new password works
    - Attempt login with old password - should fail
    - Attempt login with new password - should succeed

15. Attempt password change with invalid format
    - Try empty password or too short password
    - Verify receives error response

### User Deletion (DELETE /api/users/{id})
16. Delete a test user
    - Delete user created in step 4
    - Verify deletion succeeds (200 OK)

17. Verify deleted user is gone
    - Attempt to GET deleted user
    - Verify receives 404 error

18. Attempt to delete non-existent user
    - Use invalid ID
    - Verify receives appropriate error (404)

### Cleanup
19. Delete all test users created during test
20. Verify user count returns to initial state

## Expected Results

### Success Criteria
- All user CRUD operations complete successfully
- User data is accurately stored and retrieved
- Password is never returned in API responses
- Password change works and old password is invalidated
- Duplicate username prevention works
- Invalid operations return appropriate error codes
- All test users are cleaned up

### API Endpoints Tested
- `POST /api/users` - Create user
- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/change-password` - Change password

## Error Cases

- Creating user with duplicate username → 400/409 error
- Creating user without required fields → 400 error
- Getting non-existent user → 404 error
- Updating to duplicate username → 400/409 error
- Deleting non-existent user → 404 error
- Invalid password format → 400 error

## Data Validation

- Username: Non-empty string
- Password: Required for creation, not returned in responses
- Email: Optional, valid email format when provided
- User ID: Valid ObjectID format
- Role: Optional field

## Cleanup Procedure

1. Delete all test users by ID
2. Verify no test users remain in system
3. Verify user count matches initial state
4. Logout and cleanup authentication tokens

## Notes

- Users cannot be created without username and password (required fields)
- Password field should never be returned in GET/PUT responses
- Email and role are optional fields
- User updates require full user object (PUT replaces entire resource)
- Admin users may have special deletion restrictions (test with regular users)

## Related Tests

- API-002: Authentication & Token Management
- API-008: Schedule Management (user permissions)
- API-009: Node Management (user access control)

## References

- OpenAPI Spec: `/api/openapi.json` - User schemas and endpoints
- Helper Module: `helpers/api/user.py`
- Helper Module: `helpers/api/auth.py`
