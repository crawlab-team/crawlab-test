# API-013: Dependency Management - Repositories

**Test ID**: API-013  
**Category**: API  
**Backend**: Script (Python)  
**Priority**: P2  
**Created**: 2024-10-27

## Objective

Validate dependency repository management endpoints for searching, listing, installing, and uninstalling programming language packages.

**Endpoints Covered**:
- `GET /api/dependencies/repos` - List installed repositories
- `GET /api/dependencies/repos/search` - Search for repositories
- `GET /api/dependencies/repos/versions` - Get repository versions
- `POST /api/dependencies/repos/install` - Install repository/package
- `POST /api/dependencies/repos/uninstall` - Uninstall repository/package
- `GET /api/dependencies/{id}/logs` - Get dependency logs

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid admin credentials (`admin:admin`)
- At least one node available in the cluster
- Python dependency config properly set up
- Network access for package search (if testing remote search)

## Test Steps

### Setup

#### 1. Authenticate
- Login with admin credentials
- Obtain authentication token
- Store token for subsequent requests

### Repository List Operations

#### 2. List Installed Repositories (Python)
- GET `/api/dependencies/repos?lang=python&page=1&size=10`
- Verify paginated response with repository objects
- Each repo should have:
  - `name` (package name)
  - `version` (installed version)
  - `type` (language type)
  - Optional: `latest_version`, `description`
- Note: May be empty if no packages installed yet

#### 3. List with Custom Page Size
- GET `/api/dependencies/repos?lang=python&page=1&size=20`
- Verify size parameter respected
- Check total count in response

#### 4. List with Filter
- GET `/api/dependencies/repos?lang=python&filter={"name":"requests"}`
- Verify filter applied correctly
- Results should match filter criteria
- Note: Filter syntax depends on implementation

#### 5. List for Different Language
- GET `/api/dependencies/repos?lang=node&page=1&size=10`
- Verify language parameter works
- Results should be for Node.js packages (npm)

### Repository Search Operations

#### 6. Search for Python Package
- GET `/api/dependencies/repos/search?lang=python&query=requests&page=1&size=10`
- Verify search results returned
- Each result should have:
  - `name`
  - Optional: `description`, `latest_version`
- Note: Requires search index to be ready

#### 7. Search with Empty Query
- GET `/api/dependencies/repos/search?lang=python&query=&page=1&size=10`
- Verify API handles empty query gracefully
- May return popular packages or empty results

#### 8. Search for Specific Package
- GET `/api/dependencies/repos/search?lang=python&query=beautifulsoup4&page=1&size=5`
- Verify specific package search works
- Should find BeautifulSoup4 in results

#### 9. Search with Pagination
- GET `/api/dependencies/repos/search?lang=python&query=django&page=2&size=10`
- Verify pagination works for search results

### Repository Versions Operations

#### 10. Get Package Versions
- GET `/api/dependencies/repos/versions?lang=python&name=requests`
- Verify version list returned
- Should contain array of version strings
- Versions should be in reverse chronological order (newest first)

#### 11. Get Versions for Invalid Package
- GET `/api/dependencies/repos/versions?lang=python&name=nonexistent-package-xyz`
- Verify error handling (404 or empty array)

### Repository Install/Uninstall Operations

#### 12. Install Package (All Nodes)
- POST `/api/dependencies/repos/install`
  ```json
  {
    "lang": "python",
    "name": "requests",
    "mode": "all"
  }
  ```
- Verify 200/201/204 response
- Note: Actual installation is async

#### 13. Install Package with Version
- POST `/api/dependencies/repos/install`
  ```json
  {
    "lang": "python",
    "name": "certifi",
    "version": "2023.7.22",
    "mode": "all"
  }
  ```
- Verify version-specific installation accepted

#### 14. Install on Specific Node
- Get available node ID
- POST `/api/dependencies/repos/install`
  ```json
  {
    "lang": "python",
    "name": "urllib3",
    "mode": "specific",
    "node_ids": ["<node_id>"]
  }
  ```
- Verify node-specific installation accepted

#### 15. Uninstall Package (All Nodes)
- POST `/api/dependencies/repos/uninstall`
  ```json
  {
    "lang": "python",
    "name": "certifi",
    "mode": "all"
  }
  ```
- Verify 200/204 response
- Note: Uninstallation is async

#### 16. Uninstall from Specific Node
- POST `/api/dependencies/repos/uninstall`
  ```json
  {
    "lang": "python",
    "name": "urllib3",
    "mode": "specific",
    "node_ids": ["<node_id>"]
  }
  ```
- Verify node-specific uninstallation accepted

### Dependency Logs Operations

#### 17. Get Dependency Logs (Install)
- After installing a package, note the dependency ID
- GET `/api/dependencies/{id}/logs`
- Verify logs returned with:
  - Log lines array
  - Timestamps
  - Installation progress messages
- Note: Dependency ID must be valid from install/uninstall operation

#### 18. Get Logs for Invalid ID
- GET `/api/dependencies/invalid-id-123/logs`
- Verify error handling (404 or empty response)

### Edge Cases

#### 19. Install Without Language
- POST `/api/dependencies/repos/install` without `lang` field
- Verify proper error response (400 bad request)

#### 20. Install Without Package Name
- POST `/api/dependencies/repos/install` with `lang` but no `name`
- Verify validation error returned

#### 21. Search Without Language
- GET `/api/dependencies/repos/search?query=test` (no lang parameter)
- Verify error or default language handling

### Cleanup

#### 22. Logout
- POST `/api/logout`
- Clear authentication token

## Success Criteria

- Repository list endpoints return valid paginated data
- Search functionality returns relevant results
- Version retrieval works for valid packages
- Install/uninstall operations accept valid requests
- Logs endpoint returns installation logs
- Invalid requests return appropriate error responses
- Pagination works correctly across all list endpoints

## Expected Results

- **List Operations**: 90%+ success (4/4 steps)
- **Search Operations**: 75%+ success (3-4/4 steps)
  - Search index may not be ready initially
- **Versions Operations**: 80%+ success (1-2/2 steps)
- **Install/Uninstall**: 100% success (5/5 steps on API contract)
  - Focus on API acceptance, not actual installation success
- **Logs Operations**: 50%+ success (1/2 steps)
  - Logs require valid dependency ID from actual operations
- **Edge Cases**: 100% success (3/3 steps)

## Notes

- Install/uninstall operations are asynchronous
- Package search requires search index to be synced
- Actual package installation depends on:
  - Network connectivity
  - Package availability
  - Node system configuration
  - Dependency conflicts
- Test focuses on API contract validation
- Logs retrieval requires capturing dependency IDs from operations
- Different languages (python, node, java) have different package formats
- Some operations may timeout if package registry is slow

## Dependencies

- Test Helper: `helpers/api/dependency.py`
- Test Helper: `helpers/api/auth.py`
- Test Helper: `helpers/api/node.py` (for node IDs)
- Test Helper: `helpers/api/cleanup.py`
