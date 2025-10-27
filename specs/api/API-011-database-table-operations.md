# API-011: Database Table Operations

**Category**: API Testing  
**Priority**: P2 (High-Value Features)  
**Estimated Duration**: 5 minutes  
**Backend**: script  
**Test Runner**: `runners/api/API_011_database_table_operations.py`

## Test Objective

Validate Crawlab's database table management functionality through API endpoints. This test covers:
- Table metadata retrieval (listing all tables, getting table details)
- Table CRUD operations (create, modify, rename, drop)
- Table data operations (read, insert, update, delete)
- Error handling for invalid operations
- Pagination for table data

## Prerequisites

1. Crawlab instance running (master node)
2. API accessible at http://localhost:8080
3. Valid authentication credentials (admin/admin)
4. Access to a working database connection (MongoDB or MySQL)

## API Endpoints Tested

- `GET /api/databases/{id}/metadata` - Get all database metadata (tables list)
- `GET /api/databases/{id}/tables/metadata` - Get specific table metadata
- `POST /api/databases/{id}/tables/metadata/get` - Get table metadata (POST version)
- `POST /api/databases/{id}/tables/create` - Create table
- `POST /api/databases/{id}/tables/modify` - Modify table structure
- `POST /api/databases/{id}/tables/rename` - Rename table
- `POST /api/databases/{id}/tables/drop` - Drop table
- `POST /api/databases/{id}/tables/data/get` - Get table data (with pagination)
- `POST /api/databases/{id}/tables/data` - Insert/update/delete table data

## Test Scenarios

### 1. Authentication Setup
**Action**: Authenticate as admin user  
**Expected**: Valid JWT token received

### 2. Create Test Database
**Action**: Create a MongoDB database connection for testing
```json
{
  "data": {
    "name": "test-table-ops-db",
    "data_source": "mongo",
    "host": "localhost",
    "port": 27017,
    "database": "test_tables_db",
    "description": "Test database for table operations"
  }
}
```
**Expected**:
- Status: 200
- Database created successfully

### 3. Get Database Metadata (All Tables)
**Action**: Get metadata for entire database (lists all tables/collections)
**Expected**:
- Status: 200
- Response contains metadata structure
- May be empty initially or contain existing collections

### 4. Create Table
**Action**: Create a new table/collection
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "columns": [
    {"name": "id", "type": "int", "primary": true},
    {"name": "username", "type": "string"},
    {"name": "email", "type": "string"}
  ]
}
```
**Expected**:
- Status: 200 (or acceptable error for schema-less DBs like MongoDB)
- Note: MongoDB doesn't require schema, so this might not be applicable
- Endpoint should respond (even if operation isn't supported)

### 5. Get Table Metadata (Specific Table)
**Action**: Get metadata for the created table
**Expected**:
- Status: 200
- Response contains table schema information
- Shows columns/fields if applicable

### 6. Insert Data into Table
**Action**: Insert test data
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "action": "insert",
  "data": {
    "username": "testuser1",
    "email": "test1@example.com"
  }
}
```
**Expected**:
- Status: 200
- Data inserted successfully

### 7. Insert More Data
**Action**: Insert second record
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "action": "insert",
  "data": {
    "username": "testuser2",
    "email": "test2@example.com"
  }
}
```
**Expected**:
- Status: 200
- Second record inserted

### 8. Get Table Data
**Action**: Retrieve table data with pagination
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "page": 1,
  "size": 10
}
```
**Expected**:
- Status: 200
- Response contains inserted records
- Data includes both test users

### 9. Get Table Data with Pagination
**Action**: Get data with smaller page size
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "page": 1,
  "size": 1
}
```
**Expected**:
- Status: 200
- Only 1 record returned
- Pagination working

### 10. Update Table Data
**Action**: Update a record
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "action": "update",
  "data": {
    "email": "updated@example.com"
  },
  "conditions": {
    "username": "testuser1"
  }
}
```
**Expected**:
- Status: 200
- Record updated successfully

### 11. Verify Update
**Action**: Retrieve data again to verify update
**Expected**:
- Status: 200
- Email for testuser1 is "updated@example.com"

### 12. Delete Table Data
**Action**: Delete a record
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "action": "delete",
  "conditions": {
    "username": "testuser2"
  }
}
```
**Expected**:
- Status: 200
- Record deleted successfully

### 13. Verify Deletion
**Action**: Retrieve data to confirm deletion
**Expected**:
- Status: 200
- Only testuser1 remains
- testuser2 is gone

### 14. Rename Table (Optional)
**Action**: Rename the table
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "new_table": "users_renamed"
}
```
**Expected**:
- Status: 200 (or error if not supported)
- If supported, table renamed
- MongoDB may not support this operation

### 15. Modify Table (Optional)
**Action**: Modify table structure
```json
{
  "database": "test_tables_db",
  "table": "test_users",
  "columns": [
    {"name": "age", "type": "int", "action": "add"}
  ]
}
```
**Expected**:
- Status: 200 (or error if not supported for schema-less DBs)
- Endpoint responds appropriately

### 16. Drop Table
**Action**: Drop the test table
```json
{
  "database": "test_tables_db",
  "table": "test_users"
}
```
**Expected**:
- Status: 200
- Table dropped successfully

### 17. Verify Table Dropped
**Action**: Try to get table metadata
**Expected**:
- Status: 404 or 500
- Table no longer exists

### 18. Invalid Table Operations
**Action**: Test error handling (get data from non-existent table)
```json
{
  "database": "test_tables_db",
  "table": "nonexistent_table",
  "page": 1,
  "size": 10
}
```
**Expected**:
- Status: 500 or error response
- Proper error message

### 19. Delete Test Database
**Action**: Delete the test database connection
**Expected**:
- Status: 200
- Database deleted successfully

### 20. Cleanup Verification
**Action**: Verify test database is removed
**Expected**:
- Database no longer in list
- Test cleanup successful

## Test Data Cleanup

**Cleanup Steps**:
1. Drop all test tables created during test
2. Delete test database connection
3. Verify no residual test data remains

**Resources to Clean**:
- Database: `test-table-ops-db`
- Tables/Collections: `test_users`, `users_renamed` (if created)

## Success Criteria

- Database metadata retrieval works correctly
- Table creation endpoint accessible (may not apply to schema-less DBs)
- Table data CRUD operations work correctly (insert, read, update, delete)
- Pagination works for table data retrieval
- Table modification/rename endpoints accessible (may not be supported)
- Table drop operation works correctly
- Proper error handling for invalid operations
- Test data cleaned up after execution

## Notes

- This test focuses on MongoDB which is schema-less
- Some operations (create table with schema, modify, rename) may not be applicable to MongoDB
- Test validates API endpoints are accessible and respond appropriately
- For MongoDB, collections are created automatically on first insert
- Error responses are acceptable for schema operations on schema-less databases
- Test emphasizes data operations (CRUD) which work across all DB types
