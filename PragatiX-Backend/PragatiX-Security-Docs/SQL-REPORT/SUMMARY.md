# PragatiX — Migration Security & Schema Audit — SUMMARY

**Audited files:** `N:\pragatiX\PragatiX-Backend\migration\` (V1 → V19, 19 files)
**Scope:** primary keys, foreign keys, indexes, data types, nullability, uniqueness, security, character sets, naming, migration safety.
**Database platform declared by the migrations:** MySQL 8.0+.

---

## Global headline findings (read first)

1. **The migration set cannot build a schema on a clean MySQL 8.0 instance.** V1 fails (FK to `users` before `users` exists), V2 fails (MariaDB-only `IF EXISTS` ALTER syntax + ALTERs on columns that do not exist), V13 fails (`activity_name` column does not exist), V16 fails (FK references `stages`, renamed to `activity_stages` in V2), V17 fails (MariaDB-only syntax + non-existent table `activity_assignments` + FK to `stages`). This is why the codebase "works" — the real schema is created by **Hibernate `ddl-auto: update`**, not by these migrations.
2. **Flyway is not wired into the application.** `pom.xml` has no Flyway/Liquibase dependency and `application.yml` has no `spring.flyway.*` config. The `migration/` folder is an unused/aspirational artifact. **Fix: configure a real migration tool and set `ddl-auto: validate`.**
3. **Committed credentials in config files** (see "Beyond the migrations" section): MySQL password `sharu`, Spring Security default `admin/admin`, a hardcoded JWT signing secret, and a Twilio account SID + auth token — all in source control.
4. **Schema drift between JPA entities and the migrations.** Entities expect columns/tables the migrations never create (`activity_name`, `section_id`, `user_id`, `attendance_settings`, `activity_assignments`, `groups`, `activity_stages`, `gender_id`, `year_id`, `semester_id`, …). Whoever runs only the migrations gets a schema the application cannot use; whoever lets Hibernate run gets a schema Flyway cannot reproduce.

---

## Totals (migration findings only)

| Severity | Count |
|----------|-------|
| CRITICAL (security / data loss / migration abort) | **10** |
| HIGH (missing PK / FK / broken logic) | **9** |
| MEDIUM (missing index, wrong type, weak constraint) | **22** |
| LOW (naming / style / minor) | **17** |
| **Total findings** | **58** |

**Tables managed by the migration set:** 45
- V1 creates 37 tables; V2 renames 2 (`stages`→`activity_stages`, `student_groups`→`groups`) and adds 10 (`subjects`, `students`, `student_guardians`, `activity_subgroups`, `activities`, `discipline_logs`, `attendance`, `marks`, `system_settings`, `user_sub_roles`); V2 drops 3 (`student_profiles`, `faculty_profiles`, `student_parents`); V16 adds 1 (`activity_stage_mappings`).
- Plus 2 tables *referenced by* migrations but **never created by them**: `attendance_settings` (V18, V19) and `activity_assignments` (V17).

**Health score: 12 / 100** — computed as `100 − (4 × CRITICAL + 2 × HIGH + 1 × MEDIUM + 0.5 × LOW)`, floored at 0. The score is this low because V1, V2, V13, V16 and V17 abort on a clean MySQL 8.0 database.

---

## Findings by file

| File | C | H | M | L | Blocker? |
|------|---|---|---|---|----------|
| [V1__init.sql](V1__init.md) | 1 | 0 | 0 | 4 | **Yes — FK references table created later** |
| [V2__production_upgrade.sql](V2__production_upgrade.md) | 4 | 5 | 14 | 3 | **Yes — MariaDB syntax + unknown columns** |
| [V3__make_student_section_nullable.sql](V3__make_student_section_nullable.md) | 0 | 1 | 0 | 0 | Yes — unknown column `section_id` |
| [V4__make_student_user_nullable.sql](V4__make_student_user_nullable.md) | 0 | 1 | 0 | 0 | Yes — unknown column `user_id` |
| [V5__set_student_password_not_null.sql](V5__set_student_password_not_null.md) | 0 | 0 | 1 | 0 | Data-dependent |
| [V6__add_activity_stage_fields.sql](V6__add_activity_stage_fields.md) | 0 | 0 | 1 | 1 | No |
| [V7__default_activities_xp_category.sql](V7__default_activities_xp_category.md) | 0 | 0 | 0 | 0 | Clean |
| [V8__add_activity_event_fields.sql](V8__add_activity_event_fields.md) | 0 | 0 | 0 | 2 | No |
| [V9__update_activity_rules_fields.sql](V9__update_activity_rules_fields.md) | 0 | 0 | 1 | 1 | No |
| [V10__award_rules_refactor.sql](V10__award_rules_refactor.md) | 0 | 0 | 1 | 0 | No |
| [V11__add_assignment_mode.sql](V11__add_assignment_mode.md) | 0 | 0 | 0 | 1 | No |
| [V12__fix_activities_subgroup_column.sql](V12__fix_activities_subgroup_column.md) | 0 | 0 | 0 | 0 | Clean |
| [V13__fix_activity_unique_constraint.sql](V13__fix_activity_unique_constraint.md) | 1 | 0 | 0 | 0 | **Yes — unknown column `activity_name`** |
| [V14__remove_assigned_academic_year.sql](V14__remove_assigned_academic_year.md) | 0 | 0 | 0 | 1 | No |
| [V15__drop_legacy_subgroup_column.sql](V15__drop_legacy_subgroup_column.md) | 0 | 0 | 1 | 0 | No |
| [V16__create_activity_stage_mapping_table.sql](V16__create_activity_stage_mapping_table.md) | 1 | 0 | 0 | 1 | **Yes — FK references `stages`** |
| [V17__add_stage_id_and_overrides.sql](V17__add_stage_id_and_overrides.md) | 3 | 0 | 1 | 0 | **Yes — 3 failures** |
| [V18__update_attendance_settings_dates.sql](V18__update_attendance_settings_dates.md) | 0 | 1 | 1 | 1 | Yes — table not created by migrations |
| [V19__drop_attendance_dates.sql](V19__drop_attendance_dates.md) | 0 | 1 | 1 | 1 | Yes — table not created by migrations |

---

## Priority Action List (do these first, in this order)

1. **Make V1 runnable.** Move `departments.hod_user_id` FK creation to *after* `users` is created (or set `FOREIGN_KEY_CHECKS=0`). *(V1 — CRITICAL)*
2. **Remove all MariaDB-only `IF EXISTS` / `IF NOT EXISTS` ALTER syntax in V2 and V17** and replace with `INFORMATION_SCHEMA`-guarded `PREPARE` statements. *(V2, V17 — CRITICAL)*
3. **Delete the broken ALTERs in V2** on columns that do not exist: `users.section`, `users.year`, `audit_logs.entity_name`. *(V2 — CRITICAL)*
4. **Remove the hardcoded admin credential** (`admin` / `12345`) and the `ON DUPLICATE KEY UPDATE … password = VALUES(password)` reset clause. Bootstrap admins from environment secrets and force a password change. *(V2 — CRITICAL)*
5. **Fix FK references to `stages`** → `activity_stages(id)` in V16 and V17; create `activity_assignments` and `attendance_settings` tables in a migration instead of relying on Hibernate. *(V16, V17, V18, V19 — CRITICAL/HIGH)*
6. **Fix V13's unique constraint** to use the real columns `(subgroup_id, name)` — `activity_name` does not exist in the migration-built `activities` table. *(V13 — CRITICAL)*
7. **Re-create the ~35 FK constraints that V2 dropped and never re-added** (rules, rule_conditions, submissions, submission_evidence, violations, violation_evidence, xp_transactions, streaks, notifications, student_stage_progress, student_xp_summary, role_permissions, group_members, departments.hod_user_id). *(V2 — HIGH)*
8. **Add `UNIQUE` + index on `users.username`** (login identifier). *(V2 — HIGH)*
9. **Restore threshold-based stage promotion in the V2 triggers** (currently `ORDER BY id DESC LIMIT 1` puts every student at the top stage). *(V2 — HIGH)*
10. **Fix the V2 role seed collision** — V2 reuses ids 1–4 which V1 already assigned to STUDENT/FACULTY/HOD/ADMIN, silently renaming them. *(V2 — HIGH)*
11. **Preserve `student_parents` data** before `DROP TABLE` in V2 (guardian links are permanently lost). *(V2 — HIGH)*
12. **Align V3/V4/V5 with reality** — target the actual columns (`section`, `user_id` created explicitly), backfill NULL passwords before making them `NOT NULL`. *(V3, V4, V5)*
13. **Remove/rotate all committed secrets** (MySQL password, JWT secret, Twilio credentials, `admin/admin`) and replace Hibernate `ddl-auto: update` with a real migration tool (`validate`). *(config files)*
14. **MEDIUM cleanup batch:** numbers stored as strings in `activities.xp/cap/frequency`; unique keys on `attendance(student_id,date)` and `marks(student_id,subject_id,exam_type)`; rename `password`→`password_hash`; index `activities.name/category`; keep `audit_logs.old_value/new_value` as JSON; convert `departments.hod_user_id` to `BIGINT`; backfill `departments.code` before `NOT NULL`.

---

## Beyond the migrations — secrets and tooling found in the application config

| Severity | File | Issue | Why it matters | Fix |
|----------|------|-------|----------------|-----|
| CRITICAL | `src/main/resources/application.yml` | MySQL password `sharu` committed for user `root` | Full DB credentials in source control — any repo/CI leak gives database access | Remove; inject via env var (`${DB_PASSWORD}`) and rotate |
| CRITICAL | `src/main/resources/application.yml` | Spring Security default user `admin`/`admin` | Well-known default credential on every environment | Remove; force real user provisioning |
| CRITICAL | `src/main/resources/application.yml` | Hardcoded JWT secret `spdms_super_secret_key_must_be_at_least_256_bits_long_for_hs256_algorithm` | Static, publicly-known signing key → anyone can forge JWTs and impersonate any user | Move to `JWT_SECRET` env var; rotate |
| CRITICAL | `src/main/resources/application.properties` | Twilio account SID `ACca4ac3e3…` and auth token `e0980e6c…` committed | SMS gateway compromise / spam abuse / billing damage | Revoke token in Twilio console; move to env/secrets manager |
| CRITICAL | `src/main/resources/application.yml` | `spring.jpa.hibernate.ddl-auto: update` and **no Flyway/Liquibase dependency** | Schema is whatever Hibernate decides; migration files are never executed; schema drift guaranteed | Wire Flyway (`spring.flyway.*`, `ddl-auto: validate`) |
| HIGH | migrations ↔ entities | JPA entities require columns/tables the migrations never create (`activity_name`, `section_id`, `user_id`, `gender_id`, `year_id`, `semester_id`, `attendance_settings`, `activity_assignments`) | App and schema are out of sync; a migration-only build produces an unusable schema | Make the migration set authoritative and reconcile entities to it |

---

## Character set audit

All tables created by V1, V2 and V16 declare `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`. **No charset/collation violations found.**

---

## Naming consistency

- Mostly consistent `snake_case`. Flagged inconsistencies:
  - `users.password_hash` → renamed to `users.password` in V2 (loses hashing intent) — MEDIUM.
  - `students.student_id` is the *register/roll number*, while `student_id` elsewhere means *the student's user id* — two meanings, one name — MEDIUM.
  - `activity_stages.is_active` is `TINYINT(1)` while every other boolean uses `BOOLEAN` — LOW.
  - `attendance.date` shadows the SQL type name — LOW.
  - `groups` (renamed from `student_groups`) is fine in MySQL but confusing — LOW.
