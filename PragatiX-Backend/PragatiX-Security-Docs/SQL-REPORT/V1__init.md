# V1__init.sql

## Purpose
Initial database schema ("SPDMS – Production-Ready Schema", MySQL 8.0+). Creates 37 tables using UUID `BINARY(16)` primary keys: 10 lookup tables, RBAC (roles/permissions/user_roles/role_permissions), profiles & parent link, stages, categories, rules & rule_conditions, groups & members, submissions & evidence, violations & evidence, the XP ledger, streaks, notifications, student stage progress, the materialized XP summary, audit logs and login history — plus 3 triggers that maintain XP summaries and stage progress.

## Tables / objects created
`user_statuses`, `frequencies`, `cap_periods`, `evidence_types`, `notification_types`, `submission_statuses`, `violation_statuses`, `violation_severities`, `xp_source_types`, `departments`, `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `student_profiles`, `faculty_profiles`, `student_parents`, `stages`, `categories`, `rules`, `rule_conditions`, `student_groups`, `group_members`, `submissions`, `submission_evidence`, `violation_types`, `violations`, `violation_evidence`, `xp_transactions`, `streaks`, `notifications`, `student_stage_progress`, `student_xp_summary`, `audit_logs`, `login_history`, triggers `trg_xp_after_insert/update/delete`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| CRITICAL | `departments.hod_user_id` | `CONSTRAINT fk_departments_hod_user_id FOREIGN KEY (hod_user_id) REFERENCES users(id)` is declared **inside** `CREATE TABLE departments`, which runs **before** `users` is created. MySQL 8.0 InnoDB validates the referenced table at CREATE time → **ERROR 1824 "Failed to open the referenced table 'users'"**. The file's own comment (lines 142–143) says the FK must be added after `users` exists, but the code keeps it inline — comment and DDL contradict each other. | V1 aborts on a clean MySQL 8.0 instance, so the schema (and any migration history) can never be built from scratch. | Remove the inline constraint from `CREATE TABLE departments`, then after `users` is created: `ALTER TABLE departments ADD CONSTRAINT fk_departments_hod_user_id FOREIGN KEY (hod_user_id) REFERENCES users(id) ON DELETE SET NULL;` |
| LOW | `categories`, `roles`, `permissions` | These lookup tables have `created_at` but no `updated_at`. | No way to see when a lookup definition was last changed; audit gap for reference data. | `ALTER TABLE categories ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);` (repeat for `roles`, `permissions`) |
| LOW | `rule_conditions` | No audit timestamps at all. | Cannot tell when a condition was added or changed. | `ALTER TABLE rule_conditions ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);` |
| LOW | `login_history.user_agent`, `stages.description`, `categories.description` | `TEXT` where `VARCHAR` (≤ 500) would do. `TEXT` can't be indexed without a prefix and adds a 2-byte length prefix + overflow-page handling. | Larger storage overhead, cannot index/compare efficiently for short values. | `ALTER TABLE login_history MODIFY user_agent VARCHAR(500) NULL;` (`stages.description`, `categories.description` → `VARCHAR(500) NULL`) |
| LOW | `users.phone`, `student_profiles.guardian_phone`, `guardian_email` | PII stored in plaintext. | Breach exposes phone numbers / guardian contact details; GDPR-style liability. | No DB-level encryption in MySQL; mitigate at application layer (encrypt before persist, `AES`/app crypto), restrict column grants, and pseudonymize in reports. |

## Table checks (V1)
- **Primary keys:** all 37 tables have a PK. ✅
- **Foreign keys:** every `*_id` reference column in V1 has a FK constraint, except the ordering bug on `departments.hod_user_id` above. ✅
- **Indexes:** lookup codes are `UNIQUE`; `users.email` unique + indexed; all FK columns are indexed; heavy query paths (`submissions`, `violations`, `xp_transactions`, `notifications`) are well covered. ✅
- **Data types:** appropriate; `BINARY(16)` UUIDs consistent. ✅
- **NULL constraints:** `password_hash`, `email`, `status_id` are `NOT NULL`. ✅
- **Uniques:** `users.email`, `student_profiles.register_number`, all lookup `code` columns, `stages.order_no`, `submissions` per-student-rule-week, `xp_transactions.idempotency_key`, `streaks` (student,rule). ✅
- **Character set:** all `utf8mb4 / utf8mb4_unicode_ci`. ✅

## Suggested improvements (corrected SQL)

```sql
-- 1. Fix the CRITICAL FK ordering: create departments WITHOUT the inline FK, then:
CREATE TABLE IF NOT EXISTS departments (
    id BINARY(16) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NULL UNIQUE,
    hod_user_id BINARY(16) NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_dep_active (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- …create users…
ALTER TABLE departments ADD CONSTRAINT fk_departments_hod_user_id
    FOREIGN KEY (hod_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- 2. Audit timestamps on lookup tables
ALTER TABLE categories ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
ALTER TABLE roles       ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
ALTER TABLE permissions ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
ALTER TABLE rule_conditions ADD COLUMN created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- 3. VARCHAR instead of TEXT for short fields
ALTER TABLE login_history MODIFY user_agent VARCHAR(500) NULL;
ALTER TABLE stages       MODIFY description VARCHAR(500) NULL;
ALTER TABLE categories   MODIFY description VARCHAR(500) NULL;
```
