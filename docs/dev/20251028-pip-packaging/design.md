# Converting crawlab-test to an Installable Package

**Date**: 2025-10-28  
**Status**: ✅ Implementation Complete (this is a reference document)  
**Author**: AI Agent

> **Note**: This implementation has been completed. See `IMPLEMENTATION_COMPLETE.md` for current status.
> This document serves as the original design reference.

## Problem Statement

The current crawlab-test project requires manual `sys.path` manipulation in every test runner to resolve imports. This leads to:

1. **Boilerplate code**: Every runner has `sys.path.insert(0, ...)` at the top
2. **Import fragility**: Different runners use different path resolution strategies
3. **IDE confusion**: Auto-completion and type hints don't work properly
4. **Maintainability**: Difficult to refactor or reorganize code structure
5. **Developer friction**: New contributors struggle with import errors

**Current import patterns observed**:
```python
# Pattern 1: Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Pattern 2: Conditional addition
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Pattern 3: Relative path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
```

## Proposed Solution

Convert crawlab-test to a proper Python package that can be installed in editable mode, enabling clean imports without `sys.path` manipulation.

### Design Goals

1. **Zero sys.path manipulation**: All imports work naturally
2. **Backward compatible**: Existing test runners continue to work
3. **Developer-friendly**: `pip install -e .` or `uv pip install -e .`
4. **IDE support**: Full auto-completion and type hints
5. **Minimal disruption**: No major architectural changes

## Implementation Plan

### Phase 1: Package Structure

**Convert to proper package structure**:
```
crawlab-test/
├── pyproject.toml              # Update configuration
├── src/                        # NEW: Source directory (PEP 517)
│   └── crawlab_test/          # Package namespace
│       ├── __init__.py        # Package root
│       ├── backends/          # Move from ./backends
│       ├── core/              # Move from ./core
│       ├── helpers/           # Move from ./helpers
│       └── runners/           # Move from ./runners
├── cli.py                     # Keep at root (entry point)
├── specs/                     # Keep at root (data files)
├── docs/                      # Keep at root
├── tests/                     # NEW: Unit tests (optional)
└── tmp/                       # Keep at root (gitignored)
```

**Alternative: Flat structure (simpler)**:
```
crawlab-test/
├── pyproject.toml              # Update configuration
├── crawlab_test/              # Package namespace (no src/)
│   ├── __init__.py
│   ├── backends/
│   ├── core/
│   ├── helpers/
│   └── runners/
├── cli.py                     # Entry point script
├── specs/                     # Data files
└── ...
```

**Recommendation**: Use **flat structure** for simplicity. The `src/` layout provides better namespace isolation but adds complexity for a testing project.

### Phase 2: Update pyproject.toml

```toml
[project]
name = "crawlab-test"
version = "1.0.0"
description = "Comprehensive automated testing framework for Crawlab"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }

dependencies = [
    "pymongo>=4.0.0",
    "requests>=2.28.0",
    "psutil>=5.9.0",
    "pyyaml>=6.0",
    "playwright>=1.40.0",
    "grpcio>=1.71.0",
    "grpcio-tools>=1.71.0",
    "protobuf>=6.27.0",
    "pytest>=7.0.0",
    "pytest-timeout>=2.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["crawlab_test"]  # CHANGED: Enable package build

[tool.uv]
package = true  # CHANGED: Enable package mode

[project.scripts]
crawlab-test = "crawlab_test.cli:main"  # NEW: CLI entry point

[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

### Phase 3: Update Import Statements

**Before** (with sys.path manipulation):
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from helpers.api import AuthHelper
from helpers.api.database import DatabaseAPIHelper
from core import Config
```

**After** (clean imports):
```python
#!/usr/bin/env python3
from crawlab_test.helpers.api import AuthHelper
from crawlab_test.helpers.api.database import DatabaseAPIHelper
from crawlab_test.core import Config
```

### Phase 4: Update Entry Point (cli.py)

**Option A: Keep at root with clean imports**:
```python
#!/usr/bin/env python3
"""
Unified Test Runner CLI
"""
import argparse
import sys
from pathlib import Path

from crawlab_test.core import SpecFinder, Config, DockerDetector
from crawlab_test.backends import ScriptBackend, CopilotBackend

def main():
    """Main entry point"""
    # ... existing logic ...
    pass

if __name__ == "__main__":
    main()
```

