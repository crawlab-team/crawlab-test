"""
User Helper Module

Provides reusable functions for Crawlab user operations.
"""

import os
import requests
from typing import Dict, Optional, Tuple, List


class UserHelper:
    """Helper class for user operations."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize user helper.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    def create_user(self, token: str, username: str, password: str, 
                   email: Optional[str] = None, role: Optional[str] = None, **kwargs) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Create a new user.
        
        Args:
            token: JWT authentication token
            username: Username
            password: Password
            email: Optional email
            role: Optional role
            **kwargs: Additional user fields
            
        Returns:
            Tuple of (user_id, response_data)
        """
        try:
            payload = {
                "data": {
                    "username": username,
                    "password": password,
                    **kwargs
                }
            }
            if email:
                payload["data"]["email"] = email
            if role:
                payload["data"]["role"] = role
            
            response = requests.post(
                f"{self.base_url}/users",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('data', {}).get('_id')
                return user_id, data
            else:
                return None, {"error": f"User creation failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_user(self, token: str, user_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get user details by ID.
        
        Args:
            token: JWT authentication token
            user_id: User ID
            
        Returns:
            Tuple of (user_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get user failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_me(self, token: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get current user details.
        
        Args:
            token: JWT authentication token
            
        Returns:
            Tuple of (user_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get me failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def update_user(self, token: str, user_id: str, **updates) -> Tuple[bool, Optional[Dict]]:
        """
        Update user fields.
        
        Args:
            token: JWT authentication token
            user_id: User ID
            **updates: Fields to update
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.put(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": updates},
                timeout=10
            )
            
            return response.status_code == 200, response.json()
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def delete_user(self, token: str, user_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a user.
        
        Args:
            token: JWT authentication token
            user_id: User ID
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def list_users(self, token: str) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List all users.
        
        Args:
            token: JWT authentication token
            
        Returns:
            Tuple of (users_list, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/users",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []), data
            else:
                return None, {"error": f"List users failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def change_password(self, token: str, user_id: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Change user password (admin action).
        
        Args:
            token: JWT authentication token
            user_id: User ID
            password: New password
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/users/{user_id}/change-password",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"password": password},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def change_my_password(self, token: str, old_password: str, new_password: str) -> Tuple[bool, Optional[Dict]]:
        """
        Change current user's password.
        
        Args:
            token: JWT authentication token
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/users/me/change-password",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"old_password": old_password, "new_password": new_password},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
