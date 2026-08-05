# V14__remove_assigned_academic_year.sql

## Purpose
Consolidates `assigned_academic_year` into `academic_year` on the `users` table (if it exists) and drops any legacy `assigned_academic_year` columns from `users` and `activities`.

## Tables / columns altered
`users.academic_year` (added if absent), `users.assigned_academic_year` (dropped if both exist), `activities.assigned_academic_year` (dropped if present).

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| LOW | `users.academic_year` | Adds a denormalized `academic_year VARCHAR(50)` column to `users`. Academic year is a student-level attribute, not a user-level one. Storing it on `users` duplicates state and can drift out of sync with the student's actual year. | Data integrity risk — a user's academic year can diverge from the student record. | Keep `academic_year` on `students` only; do not add it to `users`. |

## Table checks
- All dynamic guards (`INFORMATION_SCHEMA` checks) are safe and idempotent. ✅
- No PK/FK/index changes. ✅

## Suggested improvements (corrected SQL)

```sql
-- Do NOT add academic_year to users. It belongs on students.
-- The dynamic guards are fine; just skip the users alterations.
-- V14 is essentially a no-op on a properly designed schema.
```