**Option B: Move to package and create stub**:
```python
# ./cli.py (stub at root)
#!/usr/bin/env python3
from crawlab_test.cli import main

if __name__ == "__main__":
    main()
```

```python
# crawlab_test/cli.py (actual implementation)
#!/usr/bin/env python3
def main():
    # ... all CLI logic ...
    pass

if __name__ == "__main__":
    main()
```

**Recommendation**: Use **Option A** - keep cli.py at root but use clean imports. This maintains backward compatibility with `./cli.py` invocation.

### Phase 5: Migration Strategy

**Step-by-step migration**:

1. **Create package directory**:
   ```bash
   mkdir crawlab_test
   ```

2. **Move modules** (use git mv to preserve history):
   ```bash
   git mv backends crawlab_test/
   git mv core crawlab_test/
   git mv helpers crawlab_test/
   git mv runners crawlab_test/
   ```

3. **Create __init__.py files**:
   ```bash
   # Root package
   touch crawlab_test/__init__.py
   
   # Ensure all subdirectories have __init__.py
   find crawlab_test -type d -exec touch {}/__init__.py \;
   ```

4. **Update pyproject.toml** as shown above

5. **Install in editable mode**:
   ```bash
   uv pip install -e .
   # OR
   pip install -e .
   ```

6. **Update imports** in all files:
   ```bash
   # Use find-replace across all Python files
   # Old: from helpers.api import
   # New: from crawlab_test.helpers.api import
   ```

7. **Remove sys.path manipulations**:
   ```bash
   # Remove all lines containing sys.path.insert
   ```

8. **Test**:
   ```bash
   # Run existing tests to verify nothing broke
   uv run ./cli.py --list-specs
   uv run ./cli.py --spec API-010
   ```

## Impact Analysis

### Files Requiring Updates

**High Priority** (20-30 files):
- All test runners in `runners/*/*.py` (~20 files)
- Core modules: `cli.py`, `core/*.py`
- Backend modules: `backends/*.py`

**Medium Priority** (30-50 files):
- Helper modules with cross-imports
- `__init__.py` files to ensure proper exports

**Low Priority**:
- Documentation (references to import patterns)
- CI/CD configurations (no changes needed)

### Breaking Changes

**For developers**:
- Must run `pip install -e .` after cloning
- Import paths change (but automated find-replace)

**For end users**:
- **None** - CLI interface remains identical
- Docker deployments unaffected

### Benefits

1. **No more sys.path hacks**: Clean, idiomatic Python
2. **IDE support**: Full auto-completion, go-to-definition, type hints
3. **Easier refactoring**: Safe to reorganize modules
4. **Standard workflow**: Familiar to Python developers
5. **Better testing**: Can use pytest discovery naturally
6. **Professional**: Follows Python packaging best practices

### Risks

1. **Migration effort**: ~30 files need import updates (mitigated by automated find-replace)
2. **Git history**: Moving files might complicate blame (mitigated by `git mv`)
3. **Learning curve**: New contributors need to run install step (mitigated by clear docs)

## Alternative Approaches Considered

### Alternative 1: Keep Current Structure + PYTHONPATH

**Approach**: Document that users should set `PYTHONPATH` environment variable.

**Pros**:
- No code changes needed
- Backward compatible

**Cons**:
- Still requires manual configuration
- IDE support remains poor
- Not discoverable for new developers

**Verdict**: ❌ Not recommended - doesn't solve the core problem

### Alternative 2: Namespace Package (without __init__.py)

**Approach**: Use PEP 420 namespace packages without `__init__.py` files.

**Pros**:
- More flexible for extensions
- Can split across multiple packages

**Cons**:
- More complex for this use case
- Harder to understand for new contributors
- Requires Python 3.3+

**Verdict**: ❌ Over-engineered for our needs

### Alternative 3: Monorepo with Shared Module

**Approach**: Keep as script collection, create shared `crawlab_test_common` package.

**Pros**:
- Minimal changes to existing structure
- Shared code packaged separately

**Cons**:
- Split architecture (confusing)
- Still need sys.path for runners
- More maintenance burden

**Verdict**: ❌ Doesn't fully solve the problem

## Implementation Checklist

