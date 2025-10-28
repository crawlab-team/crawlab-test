# Implementation Guide: Pip Packaging Migration

**Goal**: Convert crawlab-test to installable package with clean imports.

**Time estimate**: 8-10 hours

**Difficulty**: Medium (mostly mechanical changes)

---

## Quick Start

```bash
# 1. Create feature branch
git checkout -b feature/pip-packaging

# 2. Follow steps below
# 3. Test locally
# 4. Push and verify CI
# 5. Create PR
```

---

## Step-by-Step Implementation

### Step 1: Create Package Structure (30 min)

```bash
# Create package directory
mkdir crawlab_test

# Move modules (use git mv to preserve history)
git mv backends crawlab_test/
git mv core crawlab_test/
git mv helpers crawlab_test/
git mv runners crawlab_test/

# Create root __init__.py
cat > crawlab_test/__init__.py << 'EOF'
"""
Crawlab Test Framework

Comprehensive automated testing for Crawlab and Crawlab Pro.
"""

__version__ = "1.0.0"
__author__ = "Crawlab Team"

# Core modules
from .core import Config, SpecFinder, DockerDetector, ResultHandler

# Backends
from .backends import ScriptBackend, CopilotBackend, PlaywrightBackend

__all__ = [
    "Config",
    "SpecFinder", 
    "DockerDetector",
    "ResultHandler",
    "ScriptBackend",
    "CopilotBackend",
    "PlaywrightBackend",
]
EOF

# Verify structure
tree -L 2 crawlab_test/
```

Expected structure:
```
crawlab_test/
├── __init__.py
├── backends/
├── core/
├── helpers/
└── runners/
```

### Step 2: Update pyproject.toml (15 min)

```bash
# Edit pyproject.toml
```

Key changes:
```toml
[tool.hatch.build.targets.wheel]
packages = ["crawlab_test"]  # CHANGE: Enable package

[tool.uv]
package = true  # CHANGE: Enable package mode

[project.scripts]
crawlab-test = "crawlab_test.cli:main"  # NEW: CLI entry point (optional)
```

### Step 3: Update Imports - Automated (2 hours)

Use find-replace across all Python files:

**Pattern 1**: Update absolute imports
```bash
# Find all Python files and update imports
find crawlab_test -name "*.py" -type f -print0 | xargs -0 sed -i.bak \
  -e 's/^from helpers\./from crawlab_test.helpers./g' \
  -e 's/^from backends\./from crawlab_test.backends./g' \
  -e 's/^from core\./from crawlab_test.core./g' \
  -e 's/^import helpers\./import crawlab_test.helpers./g' \
  -e 's/^import backends\./import crawlab_test.backends./g' \
  -e 's/^import core\./import crawlab_test.core./g'

# Also update cli.py at root
sed -i.bak \
  -e 's/^from core import/from crawlab_test.core import/g' \
  -e 's/^from backends import/from crawlab_test.backends import/g' \
  cli.py
```

**Pattern 2**: Remove sys.path manipulations
```bash
# Find and remove sys.path.insert lines
find crawlab_test -name "*.py" -type f -exec sed -i.bak \
  '/sys\.path\.insert/d' {} \;

# Remove now-unnecessary Path imports used only for sys.path
# (Manual review recommended for this)
```

**Verification**:
```bash
# Check no sys.path remains
grep -r "sys.path.insert" crawlab_test/
# Should return nothing

# Check imports look correct
grep -r "from crawlab_test\." crawlab_test/ | head -20
# Should show new import format

# Remove backup files
find . -name "*.bak" -delete
```

### Step 4: Update cli.py Entry Point (30 min)

**Option A**: Keep at root with clean imports

```python
#!/usr/bin/env python3
"""
Unified Test Runner CLI
"""
import argparse
import sys
from pathlib import Path

# Clean imports - no sys.path needed!
from crawlab_test.core import SpecFinder, Config, DockerDetector, ResultHandler, ParallelTestExecutor
from crawlab_test.backends import ScriptBackend, CopilotBackend, PlaywrightBackend

def main():
    """Main entry point"""
    # ... existing logic ...
    pass

if __name__ == "__main__":
    main()
```

**Option B**: Move to package and create stub (more complex, not recommended)

### Step 5: Install and Test Locally (1 hour)

