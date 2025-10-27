#!/usr/bin/env python3
"""
Database API Helper

Provides utilities for interacting with Crawlab's database API endpoints.
Supports connection testing, metadata retrieval, CRUD operations, and more.
"""

import logging
import requests
from typing import Dict, List, Optional, Any


class DatabaseAPIHelper:
    """Helper class for database API operations"""
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize database API helper
        
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
    
    def create_database(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new database connection
        
        Args:
            data: Database configuration including:
                - name: Database connection name
                - data_source: Database type (mysql, postgres, mongodb, etc.)
                - host: Database host (optional for some types)
                - port: Database port (optional for some types)
                - username: Database username (optional)
                - password: Database password (optional)
                - database: Database name
                
        Returns:
            Created database object or None on failure
        """
        try:
            # Wrap data in {"data": {...}} as per OpenAPI spec
            response = requests.post(
                f"{self.base_url}/databases",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to create database: {e}")
            return None
    
    def get_database(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Get database details by ID
        
        Args:
            database_id: Database ID
            
        Returns:
            Database object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/databases/{database_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get database: {e}")
            return None
    
    def list_databases(self, page: int = 1, size: int = 10) -> Optional[Dict[str, Any]]:
        """
        List all databases
        
        Args:
            page: Page number
            size: Page size
            
        Returns:
            List response with data and pagination info
        """
        try:
            response = requests.get(
                f"{self.base_url}/databases",
                params={"page": page, "size": size},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to list databases: {e}")
            return None
    
    def update_database(self, database_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update database configuration
        
        Args:
            database_id: Database ID
            data: Updated configuration
            
        Returns:
            Updated database object or None on failure
        """
        try:
            # Wrap data in {"data": {...}} as per OpenAPI spec
            response = requests.put(
                f"{self.base_url}/databases/{database_id}",
                json={"data": data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to update database: {e}")
            return None
    
    def delete_database(self, database_id: str) -> bool:
        """
        Delete a database connection
        
        Args:
            database_id: Database ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/databases/{database_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete database: {e}")
            return False
    
    def batch_update_databases(self, database_ids: List[str], update_data: Dict[str, Any]) -> bool:
        """
        Batch update multiple databases
        
        Args:
            database_ids: List of database IDs
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.base_url}/databases",
                json={"ids": database_ids, "update": update_data},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch update databases: {e}")
            return False
    
    def batch_delete_databases(self, database_ids: List[str]) -> bool:
        """
        Batch delete multiple databases
        
        Args:
            database_ids: List of database IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/databases",
                json={"ids": database_ids},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to batch delete databases: {e}")
            return False
    
    def test_connection(self, database_id: str) -> Dict[str, Any]:
        """
        Test database connection
        
        Args:
            database_id: Database ID
            
        Returns:
            Connection test result with status and message
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/connection/test",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data', {})
        except Exception as e:
            self.logger.error(f"Failed to test connection: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_metadata(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Get database metadata (databases, tables, columns)
        
        Args:
            database_id: Database ID
            
        Returns:
            Metadata object or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/databases/{database_id}/metadata",
                headers=self._get_headers(),
                timeout=10  # Reduced timeout - may hang on connection issues
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get metadata: {e}")
            return None
    
    def get_table_metadata(self, database_id: str, database_name: str, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific table metadata
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            
        Returns:
            Table metadata or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/metadata/get",
                json={"database": database_name, "table": table_name},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get table metadata: {e}")
            return None
    
    def create_table(self, database_id: str, database_name: str, table_name: str, 
                     columns: List[Dict[str, Any]], indexes: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Create a table
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            columns: List of column definitions
            indexes: Optional list of index definitions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "database": database_name,
                "table": table_name,
                "columns": columns
            }
            if indexes:
                data["indexes"] = indexes
                
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/create",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to create table: {e}")
            return False
    
    def drop_table(self, database_id: str, database_name: str, table_name: str) -> bool:
        """
        Drop a table
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/drop",
                json={"database": database_name, "table": table_name},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to drop table: {e}")
            return False
    
    def modify_table(self, database_id: str, database_name: str, table_name: str,
                     columns: Optional[List[Dict[str, Any]]] = None,
                     indexes: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Modify table structure (columns and/or indexes)
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            columns: Optional column modifications
            indexes: Optional index modifications
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "database": database_name,
                "table": table_name
            }
            if columns:
                data["columns"] = columns
            if indexes:
                data["indexes"] = indexes
                
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/modify",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify table: {e}")
            return False
    
    def rename_table(self, database_id: str, database_name: str, table_name: str,
                     new_table_name: str) -> bool:
        """
        Rename a table
        
        Args:
            database_id: Database ID
            database_name: Database name (optional for some DBs)
            table_name: Current table name
            new_table_name: New table name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "table_name": table_name,
                "new_table_name": new_table_name
            }
            if database_name:
                data["database_name"] = database_name
                
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/rename",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to rename table: {e}")
            return False
    
    def get_table_data(self, database_id: str, database_name: str, table_name: str,
                       page: int = 1, size: int = 10, conditions: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get table data (read rows)
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            page: Page number
            size: Page size
            conditions: Optional filter conditions
            
        Returns:
            Data response with rows and pagination info
        """
        try:
            data = {
                "database": database_name,
                "table": table_name,
                "page": page,
                "size": size
            }
            if conditions:
                data["conditions"] = conditions
                
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/data/get",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get table data: {e}")
            return None
    
    def insert_row(self, database_id: str, database_name: str, table_name: str,
                   row: Dict[str, Any]) -> bool:
        """
        Insert a row into table
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            row: Row data as key-value pairs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/data",
                json={
                    "database": database_name,
                    "table": table_name,
                    "action": "insert",
                    "data": row
                },
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert row: {e}")
            return False
    
    def update_rows(self, database_id: str, database_name: str, table_name: str,
                    data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """
        Update rows in table
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            data: Data to update
            conditions: Filter conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/data",
                json={
                    "database": database_name,
                    "table": table_name,
                    "action": "update",
                    "data": data,
                    "conditions": conditions
                },
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to update rows: {e}")
            return False
    
    def delete_rows(self, database_id: str, database_name: str, table_name: str,
                    conditions: Dict[str, Any]) -> bool:
        """
        Delete rows from table
        
        Args:
            database_id: Database ID
            database_name: Database name
            table_name: Table name
            conditions: Filter conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/tables/data",
                json={
                    "database": database_name,
                    "table": table_name,
                    "action": "delete",
                    "conditions": conditions
                },
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete rows: {e}")
            return False
    
    def execute_query(self, database_id: str, database_name: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a custom query
        
        Args:
            database_id: Database ID
            database_name: Database name
            query: SQL or query string
            
        Returns:
            Query result or None on failure
        """
        try:
            response = requests.post(
                f"{self.base_url}/databases/{database_id}/query",
                json={
                    "database": database_name,
                    "query": query
                },
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to execute query: {e}")
            return None
    
    def get_current_metrics(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current database metrics
        
        Args:
            database_id: Database ID
            
        Returns:
            Metrics data or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/databases/{database_id}/metrics/current",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return None
    
    def get_column_types(self, database_id: str) -> Optional[List[str]]:
        """
        Get available column types for database
        
        Args:
            database_id: Database ID
            
        Returns:
            List of column types or None on failure
        """
        try:
            response = requests.get(
                f"{self.base_url}/databases/{database_id}/columns/types",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data')
        except Exception as e:
            self.logger.error(f"Failed to get column types: {e}")
            return None
