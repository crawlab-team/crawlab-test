"""
Task Helper Module

Provides reusable functions for Crawlab task operations.
"""

import os
import time
from typing import Dict, List, Optional, Tuple

import requests


class TaskHelper:
    """Helper class for task operations."""

    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize task helper.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip("/")
        os.environ["NO_PROXY"] = "localhost,127.0.0.1"

    def create_task(
        self, token: str, spider_id: str, cmd: Optional[str] = None, mode: str = "random", priority: int = 5, **kwargs
    ) -> Tuple[Optional[List[str]], Optional[Dict]]:
        """
        Create and run a task.

        Args:
            token: JWT authentication token
            spider_id: Spider ID
            cmd: Optional command override
            mode: Execution mode (random, all-nodes, selected-nodes)
            priority: Task priority (default: 5)
            **kwargs: Additional task parameters

        Returns:
            Tuple of (task_ids_list, response_data)
        """
        try:
            payload = {"spider_id": spider_id, "mode": mode, "priority": priority, **kwargs}
            if cmd:
                payload["cmd"] = cmd

            response = requests.post(
                f"{self.base_url}/tasks/run",
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
                    "error": f"Task creation failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def get_task(self, token: str, task_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get task details by ID.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Tuple of (task_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {"error": f"Get task failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def get_task_status(self, token: str, task_id: str) -> Optional[str]:
        """
        Get task status.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Task status string (pending, running, finished, error, cancelled) or None
        """
        task_data, _ = self.get_task(token, task_id)
        return task_data.get("status") if task_data else None

    def wait_for_task(
        self, token: str, task_id: str, timeout: int = 60, interval: int = 1
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Wait for task to complete.

        Args:
            token: JWT authentication token
            task_id: Task ID
            timeout: Maximum wait time in seconds (default: 60)
            interval: Check interval in seconds (default: 1)

        Returns:
            Tuple of (final_status, task_data)
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            task_data, _ = self.get_task(token, task_id)

            if task_data:
                status = task_data.get("status")

                # Check if task is in terminal state
                if status in ["finished", "error", "cancelled"]:
                    return status, task_data

            time.sleep(interval)

        # Timeout reached
        task_data, _ = self.get_task(token, task_id)
        return None, {"error": "Timeout waiting for task", "task_data": task_data}

    def get_task_logs(self, token: str, task_id: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Get task logs.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Tuple of (logs_string, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/logs", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                logs_data = data.get("data", "")

                # Handle both array and string formats
                logs = "\n".join(logs_data) if isinstance(logs_data, list) else str(logs_data) if logs_data else ""

                return logs, data
            else:
                return None, {"error": f"Get logs failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def get_task_results(self, token: str, task_id: str) -> Tuple[Optional[List], Optional[Dict]]:
        """
        Get task results.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Tuple of (results_list, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/results", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []), data
            else:
                return None, {"error": f"Get results failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def cancel_task(self, token: str, task_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Cancel a running task.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/cancel", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def restart_task(self, token: str, task_id: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Restart a task (creates new task).

        Args:
            token: JWT authentication token
            task_id: Task ID to restart

        Returns:
            Tuple of (new_task_id, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/restart", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                # Response is array of ObjectIDs
                task_ids = data.get("data", [])
                new_task_id = task_ids[0] if task_ids and len(task_ids) > 0 else None
                return new_task_id, data
            else:
                return None, {"error": f"Restart task failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def list_tasks(self, token: str, spider_id: Optional[str] = None) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List tasks, optionally filtered by spider.

        Args:
            token: JWT authentication token
            spider_id: Optional spider ID to filter tasks

        Returns:
            Tuple of (tasks_list, response_data)
        """
        try:
            params = {}
            if spider_id:
                params["spider_id"] = spider_id

            response = requests.get(
                f"{self.base_url}/tasks", headers={"Authorization": f"Bearer {token}"}, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []), data
            else:
                return None, {"error": f"List tasks failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}

    def delete_task(self, token: str, task_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a task.

        Args:
            token: JWT authentication token
            task_id: Task ID

        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def update_task(self, token: str, task_id: str, updates: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Update task (partial update).

        Args:
            token: JWT authentication token
            task_id: Task ID
            updates: Dictionary of fields to update

        Returns:
            Tuple of (updated_task, response_data)
        """
        try:
            response = requests.patch(
                f"{self.base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": updates},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {
                    "error": f"Update task failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def replace_task(self, token: str, task_id: str, task_data: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Replace task (full update).

        Args:
            token: JWT authentication token
            task_id: Task ID
            task_data: Full task data object

        Returns:
            Tuple of (replaced_task, response_data)
        """
        try:
            response = requests.put(
                f"{self.base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": task_data},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data"), data
            else:
                return None, {
                    "error": f"Replace task failed with status {response.status_code}",
                    "response": response.text,
                }

        except Exception as e:
            return None, {"error": str(e)}

    def batch_update_tasks(self, token: str, task_ids: List[str], updates: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Batch update multiple tasks.

        Args:
            token: JWT authentication token
            task_ids: List of task IDs
            updates: Dictionary of fields to update

        Returns:
            Tuple of (success, response_data)
        """
        try:
            payload = {
                "ids": task_ids,
                "update": updates,  # Changed from "data" to "update" per OpenAPI spec
            }

            response = requests.patch(
                f"{self.base_url}/tasks",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10,
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def delete_tasks(self, token: str, task_ids: List[str]) -> Tuple[bool, Optional[Dict]]:
        """
        Delete multiple tasks.

        Args:
            token: JWT authentication token
            task_ids: List of task IDs

        Returns:
            Tuple of (success, response_data)
        """
        try:
            # DELETE endpoint expects JSON body with ids array
            response = requests.delete(
                f"{self.base_url}/tasks",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"ids": task_ids},
                timeout=10,
            )

            return response.status_code == 200, response.json() if response.text else {}

        except Exception as e:
            return False, {"error": str(e)}

    def batch_delete_tasks(self, token: str, task_ids: List[str]) -> bool:
        """
        Batch delete tasks (alias for delete_tasks).

        Args:
            token: JWT authentication token
            task_ids: List of task IDs to delete

        Returns:
            True if deletion request succeeded
        """
        success, _ = self.delete_tasks(token, task_ids)
        return success

    def list_tasks_paginated(
        self, token: str, page: int = 1, size: int = 10, filter_dict: Optional[Dict] = None, sort: str = "-_id"
    ) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List tasks with pagination, filtering, and sorting.

        Args:
            token: JWT authentication token
            page: Page number (default: 1)
            size: Page size (default: 10)
            filter_dict: Filter criteria as dictionary
            sort: Sort field (use - prefix for descending)

        Returns:
            Tuple of (tasks_list, response_data with total count)
        """
        try:
            params = {"page": page, "size": size, "sort": sort}

            if filter_dict:
                import json

                params["filter"] = json.dumps(filter_dict)

            response = requests.get(
                f"{self.base_url}/tasks", headers={"Authorization": f"Bearer {token}"}, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", []), data
            else:
                return None, {"error": f"List tasks failed with status {response.status_code}"}

        except Exception as e:
            return None, {"error": str(e)}
