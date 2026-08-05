# V2__production_upgrade.sql

## Purpose
Enterprise upgrade: converts the V1 UUID `BINARY(16)` schema to `BIGINT AUTO_INCREMENT`, renames `stages`→`activity_stages` and `student_groups`→`groups`, drops all V1 foreign keys and triggers, creates 10 new production tables (`subjects`, `students`, `student_guardians`, `activity_subgroups`, `activities`, `discipline_logs`, `attendance`, `marks`, `system_settings`, `user_sub_roles`), migrates users/students/faculty data, seeds default roles and an admin user, re-creates a subset of FKs and indexes, drops the old profile/parent tables and re-creates the XP triggers.

## Tables / objects created / altered
- Renamed: `stages`→`activity_stages`, `student_groups`→`groups`.
- Created: `subjects`, `students`, `student_guardians`, `activity_subgroups`, `activities`, `discipline_logs`, `attendance`, `marks`, `system_settings`, `user_sub_roles`.
- Dropped: `student_profiles`, `faculty_profiles`, `student_parents`.
- Altered (PK/FK/data-type conversion + column adds/drops): all V1 tables.
- Recreated triggers: `trg_xp_after_insert`, `trg_xp_after_update`, `trg_xp_after_delete`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| CRITICAL | (whole migration) | Uses **MariaDB-only syntax** `ALTER TABLE … DROP FOREIGN KEY IF EXISTS` (lines 26–86) and `DROP COLUMN IF EXISTS` (lines 187–188, 835–859). Standard MySQL 8.0 does not support `IF EXISTS`/`IF NOT EXISTS` on these ALTER clauses → **syntax error (1064) at line 26**. | The migration never runs on the declared platform (header says "MySQL 8.0+"). V2 is the core of the schema — nothing after it can execute. | Guard each statement with `INFORMATION_SCHEMA` + `PREPARE`, e.g. for every FK: `SET @s=(SELECT IF(COUNT(*)>0,'ALTER TABLE departments DROP FOREIGN KEY fk_departments_hod_user_id','SELECT 1') FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='departments' AND CONSTRAINT_NAME='fk_departments_hod_user_id'); PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;` |
| CRITICAL | `users.section`, `users.year` (lines 360–361) | `ALTER TABLE users MODIFY section VARCHAR(50) DEFAULT NULL;` and `… MODIFY year VARCHAR(10) DEFAULT NULL;` — the `users` table has **no `section` or `year` column** (V1 users has none; V2 adds only `username`, `full_name`, `active`, `temp_dept_id`). → **ERROR 1054 Unknown column** → migration aborts. | Schema cannot be built; the upgrade halts mid-flight after data changes have already been made. | Delete both statements (section/year belong to `students`), or apply them to `students`. |
| CRITICAL | `audit_logs.entity_name` (line 730) | `ALTER TABLE audit_logs MODIFY entity_name VARCHAR(100) NOT NULL;` — V1 `audit_logs` has **`entity_type`**, not `entity_name`. → **ERROR 1054**. | Migration aborts. | `ALTER TABLE audit_logs MODIFY entity_type VARCHAR(100) NOT NULL;` |
| CRITICAL | `users` / `user_roles` (lines 768–771) | **Hardcoded default admin credential**: `INSERT INTO users (1,'admin', '$2a$10$…', …)` with the BCrypt hash of `12345` (documented in a comment), auto-assigned `ROLE_ADMIN`. `ON DUPLICATE KEY UPDATE … password = VALUES(password)` **resets the admin password to the known value** if the statement ever re-executes (re-run, cloned env, restore). | Publicly-known default password = instant full-admin compromise on any deployed instance; the reset clause can silently overwrite a password an admin already changed. | Remove the seed from the migration. Bootstrap via env-provided BCrypt hash + forced password change; or `INSERT … SELECT` with a hash injected at deploy time and no `ON DUPLICATE KEY UPDATE` on password. |
| HIGH | `role_permissions`, `rules`, `rule_conditions`, `group_members`, `submissions`, `submission_evidence`, `violation_types`, `violations`, `violation_evidence`, `xp_transactions`, `streaks`, `notifications`, `student_stage_progress`, `student_xp_summary`, `departments(hod_user_id)` | V2 drops **all ~50 V1 FK constraints** (lines 26–86) but only re-creates **15** (users, user_roles, groups, students, activity_subgroups, activities, discipline_logs, attendance, marks, audit_logs, login_history). The tables above are left with **no foreign keys at all**. | The DB no longer enforces any relationship in the XP domain → orphaned submissions/violations/XP rows, lost cascades, silent data corruption. | Re-add the full FK set, e.g.: `ALTER TABLE submissions ADD CONSTRAINT fk_sub_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE; ALTER TABLE submissions ADD CONSTRAINT fk_sub_rule FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE RESTRICT; ALTER TABLE violations ADD CONSTRAINT fk_vio_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE; ALTER TABLE xp_transactions ADD CONSTRAINT fk_xp_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE; ALTER TABLE rules ADD CONSTRAINT fk_rules_stage FOREIGN KEY (stage_id) REFERENCES activity_stages(id) ON DELETE RESTRICT;` (full list: see SUMMARY.md) |
| HIGH | `users.username` | Added `VARCHAR(100) NULL` (line 330), made `NOT NULL` (line 348) — but **no UNIQUE constraint and no index**. The old `idx_users_email_status` was auto-dropped when `status_id` was dropped. | Duplicate usernames possible (email-prefix collision: `a@x.com` and `a@y.com` both become `a`); every login lookup by username is a full table scan. | `ALTER TABLE users ADD UNIQUE KEY uk_users_username (username);` |
| HIGH | triggers `trg_xp_after_*` (lines 906–909 etc.) | New triggers compute the stage as `SELECT s.id FROM activity_stages s ORDER BY s.id DESC LIMIT 1` — always the **highest stage id**, ignoring `min_xp`/`max_xp` and `total_xp` (V1 used a threshold query). | Every XP insert/update/delete silently promotes the student to the top stage → ranking/promotion data corrupt. | Restore threshold logic: `SELECT s.id INTO new_stage FROM activity_stages s WHERE cur_total >= s.min_xp AND (s.max_xp IS NULL OR cur_total <= s.max_xp) ORDER BY s.min_xp DESC LIMIT 1;` |
| HIGH | `roles` (lines 761–766) | V1 roles (STUDENT, FACULTY, HOD, ADMIN, PLACEMENT_OFFICER, PARENT) become ids **1–6** after BIGINT conversion. V2 then `INSERT` ids 1–4 with `ON DUPLICATE KEY UPDATE name` → **silently renames**: STUDENT→ROLE_ADMIN, FACULTY→ROLE_TEACHER, HOD→ROLE_STUDENT, ADMIN→ROLE_TRANSPORT. | Role ids/names are scrambled; `user_roles` now point at wrong role semantics → authorization misconfig, misleading audit. | Don't reuse ids. Upsert by name with distinct ids: `INSERT INTO roles (name) VALUES ('ROLE_ADMIN'),('ROLE_TEACHER'),('ROLE_STUDENT'),('ROLE_TRANSPORT') ON DUPLICATE KEY UPDATE id=id;` then map by name: `INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username='admin' AND r.name='ROLE_ADMIN';` |
| HIGH | `student_parents` (lines 862–864) | `DROP TABLE student_profiles, faculty_profiles, student_parents;` — the student↔parent links in `student_parents` are deleted with **no migration target**. | Permanent loss of guardian/relationship data; no backup. | Migrate first: `CREATE TABLE user_relationships LIKE student_parents; INSERT INTO user_relationships SELECT * FROM student_parents;` then drop. |
| MEDIUM | `activities.xp`, `activities.cap`, `activities.frequency` (lines 263–265) | Numbers stored as `VARCHAR(100)` strings (`'50'`, `'1'`). | Numeric ops require CAST (V9 has to `CAST(xp AS SIGNED)`), no range validation, wrong sort/aggregate, junk text accepted. | `ALTER TABLE activities MODIFY xp INT NULL, MODIFY cap INT NULL;` (convert `frequency` to an FK/ENUM) |
| MEDIUM | `activities.created_at` (line 270) | `DATETIME(6) NOT NULL` with **no DEFAULT**; `updated_at DATETIME(6) DEFAULT NULL`. | Any insert omitting `created_at` fails; no auto-maintenance of timestamps. | `ALTER TABLE activities MODIFY created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);` |
| MEDIUM | `users.password`, `students.password` | `password_hash` was **renamed to `password`** (line 351); new `students.password` uses the same name. | Column name gives no indication the value is hashed → invites plaintext storage and wrong code paths; auditors cannot tell intent. (Seed does use a BCrypt hash — good — but the naming is a regression.) | `ALTER TABLE users CHANGE password password_hash VARCHAR(255) NOT NULL; ALTER TABLE students CHANGE password password_hash VARCHAR(255) NOT NULL;` |
| MEDIUM | `audit_logs.old_value`, `audit_logs.new_value` (lines 731–732) | Converted from `JSON` to `TEXT`. | Loses JSON validation — any malformed string is accepted into an audit log. | `ALTER TABLE audit_logs MODIFY old_value JSON NULL, MODIFY new_value JSON NULL;` |
| MEDIUM | `notifications` | All FKs (`fk_notif_user/type/submission/violation`) dropped and **never re-created**; new `recipient_id` is polymorphic (`recipient_type` + `recipient_id`), so no FK is possible. | Orphan notifications; no referential integrity on recipient. | Add a concrete FK for user recipients: `ALTER TABLE notifications ADD COLUMN user_id BIGINT NULL; ALTER TABLE notifications ADD CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;` |
| MEDIUM | `departments.hod_user_id` | Left as `BINARY(16)` (only id/name/code were converted); its FK was dropped at line 26 and never re-added. | Value type no longer matches `users.id` (now BIGINT) → can never join; dangling legacy column. | `ALTER TABLE departments MODIFY hod_user_id BIGINT NULL; ALTER TABLE departments ADD CONSTRAINT fk_departments_hod_user_id FOREIGN KEY (hod_user_id) REFERENCES users(id) ON DELETE SET NULL;` |
| MEDIUM | `discipline_logs.recorded_by_id` (line 751) | Backfill hardcodes `recorded_by_id = 1` ("Fallback to system admin user (id = 1)"). | XP history attributed to the wrong person if id 1 is not the admin; breaks if seed order changes. | Resolve dynamically: `(SELECT id FROM users WHERE username='admin' LIMIT 1)` |
| MEDIUM | triggers `trg_xp_after_*` | Hardcoded source-type ids `v_sub_id BIGINT DEFAULT 1`, `v_vio_id BIGINT DEFAULT 2`. | Only correct by seed-order accident; any change to `xp_source_types` insert order silently mis-totals XP. | `SET v_sub_id = (SELECT id FROM xp_source_types WHERE code='SUBMISSION' LIMIT 1); SET v_vio_id = (SELECT id FROM xp_source_types WHERE code='VIOLATION' LIMIT 1);` |
| MEDIUM | `students.student_id` | This column is the **register/roll number** (`VARCHAR(100) UNIQUE`), while `student_id` in `submissions`/`violations`/`xp_transactions` means *the student's users.id*. | Same column name, two meanings → join bugs and wrong-index usage. | Rename the roll number: `ALTER TABLE students CHANGE student_id reg_no VARCHAR(100) NOT NULL; ALTER TABLE students ADD UNIQUE KEY uk_students_reg_no (reg_no);` |
| MEDIUM | `students.spr_no` | `VARCHAR(100) DEFAULT NULL` with no UNIQUE and no index. | Duplicate SPR numbers possible; SPR lookups are full scans. | `ALTER TABLE students ADD UNIQUE KEY uk_students_spr_no (spr_no);` |
| MEDIUM | `attendance` | No UNIQUE on `(student_id, date)`. | Duplicate attendance rows for the same student/day → wrong percentages. | `ALTER TABLE attendance ADD UNIQUE KEY uk_attendance_student_date (student_id, date);` |
| MEDIUM | `marks` | No UNIQUE on `(student_id, subject_id, exam_type)`. | Duplicate exam scores double-counted in aggregates. | `ALTER TABLE marks ADD UNIQUE KEY uk_marks_student_subject_exam (student_id, subject_id, exam_type);` |
| MEDIUM | `students.year`, `students.semester`, `students.gender`, `students.academic_year` | Textual `VARCHAR` codes ('1', '2', 'Sem 1') instead of lookups/ENUM/int. | No referential/range validation; free-text drift; the JPA entity later uses lookup ids (`year_id`, `semester_id`, `gender_id`) → drift. | Convert to FK lookups or `ENUM`: `ALTER TABLE students MODIFY year INT NULL;` / add `year_id BIGINT` + FK |
| MEDIUM | `departments.code` (line 164) | `MODIFY code VARCHAR(50) NOT NULL` — data-dependent: any existing row with `NULL` code → ALTER fails. | Non-idempotent on real production data. | Backfill first: `UPDATE departments SET code = CONCAT('DEPT-', id) WHERE code IS NULL;` |
| MEDIUM | `activities` | No index on `name`, `category`, `xp_category`. | Activity search/listing by name or category scans the whole table. | `CREATE INDEX idx_activities_name ON activities (name); CREATE INDEX idx_activities_category ON activities (category);` |
| LOW | `user_statuses` | Becomes orphaned once `users.status_id` is dropped; table is kept but unused. | Dead schema; confusing. | Drop or re-link: `DROP TABLE IF EXISTS user_statuses;` (after confirming nothing references it) |
| LOW | `system_settings`, `attendance`, `marks`, `discipline_logs` | Have `created_at` but no `updated_at`. | No way to know when a record last changed. | `ALTER TABLE attendance ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;` (repeat per table) |
| LOW | `students.group_id` + `group_members` | Membership modeled twice: denormalized `students.group_id` AND the `group_members` join table. | Two sources of truth that can diverge. | Consolidate on one model (keep the join table, drop `students.group_id` or vice-versa). |

