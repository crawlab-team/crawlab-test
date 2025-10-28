#!/usr/bin/env python3
"""
Notification API Helper

Provides utilities for interacting with Crawlab's notification API endpoints.
Supports channels, alerts, settings, and notification requests.
"""

import logging
import requests
from typing import Dict, List, Optional, Any


class NotificationAPIHelper:
    """Helper class for notification API operations"""
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize notification API helper
        
        Args:
            base_url: API base URL (default: http://localhost:8080/api)
            token: Authentication token
        """
        self.base_url = (base_url or "http://localhost:8080/api").rstrip('/')
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    # Notification Channels
    
    def create_channel(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a notification channel
        
        Args:
            data: Channel configuration including:
                - name: Channel name
                - type: Channel type (email, webhook, dingtalk, slack, etc.)
                - config: Type-specific configuration
                
        Returns:
            Created channel object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/channels",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to create channel: {e}")
            return None
    
    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel details by ID
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Channel object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/channels/{channel_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get channel: {e}")
            return None
    
    def list_channels(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all channels
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/channels",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list channels: {e}")
            return None
    
    def update_channel(self, channel_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update channel configuration
        
        Args:
            channel_id: Channel ID
            data: Updated configuration
            
        Returns:
            Updated channel object or None on failure
        """
        try:
            response = requests.put(
                f"{self.base_url}/notifications/channels/{channel_id}",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to update channel: {e}")
            return None
    
    def delete_channel(self, channel_id: str) -> bool:
        """
        Delete a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/notifications/channels/{channel_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete channel: {e}")
            return False
    
    def test_channel(self, channel_id: str) -> bool:
        """
        Test channel connection
        
        Args:
            channel_id: Channel ID
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/channels/{channel_id}/test",
                headers=self._get_headers(),
                timeout=30  # Channel tests may take longer
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to test channel: {e}")
            return False
    
    def batch_update_channels(self, channel_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple channels
        
        Args:
            channel_ids: List of channel IDs
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/notifications/channels",
                json={"ids": channel_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update channels: {e}")
            return False
    
    # Notification Alerts
    
    def create_alert(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a notification alert
        
        Args:
            data: Alert configuration including:
                - name: Alert name
                - type: Alert type (task_error, task_timeout, etc.)
                - conditions: Trigger conditions
                
        Returns:
            Created alert object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/alerts",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            return None
    
    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get alert details by ID
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/alerts/{alert_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get alert: {e}")
            return None
    
    def list_alerts(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all alerts
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/alerts",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list alerts: {e}")
            return None
    
    def update_alert(self, alert_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update alert configuration
        
        Args:
            alert_id: Alert ID
            data: Updated configuration
            
        Returns:
            Updated alert object or None on failure
        """
        try:
            response = requests.put(
                f"{self.base_url}/notifications/alerts/{alert_id}",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to update alert: {e}")
            return None
    
    def delete_alert(self, alert_id: str) -> bool:
        """
        Delete an alert
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/notifications/alerts/{alert_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete alert: {e}")
            return False
    
    def batch_update_alerts(self, alert_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple alerts
        
        Args:
            alert_ids: List of alert IDs
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/notifications/alerts",
                json={"ids": alert_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update alerts: {e}")
            return False
    
    # Notification Settings
    
    def create_setting(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a notification setting (links alert to channel)
        
        Args:
            data: Setting configuration including:
                - name: Setting name
                - alert_id: Alert ID
                - channel_id: Channel ID
                - enabled: Whether setting is enabled
                
        Returns:
            Created setting object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/settings",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to create setting: {e}")
            return None
    
    def get_setting(self, setting_id: str) -> Optional[Dict[str, Any]]:
        """
        Get setting details by ID
        
        Args:
            setting_id: Setting ID
            
        Returns:
            Setting object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/settings/{setting_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get setting: {e}")
            return None
    
    def list_settings(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all settings
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/settings",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list settings: {e}")
            return None
    
    def update_setting(self, setting_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update setting configuration
        
        Args:
            setting_id: Setting ID
            data: Updated configuration
            
        Returns:
            Updated setting object or None on failure
        """
        try:
            response = requests.put(
                f"{self.base_url}/notifications/settings/{setting_id}",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to update setting: {e}")
            return None
    
    def delete_setting(self, setting_id: str) -> bool:
        """
        Delete a setting
        
        Args:
            setting_id: Setting ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/notifications/settings/{setting_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete setting: {e}")
            return False
    
    def enable_setting(self, setting_id: str) -> bool:
        """
        Enable a notification setting
        
        Args:
            setting_id: Setting ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/settings/{setting_id}/enable",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable setting: {e}")
            return False
    
    def disable_setting(self, setting_id: str) -> bool:
        """
        Disable a notification setting
        
        Args:
            setting_id: Setting ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/settings/{setting_id}/disable",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to disable setting: {e}")
            return False
    
    def get_setting_requests(self, setting_id: str, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get notification requests for a setting
        
        Args:
            setting_id: Setting ID
            page: Page number
            size: Page size
            
        Returns:
            List of notification requests or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/settings/{setting_id}/requests",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get setting requests: {e}")
            return None
    
    def batch_update_settings(self, setting_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple settings
        
        Args:
            setting_ids: List of setting IDs
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/notifications/settings",
                json={"ids": setting_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update settings: {e}")
            return False
    
    # Notification Requests
    
    def create_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a notification request (manual trigger)
        
        Args:
            data: Request data including:
                - setting_id: Setting ID
                - message: Notification message
                
        Returns:
            Created request object or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/notifications/requests",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to create request: {e}")
            return None
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get request details by ID
        
        Args:
            request_id: Request ID
            
        Returns:
            Request object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/requests/{request_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get request: {e}")
            return None
    
    def list_requests(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all notification requests
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/notifications/requests",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list requests: {e}")
            return None
    
    def delete_request(self, request_id: str) -> bool:
        """
        Delete a notification request
        
        Args:
            request_id: Request ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/notifications/requests/{request_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete request: {e}")
            return False
