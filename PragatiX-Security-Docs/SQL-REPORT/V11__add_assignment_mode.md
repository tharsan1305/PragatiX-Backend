# V11__add_assignment_mode.sql

## Purpose
Adds `assignment_mode` to the `activities` table to support three modes: MANUAL (default), GLOBAL, CLASS_COORDINATOR.

## Tables / columns altered
`activities.assignment_mode`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| LOW | `activities.assignment_mode` | `VARCHAR(50)` with no CHECK constraint — free text allows any value (e.g. 'manual', 'MANUAL', 'global', typos). | Application logic that switches on exact string match silently breaks on typos or case variants. | `ALTER TABLE activities ADD CONSTRAINT chk_activities_assignment_mode CHECK (assignment_mode IN ('MANUAL','GLOBAL','CLASS_COORDINATOR'));` |

## Table checks
- PK preserved; column added with NOT NULL DEFAULT 'MANUAL' — good. ✅

## Suggested improvements (corrected SQL)

```sql
ALTER TABLE activities
  ADD COLUMN assignment_mode VARCHAR(50) NOT NULL DEFAULT 'MANUAL';
ALTER TABLE activities ADD CONSTRAINT chk_activities_assignment_mode
  CHECK (assignment_mode IN ('MANUAL','GLOBAL','CLASS_COORDINATOR'));
```
