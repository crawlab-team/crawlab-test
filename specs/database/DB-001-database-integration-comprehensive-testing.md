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
- Go 1.23+, Docker, and Docker Compose
- Test databases (start with `docker-compose -f docker-compose.test.yml up -d`):
  - MongoDB: localhost:27017 (username: admin, password: admin)
  - MySQL: localhost:3307 (username: root, password: admin)  
  - PostgreSQL: localhost:5433 (username: admin, password: admin)
  - Elasticsearch: localhost:9200

**Override defaults** via environment variables if needed:
```bash
export MONGO_TEST_PORT=27018  # or any custom port
export MYSQL_TEST_HOST=custom.host  # or any custom host
# See core/database/service_test.go for all available variables
```

**Quick Start**:
```bash
cd tests && docker-compose -f docker-compose.test.yml up -d
cd ../core/database && go test -v -timeout 30m
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
**Method**: automated (Go test suite)
**Test Function**: `TestService_TestConnection`
**Expected**: All database types can establish connections successfully
**Validation**:
- MongoDB connection succeeds with authentication
- MySQL connection succeeds and returns connection ID
- PostgreSQL connection succeeds with proper SSL/TLS handling
- Elasticsearch connection succeeds for both nodes (9200/9201)
- Connection status updated to "online" in database registry
- Failed connections properly set status to "offline" with error details

**Coverage**:
- Test successful connections with valid credentials
- Test failed connections with invalid credentials
- Test connection timeout handling
- Test connection pooling behavior

### Step 3: Test Metadata Retrieval
**Method**: automated (Go test suite)
**Test Functions**: `TestService_GetMetadata`, `TestService_GetMetadataAllDb`
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

**Coverage**:
- GetMetadata (single database)
- GetMetadataAllDb (all databases on server)
- GetTableMetadata (specific table details)
- Empty database handling
- Large schema handling (many tables/columns)

### Step 4: Test Database Operations (DDL)
**Method**: automated (Go test suite)
**Test Functions**: `TestService_CreateDatabase`, `TestService_DropDatabase`
**Expected**: Database creation and deletion work correctly
**Validation**:
- CreateDatabase creates new database successfully
- Database appears in metadata after creation
- DropDatabase removes database completely
- Database disappears from metadata after deletion
- MongoDB: Database created automatically on first write

**Coverage**:
- Create database with standard name
- Create database with special characters (if supported)
- Drop empty database
- Drop database with tables (cascade delete)
- Attempt to create duplicate database (error handling)
- Attempt to drop non-existent database (error handling)

### Step 5: Test Table/Collection Operations
**Method**: automated (Go test suite)
**Test Functions**: `TestService_CreateTable`, `TestService_DropTable`
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

**Coverage**:
- Create table with various column types
- Create table with composite primary key
- Create table with multiple indexes (unique and non-unique)
- Drop table with data
- Drop table with foreign key references (if supported)

### Step 6: Test Schema Modification
**Method**: automated (Go test suite)
**Test Functions**: `TestService_ModifyTableColumns`, `TestService_ModifyTableIndexes`
**Expected**: Schema changes applied correctly without data loss
**Validation**:
- Add new columns:
  - Column appears in metadata
  - Existing data preserved
  - Default values applied if specified
- Remove columns:
  - Column removed from metadata
  - Remaining data intact
  - No orphaned data structures
- Modify column types:
  - Type changed correctly
  - Data converted if possible
  - Constraints updated
- Add indexes:
  - Index created and appears in metadata
  - Query performance improved
  - Unique constraints enforced
- Remove indexes:
  - Index deleted completely
  - Queries still work (slower)
- Modify indexes:
  - Index updated with new definition
  - Data integrity maintained

**Coverage**:
- MySQL: ALTER TABLE operations
- PostgreSQL: ALTER TABLE with USING clause
- Elasticsearch: Update index mappings (reindex if needed)

### Step 7: Test Data Operations (CRUD)
**Method**: automated (Go test suite)
**Test Functions**: `TestService_CreateRow`, `TestService_ReadRows`, `TestService_UpdateRow`, `TestService_DeleteRow`
**Expected**: All CRUD operations work correctly with data integrity
**Validation**:
- CreateRow (INSERT):
  - Single row insertion succeeds
  - Auto-increment values generated correctly
  - Constraints enforced (NOT NULL, UNIQUE)
  - Default values applied
  - Timestamps auto-populated
- ReadRows (SELECT):
  - All rows returned with correct data
  - Filtering works (WHERE clause equivalent)
  - Pagination works (SKIP/LIMIT)
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
  - Row count decreased

**Coverage**:
- Basic CRUD on all supported data types
- NULL value handling
- Empty string vs NULL distinction
- Large text/blob data
- Special characters and Unicode
- Concurrent operations (if applicable)

### Step 8: Test Query Execution
**Method**: automated (Go test suite)
**Test Function**: `TestService_Query`
**Expected**: Custom queries execute correctly and return proper results
**Validation**:
- SQL queries (MySQL, PostgreSQL):
  - SELECT statements return correct data
  - JOIN operations work
  - Aggregate functions (COUNT, SUM, AVG)
  - ORDER BY and GROUP BY
  - Subqueries and CTEs (Common Table Expressions)
- MongoDB queries:
  - Find operations with filters
  - Aggregation pipeline
  - Projection and sorting
- Elasticsearch queries:
  - Query DSL execution
  - Full-text search
  - Aggregations
- Query results include:
  - Column names and types
  - Row data properly formatted
  - Execution time/metrics
  - Error messages for failed queries

**Coverage**:
- Simple SELECT queries
- Complex multi-table JOINs
- Queries with parameters/bindings
- Queries returning large result sets
- Queries with syntax errors (error handling)
- Queries with timeouts

### Step 9: Test Metrics Collection
**Method**: automated (Go test suite)
**Test Function**: `TestService_GetCurrentMetric`
**Expected**: Database metrics collected accurately for monitoring
**Validation**:
- Memory metrics:
  - Total memory reported
  - Available memory tracked
  - Used memory percentage calculated
- Disk metrics:
  - Total disk space
  - Available disk space
  - Used disk percentage
- Connection metrics:
  - Active connections counted
  - Connection pool status
- Performance metrics:
  - Queries per second (QPS)
  - Cache hit ratio
  - Replication lag (if applicable)
  - Lock wait time
- All metrics > 0 and reasonable values
- Metrics updated in real-time

**Coverage**:
- MongoDB: serverStatus metrics
- MySQL: SHOW STATUS metrics
- PostgreSQL: pg_stat_database metrics
- Elasticsearch: cluster stats

### Step 10: Test Error Handling and Edge Cases
**Method**: automated (Go test suite + manual validation)
**Expected**: Graceful error handling without crashes
**Validation**:
- Invalid connection credentials fail gracefully
- Connection timeouts handled properly
- Network disconnection during operation
- Insufficient permissions errors caught
- Invalid SQL/query syntax errors reported clearly
- Constraint violations reported with details
- Concurrent access conflicts resolved
- Transaction rollback on errors (if applicable)
- Resource cleanup on failures

**Coverage**:
- Connection errors (invalid host, port, credentials)
- Schema errors (duplicate table, missing column)
- Data errors (constraint violations, type mismatches)
- Query errors (syntax errors, invalid references)
- Resource errors (disk full, memory exhausted)

## Success Criteria
- [ ] All database types establish connections successfully (TestConnection passes)
- [ ] Metadata retrieval works for all database types with complete information
- [ ] Database create/drop operations succeed without errors
- [ ] Table/collection create/drop operations work correctly
- [ ] Schema modifications (columns and indexes) applied successfully
- [ ] All CRUD operations (Create, Read, Update, Delete) work with data integrity
- [ ] Custom queries execute and return correct results
- [ ] Database metrics collected and reported accurately
- [ ] Auto-increment values generated correctly for MySQL, PostgreSQL
- [ ] Unique constraints and indexes enforced properly
- [ ] Error handling graceful with clear error messages
- [ ] No memory leaks or resource exhaustion during tests
- [ ] Connection pooling works efficiently
- [ ] Transaction support works where applicable
- [ ] All Go tests pass with 100% of test cases succeeding

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
- Integration test files are modified (`tests/specs/integration/**`, `tests/helpers/integration/**`)
- Manually triggered with test mode "all"

The CI/CD pipeline:
1. Builds Docker image with latest code
2. Starts Crawlab services (master, worker, MongoDB)
3. Starts database integration services (MySQL, PostgreSQL, Elasticsearch)
4. Waits for all services to be healthy
5. Runs integration test suite via runner scripts
6. Collects results, logs, and coverage
7. Generates summary report

### Automated (Local Development)
Use the integration test helper and runner scripts:

```bash
# Using the test helper (recommended)
cd tests
./helpers/integration/database-test-helper.py check-services  # Check service status
./helpers/integration/database-test-helper.py run-tests        # Run all tests
./helpers/integration/database-test-helper.py run-tests --database mysql  # Specific database
./helpers/integration/database-test-helper.py cleanup         # Clean up test data
./helpers/integration/database-test-helper.py report          # Generate report

# Using the integration runner directly
python runners/integration_runner.py                # Run tests
python runners/integration_runner.py --verbose      # Verbose output
python runners/integration_runner.py --coverage     # With coverage

# Or via test runner framework
./test-runner.py --spec specs/integration/INT-001-database-integration-comprehensive-testing.md
```

### Direct Go Test Execution
For development and debugging:

```bash
# Navigate to database code directory
cd core/database

# Run all tests
go test -v -timeout 30m

# Run specific test category
go test -v -run TestService_TestConnection -timeout 10m
go test -v -run TestService_GetMetadata -timeout 10m
go test -v -run TestService_CRUD -timeout 10m

# Run tests for specific database type
go test -v -run ".*MySQLService" -timeout 10m
go test -v -run ".*PostgresService" -timeout 10m

# With coverage
go test -v -coverprofile=coverage.out -timeout 30m
go tool cover -html=coverage.out -o coverage.html
```

### Docker Setup
Start required database services:

```bash
# Using docker-compose
cd tests
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

**Note**: Tests now include automatic cleanup that runs even if tests fail or panic. Manual cleanup is only needed for container management.

```bash
# Stop test execution if running
# Use Ctrl+C or kill the process

# Automatic cleanup (now handled by tests):
# - Test database records automatically deleted from MongoDB
# - Test tables and data automatically dropped
# - No manual cleanup needed for test data

# Stop and remove database containers
docker-compose -f docker-compose.test.yml down -v

# Clear test artifacts (optional)
rm -f results/* coverage.out coverage.html
rm -rf /tmp/crawlab-db-test-*
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
- Tests may take 30-45 minutes for complete run
- Individual test functions run in parallel where possible
- Large data operations may timeout - adjust `-timeout` flag
- Connection pooling reduces overhead for multiple operations

### CI/CD Integration
- Tests designed to run in GitHub Actions
- Docker containers used for database dependencies
- Test results reported in JUnit XML format
- Coverage reports uploaded to Codecov

## History
- **Created**: 2025-10-05, GitHub Copilot
- **Modified**: -
- **Last Run**: -
