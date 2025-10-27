# API-010: Database Connection & Queries

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Duration**: 5 minutes  
**Backend**: script  
**Test Runner**: `runners/api/API_010_database_connection_queries.py`

## Test Objective

Validate Crawlab's database connection management and query execution functionality through API endpoints. This test covers:
- Database connection CRUD operations
- Connection testing and validation
- Query execution
- Error handling for invalid configurations
- Pagination and filtering

## Prerequisites

1. Crawlab instance running (master node)
2. API accessible at http://localhost:8080
3. Valid authentication credentials (admin/admin)
4. Clean test environment (no existing test databases)

## API Endpoints Tested

- `POST /api/databases` - Create database connection
- `GET /api/databases` - List database connections
- `GET /api/databases/{id}` - Get database details
- `PUT /api/databases/{id}` - Update database configuration
- `DELETE /api/databases/{id}` - Delete database connection
- `POST /api/databases/{id}/connection/test` - Test connection
- `POST /api/databases/{id}/query` - Execute query
- `GET /api/databases/{id}/columns/types` - Get supported column types
- `PATCH /api/databases` - Batch update databases

## Test Scenarios

### 1. Authentication Setup
**Action**: Authenticate as admin user  
**Expected**: Valid JWT token received

### 2. Database CRUD - Create
**Action**: Create MongoDB database connection (config only, no actual connection required)
```json
{
  "data": {
    "name": "test-mongo-db",
    "data_source": "mongo",
    "host": "localhost",
    "port": 27017,
    "database": "crawlab_test",
    "description": "Test MongoDB database"
  }
}
```
**Expected**:
- Status: 200
- Response contains database ID, name, data_source
- Database created successfully

### 3. Database CRUD - List
**Action**: List all databases with pagination
**Expected**:
- Status: 200
- Response contains data array and total count
- Created database appears in list

### 4. Database CRUD - Get Details
**Action**: Get specific database by ID
**Expected**:
- Status: 200
- Response contains full database configuration
- Matches created database

### 5. Database CRUD - Update
**Action**: Update database description
```json
{
  "data": {
    "description": "Updated description"
  }
}
```
**Expected**:
- Status: 200
- Description updated successfully

### 6. Connection Testing
**Action**: Test database connection
**Expected**:
- Status: 200 or 500 (depending on actual DB availability)
- Response indicates connection status
- Note: May fail if SQLite file doesn't exist (expected)

### 7. Get Column Types
**Action**: Get supported column types for the database
**Expected**:
- Status: 200
- Response contains array of column types (may be empty for some DB types)
- Endpoint accessible

### 8. Query Execution (Optional)
**Action**: Execute simple query (if connection works)
```json
{
  "query": "SELECT 1 as test"
}
```
**Expected**:
- If DB exists: Query results returned
- If DB doesn't exist: Error response (acceptable)
- Note: This is exploratory - may not work with test DB

### 9. Create MySQL Connection (Config Only)
**Action**: Create MySQL connection (won't connect, just config)
```json
{
  "data": {
    "name": "test-mysql-db",
    "data_source": "mysql",
    "host": "localhost",
    "port": 3306,
    "username": "testuser",
    "password": "testpass",
    "database": "testdb",
    "description": "Test MySQL database"
  }
}
```
**Expected**:
- Status: 200
- MySQL connection created
- Configuration stored

### 10. Test MySQL Connection (Expected Failure)
**Action**: Test MySQL connection
**Expected**:
- Status: 500 or error response
- Connection fails (no actual MySQL server)
- Error message indicates connection problem

### 11. Pagination & Filtering
**Action**: List databases with page size = 1
**Expected**:
- Status: 200
- Only 1 database in response
- Total count reflects all databases
- Pagination working correctly

### 12. Batch Update
**Action**: Update multiple databases' descriptions at once
```json
{
  "update": {
    "description": "Batch updated"
  },
  "ids": ["<db1_id>", "<db2_id>"]
}
```
**Expected**:
- Status: 200
- Both databases updated
- Descriptions changed to "Batch updated"

### 13. Invalid Connection - Missing Required Fields
**Action**: Attempt to create database without required fields
```json
{
  "data": {
    "name": "invalid-db"
  }
}
```
**Expected**:
- Status: 400 or 500
- Error response indicating missing fields

### 14. Invalid Database ID
**Action**: Get database with non-existent ID
**Expected**:
- Status: 500 or 404
- Error response

### 15. Database CRUD - Delete
**Action**: Delete both test databases
**Expected**:
- Status: 200
- Databases deleted successfully

### 16. Verify Deletion
**Action**: List databases again
**Expected**:
- Test databases no longer in list
- Cleanup successful

## Test Data Cleanup

**Cleanup Steps**:
1. Delete all test databases created during test
2. Verify no residual test data remains

**Resources to Clean**:
- Databases: `test-mongo-db`, `test-mysql-db`

## Success Criteria

- All database CRUD operations work correctly
- Connection testing endpoint accessible (result may vary)
- Query execution endpoint accessible (result may vary)
- Proper error handling for invalid configurations
- Pagination and filtering work as expected
- Batch operations function correctly
- Test data cleaned up after execution

## Notes

- This test focuses on API functionality, not actual database connectivity
- Connection tests may fail (expected if no real DB), but endpoints should respond
- Query execution may not work without real database (acceptable)
- MongoDB is used for testing (commonly available in Crawlab deployments)
- Test validates API contract, not database drivers
