# API-016: Database ORM & Export

**Category**: API  
**Priority**: P3 (Advanced Features)  
**Estimated Time**: 20 minutes  
**Backend**: script  

## Objective

Validate database ORM (Object-Relational Mapping) configuration and data export functionality through the Crawlab API.

## Coverage

This test covers the following endpoints:

### ORM Endpoints (3)
- `GET /api/databases/{id}/orm/compatibility` - Check ORM compatibility
- `GET /api/databases/{id}/orm/status` - Get ORM status
- `PUT /api/databases/{id}/orm/status` - Update ORM status
- `POST /api/databases/{id}/orm/initialize` - Initialize ORM

### Export Endpoints (3)
- `POST /api/databases/{id}/export/{type}` - Start data export
- `GET /api/databases/{id}/export/{type}/{exportId}` - Get export status
- `GET /api/databases/{id}/export/{type}/{exportId}/download` - Download export

**Total Coverage**: 6 endpoints

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid authentication credentials (admin/admin)
- MongoDB or other database available for testing

## Test Execution Steps

### Setup
1. Authenticate and get token
2. Create test database connection (MongoDB)
3. Verify database connection

### ORM Operations
4. Check ORM compatibility for database
5. Get initial ORM status
6. Enable ORM for database
7. Verify ORM enabled
8. Initialize ORM (if supported)
9. Disable ORM
10. Verify ORM disabled

### Export Operations
11. Start CSV export for table/collection
12. Verify export ID returned
13. Get export status
14. Wait for export to complete (or reach terminal state)
15. Get export download URL (if completed)
16. Start JSON export
17. Verify JSON export started
18. Test invalid export type
19. Test export with filter
20. Test export for non-existent table

### Edge Cases
21. Test ORM operations on invalid database ID
22. Test export operations on invalid database ID
23. Test get export status with invalid export ID

### Cleanup
24. Delete test database
25. Logout

## Success Criteria

- Authentication successful
- Database created and connection verified
- ORM compatibility check returns valid response
- ORM can be enabled/disabled successfully
- ORM status reflects changes correctly
- CSV export starts successfully and returns export ID
- Export status can be retrieved
- JSON export works
- Invalid export type handled appropriately
- Invalid database/export IDs return appropriate errors
- Test database cleaned up

## Expected Results

- All API endpoints respond with appropriate status codes
- ORM compatibility check identifies whether database supports ORM
- ORM status updates persist correctly
- Export operations return valid export IDs
- Export status transitions appropriately (pending → processing → completed/failed)
- Invalid parameters return 400/404 errors
- Operations on non-existent resources return 404

## Notes

- ORM features may not be supported by all database types
- Export operations may be asynchronous and require polling for completion
- Some databases may not support ORM initialization
- Export files may require cleanup after test
- Test validates API contract rather than full export functionality
- Actual export completion requires real database with data
