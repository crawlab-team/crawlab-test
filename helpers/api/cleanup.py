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
    
    def cleanup_all(self, token: str, spider_helper=None, task_helper=None, 
                    user_helper=None, schedule_helper=None, database_helper=None,
                    git_helper=None, project_helper=None) -> bool:
        """
        Clean up all tracked resources.
        
        Args:
            token: JWT authentication token
            spider_helper: Optional spider helper for batch deletion
            task_helper: Optional task helper for batch deletion
            user_helper: Optional user helper for batch deletion
            schedule_helper: Optional schedule helper for batch deletion
            database_helper: Optional database helper for batch deletion
            git_helper: Optional git helper for batch deletion
            project_helper: Optional project helper for batch deletion
            
        Returns:
            True if cleanup successful
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
        
        # Tasks first (depend on spiders) - prefer batch deletion
        if task_helper and len(self.created_resources['tasks']) > 1:
            if task_helper.batch_delete_tasks(token, self.created_resources['tasks']):
                stats['tasks'] = len(self.created_resources['tasks'])
            else:
                # Fallback to individual deletion
                for task_id in self.created_resources['tasks']:
                    if self.delete_task(token, task_id):
                        stats['tasks'] += 1
        else:
            for task_id in self.created_resources['tasks']:
                if self.delete_task(token, task_id):
                    stats['tasks'] += 1
        
        # Schedules (depend on spiders) - prefer batch deletion
        if schedule_helper and len(self.created_resources['schedules']) > 1:
            if schedule_helper.batch_delete_schedules(token, self.created_resources['schedules']):
                stats['schedules'] = len(self.created_resources['schedules'])
            else:
                for schedule_id in self.created_resources['schedules']:
                    if self.delete_schedule(token, schedule_id):
                        stats['schedules'] += 1
        else:
            for schedule_id in self.created_resources['schedules']:
                if self.delete_schedule(token, schedule_id):
                    stats['schedules'] += 1
        
        # Spiders - prefer batch deletion
        if spider_helper and len(self.created_resources['spiders']) > 1:
            if spider_helper.batch_delete_spiders(token, self.created_resources['spiders']):
                stats['spiders'] = len(self.created_resources['spiders'])
            else:
                for spider_id in self.created_resources['spiders']:
                    if self.delete_spider(token, spider_id):
                        stats['spiders'] += 1
        else:
            for spider_id in self.created_resources['spiders']:
                if self.delete_spider(token, spider_id):
                    stats['spiders'] += 1
        
        # Users and tokens - prefer batch deletion
        if user_helper and len(self.created_resources['users']) > 1:
            if user_helper.batch_delete_users(token, self.created_resources['users']):
                stats['users'] = len(self.created_resources['users'])
            else:
                for user_id in self.created_resources['users']:
                    if self.delete_user(token, user_id):
                        stats['users'] += 1
        else:
            for user_id in self.created_resources['users']:
                if self.delete_user(token, user_id):
                    stats['users'] += 1
        
        for token_id in self.created_resources['tokens']:
            if self.delete_token(token, token_id):
                stats['tokens'] += 1
        
        # Databases - prefer batch deletion
        if database_helper and len(self.created_resources['databases']) > 1:
            if database_helper.batch_delete_databases(token, self.created_resources['databases']):
                stats['databases'] = len(self.created_resources['databases'])
            else:
                for database_id in self.created_resources['databases']:
                    if self.delete_database(token, database_id):
                        stats['databases'] += 1
        else:
            for database_id in self.created_resources['databases']:
                if self.delete_database(token, database_id):
                    stats['databases'] += 1
        
        # Git repos - prefer batch deletion
        if git_helper and len(self.created_resources['gits']) > 1:
            if git_helper.batch_delete_gits(token, self.created_resources['gits']):
                stats['gits'] = len(self.created_resources['gits'])
            else:
                for git_id in self.created_resources['gits']:
                    if self.delete_git(token, git_id):
                        stats['gits'] += 1
        else:
            for git_id in self.created_resources['gits']:
                if self.delete_git(token, git_id):
                    stats['gits'] += 1
        
        # Projects - prefer batch deletion
        if project_helper and len(self.created_resources['projects']) > 1:
            if project_helper.batch_delete_projects(token, self.created_resources['projects']):
                stats['projects'] = len(self.created_resources['projects'])
            else:
                for project_id in self.created_resources['projects']:
                    if self.delete_project(token, project_id):
                        stats['projects'] += 1
        else:
            for project_id in self.created_resources['projects']:
                if self.delete_project(token, project_id):
                    stats['projects'] += 1
        
        stats['total'] = sum(v for k, v in stats.items() if k != 'total')
        
        print(f"Cleanup stats: {stats['total']} resources deleted")
        for resource_type, count in stats.items():
            if resource_type != 'total' and count > 0:
                print(f"  - {resource_type}: {count}")
        
        return stats['total'] == sum(len(v) for v in self.created_resources.values())
    
    def reset(self):
        """Reset tracked resources."""
        for key in self.created_resources:
            self.created_resources[key] = []
