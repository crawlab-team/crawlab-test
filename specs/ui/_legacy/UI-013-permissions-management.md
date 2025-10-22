# Permissions Management Test Specification

## Overview
Test user management, role-based access control (RBAC), permissions assignment, and security features for multi-user Crawlab environments.

## Test Environment
- **Target URL**: `http://localhost:5173`
- **Test Database**: `mongodb://dev_user:dev_password@localhost:27018/crawlab_test?authSource=admin`
- **Prerequisites**: Admin user authenticated, Pro license
- **Test Users**: Admin, Developer, Viewer, Custom roles

---

## Test Cases

### TC-12-01: User Management
**Objective**: Test user creation, modification, and deletion
**Priority**: High
**Estimated Duration**: 5 minutes

**Steps**:
1. Navigate to User Management section
2. Create new user:
   - Username: "test_developer"
   - Email: "dev@test.com"
   - Password: Strong password
   - Full name: "Test Developer"
3. Set user status to Active
4. Verify user appears in user list
5. Edit user details:
   - Update email address
   - Change full name
   - Modify user status
6. Test user password reset:
   - Generate reset link
   - Verify reset process
7. Disable user account
8. Delete test user (after other tests)

**Expected Results**:
- User creation form validates inputs correctly
- User details are saved accurately
- Email validation works properly
- Password requirements are enforced
- User modification updates immediately
- Account status changes affect access

### TC-12-02: Role-Based Access Control (RBAC)
**Objective**: Test role creation and permission assignment
**Priority**: High
**Estimated Duration**: 6 minutes

**Steps**:
1. Navigate to Roles Management
2. View default roles:
   - Admin: Full system access
   - Developer: Spider and project management
   - Viewer: Read-only access
3. Create custom role:
   - Name: "Spider Manager"
   - Description: "Can manage spiders only"
   - Permissions: Spider CRUD, Task viewing
4. Configure role permissions:
   - Enable spider management
   - Disable user management
   - Allow project read access
   - Deny system settings
5. Save custom role
6. Assign role to test user
7. Verify role inheritance and conflicts

**Expected Results**:
- Default roles have appropriate permissions
- Custom role creation is flexible
- Permission granularity is detailed
- Role assignment works correctly
- Permission conflicts are handled properly

### TC-12-03: Permission Testing by Feature
**Objective**: Test specific feature permissions across different roles
**Priority**: High
**Estimated Duration**: 8 minutes

**Steps**:
1. Test Spider Management permissions:
   - Admin: Full CRUD access
   - Developer: Create, read, update, delete own
   - Viewer: Read-only access
   - Custom role: Based on configuration
2. Test Project Management permissions:
   - Create new project (by role)
   - Modify existing project
   - Delete project
   - View project analytics
3. Test User Management permissions:
   - Create users (admin only)
   - View user list (admin/developer)
   - Modify user details
   - Delete users (admin only)
4. Test System Settings permissions:
   - Access system configuration
   - Modify system settings
   - View system logs
   - Manage system integrations

**Expected Results**:
- Permissions are enforced correctly per feature
- Unauthorized actions show appropriate errors
- UI elements hide/show based on permissions
- API calls respect permission levels

### TC-12-04: Multi-User Collaboration
**Objective**: Test collaborative features and shared resource access
**Priority**: Medium
**Estimated Duration**: 5 minutes

**Steps**:
1. Create shared project with multiple users
2. Assign different roles to project members:
   - Project owner (admin)
   - Project developer
   - Project viewer
3. Test collaborative spider development:
   - Multiple users editing different spiders
   - Concurrent task execution
   - Shared spider templates
4. Test resource sharing:
   - Shared spider configurations
   - Common dependency environments
   - Shared notification settings
5. Verify access control on shared resources
6. Test collaboration notifications and activity feeds

**Expected Results**:
- Multiple users can work simultaneously
- Resource sharing maintains security
- Collaborative features enhance productivity
- Activity tracking provides transparency
- Notifications keep team informed

### TC-12-05: Permission Inheritance and Hierarchies
**Objective**: Test complex permission inheritance scenarios
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Create organizational hierarchy:
   - Organization admin
   - Department managers
   - Team leads
   - Individual contributors
2. Test permission inheritance:
   - Department inherits from organization
   - Teams inherit from departments
   - Users inherit from teams
3. Test permission overrides:
   - Grant additional permissions
   - Revoke inherited permissions
   - Resolve permission conflicts
4. Test cross-department access:
   - Shared resources between departments
   - Cross-department collaboration
   - Global resource access

**Expected Results**:
- Permission inheritance works logically
- Overrides are applied correctly
- Conflicts are resolved predictably
- Cross-department access is controlled
- Hierarchy changes propagate properly

