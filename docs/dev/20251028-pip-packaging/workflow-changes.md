# GitHub Actions Workflow Changes for Pip Packaging

This document shows the exact changes needed for both workflow files.

## 1. smoke-test.yml Changes

### Change 1: Update dependency installation

**Location**: Line ~30-35

**Before**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: 'pip'

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

**After**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: 'pip'

- name: Install package in editable mode
  run: |
    python -m pip install --upgrade pip
    pip install -e .
    echo "✅ crawlab-test package installed in editable mode"
```

### Change 2: Add package validation

**Location**: After "Install package in editable mode" step

**New step to add**:
```yaml
- name: Verify package installation
  run: |
    echo "Verifying package structure..."
    
    # Check package is importable
    python -c "import crawlab_test; print('✅ Package imported successfully')"
    
    # Check core modules
    python -c "from crawlab_test.core import Config, SpecFinder; print('✅ Core modules OK')"
    
    # Check backends
    python -c "from crawlab_test.backends import ScriptBackend, CopilotBackend; print('✅ Backends OK')"
    
    # Check helpers (sample)
    python -c "from crawlab_test.helpers.infrastructure import CrawlabAPIClient; print('✅ Helpers OK')"
    
    # Verify no dependency conflicts
    pip check
    echo "✅ No dependency conflicts found"
