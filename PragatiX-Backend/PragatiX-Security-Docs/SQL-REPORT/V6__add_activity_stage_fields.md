# V6__add_activity_stage_fields.sql

## Purpose
Adds scheduling/display fields to `activity_stages`: `start_date`, `end_date`, `display_order`, `is_active`; then initialises defaults for stage id 1.

## Tables / columns altered
`activity_stages.start_date`, `activity_stages.end_date`, `activity_stages.display_order`, `activity_stages.is_active`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| MEDIUM | `activity_stages` (line 8–13) | Defaults are applied with a hardcoded `WHERE id = 1` and hardcoded dates `'2026-01-01'`/`'2026-01-31'`. If stage id 1 is not the first stage (or the seed order differs), no defaults are applied to the real first stage; the dates are stale. | Stage configuration silently inconsistent across environments. | Drive from data instead of magic id: `UPDATE activity_stages SET display_order = id, is_active = 1 WHERE display_order = 0;` (and set date defaults per-environment) |
| LOW | `activity_stages.is_active` | Declared `TINYINT(1)` while the rest of the schema uses `BOOLEAN` for booleans. | Inconsistent typing — the ORM maps them differently. | `ALTER TABLE activity_stages MODIFY is_active BOOLEAN NOT NULL DEFAULT TRUE;` |

## Table checks
- PK (`id`) preserved. New columns are appropriately typed (`DATE`, `INT`, `TINYINT`). Adds are safe/online. ✅

## Suggested improvements (corrected SQL)

```sql
ALTER TABLE activity_stages
  ADD COLUMN start_date DATE DEFAULT NULL,
  ADD COLUMN end_date DATE DEFAULT NULL,
  ADD COLUMN display_order INT NOT NULL DEFAULT 0,
  ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Data-driven default instead of magic id = 1
UPDATE activity_stages SET display_order = id WHERE display_order = 0;
UPDATE activity_stages SET is_active = 1 WHERE is_active = 0;
```
