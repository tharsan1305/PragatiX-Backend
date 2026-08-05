# V19__drop_attendance_dates.sql

## Purpose
Drops `start_date` and `end_date` from `attendance_settings` (reversing V18).

## Tables / columns altered
`attendance_settings.start_date` (dropped), `attendance_settings.end_date` (dropped).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| HIGH | `attendance_settings` (table) | The table `attendance_settings` is **not created by any migration in this set** — it exists only because Hibernate `ddl-auto: update` creates it. On a Flyway-managed DB the ALTER fails with **ERROR 1146 Table 'attendance_settings' doesn't exist**. | Migration aborts. | Same as V18 — create the table in a migration first, or wire Hibernate to run before Flyway (fragile). |
| MEDIUM | `attendance_settings.start_date`, `end_date` | `DROP COLUMN` permanently removes data. If any application code or report wrote values to these columns between V18 and V19, that data is lost. | Data loss of the date range configuration. | Back up before dropping: `CREATE TABLE backup_attendance_settings_dates AS SELECT id, start_date, end_date FROM attendance_settings;` |
| LOW | Net effect of V18+V19 | V18 adds `start_date`/`end_date`; V19 drops them immediately. **Zero net schema change.** | Unnecessary churn in migration history; adds no value and creates a brief window where the columns exist. | Remove both V18 and V19 entirely if the columns are not needed. |

## Table checks
- No PK/FK/index changes. Columns are simply dropped.

## Suggested improvements (corrected SQL)

```sql
-- If the columns are truly unneeded, remove both V18 and V19 entirely.
-- If they are needed, keep V18 and remove V19.
-- If you must drop, back up first:
CREATE TABLE IF NOT EXISTS backup_attendance_settings_dates AS
  SELECT id, start_date, end_date FROM attendance_settings;

ALTER TABLE attendance_settings DROP COLUMN start_date, DROP COLUMN end_date;
```
