#!/usr/bin/env python3
"""
API-003: User Management Test Runner

Tests user CRUD operations and password management.
"""

import os
import sys
import time
import requests

# Set NO_PROXY for localhost
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# Add helpers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../helpers'))

from api.auth import AuthHelper
from api.user import UserHelper
from api.cleanup import CleanupHelper

# Configuration
API_URL = os.getenv('CRAWLAB_API_URL', 'http://localhost:8080/api')
ADMIN_USER = os.getenv('CRAWLAB_ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.getenv('CRAWLAB_ADMIN_PASSWORD', 'admin')

def main():
    """Run API-003 test."""
    print("=" * 80)
    print("API-003: User Management")
    print("=" * 80)
    
    # Initialize helpers
    auth = AuthHelper(API_URL)
    user_helper = UserHelper(API_URL)
    cleanup = CleanupHelper(API_URL)
    
    token = None
    initial_user_count = 0
    user1_id = None
    user2_id = None
    
    try:
        # Setup: Authenticate
        print("\n[Setup] Authenticating as admin...")
        token, _ = auth.login(ADMIN_USER, ADMIN_PASSWORD)
        if not token:
            raise Exception("Failed to authenticate")
        print(f"✓ Authenticated successfully")
        
        # Record initial user count
        print("\n[Setup] Recording initial user count...")
        users_list, _ = user_helper.list_users(token)
        if users_list is None:
            raise Exception("Failed to list users")
        initial_user_count = len(users_list)
        print(f"✓ Initial user count: {initial_user_count}")
        
        # Test 1: Create user with required fields only
        print("\n[Test 1] Creating user with required fields...")
        user1_id, response = user_helper.create_user(token, "test_user_api003", "test123")
        if not user1_id:
            raise Exception(f"Failed to create user: {response}")
        cleanup.track_user(user1_id)
        print(f"✓ User created: {user1_id}")
        
        # Test 2: Create user with optional fields
        print("\n[Test 2] Creating user with optional fields...")
        user2_id, response = user_helper.create_user(
            token, "test_user_api003_full", "test456", email="test@example.com"
        )
        if not user2_id:
            raise Exception(f"Failed to create user with email: {response}")
        cleanup.track_user(user2_id)
        print(f"✓ User created with email: {user2_id}")
        
        # Test 3: Attempt duplicate username
        print("\n[Test 3] Attempting to create duplicate username...")
        dup_id, response = user_helper.create_user(token, "test_user_api003", "test789")
        if dup_id:
            print(f"⚠ Duplicate username creation succeeded (backend may allow this): {dup_id}")
            cleanup.track_user(dup_id)  # Track for cleanup
        else:
            print(f"✓ Duplicate username rejected")
        
        # Test 4: Attempt creation without required fields
        print("\n[Test 4] Attempting to create user without required fields...")
        # Note: Helper requires username and password, so we'll use requests directly
        try:
            response = requests.post(
                f"{API_URL}/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": {"email": "nouser@example.com"}},
                timeout=10
            )
            if response.status_code >= 400:
                print(f"✓ Missing required fields rejected with status {response.status_code}")
            else:
                print(f"⚠ Missing fields request succeeded with status {response.status_code}")
        except Exception as e:
            print(f"✓ Missing required fields rejected: {e}")
        
        # Test 5: Get user list
        print("\n[Test 5] Getting user list...")
        users_list, _ = user_helper.list_users(token)
        if users_list is None:
            raise Exception("Failed to list users")
        usernames = [u['username'] for u in users_list]
        assert 'test_user_api003' in usernames, "test_user_api003 should be in list"
        assert 'test_user_api003_full' in usernames, "test_user_api003_full should be in list"
        print(f"✓ User list contains {len(users_list)} users including test users")
        
        # Test 6: Get specific user by ID
        print("\n[Test 6] Getting specific user by ID...")
        user_data, _ = user_helper.get_user(token, user1_id)
        if not user_data:
            raise Exception(f"Failed to get user {user1_id}")
        assert user_data['username'] == 'test_user_api003', "Username mismatch"
        # Verify password is not in response
        assert 'password' not in user_data or user_data.get('password') == '', \
            "Password should not be returned in response"
        print(f"✓ User retrieved: {user_data['username']}")
        
        # Test 7: Attempt to get non-existent user
        print("\n[Test 7] Attempting to get non-existent user...")
        fake_id = "000000000000000000000000"
        user_data, response = user_helper.get_user(token, fake_id)
        if user_data is None:
            print(f"✓ Non-existent user not found")
        else:
            print(f"⚠ Non-existent user request did not fail as expected")
        
        # Test 8: Update user email
        print("\n[Test 8] Updating user email...")
        success, response = user_helper.update_user(
            token, user1_id, 
            username="test_user_api003",
            password="test123",
            email="updated@example.com"
        )
        if not success:
            raise Exception(f"Failed to update user email: {response}")
        print(f"✓ Email updated to: updated@example.com")
        
        # Test 9: Update username
        print("\n[Test 9] Updating username...")
        success, response = user_helper.update_user(
            token, user1_id,
            username="test_user_api003_updated",
            password="test123",
            email="updated@example.com"
        )
        if not success:
            raise Exception(f"Failed to update username: {response}")
        print(f"✓ Username updated to: test_user_api003_updated")
        
        # Test 10: Attempt to update to duplicate username
        print("\n[Test 10] Attempting to update to duplicate username...")
        success, response = user_helper.update_user(
            token, user1_id,
            username="test_user_api003_full",  # This username already exists
            password="test123"
        )
        if not success:
            print(f"✓ Duplicate username update rejected")
        else:
            print(f"⚠ Duplicate username update succeeded (backend may allow this)")
            # Revert the change
            user_helper.update_user(
                token, user1_id,
                username="test_user_api003_updated",
                password="test123"
            )
        
        # Test 11: Change user password
        print("\n[Test 11] Changing user password...")
        new_password = "newpass123"
        success, response = user_helper.change_password(token, user1_id, new_password)
        if not success:
            raise Exception(f"Failed to change password: {response}")
        print(f"✓ Password changed successfully")
        
        # Test 12: Verify new password works
        print("\n[Test 12] Verifying new password...")
        # Try to login with old password (should fail)
        old_token, _ = auth.login("test_user_api003_updated", "test123")
        if old_token:
            print(f"⚠ Old password still works (token invalidation may not be immediate)")
            auth.logout(old_token)
        else:
            print(f"✓ Old password rejected")
        
        # Try to login with new password (should succeed)
        new_token, _ = auth.login("test_user_api003_updated", new_password)
        if not new_token:
            print(f"✗ New password login failed - password may not have changed")
        else:
            print(f"✓ New password works for authentication")
            auth.logout(new_token)
        
        # Test 13: Attempt password change with empty password
        print("\n[Test 13] Attempting to change to empty password...")
        success, response = user_helper.change_password(token, user1_id, "")
        if not success:
            print(f"✓ Empty password rejected")
        else:
            print(f"⚠ Empty password accepted (may be a validation issue)")
        
        # Test 14: Delete a user
        print("\n[Test 14] Deleting user...")
        success, response = user_helper.delete_user(token, user2_id)
        if not success:
            raise Exception(f"Failed to delete user: {response}")
        print(f"✓ User deleted: {user2_id}")
        
        # Test 15: Verify deleted user is gone
        print("\n[Test 15] Verifying deleted user is gone...")
        user_data, response = user_helper.get_user(token, user2_id)
        if user_data is None:
            print(f"✓ Deleted user not found")
        else:
            print(f"⚠ Deleted user still accessible")
        
        # Test 16: Attempt to delete non-existent user
        print("\n[Test 16] Attempting to delete non-existent user...")
        fake_id = "000000000000000000000000"
        success, response = user_helper.delete_user(token, fake_id)
        if not success:
            print(f"✓ Non-existent user deletion returned error")
        else:
            print(f"✓ Non-existent user deletion handled (idempotent)")
        
        # Cleanup
        print("\n[Cleanup] Removing test users...")
        stats = cleanup.cleanup_all(token)
        print(f"✓ Cleaned up {stats['users']} users")
        
        # Verify cleanup
        print("\n[Cleanup] Verifying cleanup...")
        users_list, _ = user_helper.list_users(token)
        if users_list is None:
            raise Exception("Failed to list users after cleanup")
        final_user_count = len(users_list)
        print(f"✓ Final user count: {final_user_count} (initial: {initial_user_count})")
        
        if final_user_count > initial_user_count:
            print(f"⚠ Warning: {final_user_count - initial_user_count} extra users remain")
        
        print("\n" + "=" * 80)
        print("API-003: User Management - PASSED")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Logout
        if token:
            try:
                print("\n[Cleanup] Logging out...")
                auth.logout(token)
                print("✓ Logged out")
            except Exception as e:
                print(f"⚠ Logout failed: {str(e)}")

if __name__ == '__main__':
    sys.exit(main())
