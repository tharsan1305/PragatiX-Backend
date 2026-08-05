# V13__fix_activity_unique_constraint.sql

## Purpose
Replaces the old `uq_activity` unique constraint (on `category_id`, `activity_name`) with `uq_activity_subgroup` (on `subgroup_id`, `activity_name`) using dynamic `INFORMATION_SCHEMA` guards.

## Tables / columns altered
`activities` — drops index `uq_activity`, adds unique constraint `uq_activity_subgroup (subgroup_id, activity_name)`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| CRITICAL | `activities.activity_name`, `activities.category_id` | The migration references columns that **do not exist** in the migration-built schema. V2 created `activities` with `name` (not `activity_name`) and has **no `category_id` column** at all (V2 activities has `category VARCHAR(50)`, not `category_id`). The `ALTER TABLE activities DROP INDEX uq_activity` and `ADD CONSTRAINT uq_activity_subgroup UNIQUE (subgroup_id, activity_name)` both fail with **ERROR 1054 Unknown column** on a migration-built schema. | Migration aborts on a Flyway-managed DB. The constraint only "works" because Hibernate `ddl-auto: update` created `activity_name` from the JPA entity — but that's the schema drift problem. | Reference the real column `name` instead: `ALTER TABLE activities ADD CONSTRAINT uq_activity_subgroup UNIQUE (subgroup_id, name);` and drop the reference to the never-created `uq_activity`. |

## Table checks
- `activities` PK (`id`) and existing indexes preserved. ✅
- The dynamic guard for dropping `uq_activity` is safe (skips if not found). ✅

## Suggested improvements (corrected SQL)

```sql
-- Drop the legacy constraint only if it exists (safe guard is fine)
SET @dbname = DATABASE();
SET @tablename = 'activities';
SET @oldconstraint = 'uq_activity';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @oldconstraint) > 0,
  'ALTER TABLE activities DROP INDEX uq_activity;',
  'SELECT 1;'
));
PREPARE dropIndex FROM @preparedStatement; EXECUTE dropIndex; DEALLOCATE PREPARE dropIndex;

-- Add the new constraint using the REAL column name (name, not activity_name)
SET @newconstraint = 'uq_activity_subgroup';
SET @preparedStatement2 = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @newconstraint) > 0,
  'SELECT 1;',
  'ALTER TABLE activities ADD CONSTRAINT uq_activity_subgroup UNIQUE (subgroup_id, name);'
));
PREPARE addIndex FROM @preparedStatement2; EXECUTE addIndex; DEALLOCATE PREPARE addIndex;
```
