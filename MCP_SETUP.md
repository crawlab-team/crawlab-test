# MCP Setup for GitHub Copilot CLI

## Overview

This directory contains MCP (Model Context Protocol) configuration for enabling Playwright browser automation tools in GitHub Copilot CLI. The configuration is automatically installed to `~/.copilot/mcp-config.json` when running tests through the Copilot backend.

## Configuration File

**Source**: `tests/mcp-config.json` (template in repository)
**Target**: `~/.copilot/mcp-config.json` (automatically installed)

This file configures the Playwright MCP server so Copilot CLI can use interactive browser automation tools instead of generating static scripts.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

**✅ Automatic**: The test framework automatically copies this to `~/.copilot/mcp-config.json` before running tests.

## Usage

### Automatic Setup (Recommended)

**✅ The test framework automatically handles MCP configuration!**

When running tests via the CLI:

```bash
# The backend automatically installs MCP config to ~/.copilot/
./cli.py --spec UI-001 --backend copilot

# Works with any UI test
./cli.py --spec "spider management" --backend copilot
```

The `CopilotBackend` class:
1. Detects `mcp-config.json` in the tests directory
2. Creates `~/.copilot/` directory if it doesn't exist
3. Copies the config to `~/.copilot/mcp-config.json`
4. Copilot CLI automatically loads MCP servers from this standard location
5. Playwright MCP tools become available during test execution

You don't need to manually configure anything.

### Manual Setup (For Direct Copilot CLI Usage)

If you want to use Copilot CLI directly (outside the test framework):

```bash
# Copy config to global location
mkdir -p ~/.copilot
cp tests/mcp-config.json ~/.copilot/mcp-config.json

# Now use copilot normally - it will automatically load MCP servers
copilot -p "Your prompt here"
```

### Verification

To verify MCP servers are loaded:

```bash
# Run a test and look for this line in the output:
./cli.py --spec UI-001 --backend copilot

# You should see:
# ✓ MCP config installed to: /Users/yourname/.copilot/mcp-config.json

# Check if the config file exists
ls -la ~/.copilot/mcp-config.json
```

## Implementation Details

**✅ IMPLEMENTED**: The Copilot backend now automatically installs MCP configuration when executing tests.

The `CopilotBackend` class in `backends/copilot_backend.py` has a `_setup_mcp_config()` method that:

1. Checks for `mcp-config.json` in the tests directory
2. Creates `~/.copilot/` directory if it doesn't exist
3. Copies the configuration to `~/.copilot/mcp-config.json`
4. Logs whether MCP configuration was successfully installed

### Implementation

```python
def _setup_mcp_config(self) -> None:
    """Setup MCP configuration in ~/.copilot/mcp-config.json"""
    source_config = self.base_dir / "mcp-config.json"
    home_dir = Path.home()
    copilot_dir = home_dir / ".copilot"
    target_config = copilot_dir / "mcp-config.json"
    
    # Ensure ~/.copilot directory exists
    copilot_dir.mkdir(parents=True, exist_ok=True)
    
    if source_config.exists():
        # Copy config to global location
        with open(source_config, 'r') as f:
            config_data = json.load(f)
        with open(target_config, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✓ MCP config installed to: {target_config}")
```

This happens automatically in the `execute()` method before running Copilot CLI.

## Installing Playwright MCP Server

The Playwright MCP server needs to be available in the environment:

```bash
# Install Playwright MCP server globally (for development)
npm install -g @playwright/mcp

# Or use npx (no installation needed, but slower first run)
npx @playwright/mcp@latest
```

## CI Environment Setup

**✅ Configured in GitHub Actions**: The MCP configuration is set up in the `.github/workflows/copilot-setup-steps.yml` workflow.

### Workflow Configuration

The GitHub Actions workflow includes these steps:

```yaml
- name: Setup MCP configuration
  run: |
    mkdir -p ~/.copilot
    cp tests/mcp-config.json ~/.copilot/mcp-config.json
    echo "✓ MCP config installed to ~/.copilot/mcp-config.json"
    npm install -g @playwright/mcp
```

**Location**: `.github/workflows/copilot-setup-steps.yml` (Step 11)

**How it works:**
1. GitHub Actions runner has a clean home directory
2. The workflow creates `~/.copilot/` directory
3. Copies `tests/mcp-config.json` to `~/.copilot/mcp-config.json`
4. Installs Playwright MCP server globally
5. When Copilot CLI runs, it automatically loads the config from `~/.copilot/`

**For other workflows**: If you create additional test workflows, include the "Setup MCP configuration" step before running tests with the Copilot backend.

## Verifying MCP Setup

To verify MCP servers are available to Copilot CLI:

```bash
# Start Copilot CLI with MCP config
MCP_CONFIG=./tests/mcp-config.json copilot

# In the session, check available tools
# You should see Playwright MCP tools listed
```

## Architecture Comparison

### Before (Static Script Approach)
```
Copilot CLI → Creates Node.js script → Runs Playwright programmatically
              ❌ Not interactive
              ❌ Can't adapt to UI changes
              ❌ Brittle selectors
```

### After (MCP Approach)
```
Copilot CLI → MCP Client → Playwright MCP Server → Interactive browser automation
              ✅ Real-time exploration
              ✅ Adaptive to UI structure
              ✅ Uses actual MCP tools:
                 - mcp_playwright_browser_navigate
                 - mcp_playwright_browser_snapshot
                 - mcp_playwright_browser_click
                 - etc.
```

## Troubleshooting

### MCP Server Not Found

If Copilot CLI can't find the MCP server:

1. Check `npx @playwright/mcp` runs successfully
2. Verify MCP_CONFIG path is absolute
3. Check environment variable is set: `echo $MCP_CONFIG`

### Playwright Installation Issues

If Playwright browsers aren't installed:

```bash
npx playwright install chromium
```

### Permission Errors

Ensure the test directory and MCP config are readable:

```bash
chmod +r tests/mcp-config.json
```

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [GitHub Copilot CLI MCP Support](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line)
- [Playwright MCP Server](https://github.com/microsoft/playwright)
- [MCP Extensibility Guide](https://deepwiki.com/github/copilot-cli/4.2-mcp-extensibility)
