# API-019: Projects & Environments

**Category**: API  
**Priority**: P3 (Advanced Features)  
**Estimated Time**: 15 minutes  
**Backend**: script  

## Objective

Validate project and environment management functionality through the Crawlab API. Projects and environments help organize spiders and tasks.

## Coverage

This test covers the following endpoints:

### Projects (5)
- `POST /projects` - Create project
- `GET /projects` - List projects
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `PATCH /projects` - Batch update projects

### Environments (5)
- `POST /environments` - Create environment
- `GET /environments` - List environments
- `GET /environments/{id}` - Get environment details
- `PUT /environments/{id}` - Update environment
- `DELETE /environments/{id}` - Delete environment
- `PATCH /environments` - Batch update environments

**Total Coverage**: 10 endpoints (plus 2 batch operations)

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid authentication credentials (admin/admin)

## Test Execution Steps

### Setup
1. Authenticate and get token

### Projects
2. Create project
3. Verify project created with correct properties
4. List projects with pagination
5. Get project details by ID
6. Update project properties
7. Verify project updated
8. Create second project for batch operations
9. Batch update multiple projects
10. Delete single project
11. Verify project deleted

### Environments
12. Create environment
13. Verify environment created with correct properties
14. List environments with pagination
15. Get environment details by ID
16. Update environment properties
17. Verify environment updated
18. Create second environment for batch operations
19. Batch update multiple environments
20. Delete single environment
21. Verify environment deleted

### Edge Cases
22. Test project creation with duplicate name
23. Test environment with invalid properties
24. Test operations on non-existent IDs
25. Test batch operations with invalid IDs

### Cleanup
26. Cleanup remaining test resources
27. Logout

## Success Criteria

- Authentication successful
- Projects can be created with name and description
- Environments can be created with name and configuration
- List operations support pagination
- Get operations return correct details
- Update operations persist changes
- Delete operations remove resources
- Batch operations work correctly
- Invalid operations return appropriate errors
- All test resources cleaned up

## Expected Results

- All API endpoints respond with appropriate status codes
- Projects organize related spiders
- Environments define execution contexts
- Batch operations handle multiple IDs correctly
- Invalid parameters return 400/404 errors
- Operations on non-existent resources return 404
- Duplicate names may be allowed or rejected (to be verified)

## Notes

- Projects and environments are organizational features
- They may have relationships with spiders and tasks
- Test focuses on CRUD operations and API correctness
- Actual usage requires integration with spider management
