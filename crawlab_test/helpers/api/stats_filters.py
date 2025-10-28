#!/usr/bin/env python3
"""
Stats & Filters API Helper

Provides utilities for interacting with Crawlab's statistics and filter API endpoints.
"""

import logging
import requests
from typing import Dict, Optional, Any


class StatsFiltersAPIHelper:
    """Helper class for stats and filters API operations"""
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize stats/filters API helper
        
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
    
    # Statistics
    
    def get_stats_overview(self) -> Optional[Dict[str, Any]]:
        """
        Get system overview statistics
        
        Returns:
            Overview stats object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/stats/overview",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get stats overview: {e}")
            return None
    
    def get_stats_daily(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get daily statistics
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Daily stats object or None on failure
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
                
            response = requests.get(
                f"{self.base_url}/stats/daily",
                params=params if params else None,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get stats daily: {e}")
            return None
    
    def get_stats_tasks(self) -> Optional[Dict[str, Any]]:
        """
        Get task statistics
        
        Returns:
            Task stats object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/stats/tasks",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get stats tasks: {e}")
            return None
    
    # Filters
    
    def get_filter_options(self, collection: str, filter_query: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get filter options for a collection
        
        Args:
            collection: Collection name (e.g., 'spiders', 'tasks')
            filter_query: Optional filter query
            
        Returns:
            Filter options or None on failure
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query
                
            response = requests.get(
                f"{self.base_url}/filters/{collection}",
                params=params if params else None,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get filter options: {e}")
            return None
    
    def get_filter_options_with_value(self, collection: str, value: str, 
                                       filter_query: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get filter options with value filter
        
        Args:
            collection: Collection name
            value: Value to filter by
            filter_query: Optional filter query
            
        Returns:
            Filter options or None on failure
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query
                
            response = requests.get(
                f"{self.base_url}/filters/{collection}/{value}",
                params=params if params else None,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get filter options with value: {e}")
            return None
    
    def get_filter_options_with_label(self, collection: str, value: str, label: str,
                                       filter_query: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get filter options with value and label
        
        Args:
            collection: Collection name
            value: Value to filter by
            label: Label to filter by
            filter_query: Optional filter query
            
        Returns:
            Filter options or None on failure
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query
                
            response = requests.get(
                f"{self.base_url}/filters/{collection}/{value}/{label}",
                params=params if params else None,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get filter options with label: {e}")
            return None
