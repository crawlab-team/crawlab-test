"""
Docker Detection Module

This module provides functionality to detect and interact with Docker environments.
"""

import sys
from pathlib import Path
from typing import Dict, Optional

# Try to import Docker utilities
try:
    # Add helpers/common to path
    helpers_path = Path(__file__).parent.parent / "helpers" / "common"
    if str(helpers_path) not in sys.path:
        sys.path.append(str(helpers_path))
    from docker_utils import docker_utils
except ImportError:
    docker_utils = None


class DockerDetector:
    """Detects and provides information about Docker environments"""
    
    def __init__(self):
        """Initialize DockerDetector"""
        self.docker_utils = docker_utils
    
    def is_docker_available(self) -> bool:
        """
        Check if Docker is available
        
        Returns:
            True if Docker is available
        """
        if not self.docker_utils:
            return False
        
        try:
            return self.docker_utils.is_available()
        except Exception:
            return False
    
    def is_docker_environment(self) -> bool:
        """
        Detect if we're in a Docker environment
        
        Returns:
            True if running in Docker or Crawlab containers found
        """
        if not self.docker_utils:
            return False
        
        try:
            return (
                self.docker_utils.is_running_in_container() or 
                bool(self.docker_utils.find_crawlab_containers())
            )
        except Exception:
            return False
    
    def get_docker_info(self) -> Dict:
        """
        Get Docker environment information
        
        Returns:
            Dictionary with Docker environment details
        """
        if not self.docker_utils:
            return {"error": "Docker utils not available"}
        
        try:
            containers = self.docker_utils.find_crawlab_containers()
            master = self.docker_utils.find_master_container()
            api_url = self.docker_utils.detect_crawlab_api_url()
            
            return {
                "containers_found": len(containers),
                "master_container": master.get('Names') if master else None,
                "api_url": api_url,
                "docker_available": self.docker_utils.is_available()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_crawlab_api_url(self) -> Optional[str]:
        """
        Get Crawlab API URL
        
        Returns:
            API URL if available, None otherwise
        """
        if not self.docker_utils:
            return None
        
        try:
            return self.docker_utils.detect_crawlab_api_url()
        except Exception:
            return None
    
    def find_master_container(self) -> Optional[Dict]:
        """
        Find Crawlab master container
        
        Returns:
            Container information or None
        """
        if not self.docker_utils:
            return None
        
        try:
            return self.docker_utils.find_master_container()
        except Exception:
            return None
