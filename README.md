# Crawlab Test

Comprehensive automated testing framework for [Crawlab](https://github.com/crawlab-team/crawlab) and [Crawlab Pro](https://github.com/crawlab-team/crawlab-pro).

> **Note**: This is a standalone testing repository that can be used independently or alongside the main Crawlab repositories. It was extracted from `crawlab-pro/tests` for better management and maintainability.

## Overview

This testing framework follows a flexible, scenario-based approach where each test case is designed specifically for what it needs to test, using the most appropriate tools and methods. Unlike traditional testing frameworks that impose rigid structures, this approach adapts to the specific needs of each test scenario.

## Key Features

- **Unified Markdown Specifications**: Human-readable test cases that can be executed by AI, scripts, or manually
- **Flexible Execution**: Use scripts, AI tools, manual testing, or hybrid approaches as needed
- **Modular Architecture**: Clean separation between core modules, backends, and CLI
- **Multiple Backends**: Script, Copilot CLI, and Playwright backends
- **Tool-Agnostic**: Not tied to specific testing frameworks - use whatever works best
- **Scenario-Driven**: Each test targets real-world scenarios that matter to users
- **Self-Contained**: Each test spec includes everything needed to understand and execute

## Quick Start

### Initial Setup

Before running UI tests, you need to install Playwright browsers:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for UI tests)
./setup-playwright.sh

# Or install with system dependencies (may require sudo)
./setup-playwright.sh --with-deps

# Or install all browsers (chromium, firefox, webkit)
./setup-playwright.sh --all
```

### Using the New Unified CLI (Recommended)

The unified CLI (`cli.py`) is the primary entry point for all test execution. It automatically detects the best backend for your test and provides a consistent interface.

```bash
# List available test specifications
./cli.py --list-specs

# Search for tests
./cli.py --search docker

# Run a test by ID (auto-detects best backend)
./cli.py --spec UI-001

# Run a test by name (fuzzy search)
./cli.py --spec "spider management"

# Run with specific backend
./cli.py --spec UI-001 --backend playwright
./cli.py --spec CLS-001 --backend script
./cli.py --spec DB-001 --backend copilot

# Run with specific AI model (Copilot backend only)
./cli.py --spec DB-001 --backend copilot --model gpt-4o
./cli.py --spec DB-001 --backend copilot --model claude-3.5-sonnet
./cli.py --spec DB-001 --backend copilot --model o1-preview

# Dry run to see what would execute
./cli.py --spec UI-001 --dry-run

# Run in CI mode
./cli.py --spec UI-001 --ci --timeout 15
```

**Backend Auto-Detection:**
1. **Script Backend**: If a runner script exists in `runners/` directory
2. **Playwright Backend**: For UI tests with Playwright available
3. **Copilot Backend**: Default fallback if Copilot CLI is available

## Architecture

The test framework has been refactored into a clean, modular architecture:

```
cli.py (Main Entry Point)
    │
    ├── Core Modules (core/)
    │   ├── spec_finder.py      # Find and search test specs
    │   ├── config.py            # Configuration management
    │   ├── docker_detector.py   # Docker environment detection
    │   └── result_handler.py    # Result saving and reporting
    │
    └── Backends (backends/)
        ├── base.py              # Abstract backend interface
        ├── script_backend.py    # Python/Shell script execution
        ├── copilot_backend.py   # GitHub Copilot CLI execution
        └── playwright_backend.py # TypeScript Playwright tests
```

### Backend Selection

The CLI automatically selects the best backend:

1. **Script Backend**: If a runner script exists in `runners/` directory
2. **Playwright Backend**: For UI tests with Playwright available
3. **Copilot Backend**: Default fallback if Copilot CLI is available

You can also explicitly specify a backend: `--backend script|copilot|playwright`

For more details, see:
- `docs/TEST_RUNNER_ARCHITECTURE.md` - Technical architecture and design patterns
- `docs/UI_TESTING_README.md` - UI testing with Playwright

## Docker Support

The testing framework automatically detects and supports Docker-based Crawlab deployments:

### Automatic Detection
- **Container Discovery**: Uses Docker CLI to find running Crawlab containers
- **API Endpoint**: Automatically detects master container and API endpoints
- **Environment Detection**: Identifies if tests are running inside or outside containers

### Docker Commands
```bash
# Check Docker environment health
./helpers/infrastructure/docker-manager.py --action health

