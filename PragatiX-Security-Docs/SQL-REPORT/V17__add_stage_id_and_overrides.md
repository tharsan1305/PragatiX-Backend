# V17__add_stage_id_and_overrides.sql

## Purpose
Adds `stage_id` to `activity_assignments` (with FK) and override columns (`award_xp`, `award_enabled`, `penalty_enabled`, `penalty_xp`, `award_frequency`) to `activity_stage_mappings`.

## Tables / columns altered
`activity_assignments.stage_id` (conditional), `activity_stage_mappings.award_xp`, `award_enabled`, `penalty_enabled`, `penalty_xp`, `award_frequency`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| CRITICAL | `activity_assignments` (table) | The migration targets `activity_assignments`, which **no migration in this set creates** (only the JPA entity defines it, created by Hibernate `ddl-auto: update`). On a migration-managed DB → **ERROR 1146 Table 'activity_assignments' doesn't exist**. | Migration aborts. | Create `activity_assignments` in a migration first, or ensure Hibernate runs before this migration (fragile). |
| CRITICAL | `activity_assignments.stage_id` FK | `CONSTRAINT fk_aa_stage FOREIGN KEY (stage_id) REFERENCES stages(id)` — `stages` was renamed to `activity_stages` in V2. **ERROR 1824** on a migration-built DB. | FK creation fails; migration aborts. | Change reference: `REFERENCES activity_stages(id) ON DELETE CASCADE`. |
| CRITICAL | `activity_stage_mappings` (lines 34–38) | Uses `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` — **MariaDB-only syntax** not supported in standard MySQL 8.0 → syntax error (1064). | Migration aborts on MySQL 8.0. | Replace each with an `INFORMATION_SCHEMA`-guarded `PREPARE` statement, e.g.: `SET @s=(SELECT IF(COUNT(*)=0,'ALTER TABLE activity_stage_mappings ADD COLUMN award_xp INT NULL','SELECT 1') FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='activity_stage_mappings' AND COLUMN_NAME='award_xp'); PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;` |
| MEDIUM | `activity_stage_mappings.award_frequency` | `VARCHAR(50) NULL` with no CHECK constraint. | Free-text allows any value; domain values should be restricted. | Add CHECK: `CHECK (award_frequency IN ('One Time','Daily','Weekly','Monthly'))`. |

## Table checks
- `activity_stage_mappings` already has PK, unique key, and 3 FKs from V16 — all preserved. ✅
- Override columns are additive and nullable — safe. ✅

## Suggested improvements (corrected SQL)

```sql
-- 1. Guard the activity_assignments ALTER with INFORMATION_SCHEMA
SET @dbname = DATABASE();
SET @tablename = 'activity_assignments';
SET @columnname = 'stage_id';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) = 0,
  'ALTER TABLE activity_assignments ADD COLUMN stage_id BIGINT NULL;',
  'SELECT 1;'
));
PREPARE stmt1 FROM @preparedStatement; EXECUTE stmt1; DEALLOCATE PREPARE stmt1;

-- 2. FK must reference activity_stages, not stages
SET @constraintname = 'fk_aa_stage';
SET @preparedStatement2 = (SELECT IF(
  (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND CONSTRAINT_NAME = @constraintname) = 0,
  'ALTER TABLE activity_assignments ADD CONSTRAINT fk_aa_stage FOREIGN KEY (stage_id) REFERENCES activity_stages(id) ON DELETE CASCADE;',
  'SELECT 1;'
));
PREPARE stmt2 FROM @preparedStatement2; EXECUTE stmt2; DEALLOCATE PREPARE stmt2;

-- 3. Replace MariaDB-only ADD COLUMN IF NOT EXISTS with INFORMATION_SCHEMA guards
-- (repeat pattern for each of the 5 override columns on activity_stage_mappings)
```
