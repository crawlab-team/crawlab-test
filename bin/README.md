# Test Management Tools

This directory contains helper scripts for managing test specifications and runners.

## manage-test.py

A comprehensive tool for creating, listing, validating, and managing test specs and runners with proper formatting and numbering control.

### Features

- **Auto-numbering**: Automatically assigns next available test ID or detects gaps
- **Format control**: Enforces consistent naming and structure
- **Validation**: Checks specs for required sections and proper format
- **Dual creation**: Can create both spec and runner in one command
- **Category support**: Handles all test categories (api, ui, cluster, etc.)

### Quick Start

```bash
# List all tests in a category
./bin/manage-test.py list --category api

# Find next available ID (checks for gaps)
./bin/manage-test.py next-id --category api

# Create a new test spec
./bin/manage-test.py create --category api --title "User Settings" --priority high

# Create spec with specific ID and runner
./bin/manage-test.py create --category api --id 025 --title "Data Export" --with-runner

# Validate existing spec
./bin/manage-test.py validate specs/api/API-001-task-execution.md

# Create runner from existing spec
./bin/manage-test.py create-runner specs/api/API-018-something.md
```

### Commands

#### create

Create a new test specification with proper formatting.

**Required:**
- `--category`: Test category (api, cluster, database, integration, performance, reliability, system, ui)
- `--title`: Human-readable test title

**Optional:**
- `--id`: Specific test number (auto-assigned if not provided, will find gaps)
- `--priority`: Test priority (critical, high, medium, low) [default: medium]
- `--complexity`: Test complexity (simple, moderate, complex) [default: moderate]
- `--backend`: Test backend (script, copilot, playwright) [default: script]
- `--duration`: Expected duration [default: "5-10 minutes"]
- `--with-runner`: Also create runner script

**Examples:**
```bash
# Auto-number, basic spec
./bin/manage-test.py create --category api --title "User Management"

# Specific ID with runner
./bin/manage-test.py create --category ui --id 010 --title "Login Flow" --backend playwright --with-runner

# Critical test with custom settings
./bin/manage-test.py create --category reliability --title "Database Failover" --priority critical --complexity complex --duration "30-60 minutes"
```

#### list

List all existing tests, showing which have runners.

**Optional:**
- `--category`: Filter by specific category (shows all if not provided)

**Examples:**
```bash
# List all tests
./bin/manage-test.py list

# List only API tests
./bin/manage-test.py list --category api
```

**Output:**
```
API Tests (API-XXX):
--------------------------------------------------------------------------------
  API-001: task-execution-with-file-sync                      [Runner: ✗]
  API-002: authentication-token-management                    [Runner: ✓]
  ...
```

#### next-id

Find the next available test ID for a category. Detects gaps in numbering.

**Required:**
- `--category`: Test category

**Examples:**
```bash
./bin/manage-test.py next-id --category api
# Output: Next available ID: API-018
```

#### validate

Validate a test specification file format.

**Required:**
- `spec_file`: Path to spec file

**Examples:**
```bash
./bin/manage-test.py validate specs/api/API-001-task-execution.md
```