# List all Crawlab containers
./helpers/infrastructure/docker-manager.py --action list

# Disconnect a worker container (network isolation)
./helpers/infrastructure/docker-manager.py --action disconnect --container worker-1 --method network

# Reconnect a worker container
./helpers/infrastructure/docker-manager.py --action reconnect --container worker-1

# Monitor reconciliation during disruption
./helpers/infrastructure/docker-manager.py --action monitor --timeout 60

# Get container logs
./helpers/infrastructure/docker-manager.py --action logs --container master --lines 50

# Execute command in container
./helpers/infrastructure/docker-manager.py --action exec --container worker-1 --command ps aux
```

## GitHub Copilot CLI Integration

The framework integrates with GitHub Copilot CLI for AI-assisted test execution, particularly useful for UI tests and complex workflows.

### Prerequisites

```bash
# Install GitHub CLI
# https://cli.github.com/

# Install Copilot CLI extension (done automatically if missing)
gh extension install github/gh-copilot

# Verify installation
copilot --version
```

### Usage Modes

#### Copilot Mode (Default)
Best for automated testing with AI assistance:

```bash
./run-with-copilot.py specs/ui/UI-001-spider-management-workflow-validation.md

# Or via test-runner
./test-runner.py --spec specs/ui/UI-001-spider-management-workflow-validation.md --method copilot
```

#### Script Mode
For direct Python/shell script execution:

```bash
# Via test-runner
# Script mode (when available and working)
./test-runner.py --spec specs/cluster/CLS-001-master-worker-node-disconnection-and-reconnection-stability.md --method script
```

### Execution Methods Explained

| Method | Description | Best For | Tool Approval |
|------|-------------|----------|---------------|
| `copilot` | AI-powered test execution via GitHub Copilot CLI | All tests, CI/CD | All tools except dangerous operations (rm -rf, git push) |
| `script` | Direct execution via Python/shell scripts | Tests with dedicated test runners | N/A (direct execution) |

### Features

- **Automatic Setup**: Installs Copilot CLI extension if missing
- **Security**: All tools allowed except dangerous operations (rm -rf, git push)
- **Logging**: Complete execution logs saved to `results/`
- **Summaries**: Auto-generated test reports in Markdown and JSON
- **Category Detection**: Auto-selects appropriate test execution method
- **CI/CD Ready**: Fully automated execution in all environments

### Environment Variables

```bash
# Set AI model (default: claude-sonnet-4)
export COPILOT_MODEL=gpt-5

# Override Crawlab API endpoint
export CRAWLAB_API_URL=http://localhost:8080

# Set test timeout (minutes)
export TEST_TIMEOUT_MINUTES=60
```

### Examples

```bash
# Copilot-powered UI test
./run-with-copilot.py specs/ui/UI-001-spider-management-workflow-validation.md

# Copilot-powered cluster test
./run-with-copilot.py specs/scheduler/SCH-001-task-status-reconciliation-and-process-verification.md

# Script-based dependency test
./test-runner.py --spec specs/dependencies/DEP-001-dependencies-installation-robustness.md --method script

