"""
Spider Helper Module

Provides reusable functions for Crawlab spider operations.
"""

import os
from typing import Dict, List, Optional, Tuple

import requests


class SpiderHelper:
    """Helper class for spider operations."""

    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize spider helper.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip("/")
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"

    def create_spider(
        self, token: str, name: str, cmd: str = "python main.py", project_id: Optional[str] = None, **kwargs
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Create a new spider.

        Args:
            token: JWT authentication token
            name: Spider name
            cmd: Spider command (default: python main.py)
            project_id: Optional project ID
            **kwargs: Additional spider fields

        Returns:
            Tuple of (spider_id, response_data)
        """
        try:
            payload = {"data": {"name": name, "cmd": cmd, **kwargs}}
            if project_id:
                payload["data"]["project_id"] = project_id

            response = requests.post(
                f"{self.base_url}/spiders",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                spider_id = data.get("data", {}).get("_id")
                return spider_id, data
            else:
                return None, {
                    "error": f"Spider creation failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def get_spider(self, token: str, spider_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get spider details by ID.

        Args:
            token: JWT authentication token
            spider_id: Spider ID

        Returns:
            Tuple of (spider_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/spiders/{spider_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {"error": f"Get spider failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def update_spider(self, token: str, spider_id: str, **updates) -> Tuple[bool, Optional[Dict]]:
        """
        Update spider fields.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            **updates: Fields to update

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.put(
                f"{self.base_url}/spiders/{spider_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": updates},
                timeout=10,
            )

            return response.status_code == 200, response.json()

        except Exception as e:
            return False, {"error": str(e)}

    def delete_spider(self, token: str, spider_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/spiders/{spider_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def list_spiders(self, token: str) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List all spiders.

        Args:
            token: JWT authentication token

        Returns:
            Tuple of (spiders_list, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/spiders", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []), data
            else:
                return None, {"error": f"List spiders failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def save_file(self, token: str, spider_id: str, path: str, content: str) -> Tuple[bool, Optional[Dict]]:
        """
        Save a file to spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            path: File path (relative to spider root)
            content: File content

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/spiders/{spider_id}/files/save",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"path": path, "data": content},
                timeout=10,
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def list_files(self, token: str, spider_id: str, path: str = "/") -> Tuple[Optional[List], Optional[Dict]]:
        """
        List files in spider directory.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            path: Directory path (default: /)

        Returns:
            Tuple of (files_list, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/spiders/{spider_id}/files/list",
                headers={"Authorization": f"Bearer {token}"},
                params={"path": path},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []), data
            else:
                return None, {"error": f"List files failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def get_file(self, token: str, spider_id: str, path: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Get file content from spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            path: File path

        Returns:
            Tuple of (file_content, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/spiders/{spider_id}/files/get",
                headers={"Authorization": f"Bearer {token}"},
                params={"path": path},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {"error": f"Get file failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def get_file_info(self, token: str, spider_id: str, path: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get file info (metadata) from spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            path: File path

        Returns:
            Tuple of (file_info, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/spiders/{spider_id}/files/info",
                headers={"Authorization": f"Bearer {token}"},
                params={"path": path},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {"error": f"Get file info failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def copy_file(self, token: str, spider_id: str, src_path: str, dest_path: str) -> Tuple[bool, Optional[Dict]]:
        """
        Copy a file within spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/spiders/{spider_id}/files/copy",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"path": src_path, "new_path": dest_path},
                timeout=10,
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def rename_file(self, token: str, spider_id: str, old_path: str, new_path: str) -> Tuple[bool, Optional[Dict]]:
        """
        Rename a file in spider.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            old_path: Current file path
            new_path: New file path

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/spiders/{spider_id}/files/rename",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"path": old_path, "newPath": new_path},
                timeout=10,
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def run_spider(
        self, token: str, spider_id: str, cmd: Optional[str] = None, mode: str = "random", priority: int = 5
    ) -> Tuple[Optional[List[str]], Optional[Dict]]:
        """
        Run a spider (creates task).

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            cmd: Optional command override
            mode: Execution mode (random, all-nodes, selected-nodes)
            priority: Task priority (default: 5)

        Returns:
            Tuple of (task_ids_list, response_data)
        """
        try:
            payload = {"spider_id": spider_id, "mode": mode, "priority": priority}
            if cmd:
                payload["cmd"] = cmd

            response = requests.post(
                f"{self.base_url}/spiders/{spider_id}/run",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                task_ids = data.get("data", [])
                # Handle both array and single object responses
                if isinstance(task_ids, list):
                    return task_ids, data
                else:
                    return [task_ids] if task_ids else [], data
            else:
                return None, {
                    "error": f"Run spider failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}
