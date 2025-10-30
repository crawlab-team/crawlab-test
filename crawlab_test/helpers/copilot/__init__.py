"""
GitHub Copilot CLI Helper Utilities

This module provides utility functions for working with GitHub Copilot CLI
in the context of Crawlab test execution.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def is_copilot_available() -> bool:
    """
    Check if GitHub Copilot CLI is installed and available.

    Returns:
        bool: True if copilot command is available, False otherwise
    """
    return shutil.which("copilot") is not None


def is_gh_cli_available() -> bool:
    """
    Check if GitHub CLI is installed.

    Returns:
        bool: True if gh command is available, False otherwise
    """
    return shutil.which("gh") is not None


def check_copilot_extension() -> bool:
    """
    Check if GitHub Copilot CLI extension is installed.

    Returns:
        bool: True if extension is installed, False otherwise
    """
    if not is_gh_cli_available():
        return False

    try:
        result = subprocess.run(["gh", "extension", "list"], capture_output=True, text=True, check=True)
        return "gh-copilot" in result.stdout
    except subprocess.CalledProcessError:
        return False


def install_copilot_extension() -> bool:
    """
    Install GitHub Copilot CLI extension.

    Returns:
        bool: True if installation succeeded, False otherwise
    """
    if not is_gh_cli_available():
        return False

    try:
        subprocess.run(["gh", "extension", "install", "github/gh-copilot"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def setup_copilot() -> Dict[str, any]:
    """
    Setup GitHub Copilot CLI with all prerequisites.

    Returns:
        dict: Status information with keys:
            - gh_cli_available: bool
            - extension_installed: bool
            - copilot_available: bool
            - ready: bool
            - message: str
    """
    status = {
        "gh_cli_available": is_gh_cli_available(),
        "extension_installed": False,
        "copilot_available": False,
        "ready": False,
        "message": "",
    }

    if not status["gh_cli_available"]:
        status["message"] = "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
        return status

    status["extension_installed"] = check_copilot_extension()

    if not status["extension_installed"]:
        status["message"] = "Installing GitHub Copilot CLI extension..."
        if install_copilot_extension():
            status["extension_installed"] = True
            status["message"] = "GitHub Copilot CLI extension installed successfully"
        else:
            status["message"] = "Failed to install GitHub Copilot CLI extension"
            return status

    status["copilot_available"] = is_copilot_available()

    if not status["copilot_available"]:
        status["message"] = "Copilot command not found. Extension may need to be reloaded."
        return status

    status["ready"] = True
    status["message"] = "GitHub Copilot CLI is ready"

    return status


def build_copilot_command(
    prompt: str,
    mode: str = "interactive",
    allowed_tools: Optional[List[str]] = None,
    denied_tools: Optional[List[str]] = None,
    allow_all: bool = False,
) -> List[str]:
    """
    Build a Copilot CLI command with the specified configuration.

    Args:
        prompt: The prompt to send to Copilot
        mode: 'interactive' or 'programmatic'
        allowed_tools: List of tools to allow (e.g., ['write', 'shell(docker)'])
        denied_tools: List of tools to deny (e.g., ['shell(rm)'])
        allow_all: If True, allow all tools (use with caution)

    Returns:
        list: Command as list of arguments
    """
    if mode == "interactive":
        return ["copilot"]

    cmd = ["copilot", "-p", prompt]

    if allow_all:
        cmd.append("--allow-all-tools")

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allow-tool", tool])

    if denied_tools:
        for tool in denied_tools:
            cmd.extend(["--deny-tool", tool])

    return cmd


def get_safe_tool_config(category: str = "general") -> Dict[str, List[str]]:
    """
    Get safe tool configuration for different test categories.

    Args:
        category: Test category (ui, infrastructure, dependencies, etc.)

    Returns:
        dict: Configuration with 'allowed_tools' and 'denied_tools' lists
    """
    # Always deny these dangerous operations
    common_denied = [
        "shell(rm -rf)",
        "shell(git push)",
        "shell(git force-push)",
        "shell(sudo rm)",
    ]

    configs = {
        "ui": {
            "allowed_tools": [
                "write",
                "shell(npm)",
                "shell(node)",
                "shell(npx)",
            ],
            "denied_tools": [*common_denied, "shell(rm)"],
        },
        "infrastructure": {
            "allowed_tools": [
                "write",
                "shell(docker)",
                "shell(curl)",
                "shell(python)",
            ],
            "denied_tools": [*common_denied, "shell(docker rm -f)"],
        },
        "dependencies": {
            "allowed_tools": [
                "write",
                "shell(pip)",
                "shell(npm)",
                "shell(python)",
                "shell(curl)",
            ],
            "denied_tools": [*common_denied, "shell(rm)"],
        },
        "api": {
            "allowed_tools": [
                "write",
                "shell(curl)",
                "shell(python)",
            ],
            "denied_tools": [*common_denied, "shell(rm)"],
        },
        "general": {
            "allowed_tools": [
                "write",
                "shell(python)",
                "shell(curl)",
            ],
            "denied_tools": [*common_denied, "shell(rm)"],
        },
    }

    return configs.get(category, configs["general"])


def format_spec_prompt(spec_path: Path, mode: str = "full") -> str:
    """
    Format a test specification into a prompt for Copilot CLI.

    Args:
        spec_path: Path to the test specification file
        mode: 'full', 'step-by-step', or 'summary'

    Returns:
        str: Formatted prompt
    """
    prompts = {
        "full": f"""Execute the complete test specification at {spec_path}.

Follow all steps including:
1. Prerequisites verification
2. Setup procedures
3. Test execution
4. Validation of success criteria
5. Cleanup procedures

After each major step, show validation results and confirm before proceeding.
Generate a detailed summary report at the end with pass/fail status and any issues encountered.""",
        "step-by-step": f"""Read the test specification at {spec_path}.

Execute the test step by step:
- Show me the current step before executing
- Execute the step
- Show validation results
- Wait for my confirmation before proceeding to the next step

At the end, provide a summary of all results.""",
        "summary": f"""Read and execute the test specification at {spec_path}.

Execute all steps automatically and provide a summary report with:
- Test name and category
- Pass/fail status
- Any errors or warnings
- Overall result""",
    }

    return prompts.get(mode, prompts["full"])


# Convenience exports
__all__ = [
    "build_copilot_command",
    "check_copilot_extension",
    "format_spec_prompt",
    "get_safe_tool_config",
    "install_copilot_extension",
    "is_copilot_available",
    "is_gh_cli_available",
    "setup_copilot",
]