# Use specific model
COPILOT_MODEL=gpt-5 ./run-with-copilot.py specs/ui/UI-001-spider-management-workflow-validation.md
```

### Security Considerations

The framework balances flexibility with safety:

- **All tools allowed**: Maximum flexibility for AI-assisted testing
- **Critical protections**: Dangerous operations (rm -rf, git push) are blocked
- **Trusted directories**: Copilot CLI operates within the tests/ directory
- **Test environment**: Designed for test/staging, not production
- **Reversible**: Docker containers can be destroyed and recreated

See [.github/instructions/copilot-cli-testing.md](.github/instructions/copilot-cli-testing.md) for comprehensive documentation.

### MCP (Model Context Protocol) Configuration

**✅ Automatic Setup**: The test framework automatically configures MCP servers for enhanced testing capabilities.

#### Playwright MCP Server

The `mcp-config.json` file is automatically installed to `~/.copilot/mcp-config.json` to enable Playwright browser automation tools:

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

**How it works:**
1. When running tests with `--backend copilot`, the framework automatically copies `mcp-config.json` to `~/.copilot/mcp-config.json`
2. Copilot CLI loads the Playwright MCP server from this standard location
3. Interactive browser automation tools become available during test execution
4. Tests can use tools like `mcp_playwright_browser_navigate`, `mcp_playwright_browser_click`, etc.

**No manual setup required** - the framework handles everything automatically!

For more details, see [MCP_SETUP.md](MCP_SETUP.md).

## Testing SOP (Standard Operating Procedure)

### 1. Create Specifications
- Write unified markdown specification files for each test case
- Specs define the scenario, requirements, validation criteria, and execution approach
- Each spec is self-contained and executable
- Use the [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) as starting point

### 2. Create Helper/Utility Scripts (When Needed)
- Build helper scripts for complex operations or reusable functionality
- Scripts can be in any language (Python, Go, Bash, Node.js, etc.)
- Focus on reusability and modularity
- Include clear CLI interfaces and documentation

### 3. Execute Tests
- Use the most appropriate execution method for each scenario:
  - **Copilot**: AI-powered test execution via GitHub Copilot CLI
  - **Scripts**: Direct Python/shell script execution with dedicated test runners

## Directory Structure

```
crawlab-test/                      # Root of test repository
├── README.md                      # This overview document
├── SPEC_TEMPLATE.md              # Template for creating new test specs
├── TESTING_SOP.md               # Detailed SOP and guidelines
├── cli.py                        # Universal CLI entry point
├── specs/                        # Test specifications (markdown)
│   ├── api/                      # API/Backend tests
│   │   ├── endpoints-validation.md
│   │   └── authentication.md
│   ├── cluster/                  # Cluster/distributed system tests
│   │   ├── CLS-001-master-worker-node-disconnection-and-reconnection-stability.md
│   │   └── CLS-002-docker-container-node-disconnection-and-recovery.md
│   ├── database/                 # Database integration tests
│   │   └── DB-001-database-integration-comprehensive-testing.md
│   ├── dependencies/             # Dependency management tests
│   │   ├── DEP-001-dependencies-installation-robustness.md
│   │   └── DEP-002-dependency-handler-network-reconnection-resilience.md
│   ├── scheduler/                # Task execution and scheduling tests
│   │   └── SCH-001-task-status-reconciliation-and-process-verification.md
│   ├── system/                   # System configuration tests
│   │   └── SYS-001-chinese-locale-support-validation.md
│   └── ui/                       # UI workflow tests
│       └── UI-001-spider-management-workflow-validation.md
├── helpers/                      # Utility scripts and tools
│   ├── api/
│   │   └── api-client.py
│   ├── cluster/
│   │   ├── node-manager.py
│   │   ├── docker-manager.py        # Docker container management
│   │   └── cluster-utils.sh
│   ├── database/
│   │   └── database-test-helper.py  # Database integration test helper
│   ├── dependencies/
│   │   ├── package-installer.py
│   │   └── env-manager.py
│   ├── scheduler/
│   │   ├── task-monitor.go
│   │   └── reconciliation-health.py
│   ├── system/
│   │   └── locale-validator.py
│   ├── ui/
│   │   ├── browser-automation.js
│   │   └── ai-interactions.ts
│   └── common/
│       ├── crawlab-client.py
│       ├── docker_utils.py          # Docker utilities
│       ├── mongodb-utils.py
│       └── test-runner.py
├── results/                      # Test execution results
└── config/                       # Configuration files
    ├── environments.yml
    └── test-config.yml
