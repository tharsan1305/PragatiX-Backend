# V15__drop_legacy_subgroup_column.sql

## Purpose
Safely drops the legacy `subgroup` VARCHAR column from `activities` if present, using a two-step dynamic guard (first NULL it, then drop it).

## Tables / columns altered
`activities.subgroup` — dropped (conditional).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| MEDIUM | `activities.subgroup` | `DROP COLUMN subgroup` permanently deletes any data still present in that column. The migration guards against the column not existing, but does **not** back up the data before dropping. | If any legacy data was still in `subgroup` (e.g. a text label that wasn't migrated to `subgroup_id`), it is gone forever with no recovery path. | Snapshot the data before dropping: `CREATE TABLE backup_activities_subgroup AS SELECT id, subgroup FROM activities;` then proceed with the drop. |

## Table checks
- Dynamic guard is safe (checks INFORMATION_SCHEMA first). ✅
- PK, FKs, other columns unchanged. ✅

## Suggested improvements (corrected SQL)

```sql
-- Preserve legacy data before dropping
CREATE TABLE IF NOT EXISTS backup_activities_subgroup AS
  SELECT id, subgroup FROM activities WHERE subgroup IS NOT NULL;

-- Then proceed with the two-step drop (as written)
SET @dbname = DATABASE();
SET @tablename = 'activities';
SET @columnname = 'subgroup';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE activities MODIFY COLUMN subgroup VARCHAR(255) NULL;',
  'SELECT 1;'
));
PREPARE stmt1 FROM @preparedStatement; EXECUTE stmt1; DEALLOCATE PREPARE stmt1;

SET @preparedStatement2 = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
  'ALTER TABLE activities DROP COLUMN subgroup;',
  'SELECT 1;'
));
PREPARE stmt2 FROM @preparedStatement2; EXECUTE stmt2; DEALLOCATE PREPARE stmt2;
```