```

### Change 3: Update syntax checking

**Location**: Line ~45-50

**Before**:
```yaml
- name: Check Python syntax
  run: |
    python -m py_compile cli.py
    python -m py_compile backends/*.py
    python -m py_compile core/*.py
```

**After**:
```yaml
- name: Check Python syntax
  run: |
    echo "Checking Python syntax..."
    
    # Check entry point
    python -m py_compile cli.py
    
    # Check package modules
    find crawlab_test -name "*.py" -type f -exec python -m py_compile {} \;
    
    echo "✅ All Python files compiled successfully"
```

### Change 4: Update CLI verification

**Location**: Line ~35-40

**Before**:
```yaml
- name: Verify CLI works
  run: |
    chmod +x cli.py
    ./cli.py --help
    ./cli.py --list-specs
```

**After**:
```yaml
- name: Verify CLI works
  run: |
    chmod +x cli.py
    
    echo "Testing CLI help..."
    ./cli.py --help
    
    echo "Testing CLI list-specs..."
    ./cli.py --list-specs
    
    echo "Testing CLI search..."
    ./cli.py --search api
    
    echo "✅ CLI is functional"
```

### Change 5: Update structure verification

**Location**: Line ~70-80

**Before**:
```yaml
- name: Verify test structure
  run: |
    echo "Checking test structure..."
    
    # Check that specs directory exists
    if [ ! -d "specs" ]; then
      echo "❌ specs/ directory not found"
      exit 1
    fi
    
    # ... rest of checks ...
    
    # Check that backends exist
    if [ ! -f "backends/script_backend.py" ]; then
      echo "❌ script_backend.py not found"
      exit 1
    fi
```

**After**:
```yaml
- name: Verify test structure
  run: |
    echo "Checking test structure..."
    
    # Check that specs directory exists
    if [ ! -d "specs" ]; then
      echo "❌ specs/ directory not found"
      exit 1
    fi
    
    # ... rest of checks ...
    
    # Check that package directory exists
    if [ ! -d "crawlab_test" ]; then
      echo "❌ crawlab_test/ package directory not found"
      exit 1
    fi
    
    # Check that backends exist in package
    if [ ! -f "crawlab_test/backends/script_backend.py" ]; then
      echo "❌ script_backend.py not found in package"
      exit 1
    fi
    
    echo "✅ Test structure looks good"
```

---

## 2. test.yml Changes

### Change 1: Update dependency installation (uv method)

**Location**: Line ~250-255

**Before**:
```yaml
- name: Set up Python
  run: uv python install ${{ env.PYTHON_VERSION }}

- name: Install dependencies
  run: uv sync
```

**After**:
```yaml
- name: Set up Python
  run: uv python install ${{ env.PYTHON_VERSION }}

- name: Install package in editable mode
  run: |
    uv pip install -e .
    echo "✅ crawlab-test package installed in editable mode"
```

### Change 2: Add package validation

**Location**: After "Install package in editable mode" step

**New step to add**:
```yaml
- name: Verify package installation
  run: |
    echo "Verifying crawlab-test package..."
    
    # Check package imports
    uv run python -c "import crawlab_test; print('✅ Package OK')"
    uv run python -c "from crawlab_test.core import SpecFinder; print('✅ SpecFinder OK')"
    uv run python -c "from crawlab_test.backends import ScriptBackend; print('✅ Backends OK')"
    
    # Verify CLI entry point
    ./cli.py --version || echo "CLI version check (optional)"
    
    echo "✅ Package verified successfully"
```

### Change 3: No changes needed for test execution

The test execution steps remain **unchanged** because:
- CLI invocation stays the same (`./cli.py --spec ...`)
- Package imports happen internally
- Results directory structure unchanged

**These steps remain as-is**:
```yaml
- name: List available specs
  run: |
    echo "Available specs for category: ${{ matrix.category }}"
    ./cli.py --list-specs --category ${{ matrix.category }}

- name: Run tests
  env:
    CRAWLAB_API_URL: ${{ env.CRAWLAB_API_URL }}
    # ... other env vars ...
  run: |
    # These commands remain exactly the same
    uv run ./cli.py --spec "$SPEC_ID" --ci
    uv run ./cli.py --category ${{ matrix.category }} --parallel $PARALLEL_WORKERS --ci
```

---

## 3. Complete Updated smoke-test.yml

Here's the complete updated file for reference:

```yaml
name: Smoke Tests

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  PYTHON_VERSION: '3.9'

jobs:
  smoke-test:
    name: Quick Smoke Test
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install package in editable mode
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          echo "✅ crawlab-test package installed in editable mode"
      
      - name: Verify package installation
        run: |
          echo "Verifying package structure..."
          python -c "import crawlab_test; print('✅ Package imported successfully')"
          python -c "from crawlab_test.core import Config, SpecFinder; print('✅ Core modules OK')"
          python -c "from crawlab_test.backends import ScriptBackend, CopilotBackend; print('✅ Backends OK')"
          python -c "from crawlab_test.helpers.infrastructure import CrawlabAPIClient; print('✅ Helpers OK')"
          pip check
          echo "✅ No dependency conflicts found"
      
      - name: Verify CLI works
        run: |
          chmod +x cli.py
          echo "Testing CLI help..."
          ./cli.py --help
          echo "Testing CLI list-specs..."
          ./cli.py --list-specs
          echo "Testing CLI search..."
          ./cli.py --search api
          echo "✅ CLI is functional"
      
      - name: Check Python syntax
        run: |
          echo "Checking Python syntax..."
          python -m py_compile cli.py
          find crawlab_test -name "*.py" -type f -exec python -m py_compile {} \;
          echo "✅ All Python files compiled successfully"
      
      - name: Verify test structure
        run: |
          echo "Checking test structure..."
          
          if [ ! -d "specs" ]; then
            echo "❌ specs/ directory not found"
            exit 1
          fi
          
          CATEGORIES=("api" "reliability" "performance" "integration" "ui")
          for cat in "${CATEGORIES[@]}"; do
            if [ ! -d "specs/$cat" ]; then
              echo "⚠️  Warning: specs/$cat/ directory not found"
            else
              COUNT=$(find "specs/$cat" -name "*.md" -type f | wc -l)
              echo "✅ specs/$cat/: $COUNT spec(s)"
            fi
          done
          
          if [ ! -d "crawlab_test" ]; then
            echo "❌ crawlab_test/ package directory not found"
            exit 1
          fi
          
          if [ ! -f "crawlab_test/backends/script_backend.py" ]; then
            echo "❌ script_backend.py not found in package"
            exit 1
          fi
          
          if [ ! -f "crawlab_test/backends/copilot_backend.py" ]; then
            echo "❌ copilot_backend.py not found in package"
            exit 1
          fi
          
          echo "✅ Test structure looks good"
      
      - name: Test spec finder
        id: spec_finder
        run: |
          python .github/workflows/test_spec_finder.py
      
      - name: Summary
        if: always()
        run: |
          echo "## Smoke Test Results" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{ steps.spec_finder.outcome }}" = "success" ]; then
            echo "✅ Spec finder tests passed" >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ Spec finder tests failed" >> $GITHUB_STEP_SUMMARY
          fi
          
          echo "✅ Package installation verified" >> $GITHUB_STEP_SUMMARY
          echo "✅ Python syntax checks completed" >> $GITHUB_STEP_SUMMARY
          echo "✅ CLI is executable and functional" >> $GITHUB_STEP_SUMMARY
          echo "✅ Test structure validated" >> $GITHUB_STEP_SUMMARY
          
          echo "" >> $GITHUB_STEP_SUMMARY
          if [ "${{ steps.spec_finder.outcome }}" = "success" ]; then
            echo "**Status**: ✅ All smoke tests passed" >> $GITHUB_STEP_SUMMARY
          else
            echo "**Status**: ❌ Some smoke tests failed" >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
```

---

## 4. Key test.yml Changes Summary

Since test.yml is very long, here are just the critical changes:

**Lines ~250-255** (Install dependencies):
```yaml
# BEFORE
- name: Install dependencies
  run: uv sync

# AFTER
- name: Install package in editable mode
  run: |
    uv pip install -e .
    echo "✅ crawlab-test package installed in editable mode"
```

**Lines ~255-260** (Add new verification step):
```yaml
- name: Verify package installation
  run: |
    echo "Verifying crawlab-test package..."
    uv run python -c "import crawlab_test; print('✅ Package OK')"
    uv run python -c "from crawlab_test.core import SpecFinder; print('✅ SpecFinder OK')"
    uv run python -c "from crawlab_test.backends import ScriptBackend; print('✅ Backends OK')"
    echo "✅ Package verified successfully"
```

**All other steps remain unchanged** - test execution, Docker setup, artifact upload, etc.

---

## 5. Migration Checklist for CI

When implementing these changes:

- [ ] Backup both workflow files
- [ ] Update `smoke-test.yml` with all 5 changes
- [ ] Update `test.yml` with 2 changes (install + verify)
- [ ] Update `.github/workflows/test_spec_finder.py` if it exists (update imports)
- [ ] Test on feature branch first
- [ ] Verify smoke tests pass
- [ ] Verify at least one category of spec tests passes
- [ ] Check workflow logs for any import errors
- [ ] Merge to main/develop only after verification

---

## 6. Rollback Plan

If CI breaks after merging:

### Quick Revert
```bash
git revert <commit-hash>
git push origin main
```

### Emergency Hotfix

Add to both workflows temporarily:

```yaml
- name: Install dependencies (with fallback)
  run: |
    if pip install -e . 2>/dev/null; then
      echo "✅ Installed as package"
    else
      echo "⚠️ Package install failed, using fallback"
      pip install -r requirements.txt
      # Add project root to Python path as fallback
      echo "PYTHONPATH=$PWD:$PYTHONPATH" >> $GITHUB_ENV
    fi
```

---

## 7. Testing Before Merge

Local verification:
```bash
# 1. Install package
pip install -e .

# 2. Verify imports work
python -c "from crawlab_test.core import Config"
python -c "from crawlab_test.helpers.api import AuthHelper"

# 3. Run CLI
./cli.py --help
./cli.py --list-specs

# 4. Run a quick test
./cli.py --spec API-010

# 5. Check no sys.path remains
grep -r "sys.path.insert" crawlab_test/
# Should return nothing

# 6. Syntax check
find crawlab_test -name "*.py" -exec python -m py_compile {} \;
```

CI verification after push to feature branch:
1. Check smoke test passes
2. Manually trigger test workflow with category: `api`
3. Review workflow logs for import errors
4. Download artifacts and verify structure
5. Only merge if all checks pass

---

## Summary

**Total workflow changes**: 
- smoke-test.yml: 5 modifications + 1 new step
- test.yml: 1 modification + 1 new step

**Impact**: Minimal - mostly installation method changes, no test execution changes

**Risk**: Low - can rollback easily, fallback option available

**Benefit**: High - eliminates sys.path hacks, enables proper IDE support, professional packaging
