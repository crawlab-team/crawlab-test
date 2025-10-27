# DB-001 - Database Integration Comprehensive Testing

## Metadata
- **Category**: database
- **Priority**: high
- **Complexity**: complex
- **Duration**: 30-45 minutes
- **Environment**: local/staging
- **Dependencies**: MongoDB, MySQL, PostgreSQL, Elasticsearch, Crawlab backend

## Scenario
This test validates the comprehensive database integration functionality in Crawlab, ensuring that all primary supported database types (MongoDB, MySQL, PostgreSQL, Elasticsearch) can be connected, managed, and operated through Crawlab's database service layer. This includes connection management, metadata retrieval, schema operations (DDL), data operations (CRUD), and query execution. This is critical for ensuring data collection workflows work correctly across different database backends.

**Note**: MSSQL Server is not included in integration tests as it is not a primary supported database.

## Prerequisites
- Python 3.9+, Docker, and Docker Compose
- Crawlab backend running at http://localhost:8080 (or configured API endpoint)
- Test databases (start with `docker-compose -f docker-compose.test.yml up -d`):
  - MongoDB: localhost:27017 (username: admin, password: admin)
  - MySQL: localhost:3307 (username: root, password: admin)  
  - PostgreSQL: localhost:5433 (username: admin, password: admin)
  - Elasticsearch: localhost:9200

**Override defaults** via environment variables if needed:
```bash
export MYSQL_TEST_HOST=custom.host      # Default: localhost
export MYSQL_TEST_PORT=3308             # Default: 3307
export POSTGRES_TEST_HOST=custom.host   # Default: localhost
export POSTGRES_TEST_PORT=5434          # Default: 5433
export MONGO_TEST_HOST=custom.host      # Default: localhost
export MONGO_TEST_PORT=27018            # Default: 27017
export ELASTICSEARCH_TEST_HOST=custom.host  # Default: localhost
export ELASTICSEARCH_TEST_PORT=9201     # Default: 9200
```

**Quick Start**:
```bash
# Start test databases
docker-compose -f docker-compose.test.yml up -d

# Run the test
cd crawlab-test
uv run ./cli.py --spec DB-001
```

## Test Steps

### Step 1: Setup Test Environment
**Method**: automated
**Expected**: Test environment initializes successfully, all database containers are running
**Validation**: 
- All database services are accessible
- Test framework initialization succeeds
- No connection errors in logs

**Notes**: 
- In CI/CD: Handled automatically by test action scripts
- Locally: Use integration test helper to check and start services
- Runner script manages service health checks and initialization

### Step 2: Test Connection Management
**Method**: automated (Python runner via API)
**Expected**: All database types can establish connections successfully
**Validation**:
- MongoDB connection succeeds with authentication
- MySQL connection succeeds and returns connection ID
- PostgreSQL connection succeeds with proper SSL/TLS handling
- Elasticsearch connection succeeds
- Connection status updated to "online" in database registry
- Failed connections properly set status to "offline" with error details

**Implementation**:
- Create database connections via `/databases` API endpoint
- Test each connection using `/databases/{id}/connection/test` endpoint
- Verify connection status in response

### Step 3: Test Metadata Retrieval
**Method**: automated (Python runner via API)
**Expected**: Metadata correctly retrieved for all database types
**Validation**:
- Database lists returned correctly
- Table/collection lists complete and accurate
- Column/field metadata includes:
  - Name, type, constraints (NOT NULL, PRIMARY KEY, etc.)
  - Default values where applicable
  - Auto-increment settings for supported databases
- Index metadata includes:
  - Index name, columns, uniqueness
  - Index type (B-tree, hash, etc.)
- MongoDB: Collection schema inference works correctly
- Elasticsearch: Index mappings retrieved properly

**Implementation**:
- Use `/databases/{id}/metadata` API endpoint for full metadata
- Use `/databases/{id}/tables/metadata/get` for specific table details
- Verify metadata structure and completeness

### Step 4: Test Database Operations (DDL)
**Method**: automated (Python runner via API)
**Expected**: Database creation and deletion work correctly
**Validation**:
- Database creation via API succeeds
- Database appears in metadata after creation
- Database deletion removes connection completely
- MongoDB: Database created automatically on first write

**Implementation**:
- Use `/databases` POST endpoint to create database connections
- Use `/databases/{id}` DELETE endpoint to remove connections
- Verify using `/databases` GET endpoint

**Note**: This step tests database _connection_ management in Crawlab, not database creation on the actual database server (which is handled at the database level)