## Additional notes
- `SET FOREIGN_KEY_CHECKS = 0` at the start masks the FK-ordering problem instead of fixing it. The `IF EXISTS` syntax is the real blocker.
- The only re-created FKs (section 10) are correct for the tables they cover (students, groups, activities, attendance, marks, audit, login). Everything else is missing.

## Suggested improvements (corrected SQL)

```sql
-- 1. Replace MariaDB-only syntax with guarded PREPARE (one example; apply to all ~60 statements)
SET @s = (SELECT IF(COUNT(*)>0, 'ALTER TABLE departments DROP FOREIGN KEY fk_departments_hod_user_id', 'SELECT 1')
          FROM information_schema.TABLE_CONSTRAINTS
          WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME='departments' AND CONSTRAINT_NAME='fk_departments_hod_user_id');
PREPARE stmt FROM @s; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 2. Remove the two broken ALTERs on users.section / users.year (do not exist).

-- 3. Fix the audit_logs alter to use the real column
ALTER TABLE audit_logs MODIFY entity_type VARCHAR(100) NOT NULL;

-- 4. Remove the hardcoded admin seed; bootstrap at deploy time instead
--    (env var BCRYPT_HASH) — never commit a known password.

-- 5. Re-add dropped foreign keys (subset; repeat for all)
ALTER TABLE rules          ADD CONSTRAINT fk_rules_stage FOREIGN KEY (stage_id) REFERENCES activity_stages(id) ON DELETE RESTRICT;
ALTER TABLE rules          ADD CONSTRAINT fk_rules_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT;
ALTER TABLE rule_conditions ADD CONSTRAINT fk_rule_conditions_rule FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE;
ALTER TABLE group_members  ADD CONSTRAINT fk_gm_group FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE;
ALTER TABLE group_members  ADD CONSTRAINT fk_gm_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE submissions    ADD CONSTRAINT fk_sub_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE submissions    ADD CONSTRAINT fk_sub_rule FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE RESTRICT;
ALTER TABLE submissions    ADD CONSTRAINT fk_sub_status FOREIGN KEY (status_id) REFERENCES submission_statuses(id) ON DELETE RESTRICT;
ALTER TABLE submission_evidence ADD CONSTRAINT fk_ev_submission FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE;
ALTER TABLE violations     ADD CONSTRAINT fk_vio_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE violations     ADD CONSTRAINT fk_vio_type FOREIGN KEY (violation_type_id) REFERENCES violation_types(id) ON DELETE RESTRICT;
ALTER TABLE violation_evidence ADD CONSTRAINT fk_ve_violation FOREIGN KEY (violation_id) REFERENCES violations(id) ON DELETE CASCADE;
ALTER TABLE xp_transactions ADD CONSTRAINT fk_xp_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE xp_transactions ADD CONSTRAINT fk_xp_source_type FOREIGN KEY (source_type_id) REFERENCES xp_source_types(id) ON DELETE RESTRICT;
ALTER TABLE streaks        ADD CONSTRAINT fk_streak_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE streaks        ADD CONSTRAINT fk_streak_rule FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE;
ALTER TABLE notifications  ADD CONSTRAINT fk_notif_user FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE student_stage_progress ADD CONSTRAINT fk_ssp_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE student_stage_progress ADD CONSTRAINT fk_ssp_stage FOREIGN KEY (current_stage_id) REFERENCES activity_stages(id) ON DELETE RESTRICT;
ALTER TABLE student_xp_summary ADD CONSTRAINT fk_sxs_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE;
ALTER TABLE departments MODIFY hod_user_id BIGINT NULL;
ALTER TABLE departments ADD CONSTRAINT fk_departments_hod_user_id FOREIGN KEY (hod_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- 6. Username uniqueness
ALTER TABLE users ADD UNIQUE KEY uk_users_username (username);

-- 7. Trigger: restore threshold-based stage lookup (in all three triggers)
SELECT s.id INTO new_stage FROM activity_stages s
WHERE cur_total >= s.min_xp AND (s.max_xp IS NULL OR cur_total <= s.max_xp)
ORDER BY s.min_xp DESC LIMIT 1;

-- 8. Roles: no id reuse
INSERT INTO roles (name) VALUES ('ROLE_ADMIN'),('ROLE_TEACHER'),('ROLE_STUDENT'),('ROLE_TRANSPORT') ON DUPLICATE KEY UPDATE id=id;
INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username='admin' AND r.name='ROLE_ADMIN';

-- 9. Preserve parent links before dropping
CREATE TABLE user_relationships LIKE student_parents;
INSERT INTO user_relationships SELECT * FROM student_parents;
DROP TABLE IF EXISTS student_profiles, faculty_profiles, student_parents;

-- 10. Numeric-as-string + defaults + keys
ALTER TABLE activities MODIFY xp INT NULL, MODIFY cap INT NULL;
ALTER TABLE activities MODIFY created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
ALTER TABLE attendance ADD UNIQUE KEY uk_attendance_student_date (student_id, date);
ALTER TABLE marks ADD UNIQUE KEY uk_marks_student_subject_exam (student_id, subject_id, exam_type);
CREATE INDEX idx_activities_name ON activities (name);
CREATE INDEX idx_activities_category ON activities (category);
```
