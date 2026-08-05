# V18__update_attendance_settings_dates.sql

## Purpose
Adds `start_date` and `end_date` columns to `attendance_settings`, then drops the legacy `week_start_day` and `week_end_day` columns.

## Tables / columns altered
`attendance_settings.start_date`, `attendance_settings.end_date`, `attendance_settings.week_start_day` (dropped), `attendance_settings.week_end_day` (dropped).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| HIGH | `attendance_settings` (table) | The table `attendance_settings` is **not created by any migration in this set** — it exists only because Hibernate `ddl-auto: update` creates it from the `AttendanceSettings` JPA entity. On a Flyway-managed DB the ALTER fails with **ERROR 1146 Table 'attendance_settings' doesn't exist**. | Migration aborts; the migration set is not authoritative for this table. | Add a `CREATE TABLE attendance_settings (...)` migration before V18, or ensure Hibernate runs before Flyway (fragile). |
| MEDIUM | `attendance_settings.week_start_day`, `week_end_day` | `DROP COLUMN` permanently removes weekly scheduling configuration with **no backup**. | If any row had non-NULL values in these columns, the weekly engine configuration is lost forever. | Back up before dropping: `CREATE TABLE backup_attendance_settings_week_config AS SELECT id, week_start_day, week_end_day FROM attendance_settings;` |
| LOW | `attendance_settings.start_date`, `end_date` | V18 adds these columns only for V19 to immediately drop them — **net-zero churn**. The columns exist for one migration and are removed in the next. | Pointless DDL churn; adds noise to migration history and briefly creates a column that is never meaningfully used. | Remove both V18 and V19 entirely if the intent is to drop the columns; or keep them if they are actually needed. |
| LOW | `attendance_settings` | No CHECK constraint on `end_date >= start_date`. | Allows invalid date ranges (end before start). | `ALTER TABLE attendance_settings ADD CONSTRAINT chk_settings_dates CHECK (end_date >= start_date);` |

## Table checks
- `attendance_settings` has no PK defined in these migrations — the JPA entity likely defines one (Hibernate). Not verifiable from migrations alone.
- No charset/collation specified for the table (inherits from DB default).

## Suggested improvements (corrected SQL)

```sql
-- If the table must be managed by migrations, create it first:
CREATE TABLE IF NOT EXISTS attendance_settings (
  id BIGINT NOT NULL AUTO_INCREMENT,
  academic_year VARCHAR(50) NOT NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  week_start_day INT NULL,
  week_end_day INT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Then alter safely
ALTER TABLE attendance_settings
  ADD COLUMN start_date DATE NULL,
  ADD COLUMN end_date DATE NULL;

-- Back up before dropping legacy columns
CREATE TABLE IF NOT EXISTS backup_attendance_settings_week_config AS
  SELECT id, week_start_day, week_end_day FROM attendance_settings;

ALTER TABLE attendance_settings
  DROP COLUMN week_start_day,
  DROP COLUMN week_end_day;

-- Enforce valid date ranges
ALTER TABLE attendance_settings
  ADD CONSTRAINT chk_settings_dates CHECK (end_date >= start_date);
```
