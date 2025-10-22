# Testing SOP (Standard Operating Procedure)

## Overview

This document provides comprehensive guidelines for creating, implementing, and executing test cases using our flexible, scenario-based testing framework. The approach prioritizes practicality and effectiveness over rigid frameworks.

## Core Philosophy

1. **Scenario-Driven**: Every test targets a specific real-world scenario that matters to users
2. **Tool-Agnostic**: Use whatever works best for each specific test case
3. **Self-Contained**: Each test spec includes everything needed to understand and execute
4. **Flexible Execution**: Support for scripts, AI tools, manual steps, or combinations
5. **Clear Documentation**: Unified format makes tests discoverable and maintainable

## SOP Steps

### 1. Create Test Specifications

#### 1.1 Choose Test Category
Determine which category your test belongs to:
- **api**: API endpoint functionality, authentication, data validation
- **cluster**: Node management, cluster stability, worker reconnection
- **database**: Database connectivity, queries, data persistence
- **dependencies**: Package installation, environment management, conflicts
- **scheduler**: Task scheduling, execution, status reconciliation
- **system**: System resources, health checks, core functionality
- **ui**: User interface workflows, usability, browser compatibility

#### 1.1.1 Special Guidelines for API Tests
**CRITICAL**: Before creating any API test spec or runner:

1. **Check the OpenAPI specification first**:
   ```bash
   # Fetch the live API spec
   curl -s http://localhost:8080/api/openapi.json | jq . > /tmp/api-spec.json
   
   # Check specific endpoint
   curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders".post'
   
   # Check request schema
   curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Create_spiderInput'
   ```

2. **Common API patterns to verify**:
   - **Request wrapper**: Some endpoints require `{"data": {...}}` wrapper
   - **Response format**: Check if data is in `.data`, `.data[0]`, or direct
   - **Array vs Object**: Task run returns array of IDs, not single object
   - **Required fields**: Check schema for required vs optional fields
   - **Endpoint variations**: `/spiders/:id/files/save` vs `/spiders/:id/files/save/batch`

3. **Example - Spider Creation**:
   ```bash
   # Check endpoint
   curl -s http://localhost:8080/api/openapi.json | jq '.paths."/spiders".post'
   # Returns: requires Create_spiderInput
   
   # Check schema
   curl -s http://localhost:8080/api/openapi.json | jq '.components.schemas.Create_spiderInput'
   # Returns: {"data": {...}} wrapper required!
   ```

4. **Document your findings**:
   - Add API endpoint details in test spec
   - Include example request/response payloads
   - Note any quirks or non-standard patterns

**Why this matters**: The OpenAPI spec is the source of truth. Guessing payload formats wastes time and leads to flaky tests.

#### 1.2 Use the Unified Template
Start with the [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md) and fill in all sections:

```bash
cp SPEC_TEMPLATE.md specs/[category]/[test-name].md
```

#### 1.3 Define Clear Success Criteria
Write measurable, objective criteria:
- ✅ **Good**: "Worker reconnection successful within 60 seconds"
- ❌ **Bad**: "System works properly after reconnection"

#### 1.4 Choose Execution Methods
For each test step, select the most appropriate method:

| Method | Best For | Example |
|--------|----------|---------|
| **script** | API calls, backend validation, system operations | API-001, CLS-003, database tests |
| **copilot** | UI workflows with dynamic discovery | UI-003 (task management) |
| **playwright** | Deterministic UI automation | Login flows, form submissions |
| **manual** | Exploratory testing, complex judgments | Usability assessment, edge cases |

**Test Category Guidelines**:
- **API tests**: Always use `script` backend with Python runners
- **Cluster tests**: Use `script` backend for performance/stress tests
- **UI tests**: Use `copilot` for flexible workflows, `playwright` for deterministic steps
- **System tests**: Use `script` backend for infrastructure validation