```bash
# Install in editable mode
pip install -e .
# or
uv pip install -e .

# Verify package installed
pip list | grep crawlab-test
# Should show: crawlab-test 1.0.0 /path/to/crawlab-test

# Test imports
python -c "import crawlab_test; print('✅ Package OK')"
python -c "from crawlab_test.core import Config; print('✅ Core OK')"
python -c "from crawlab_test.helpers.api import AuthHelper; print('✅ Helpers OK')"
python -c "from crawlab_test.backends import ScriptBackend; print('✅ Backends OK')"

# Test CLI
./cli.py --help
./cli.py --list-specs
./cli.py --search api

# Run actual test
./cli.py --spec API-010

# Check for import errors
echo $?  # Should be 0
```

### Step 6: Update CI Workflows (1 hour)

```bash
# Edit both workflow files
vim .github/workflows/smoke-test.yml
vim .github/workflows/test.yml
```

Apply changes from `workflow-changes.md`:

**smoke-test.yml**:
- Update dependency installation (pip install -e .)
- Add package verification step
- Update syntax checking (crawlab_test/**/*.py)
- Update structure verification

**test.yml**:
- Update dependency installation (uv pip install -e .)
- Add package verification step
- Keep everything else the same

### Step 7: Test Locally - Full Suite (2 hours)

```bash
# Syntax check all files
find crawlab_test -name "*.py" -exec python -m py_compile {} \;

# Run multiple tests to verify
./cli.py --spec API-006
./cli.py --spec API-007  
./cli.py --spec API-008

# Check dependency conflicts
pip check

# Verify no leftover imports
grep -r "sys.path" crawlab_test/ | grep -v ".pyc" | grep -v "__pycache__"
```

### Step 8: Update Documentation (1 hour)

```bash
# Update README.md
vim README.md
```

Add installation section:
```markdown
## Installation

### For Development

\`\`\`bash
# Clone repository
git clone https://github.com/crawlab-team/crawlab-test.git
cd crawlab-test

# Install in editable mode
pip install -e .
# or with uv
uv pip install -e .

# Install Playwright browsers (for UI tests)
./setup-playwright.sh
\`\`\`
```

```bash
# Update AGENTS.md
vim AGENTS.md
```

Update development workflow section:
```markdown
## Development Workflow

### Setup
\`\`\`bash
# Install package in editable mode
pip install -e .

# Make changes
vim crawlab_test/helpers/api/auth.py

# Changes are immediately available (editable mode)
./cli.py --spec API-001
\`\`\`
```

```bash
# Update CI_INTEGRATION.md
vim CI_INTEGRATION.md
```

Update installation instructions as per workflow-changes.md.

### Step 9: Commit Changes (30 min)

```bash
# Stage all changes
git add -A

# Commit with detailed message
git commit -m "refactor: Convert to installable pip package

- Move modules to crawlab_test/ package directory
- Update all imports to use crawlab_test.* namespace
- Remove sys.path manipulations from all files
- Update pyproject.toml to enable package build
- Update CI workflows for package installation
- Update documentation with new setup instructions

Benefits:
- Clean imports without sys.path hacks
- Full IDE support (auto-completion, go-to-definition)
- Standard Python packaging practices
- Better maintainability and refactoring support

Breaking changes:
- Developers must run 'pip install -e .' after cloning
- Import paths changed (but automated migration)

Tested:
- [x] Local installation and imports
- [x] CLI functionality
- [x] Test execution (API-006, API-007, API-008)
- [x] Package integrity (pip check)
- [ ] CI workflows (to be verified on push)
"
```

### Step 10: Push and Verify CI (1 hour)

```bash
# Push to feature branch
git push -u origin feature/pip-packaging

# Monitor GitHub Actions
# 1. Go to Actions tab
# 2. Watch "Smoke Tests" workflow
# 3. If green, manually trigger "Test Specs" with category: api

# Check for issues in logs
# Look for:
# - Import errors (ModuleNotFoundError)
# - Package installation failures
# - Test execution failures

# If issues found, fix and push again
git commit -am "fix: Address CI import issues"
git push
```

### Step 11: Create PR and Review (30 min)

