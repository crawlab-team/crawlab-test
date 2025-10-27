# API-012: Dependency Management - Configs

**Test ID**: API-012  
**Category**: API  
**Backend**: Script (Python)  
**Priority**: P2  
**Created**: 2024-10-27

## Objective

Validate dependency configuration management endpoints for managing programming language dependency settings and configuration setups.

**Endpoints Covered**:
- `GET /api/dependencies/configs/{lang}` - Get dependency config
- `PUT /api/dependencies/configs/{lang}` - Update dependency config
- `GET /api/dependencies/configs/{lang}/versions` - Get config versions
- `GET /api/dependencies/configs/{lang}/setups` - List config setups
- `POST /api/dependencies/configs/{lang}/setups/install` - Install config setup
- `POST /api/dependencies/configs/{lang}/setups/uninstall` - Uninstall config setup

## Prerequisites

- Crawlab server running at `http://localhost:8080`
- Valid admin credentials (`admin:admin`)
- At least one node available in the cluster
- Supported programming language runtime (e.g., Python, Node.js)

## Test Steps

### Setup

#### 1. Authenticate
- Login with admin credentials
- Obtain authentication token
- Store token for subsequent requests

### Dependency Config Operations

#### 2. Get Python Config
- GET `/api/dependencies/configs/python`
- Verify config object returned with:
  - `key` = "python"
  - `exec_cmd` (e.g., "python3")
  - `pkg_cmd` (e.g., "pip3")
  - `pkg_src_url` (e.g., PyPI URL)
  - `setup` flag (boolean)

#### 3. Update Python Config
- PUT `/api/dependencies/configs/python` with modified commands:
  ```json
  {
    "exec_cmd": "python3",
    "pkg_cmd": "pip3 install",
    "pkg_src_url": "https://pypi.org/simple"
  }
  ```
- Verify 200/204 response
- GET config again to verify changes persisted

#### 4. Restore Original Config
- PUT `/api/dependencies/configs/python` with original values
- Verify restoration successful

#### 5. Get Config Versions
- GET `/api/dependencies/configs/python/versions`
- Verify response contains array of version strings
- Check for common Python versions (3.8, 3.9, 3.10, etc.)
- Note: May return empty array if versions not cached

#### 6. Test Invalid Language
- GET `/api/dependencies/configs/invalid-language`
- Expect 404 or empty response
- Verify error handling

### Config Setup Operations

#### 7. List Config Setups
- GET `/api/dependencies/configs/python/setups`
- Verify paginated response with setup objects
- Each setup should have:
  - `dependency_config_id`
  - `node_id`
  - `version`
  - `status` (installing/installed/failed)
  - Optional: `error`, `drivers`

#### 8. List Config Setups with Pagination
- GET `/api/dependencies/configs/python/setups?page=1&size=5`
- Verify pagination parameters respected
- Check `total` count in response

#### 9. Install Config Setup (All Nodes)
- POST `/api/dependencies/configs/python/setups/install`
  ```json
  {
    "mode": "all"
  }
  ```
- Verify 200/201/204 response
- Note: Actual installation may be async
- Check setup list for new installation tasks

#### 10. Install Config Setup (Specific Node)
- Get list of available nodes
- POST `/api/dependencies/configs/python/setups/install`
  ```json
  {
    "mode": "specific",
    "node_ids": ["<node_id>"]
  }
  ```
- Verify installation initiated

#### 11. Install with Version
- POST `/api/dependencies/configs/python/setups/install`
  ```json
  {
    "mode": "all",
    "version": "3.10"
  }
  ```
- Verify version-specific installation accepted
- Note: Actual version availability depends on system

#### 12. Uninstall Config Setup (All Nodes)
- POST `/api/dependencies/configs/python/setups/uninstall`
  ```json
  {
    "mode": "all"
  }
  ```
- Verify 200/204 response
- Note: Uninstallation may be async

#### 13. Uninstall Config Setup (Specific Node)
- POST `/api/dependencies/configs/python/setups/uninstall`
  ```json
  {
    "mode": "specific",
    "node_ids": ["<node_id>"]
  }
  ```
- Verify uninstallation initiated

### Edge Cases

#### 14. Install Without Mode
- POST `/api/dependencies/configs/python/setups/install` with empty body
- Verify API handles gracefully (default to "all" or error)

#### 15. Invalid Node ID
- POST `/api/dependencies/configs/python/setups/install` with invalid node ID
- Verify proper error handling

### Cleanup

#### 16. Logout
- POST `/api/logout`
- Clear authentication token

## Success Criteria

- All config retrieval endpoints return valid data structures
- Config update operations persist changes correctly
- Versions endpoint returns array (even if empty)
- Setup list endpoint returns paginated results
- Install/uninstall operations accept valid parameters
- Invalid requests return appropriate error responses
- All operations respect authentication requirements

## Expected Results

- **Config Operations**: 100% success (6/6 steps)
- **Setup Operations**: 80%+ success (7-8/9 steps)
  - Actual installation success depends on system environment
  - API contract validation is primary goal
- **Edge Cases**: 100% success (2/2 steps)

## Notes

- Install/uninstall operations are typically asynchronous
- Actual dependency installation requires proper system setup
- Focus is on API contract validation, not full installation success
- Config setup status may take time to update
- Test validates endpoint availability and request/response formats
- Python is used as primary test language (most common)
- Other languages (node, java, etc.) follow similar patterns

## Dependencies

- Test Helper: `helpers/api/dependency.py`
- Test Helper: `helpers/api/auth.py`
- Test Helper: `helpers/api/node.py` (for node IDs)
- Test Helper: `helpers/api/cleanup.py`
