# Database Integration Test Specification

## Overview
Test database integration features including database connections, data source management, data export/import, and various database type support.

## Test Environment
- **Target URL**: `http://localhost:5173`
- **Test Database**: `mongodb://dev_user:dev_password@localhost:27018/crawlab_test?authSource=admin`
- **Prerequisites**: Authenticated user, access to various database types, Pro license
- **Test Databases**: MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch instances

---

## Test Cases

### TC-08-01: Database Connection Setup
**Objective**: Verify connecting to various database types
**Priority**: High
**Estimated Duration**: 6 minutes

**Steps**:
1. Navigate to Database Integration section
2. Click "Add Database Connection"
3. Test MySQL connection:
   - Select MySQL database type
   - Enter connection details (host, port, username, password, database)
   - Test connection
   - Save connection with name "MySQL Test DB"
4. Test PostgreSQL connection:
   - Configure PostgreSQL connection
   - Test SSL connection options
   - Verify connection success
5. Test MongoDB connection:
   - Configure MongoDB with authentication
   - Test connection string format
   - Verify database listing
6. Test Redis connection:
   - Configure Redis with password
   - Test connection and ping
7. Verify all connections appear in database list

**Expected Results**:
- All database types are supported
- Connection forms validate inputs correctly
- Test connection provides clear feedback
- Connections are saved with proper credentials
- Database list shows all active connections

### TC-08-02: Database Schema Exploration
**Objective**: Test database schema browsing and exploration
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Select MySQL database connection
2. Browse database schemas/databases
3. Explore table structure:
   - View table list
   - Click on table to see columns
   - Check data types and constraints
   - View indexes and keys
4. Test PostgreSQL schema exploration:
   - Browse schemas within database
   - View table relationships
   - Check stored procedures/functions
5. Test MongoDB collection exploration:
   - Browse collections
   - View document structure
   - Check indexes
6. Search for specific tables/collections

**Expected Results**:
- Schema browsing is intuitive and fast
- Table/collection structures are accurately displayed
- Relationships and constraints are visible
- Search functionality works effectively
- Different database types are handled appropriately

### TC-08-03: Data Export Configuration
**Objective**: Test exporting spider results to external databases
**Priority**: High
**Estimated Duration**: 6 minutes

**Steps**:
1. Navigate to spider with completed results
2. Click "Export Data" option
3. Configure export to MySQL:
   - Select target database
   - Choose destination table
   - Map spider fields to table columns
   - Set export options (insert/update)
4. Execute export operation
5. Verify export progress tracking
6. Check exported data in target database
7. Test export to PostgreSQL with different mapping
8. Test export to MongoDB collection
9. Configure scheduled/automatic exports

**Expected Results**:
- Export configuration is flexible and clear
- Field mapping works correctly
- Export operations complete successfully
- Progress tracking is accurate
- Data integrity is maintained
- Scheduled exports function properly

### TC-08-04: Data Import and Seeding
**Objective**: Test importing data from external databases
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Navigate to Data Import section
2. Select source database connection
3. Choose source table/collection
4. Configure import settings:
   - Select specific columns/fields
   - Set data transformation rules
   - Configure data filtering
5. Preview import data
6. Execute import operation
7. Verify imported data appears in Crawlab
8. Test incremental import functionality
9. Configure import scheduling

**Expected Results**:
- Import configuration is comprehensive
- Data preview is accurate
- Import operations are reliable
- Data transformations work correctly
- Incremental imports detect changes
- Scheduling works as expected

### TC-08-05: Real-time Data Synchronization
**Objective**: Test real-time sync between Crawlab and external databases
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Configure real-time sync for a spider
2. Set up bi-directional synchronization
3. Configure sync triggers:
   - On spider completion
   - On data change
   - Time-based intervals
4. Test sync with MySQL database
5. Make changes in external database
6. Verify changes sync to Crawlab
7. Make changes in Crawlab
8. Verify changes sync to external database
9. Check sync conflict resolution

**Expected Results**:
- Real-time sync is configured easily
- Sync triggers work reliably
- Bi-directional sync maintains consistency
- Conflicts are detected and resolved
- Sync performance is acceptable

### TC-08-06: Database Query Builder
**Objective**: Test visual query builder for database operations
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Open query builder interface
2. Select database connection
3. Build simple SELECT query:
   - Choose table
   - Select columns
   - Add WHERE conditions
   - Set ORDER BY clause
4. Execute query and view results
5. Build complex JOIN query:
   - Add multiple tables
   - Configure JOIN conditions
   - Test INNER, LEFT, RIGHT joins
6. Save query for reuse
7. Export query results

**Expected Results**:
- Query builder is intuitive and powerful
- Visual query construction works correctly
- SQL generation is accurate
- Query execution is fast
- Results display is clear and navigable
- Query saving and reuse functions properly

### TC-08-07: Database Performance Monitoring
**Objective**: Test database connection performance monitoring
**Priority**: Low
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to Database Performance dashboard
2. View connection performance metrics:
   - Connection latency
   - Query execution times
   - Data transfer rates
   - Error rates
3. Check historical performance trends
4. Set up performance alerts:
   - Slow query detection
   - Connection timeout alerts
   - High error rate warnings
5. Test alert triggering
6. View performance optimization suggestions

**Expected Results**:
- Performance metrics are comprehensive
- Historical data provides useful insights
- Alerts trigger appropriately
- Optimization suggestions are helpful
- Dashboard is responsive and informative

### TC-08-08: Database Security and Access Control
**Objective**: Test database security features and access control
**Priority**: High
**Estimated Duration**: 4 minutes

**Steps**:
1. Configure database connection with limited user permissions
2. Test connection with read-only access
3. Verify write operations are blocked appropriately
4. Test SSL/TLS connection security
5. Configure connection encryption
6. Test credential rotation:
   - Update database password
   - Update connection in Crawlab
   - Verify continued functionality
7. Test connection pooling and limits
8. Verify audit logging for database operations

**Expected Results**:
- Access control is enforced correctly
- SSL/TLS connections work securely
- Credential management is secure
- Connection pooling optimizes performance
- Audit logs capture important operations
- Security settings are configurable

---

## Test Data Requirements

### Database Instances
- **MySQL 8.0+**: With test schema and sample data
- **PostgreSQL 13+**: With multiple schemas and complex relationships
- **MongoDB 4.4+**: With collections and various document structures
- **Redis 6.0+**: With different data types and structures
- **Elasticsearch 7.x**: With indices and sample documents

### Test Data Sets
- **Customer data**: Names, emails, addresses (100+ records)
- **Product catalog**: Items, categories, prices (500+ records)
- **Transaction logs**: Timestamps, amounts, references (1000+ records)
- **Hierarchical data**: Categories with parent-child relationships

### Database Schemas
```sql
-- MySQL Test Schema
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

## Success Criteria
- All major database types connect successfully
- Data export/import operations work reliably
- Real-time synchronization maintains data consistency
- Query builder generates correct SQL
- Performance monitoring provides useful insights
- Security features protect database access

## Performance Benchmarks
- Database connection: < 5 seconds
- Schema exploration: < 3 seconds
- Data export (1000 records): < 30 seconds
- Data import (1000 records): < 45 seconds
- Query execution: < 10 seconds for complex queries
- Real-time sync latency: < 5 seconds

## Security Requirements
- All database credentials encrypted at rest
- SSL/TLS connections supported
- Role-based access control enforced
- Audit logging for all operations
- Connection timeout and retry mechanisms
- SQL injection prevention measures
