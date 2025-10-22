# Dependencies Management Test Specification

## Overview
Test dependency management features including package installation, version control, environment management, and dependency conflict resolution for spider execution environments.

## Test Environment
- **Target URL**: `http://localhost:5173`
- **Test Database**: `mongodb://dev_user:dev_password@localhost:27018/crawlab_test?authSource=admin`
- **Prerequisites**: Authenticated user, node management access, Pro license
- **Test Environments**: Python, Node.js, Go environments

---

## Test Cases

### TC-09-01: Python Package Management
**Objective**: Test Python package installation and management
**Priority**: High
**Estimated Duration**: 6 minutes

**Steps**:
1. Navigate to Dependencies Management section
2. Select "Python" environment
3. View currently installed packages
4. Install new package:
   - Search for "requests" package
   - Select specific version (e.g., 2.28.1)
   - Click install and monitor progress
5. Verify package appears in installed list
6. Test package upgrade:
   - Select requests package
   - Upgrade to latest version
   - Verify version change
7. Test package removal:
   - Select test package
   - Uninstall and confirm
8. Test bulk package installation from requirements.txt

**Expected Results**:
- Package search works efficiently
- Installation progress is clearly shown
- Version management is accurate
- Bulk installation from requirements file works
- Package operations complete successfully

### TC-09-02: Node.js Package Management
**Objective**: Test npm/yarn package management for Node.js spiders
**Priority**: High
**Estimated Duration**: 5 minutes

**Steps**:
1. Switch to Node.js environment
2. View current package.json dependencies
3. Install new npm package:
   - Search for "axios" package
   - Install specific version
   - Verify installation in node_modules
4. Test development dependencies:
   - Install dev dependency (e.g., "eslint")
   - Verify it appears in devDependencies
5. Test package.json management:
   - Edit package.json directly
   - Run npm install to sync changes
6. Test yarn vs npm package manager selection
7. Test global vs local package installation

**Expected Results**:
- npm/yarn operations work correctly
- package.json is maintained accurately
- Development and production dependencies are handled properly
- Package manager selection affects behavior appropriately

### TC-09-03: Dependency Conflict Resolution
**Objective**: Test handling of dependency conflicts and version incompatibilities
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Create scenario with conflicting dependencies:
   - Install package A requiring dependency X v1.0
   - Install package B requiring dependency X v2.0
2. View conflict detection and warnings
3. Check suggested resolution options:
   - Use latest compatible version
   - Force specific version
   - Manual resolution
4. Apply conflict resolution
5. Verify resolution doesn't break existing functionality
6. Test dependency tree visualization
7. Check dependency audit for security issues
8. Test lock file (requirements.txt / package-lock.json) management

**Expected Results**:
- Conflicts are detected automatically
- Clear resolution options are provided
- Resolution maintains application stability
- Dependency tree is visualized clearly
- Security audits identify vulnerabilities

### TC-09-04: Environment Isolation
**Objective**: Test isolated environments for different spiders/projects
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Create new isolated environment:
   - Name: "Project A Environment"
   - Base: Python 3.9
   - Isolated: Yes
2. Install specific packages in this environment
3. Create second isolated environment:
   - Name: "Project B Environment"
   - Base: Python 3.8
   - Different package versions
4. Assign spiders to different environments
5. Verify package isolation between environments
6. Test environment switching for spiders
7. Check resource usage per environment
8. Test environment cloning/duplication

**Expected Results**:
- Environments are properly isolated
- Package versions don't conflict between environments
- Spider assignment works correctly
- Environment switching is seamless
- Resource usage is tracked accurately

### TC-09-05: Custom Package Sources
**Objective**: Test adding custom package repositories and sources
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to Package Sources configuration
2. Add custom PyPI index:
   - URL: Custom package repository
   - Authentication if required
   - Priority/order setting
3. Test package installation from custom source
4. Add private npm registry:
   - Configure registry URL
   - Set authentication token
   - Test package availability
5. Configure package source priorities
6. Test fallback to default sources
7. Verify source selection during installation

**Expected Results**:
- Custom sources are configured easily
- Authentication works securely
- Package installation uses correct sources
- Fallback mechanisms work properly
- Source priorities are respected