- [ ] Create package directory structure
- [ ] Update pyproject.toml configuration
- [ ] Move modules using `git mv`
- [ ] Create __init__.py files
- [ ] Update imports in all Python files
- [ ] Remove sys.path manipulations
- [ ] Update cli.py entry point
- [ ] Test installation: `uv pip install -e .`
- [ ] Verify all tests still run
- [ ] Update README.md installation instructions
- [ ] Update AGENTS.md guidelines
- [ ] Update CI/CD workflows (if needed)
- [ ] Create migration guide for contributors

## Timeline Estimate

- **Preparation**: 1 hour (planning, backup)
- **Structural changes**: 2 hours (moving files, creating __init__.py)
- **Import updates**: 3 hours (automated + manual verification)
- **Testing**: 2 hours (run test suite, fix issues)
- **Documentation**: 1 hour (update docs)

**Total**: ~8-10 hours of work

## Success Criteria

1. ✅ All imports work without sys.path manipulation
2. ✅ `uv pip install -e .` succeeds
3. ✅ All existing tests pass without modification
4. ✅ IDE provides full auto-completion
5. ✅ `./cli.py --list-specs` works
6. ✅ CI/CD pipeline passes
7. ✅ Documentation updated

## Rollback Plan

If issues arise:
1. Revert git commits (package structure preserved in history)
2. Or keep package but add backward-compatible sys.path additions temporarily
3. Feature flag: `USE_PACKAGE_IMPORTS=false` in config

## Questions for Review

1. **Prefer src/ layout or flat package?** → Recommend flat for simplicity
2. **Keep cli.py at root or move inside package?** → Recommend keep at root
3. **Migrate all at once or incrementally?** → Recommend all at once (cleaner)
4. **Add unit tests while migrating?** → Optional, but recommended for core modules
5. **Update CI to verify package integrity?** → Yes, add `pip check` step

## CI/CD Integration

### Current GitHub Actions Workflows

The project has two main workflows:

1. **`smoke-test.yml`** - Fast validation (2-3 min)
   - Python syntax checks
   - CLI functionality tests
   - Structure validation

2. **`test.yml`** - Full spec-based testing (5-30 min per category)
   - Smart category detection
   - Parallel test execution
   - Docker orchestration
   - Test result artifacts

### Changes Required for Packaging

**Update workflow installation steps**:

**Before** (current):
```yaml
- name: Install dependencies
  run: uv sync
```

**After** (with packaging):
```yaml
- name: Install package in editable mode
  run: |
    uv pip install -e .
    # or: pip install -e .
```

**Specific workflow updates needed**:

#### 1. smoke-test.yml Updates

```yaml
# Current
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt

# New
- name: Install package and dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .  # Installs package + dependencies
```

```yaml
# Current
- name: Check Python syntax
  run: |
    python -m py_compile cli.py
    python -m py_compile backends/*.py
    python -m py_compile core/*.py

# New  
- name: Check Python syntax
  run: |
    python -m py_compile cli.py
    python -m py_compile crawlab_test/**/*.py
```

#### 2. test.yml Updates

```yaml
# Current
- name: Install dependencies
  run: uv sync

# New
- name: Install package in editable mode
  run: |
    uv pip install -e .
    echo "✅ crawlab-test package installed"
```

```yaml
# No change needed for CLI invocations
- name: Run tests
  run: |
    # These remain the same
    ./cli.py --spec API-001
    ./cli.py --list-specs --category ${{ matrix.category }}
```

#### 3. New Validation Steps

Add package integrity checks:

```yaml
- name: Verify package installation
  run: |
    # Check package is importable
    python -c "import crawlab_test; print(f'✅ Package version: {crawlab_test.__version__}')"
    
    # Check package structure
    python -c "from crawlab_test.core import Config, SpecFinder; print('✅ Core modules OK')"
    python -c "from crawlab_test.backends import ScriptBackend; print('✅ Backends OK')"
    python -c "from crawlab_test.helpers.api import AuthHelper; print('✅ Helpers OK')"
    
    # Verify no import conflicts
    pip check
```

### Migration Strategy for CI

**Phase 1: Preparation**
1. Create feature branch `feature/pip-packaging`
2. Implement package structure locally
3. Test locally with `pip install -e .`

**Phase 2: CI Updates**
1. Update both workflow files simultaneously
2. Add package validation steps
3. Keep backward compatibility initially

**Phase 3: Testing**
1. Push to feature branch
2. Verify smoke tests pass
3. Verify at least one category of spec tests passes
4. Check all import paths work in CI

