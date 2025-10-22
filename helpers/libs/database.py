#!/usr/bin/env python3
"""
Database helper utilities for testing
Provides MongoDB access and common database operations for test scenarios.
"""

import os
import time
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
import logging

# Task status constants - must match Go constants
TASK_STATUS_PENDING = "pending"
TASK_STATUS_ASSIGNED = "assigned"  
TASK_STATUS_RUNNING = "running"
TASK_STATUS_FINISHED = "finished"
TASK_STATUS_ERROR = "error"
TASK_STATUS_CANCELLED = "cancelled"
TASK_STATUS_ABNORMAL = "abnormal"
TASK_STATUS_NODE_DISCONNECTED = "node_disconnected"

NODE_STATUS_ONLINE = "online"
NODE_STATUS_OFFLINE = "offline"
NODE_STATUS_UNKNOWN = "unknown"

class DatabaseHelper:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            'CRAWLAB_MONGO_URI', 
            'mongodb://localhost:27017'
        )
        self.database_name = os.getenv('CRAWLAB_MONGO_DATABASE', 'crawlab_test')
        self.client = None
        self.db = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def connect(self) -> Database:
        """Establish database connection"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            self.logger.info(f"Connected to MongoDB: {self.database_name}")
            return self.db
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            
    def get_collection(self, name: str) -> Collection:
        """Get a collection by name"""
        if self.db is None:
            self.connect()
        return self.db[name]
    
    # Task operations
    def create_test_task(self, **kwargs) -> Dict[str, Any]:
        """Create a test task with default values"""
        default_task = {
            "status": TASK_STATUS_PENDING,
            "spider_id": ObjectId(),
            "node_id": ObjectId(),
            "type": "spider",
            "mode": "all-nodes",
            "cmd": "python3 test_spider.py",
            "param": "",
            "priority": 5,
            "created_by": ObjectId(),
            "created_at": time.time(),
            "updated_at": time.time(),
            "error": "",
            "pid": 0,
        }
        default_task.update(kwargs)
        
        tasks_collection = self.get_collection("tasks")
        result = tasks_collection.insert_one(default_task)
        default_task["_id"] = result.inserted_id
        
        self.logger.debug(f"Created test task: {result.inserted_id}")
        return default_task
    
    def get_task_by_id(self, task_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        tasks_collection = self.get_collection("tasks")
        return tasks_collection.find_one({"_id": task_id})
    
    def update_task_status(self, task_id: ObjectId, status: str, error: str = None) -> bool:
        """Update task status"""
        tasks_collection = self.get_collection("tasks")
        update_data = {
            "status": status,
            "updated_at": time.time()
        }
        if error is not None:
            update_data["error"] = error
            
        result = tasks_collection.update_one(
            {"_id": task_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all tasks with specified status"""
        tasks_collection = self.get_collection("tasks")
        return list(tasks_collection.find({"status": status}))
    
    def get_tasks_by_node(self, node_id: ObjectId, status: str = None) -> List[Dict[str, Any]]:
        """Get tasks for a specific node, optionally filtered by status"""
        tasks_collection = self.get_collection("tasks")
        query = {"node_id": node_id}
        if status:
            query["status"] = status
        return list(tasks_collection.find(query))
    
    def count_tasks_by_status(self, status: str) -> int:
        """Count tasks with specified status"""
        tasks_collection = self.get_collection("tasks")
        return tasks_collection.count_documents({"status": status})
    
    def delete_test_tasks(self, task_ids: List[ObjectId] = None) -> int:
        """Delete test tasks. If task_ids is None, deletes all tasks."""
        tasks_collection = self.get_collection("tasks")
        if task_ids:
            result = tasks_collection.delete_many({"_id": {"$in": task_ids}})
        else:
            result = tasks_collection.delete_many({})
        
        self.logger.info(f"Deleted {result.deleted_count} test tasks")
        return result.deleted_count
    
    # Node operations
    def create_test_node(self, **kwargs) -> Dict[str, Any]:
        """Create a test node with default values"""
        default_node = {
            "key": f"test-worker-{int(time.time())}",
            "name": f"Test Worker {int(time.time())}",
            "status": NODE_STATUS_ONLINE,
            "ip": "127.0.0.1",
            "mac": "00:00:00:00:00:00",
            "hostname": "test-worker",
            "available_runners": 4,
            "max_runners": 4,
            "enabled": True,
            "created_at": time.time(),
            "updated_at": time.time(),
            "last_heartbeat_ts": time.time(),
        }
        default_node.update(kwargs)
        
        nodes_collection = self.get_collection("nodes")
        result = nodes_collection.insert_one(default_node)
        default_node["_id"] = result.inserted_id
        
        self.logger.debug(f"Created test node: {result.inserted_id}")
        return default_node
    
    def get_node_by_id(self, node_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        nodes_collection = self.get_collection("nodes")
        return nodes_collection.find_one({"_id": node_id})
    
    def get_node_by_key(self, node_key: str) -> Optional[Dict[str, Any]]:
        """Get node by key"""
        nodes_collection = self.get_collection("nodes")
        return nodes_collection.find_one({"key": node_key})
    
    def update_node_status(self, node_id: ObjectId, status: str) -> bool:
        """Update node status"""
        nodes_collection = self.get_collection("nodes")
        result = nodes_collection.update_one(
            {"_id": node_id},
            {"$set": {
                "status": status,
                "updated_at": time.time(),
                "last_heartbeat_ts": time.time() if status == NODE_STATUS_ONLINE else None
            }}
        )
        return result.modified_count > 0
    
    def get_online_nodes(self) -> List[Dict[str, Any]]:
        """Get all online nodes"""
        nodes_collection = self.get_collection("nodes")
        return list(nodes_collection.find({"status": NODE_STATUS_ONLINE}))
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes regardless of status"""
        nodes_collection = self.get_collection("nodes")
        return list(nodes_collection.find({}))
    
    def delete_test_nodes(self, node_ids: List[ObjectId] = None) -> int:
        """Delete test nodes. If node_ids is None, deletes all nodes."""
        nodes_collection = self.get_collection("nodes")
        if node_ids:
            result = nodes_collection.delete_many({"_id": {"$in": node_ids}})
        else:
            result = nodes_collection.delete_many({})
        
        self.logger.info(f"Deleted {result.deleted_count} test nodes")
        return result.deleted_count
    
    # Spider operations
    def create_test_spider(self, **kwargs) -> Dict[str, Any]:
        """Create a test spider with default values"""
        default_spider = {
            "name": f"test-spider-{int(time.time())}",
            "display_name": f"Test Spider {int(time.time())}",
            "type": "customized",
            "cmd": "python3 main.py",
            "param": "",
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        default_spider.update(kwargs)
        
        spiders_collection = self.get_collection("spiders")
        result = spiders_collection.insert_one(default_spider)
        default_spider["_id"] = result.inserted_id
        
        self.logger.debug(f"Created test spider: {result.inserted_id}")
        return default_spider
    
    def delete_test_spiders(self, spider_ids: List[ObjectId] = None) -> int:
        """Delete test spiders"""
        spiders_collection = self.get_collection("spiders")
        if spider_ids:
            result = spiders_collection.delete_many({"_id": {"$in": spider_ids}})
        else:
            result = spiders_collection.delete_many({})
        
        self.logger.info(f"Deleted {result.deleted_count} test spiders")
        return result.deleted_count
    
    # Utility operations
    def wait_for_task_status_change(self, task_id: ObjectId, expected_status: str, 
                                   timeout: int = 60, poll_interval: float = 1.0) -> bool:
        """Wait for a task to reach the expected status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task_by_id(task_id)
            if task and task.get("status") == expected_status:
                return True
            time.sleep(poll_interval)
        
        return False
    
    def wait_for_task_status_not(self, task_id: ObjectId, unwanted_status: str, 
                                timeout: int = 60, poll_interval: float = 1.0) -> bool:
        """Wait for a task to NOT be in the unwanted status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task_by_id(task_id)
            if task and task.get("status") != unwanted_status:
                return True
            time.sleep(poll_interval)
        
        return False
    
    def cleanup_all_test_data(self):
        """Clean up all test data"""
        self.delete_test_tasks()
        self.delete_test_nodes() 
        self.delete_test_spiders()
        self.logger.info("Cleaned up all test data")