"""
Node Group Helper Module

Provides reusable functions for Crawlab node group operations.
"""

import os
from typing import Dict, List, Optional, Tuple

import requests


class NodeGroupHelper:
    """Helper class for node group operations."""

    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize node group helper.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip("/")
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"

    def create_node_group(
        self, token: str, name: str, description: Optional[str] = None, node_ids: Optional[List[str]] = None
    ) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Create a new node group.

        Args:
            token: JWT authentication token
            name: Node group name
            description: Optional description
            node_ids: Optional list of node IDs to include

        Returns:
            Tuple of (created_group, response_data)
        """
        try:
            payload = {"data": {"name": name}}

            if description is not None:
                payload["data"]["description"] = description

            if node_ids is not None:
                payload["data"]["node_ids"] = node_ids

            response = requests.post(
                f"{self.base_url}/node-groups",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {
                    "error": f"Create node group failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def list_node_groups(
        self, token: str, page: int = 1, size: int = 10, filter_str: Optional[str] = None
    ) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List node groups with optional filtering.

        Args:
            token: JWT authentication token
            page: Page number (default: 1)
            size: Page size (default: 10)
            filter_str: Optional filter string (searches in name/description)

        Returns:
            Tuple of (groups_list, response_data)
        """
        try:
            params = {"page": page, "size": size}

            if filter_str:
                params["filter"] = filter_str

            response = requests.get(
                f"{self.base_url}/node-groups", headers={"Authorization": f"Bearer {token}"}, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                groups = data.get("data")
                return (groups if groups is not None else []), data
            else:
                return None, {"error": f"List node groups failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def get_node_group(self, token: str, group_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get node group details by ID.

        Args:
            token: JWT authentication token
            group_id: Node group ID

        Returns:
            Tuple of (group_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/node-groups/{group_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {"error": f"Get node group failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def update_node_group(
        self, token: str, group_id: str, updates: Dict
    ) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Update node group.

        Args:
            token: JWT authentication token
            group_id: Node group ID
            updates: Dictionary of fields to update (name, description, node_ids)

        Returns:
            Tuple of (updated_group, response_data)
        """
        try:
            payload = {"data": updates}

            response = requests.put(
                f"{self.base_url}/node-groups/{group_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {
                    "error": f"Update node group failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def delete_node_group(self, token: str, group_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a node group by ID.

        Args:
            token: JWT authentication token
            group_id: Node group ID

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/node-groups/{group_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Delete node group failed with status {response.status_code}"}

        except Exception as e:
            return False, {"error": str(e)}

    def delete_node_groups_batch(self, token: str, group_ids: List[str]) -> Tuple[bool, Optional[Dict]]:
        """
        Delete multiple node groups.

        Args:
            token: JWT authentication token
            group_ids: List of node group IDs to delete

        Returns:
            Tuple of (success, response_data)
        """
        try:
            payload = {"ids": group_ids}

            response = requests.delete(
                f"{self.base_url}/node-groups",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Batch delete node groups failed with status {response.status_code}"}

        except Exception as e:
            return False, {"error": str(e)}

    def add_node_to_group(
        self, token: str, group_id: str, node_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Add a node to a node group.

        Args:
            token: JWT authentication token
            group_id: Node group ID
            node_id: Node ID to add

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # No data wrapper for this endpoint - direct JSON body
            payload = {"node_id": node_id}

            response = requests.post(
                f"{self.base_url}/node-groups/{group_id}/nodes",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {
                    "error": f"Add node to group failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return False, {"error": str(e)}

    def remove_node_from_group(
        self, token: str, group_id: str, node_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Remove a node from a node group.

        Args:
            token: JWT authentication token
            group_id: Node group ID
            node_id: Node ID to remove

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/node-groups/{group_id}/nodes/{node_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {"error": f"Remove node from group failed with status {response.status_code}"}

        except Exception as e:
            return False, {"error": str(e)}
