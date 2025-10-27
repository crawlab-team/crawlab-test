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

**✅ Configured in GitHub Actions**: The MCP configuration is set up in the `.github/workflows/test.yml` workflow.

### Workflow Configuration

The GitHub Actions workflow includes these steps:

```yaml
- name: Install GitHub Copilot CLI and MCP servers
  if: matrix.category == 'ui' || inputs.backend == 'copilot'
  run: |
    npm install -g @github/copilot
    npm install -g @playwright/mcp
    mkdir -p ~/.copilot
    cp mcp-config.json ~/.copilot/mcp-config.json
    echo "✓ MCP config installed to ~/.copilot/mcp-config.json"
```

**Location**: `.github/workflows/test.yml` (in the test job steps)

**How it works:**
1. GitHub Actions runner has a clean home directory
2. Installs GitHub Copilot CLI globally
3. **Installs Playwright MCP server** globally (`@playwright/mcp`)
4. Creates `~/.copilot/` directory
5. Copies `mcp-config.json` to `~/.copilot/mcp-config.json`
6. When Copilot CLI runs, it **automatically loads MCP config** from `~/.copilot/mcp-config.json`
7. The Playwright MCP server becomes available as MCP tools in Copilot

**Critical**: Both the MCP config file AND the actual MCP server npm package must be installed. The config tells Copilot where to find the server, and the server provides the actual tools.

**For other workflows**: If you create additional test workflows, include both:
1. Install the MCP server: `npm install -g @playwright/mcp`
2. Setup the config: Copy `mcp-config.json` to `~/.copilot/mcp-config.json`

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

1. **Check the MCP server is installed**:
   ```bash
   npm list -g @playwright/mcp
   # Should show the installed version
   ```

2. **Verify the MCP server runs successfully**:
   ```bash
   npx @playwright/mcp
   # Should start the server without errors
   ```

3. **Check the MCP config file exists**:
   ```bash
   cat ~/.copilot/mcp-config.json
   # Should show the Playwright server configuration
   ```

4. **Verify Copilot CLI loads the config**:
   ```bash
   # Copilot CLI automatically loads from ~/.copilot/mcp-config.json
   # No environment variable needed
   ```

### Common Issue: MCP Config Exists But Tools Not Available

**Symptoms**: 
- `✓ MCP config installed to: ~/.copilot/mcp-config.json` appears in logs
- But tests skip with "MCP Playwright tools not available"

**Root Cause**: The MCP **config file** was created, but the actual **MCP server npm package** (`@playwright/mcp`) was never installed.

**Solution**:
```bash
# Install the Playwright MCP server package
npm install -g @playwright/mcp

# Verify it's installed
npm list -g @playwright/mcp

# Test it works
npx @playwright/mcp --help
```

**In CI**: Make sure your workflow includes:
```yaml
- name: Install Playwright MCP Server
  run: npm install -g @playwright/mcp
```

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
