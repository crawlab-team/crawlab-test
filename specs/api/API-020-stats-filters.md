# API-020: Stats & Filters

**Category**: API  
**Priority**: P3 (Advanced Features)  
**Estimated Time**: 10 minutes  
**Backend**: script  

## Objective

Validate statistics and filter management functionality through the Crawlab API. These endpoints provide system metrics and dynamic filter options for the UI.

## Coverage

This test covers the following endpoints:

### Statistics (3)
- `GET /stats/overview` - Get system overview statistics
- `GET /stats/daily` - Get daily statistics
- `GET /stats/tasks` - Get task statistics

### Filters (3)
- `GET /filters/{col}` - Get filter options for collection
- `GET /filters/{col}/{value}` - Get filter options with value filter
- `GET /filters/{col}/{value}/{label}` - Get filter options with value and label

**Total Coverage**: 6 endpoints

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid authentication credentials (admin/admin)
- Some existing data (spiders, tasks) for meaningful statistics

## Test Execution Steps

### Setup
1. Authenticate and get token

### Statistics
2. Get system overview statistics
3. Verify overview contains expected fields (total spiders, tasks, etc.)
4. Get daily statistics
5. Verify daily stats structure
6. Get task statistics
7. Verify task stats structure
8. Test stats with date range parameters (if supported)

### Filters
9. Get filter options for 'spiders' collection
10. Verify filter options structure
11. Get filter options for 'tasks' collection
12. Verify task filter options
13. Get filter options with value filter
14. Get filter options with value and label
15. Test filter with query parameter
16. Test filter for non-existent collection

### Edge Cases
17. Test stats endpoints without authentication
18. Test filter with invalid collection name
19. Test filter endpoints with special characters

### Cleanup
20. Logout

## Success Criteria

- Authentication successful
- Overview statistics returned with system counts
- Daily statistics show time-series data
- Task statistics show execution metrics
- Filter endpoints return field options for collections
- Filters support value and label parameters
- Filters support query parameters for filtering
- Invalid collection names handled appropriately
- All endpoints respond with correct structure

## Expected Results

- Stats overview includes: total spiders, tasks, nodes, etc.
- Daily stats may include time-series arrays
- Task stats include success/failure counts, duration metrics
- Filter options include available values for UI dropdowns
- Filters support dynamic field discovery
- Invalid parameters return 400/404 errors
- Stats may return empty/zero values if no data exists

## Notes

- Statistics depend on existing system data
- Empty system may return zero values for counts
- Filter options are dynamic based on actual data
- Test focuses on API structure rather than data accuracy
- Some stats may require time-range parameters
