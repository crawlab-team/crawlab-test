"""
Cleanup Helper Module

Provides utilities for cleaning up test data.
"""

import os
import requests
from typing import Dict, List, Optional


class CleanupHelper:
    """Helper class for test cleanup operations."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        """
        Initialize cleanup helper.
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        self.created_resources = {
            'spiders': [],
            'tasks': [],
            'users': [],
            'tokens': [],
            'schedules': [],
            'databases': [],
            'gits': [],
            'projects': [],
            'environments': [],
            'notifications': []
        }
    
    def track_spider(self, spider_id: str):
        """Track a spider for cleanup."""
        if spider_id and spider_id not in self.created_resources['spiders']:
            self.created_resources['spiders'].append(spider_id)
    
    def track_task(self, task_id: str):
        """Track a task for cleanup."""
        if task_id and task_id not in self.created_resources['tasks']:
            self.created_resources['tasks'].append(task_id)
    
    def track_user(self, user_id: str):
        """Track a user for cleanup."""
        if user_id and user_id not in self.created_resources['users']:
            self.created_resources['users'].append(user_id)
    
    def track_token(self, token_id: str):
        """Track a token for cleanup."""
        if token_id and token_id not in self.created_resources['tokens']:
            self.created_resources['tokens'].append(token_id)
    
    def track_schedule(self, schedule_id: str):
        """Track a schedule for cleanup."""
        if schedule_id and schedule_id not in self.created_resources['schedules']:
            self.created_resources['schedules'].append(schedule_id)
    
    def track_database(self, database_id: str):
        """Track a database for cleanup."""
        if database_id and database_id not in self.created_resources['databases']:
            self.created_resources['databases'].append(database_id)
    
    def track_git(self, git_id: str):
        """Track a git repo for cleanup."""
        if git_id and git_id not in self.created_resources['gits']:
            self.created_resources['gits'].append(git_id)
    
    def track_project(self, project_id: str):
        """Track a project for cleanup."""
        if project_id and project_id not in self.created_resources['projects']:
            self.created_resources['projects'].append(project_id)
    
    def delete_spider(self, token: str, spider_id: str) -> bool:
        """Delete a spider."""
        try:
            response = requests.delete(
                f"{self.base_url}/spiders/{spider_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_task(self, token: str, task_id: str) -> bool:
        """Delete a task."""
        try:
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_user(self, token: str, user_id: str) -> bool:
        """Delete a user."""
        try:
            response = requests.delete(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_token(self, token: str, token_id: str) -> bool:
        """Delete a token."""
        try:
            response = requests.delete(
                f"{self.base_url}/tokens/{token_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_schedule(self, token: str, schedule_id: str) -> bool:
        """Delete a schedule."""
        try:
            response = requests.delete(
                f"{self.base_url}/schedules/{schedule_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_database(self, token: str, database_id: str) -> bool:
        """Delete a database."""
        try:
            response = requests.delete(
                f"{self.base_url}/databases/{database_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_git(self, token: str, git_id: str) -> bool:
        """Delete a git repo."""
        try:
            response = requests.delete(
                f"{self.base_url}/gits/{git_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def delete_project(self, token: str, project_id: str) -> bool:
        """Delete a project."""
        try:
            response = requests.delete(
                f"{self.base_url}/projects/{project_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def cleanup_all(self, token: str) -> Dict[str, int]:
        """
        Clean up all tracked resources.
        
        Args:
            token: JWT authentication token
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            'spiders': 0,
            'tasks': 0,
            'users': 0,
            'tokens': 0,
            'schedules': 0,
            'databases': 0,
            'gits': 0,
            'projects': 0,
            'total': 0
        }
        
        # Clean up in reverse dependency order
        
        # Tasks first (depend on spiders)
        for task_id in self.created_resources['tasks']:
            if self.delete_task(token, task_id):
                stats['tasks'] += 1
        
        # Schedules (depend on spiders)
        for schedule_id in self.created_resources['schedules']:
            if self.delete_schedule(token, schedule_id):
                stats['schedules'] += 1
        
        # Spiders
        for spider_id in self.created_resources['spiders']:
            if self.delete_spider(token, spider_id):
                stats['spiders'] += 1
        
        # Users and tokens
        for user_id in self.created_resources['users']:
            if self.delete_user(token, user_id):
                stats['users'] += 1
        
        for token_id in self.created_resources['tokens']:
            if self.delete_token(token, token_id):
                stats['tokens'] += 1
        
        # Databases
        for database_id in self.created_resources['databases']:
            if self.delete_database(token, database_id):
                stats['databases'] += 1
        
        # Git repos
        for git_id in self.created_resources['gits']:
            if self.delete_git(token, git_id):
                stats['gits'] += 1
        
        # Projects
        for project_id in self.created_resources['projects']:
            if self.delete_project(token, project_id):
                stats['projects'] += 1
        
        stats['total'] = sum(v for k, v in stats.items() if k != 'total')
        
        return stats
    
    def reset(self):
        """Reset tracked resources."""
        for key in self.created_resources:
            self.created_resources[key] = []
