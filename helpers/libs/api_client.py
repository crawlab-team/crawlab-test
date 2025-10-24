#!/usr/bin/env python3
"""
API client for Crawlab REST API
Provides methods to interact with Crawlab master node for testing purposes.
Supports both local and Docker-based deployments via auto-detection.
"""

import os
import time
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from bson import ObjectId

try:
    from .docker_utils import docker_utils
except ImportError:
    # Fallback if docker_utils is not available
    docker_utils = None

class CrawlabAPIClient:
    def __init__(self, base_url: str = None, api_token: str = None, auto_detect_docker: bool = True):
        self.base_url = base_url or self._detect_crawlab_url(auto_detect_docker)
        self.api_token = api_token or os.getenv('CRAWLAB_API_TOKEN')
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_docker_env = self._is_docker_environment()
        
        # Set up default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if self.api_token:
            self.session.headers['Authorization'] = f'Bearer {self.api_token}'
            
        self.logger.info(f"Initialized API client for {self.base_url} (Docker: {self.is_docker_env})")
    
    @property
    def docker(self):
        """Access to Docker utilities (if available)"""
        return docker_utils
    
    def _detect_crawlab_url(self, auto_detect: bool = True) -> str:
        """Detect the Crawlab master URL based on environment"""
        # Check explicit environment variable first
        if os.getenv('CRAWLAB_MASTER_URL'):
            return os.getenv('CRAWLAB_MASTER_URL').rstrip('/')
        
        if not auto_detect:
            return 'http://localhost:8080'
        
        # Try to detect Docker environment using Docker utils
        if docker_utils and docker_utils.is_available():
            docker_url = docker_utils.detect_crawlab_api_url()
            if docker_url and self._test_connectivity(docker_url):
                self.logger.info(f"Detected Docker Crawlab at {docker_url}")
                return docker_url
        
        # Default to localhost
        return 'http://localhost:8080'
    
    def _is_docker_environment(self) -> bool:
        """Check if we're running in a Docker environment"""
        if docker_utils:
            return docker_utils.is_running_in_container() or bool(docker_utils.find_crawlab_containers())
        return False
    
    def _test_connectivity(self, url: str, timeout: int = 2) -> bool:
        """Test if a URL is accessible"""
        try:
            response = requests.get(f"{url}/api/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def login(self, username: str = "admin", password: str = "admin") -> str:
        """Login and retrieve API token using admin credentials"""
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            # Make login request without authentication
            url = f"{self.base_url}/api/login"
            response = self.session.post(url, json=login_data)
            
            self.logger.debug(f"POST /login -> {response.status_code}")
            
            if response.status_code != 200:
                self.logger.error(f"Login failed: {response.status_code} - {response.text}")
                raise Exception(f"Login failed with status {response.status_code}")
            
            data = response.json()
            if not data.get('data'):
                raise Exception("Login response does not contain a token")
            
            # Set the token for future requests
            self.api_token = data['data']
            self.session.headers['Authorization'] = f'Bearer {self.api_token}'
            
            self.logger.info(f"Successfully logged in as {username}")
            return self.api_token
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise
    
    def ensure_authenticated(self, username: str = "admin", password: str = "admin") -> str:
        """Ensure we have a valid API token, login if necessary"""
        if not self.api_token:
            return self.login(username, password)
        return self.api_token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"{method} {endpoint} -> {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {method} {endpoint} - {e}")
            raise
    
    def _get_json_response(self, response: requests.Response) -> Dict[str, Any]:
        """Extract JSON data from response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {response.status_code} - {response.text}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid JSON response: {response.text}")
            raise
    
    # Node operations
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get list of all nodes"""
        response = self._request('GET', '/nodes')
        data = self._get_json_response(response)
        return data.get('data', [])
    
    def get_node_by_id(self, node_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        response = self._request('GET', f'/nodes/{str(node_id)}')
        if response.status_code == 404:
            return None
        data = self._get_json_response(response)
        return data.get('data')
    
    def get_node_by_key(self, node_key: str) -> Optional[Dict[str, Any]]:
        """Get node by key"""
        nodes = self.get_nodes()
        for node in nodes:
            if node.get('key') == node_key:
                return node
        return None
    
    # Task operations
    def get_tasks(self, **params) -> List[Dict[str, Any]]:
        """Get list of tasks with optional filtering"""
        response = self._request('GET', '/tasks', params=params)
        data = self._get_json_response(response)
        return data.get('data', [])
    
    def get_task_by_id(self, task_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        response = self._request('GET', f'/tasks/{str(task_id)}')
        if response.status_code == 404:
            return None
        data = self._get_json_response(response)
        return data.get('data')
    
    def run_task(self, task_data: Dict[str, Any]) -> List[str]:
        """
        Run a task (creates and schedules it).
        
        This calls POST /tasks/run which:
        1. Validates the spider_id
        2. Schedules the task via spider admin service
        3. Returns a list of created task IDs
        
        Args:
            task_data: Must include 'spider_id' and optionally:
                - mode: 'random' | 'all-nodes' | 'selected-nodes'
                - node_ids: List of node IDs (for 'selected-nodes' mode)
                - cmd: Command to run
                - param: Parameters
                - priority: Task priority
        
        Returns:
            List of task IDs (usually one, but can be multiple for 'all-nodes' mode)
        """
        response = self._request('POST', '/tasks/run', json=task_data)
        data = self._get_json_response(response)
        task_ids = data.get('data', [])
        # Handle both list and single ID responses
        if isinstance(task_ids, list):
            return task_ids
        return [task_ids] if task_ids else []
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method - deprecated. Use run_task() instead.
        Creates and runs a task, returning the first task created.
        """
        task_ids = self.run_task(task_data)
        if not task_ids:
            raise Exception("No task IDs returned from run_task")
        # Get the first task
        return self.get_task_by_id(task_ids[0])
    
    def update_task(self, task_id: Union[str, ObjectId], task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        response = self._request('PUT', f'/tasks/{str(task_id)}', json=task_data)
        data = self._get_json_response(response)
        return data.get('data')
    
    def cancel_task(self, task_id: Union[str, ObjectId], force: bool = False) -> bool:
        """Cancel a running task"""
        response = self._request('POST', f'/tasks/{str(task_id)}/cancel', 
                               json={'force': force})
        return response.status_code == 200
    
    def restart_task(self, task_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Restart a task"""
        response = self._request('POST', f'/tasks/{str(task_id)}/restart')
        data = self._get_json_response(response)
        return data.get('data')
    
    def delete_task(self, task_id: Union[str, ObjectId]) -> bool:
        """Delete a task"""
        response = self._request('DELETE', f'/tasks/{str(task_id)}')
        return response.status_code == 200
    
    # Task reconciliation operations
    def force_reconcile_task(self, task_id: Union[str, ObjectId]) -> bool:
        """Force reconciliation of a specific task"""
        response = self._request('POST', f'/tasks/{str(task_id)}/reconcile')
        return response.status_code == 200
    
    def get_reconciliation_status(self) -> Dict[str, Any]:
        """Get status of the reconciliation service"""
        response = self._request('GET', '/system/reconciliation/status')
        data = self._get_json_response(response)
        return data.get('data', {})
    
    def trigger_reconciliation(self) -> bool:
        """Trigger manual reconciliation cycle"""
        response = self._request('POST', '/system/reconciliation/trigger')
        return response.status_code == 200
    
    # Spider operations
    def get_spiders(self) -> List[Dict[str, Any]]:
        """Get list of all spiders"""
        response = self._request('GET', '/spiders')
        data = self._get_json_response(response)
        return data.get('data', [])
    
    def get_spider_by_id(self, spider_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """Get spider by ID"""
        response = self._request('GET', f'/spiders/{str(spider_id)}')
        if response.status_code == 404:
            return None
        data = self._get_json_response(response)
        return data.get('data')
    
    def create_spider(self, spider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new spider"""
        response = self._request('POST', '/spiders', json=spider_data)
        data = self._get_json_response(response)
        return data.get('data')
    
    def run_spider(self, spider_id: Union[str, ObjectId], **kwargs) -> Dict[str, Any]:
        """Run a spider"""
        run_data = {
            'mode': kwargs.get('mode', 'all-nodes'),
            'node_ids': kwargs.get('node_ids', []),
            'param': kwargs.get('param', ''),
            'priority': kwargs.get('priority', 5),
        }
        response = self._request('POST', f'/spiders/{str(spider_id)}/run', json=run_data)
        data = self._get_json_response(response)
        return data.get('data')
    
    # System operations
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        response = self._request('GET', '/system-info')
        data = self._get_json_response(response)
        return data.get('data', {})
    
    def ping(self) -> bool:
        """Ping the API to check connectivity"""
        try:
            response = self._request('GET', '/health')
            return response.status_code == 200
        except:
            return False
    
    # Helper methods
    def wait_for_task_status(self, task_id: Union[str, ObjectId], expected_status: str, 
                           timeout: int = 60, poll_interval: float = 2.0) -> bool:
        """Wait for a task to reach the expected status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task_by_id(task_id)
            if task and task.get('status') == expected_status:
                return True
            time.sleep(poll_interval)
        
        return False
    
    def wait_for_node_status(self, node_key: str, expected_status: str, 
                           timeout: int = 60, poll_interval: float = 2.0) -> bool:
        """Wait for a node to reach the expected status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            node = self.get_node_by_key(node_key)
            if node and node.get('status') == expected_status:
                return True
            time.sleep(poll_interval)
        
        return False