### Step 5: Test Table/Collection Operations
**Method**: automated (Python runner via API)
**Expected**: Table/collection management operations succeed
**Validation**:
- CreateTable creates table with correct schema:
  - All columns defined with proper types
  - Primary keys configured correctly
  - Constraints applied (NOT NULL, AUTO_INCREMENT)
  - Indexes created as specified
- DropTable removes table completely
- Table appears/disappears in metadata correctly
- MongoDB: Collection creation implicit
- Elasticsearch: Index creation with mappings

**Implementation**:
- Use `/databases/{id}/tables/create` POST endpoint to create tables
- Use `/databases/{id}/tables/drop` POST endpoint to drop tables
- Use `/databases/{id}/tables/metadata/get` POST endpoint to verify table structure
- Test on MySQL and PostgreSQL (primary SQL databases)

### Step 6: Test Schema Modification
**Method**: automated (Python runner via API)
**Expected**: Schema changes applied correctly without data loss
**Validation**:
- Add new columns:
  - Column appears in metadata
  - Existing data preserved
  - Default values applied if specified
- Add/modify indexes:
  - Index created and appears in metadata
  - Unique constraints enforced

**Implementation**:
- Use `/databases/{id}/tables/modify` POST endpoint for schema changes
- Pass column and index modifications in request body
- Verify changes using metadata endpoint

**Note**: Complex schema modifications (column type changes, removing columns) may have limited support depending on database type. Test focuses on common operations: adding columns and managing indexes.

### Step 7: Test Data Operations (CRUD)
**Method**: automated (Python runner via API)
**Expected**: All CRUD operations work correctly with data integrity
**Validation**:
- CreateRow (INSERT):
  - Single row insertion succeeds
  - Auto-increment values generated correctly
  - Constraints enforced (NOT NULL, UNIQUE)
  - Default values applied
- ReadRows (SELECT):
  - All rows returned with correct data
  - Filtering works (WHERE clause equivalent)
  - Pagination works (page/size parameters)
  - Row count accurate
  - Data types preserved
- UpdateRow (UPDATE):
  - Specified rows updated correctly
  - Other rows unchanged
  - Update filter works properly
  - Updated values persist
- DeleteRow (DELETE):
  - Specified rows deleted
  - Other rows preserved
  - Delete filter works correctly

**Implementation**:
- Use `/databases/{id}/tables/data` POST endpoint with action="insert" for INSERT
- Use `/databases/{id}/tables/data` POST endpoint with action="update" for UPDATE
- Use `/databases/{id}/tables/data` POST endpoint with action="delete" for DELETE
- Use `/databases/{id}/tables/data/get` POST endpoint for SELECT
- Test on MySQL and PostgreSQL with test tables

### Step 8: Test Query Execution
**Method**: automated (Python runner via API)
**Expected**: Custom queries execute correctly and return proper results
**Validation**:
- SQL queries (MySQL, PostgreSQL):
  - SELECT statements return correct data
  - Version queries work (basic validation)
- MongoDB queries:
  - Find operations with filters (if implemented)
- Elasticsearch queries:
  - Query DSL execution (if implemented)
- Query results include:
  - Column names and types
  - Row data properly formatted
  - Error messages for failed queries

**Implementation**:
- Use `/databases/{id}/query` POST endpoint
- Pass database name and query string in request body
- Test with simple queries (e.g., SELECT VERSION())
- Verify response contains result data

### Step 9: Test Metrics Collection
**Method**: automated (Python runner via API)
**Expected**: Database metrics collected accurately for monitoring
**Validation**:
- Memory metrics (if available):
  - Total memory reported
  - Available memory tracked
- Disk metrics (if available):
  - Total disk space
  - Available disk space
- Connection metrics (if available):
  - Active connections counted
- Performance metrics (if available):
  - Queries per second (QPS)
  - Cache hit ratio
- Metrics API responds without errors

**Implementation**:
- Use `/databases/{id}/metrics/current` GET endpoint
- Verify response structure
- Log metric values for verification

**Note**: Metric availability varies by database type. Some databases may not provide all metrics through the API.

### Step 10: Test Error Handling and Edge Cases
**Method**: automated (Python runner via API)
**Expected**: Graceful error handling without crashes
**Validation**:
- Invalid connection credentials fail gracefully
- Connection timeouts handled properly
- Invalid SQL/query syntax errors reported clearly
- Constraint violations reported with details
- API returns proper error responses (4xx/5xx status codes)
- Error messages are descriptive

**Implementation**:
- Test with invalid credentials (negative test)
- Test with malformed SQL queries
- Test constraint violations (duplicate keys, NOT NULL violations)
- Verify API error responses contain useful error messages

