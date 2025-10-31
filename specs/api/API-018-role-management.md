# API-018: Role Management

**Category**: API  
**Priority**: P2 (Core Features)  
**Estimated Time**: 15 minutes  
**Backend**: script  

## Objective

Validate role management functionality through the Crawlab API. Roles define user permissions and access control within the system.

## Coverage

This test covers the following endpoints:

### Roles (5)
- `GET /roles` - List roles
- `GET /roles/{id}` - Get role details
- `PUT /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role
- `DELETE /roles` - Batch delete roles

**Total Coverage**: 5 endpoints

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid authentication credentials (admin/admin)
- System has default roles (admin, normal user, etc.)

## Test Execution Steps

### Setup
1. Authenticate and get token
2. Record initial role count for validation

### Role Listing
3. List all roles
   - Verify default system roles exist
   - Verify pagination parameters work
   - Verify user counts are included in response
   - Check that `is_root_admin` flag is set correctly

4. Get role details by ID
   - Select a role from the list
   - Verify role details are complete
   - Verify permissions/pages arrays are present
   - Check `is_root_admin` matches `root_admin` field

### Role Updates
5. Update role properties (name, description)
   - Update a test role's name and description
   - Verify changes are persisted
   - Verify user associations remain intact

6. Update role permissions
   - Modify role's pages/permissions arrays
   - Verify permission changes are applied
   - Ensure changes don't affect other roles

7. Attempt to update non-existent role
   - Use invalid role ID
   - Verify receives 404 error

### Role Deletion
8. Delete single role
   - Create a temporary test role first (if possible)
   - Delete the test role
   - Verify deletion succeeds
   - Verify role is removed from list

9. Verify deleted role cannot be retrieved
   - Attempt to GET deleted role
   - Verify receives 404 error

10. Batch delete roles
    - Create multiple test roles (if possible)
    - Delete them in batch using DELETE /roles
    - Verify all roles are deleted

11. Attempt to delete system/protected roles
    - Try to delete admin or root roles
    - Verify appropriate error or protection mechanism

### Edge Cases
12. Invalid role ID format
    - Use malformed ObjectID
    - Verify receives 400 error

13. List roles with filters
    - Test filtering by name pattern (if supported)
    - Test sorting by different fields
    - Verify pagination with various page sizes

### Cleanup
14. Delete any test roles created during testing
15. Verify role count returns to expected state

## Expected Results

### Success Criteria
- All role listing operations return valid data
- Role details include complete information
- Role updates persist correctly
- Permissions/pages arrays are handled properly
- Role deletion works for non-system roles
- Batch operations complete successfully
- System roles are protected from deletion
- User counts are accurately calculated
- `is_root_admin` flag works correctly
- Invalid operations return appropriate error codes

### Key Validations
1. **Role Structure**:
   - `_id`: Valid ObjectID
   - `name`: Non-empty string
   - `description`: String (optional)
   - `pages`: Array of page permissions
   - `permissions`: Array of specific permissions
   - `root_admin`: Boolean
   - `is_root_admin`: Boolean (derived field)
   - `user_count`: Integer (number of users with this role)

2. **Default Roles**:
   - System should have at least one admin role
   - Root admin role should have `root_admin: true`
   - Role list should not be empty

3. **User Count**:
   - Each role should include accurate user count
   - Count should update when users are assigned/unassigned

## Error Cases

- Getting non-existent role → 404 error
- Updating non-existent role → 404 error
- Deleting protected system role → 400/403 error
- Invalid ObjectID format → 400 error
- Empty/invalid update data → 400 error

## Data Validation

- Role ID: Valid MongoDB ObjectID format
- Name: Non-empty string, unique identifier
- Description: Optional string
- Pages: Array of page identifiers
- Permissions: Array of permission strings
- Root Admin: Boolean flag for super admin privileges
- User Count: Non-negative integer

## Cleanup Procedure

1. Delete all test roles created during testing
2. Verify no test roles remain in system
3. Verify role count matches expected state
4. Logout and cleanup authentication tokens

## Notes

- System/default roles may have special protection mechanisms
- Deleting a role may require handling associated users
- The `is_root_admin` field is a computed field derived from `root_admin`
- Role permissions affect user access throughout the system
- Some roles may be required for system operation
- User count is calculated by querying users with matching role IDs

## Related Tests

- API-002: Authentication & Token Management
- API-003: User Management (roles assigned to users)

## References

- OpenAPI Spec: `/api/openapi.json` - Role schemas and endpoints
- Controller: `core/controllers/role.go`
- Model: Check role model definition for complete schema
