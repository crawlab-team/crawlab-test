# DEP-001 - Dependencies Installation Robustness

## Metadata
- **Category**: dependencies
- **Priority**: high
- **Complexity**: moderate
- **Duration**: 10-15 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker, package managers (pip, npm, etc.)

## Scenario
This test validates that Crawlab's dependency installation system can handle various edge cases robustly, including network failures, package conflicts, version mismatches, and concurrent installations. This ensures spiders can reliably install their required dependencies in production environments.

## Prerequisites
- Crawlab cluster running with at least 1 worker node
- Worker nodes have package managers installed (pip, npm, yarn, etc.)
- Network access to package repositories
- Test spider projects with various dependency requirements
- Sufficient disk space for package installations

## Test Steps

### Step 1: System Prerequisites Check
**Method**: script
**Command**: Verify dependency management system is properly configured
**Expected**: Dependency management system is properly configured
**Validation**: Python environments, package managers, network access available

### Step 2: Normal Package Installation
**Method**: script
**Command**: Test normal package installation with common packages
**Expected**: Packages install successfully without errors
**Validation**: Packages importable, correct versions installed

### Step 3: Version Conflict Resolution
**Method**: script
**Command**: Test version conflict resolution with incompatible package versions
**Expected**: System handles version conflicts gracefully
**Validation**: Clear error messages, system remains stable

### Step 4: Network Interruption Recovery
**Method**: script
**Command**: Test installation recovery after network interruption during package download
**Expected**: Installation resumes after network restoration
**Validation**: Package installation completes successfully

### Step 5: Concurrent Installation Stress
**Method**: script
**Command**: Test concurrent package installations to verify no race conditions
**Expected**: Multiple installations proceed without conflicts
**Validation**: No race conditions, all packages installed correctly

### Step 6: Large Package Handling
**Method**: script
**Command**: Test installation of large packages to verify timeout and memory handling
**Expected**: Large packages install without timeout or memory issues
**Validation**: Installation completes, packages functional

### Step 7: Dependency Isolation
**Method**: script
**Command**: Test dependency isolation between different spider environments
**Expected**: Different spiders maintain separate dependency versions
**Validation**: No cross-contamination between spider environments

### Step 8: Test Missing Dependencies Detection
**Method**: script
**Command**: Test error handling when spider has missing dependencies
**Expected**: System detects and reports missing dependencies clearly
**Validation**: 
- Clear error messages about missing packages
- Suggestions for resolution provided
- Spider execution prevented until resolved

## Success Criteria
- [ ] Normal package installation completes successfully
- [ ] Version conflicts detected and reported clearly
- [ ] Network interruptions handled gracefully with cleanup
- [ ] Concurrent installations work without corruption
- [ ] Large packages install with proper progress tracking
- [ ] Package isolation prevents version conflicts
- [ ] Missing dependencies detected before spider execution
- [ ] Failed installations don't corrupt the environment
- [ ] Retry mechanisms work correctly
- [ ] Cleanup operations remove packages completely

## Failure Scenarios
- **Scenario**: Package installation leaves corrupted state
- **Symptoms**: Import errors, partial installations, broken environments
- **Action**: Check cleanup mechanisms and rollback procedures

- **Scenario**: Concurrent installations cause race conditions
- **Symptoms**: File locks, corrupted packages, installation failures
- **Action**: Verify locking mechanisms and installation queuing

- **Scenario**: Large packages fail due to resource constraints
- **Symptoms**: Out of memory, disk space, timeout errors
- **Action**: Check resource monitoring and graceful degradation

## Execution

### Automated
```bash
# Execute via test-runner (auto-discovers runner script)
./test-runner.py --spec specs/dependencies/DEP-001-dependencies-installation-robustness.md

# Or specify script method explicitly
./test-runner.py --spec specs/dependencies/DEP-001-dependencies-installation-robustness.md --method script
```

### AI-Assisted
```bash
# Let AI execute the test using browser automation
ai-test-runner --spec specs/dependencies/installation-robustness.md --domain ui
```

### Manual
1. Open Crawlab UI and navigate to spiders
2. Create test spider with various dependencies
3. Attempt installation and monitor progress
4. Try installing conflicting versions
5. Simulate network issues during installation
6. Verify isolation between different spider environments

## Cleanup
- Remove test packages: Clean up test packages from environments
- Reset virtual environments: Reset spider environments to clean state
- Clear package caches: Clear pip and package manager caches
- Test-runner handles automatic cleanup of test artifacts

## Notes
- Test with different package managers (pip, conda, npm)
- Consider testing with private package repositories
- Monitor disk space usage during large package installations
- Test behavior with slow network connections
- Verify security aspects of package installation

## History
- **Created**: 2025-09-17, Assistant
- **Modified**: -
- **Last Run**: -