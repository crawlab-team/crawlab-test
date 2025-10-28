"""
Git Helper Module

Provides reusable functions for Crawlab git operations.
"""

import os
from typing import Dict, List, Optional, Tuple

import requests


class GitHelper:
    """Helper class for git operations."""

    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize git helper.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip("/")
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"

    def _get_headers(self, token: str) -> Dict[str, str]:
        """
        Get request headers with authentication token.

        Args:
            token: JWT authentication token

        Returns:
            Dictionary of headers
        """
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def create_git(
        self,
        token: str,
        name: str,
        url: str,
        auth_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Create a new git repository connection.

        Args:
            token: JWT authentication token
            name: Git repository name
            url: Git repository URL
            auth_type: Authentication type (http, ssh)
            username: Git username (for HTTP auth)
            password: Git password/token (for HTTP auth)
            **kwargs: Additional git fields

        Returns:
            Tuple of (git_id, response_data)
        """
        try:
            payload = {"data": {"name": name, "url": url, **kwargs}}

            if auth_type:
                payload["data"]["auth_type"] = auth_type
            if username:
                payload["data"]["username"] = username
            if password:
                payload["data"]["password"] = password

            response = requests.post(
                f"{self.base_url}/gits", headers=self._get_headers(token), json=payload, timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                git_data = data.get("data", {})
                git_id = git_data.get("_id")
                return git_id, data
            else:
                return None, response.json()

        except Exception as e:
            print(f"Error creating git: {e}")
            return None, None

    def get_git(self, token: str, git_id: str) -> Optional[Dict]:
        """
        Get git repository details by ID.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            Git repository data or None
        """
        try:
            response = requests.get(f"{self.base_url}/gits/{git_id}", headers=self._get_headers(token), timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error getting git: {e}")
            return None

    def list_gits(self, token: str, page: int = 1, size: int = 10, conditions: Optional[str] = None) -> Optional[Dict]:
        """
        List git repositories with pagination and filtering.

        Args:
            token: JWT authentication token
            page: Page number (default: 1)
            size: Page size (default: 10)
            conditions: JSON filter conditions

        Returns:
            Response data with list of gits
        """
        try:
            params = {"page": page, "size": size}
            if conditions:
                params["conditions"] = conditions

            response = requests.get(
                f"{self.base_url}/gits", headers=self._get_headers(token), params=params, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error listing gits: {e}")
            return None

    def update_git(self, token: str, git_id: str, **kwargs) -> Optional[Dict]:
        """
        Update git repository.

        Args:
            token: JWT authentication token
            git_id: Git repository ID
            **kwargs: Fields to update

        Returns:
            Response data or None
        """
        try:
            payload = {"data": kwargs}

            response = requests.put(
                f"{self.base_url}/gits/{git_id}", headers=self._get_headers(token), json=payload, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error updating git: {e}")
            return None

    def delete_git(self, token: str, git_id: str) -> bool:
        """
        Delete git repository.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            True if deleted successfully
        """
        try:
            response = requests.delete(f"{self.base_url}/gits/{git_id}", headers=self._get_headers(token), timeout=10)

            return response.status_code in [200, 204]

        except Exception as e:
            print(f"Error deleting git: {e}")
            return False

    def batch_update_gits(self, token: str, git_ids: List[str], **kwargs) -> Optional[Dict]:
        """
        Batch update git repositories.

        Args:
            token: JWT authentication token
            git_ids: List of git IDs to update
            **kwargs: Fields to update

        Returns:
            Response data or None
        """
        try:
            payload = {"ids": git_ids, "update": kwargs}

            response = requests.patch(
                f"{self.base_url}/gits", headers=self._get_headers(token), json=payload, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error batch updating gits: {e}")
            return None

    def batch_delete_gits(self, token: str, git_ids: List[str]) -> bool:
        """
        Batch delete git repositories.

        Args:
            token: JWT authentication token
            git_ids: List of git IDs to delete

        Returns:
            True if deleted successfully
        """
        try:
            response = requests.delete(
                f"{self.base_url}/gits", headers=self._get_headers(token), json={"ids": git_ids}, timeout=10
            )

            return response.status_code in [200, 204]

        except Exception as e:
            print(f"Error batch deleting gits: {e}")
            return False

    def clone_git(self, token: str, git_id: str, branch: Optional[str] = None) -> Optional[Dict]:
        """
        Clone git repository.

        Args:
            token: JWT authentication token
            git_id: Git repository ID
            branch: Branch to checkout (optional)

        Returns:
            Response data or None
        """
        try:
            payload = {}
            if branch:
                payload["branch"] = branch

            response = requests.post(
                f"{self.base_url}/gits/{git_id}/clone",
                headers=self._get_headers(token),
                json=payload,
                timeout=120,  # Cloning can take time
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error cloning git: {e}")
            return None

    def checkout_git(self, token: str, git_id: str, branch: str) -> Optional[Dict]:
        """
        Checkout git branch.

        Args:
            token: JWT authentication token
            git_id: Git repository ID
            branch: Branch name to checkout

        Returns:
            Response data or None
        """
        try:
            payload = {"branch": branch}

            response = requests.post(
                f"{self.base_url}/gits/{git_id}/checkout", headers=self._get_headers(token), json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error checking out branch: {e}")
            return None

    def pull_git(self, token: str, git_id: str) -> Optional[Dict]:
        """
        Pull git repository changes.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            Response data or None
        """
        try:
            response = requests.post(
                f"{self.base_url}/gits/{git_id}/pull", headers=self._get_headers(token), timeout=60
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error pulling git: {e}")
            return None

    def commit_git(self, token: str, git_id: str, message: str, files: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Commit changes to git repository.

        Args:
            token: JWT authentication token
            git_id: Git repository ID
            message: Commit message
            files: List of files to commit (optional, commits all if not provided)

        Returns:
            Response data or None
        """
        try:
            payload = {"message": message}
            if files:
                payload["files"] = files

            response = requests.post(
                f"{self.base_url}/gits/{git_id}/commit", headers=self._get_headers(token), json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error committing changes: {e}")
            return None

    def push_git(self, token: str, git_id: str) -> Optional[Dict]:
        """
        Push git repository changes.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            Response data or None
        """
        try:
            response = requests.post(
                f"{self.base_url}/gits/{git_id}/push", headers=self._get_headers(token), timeout=60
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error pushing git: {e}")
            return None

    def get_git_branches(self, token: str, git_id: str) -> Optional[Dict]:
        """
        Get git repository branches.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            Response data with branches list
        """
        try:
            response = requests.get(
                f"{self.base_url}/gits/{git_id}/branches", headers=self._get_headers(token), timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error getting git branches: {e}")
            return None

    def get_git_remotes(self, token: str, git_id: str) -> Optional[Dict]:
        """
        Get git repository remotes.

        Args:
            token: JWT authentication token
            git_id: Git repository ID

        Returns:
            Response data with remotes list
        """
        try:
            response = requests.get(
                f"{self.base_url}/gits/{git_id}/remotes", headers=self._get_headers(token), timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error getting git remotes: {e}")
            return None

    def get_git_logs(self, token: str, git_id: str, page: int = 1, size: int = 10) -> Optional[Dict]:
        """
        Get git repository commit logs.

        Args:
            token: JWT authentication token
            git_id: Git repository ID
            page: Page number
            size: Page size

        Returns:
            Response data with commit logs
        """
        try:
            params = {"page": page, "size": size}

            response = requests.get(
                f"{self.base_url}/gits/{git_id}/logs", headers=self._get_headers(token), params=params, timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            print(f"Error getting git logs: {e}")
            return None
