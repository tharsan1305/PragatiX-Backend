# V10__award_rules_refactor.sql

## Purpose
Adds `award_frequency` and `award_days` to `activities`, migrates `reset_period` → `award_frequency`, enforces `maximum_awards = 1` for one-time/manual activities, and adds an index on `award_frequency`.

## Tables / columns altered
`activities.award_frequency`, `activities.award_days`, index `idx_activities_award_frequency`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| MEDIUM | `activities.award_frequency`, `activities.award_days` | Free-text `VARCHAR` with no CHECK constraint, and `award_days` is a **comma-separated CSV string** (`'Monday,Wednesday,Friday'`). | Invalid frequency values slip in (`'daily'`, `'Daily ', 'WEEKLY'`); CSV weekdays can't be queried/indexed/validated cleanly and mix spelling. | Add a CHECK on allowed values; normalise weekday storage to a separate table or a SET column. `ALTER TABLE activities ADD CONSTRAINT chk_activities_award_frequency CHECK (award_frequency IN ('One Time','Daily','Weekly','Monthly','Manual'));` |

## Table checks
- `NOT NULL DEFAULT 'One Time'` on `award_frequency` is good. ✅
- The migration logic is correct and idempotent (normalises known `reset_period` values; NULL/empty fall through to 'One Time'). ✅
- Index on `award_frequency` added — good (this is the lookup column). ✅

## Suggested improvements (corrected SQL)

```sql
-- Keep the add + backfill as-is (they are correct), then:

ALTER TABLE activities ADD CONSTRAINT chk_activities_award_frequency
  CHECK (award_frequency IN ('One Time','Daily','Weekly','Monthly','Manual'));

-- Prefer a normalized weekdays model instead of CSV:
CREATE TABLE activity_award_days (
  activity_id BIGINT NOT NULL,
  day_name VARCHAR(20) NOT NULL,
  PRIMARY KEY (activity_id, day_name),
  CONSTRAINT fk_aad_activity FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- (backfill from award_days, then drop the CSV column if desired)
```
