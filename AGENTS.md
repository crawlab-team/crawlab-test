# Crawlab Test - AI Agent Guidelines

## 🎯 Core Principles

**Test Quality**: Deterministic, maintainable, and valuable tests only.

**Key Philosophies**:
- **Spec-driven**: Write specifications before implementation
- **Deterministic**: Same test → Same result every time
- **DRY**: Reusable components over duplication
- **No unnecessary docs**: Code and tests are the documentation

### ⚠️ Documentation Policy

**FORBIDDEN**:
- Summary/progress files (`SUMMARY.md`, `CHANGES.md`, `PROGRESS.md`)
- Session notes, implementation logs, work journals

**ALLOWED**:
- Test specs in `specs/` following [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)
- Updates to critical docs when materially outdated
- Helper script documentation
- Code comments for complex logic only

**Multi-session tasks**: Use `manage_todo_list` tool (persists automatically)

## 🏗️ Repository Structure

**Key Directories**:
- `specs/` - Test specifications (api, cluster, database, dependencies, scheduler, system, ui)
- `runners/` - Python test runners that execute specifications
- `helpers/` - Reusable utilities organized by purpose:
  - `api/` - API client helpers (auth, spider, task, etc.)
  - `infrastructure/` - Core infrastructure (API client, Docker, database, system utilities)
  - `testing/` - Testing tools (monitors, simulators, validators, managers)
  - `cluster/` - Cluster-specific utilities (gRPC, file sync)
  - `ui/` - UI test helpers (actions, browser, validators)
  - `suites/` - Reusable test suites
- `backends/` - Backend implementations (script, copilot, playwright)
- `docs/` - Testing framework documentation
- `core/` - Core framework (config, parallel execution, spec finder)

## 🧪 Testing Workflow

### Test Categories

Choose the right category and backend:

| Category | Backend | Best For |
|----------|---------|----------|
| **API** | script | Backend validation, endpoint testing (fast: ~10s) |
| **Cluster** | script | Distributed system, node operations |
| **Database** | script | DB integration, connection management |
| **Scheduler** | script | Task execution, process verification |
| **UI** | playwright | End-to-end workflows (slow: ~10-15min) |

### Creating Tests

1. **Write spec**: `specs/[category]/[TEST-ID]-[name].md` (use [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md))
2. **Implement runner**: `runners/[category]/[TEST-ID]_[name].py` (if script backend)
3. **Test locally**: `uv run ./cli.py --spec [TEST-ID]`
4. **Verify determinism**: Run multiple times

### Critical: API Testing

**ALWAYS check OpenAPI spec first**: `http://localhost:8080/api/openapi.json`

```bash
# Check endpoint format
curl -s http://localhost:8080/api/openapi.json | jq '.paths."/tasks".patch'
```

**Common patterns**:
- Some endpoints need `{"data": {...}}` wrapper, others don't
- Task run/restart returns **array of IDs**, not single object
- Batch operations: field name is `"update"` not `"data"`
- DELETE can use JSON body: `{"ids": [...]}`
- Field names are **case-sensitive**

📖 **Full details**: [specs/api/README.md](specs/api/README.md) | [docs/API_TEST_TROUBLESHOOTING.md](docs/API_TEST_TROUBLESHOOTING.md)

## 🔧 Code Standards

### Python (Test Runners)
- **Python 3.9+** required
- **Type hints** for function signatures
- **Error handling**: Handle exceptions explicitly
- **Dependencies**: Use `uv` for management (pip fallback available)

### TypeScript (UI Tests)
- **Strict mode** enabled
- **Page object pattern** for maintainability
- **Async/await** for all browser operations

### Test Specifications
- Follow [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md)
- Clear objectives and success criteria
- Detailed execution steps
- Document cleanup procedures

## 🚀 Running Tests

### Quick Commands
```bash
# List/search tests
uv run ./cli.py --list-specs
uv run ./cli.py --search docker

# Run specific test
uv run ./cli.py --spec UI-001
uv run ./cli.py --spec CLS-001 --backend script

# CI mode with timeout
uv run ./cli.py --spec UI-001 --ci --timeout 15
```

**Full documentation**: [README.md](README.md) | [TESTING_SOP.md](TESTING_SOP.md)

## 🔍 Troubleshooting Test Failures

### Quick Workflow

**For API test failures:**
1. ✅ Check OpenAPI spec first: `curl -s http://localhost:8080/api/openapi.json | jq '.paths."/endpoint"'`
2. Compare with helper code implementation
3. Check infrastructure (Docker, databases, network)
4. Only then read backend Go code

**For CI/CD failures:**
1. Download artifacts (screenshots, logs, system-info)
2. Reproduce locally with `--ci` flag
3. Compare local vs CI environment
4. Check for timing/resource issues

**DO NOT:**
- ❌ Guess API formats without checking spec
- ❌ Batch-update todos (mark individually)
- ❌ Skip investigation and re-run blindly

📖 **Full guides**: 
- [API Test Troubleshooting](docs/API_TEST_TROUBLESHOOTING.md)
- [CI/CD Troubleshooting](docs/CI_TROUBLESHOOTING.md)

## 📋 Decision Framework

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
