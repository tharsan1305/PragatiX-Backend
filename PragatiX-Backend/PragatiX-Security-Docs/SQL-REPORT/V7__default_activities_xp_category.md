# V7__default_activities_xp_category.sql

## Purpose
Backfills NULL `xp_category` values in `activities` to `'Academic'` for backward compatibility.

## Tables / columns altered
`activities.xp_category` (data only).

## Findings

**No issues found.** This is a non-destructive, targeted data backfill:
- It does not alter schema, drop data, or weaken constraints.
- `xp_category` exists on `activities` (created in V2). ✅
- It only touches rows where `xp_category IS NULL`. ✅

## Table checks
- PK, indexes, constraints unchanged. Clean.

## Suggested improvements

None required. (Optional: to keep the invariant enforced going forward, add a `CHECK (xp_category IN ('Academic','Sports','Cultural',…))` — but this is a product-domain decision.)