### TC-12-06: API Access and Token Management
**Objective**: Test API authentication and authorization
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to API Token Management
2. Generate API token for user:
   - Set token name and description
   - Configure token permissions
   - Set expiration date
3. Test API access with token:
   - Make authenticated API calls
   - Verify permission enforcement
   - Test token-based authorization
4. Test token management:
   - List active tokens
   - Revoke token access
   - Rotate token keys
5. Test API rate limiting by user role
6. Verify API audit logging

**Expected Results**:
- API tokens are generated securely
- Token permissions are enforced
- Token management is comprehensive
- Rate limiting works per role
- API access is audited properly

### TC-12-07: Security and Audit Features
**Objective**: Test security monitoring and audit capabilities
**Priority**: Medium
**Estimated Duration**: 4 minutes

**Steps**:
1. Navigate to Security Audit section
2. View user activity logs:
   - Login/logout events
   - Permission changes
   - Resource access attempts
   - Failed authentication attempts
3. Test security alerts:
   - Multiple failed login attempts
   - Unusual access patterns
   - Permission escalation attempts
4. Configure security policies:
   - Password complexity requirements
   - Session timeout settings
   - Failed login lockout
5. Test compliance reporting:
   - Generate access reports
   - Export audit logs
   - User permission summaries

**Expected Results**:
- Comprehensive activity logging
- Security alerts trigger appropriately
- Policy enforcement is effective
- Compliance reports are detailed
- Audit trails are tamper-evident

### TC-12-08: Single Sign-On (SSO) Integration
**Objective**: Test SSO integration and external authentication
**Priority**: Low
**Estimated Duration**: 4 minutes

**Steps**:
1. Configure SSO integration:
   - LDAP/Active Directory
   - SAML 2.0 provider
   - OAuth 2.0 / OpenID Connect
2. Test SSO authentication flow:
   - Redirect to external provider
   - Handle authentication response
   - Map external user to internal user
3. Test user provisioning:
   - Auto-create users on first login
   - Update user details from SSO
   - Handle group/role mapping
4. Test SSO user management:
   - Sync user status changes
   - Handle disabled accounts
   - Manage SSO failures
5. Test mixed authentication:
   - Local and SSO users coexisting
   - Authentication fallback options

**Expected Results**:
- SSO integration works seamlessly
- User provisioning is automatic
- Role mapping is accurate
- Mixed authentication is supported
- SSO failures are handled gracefully

---

## Test Data Requirements

### Test Users
```yaml
users:
  - username: admin_user
    role: Admin
    email: admin@test.com
    status: Active
    
  - username: dev_user1
    role: Developer
    email: dev1@test.com
    status: Active
    
  - username: dev_user2
    role: Developer
    email: dev2@test.com
    status: Active
    
  - username: viewer_user
    role: Viewer
    email: viewer@test.com
    status: Active
    
  - username: custom_user
    role: Spider Manager
    email: custom@test.com
    status: Active
```

### Test Roles and Permissions
```yaml
roles:
  admin:
    permissions:
      - "*"  # All permissions
      
  developer:
    permissions:
      - "spider:*"
      - "project:*"
      - "task:read"
      - "node:read"
      
  viewer:
    permissions:
      - "spider:read"
      - "project:read"
      - "task:read"
      - "node:read"
      
  spider_manager:
    permissions:
      - "spider:create"
      - "spider:read"
      - "spider:update"
      - "spider:delete"
      - "task:read"
      - "task:execute"
```

### Permission Matrix
| Feature | Admin | Developer | Viewer | Custom |
|---------|-------|-----------|--------|---------|
| User Management | ✓ | ✗ | ✗ | ✗ |
| Spider CRUD | ✓ | ✓ | R | ✓ |
| Project Management | ✓ | ✓ | R | R |
| Task Execution | ✓ | ✓ | ✗ | ✓ |
| System Settings | ✓ | ✗ | ✗ | ✗ |
| Node Management | ✓ | R | R | ✗ |

## Success Criteria
- User management operations work correctly
- Role-based permissions are enforced consistently
- Collaborative features maintain security
- Permission inheritance functions properly
- API access control is secure
- Audit and security features provide comprehensive monitoring

## Performance Benchmarks
- User creation: < 3 seconds
- Role assignment: < 2 seconds
- Permission check: < 100ms
- Authentication: < 1 second
- Audit log query: < 5 seconds
- User list loading: < 3 seconds

## Security Requirements
- Passwords meet complexity requirements
- Session management is secure
- Permission checks are server-side enforced
- Audit logs are immutable
- API tokens are properly secured
- SSO integration follows security best practices
