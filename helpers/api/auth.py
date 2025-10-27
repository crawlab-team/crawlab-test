"""
Authentication Helper Module

Provides reusable functions for Crawlab API authentication.
"""

import os
import requests
from typing import Dict, Optional, Tuple


class AuthHelper:
    """Helper class for API authentication operations."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize API auth helper.
        
        Args:
            base_url: Base URL for the API (default: http://localhost:8080/api)
        """
        self.base_url = base_url.rstrip('/')
        # Set NO_PROXY to avoid proxy issues with localhost
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        
    def login(self, username: str = "admin", password: str = "admin") -> Tuple[Optional[str], Optional[Dict]]:
        """
        Login and get authentication token.
        
        Args:
            username: Username for login (default: admin)
            password: Password for login (default: admin)
            
        Returns:
            Tuple of (token, response_data) where token is the JWT token string
            Returns (None, error_data) on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('data')
                return token, data
            else:
                return None, {"error": f"Login failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def logout(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Logout and invalidate token.
        
        Args:
            token: JWT token to invalidate
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/logout",
                headers=self.get_auth_headers(token),
                timeout=10
            )
            
            return response.status_code == 200, response.json()
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """
        Get authentication headers with token.
        
        Args:
            token: JWT token
            
        Returns:
            Dictionary with Authorization header
        """
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if a token is valid by making a test request.
        
        Args:
            token: JWT token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Use /users/me endpoint to verify token
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.get_auth_headers(token),
                timeout=10
            )
            return response.status_code == 200
            
        except Exception:
            return False
    
    def create_token(self, token: str, name: str, role: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Create a new API token.
        
        Args:
            token: Admin JWT token for authentication
            name: Name for the new token
            role: Optional role for the token
            
        Returns:
            Tuple of (token_id, response_data)
        """
        try:
            payload = {"data": {"name": name}}
            if role:
                payload["data"]["role"] = role
                
            response = requests.post(
                f"{self.base_url}/tokens",
                headers=self.get_auth_headers(token),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token_id = data.get('data', {}).get('_id')
                return token_id, data
            else:
                return None, {"error": f"Token creation failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_token(self, token: str, token_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get token details by ID.
        
        Args:
            token: Admin JWT token for authentication
            token_id: ID of the token to retrieve
            
        Returns:
            Tuple of (token_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/tokens/{token_id}",
                headers=self.get_auth_headers(token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get token failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def list_tokens(self, token: str) -> Tuple[Optional[list], Optional[Dict]]:
        """
        List all tokens.
        
        Args:
            token: Admin JWT token for authentication
            
        Returns:
            Tuple of (tokens_list, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/tokens",
                headers=self.get_auth_headers(token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []), data
            else:
                return None, {"error": f"List tokens failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def delete_token(self, token: str, token_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a token by ID.
        
        Args:
            token: Admin JWT token for authentication
            token_id: ID of the token to delete
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/tokens/{token_id}",
                headers=self.get_auth_headers(token),
                timeout=10
            )
            
            return response.status_code == 200, response.json()
            
        except Exception as e:
            return False, {"error": str(e)}


# Convenience functions for quick usage
def quick_login(username: str = "admin", password: str = "admin") -> Optional[str]:
    """
    Quick login function that returns just the token.
    
    Args:
        username: Username for login
        password: Password for login
        
    Returns:
        JWT token string or None on failure
    """
    auth = AuthHelper()
    token, _ = auth.login(username, password)
    return token


def get_auth_headers(token: str) -> Dict[str, str]:
    """
    Quick function to get auth headers.
    
    Args:
        token: JWT token
        
    Returns:
        Dictionary with Authorization header
    """
    auth = AuthHelper()
    return auth.get_auth_headers(token)