## Success Criteria
- [ ] All database types establish connections successfully via API
- [ ] Metadata retrieval works for all database types with complete information
- [ ] Database connection management (create/delete) works correctly
- [ ] Table/collection create/drop operations work correctly
- [ ] Schema modifications (add columns, manage indexes) applied successfully
- [ ] All CRUD operations (Create, Read, Update, Delete) work with data integrity
- [ ] Custom queries execute and return correct results
- [ ] Database metrics API responds without errors
- [ ] Auto-increment values generated correctly for MySQL, PostgreSQL
- [ ] Unique constraints and indexes enforced properly
- [ ] Error handling graceful with clear error messages
- [ ] All Python test cases pass successfully
- [ ] Test cleanup removes all created resources

## Failure Scenarios

### Scenario 1: Database Connection Failure
**Symptoms**: 
- Tests skip with message: "Skipping test - MySQLService service not available at localhost:3307"
- All tests for a specific database type are skipped
- No connection errors logged (graceful skip)

**Previous Behavior** (before fix):
- Tests would fail with "Connection refused" errors
- Exit code 1 even when services intentionally not running

**Current Behavior** (after fix):
- Tests detect service availability before running
- Tests skip gracefully when services unavailable
- Only fails if service is available but test logic fails

**Action**: 
- If tests should run: Start database services using docker-compose
  ```bash
  cd tests
  docker-compose -f docker-compose.test.yml up -d
  ```
- Verify services are healthy: `docker-compose -f docker-compose.test.yml ps`
- Check connectivity: `telnet localhost <port>`
- Review database logs if services fail health checks
- See [Database Tests Setup Guide](../../README-DATABASE-TESTS.md) for detailed troubleshooting

### Scenario 2: Duplicate Key Errors in MongoDB
**Symptoms**:
- Tests fail with: "E11000 duplicate key error collection: crawlab_test.databases index: _id_ dup key"
- Multiple tests fail with same error pattern
- Error occurs during test setup

**Previous Behavior** (before fix):
- Tests reused database record IDs from previous runs
- Failed/interrupted tests left orphaned records
- Manual cleanup required between test runs

**Current Behavior** (after fix):
- Each test generates unique ObjectID for database records
- `t.Cleanup()` ensures cleanup runs even on panic
- Automatic cleanup prevents duplicate key errors

**Action**: 
- **Should not occur** with current code
- If it does occur (rare edge case):
  ```bash
  # Restart containers with fresh volumes
  docker-compose -f docker-compose.test.yml down -v
  docker-compose -f docker-compose.test.yml up -d
  ```
- Report as a bug if persistent

### Scenario 3: Metadata Retrieval Returns Empty or Incomplete Data
**Symptoms**:
- GetMetadata returns empty list or missing tables
- Column definitions incomplete or incorrect
- Index information missing

**Action**:
- Verify database has tables/collections
- Check permissions for metadata queries
- Review query execution logs for errors
- Validate data source-specific metadata queries
- Check for schema cache issues

### Scenario 4: Schema Operations Fail
**Symptoms**:
- CreateTable fails with error
- ModifyTable doesn't apply changes
- Metadata doesn't reflect schema changes

**Action**:
- Check for locked tables (other connections)
- Verify sufficient permissions for DDL operations
- Review database-specific syntax for DDL
- Check for constraint conflicts
- Validate data type compatibility

### Scenario 5: CRUD Operations Return Wrong Data
**Symptoms**:
- CreateRow succeeds but data not found
- ReadRows returns incorrect data or count
- UpdateRow doesn't change data
- DeleteRow doesn't remove data

**Action**:
- Verify transaction commit behavior
- Check for caching issues
- Validate filter/query syntax
- Review data type conversion logic
- Check for timezone/encoding issues

### Scenario 6: Query Execution Times Out or Fails
**Symptoms**:
- Query hangs indefinitely
- Timeout errors in logs
- Incorrect query results

**Action**:
- Set appropriate query timeout values
- Check for missing indexes on filtered columns
- Validate query syntax for specific database
- Review query execution plans
- Check for table locks or deadlocks

### Scenario 7: Metrics Collection Shows Zero or Invalid Values
**Symptoms**:
- All metrics return 0
- Memory/disk percentages > 100%
- Negative values in metrics

**Action**:
- Verify metric collection queries work
- Check permissions for system tables/views
- Validate metric calculation logic
- Review database-specific metric sources
- Check for unit conversion errors (KB vs MB vs GB)

## Execution

