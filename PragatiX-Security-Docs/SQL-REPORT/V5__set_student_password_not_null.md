# V5__set_student_password_not_null.sql

## Purpose
Enforces that `students.password` is never NULL.

## Tables / columns altered
`students.password`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| MEDIUM | `students.password` | `MODIFY COLUMN password varchar(255) NOT NULL` is **data-dependent**: V2 created `students.password` as `VARCHAR(255) DEFAULT NULL`, populated only for rows migrated from `users`. Any `students` row with a NULL password (e.g. rows created directly, or students whose `users` row was missing) → the ALTER fails (error 1265 in strict mode). | Migration aborts on real data; also leaves the ambiguous `password` (vs `password_hash`) naming in place — see V2. | Backfill first, then alter — and rename to `password_hash`: `UPDATE students SET password = '' WHERE password IS NULL; ALTER TABLE students MODIFY COLUMN password varchar(255) NOT NULL; ALTER TABLE students CHANGE password password_hash varchar(255) NOT NULL;` |

## Table checks
- This column stores a credential; confirm the application always writes a BCrypt hash (the V2 admin seed uses BCrypt — good).

## Suggested improvements (corrected SQL)

```sql
-- Backfill before enforcing NOT NULL
UPDATE students SET password = '' WHERE password IS NULL;

-- Enforce + signal hashing intent
ALTER TABLE students MODIFY COLUMN password varchar(255) NOT NULL;
ALTER TABLE students CHANGE password password_hash varchar(255) NOT NULL;
```
