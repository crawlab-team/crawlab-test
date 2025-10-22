# Legacy UI Test Specifications

This directory contains the original UI test specifications in the old format, before conversion to the Copilot approach.

## Status: Archived (Reference Only)

These specs are kept for reference during the conversion process. They contain valuable test scenarios and implementation details that inform the new Copilot-based specs.

## What's Here

### Duplicate/Superseded Specs (Old Format)
- `UI-004-task-management.md` → **Superseded by** `../UI-003-task-management.md` (new)
- `UI-005-node-management.md` → **Superseded by** `../UI-004-node-management.md` (new)
- `UI-006-project-management.md` → **Superseded by** `../UI-005-project-management.md` (new)
- `UI-007-schedule-management.md` → **Superseded by** `../UI-006-schedule-management.md` (new)
- `UI-001-spider-management-workflow-validation.md` → **Merged into** `../UI-001-spider-management.md`

### Awaiting Conversion (Old Format)
These specs still need conversion to Copilot approach:
- `UI-008-git-integration.md` → To become `../UI-009-git-integration.md` (new)
- `UI-009-database-integration.md` → To become `../UI-010-database-integration.md` (new)
- `UI-010-dependencies-management.md` → To become `../UI-011-dependencies-management.md` (new)
- `UI-011-autoprobe-ai.md` → To become `../UI-007-autoprobe-ai.md` (new)
- `UI-012-notifications-system.md` → To become `../UI-008-notifications-system.md` (new)
- `UI-013-permissions-management.md` → To become `../UI-012-permissions-management.md` (new)
- `UI-014-system-settings.md` → To become `../UI-013-system-settings.md` (new)

## Old Format Characteristics

The legacy specs used:
- Hard-coded Playwright selectors (CSS selectors, IDs)
- Technical implementation details
- Specific element finding strategies
- Test case structure instead of workflow steps

## New Format Characteristics

The converted specs use:
- High-level instructions for Copilot
- Snapshot-based UI discovery
- Semantic element finding (by purpose/text)
- Observable validation through UI changes
- No hard-coded selectors
- Adaptive to UI changes

## Conversion Guide

See `../../docs/dev/20251020-ui-specs-copilot-refactoring/COMPLETION_GUIDE.md` for:
- Complete conversion template
- Quality checklist
- Reference to completed examples
- Step-by-step process

## Migration Timeline

- **Phase 1** (Completed): UI-001, UI-002 converted
- **Phase 2** (Completed): UI-003 through UI-006 converted (4 specs)
- **Phase 3** (Remaining): UI-007 through UI-013 (7 specs to convert)

## When to Delete

These legacy specs can be deleted once:
1. All 11 specs are converted to Copilot format
2. New specs have been tested and validated
3. Team confirms no longer need old format for reference

**Until then, keep them archived here for reference.**

---

*Last Updated: 2025-10-20*
*Status: 4/11 converted, 7 awaiting conversion*
