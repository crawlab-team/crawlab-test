# Documentation Archive

Historical documentation organized by date and topic. Each archive contains complete context for resolved issues.

## Structure

```
archive/
├── README.md (this file)
├── YYYY-MM-topic-name/
│   ├── README.md (archive summary)
│   └── *.md (detailed documents)
```

## Archives

### 📁 [2025-10-playwright-ui-test-fixes](./2025-10-playwright-ui-test-fixes/)

**Date**: October 10, 2025  
**Status**: ✅ Fixed  
**Impact**: UI-001 test now runs successfully  

UI test failing due to missing Playwright browser binaries. Fixed with:
- Automated browser setup script
- Enhanced error handling with helpful messages
- Comprehensive documentation

[Read full summary →](./2025-10-playwright-ui-test-fixes/README.md)

### 📁 [2025-10-database-integration-test-fixes](./2025-10-database-integration-test-fixes/)

**Date**: October 10, 2025  
**Status**: ✅ Fixed  
**Impact**: 14% → 100% test success rate  

Database integration tests were failing/skipped. Fixed three core issues:
- MongoDB authentication mismatch
- Missing environment variables for test services  
- Missing mongosh CLI

[Read full summary →](./2025-10-database-integration-test-fixes/README.md)

---

## Quick Search

```bash
# Find specific topic
ls -d tests/docs/archive/*/

# Search all archives
grep -r "keyword" tests/docs/archive/

# List by date
ls -lt tests/docs/archive/
```
