# V4__make_student_user_nullable.sql

## Purpose
Makes `user_id` nullable on the `students` table.

## Tables / columns altered
`students.user_id` (intended).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| HIGH | `students.user_id` | The migration targets `students.user_id`, but **no migration in this set creates that column** (V2's `students` has no `user_id`; it exists only in the JPA `Student` entity via Hibernate `ddl-auto: update`). On a schema built from these migrations the ALTER fails with **ERROR 1054 Unknown column 'user_id'**. | Migration set is not self-contained; aborts on a migration-managed DB. | Create the column first: `ALTER TABLE students ADD COLUMN user_id BIGINT NULL; ALTER TABLE students MODIFY COLUMN user_id bigint NULL;` — and add the FK once created: `ALTER TABLE students ADD CONSTRAINT fk_students_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;` |

## Table checks
- The `students` table has a PK; this migration doesn't change that.

## Suggested improvements (corrected SQL)

```sql
ALTER TABLE students ADD COLUMN user_id BIGINT NULL;
ALTER TABLE students MODIFY COLUMN user_id bigint NULL;
ALTER TABLE students ADD CONSTRAINT fk_students_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```
