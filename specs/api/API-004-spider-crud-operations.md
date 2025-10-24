# API-004: Spider CRUD Operations

**Category**: API Testing  
**Priority**: P1 (Critical Foundation)  
**Estimated Duration**: 3-5 minutes  
**Backend**: script

## Overview

Validates complete CRUD (Create, Read, Update, Delete) operations for spiders via the Crawlab API. This test ensures the core spider management endpoints work correctly with proper request/response handling.

## Objectives

- Verify spider creation with required and optional fields
- Validate spider retrieval by ID
- Test spider updates (both partial and full)
- Confirm spider deletion
- Test listing spiders with pagination
- Validate duplicate name handling
- Ensure proper error responses

## Prerequisites

- Crawlab instance running at `http://localhost:8080`
- Valid authentication token (admin credentials)
- Clean test environment (no existing test spiders)

## API Endpoints Tested

- `POST /api/spiders` - Create spider
- `GET /api/spiders/{id}` - Get spider by ID
- `GET /api/spiders` - List spiders
- `PUT /api/spiders/{id}` - Replace spider (full update)
- `PATCH /api/spiders/{id}` - Update spider (partial update)
- `DELETE /api/spiders/{id}` - Delete spider

## Test Steps

### 1. Setup and Authentication
- Login with admin credentials
- Obtain JWT token for subsequent requests

### 2. Create Spider - Basic
- Create spider with minimal required fields:
  - name: "test-spider-crud-001"
  - cmd: "python main.py"
- Verify response contains:
  - Spider ID
  - Created timestamp
  - All provided fields
- Save spider ID for subsequent tests

### 3. Retrieve Spider
- Get spider by ID from step 2
- Verify all fields match creation data:
  - name: "test-spider-crud-001"
  - cmd: "python main.py"
- Confirm presence of system fields (_id, created_at)

### 4. Create Spider - Full Fields
- Create spider with all optional fields:
  - name: "test-spider-crud-002"
  - cmd: "scrapy crawl myspider"
  - description: "Test spider with full configuration"
  - mode: "random"
  - priority: 7
  - col_name: "test_results"
- Verify all fields are persisted correctly

### 5. List Spiders
- Get list of all spiders
- Verify both test spiders are present
- Check pagination parameters (page, size)
- Verify response includes total count

### 6. Update Spider - Partial (PATCH)
- Update spider from step 2 with:
  - description: "Updated description"
  - priority: 8
- Verify only specified fields changed
- Confirm other fields remain unchanged
- Check updated_at timestamp changed

### 7. Update Spider - Full (PUT)
- Replace spider from step 2 with:
  - name: "test-spider-crud-001-updated"
  - cmd: "python spider.py"
  - description: "Fully replaced spider"
  - mode: "all"
  - priority: 9
- Verify all fields match new values
- Confirm spider ID remains the same

### 8. Duplicate Name Validation
- Attempt to create spider with duplicate name:
  - name: "test-spider-crud-001-updated" (already exists)
  - cmd: "python test.py"
- Verify request is rejected with appropriate error
- Expected: 400 Bad Request or similar

### 9. Invalid ID Handling
- Attempt to get spider with invalid ID:
  - ID: "000000000000000000000000" (non-existent)
- Verify 404 Not Found response
- Attempt to update non-existent spider
- Attempt to delete non-existent spider

### 10. Delete Spider
- Delete spider from step 2
- Verify deletion succeeds (200 OK)
- Attempt to retrieve deleted spider
- Verify spider no longer exists (404 Not Found)

### 11. Delete Second Spider
- Delete spider from step 4
- Verify deletion succeeds
- Confirm cleanup is complete

### 12. List After Deletion
- List all spiders
- Verify test spiders no longer present
- Confirm list is clean

## Success Criteria

- All spider CRUD operations work correctly
- Response data matches request data
- System fields (ID, timestamps) are properly maintained
- Partial updates only modify specified fields
- Full updates replace all fields
- Duplicate names are rejected
- Invalid IDs return appropriate errors
- Deletions are permanent and verifiable
- All HTTP status codes are correct

## Cleanup

- Delete all test spiders created during test
- No lingering test data in database

## Expected Results

- Test execution completes in < 5 minutes
- All assertions pass successfully
- No unexpected errors or warnings
- Clean test environment after completion

## Known Issues

None currently documented.

## Notes

- Request format: `{"data": {...}}` wrapper required for POST/PUT
- Response format: `{"data": {...}}` for single object
- Spider names should be unique across the system
- System maintains created_by and updated_by fields automatically
- Priority default is 5 (range typically 1-10)
- Mode options: "random", "all", "selected-nodes"
