"""
Node Helper Module

Provides reusable functions for Crawlab node operations.
"""

import os
import requests
from typing import Dict, Optional, Tuple, List


class NodeHelper:
    """Helper class for node operations."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize node helper.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    def list_nodes(self, token: str, page: int = 1, size: int = 10,
                   filter_dict: Optional[Dict] = None) -> Tuple[Optional[List], Optional[Dict]]:
        """
        List nodes with optional filtering.
        
        Args:
            token: JWT authentication token
            page: Page number (default: 1)
            size: Page size (default: 10)
            filter_dict: Optional filter criteria as dictionary
            
        Returns:
            Tuple of (nodes_list, response_data)
        """
        try:
            params = {"page": page, "size": size}
            
            if filter_dict:
                import json
                params["filter"] = json.dumps(filter_dict)
            
            response = requests.get(
                f"{self.base_url}/nodes",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []), data
            else:
                return None, {"error": f"List nodes failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_node(self, token: str, node_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get node details by ID.
        
        Args:
            token: JWT authentication token
            node_id: Node ID
            
        Returns:
            Tuple of (node_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/nodes/{node_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get node failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def update_node(self, token: str, node_id: str, updates: Dict) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Update node (partial update).
        
        Args:
            token: JWT authentication token
            node_id: Node ID
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (updated_node, response_data)
        """
        try:
            response = requests.patch(
                f"{self.base_url}/nodes/{node_id}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"data": updates},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Update node failed with status {response.status_code}", "response": response.text}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_node_metrics(self, token: str, page: int = 1, size: int = 10) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get metrics for all nodes.
        
        Args:
            token: JWT authentication token
            page: Page number (default: 1)
            size: Page size (default: 10)
            
        Returns:
            Tuple of (metrics_dict, response_data)
            metrics_dict maps node_id -> metric data
        """
        try:
            params = {"page": page, "size": size}
            
            response = requests.get(
                f"{self.base_url}/nodes/metrics",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}), data
            else:
                return None, {"error": f"Get node metrics failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_node_current_metrics(self, token: str, node_id: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get current metrics for a specific node.
        
        Args:
            token: JWT authentication token
            node_id: Node ID
            
        Returns:
            Tuple of (metrics_data, response_data)
        """
        try:
            response = requests.get(
                f"{self.base_url}/nodes/{node_id}/metrics/current",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data'), data
            else:
                return None, {"error": f"Get node current metrics failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_node_time_range_metrics(self, token: str, node_id: str, 
                                    start_time: Optional[str] = None,
                                    end_time: Optional[str] = None) -> Tuple[Optional[List], Optional[Dict]]:
        """
        Get time-range metrics for a specific node.
        
        Args:
            token: JWT authentication token
            node_id: Node ID
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            
        Returns:
            Tuple of (metrics_list, response_data)
        """
        try:
            params = {}
            if start_time:
                params['start_time'] = start_time
            if end_time:
                params['end_time'] = end_time
            
            response = requests.get(
                f"{self.base_url}/nodes/{node_id}/metrics/time-range",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []), data
            else:
                return None, {"error": f"Get node time-range metrics failed with status {response.status_code}"}
                
        except Exception as e:
            return None, {"error": str(e)}
    
    def get_master_node(self, token: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get the master node.
        
        Args:
            token: JWT authentication token
            
        Returns:
            Tuple of (master_node_data, response_data)
        """
        nodes, response = self.list_nodes(token, size=100)
        
        if nodes:
            master_nodes = [n for n in nodes if n.get('is_master')]
            if master_nodes:
                return master_nodes[0], response
            else:
                return None, {"error": "No master node found"}
        else:
            return None, response
    
    def get_worker_nodes(self, token: str) -> Tuple[Optional[List], Optional[Dict]]:
        """
        Get all worker nodes (non-master nodes).
        
        Args:
            token: JWT authentication token
            
        Returns:
            Tuple of (worker_nodes_list, response_data)
        """
        nodes, response = self.list_nodes(token, size=100)
        
        if nodes:
            worker_nodes = [n for n in nodes if not n.get('is_master')]
            return worker_nodes, response
        else:
            return None, response
