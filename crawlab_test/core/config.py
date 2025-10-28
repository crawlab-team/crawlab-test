"""
Configuration Module

This module handles loading and managing test configuration.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Manages test configuration"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize Config
        
        Args:
            base_dir: Base directory for tests (defaults to tests directory)
        """
        if base_dir is None:
            # Default to tests directory (parent of core)
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.specs_dir = self.base_dir / "specs"
        
        # Load CI configuration
        self.ci_config = self._load_ci_config()
        
        # CI Environment detection
        self.is_ci = os.getenv('CI_ENVIRONMENT', 'false').lower() == 'true'
        self.is_github_actions = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
    
    def _load_ci_config(self) -> Dict:
        """
        Load CI configuration from ci.env file
        
        Returns:
            Dictionary of configuration values
        """
        config = {}
        ci_env_file = self.base_dir / "ci.env"
        
        if ci_env_file.exists():
            try:
                with open(ci_env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Failed to load CI config: {e}")
        
        return config
    
    def load_category_config(self, category: str) -> Dict:
        """
        Load category configuration from _matrix.json
        
        Args:
            category: Category name (e.g., 'ui', 'cluster')
            
        Returns:
            Dictionary of category configuration
        """
        config = {}
        matrix_file = self.specs_dir / category / "_matrix.json"
        
        if matrix_file.exists():
            try:
                with open(matrix_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load matrix config for {category}: {e}")
        
        return config
    
    def get_timeout_for_category(self, category: str, default: int = 30) -> int:
        """
        Get timeout in minutes for a category
        
        Args:
            category: Category name
            default: Default timeout in minutes
            
        Returns:
            Timeout in minutes
        """
        timeout_key = f"CATEGORY_REQUIREMENTS_{category.upper()}"
        
        if timeout_key in self.ci_config:
            try:
                # Format: docker,timeout_minutes,retry_count
                parts = self.ci_config[timeout_key].split(',')
                if len(parts) >= 2:
                    return int(parts[1])
            except (ValueError, IndexError):
                pass
        
        # Check environment variable
        env_timeout = os.getenv('TEST_TIMEOUT_MINUTES')
        if env_timeout:
            try:
                return int(env_timeout)
            except ValueError:
                pass
        
        return default
    
    def get_retry_count_for_category(self, category: str, default: int = 1) -> int:
        """
        Get retry count for a category
        
        Args:
            category: Category name
            default: Default retry count
            
        Returns:
            Retry count
        """
        timeout_key = f"CATEGORY_REQUIREMENTS_{category.upper()}"
        
        if timeout_key in self.ci_config:
            try:
                # Format: docker,timeout_minutes,retry_count
                parts = self.ci_config[timeout_key].split(',')
                if len(parts) >= 3:
                    return int(parts[2])
            except (ValueError, IndexError):
                pass
        
        return default
    
    def requires_docker(self, category: str) -> bool:
        """
        Check if a category requires Docker
        
        Args:
            category: Category name
            
        Returns:
            True if Docker is required
        """
        timeout_key = f"CATEGORY_REQUIREMENTS_{category.upper()}"
        
        if timeout_key in self.ci_config:
            parts = self.ci_config[timeout_key].split(',')
            if len(parts) >= 1:
                return parts[0].strip().lower() == 'docker'
        
        return False