**Checks:**
- Filename format (PREFIX-NNN-title.md)
- Title format (# PREFIX-NNN - Title)
- Required sections (Metadata, Scenario, Prerequisites, etc.)
- Required metadata fields (Category, Priority, Complexity, Duration)

#### create-runner

Create a runner script from an existing spec file.

**Required:**
- `spec_file`: Path to spec file

**Examples:**
```bash
./bin/manage-test.py create-runner specs/api/API-010-database.md
```

Creates: `crawlab_test/runners/api/API-010_database.py`

### File Naming Conventions

The tool enforces these naming patterns:

**Spec files:**
- Format: `{PREFIX}-{NNN}-{slug}.md`
- Example: `API-001-task-execution-with-file-sync.md`
- Location: `specs/{category}/`

**Runner files:**
- Format: `{PREFIX}-{NNN}_{slug}.py`
- Example: `API_001_task_execution_with_file_sync.py`
- Location: `crawlab_test/runners/{category}/`

**Category prefixes:**
- api → API
- cluster → CLS
- database → DB
- integration → INT
- performance → PERF
- reliability → REL
- system → SYS
- ui → UI

### ID Assignment

The tool intelligently assigns test IDs:

1. **Auto-assign**: Finds next available number, detecting gaps
   - If tests exist: 001, 002, 004 → assigns 003 (fills gap)
   - If no gaps: 001, 002, 003 → assigns 004

2. **Manual assign**: Use `--id` flag for specific number
   - Validates that ID doesn't already exist
   - Useful for reserving specific numbers

### Generated Content

**Spec files** include:
- Proper test ID and title
- Metadata section with all required fields
- Template sections (Scenario, Prerequisites, Steps, etc.)
- Current date in History section

**Runner files** include:
- Proper test ID and title in docstring
- Standard imports (helpers, assertions)
- Authentication boilerplate
- Step printing utility
- Error handling and cleanup
- Executable permissions

### Integration with AI Agents

This tool provides **controlled test creation** for AI agents:

**Benefits:**
- No more manual ID assignment
- Consistent formatting
- Enforced structure
- Gap detection
- Validation before use

**Usage in AI workflows:**
1. AI checks next ID: `./bin/manage-test.py next-id --category api`
2. AI creates test: `./bin/manage-test.py create --category api --title "..." --with-runner`
3. AI validates: `./bin/manage-test.py validate specs/api/API-XXX-...md`
4. AI implements test logic in generated runner

### Best Practices

1. **Always validate** specs after manual edits
2. **Use gaps** instead of always taking max + 1
3. **Create runners** when creating specs (`--with-runner`)
4. **Set priority** appropriately (affects CI execution order)
5. **Choose backend** based on what you're testing:
   - `script`: API/backend tests (fast, reliable)
   - `playwright`: UI tests (slower, visual)
   - `copilot`: Complex multi-step scenarios

### Troubleshooting

**Error: "Test ID already exists"**
- Check with `list` command
- Use different ID or let it auto-assign

**Error: "Invalid category"**
- Check available categories: api, cluster, database, integration, performance, reliability, system, ui
- Use lowercase

**Validation fails on existing spec**
- Spec may be using old format
- Check against SPEC_TEMPLATE.md
- Ensure required sections exist

**Runner not executable**
- Script automatically sets +x
- If needed: `chmod +x crawlab_test/runners/category/TEST_ID_name.py`

### Examples

#### Create API test with runner
```bash
./bin/manage-test.py create \
  --category api \
  --title "Data Export Functionality" \
  --priority high \
  --complexity moderate \
  --duration "5-10 minutes" \
  --with-runner
```

#### Create UI test (specific ID, no runner yet)
```bash
./bin/manage-test.py create \
  --category ui \
  --id 010 \
  --title "Login Flow" \
  --backend playwright \
  --priority critical \
  --complexity simple

# Create runner later
./bin/manage-test.py create-runner specs/ui/UI-010-login-flow.md
```

#### Find gaps and fill them
```bash
# Find next (will show gap if exists)
./bin/manage-test.py next-id --category api

# Create test to fill gap
./bin/manage-test.py create --category api --title "Fill Gap Test"
```

#### Batch validation
```bash
# Validate all specs in category
for spec in specs/api/*.md; do
  if [[ $(basename "$spec") != "README.md" ]]; then
    ./bin/manage-test.py validate "$spec"
  fi
done
```

### See Also

- [SPEC_TEMPLATE.md](../SPEC_TEMPLATE.md) - Template for test specifications
- [TESTING_SOP.md](../TESTING_SOP.md) - Standard operating procedures for testing
- [AGENTS.md](../AGENTS.md) - Guidelines for AI agents working with tests
