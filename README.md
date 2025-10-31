# Crawlab Test

Comprehensive automated testing framework for [Crawlab](https://github.com/crawlab-team/crawlab) and [Crawlab Pro](https://github.com/crawlab-team/crawlab-pro).

> **Note**: This is a standalone testing repository that can be used independently or alongside the main Crawlab repositories. It was extracted from `crawlab-pro/tests` for better management and maintainability.

> **Important**: Most tests require **Crawlab Pro** features (gRPC, advanced clustering, etc.). The default configuration uses `crawlabteam/crawlab-pro:develop`. If you need to test with Community Edition, set `CRAWLAB_IMAGE=crawlabteam/crawlab:develop`.

## Overview

Spec-driven testing framework for Crawlab with multiple execution backends:
- **Script backend**: Fast Python/shell test runners for API, cluster, and system tests
- **Copilot backend**: AI-powered execution for complex scenarios
- **Playwright backend**: Deterministic UI automation with TypeScript

## Key Features

- **Unified CLI**: Single `cli.py` entry point for all tests
- **Markdown Specs**: Human-readable test specifications
- **Modular Architecture**: Clean separation between core, backends, and helpers
- **Docker Support**: Auto-detects containerized deployments
- **CI/CD Ready**: GitHub Actions integration with smart category detection

## Quick Start

### Initial Setup

Before running tests, install dependencies using `uv` (recommended) or `pip`:

#### Using uv (Recommended - Fast & Reproducible)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (including Python if needed)
uv sync

# Install crawlab-test package in editable mode (REQUIRED)
uv pip install -e .

# Install Playwright browsers (required for UI tests)
./setup-playwright.sh

# Or install with system dependencies (may require sudo)
./setup-playwright.sh --with-deps

# Or install all browsers (chromium, firefox, webkit)
./setup-playwright.sh --all
```

#### Using pip (Fallback)

```bash
# Install crawlab-test package in editable mode (REQUIRED - includes all dependencies)
pip install -e .

# Install Playwright browsers
./setup-playwright.sh
```

### Basic Usage

```bash
# List available tests
uv run ./cli.py --list-specs

# List tests by category
uv run ./cli.py --list-specs --category api

# List tests for multiple categories
uv run ./cli.py --list-specs --category api ui cluster

# Run a specific test (auto-detects best backend)
uv run ./cli.py --spec UI-001

# Search for tests
uv run ./cli.py --search docker

# Run with specific backend
uv run ./cli.py --spec API-001 --backend script
uv run ./cli.py --spec UI-001 --backend copilot --model gpt-4o

# CI mode
uv run ./cli.py --spec CLS-001 --ci --timeout 30
```

**Note**: Scripts work without `uv run` prefix if dependencies are installed via pip.

## Architecture

```
cli.py (Main Entry Point)
├── Core: spec_finder, config, docker_detector, result_handler
└── Backends: script, copilot, playwright
```

**Backend Auto-Selection**:
1. Script backend if runner exists in `runners/`
2. Playwright backend for UI tests
3. Copilot backend as fallback

📖 **Details**: See [docs/architecture.md](docs/architecture.md) for technical deep-dive

## Docker Support

Auto-detects Docker containers and API endpoints. The test framework uses **Crawlab Pro** by default.

### Starting Test Environment

```bash
# Start Crawlab Pro services (default: develop tag)
docker compose -f docker-compose.test.yml up -d

# Or specify a different tag
CRAWLAB_IMAGE=crawlabteam/crawlab-pro:latest docker compose -f docker-compose.test.yml up -d

# Or use Community Edition (limited features, some tests will fail)
CRAWLAB_IMAGE=crawlabteam/crawlab:develop docker compose -f docker-compose.test.yml up -d

# Check service status
docker compose -f docker-compose.test.yml ps
```

### Container Management

Use `helpers/testing/managers/docker_manager.py` for container operations:

```bash
./helpers/testing/managers/docker_manager.py --action health
./helpers/testing/managers/docker_manager.py --action list
./helpers/testing/managers/docker_manager.py --action disconnect --container worker-1
```

### Diagnostics Collection

Collect Docker logs and system diagnostics for troubleshooting:

```bash
# Collect all diagnostics (logs, system info, network config)
./helpers/testing/managers/collect_diagnostics.py

# Specify output directory
./helpers/testing/managers/collect_diagnostics.py --output-dir /tmp/diagnostics

# Collect logs from specific containers only
./helpers/testing/managers/collect_diagnostics.py --containers master worker

# Use custom namespace (for CI environments)
./helpers/testing/managers/collect_diagnostics.py --namespace crawlab_ci_12345
```

**Collected artifacts include**:
- Container logs (master, worker, mongo, etc.)
- Container inspect data (JSON)
- Docker Compose service status
- Network configuration
- System information (disk, memory, Docker stats)

**Note**: In GitHub Actions, diagnostics are automatically collected on test failure and uploaded as artifacts.

## Copilot Backend

AI-powered test execution with GitHub Copilot CLI. Automatically configures MCP (Model Context Protocol) for Playwright tools.

```bash
# Copilot mode with specific model
uv run ./cli.py --spec UI-001 --backend copilot --model gpt-4o
```

📖 **Details**: See [MCP_SETUP.md](MCP_SETUP.md) for configuration

## Creating Tests

1. **Write spec**: Copy [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) to `specs/[category]/`
2. **Create runner** (optional): Python script in `runners/[category]/`
3. **Execute**: `./cli.py --spec [TEST-ID]`

📖 **Full guide**: See [TESTING_SOP.md](TESTING_SOP.md) for detailed procedures

## Directory Structure

```
crawlab-test/
├── cli.py                  # Main entry point
├── specs/                  # Test specifications
│   ├── api/               # API tests
│   ├── cluster/           # Cluster tests
│   ├── database/          # Database tests
│   └── ui/                # UI tests
├── runners/               # Test execution scripts
├── helpers/               # Reusable utilities
├── backends/              # Execution backends
├── core/                  # Core modules
└── docs/                  # Documentation
```

## Test Categories

Tests are organized by **category** (high-level test type):

- **API**: Backend endpoints, authentication, data validation
- **Integration**: Cross-system integration tests
- **Performance**: Load testing, pressure tests, long-term stability
- **Reliability**: Resilience, recovery, graceful shutdown testing
- **UI**: Web interface workflows, browser automation

List available tests: `./cli.py --list-specs` (organized by category and suite)
Filter by category: `./cli.py --list-specs --category api`

### Recently Added Tests (2025-10-31)

**REL-006: Graceful Shutdown and Process Termination** ✅
- Validates master/worker graceful shutdown with SIGTERM
- Tests task cancellation process termination
- Detects zombie processes
- Addresses bugs #1609 (task killing) and #1584 (master shutdown)
- Run: `uv run ./cli.py --spec REL-006`

**PERF-003: Long-Term Stability and Memory Leak Detection** ✅
- 24-48 hour continuous monitoring
- Memory growth analysis using linear regression
- Goroutine and connection pool leak detection
- Automated baseline establishment and cleanup validation
- Addresses bug #1600 (memory leaks)
- Run: `uv run python crawlab_test/runners/performance/PERF_003_long_term_stability.py --duration 24h`
- **Note**: This is a long-running test (24+ hours), run with caution

## Documentation

- **[TESTING_SOP.md](TESTING_SOP.md)** - Standard operating procedures
- **[SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)** - Test specification template
- **[CI_INTEGRATION.md](CI_INTEGRATION.md)** - GitHub Actions integration
- **[docs/](docs/)** - Technical deep-dives and guides

## CI/CD Integration

GitHub Actions automatically runs tests on PR. Smart category detection runs only affected tests.

```yaml
# Manually trigger workflow
workflow_dispatch:
  inputs:
    category: [api, cluster, database, ui, ...]
    spec_id: UI-001
```

📖 **Full guide**: See [CI_INTEGRATION.md](CI_INTEGRATION.md)

