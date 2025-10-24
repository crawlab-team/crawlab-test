# API-005: Spider File Management

**Category**: API Testing  
**Priority**: P1 (Critical Foundation)  
**Estimated Duration**: 3-5 minutes  
**Backend**: script

## Overview

Validates spider file management operations including creating files, reading content, listing directories, renaming, copying, and deleting files within spider projects via the Crawlab API.

## Objectives

- Verify file creation (save) with content
- Test directory creation
- Validate file content retrieval
- Test file listing in directories
- Confirm file metadata (info) retrieval
- Test file renaming operations
- Verify file copying
- Validate file deletion
- Ensure proper error handling for invalid paths

## Prerequisites

- Crawlab instance running at `http://localhost:8080`
- Valid authentication token (admin credentials)
- Clean test environment

## API Endpoints Tested

- `POST /api/spiders/{id}/files/save` - Save/create file
- `POST /api/spiders/{id}/files/save/dir` - Create directory
- `GET /api/spiders/{id}/files/get` - Get file content
- `GET /api/spiders/{id}/files/list` - List files in directory
- `GET /api/spiders/{id}/files/info` - Get file metadata
- `POST /api/spiders/{id}/files/rename` - Rename file
- `POST /api/spiders/{id}/files/copy` - Copy file
- `DELETE /api/spiders/{id}/files` - Delete file

## Test Steps

### 1. Setup and Authentication
- Login with admin credentials
- Obtain JWT token for subsequent requests

### 2. Create Test Spider
- Create a spider for file operations testing
- Name: "test-spider-files-001"
- Save spider ID for file operations

### 3. Save File - Create Main Script
- Save a Python file to spider
- Path: "main.py"
- Content: Simple Python script (print hello world)
- Verify file is created successfully

### 4. Get File Content
- Retrieve content of "main.py"
- Verify content matches what was saved
- Check content is returned as string

### 5. Get File Info (Metadata)
- Get file info for "main.py"
- Verify metadata includes:
  - File name
  - File size
  - File type (not directory)
- Confirm is_dir is false

### 6. Save File - Create Config
- Save a JSON config file
- Path: "config.json"
- Content: JSON configuration data
- Verify file is created

### 7. Create Directory
- Create a subdirectory "utils"
- Path: "utils"
- Verify directory is created

### 8. Save File in Subdirectory
- Save file in "utils" directory
- Path: "utils/helper.py"
- Content: Python helper function
- Verify file is created in subdirectory

### 9. List Root Directory Files
- List files in root directory ("/")
- Verify list contains:
  - main.py
  - config.json
  - utils/ (directory)
- Check proper file/directory distinction

### 10. List Subdirectory Files
- List files in "utils" directory
- Verify list contains:
  - helper.py
- Confirm subdirectory listing works

### 11. Get Directory Info
- Get info for "utils" directory
- Verify is_dir is true
- Confirm it's recognized as directory

### 12. Copy File
- Copy "main.py" to "main_backup.py"
- Source: "main.py"
- Destination: "main_backup.py"
- Verify copy succeeds

### 13. Verify Copied File
- Get content of "main_backup.py"
- Verify content matches original "main.py"
- Confirm both files exist independently

### 14. Rename File
- Rename "main_backup.py" to "main_copy.py"
- Old path: "main_backup.py"
- New path: "main_copy.py"
- Verify rename succeeds

### 15. Verify Renamed File
- Get content of "main_copy.py"
- Verify file exists with new name
- Confirm old name no longer exists
- Check content is preserved

### 16. Delete File
- Delete "main_copy.py"
- Verify deletion succeeds
- Attempt to get deleted file
- Confirm file no longer exists

### 17. Delete File in Subdirectory
- Delete "utils/helper.py"
- Verify deletion succeeds
- List "utils" directory
- Confirm directory is now empty

### 18. Invalid Path Handling
- Attempt to get non-existent file
- Path: "nonexistent.py"
- Verify appropriate error response
- Attempt to delete non-existent file

### 19. Cleanup Spider
- Delete test spider
- Verify spider and all files are removed

## Success Criteria

- All file save operations work correctly
- File content retrieval returns exact content
- File metadata provides accurate information
- Directory creation and listing work properly
- File listing correctly distinguishes files from directories
- Copy operation creates independent duplicate
- Rename operation preserves content
- Delete operations remove files permanently
- Invalid paths return appropriate errors
- All HTTP status codes are correct

## Cleanup

- Delete test spider (removes all associated files)
- No lingering test data in database

## Expected Results

- Test execution completes in < 5 minutes
- All assertions pass successfully
- No unexpected errors or warnings
- Clean test environment after completion

## Known Issues

None currently documented.

## Notes

- File paths are relative to spider root directory
- File content is transmitted as string (data field)
- Directory creation may be implicit when saving files in new paths
- Spider deletion removes all associated files automatically
- File operations are synchronous