```

## Example Test Cases

We've created several example test cases to demonstrate the framework:

### Cluster Testing
- **[Node Disconnection](specs/cluster/CLS-001-master-worker-node-disconnection-and-reconnection-stability.md)**: Tests master/worker node stability during network issues
- Uses Python scripts for node management and system monitoring
- **[Docker Container Disconnection](specs/cluster/CLS-002-docker-container-node-disconnection-and-recovery.md)**: Docker-specific container disconnection and recovery testing
- Features container network isolation, pause/resume operations, and cluster recovery validation

### Scheduler Testing
- **[Task Reconciliation](specs/scheduler/SCH-001-task-status-reconciliation-and-process-verification.md)**: Comprehensive test suite for task status reconciliation
- Features zombie task detection, worker reconnection scenarios, and conservative status handling validation

### Database Testing
- **[Database Integration](specs/database/DB-001-database-integration-comprehensive-testing.md)**: Comprehensive database integration testing
- Validates connectivity and operations for MongoDB, MySQL, PostgreSQL, and Elasticsearch

### Dependency Testing  
- **[Installation Robustness](specs/dependencies/installation-robustness.md)**: Tests package installation edge cases
- Uses Python scripts for package management and environment isolation

### UI Testing
- **[Spider Management](specs/ui/spider-management.md)**: Tests complete spider lifecycle through web interface
- Uses AI tools for browser automation and natural language interactions

### Integration Testing
- **[Database Integration](specs/integration/INT-001-database-integration-comprehensive-testing.md)**: Comprehensive database integration tests
- Tests primary supported database types (MongoDB, MySQL, PostgreSQL, Elasticsearch)
- Validates connection management, metadata retrieval, schema operations, CRUD operations, and query execution
- Uses Go tests with helper scripts for service management and reporting
- **Note**: MSSQL Server is excluded from integration tests as it is not a primary supported database

## Execution Methods

### Automated Execution
```bash
# Use the test runner for automatic method selection
./test-runner.py --spec specs/infrastructure/node-disconnection.md

# Execute helper scripts directly
./helpers/infrastructure/node-manager.py --disconnect worker-1
```

### Copilot CLI Execution
```bash
# For UI tests and complex interactions
./test-runner.py --spec specs/ui/spider-management.md --method copilot

# Or use the Copilot wrapper directly
./run-with-copilot.py specs/ui/spider-management.md

# Specify a model for Copilot execution
./cli.py --spec UI-001 --backend copilot --model gpt-4o
./cli.py --spec UI-001 --backend copilot --model claude-3.5-sonnet
./cli.py --spec UI-001 --backend copilot --model o1-preview

# Automated mode for CI/CD
# Run in CI
CI=true ./test-runner.py --spec <spec-file> --method copilot
```

**Supported Models:**
- `gpt-4` - GPT-4 (standard)
- `gpt-4o` - GPT-4 Optimized (recommended for most use cases)
- `claude-3.5-sonnet` - Anthropic Claude 3.5 Sonnet
- `o1-preview` - OpenAI O1 Preview (best for complex reasoning)
- And other models supported by GitHub Copilot CLI

### Hybrid Execution
Combine multiple approaches:
1. Scripts for setup/teardown
2. Copilot CLI for UI interactions  
3. Manual for complex validations
4. Scripts for data verification

## Benefits of This Approach

1. **Flexibility**: Each test uses the most appropriate tools and methods
2. **Maintainability**: Tests are documented in readable markdown format
3. **Scalability**: Easy to add new test categories and execution methods
3. **Tool Independence**: Not locked into specific testing frameworks
4. **Copilot CLI Integration**: Specifications can be read and executed by AI
5. **Human-Friendly**: Clear documentation that anyone can understand and follow
6. **Practical**: Focuses on real-world scenarios that matter to users
7. **Docker-Compatible**: Seamless support for containerized deployments

## Docker Testing

### Prerequisites
- Docker and Docker CLI installed
- Crawlab running in Docker containers (via docker-compose or standalone)
- Network permissions for container operations

### Supported Operations
- **Container Discovery**: Automatic detection of Crawlab containers
- **Network Isolation**: Simulate network disconnections via Docker networks
- **Container Pause/Resume**: Simulate complete worker failures
- **Log Access**: Retrieve logs from any container
- **Command Execution**: Execute commands inside containers
- **Health Monitoring**: Check container and cluster health

### Environment Variables
```bash
# Override auto-detected master URL
export CRAWLAB_MASTER_URL="http://localhost:8080"

