# V3__make_student_section_nullable.sql

## Purpose
Makes `section_id` nullable on the `students` table.

## Tables / columns altered
`students.section_id` (intended).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| HIGH | `students.section_id` | The migration targets `students.section_id`, but **no migration in this set creates that column**. V2 created `students.section` as `VARCHAR(50)` — not `section_id` (which exists only in the JPA entity via Hibernate `ddl-auto: update`). On a schema built from these migrations the ALTER fails with **ERROR 1054 Unknown column 'section_id'**. | The migration set is not self-contained; on a Flyway-managed DB this aborts. | `ALTER TABLE students ADD COLUMN section_id BIGINT NULL;` (create the column explicitly first), or if the real column is `section`: `ALTER TABLE students MODIFY COLUMN section VARCHAR(50) NULL;` |

## Table checks
- The `students` table itself (from V2) has a PK (`id`), UNIQUE on `student_id` and `email`. Not affected by this migration.

## Suggested improvements (corrected SQL)

```sql
-- Option A: if section_id is the intended column, create it explicitly first
ALTER TABLE students ADD COLUMN section_id BIGINT NULL;
ALTER TABLE students MODIFY COLUMN section_id bigint NULL;

-- Option B: if the legacy VARCHAR column is what exists
ALTER TABLE students MODIFY COLUMN section VARCHAR(50) NULL;
```