**Runner Location**:
- API/backend test runners: `tests/runners/[category]/[TEST-ID]_[name].py`
- UI Copilot tests: Execute via `./cli.py --spec [TEST-ID] --backend copilot`
- Playwright tests: `tests/ui-playwright/tests/[category]/[name].spec.ts`

### 2. Create Helper/Utility Scripts

#### 2.1 Determine Script Necessity
Create helper scripts when:
- Multiple test specs need similar functionality
- Complex operations require precise control
- Automated validation is needed
- System state manipulation is required
#### 2.3 Script Organization
```
tests/
├── runners/                 # Test execution scripts
│   ├── api/                # API test runners
│   │   └── API_001_*.py
│   ├── cluster/            # Cluster test runners
│   │   └── CLS_003_*.py
│   └── [category]/         # Other category runners
├── helpers/                 # Utility functions
│   ├── common/             # Shared utilities
│   │   └── utils.py        # Common helper functions
│   ├── libs/               # Library modules
│   │   └── crawlab_client.py
│   └── [category]/         # Category-specific helpers
├── specs/                   # Test specifications
│   └── [category]/         # Category folders
└── tools/                   # Testing tools
    └── report_test_result.py
```pers/
├── [category]/              # Category-specific scripts
│   ├── [function].py       # Main functionality
│   └── [function]_test.py  # Script unit tests
├── common/                 # Shared utilities
│   ├── crawlab-client.py   # API client
│   ├── db-utils.py        # Database utilities
│   └── config.py          # Configuration management
└── README.md              # Helper documentation
```

#### 2.4 Script Requirements
- **Clear CLI interface**: Use argparse, click, or similar
- **Error handling**: Graceful failure with helpful messages
- **Logging**: Appropriate log levels and output
- **Configuration**: Support environment variables and config files
- **Documentation**: Clear usage examples and parameter descriptions

### 3. Execute Test Cases

#### 3.1 Using the Test Runner CLI
The unified test runner (`cli.py`) is the recommended way to execute tests:

```bash
cd tests

# Run a specific test by ID
./cli.py --spec API-001
./cli.py --spec UI-003
./cli.py --spec CLS-003

# Run a test by name (fuzzy search)
./cli.py --spec "spider management"
./cli.py --spec "task execution"

# List all available specs
./cli.py --list-specs

# Search for specs
./cli.py --search grpc
./cli.py --search api

# Specify backend explicitly
./cli.py --spec API-001 --backend script     # Use script runner
./cli.py --spec UI-003 --backend copilot     # Use Copilot AI
./cli.py --spec UI-001 --backend playwright  # Use Playwright

# Auto-select backend (default)
./cli.py --spec API-001  # Automatically selects 'script' for API tests
```

**Backend Selection**:
- **script**: Python/Bash runners in `tests/runners/` (for API, cluster, system tests)
- **copilot**: GitHub Copilot CLI with MCP Playwright (for UI tests)
- **playwright**: Direct Playwright execution (for UI tests)
- **auto** (default): Automatically selects best backend based on test category

#### 3.2 Direct Script Execution
For API and backend tests with Python runners:

```bash
cd tests/runners/api
./API_001_task_execution_with_file_sync.py