# Set API token for authentication
export CRAWLAB_API_TOKEN="your-token-here"

# Configure Docker daemon (if remote)
export DOCKER_HOST="tcp://remote-docker:2376"
```

### Docker Test Examples
```bash
# Run comprehensive Docker container test
./test-runner.py --spec specs/infrastructure/docker-container-disconnection.md

# Health check
./helpers/infrastructure/docker-manager.py --action health

# Test container network isolation
./helpers/infrastructure/docker-manager.py --action disconnect --container worker-1 --method network
sleep 30
./helpers/infrastructure/docker-manager.py --action reconnect --container worker-1

# Test container pause/resume
./helpers/infrastructure/docker-manager.py --action disconnect --container worker-2 --method pause
sleep 30
./helpers/infrastructure/docker-manager.py --action reconnect --container worker-2
```

## Getting Started

1. **Read the SOP**: Start with [TESTING_SOP.md](TESTING_SOP.md) for detailed guidelines
2. **Examine Examples**: Look at the example test specs in `specs/` directory  
3. **Try the Runner**: Use `./test-runner.py --list-specs` to see available tests
4. **Create Your First Test**: Copy `SPEC_TEMPLATE.md` and adapt it for your scenario
5. **Build Helpers**: Create utility scripts in `helpers/` as needed
6. **Execute and Iterate**: Run tests and improve based on results

## Philosophy

This framework embraces the principle that **different scenarios require different approaches**. Instead of forcing all tests into a single framework, we provide a flexible foundation that can adapt to specific testing needs while maintaining consistency in documentation and execution patterns.

The result is a practical, maintainable testing approach that grows with your needs and provides real value in ensuring system quality.

## Task Reconciliation Test Suite

A comprehensive implementation of the Task Reconciliation Service test specification (TC-INF-002) is available in the infrastructure helpers. This validates critical system stability features:

### Quick Start
```bash
# Run complete reconciliation test suite
./helpers/infrastructure/task-reconciliation-test.py --full-suite

# Test specific scenarios
./helpers/infrastructure/task-reconciliation-test.py --test zombie-detection
./helpers/infrastructure/task-reconciliation-test.py --test worker-reconnection
```

### Key Features
- **Zombie Task Detection**: Validates detection of orphaned processes vs database state
- **Conservative Status Logic**: Ensures uncertain statuses aren't falsely marked as errors  
- **Worker Reconnection**: Tests task reconciliation when nodes reconnect
- **Process Status Monitoring**: Validates gRPC process status query protocol
- **Load Testing**: Reconciliation performance under high task volumes

### Test Components
- `reconciliation-health.py` - Service health validation
- `task-baseline.py` - Create test task states
- `process-killer.py` - Simulate zombie tasks
- `reconciliation-monitor.py` - Monitor reconciliation cycles
- `status-validator.py` - Validate conservative logic
- `task-reconciliation-test.py` - Main test orchestrator

See the full specification at `specs/infrastructure/task-reconciliation.md` for detailed test scenarios and success criteria.

## Browser Chinese Locale Validation

Validates Chinese character support for browser automation (Playwright, Selenium) in containers.

```bash
# Full validation (system + browsers)
python runners/infrastructure/INF_004_chinese_locale_support_validation.py

# Skip browser tests
python runners/infrastructure/INF_004_chinese_locale_support_validation.py --skip-browsers

# Standalone browser test (inside container)
python helpers/tools/browser_chinese_test.py
```

**Tests:** System locale, Chinese fonts, Playwright rendering, Selenium rendering  
**Content:** 你好世界, 爬虫测试, 任务执行, 节点管理, 数据采集  
**Output:** Screenshots saved to `/tmp/*.png`

See `docs/BROWSER_CHINESE_LOCALE_VALIDATION.md` for details.