```bash
# Create PR via GitHub UI or gh CLI
gh pr create \
  --title "Convert crawlab-test to installable pip package" \
  --body "$(cat << 'EOF'
## Summary
Converts crawlab-test to proper Python package with clean imports.

## Changes
- Created `crawlab_test/` package directory
- Updated all imports to use `crawlab_test.*` namespace  
- Removed sys.path manipulations (100+ lines removed)
- Updated pyproject.toml for package build
- Updated CI workflows for package installation
- Updated documentation

## Benefits
- ✅ No more sys.path hacks
- ✅ Full IDE support (auto-completion, type hints)
- ✅ Standard Python workflow
- ✅ Professional packaging

## Testing
- [x] Local installation: `pip install -e .`
- [x] All imports work cleanly
- [x] CLI functions correctly
- [x] Tests execute successfully (API-006, 007, 008)
- [x] Smoke tests pass in CI
- [x] Spec tests pass in CI (api category)

## Migration Guide
For developers:
\`\`\`bash
git pull origin main
pip install -e .  # Required after pulling
\`\`\`

## Documentation
- See `docs/dev/20251028-pip-packaging/design.md` for full design
- See `docs/dev/20251028-pip-packaging/workflow-changes.md` for CI details

## Rollback Plan
If issues arise:
\`\`\`bash
git revert <this-commit>
\`\`\`
Or use feature flag in CI (see workflow-changes.md)
EOF
)"

# Add reviewers
gh pr edit --add-reviewer @crawlab-team
```

---

## Troubleshooting

### Issue: ModuleNotFoundError after install

**Cause**: Package not installed properly

**Solution**:
```bash
# Reinstall
pip uninstall crawlab-test
pip install -e .

# Verify
python -c "import crawlab_test"
```

### Issue: Import errors in tests

**Cause**: Missed some imports during migration

**Solution**:
```bash
# Find remaining old imports
grep -r "from helpers\." crawlab_test/
grep -r "from backends\." crawlab_test/
grep -r "from core\." crawlab_test/

# Update manually or re-run sed command
```

### Issue: CI fails with "package not found"

**Cause**: Workflow not updated correctly

**Solution**:
- Check workflow has `pip install -e .` or `uv pip install -e .`
- Verify `packages = ["crawlab_test"]` in pyproject.toml
- Check `package = true` in [tool.uv] section

### Issue: Tests pass locally but fail in CI

**Cause**: Environment differences

**Solution**:
```bash
# Run in CI mode locally
./cli.py --spec API-010 --ci

# Check Docker is running
docker ps

# Check API is accessible
curl http://localhost:8080/api/health
```

### Issue: Circular import errors

**Cause**: Package structure creates circular dependencies

**Solution**:
- Review import chains
- Move common utilities to separate module
- Use TYPE_CHECKING for type hints only

---

## Verification Checklist

Before creating PR:

- [ ] `pip install -e .` succeeds
- [ ] All imports work: `python -c "import crawlab_test"`
- [ ] CLI works: `./cli.py --help`, `--list-specs`
- [ ] At least 3 tests pass: API-006, API-007, API-008
- [ ] No sys.path remains: `grep -r "sys.path.insert" crawlab_test/`
- [ ] No dependency conflicts: `pip check`
- [ ] Syntax valid: `find crawlab_test -name "*.py" -exec python -m py_compile {} \;`
- [ ] Smoke tests pass in CI
- [ ] At least one category passes in CI (api recommended)
- [ ] Documentation updated: README.md, AGENTS.md, CI_INTEGRATION.md
- [ ] Commit message is detailed and clear

---

## Time Breakdown

| Task | Estimated | Notes |
|------|-----------|-------|
| Package structure | 30 min | Mostly git mv commands |
| pyproject.toml | 15 min | Few lines to change |
| Import updates | 2 hours | Automated but needs verification |
| cli.py updates | 30 min | Straightforward changes |
| Local testing | 1 hour | Install and run tests |
| CI workflow updates | 1 hour | Two files, clear changes |
| Full test suite | 2 hours | Multiple tests to verify |
| Documentation | 1 hour | Three docs to update |
| Commit & push | 30 min | Writing good commit message |
| CI verification | 1 hour | Monitor and fix if needed |
| PR creation | 30 min | Writing good description |
| **Total** | **~10 hours** | Can be done in 1-2 days |

---

## Success Criteria

1. ✅ Package installs cleanly: `pip install -e .`
2. ✅ All imports work without sys.path
3. ✅ CLI functions correctly
4. ✅ Tests execute successfully
5. ✅ IDE provides auto-completion
6. ✅ CI workflows pass (smoke + at least one category)
7. ✅ No regression in functionality
8. ✅ Documentation updated
9. ✅ Team can follow migration guide

When all checked, ready to merge! 🚀