cd tests/runners/cluster
./CLS_003_grpc_streaming_performance.py
```

#### 3.3 Manual Execution
When human judgment is required:
1. Open the test specification markdown file
2. Follow each step sequentially
3. Verify validation criteria manually
4. Document results using `tools/report_test_result.py`

## Guidelines for Test Creation

### Test Specification Quality

#### Mandatory Elements
- **Clear scenario description**: What and why you're testing
- **Comprehensive prerequisites**: Everything needed before starting
- **Detailed execution steps**: Unambiguous instructions
- **Objective success criteria**: Measurable outcomes
- **Cleanup procedures**: How to restore initial state

#### Best Practices
- **One scenario per spec**: Keep tests focused and manageable
- **Environment agnostic**: Tests should work in different environments
- **Idempotent**: Running multiple times shouldn't cause issues
- **Time-bounded**: Include realistic duration estimates
- **Version controlled**: Track changes and maintain history

### Helper Script Quality

#### Code Standards
- **Error handling**: Graceful failure with meaningful messages
- **Logging**: Appropriate verbosity levels
- **Documentation**: Clear docstrings and usage examples
- **Testing**: Unit tests for complex logic
- **Configuration**: External configuration support

#### Reusability
- **Modular design**: Break functionality into reusable components
- **Parameter-driven**: Support different scenarios via parameters
- **Library-friendly**: Can be imported and used by other scripts
- **Standard interfaces**: Consistent CLI patterns across scripts

### Execution Best Practices

#### Before Testing
1. **Environment preparation**: Ensure prerequisites are met
2. **Baseline establishment**: Document initial system state
3. **Resource availability**: Check disk space, memory, network
4. **Permission verification**: Ensure adequate access rights

#### During Testing
1. **Progress monitoring**: Track execution and log appropriately
2. **State validation**: Verify intermediate states match expectations
3. **Error collection**: Capture detailed error information
4. **Artifact preservation**: Save logs, screenshots, data for analysis

#### After Testing
1. **Cleanup execution**: Restore system to initial state
2. **Result documentation**: Record outcomes and observations
3. **Issue reporting**: Document any problems discovered
4. **Spec updates**: Update specifications based on learnings

## Example Workflows

### Creating a New API Test

1. **Check OpenAPI spec first**: 
   ```bash
   curl -s http://localhost:8080/api/openapi.json | jq '.paths."/endpoint"'
   ```
2. **Create the spec**: `specs/api/API-002-new-feature.md`
3. **Document API details**: Include request/response formats from OpenAPI spec
4. **Create Python runner**: `runners/api/API_002_new_feature.py`
5. **Execute and validate**: `./cli.py --spec API-002`
6. **Verify fast execution**: Should complete in < 30 seconds

### Creating a New Cluster Test

1. **Identify the scenario**: "Test gRPC streaming under high load"
2. **Create the spec**: `specs/cluster/CLS-004-grpc-load-test.md`
3. **Create Python runner**: `runners/cluster/CLS_004_grpc_load_test.py`
4. **Use helper libraries**: Import from `helpers/libs/` for common operations
5. **Execute and validate**: `./cli.py --spec CLS-004`
6. **Document performance**: Include timing and resource usage

### Creating a New UI Test

1. **Identify the workflow**: "User creates spider, uploads files, runs task"
2. **Create the spec**: `specs/ui/UI-004-spider-workflow.md`
3. **Plan execution approach**:
   - For dynamic workflows: Use Copilot backend with high-level instructions
   - For deterministic flows: Use Playwright with explicit selectors
4. **Add UI-specific notes**: Document Element Plus component interactions
5. **Execute**: `./cli.py --spec UI-004 --backend copilot`
6. **Optimize for speed**: Prefer API validation over UI when possible

## Troubleshooting

### Common Issues

#### Test Spec Problems
- **Ambiguous instructions**: Add more specific details and examples
- **Missing prerequisites**: Document all required setup steps
- **Unclear success criteria**: Make criteria more objective and measurable

#### Helper Script Issues
- **Environment dependencies**: Use virtual environments and dependency management
- **Permission problems**: Document required permissions and setup
- **Configuration issues**: Provide clear configuration examples

#### Execution Problems
- **Environment inconsistencies**: Use containerization or environment management
- **Timing issues**: Add appropriate waits and retries
- **Resource constraints**: Monitor and handle resource limitations

### Getting Help

1. **Check existing specs**: Look for similar test cases
2. **Review helper documentation**: Check if utilities already exist
3. **Consult team members**: Ask for guidance on approach
4. **Iterate and improve**: Start simple and enhance based on learnings

## Conclusion

This SOP provides the foundation for effective, practical testing at Crawlab. By following these guidelines, you can create robust, maintainable test cases that provide real value in ensuring system quality and reliability.

Remember: The goal is not perfect test coverage, but practical validation of critical scenarios that matter to users and the business.