# V8__add_activity_event_fields.sql

## Purpose
Adds event-management fields to `activities`: `maximum_awards`, `display_order`, `status`.

## Tables / columns altered
`activities.maximum_awards`, `activities.display_order`, `activities.status`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| LOW | `activities.status` | `VARCHAR(50) DEFAULT 'ACTIVE'` with no CHECK constraint. | Free text allows typos/invalid states ('active', 'disabled', '') → engine logic that compares to 'ACTIVE' silently breaks. | `ALTER TABLE activities MODIFY status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'; ALTER TABLE activities ADD CONSTRAINT chk_activities_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'));` |
| LOW | `activities.maximum_awards`, `activities.display_order` | Added as nullable `INT` with defaults but no `NOT NULL`. | Optional nulls complicate `COALESCE` logic at read time. | `ALTER TABLE activities MODIFY maximum_awards INT NOT NULL DEFAULT 1, MODIFY display_order INT NOT NULL DEFAULT 0;` |

## Table checks
- PK preserved; adds are online/safe. No data loss. ✅

## Suggested improvements (corrected SQL)

```sql
ALTER TABLE activities
  ADD COLUMN maximum_awards INT NOT NULL DEFAULT 1,
  ADD COLUMN display_order INT NOT NULL DEFAULT 0,
  ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE';

ALTER TABLE activities ADD CONSTRAINT chk_activities_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'));
```
