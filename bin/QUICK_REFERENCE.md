# Test Management Quick Reference

## Common Commands

```bash
# List all tests
./bin/manage-test.py list

# List tests by category
./bin/manage-test.py list --category api

# Find next available ID
./bin/manage-test.py next-id --category api

# Create spec only
./bin/manage-test.py create --category api --title "User Settings"

# Create spec + runner
./bin/manage-test.py create --category api --title "Data Export" --with-runner

# Create with specific ID
./bin/manage-test.py create --category api --id 025 --title "Analytics" --with-runner

# Validate spec
./bin/manage-test.py validate specs/api/API-001-task-execution.md

# Create runner from existing spec
./bin/manage-test.py create-runner specs/api/API-018-something.md
```

## Categories & Prefixes

| Category | Prefix | Usage |
|----------|--------|-------|
| api | API | Backend API tests |
| integration | INT | Integration tests |
| performance | PERF | Performance tests |
| reliability | REL | Reliability/resilience tests |
| ui | UI | UI/frontend tests |

## Options

### Priority
- `critical` - Must pass, blocks release
- `high` - Important functionality
- `medium` - Standard tests (default)
- `low` - Nice-to-have

### Complexity
- `simple` - Straightforward, few steps
- `moderate` - Multi-step, standard (default)
- `complex` - Many steps, intricate logic

### Backend
- `script` - Python script runner (default, fast)
- `playwright` - Browser automation (UI tests)
- `copilot` - AI-driven complex scenarios

## File Locations

```
specs/{category}/{PREFIX}-{NNN}-{slug}.md
crawlab_test/runners/{category}/{PREFIX}_{NNN}_{slug}.py
```

Examples:
- `specs/api/API-001-task-execution.md`
- `crawlab_test/runners/api/API_001_task_execution.py`

## Workflow

1. **Check what exists**: `./bin/manage-test.py list --category api`
2. **Find next ID**: `./bin/manage-test.py next-id --category api`
3. **Create test**: `./bin/manage-test.py create --category api --title "..." --with-runner`
4. **Validate**: `./bin/manage-test.py validate specs/api/API-XXX-....md`
5. **Implement**: Edit the generated runner script
6. **Test**: `./cli.py --spec API-XXX`
