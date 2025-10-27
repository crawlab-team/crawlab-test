"""
Schedule Helper Module

Provides reusable functions for Crawlab schedule operations.
"""

import os
import requests
from typing import Dict, Optional, Tuple, List


class ScheduleHelper:
    """Helper class for schedule operations."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize schedule helper.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    def create_schedule(self, token: str, spider_id: str, name: str, 
                       cron: str, enabled: bool = True, **kwargs) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Create a new schedule.
        
        Args:
            token: JWT authentication token
            spider_id: Spider ID to schedule
            name: Schedule name
            cron: Cron expression (e.g., "0 0 * * *")
            enabled: Whether schedule is enabled (default: True)
            **kwargs: Additional schedule parameters (cmd, mode, priority, etc.)
            
        Returns:
            Tuple of (schedule_id, response_data)
        """
        try:
            payload = {
                "spider_id": spider_id,
                "name": name,
                "cron": cron,
                "enabled": enabled,
                **kwargs
            }
            
            response = requests.post(
                f"{self.base_url}/schedules",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": payload},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                schedule = data.get('data', {})
                return schedule.get('_id'), data
            else:
                return None, {"error": f"Schedule creation failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_schedule(self, token: str, schedule_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get schedule details by ID.
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            
        Returns:
            Tuple of (schedule_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get schedule failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def list_schedules(self, token: str, spider_id: Optional[str] = None,
                      page: int = 1, size: int = 10) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List schedules with optional filtering.
        
        Args:
            token: JWT authentication token
            spider_id: Optional spider ID to filter schedules
            page: Page number (default: 1)
            size: Page size (default: 10)
            
        Returns:
            Tuple of (schedules_list, response_data)
        """
        try:
            params = {"page": page, "size": size}
            
            if spider_id:
                import json
                params["filter"] = json.dumps({"spider_id": spider_id})
            
            response = requests.get(
                f"{self.base_url}/schedules",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []), data
            else:
                return None, {"error": f"List schedules failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def update_schedule(self, token: str, schedule_id: str, updates: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Update schedule (partial update).
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (updated_schedule, response_data)
        """
        try:
            response = requests.patch(
                f"{self.base_url}/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": updates},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Update schedule failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def replace_schedule(self, token: str, schedule_id: str, schedule_data: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Replace schedule (full update).
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            schedule_data: Full schedule data object
            
        Returns:
            Tuple of (replaced_schedule, response_data)
        """
        try:
            response = requests.put(
                f"{self.base_url}/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": schedule_data},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Replace schedule failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def delete_schedule(self, token: str, schedule_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Delete a schedule.
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def enable_schedule(self, token: str, schedule_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Enable a schedule.
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/schedules/{schedule_id}/enable",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def disable_schedule(self, token: str, schedule_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Disable a schedule.
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/schedules/{schedule_id}/disable",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def run_schedule(self, token: str, schedule_id: str, **kwargs) -> Tuple[Optional[List[str]], Optional[Dict]]:
        """
        Run a schedule immediately (creates task).
        
        Args:
            token: JWT authentication token
            schedule_id: Schedule ID
            **kwargs: Optional parameters (cmd, mode, priority, node_ids, param)
            
        Returns:
            Tuple of (task_ids, response_data)
        """
        try:
            # Build request body with optional parameters
            payload = {}
            if kwargs:
                # Only include valid fields
                valid_fields = ['cmd', 'mode', 'priority', 'node_ids', 'param']
                payload = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            response = requests.post(
                f"{self.base_url}/schedules/{schedule_id}/run",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload if payload else {},  # Send empty object if no params
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                task_ids = data.get('data', [])
                # Handle both array and single object responses
                if isinstance(task_ids, list):
                    return task_ids, data
                elif isinstance(task_ids, str):
                    return [task_ids], data
                else:
                    return [task_ids] if task_ids else [], data
            else:
                return None, {"error": f"Run schedule failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def batch_update_schedules(self, token: str, schedule_ids: List[str], updates: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Batch update multiple schedules.
        
        Args:
            token: JWT authentication token
            schedule_ids: List of schedule IDs
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            payload = {
                "ids": schedule_ids,
                "update": updates
            }
            
            response = requests.patch(
                f"{self.base_url}/schedules",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def delete_schedules(self, token: str, schedule_ids: List[str]) -> Tuple[bool, Optional[Dict]]:
        """
        Delete multiple schedules.
        
        Args:
            token: JWT authentication token
            schedule_ids: List of schedule IDs
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/schedules",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"ids": schedule_ids},
                timeout=10
            )
            
            return response.status_code == 200, response.json() if response.text else {}
            
        except Exception as e:
            return False, {"error": str(e)}