### TC-09-06: Dependency Scanning and Security
**Objective**: Test dependency security scanning and vulnerability detection
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to Security Scanning section
2. Run security scan on current dependencies
3. View vulnerability report:
   - Severity levels
   - Affected packages
   - Available fixes
   - Upgrade recommendations
4. Apply security updates:
   - Auto-update safe packages
   - Manual review for breaking changes
5. Configure automatic security scanning
6. Set up vulnerability alerts
7. Test compliance reporting
8. Check license compatibility scanning

**Expected Results**:
- Security scans are comprehensive
- Vulnerabilities are clearly prioritized
- Update recommendations are accurate
- Automated scanning works reliably
- Compliance reports are detailed

### TC-09-07: Bulk Operations and Import/Export
**Objective**: Test bulk dependency operations and environment portability
**Priority**: Low
**Estimated Duration**: 4 minutes

**Steps**:
1. Export current environment:
   - Generate requirements.txt
   - Export package.json
   - Create environment snapshot
2. Import environment to new node:
   - Upload requirements file
   - Restore from snapshot
   - Verify package installation
3. Test bulk package operations:
   - Update all packages
   - Remove unused packages
   - Clean package cache
4. Clone environment across nodes
5. Test environment backup and restore
6. Verify cross-platform compatibility

**Expected Results**:
- Environment export is complete
- Import recreates environment accurately
- Bulk operations work efficiently
- Environment cloning preserves functionality
- Cross-platform issues are handled

### TC-09-08: Performance and Resource Monitoring
**Objective**: Test dependency management performance and resource usage
**Priority**: Low
**Estimated Duration**: 3 minutes

**Steps**:
1. Monitor package installation performance:
   - Installation time tracking
   - Download speed monitoring
   - Disk space usage
2. Check dependency cache management:
   - Cache hit rates
   - Cache size limits
   - Cache cleanup policies
3. Test concurrent package operations:
   - Multiple simultaneous installations
   - Resource contention handling
4. Monitor memory usage during operations
5. Check network bandwidth usage
6. Test package installation optimization

**Expected Results**:
- Performance metrics are tracked
- Resource usage is optimized
- Concurrent operations work smoothly
- Cache management is efficient
- Network usage is reasonable

---

## Test Data Requirements

### Package Test Sets

#### Python Packages
- **Basic packages**: requests, numpy, pandas
- **Version-specific**: Django==3.2.0, Flask==2.0.1
- **Development tools**: pytest, black, flake8
- **Data science**: scikit-learn, matplotlib, seaborn
- **Conflicting packages**: Different versions of same dependency

#### Node.js Packages
- **Utility packages**: lodash, moment, axios
- **Development tools**: eslint, prettier, jest
- **Framework packages**: express, react, vue
- **Global tools**: pm2, nodemon, typescript

#### Test Requirements Files
```txt
# requirements.txt
requests==2.28.1
pandas>=1.3.0
numpy==1.21.0
scikit-learn~=1.0.0
```

```json
// package.json
{
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "4.17.21"
  },
  "devDependencies": {
    "jest": "^28.0.0",
    "eslint": "^8.15.0"
  }
}
```

### Environment Configurations
- **Python 3.8**: With basic data science stack
- **Python 3.9**: With web scraping tools
- **Node.js 16**: With modern JavaScript tools
- **Node.js 18**: With latest features

## Success Criteria
- Package management operations complete successfully
- Dependency conflicts are resolved effectively
- Environment isolation prevents package interference
- Security scanning identifies and resolves vulnerabilities
- Bulk operations and import/export work reliably
- Performance monitoring provides useful insights

## Performance Benchmarks
- Package search: < 2 seconds
- Single package installation: < 30 seconds
- Bulk installation (10 packages): < 5 minutes
- Environment export: < 10 seconds
- Security scan: < 60 seconds
- Environment switching: < 5 seconds

## Integration Points
- Spider execution uses correct environment packages
- Node assignment respects environment configuration
- Task execution includes dependency verification
- Performance metrics integrate with system monitoring
