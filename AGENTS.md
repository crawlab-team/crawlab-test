# Crawlab Test - AI Agent Guidelines

## 🎯 Testing Principles

**Test Quality**: Tests should be deterministic, maintainable, and provide real value.

- **Spec-driven development**: Write specifications before implementation
- **Deterministic execution**: Same test → Same result every time
- **Reusable components**: DRY principle - write once, use everywhere
- **Clear documentation**: Each test should be self-explanatory

### ⚠️ CRITICAL: NO UNNECESSARY DOCUMENTATION
**DO NOT create, update, or maintain any of the following:**
- Summary documents (e.g., `SUMMARY.md`, `CHANGES.md`, `UPDATES.md`)
- Progress tracking files (e.g., `PROGRESS.md`, `STATUS.md`)
- Redundant documentation that duplicates code comments
- Session notes, implementation logs, or work journals

**Only documentation allowed:**
- Test specifications in `specs/` following [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)
- Updates to critical docs (README, TESTING_SOP) when materially outdated
- Code comments explaining complex test logic
- Helper script documentation when adding new utilities

**For multi-session tasks:**
- Use the built-in `manage_todo_list` tool to track progress
- Git commit messages provide the historical record
- If you must leave notes, use a `tmp/` directory (add to .gitignore)

**When in doubt: Don't create documentation. Write tests.**

## 🏗️ Repository Structure

### Directory Layout
- **`specs/`**: Test specifications in markdown (api, cluster, database, dependencies, scheduler, system, ui)
- **`runners/`**: Python test runners that execute specifications
- **`helpers/`**: Reusable utilities and helper scripts
- **`backends/`**: Backend implementations (script, copilot, playwright)
- **`core/`**: Core modules (config, spec finder, docker detection, result handler)
- **`ui-playwright/`**: TypeScript/Playwright UI test suite
- **`docs/`**: Testing framework documentation
- **`results/`**: Test execution results (gitignored)

## 🧪 Testing Workflow

### Before Creating Tests

1. **Check existing patterns**: Search for similar test specs and runners
2. **Understand the test category**: API, cluster, database, dependencies, scheduler, system, or UI?
3. **Choose the right backend**: Script (Python), Copilot (AI-assisted), or Playwright (TypeScript UI)
4. **Review TESTING_SOP.md**: Follow established patterns and guidelines

### Test Categories

- **API tests**: Backend API validation, endpoint testing, data integrity
  - ALWAYS check `http://localhost:8080/api/openapi.json` before writing API tests
  - See [specs/api/README.md](specs/api/README.md) for API testing guide
  - Verify request/response formats, wrappers, and field requirements
- **Cluster tests**: Distributed system behavior, node disconnection/reconnection
- **Database tests**: Database integration, connection management, CRUD operations
- **Dependencies tests**: Package installation, dependency management
- **Scheduler tests**: Task execution, reconciliation, process verification
- **System tests**: Configuration, locale support, system-level operations
- **UI tests**: End-to-end user workflows, browser automation

### Test Execution Methods

| Backend | Best For | Tools |
|---------|----------|-------|
| **script** | API, cluster, system tests | Python runners with helper libraries |
| **copilot** | Complex scenarios, AI-assisted execution | GitHub Copilot CLI |
| **playwright** | UI tests, browser automation | TypeScript/Playwright framework |

### Creating New Tests

1. **Write specification**: Copy [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) to `specs/[category]/[TEST-ID]-[name].md`
2. **Implement runner** (if using script backend): Create `runners/[category]/[TEST-ID]_[name].py`
3. **Add helpers** (if needed): Create reusable utilities in `helpers/[category]/`
4. **Test locally**: Run `uv run ./cli.py --spec [TEST-ID]`
5. **Verify determinism**: Run test multiple times to ensure consistent results

### Testing Best Practices

- **Fast validation**: Prefer API tests (10s) over UI tests (10-15min) for backend validation
- **Deterministic UI tests**: Use Python/Playwright test runners, not autonomous AI
- **Docker support**: Tests auto-detect Docker environments automatically
- **Error handling**: Tests should handle failures gracefully and report clear errors
- **Cleanup**: Always clean up test data, containers, and processes after tests
- **Screenshots**: UI tests should capture screenshots at critical steps
- **Logging**: Detailed logging for debugging failed test runs

## 🔧 Development Standards

### Python Code Standards
- **Python version**: 3.9+ required (for grpcio-tools + protobuf 6.x compatibility)
- **Type hints**: Use type annotations for function signatures
- **Error handling**: Always handle exceptions explicitly
- **Logging**: Use Python logging module for observability
- **Dependencies**: Use `uv` for dependency management (pip fallback available)

### TypeScript Code Standards (UI tests)
- **TypeScript**: Strict mode enabled
- **Playwright**: Follow Playwright best practices
- **Page Objects**: Use page object pattern for maintainability
- **Async/await**: Proper async handling for all browser operations

### Test Specification Standards
- **Markdown format**: Follow [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) structure
- **Clear objectives**: Define what the test validates
- **Prerequisites**: List all required setup steps
- **Step-by-step**: Detailed execution steps
- **Success criteria**: Explicit validation criteria
- **Cleanup**: Document cleanup procedures

## 🚀 Running Tests

### Quick Start
```bash
# Install dependencies (recommended: uv)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv if needed
uv sync                              # Fast, reproducible install
./setup-playwright.sh                # For UI tests

# Or use pip (fallback)
pip install -r requirements.txt

# List available tests
uv run ./cli.py --list-specs

# Run a specific test
uv run ./cli.py --spec UI-001
uv run ./cli.py --spec CLS-001 --backend script
uv run ./cli.py --spec DB-001 --backend copilot --model gpt-4o

# Search for tests
uv run ./cli.py --search docker

# Note: Scripts work without 'uv run' if dependencies installed
```

### CI/CD Integration
```bash
# Run in CI mode with timeout
uv run ./cli.py --spec UI-001 --ci --timeout 15

# Dry run to preview execution
uv run ./cli.py --spec UI-001 --dry-run
```

### Docker Testing
```bash
# Check Docker environment
./helpers/tools/docker_manager.py --action health

# List Crawlab containers
./helpers/tools/docker_manager.py --action list

# Test container operations
./helpers/tools/docker_manager.py --action disconnect --container worker-1
```

## 📖 Decision Framework

1. **Does a similar test exist?** → Use it as a template
2. **Which backend fits best?** → Script for API/system, Playwright for UI, Copilot for complex scenarios
3. **Is it deterministic?** → Non-negotiable for reliable testing
4. **Can it run in Docker?** → Most Crawlab deployments use Docker
5. **Is it maintainable?** → Code should be clear and well-documented
6. **Does it provide value?** → Test real-world scenarios that matter

## 🔗 Integration with Crawlab Pro

This repository tests [Crawlab Pro](https://github.com/crawlab-team/crawlab-pro):

- **API Endpoint**: `http://localhost:8080` (auto-detected from Docker if running)
- **Authentication**: `admin:admin` (default, configurable in `config.json`)
- **Test Data**: Tests create and clean up their own data
- **Independence**: Tests should not depend on external state

For Crawlab Pro development guidelines, see [crawlab-pro/AGENTS.md](https://github.com/crawlab-team/crawlab-pro/blob/develop/AGENTS.md).
