# V9__update_activity_rules_fields.sql

## Purpose
Adds award-rule fields to `activities` (`award_xp`, `award_type`, `repeat_allowed`, `reset_period`) and migrates existing values from `xp` and `frequency`.

## Tables / columns altered
`activities.award_xp`, `activities.award_type`, `activities.repeat_allowed`, `activities.reset_period`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| MEDIUM | `activities.award_xp` (line 8) | `UPDATE activities SET award_xp = CAST(COALESCE(xp,'0') AS SIGNED);` — if `xp` contains any non-numeric text (e.g. `'50 XP'`, `'high'`, `'100+'`), MySQL `CAST(... AS SIGNED)` **silently returns 0** (with only a warning). Real XP values are quietly zeroed and the originals stay in the now-redundant `xp` column. | Silent data corruption that is unrecoverable after the migration commits; award values wrong, students under/over-rewarded. | Audit before casting, then migrate only clean values: `SELECT id, xp FROM activities WHERE xp IS NOT NULL AND xp NOT REGEXP '^[0-9]+$';` then `UPDATE activities SET award_xp = xp WHERE xp REGEXP '^[0-9]+$'; UPDATE activities SET award_xp = 0 WHERE award_xp IS NULL;` (or fail the migration if junk is found). Also drop the duplicate `xp` column afterwards: `ALTER TABLE activities DROP COLUMN xp;` |
| LOW | `activities.award_type`, `activities.reset_period` | Free-text `VARCHAR(50)` with no CHECK/ENUM ('Fixed XP', 'Once', …). | Unvalidated domain values drift ('fixed', 'FIXED XP', 'Daily'); logic switches on strings. | `ALTER TABLE activities ADD CONSTRAINT chk_activities_award_type CHECK (award_type IN ('Fixed XP','Per Point','Penalty')); ALTER TABLE activities ADD CONSTRAINT chk_activities_reset_period CHECK (reset_period IN ('Once','Daily','Weekly','Monthly'));` |

## Table checks
- PK preserved; column adds are safe. The data migration is the risk point.

## Suggested improvements (corrected SQL)

```sql
-- First validate the source data
SELECT id, xp FROM activities WHERE xp IS NOT NULL AND xp NOT REGEXP '^[0-9]+$';

-- Migrate only clean numeric values
UPDATE activities SET award_xp = xp WHERE xp REGEXP '^[0-9]+$';
UPDATE activities SET award_xp = 0 WHERE award_xp IS NULL;

-- Enforce domain values
ALTER TABLE activities ADD CONSTRAINT chk_activities_award_type CHECK (award_type IN ('Fixed XP','Per Point','Penalty'));
ALTER TABLE activities ADD CONSTRAINT chk_activities_reset_period CHECK (reset_period IN ('Once','Daily','Weekly','Monthly'));

-- After the legacy column is no longer needed
ALTER TABLE activities DROP COLUMN xp;
```
