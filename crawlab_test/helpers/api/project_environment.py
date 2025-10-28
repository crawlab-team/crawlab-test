#!/usr/bin/env python3
"""
Project & Environment API Helper

Provides utilities for interacting with Crawlab's project and environment API endpoints.
"""

import logging
from typing import Any, Dict, List, Optional

import requests


class ProjectEnvironmentAPIHelper:
    """Helper class for project and environment API operations"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize project/environment API helper

        Args:
            base_url: API base URL (default: http://localhost:8080/api)
            token: Authentication token
        """
        self.base_url = (base_url or "http://localhost:8080/api").rstrip("/")
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # Projects

    def create_project(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new project

        Args:
            data: Project data including:
                - name: Project name
                - description: Project description (optional)
                - tags: Project tags (optional)

        Returns:
            Created project object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/projects", json={"data": data}, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            return None

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project details by ID

        Args:
            project_id: Project ID

        Returns:
            Project object or None on failure
        """
        try:
            response = requests.get(f"{self.base_url}/projects/{project_id}", headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to get project: {e}")
            return None

    def list_projects(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all projects

        Args:
            page: Page number
            size: Page size

        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/projects",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            return None

    def update_project(self, project_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update project properties

        Args:
            project_id: Project ID
            data: Updated data

        Returns:
            Updated project object or None on failure
        """
        try:
            response = requests.put(
                f"{self.base_url}/projects/{project_id}", json={"data": data}, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to update project: {e}")
            return None

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project

        Args:
            project_id: Project ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/projects/{project_id}", headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete project: {e}")
            return False

    def batch_update_projects(self, project_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple projects

        Args:
            project_ids: List of project IDs
            update_data: Data to update

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/projects",
                json={"ids": project_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update projects: {e}")
            return False

    def batch_delete_projects(self, project_ids: List[str]) -> bool:
        """
        Batch delete multiple projects

        Args:
            project_ids: List of project IDs

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/projects", json={"ids": project_ids}, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch delete projects: {e}")
            return False

    # Environments

    def create_environment(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new environment

        Args:
            data: Environment data including:
                - key: Environment key/name
                - value: Environment value

        Returns:
            Created environment object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/environments", json={"data": data}, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to create environment: {e}")
            return None

    def get_environment(self, environment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get environment details by ID

        Args:
            environment_id: Environment ID

        Returns:
            Environment object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/environments/{environment_id}", headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to get environment: {e}")
            return None

    def list_environments(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all environments

        Args:
            page: Page number
            size: Page size

        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/environments",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list environments: {e}")
            return None

    def update_environment(self, environment_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update environment properties

        Args:
            environment_id: Environment ID
            data: Updated data

        Returns:
            Updated environment object or None on failure
        """
        try:
            response = requests.put(
                f"{self.base_url}/environments/{environment_id}",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data")
        except Exception as e:
            self.logger.error(f"Failed to update environment: {e}")
            return None

    def delete_environment(self, environment_id: str) -> bool:
        """
        Delete an environment

        Args:
            environment_id: Environment ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/environments/{environment_id}", headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete environment: {e}")
            return False

    def batch_update_environments(self, environment_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple environments

        Args:
            environment_ids: List of environment IDs
            update_data: Data to update

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/environments",
                json={"ids": environment_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update environments: {e}")
            return False

    def batch_delete_environments(self, environment_ids: List[str]) -> bool:
        """
        Batch delete multiple environments

        Args:
            environment_ids: List of environment IDs

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/environments", json={"ids": environment_ids}, headers=self._get_headers(), timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch delete environments: {e}")
            return False