**Phase 4: Rollout**
1. Create PR with all changes
2. Review CI results
3. Merge to main/develop
4. Monitor CI on main branch

### Rollback Strategy for CI

If CI breaks after merge:

**Option 1: Quick revert**
```bash
git revert <commit-hash>
git push
```

**Option 2: Hotfix with fallback**

Add conditional install in workflows:
```yaml
- name: Install dependencies (with fallback)
  run: |
    # Try new method
    if pip install -e . 2>/dev/null; then
      echo "✅ Installed as package"
    else
      # Fallback to old method
      echo "⚠️ Falling back to legacy installation"
      pip install -r requirements.txt
    fi
```

**Option 3: Feature flag**

Add environment variable:
```yaml
env:
  USE_PACKAGE_MODE: 'true'  # Set to 'false' to disable

steps:
  - name: Install dependencies
    run: |
      if [ "$USE_PACKAGE_MODE" = "true" ]; then
        pip install -e .
      else
        pip install -r requirements.txt
      fi
```

### Impact on CI Performance

**Expected changes**:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Dependency install | ~10s | ~12s | +2s (negligible) |
| Python module load | Same | Same | No change |
| Test execution | Same | Same | No change |
| Cache effectiveness | Good | Better | Package metadata cached |

**Total impact**: < 5% increase in CI time, acceptable trade-off for better maintainability.

### CI Best Practices with Packaging

1. **Cache pip dependencies**:
```yaml
- name: Setup Python with cache
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
    cache: 'pip'
```

2. **Use UV's built-in caching** (already enabled):
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true  # Already in place
```

3. **Verify package integrity**:
```yaml
- name: Check package health
  run: |
    pip check  # Verify dependencies
    python -m crawlab_test.cli --version  # Verify entry point
```

4. **Artifact handling** (no changes needed):
   - Results still written to `results/`
   - Artifacts still uploaded normally
   - No impact on test execution

### Documentation Updates for CI/CD

**Files requiring updates**:

1. **CI_INTEGRATION.md** - Update installation instructions:
```markdown
## Installation in CI

### Using pip
\`\`\`yaml
- name: Install package
  run: pip install -e .
\`\`\`

### Using uv (recommended)
\`\`\`yaml
- name: Install package
  run: uv pip install -e .
\`\`\`
```

2. **README.md** - Update CI badge section (if any)

3. **AGENTS.md** - Update development workflow:
```markdown
## Running Tests Locally

\`\`\`bash
# Install in editable mode
pip install -e .

# Run tests
./cli.py --spec API-001
\`\`\`
```

### Testing the CI Changes

**Pre-merge checklist**:

```bash
# 1. Test package installation
pip install -e .
python -c "import crawlab_test; print('OK')"

# 2. Test CLI still works
./cli.py --help
./cli.py --list-specs

# 3. Test imports work
python -c "from crawlab_test.helpers.api import AuthHelper"

# 4. Run actual test
./cli.py --spec API-010 --ci

# 5. Verify no sys.path in code
grep -r "sys.path.insert" runners/ helpers/ backends/ core/
# Should return nothing

# 6. Check syntax
python -m py_compile crawlab_test/**/*.py
```

**Post-merge monitoring**:

1. Watch first CI run on main/develop
2. Check smoke test passes
3. Verify at least one category of spec tests passes
4. Monitor for import errors in logs
5. Check artifacts are generated correctly

## Next Steps

1. **Get approval** on proposed structure
2. **Review CI/CD impact** with team
3. **Create feature branch**: `feature/pip-packaging`
4. **Implement migration** following checklist
5. **Update CI workflows** (both .yml files)
6. **Test locally** with full test suite
7. **Push and verify CI** on feature branch
8. **Create PR** with detailed migration notes
9. **Monitor CI results** and fix any issues
10. **Update team documentation** and onboarding guides

## References

- [PEP 517 - Pyproject.toml specification](https://peps.python.org/pep-0517/)
- [PEP 518 - Build system requirements](https://peps.python.org/pep-0518/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [Hatchling - Modern build backend](https://hatch.pypa.io/latest/)
- [UV - Fast Python package manager](https://github.com/astral-sh/uv)
- [GitHub Actions - Python setup](https://github.com/actions/setup-python)
- [GitHub Actions - Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
