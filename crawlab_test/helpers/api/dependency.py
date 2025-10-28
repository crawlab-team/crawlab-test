"""
API helper functions for dependency management operations.

This module provides functions for:
- Dependency configuration CRUD
- Config setup list/install/uninstall
- Repository list/search/versions/install/uninstall
- Dependency logs retrieval
"""

import os
from typing import Any, Dict, List, Optional

import requests

# Disable proxy for localhost
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

API_URL = os.getenv("API_URL", "http://localhost:8080/api")


def _get_headers(token: str) -> Dict[str, str]:
    """Get headers with authorization token"""
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ============================================================================
# Dependency Config Operations
# ============================================================================


def get_dependency_config(token: str, lang: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Get dependency configuration for a specific language.

    Args:
        token: Authentication token
        lang: Programming language (python, node, java, etc.)
        timeout: Request timeout in seconds

    Returns:
        Config data or None if request fails
    """
    response = requests.get(f"{API_URL}/dependencies/configs/{lang}", headers=_get_headers(token), timeout=timeout)
    if response.status_code == 200:
        return response.json()
    return None


def update_dependency_config(
    token: str, lang: str, exec_cmd: str, pkg_cmd: str, pkg_src_url: str, timeout: int = 10
) -> bool:
    """
    Update dependency configuration for a specific language.

    Args:
        token: Authentication token
        lang: Programming language
        exec_cmd: Command to execute
        pkg_cmd: Package command
        pkg_src_url: Package source URL
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    response = requests.put(
        f"{API_URL}/dependencies/configs/{lang}",
        headers=_get_headers(token),
        json={"exec_cmd": exec_cmd, "pkg_cmd": pkg_cmd, "pkg_src_url": pkg_src_url},
        timeout=timeout,
    )
    return response.status_code in [200, 204]


def get_dependency_config_versions(token: str, lang: str, timeout: int = 10) -> Optional[List[str]]:
    """
    Get available versions for a dependency configuration.

    Args:
        token: Authentication token
        lang: Programming language
        timeout: Request timeout in seconds

    Returns:
        List of version strings or None if request fails
    """
    response = requests.get(
        f"{API_URL}/dependencies/configs/{lang}/versions", headers=_get_headers(token), timeout=timeout
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    return None


# ============================================================================
# Dependency Config Setup Operations
# ============================================================================


def get_dependency_config_setups(
    token: str, lang: str, page: int = 1, size: int = 10, timeout: int = 10
) -> Optional[Dict[str, Any]]:
    """
    Get list of dependency config setups.

    Args:
        token: Authentication token
        lang: Programming language
        page: Page number
        size: Page size
        timeout: Request timeout in seconds

    Returns:
        Setup list data or None if request fails
    """
    response = requests.get(
        f"{API_URL}/dependencies/configs/{lang}/setups",
        headers=_get_headers(token),
        params={"page": page, "size": size},
        timeout=timeout,
    )
    if response.status_code == 200:
        return response.json()
    return None


def install_dependency_config_setup(
    token: str,
    lang: str,
    mode: str = "all",
    node_ids: Optional[List[str]] = None,
    version: Optional[str] = None,
    timeout: int = 60,
) -> bool:
    """
    Install dependency configuration setup.

    Args:
        token: Authentication token
        lang: Programming language
        mode: Installation mode ('all' or specific nodes)
        node_ids: List of node IDs (when mode != 'all')
        version: Version to install
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    payload = {"mode": mode}
    if node_ids:
        payload["node_ids"] = node_ids
    if version:
        payload["version"] = version

    response = requests.post(
        f"{API_URL}/dependencies/configs/{lang}/setups/install",
        headers=_get_headers(token),
        json=payload,
        timeout=timeout,
    )
    return response.status_code in [200, 201, 204]


def uninstall_dependency_config_setup(
    token: str, lang: str, mode: str = "all", node_ids: Optional[List[str]] = None, timeout: int = 60
) -> bool:
    """
    Uninstall dependency configuration setup.

    Args:
        token: Authentication token
        lang: Programming language
        mode: Uninstallation mode ('all' or specific nodes)
        node_ids: List of node IDs (when mode != 'all')
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    payload = {"mode": mode}
    if node_ids:
        payload["node_ids"] = node_ids

    response = requests.post(
        f"{API_URL}/dependencies/configs/{lang}/setups/uninstall",
        headers=_get_headers(token),
        json=payload,
        timeout=timeout,
    )
    return response.status_code in [200, 204]


# ============================================================================
# Dependency Repository Operations
# ============================================================================


def get_dependency_repos(
    token: str,
    lang: str = "python",
    page: int = 1,
    size: int = 10,
    filter_query: Optional[str] = None,
    timeout: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Get list of installed dependency repositories.

    Args:
        token: Authentication token
        lang: Programming language
        page: Page number
        size: Page size
        filter_query: Filter query string
        timeout: Request timeout in seconds

    Returns:
        Repository list data or None if request fails
    """
    params = {"lang": lang, "page": page, "size": size}
    if filter_query:
        params["filter"] = filter_query

    response = requests.get(
        f"{API_URL}/dependencies/repos", headers=_get_headers(token), params=params, timeout=timeout
    )
    if response.status_code == 200:
        return response.json()
    return None


def search_dependency_repos(
    token: str, lang: str, query: str, page: int = 1, size: int = 10, timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """
    Search for dependency repositories.

    Args:
        token: Authentication token
        lang: Programming language
        query: Search query
        page: Page number
        size: Page size
        timeout: Request timeout in seconds (longer for search)

    Returns:
        Search results data or None if request fails
    """
    response = requests.get(
        f"{API_URL}/dependencies/repos/search",
        headers=_get_headers(token),
        params={"lang": lang, "query": query, "page": page, "size": size},
        timeout=timeout,
    )
    if response.status_code == 200:
        return response.json()
    return None


def get_dependency_repo_versions(token: str, lang: str, name: str, timeout: int = 10) -> Optional[List[str]]:
    """
    Get available versions for a dependency repository.

    Args:
        token: Authentication token
        lang: Programming language
        name: Repository name
        timeout: Request timeout in seconds

    Returns:
        List of version strings or None if request fails
    """
    response = requests.get(
        f"{API_URL}/dependencies/repos/versions",
        headers=_get_headers(token),
        params={"lang": lang, "repo": name},
        timeout=timeout,
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    return None


def install_dependency_repo(
    token: str,
    lang: str,
    name: str,
    version: Optional[str] = None,
    mode: str = "all",
    node_ids: Optional[List[str]] = None,
    timeout: int = 120,
) -> bool:
    """
    Install a dependency repository.

    Args:
        token: Authentication token
        lang: Programming language
        name: Repository name
        version: Version to install (latest if not specified)
        mode: Installation mode ('all' or specific nodes)
        node_ids: List of node IDs (when mode != 'all')
        timeout: Request timeout in seconds (longer for install)

    Returns:
        True if successful, False otherwise
    """
    payload = {"lang": lang, "name": name, "mode": mode}
    if version:
        payload["version"] = version
    if node_ids:
        payload["node_ids"] = node_ids

    response = requests.post(
        f"{API_URL}/dependencies/repos/install", headers=_get_headers(token), json=payload, timeout=timeout
    )
    return response.status_code in [200, 201, 204]


def uninstall_dependency_repo(
    token: str, lang: str, name: str, mode: str = "all", node_ids: Optional[List[str]] = None, timeout: int = 60
) -> bool:
    """
    Uninstall a dependency repository.

    Args:
        token: Authentication token
        lang: Programming language
        name: Repository name
        mode: Uninstallation mode ('all' or specific nodes)
        node_ids: List of node IDs (when mode != 'all')
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    payload = {"lang": lang, "names": [name], "mode": mode}
    if node_ids:
        payload["node_ids"] = node_ids

    response = requests.post(
        f"{API_URL}/dependencies/repos/uninstall", headers=_get_headers(token), json=payload, timeout=timeout
    )
    return response.status_code in [200, 204]


# ============================================================================
# Dependency Logs
# ============================================================================


def get_dependency_logs(token: str, dependency_id: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Get logs for a specific dependency.

    Args:
        token: Authentication token
        dependency_id: Dependency ID
        timeout: Request timeout in seconds

    Returns:
        Logs data or None if request fails
    """
    response = requests.get(
        f"{API_URL}/dependencies/{dependency_id}/logs", headers=_get_headers(token), timeout=timeout
    )
    if response.status_code == 200:
        return response.json()
    return None
