# V12__fix_activities_subgroup_column.sql

## Purpose
Safely makes the legacy `subgroup` column on `activities` nullable if it exists, using a dynamic `INFORMATION_SCHEMA` guard.

## Tables / columns altered
`activities.subgroup` (conditional — only if the column exists).

## Findings

**No issues found.** The migration is safe:
- Uses `INFORMATION_SCHEMA.COLUMNS` to check existence before altering — idempotent.
- Only modifies the column to `NULL`; does not drop data.
- Does not affect any other table. ✅

## Table checks
- PK, FKs, indexes on `activities` unchanged. ✅

## Suggested improvements

None required. (Optional: the legacy `subgroup` column is now redundant once `subgroup_id` (FK to `activity_subgroups`) exists — V15 drops it.)