### Automated (CI/CD)
Tests run automatically when:
- Database code changes are detected (`core/database/**`)
- Database test files are modified (`crawlab-test/specs/database/**`, `crawlab-test/runners/database/**`)
- Manually triggered with test mode "all"

The CI/CD pipeline:
1. Builds Docker image with latest code
2. Starts Crawlab services (master, worker, MongoDB)
3. Starts database integration services (MySQL, PostgreSQL, Elasticsearch, MongoDB)
4. Waits for all services to be healthy
5. Runs database integration test via Python runner
6. Collects results and logs
7. Generates summary report

### Automated (Local Development)
Use the test CLI:

```bash
# Run the database integration test
cd crawlab-test
uv run ./cli.py --spec DB-001

# Or with explicit backend
uv run ./cli.py --spec DB-001 --backend script

# With verbose output
uv run ./cli.py --spec DB-001 -v

# Check database services first
cd helpers/database
./database-test-helper.py check-services
```

### Direct Python Runner Execution
For development and debugging:

```bash
# Navigate to test directory
cd crawlab-test

# Run the runner directly
python runners/database/DB_001_database_integration_comprehensive_testing.py

# Or with environment variables for custom database configuration
MYSQL_TEST_PORT=3308 python runners/database/DB_001_database_integration_comprehensive_testing.py
```

### Docker Setup
Start required database services:

```bash
# Using docker-compose
cd crawlab-test
docker-compose -f docker-compose.test.yml up -d

# Check services are running
docker-compose -f docker-compose.test.yml ps

# View logs
docker-compose -f docker-compose.test.yml logs -f mysql

# Stop services
docker-compose -f docker-compose.test.yml down -v
```

### Manual Verification
For specific scenarios that require manual inspection:

1. **Connection Testing**:
   - Open Crawlab UI → Database Management
   - Add new database connections for each type
   - Click "Test Connection" button
   - Verify status shows "online" with green indicator

2. **Metadata Browsing**:
   - Navigate to database details page
   - Expand database → table structure
   - Verify all columns, types, and indexes visible
   - Check metadata refresh updates correctly

3. **Data Operations**:
   - Use built-in data browser
   - Insert new rows via UI
   - Edit existing rows
   - Delete rows and verify removal
   - Run custom queries in query console

4. **Monitoring**:
   - Open database metrics dashboard
   - Verify real-time metrics updating
   - Check historical metric trends
   - Validate alert thresholds

## Cleanup

**Note**: Tests include automatic cleanup that runs even if tests fail. Manual cleanup is only needed for container management.

```bash
# Stop test execution if running
# Use Ctrl+C or kill the process

# Automatic cleanup (handled by test runner):
# - Test database connections automatically deleted via API
# - Test tables and data automatically dropped
# - Resources tracked and cleaned up in finally block

# Stop and remove database containers
cd crawlab-test
docker-compose -f docker-compose.test.yml down -v

# Clear test results (optional)
rm -f results/*
```

## Notes

### Database-Specific Considerations

**MongoDB**:
- No explicit database creation needed (auto-created on first write)
- Collections are schema-less (schema inference from data)
- Index creation is asynchronous
- Replica set configuration affects connection strings

**MySQL**:
- Requires explicit database creation
- Auto-increment starts at 1 by default
- Index names must be unique per table
- Storage engine affects feature availability (InnoDB vs MyISAM)

**PostgreSQL**:
- Requires explicit database creation
- Serial/identity columns for auto-increment
- Schema (namespace) support
- Advanced features: JSONB, full-text search, CTEs

**Elasticsearch**:
- No traditional database concept (indices instead)
- Schema defined via mappings
- Document-oriented (JSON)
- Full-text search and aggregations built-in

### Test Data Patterns
- Use consistent naming: `test_*` for databases, `test_table` for tables
- Include variety of data types in test schemas
- Test edge cases: NULL, empty strings, special characters
- Use realistic data volumes for performance tests

### Performance Considerations
- Tests may take 10-20 minutes for complete run (API-based tests are faster than Go tests)
- Tests run sequentially to avoid database locking issues
- Connection testing includes brief delays for initialization
- CRUD operations use small test tables for speed

### CI/CD Integration
- Tests designed to run in GitHub Actions
- Docker containers used for database dependencies
- Python-based runner for cross-platform compatibility
- Test results logged and can be exported to various formats

## History
- **Created**: 2025-10-05, GitHub Copilot
- **Modified**: 2025-10-27, GitHub Copilot - Migrated from Go test wrapper to Python API runner
- **Last Run**: -
