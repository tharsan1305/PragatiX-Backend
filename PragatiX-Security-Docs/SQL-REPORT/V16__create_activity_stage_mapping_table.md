# V16__create_activity_stage_mapping_table.sql

## Purpose
Creates `activity_stage_mappings` (a reusable mapping table linking activities to stages via subgroups) and backfills it from existing `activities` + `activity_subgroups` data.

## Tables / objects created
`activity_stage_mappings` — columns: `id` (BIGINT PK AUTO_INCREMENT), `activity_id`, `stage_id`, `subgroup_id`, `display_order`, `created_at`. Unique key `uq_stage_activity (stage_id, activity_id)`. FKs to `activities`, `activity_stages`, `activity_subgroups`.

## Findings

| Severity | Table/Column | Issue | Why it matters | Recommended fix (SQL) |
|----------|--------------|-------|----------------|------------------------|
| CRITICAL | `activity_stage_mappings.stage_id` FK | `CONSTRAINT fk_asm_stage FOREIGN KEY (stage_id) REFERENCES stages(id)` — the table `stages` was **renamed to `activity_stages`** in V2. MySQL 8.0 raises **ERROR 1824 "Failed to open the referenced table 'stages'"** at CREATE TABLE time. | The entire migration aborts; `activity_stage_mappings` is never created. | Change the FK reference: `CONSTRAINT fk_asm_stage FOREIGN KEY (stage_id) REFERENCES activity_stages(id) ON DELETE CASCADE` |
| LOW | `activity_stage_mappings` | Has `created_at` but no `updated_at` audit column. | Cannot detect when a mapping was last modified. | `ALTER TABLE activity_stage_mappings ADD COLUMN updated_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);` |

## Table checks
- PK (`id`) present. ✅
- Unique key `uq_stage_activity` on `(stage_id, activity_id)` — prevents duplicate mappings. ✅
- FK to `activity_subgroups` on `subgroup_id` — correct. ✅
- FK to `activities` on `activity_id` — correct. ✅
- Backfill INSERT IGNORE is safe (idempotent). ✅

## Suggested improvements (corrected SQL)

```sql
CREATE TABLE IF NOT EXISTS `activity_stage_mappings` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `activity_id` BIGINT NOT NULL,
  `stage_id` BIGINT NOT NULL,
  `subgroup_id` BIGINT NOT NULL,
  `display_order` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_stage_activity` (`stage_id`, `activity_id`),
  CONSTRAINT `fk_asm_activity` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_asm_stage` FOREIGN KEY (`stage_id`) REFERENCES `activity_stages` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_asm_subgroup` FOREIGN KEY (`subgroup_id`) REFERENCES `activity_subgroups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO activity_stage_mappings (activity_id, stage_id, subgroup_id, created_at)
SELECT a.id, sg.stage_id, a.subgroup_id, NOW()
FROM activities a
JOIN activity_subgroups sg ON a.subgroup_id = sg.id;
```
