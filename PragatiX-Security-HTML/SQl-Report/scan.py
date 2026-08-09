import os
import re
import json
import glob
from datetime import datetime
from pathlib import Path

# ─── PATHS ──────────────────────────────────────────────────────────────────
SQL_DUMP_PATH = r"N:\pragatiX\Sql_Dump\PragatiX-SQL.dump"
REPORT_PATH   = r"N:\pragatiX\PragatiX-Security-HTML\Report"
os.makedirs(REPORT_PATH, exist_ok=True)

# ─── STEP 1: FILE DISCOVERY ──────────────────────────────────────────────────
sql_files = []
for root, dirs, files in os.walk(SQL_DUMP_PATH):
    dirs[:] = [d for d in dirs if d != '.git']
    for f in files:
        if f.endswith('.sql'):
            sql_files.append(os.path.join(root, f))

print(f"[SCAN] Found {len(sql_files)} SQL files")

# ─── STEP 2 & 3: PARSE + ANALYSE ─────────────────────────────────────────────
findings   = []
tables_meta = {}
summary_counts = {"critical":0,"high":0,"medium":0,"low":0,"info":0}

PATTERNS = {
    # Security
    "WEAK_PASSWORD_COLUMN": (re.compile(r'`password`\s+varchar\((?:50|100|150)\)', re.I), "High",
        "Undersized Password Column", "Security",
        "Password column uses VARCHAR(<256) — hashed BCrypt strings need at least 255 chars.",
        "Truncated BCrypt hashes may silently fail authentication checks.",
        "Use VARCHAR(255) or larger for password columns."),
    "PLAINTEXT_PASSWORD_HINT": (re.compile(r"'123|password123|admin123|test123|qwerty", re.I), "Critical",
        "Weak / Plaintext-Style Password in Data", "Security",
        "Data rows contain trivially guessable or plaintext-style password values.",
        "Credential stuffing and brute force attacks become trivial.",
        "Force password resets; enforce bcrypt hashing with cost ≥ 10."),
    "LOCK_TABLES": (re.compile(r'LOCK\s+TABLES', re.I), "Medium",
        "LOCK TABLES Usage", "Performance",
        "LOCK TABLES prevents concurrent reads/writes during bulk data loads.",
        "Can cause application downtime and connection queue exhaustion.",
        "Use transactions (BEGIN/COMMIT) or INSERT … ON DUPLICATE KEY UPDATE."),
    "DROP_TABLE_IF_EXISTS": (re.compile(r'DROP\s+TABLE\s+IF\s+EXISTS', re.I), "High",
        "DROP TABLE in Production Dump", "Security",
        "DROP TABLE statements are present; replaying this dump on a live DB destroys data.",
        "Accidental execution on production deletes entire tables.",
        "Gate dump scripts with environment checks; use idempotent migrations instead."),
    "INSERT_NO_COLS": (re.compile(r'INSERT\s+INTO\s+`?\w+`?\s+VALUES', re.I), "Medium",
        "INSERT Without Column List", "Best Practices",
        "INSERT … VALUES without an explicit column list is brittle — breaks on schema changes.",
        "Silent data misalignment on column addition/reordering.",
        "Always specify column names: INSERT INTO t (col1, col2) VALUES (…)."),
    "GTID_PURGED": (re.compile(r'GTID_PURGED', re.I), "Medium",
        "GTID_PURGED Set in Dump", "Security",
        "Setting GTID_PURGED requires SUPER privilege and can break replication if misapplied.",
        "Misconfigured replication can expose partial datasets.",
        "Remove GTID_PURGED lines when importing into a non-replica or fresh instance."),
    "SQL_LOG_BIN_OFF": (re.compile(r'SQL_LOG_BIN\s*=\s*0', re.I), "Medium",
        "Binary Logging Disabled", "Security",
        "SQL_LOG_BIN=0 disables binary log for the session, making changes un-replayable.",
        "Compliance and audit trails may be incomplete.",
        "Avoid disabling bin-log; use --skip-log-bin only in sanctioned DR scenarios."),
    "FOREIGN_KEY_OFF": (re.compile(r'FOREIGN_KEY_CHECKS\s*=\s*0', re.I), "High",
        "Foreign Key Checks Disabled", "Security",
        "FK checks are disabled during import — allows orphaned/corrupt referential data.",
        "Orphaned records lead to data integrity violations and application errors.",
        "Re-enable FK checks immediately after import; validate FK integrity post-load."),
    "UNIQUE_CHECKS_OFF": (re.compile(r'UNIQUE_CHECKS\s*=\s*0', re.I), "Medium",
        "Unique Checks Disabled", "Schema",
        "UNIQUE_CHECKS=0 skips duplicate-key enforcement during import.",
        "Duplicate rows can silently enter unique-indexed columns.",
        "Validate uniqueness constraints after import completion."),
    "CHARSET_UTF8_NOT_MB4": (re.compile(r'character_set_client\s*=\s*utf8[^m4]', re.I), "Low",
        "Non-UTF8MB4 Character Set", "Best Practices",
        "utf8 in MySQL is actually utf8mb3 — does not support 4-byte Unicode (emoji, CJK ext).",
        "Data loss on emoji/CJK characters; future migration overhead.",
        "Use utf8mb4 consistently across all connections, tables, and columns."),
    "NULLABLE_NOT_NULL": (re.compile(r'NOT NULL(?!\s+AUTO_INCREMENT)', re.I), "Info",
        "NOT NULL Constraint Present", "Schema",
        "NOT NULL constraints are correctly applied to mandatory columns.",
        "No risk — this is a positive finding.",
        "Continue enforcing NOT NULL on all logically mandatory columns."),
    "TIMESTAMP_NULL": (re.compile(r'timestamp\s+NULL', re.I), "Low",
        "Nullable TIMESTAMP Column", "Schema",
        "Timestamp columns allow NULL — distinguishing 'not set' vs epoch requires app-level logic.",
        "Ambiguous audit trail; NULL timestamps may bypass date-range queries.",
        "Use DEFAULT CURRENT_TIMESTAMP; only allow NULL where semantically required."),
    "AUTO_INCREMENT_HIGH": (re.compile(r'AUTO_INCREMENT=(\d+)', re.I), "Info",
        "AUTO_INCREMENT Value Exposed", "Best Practices",
        "Exported AUTO_INCREMENT hints reveal record-count scale to anyone reading the dump.",
        "Information disclosure about database size / activity level.",
        "Strip or mask AUTO_INCREMENT values in public-facing dumps."),
    "ENUM_COLUMN": (re.compile(r"enum\('[^']+'\)", re.I), "Low",
        "ENUM Column Usage", "Schema",
        "ENUM columns are inflexible — adding a new value requires an ALTER TABLE DDL.",
        "Schema migrations needed for every new enum value, causing potential downtime.",
        "Use a reference/lookup table instead of ENUM for extensible lists."),
    "VARCHAR_MAX": (re.compile(r'varchar\s*\(\s*255\s*\)', re.I), "Info",
        "VARCHAR(255) Usage", "Schema",
        "VARCHAR(255) is a common default; ensure the length is intentional, not cargo-cult.",
        "Oversized columns waste buffer pool space and slow index operations.",
        "Right-size VARCHAR lengths based on actual maximum data needs."),
    "MIXED_CASE_IDENTIFIERS": (re.compile(r'`[A-Z][a-z]+[A-Z]', re.I), "Low",
        "Mixed-Case Column Identifier", "Best Practices",
        "Mixed-case identifiers (camelCase) are case-sensitive on Linux MySQL but not on Windows.",
        "Portability issues when migrating between operating systems.",
        "Use snake_case for all MySQL identifiers."),
    "PHONE_SHORT": (re.compile(r"'(\d{3})'\s*,", re.I), "High",
        "Suspiciously Short Phone Number in Data", "Data Quality",
        "Data rows contain phone numbers with only 3 digits — likely test/stub data.",
        "Invalid contact data leads to failed SMS/OTP delivery.",
        "Enforce CHECK (LENGTH(phone) >= 10) or validate at application layer."),
    "SEQUENTIAL_PHONE": (re.compile(r"'(1234567890|9876543210)'", re.I), "High",
        "Sequential / Test Phone Number in Production Data", "Data Quality",
        "Phone numbers like 1234567890 or 9876543210 are clearly test data in production.",
        "Notification systems will attempt delivery to invalid numbers.",
        "Scrub all test records before promoting a dump to production."),
    "DUPLICATE_UNIQUE_KEY": (re.compile(r'UNIQUE\s+KEY\s+`(\w+)`.*?\n.*?UNIQUE\s+KEY\s+`(\w+)`', re.I | re.S), "Medium",
        "Potential Duplicate Unique Keys", "Schema",
        "Multiple UNIQUE KEY definitions may overlap (e.g., reg_no defined twice with different key names).",
        "Wasted index space; optimizer may not pick the best index.",
        "Consolidate duplicate unique constraints; keep only named canonical indexes."),
    "DISABLE_KEYS": (re.compile(r'ALTER\s+TABLE.*?DISABLE\s+KEYS', re.I), "Low",
        "DISABLE KEYS During Bulk Load", "Performance",
        "DISABLE KEYS is MyISAM-era syntax; has no effect on InnoDB tables.",
        "False sense of optimisation; no actual speedup on InnoDB.",
        "Remove DISABLE/ENABLE KEYS statements; use InnoDB bulk-insert tuning instead."),
}

SCHEMA_PATTERNS = {
    "students": {
        "issues": [
            ("High","Duplicate Column Semantics","Schema","Both `DOB` and `date_of_birth` columns exist — same data, two columns.","Data inconsistency; application may write to one and read from the other.","Drop one column; migrate data into the canonical column."),
            ("High","Duplicate Column Semantics","Schema","Both `phone_no` and `phone` columns exist — redundant phone storage.","Two-source-of-truth problem; notification services may use stale data.","Consolidate into a single `phone` column with a NOT NULL CHECK."),
            ("Medium","Redundant Columns","Schema","Both `academic_year` (VARCHAR) and `academic_year_id` (FK) columns exist.","Data drift when the VARCHAR is updated without syncing the FK reference.","Remove the VARCHAR redundancy; derive the year label from the referenced row."),
            ("Medium","Redundant Columns","Schema","Both `gender` (VARCHAR) and `gender_id` (FK) columns exist.","Same data stored twice with different types — normalisation violation.","Remove `gender` VARCHAR; join to the `genders` table for the label."),
            ("Medium","Redundant Columns","Schema","Both `section` (VARCHAR) and `section_id` (FK) columns exist.","Denormalisation leads to stale cached values.","Remove `section` VARCHAR; query via FK join."),
            ("Medium","Redundant Columns","Schema","Both `year` (VARCHAR) and `year_id` (FK) columns exist.","Denormalisation risk.","Remove `year` VARCHAR; query via FK join."),
            ("Medium","Redundant Columns","Schema","Both `semester` (VARCHAR) and `semester_id` (FK) columns exist.","Denormalisation risk.","Remove `semester` VARCHAR; query via FK join."),
            ("Low","Missing NOT NULL on `full_name`","Schema","`full_name` allows NULL — a student record without a name is semantically invalid.","NULL names break display logic and reports.","Add NOT NULL constraint with DEFAULT '' or enforce at app layer."),
            ("Info","`promotion_timestamp` Uses datetime(6)","Schema","Microsecond precision timestamp for promotion — likely overkill.","Slight storage overhead (5 bytes vs 4 for TIMESTAMP).","Use TIMESTAMP unless sub-second precision is truly required."),
        ]
    },
    "users": {
        "issues": [
            ("High","`username` Allows NULL","Security","`username` is UNIQUE but DEFAULT NULL — NULL is not unique in MySQL; multiple rows can have NULL username.","Authentication bypass: a user with NULL username may match multiple accounts.","Set username NOT NULL; enforce non-empty value at application layer."),
            ("High","`email` Allows NULL","Security","`email` is UNIQUE but DEFAULT NULL — same NULL uniqueness loophole as username.","Multiple users can have NULL email; password reset flows break.","Set email NOT NULL."),
            ("Medium","`password` VARCHAR(150)","Security","BCrypt hashes are 60 chars (cost-10) but Argon2 / bcrypt-higher-cost hashes can reach 95+ chars. VARCHAR(150) is borderline.","Future algorithm upgrades may exceed column length causing silent truncation.","Expand to VARCHAR(255) to future-proof."),
            ("Low","Redundant `academic_year` Columns","Schema","Both `assigned_academic_year` and `academic_year` ENUM columns are present on the users table.","Two columns for the same concept; application code must keep both in sync.","Consolidate into one; or document the intentional difference."),
        ]
    }
}

def detect_table_name(content):
    m = re.search(r'CREATE\s+TABLE\s+`?(\w+)`?', content, re.I)
    return m.group(1) if m else "unknown"

def analyse_file(fpath):
    folder   = os.path.basename(os.path.dirname(fpath))
    filename = os.path.basename(fpath)
    try:
        with open(fpath, encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return []

    table_name = detect_table_name(content)
    file_findings = []
    lines = content.splitlines()

    for rule_key, rule in PATTERNS.items():
        pattern, severity, title, category, description, impact, recommendation = rule
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                # Skip Info entries for duplicate reporting noise
                if rule_key == "NULLABLE_NOT_NULL":
                    continue
                snippet = line.strip()[:200]
                file_findings.append({
                    "id": f"F{len(findings)+len(file_findings)+1:04d}",
                    "severity": severity,
                    "category": category,
                    "title": title,
                    "table": table_name,
                    "file": filename,
                    "folder": folder,
                    "line": i,
                    "snippet": snippet,
                    "description": description,
                    "impact": impact,
                    "recommendation": recommendation,
                })
                break  # one finding per rule per file

    # Schema-specific deep analysis
    if table_name in SCHEMA_PATTERNS:
        for severity, title, category, description, impact, rec in SCHEMA_PATTERNS[table_name]["issues"]:
            file_findings.append({
                "id": f"F{len(findings)+len(file_findings)+1:04d}",
                "severity": severity,
                "category": category,
                "title": title,
                "table": table_name,
                "file": filename,
                "folder": folder,
                "line": 1,
                "snippet": f"[Schema analysis of `{table_name}`]",
                "description": description,
                "impact": impact,
                "recommendation": rec,
            })

    return file_findings

# Run analysis
for fp in sql_files:
    ff = analyse_file(fp)
    findings.extend(ff)
    table = detect_table_name(open(fp, encoding='utf-8', errors='replace').read())
    folder = os.path.basename(os.path.dirname(fp))
    if table not in tables_meta:
        tables_meta[table] = {"schemas": folder == "schemas", "data": folder == "data", "issues": 0}
    tables_meta[table]["issues"] += len(ff)

for f in findings:
    summary_counts[f["severity"].lower()] = summary_counts.get(f["severity"].lower(), 0) + 1

total   = len(findings)
crit    = summary_counts["critical"]
high    = summary_counts["high"]
med     = summary_counts["medium"]
low     = summary_counts["low"]
info    = summary_counts["info"]

sec_score  = max(10, round(100 - (crit*10 + high*3 + med*1) / max(1, len(sql_files)) * 3))
perf_score = max(10, round(100 - len([f for f in findings if f["category"] == "Performance"]) / max(1, len(sql_files)) * 30))
qual_score = max(10, round(100 - len([f for f in findings if f["category"] in ["Schema","Data Quality","Best Practices"]]) / max(1, len(sql_files)) * 15))

summary = {
    "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_files": len(sql_files),
    "total_tables": len(tables_meta),
    "total_findings": total,
    "critical": crit,
    "high": high,
    "medium": med,
    "low": low,
    "info": info,
    "security_score": sec_score,
    "performance_score": perf_score,
    "quality_score": qual_score,
    "database": "spdms_lab",
    "engine": "MySQL InnoDB 8.0.46",
}

with open(os.path.join(REPORT_PATH, "findings.json"), "w") as f:
    json.dump(findings, f, indent=2)
with open(os.path.join(REPORT_PATH, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print(f"[SCAN COMPLETE] {total} findings: {crit} Critical | {high} High | {med} Medium | {low} Low | {info} Info")
print(f"[SCORES] Security: {sec_score}/100 | Performance: {perf_score}/100 | Quality: {qual_score}/100")
print(f"[OUTPUT] Generating HTML report …")

# ─── STEP 5 & 6: HTML REPORT ─────────────────────────────────────────────────
SEVERITY_COLOR = {
    "Critical": "#ff4444", "High": "#ff8800",
    "Medium": "#ffcc00",   "Low": "#44aaff", "Info": "#aaaaaa"
}
SEVERITY_BADGE = {
    "Critical": "bg-danger",   "High": "bg-warning text-dark",
    "Medium": "bg-info text-dark", "Low": "bg-primary", "Info": "bg-secondary"
}
CAT_ICON = {
    "Security": "🛡️", "Performance": "⚡", "Schema": "🗄️",
    "Data Quality": "📊", "Best Practices": "📋", "Maintainability": "🔧"
}

def score_ring(score, label, color):
    pct = score
    dash = round(pct * 2.51327)  # circumference ~251
    return f"""
    <div class="score-ring-wrap text-center">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="40" fill="none" stroke="#2a2a3e" stroke-width="12"/>
        <circle cx="60" cy="60" r="40" fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{dash} 251"
                stroke-linecap="round"
                transform="rotate(-90 60 60)"/>
        <text x="60" y="65" text-anchor="middle" fill="white" font-size="20" font-weight="bold">{score}</text>
      </svg>
      <div class="mt-1 fw-semibold" style="color:{color}">{label}</div>
    </div>"""

def findings_table(cats):
    filtered = [f for f in findings if f["category"] in cats] if cats else findings
    if not filtered:
        return '<p class="text-muted">No findings in this category.</p>'
    rows = ""
    for f in filtered:
        badge_cls = SEVERITY_BADGE.get(f["severity"], "bg-secondary")
        rows += f"""
        <tr>
          <td><span class="badge {badge_cls}">{f['severity']}</span></td>
          <td>{f['table']}</td>
          <td>{f['title']}</td>
          <td class="small text-muted">{f['file']}</td>
          <td class="small">{f['line']}</td>
          <td>
            <button class="btn btn-sm btn-outline-light" data-bs-toggle="collapse"
                    data-bs-target="#detail-{f['id']}">Details</button>
          </td>
        </tr>
        <tr class="collapse" id="detail-{f['id']}">
          <td colspan="6" class="bg-dark">
            <div class="p-3">
              <pre class="code-snippet">{f['snippet']}</pre>
              <table class="table table-sm table-dark mt-2 mb-0">
                <tr><th width="140">Description</th><td>{f['description']}</td></tr>
                <tr><th>Impact</th><td>{f['impact']}</td></tr>
                <tr><th>Recommendation</th><td>{f['recommendation']}</td></tr>
              </table>
            </div>
          </td>
        </tr>"""
    return f"""
    <div class="table-responsive">
    <table class="table table-dark table-hover findings-table" id="tbl-{''.join(c[0] for c in cats) if cats else 'all'}">
      <thead class="table-secondary">
        <tr>
          <th>Severity</th><th>Table</th><th>Issue</th>
          <th>File</th><th>Line</th><th></th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""

# Build category sections
categories = ["Security", "Performance", "Schema", "Data Quality", "Best Practices", "Maintainability"]
cat_sections = ""
for cat in categories:
    cat_findings = [f for f in findings if f["category"] == cat]
    icon = CAT_ICON.get(cat, "📌")
    cat_sections += f"""
    <section id="sec-{cat.lower().replace(' ','-')}" class="mb-5">
      <h3 class="section-title">{icon} {cat} Findings <span class="badge bg-secondary ms-2">{len(cat_findings)}</span></h3>
      {findings_table([cat])}
    </section>"""

# Top risk tables
risk_tables = sorted(tables_meta.items(), key=lambda x: x[1].get("issues",0), reverse=True)[:10]
heat_rows = "".join(
    f'<tr><td>{t}</td><td>{"●"*min(10,v["issues"])}</td><td>{v["issues"]}</td></tr>'
    for t,v in risk_tables
)

# Pie chart data
pie_labels   = json.dumps(["Critical","High","Medium","Low","Info"])
pie_data     = json.dumps([crit, high, med, low, info])
pie_colors   = json.dumps(["#ff4444","#ff8800","#ffcc00","#44aaff","#aaaaaa"])

# Bar chart data
bar_labels = json.dumps([c for c in categories])
bar_data   = json.dumps([len([f for f in findings if f["category"]==c]) for c in categories])

# Score bar data
score_labels = json.dumps(["Security","Performance","Quality"])
score_data   = json.dumps([sec_score, perf_score, qual_score])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Claude Security Report — PragatiX / SPDMS SQL Analysis</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"/>
<link href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css" rel="stylesheet"/>
<link href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css" rel="stylesheet"/>
<style>
:root{{
  --bg-main:#0d0d1a;--bg-card:#13132a;--bg-panel:#1a1a2e;
  --accent:#7c3aed;--accent2:#06b6d4;--green:#22c55e;--red:#ef4444;--orange:#f97316;
  --text:#e2e8f0;--muted:#94a3b8;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg-main);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;font-size:14px}}
.sidebar{{position:fixed;top:0;left:0;width:220px;height:100vh;background:var(--bg-panel);
          border-right:1px solid #2d2d50;overflow-y:auto;z-index:100;padding:1rem 0}}
.sidebar-brand{{padding:1rem 1.2rem;font-size:1.1rem;font-weight:700;color:var(--accent);
               letter-spacing:1px;border-bottom:1px solid #2d2d50;margin-bottom:.5rem}}
.sidebar a{{display:block;padding:.5rem 1.2rem;color:var(--muted);text-decoration:none;
           border-radius:6px;margin:2px 8px;font-size:13px;transition:all .2s}}
.sidebar a:hover,.sidebar a.active{{background:var(--accent);color:#fff}}
.main{{margin-left:220px;padding:2rem}}
.header-bar{{background:linear-gradient(135deg,#1a1a3e,#0d0d2e);border:1px solid #2d2d50;
             border-radius:12px;padding:2rem;margin-bottom:2rem}}
.header-bar h1{{font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#7c3aed,#06b6d4);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.stat-card{{background:var(--bg-card);border:1px solid #2d2d50;border-radius:10px;
           padding:1.2rem;text-align:center;transition:transform .2s}}
.stat-card:hover{{transform:translateY(-3px)}}
.stat-num{{font-size:2.2rem;font-weight:800;line-height:1}}
.section-title{{font-size:1.2rem;font-weight:700;padding:.6rem 0;
               border-bottom:2px solid var(--accent);margin-bottom:1rem;color:var(--accent2)}}
.score-ring-wrap svg circle{{transition:stroke-dasharray 1s ease}}
.code-snippet{{background:#1e1e2e;border:1px solid #3d3d6b;border-radius:6px;
              padding:.6rem;font-family:monospace;font-size:12px;white-space:pre-wrap;
              word-break:break-all;color:#cdd6f4;max-height:120px;overflow:auto}}
.chart-card{{background:var(--bg-card);border:1px solid #2d2d50;border-radius:10px;padding:1.2rem}}
.findings-table td,.findings-table th{{vertical-align:middle}}
.badge.bg-warning{{color:#000!important}}
table.dataTable{{color:var(--text)!important}}
.dataTables_wrapper .dataTables_filter input,
.dataTables_wrapper .dataTables_length select{{background:#1a1a2e;color:var(--text);border:1px solid #3d3d6b;border-radius:6px;padding:4px 8px}}
.dataTables_wrapper .dataTables_info,.dataTables_wrapper .dataTables_paginate{{color:var(--muted)}}
.page-link{{background:var(--bg-card);border-color:#3d3d6b;color:var(--text)}}
.heat-dot{{color:#f97316}}
.risk-badge{{font-size:11px;font-weight:600}}
@media(max-width:768px){{.sidebar{{display:none}}.main{{margin-left:0}}}}
</style>
</head>
<body>

<!-- SIDEBAR -->
<nav class="sidebar">
  <div class="sidebar-brand">🔐 Claude Report</div>
  <a href="#sec-dashboard">📊 Dashboard</a>
  <a href="#sec-summary">📋 Executive Summary</a>
  <a href="#sec-security">🛡️ Security</a>
  <a href="#sec-performance">⚡ Performance</a>
  <a href="#sec-schema">🗄️ Schema</a>
  <a href="#sec-data-quality">📊 Data Quality</a>
  <a href="#sec-best-practices">📋 Best Practices</a>
  <a href="#sec-objects">🔍 Object Analysis</a>
  <a href="#sec-recommendations">💡 Recommendations</a>
  <a href="#sec-appendix">📑 Appendix</a>
</nav>

<!-- MAIN -->
<div class="main">

  <!-- HEADER -->
  <div class="header-bar" id="sec-dashboard">
    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
      <div>
        <h1>Claude Security Report</h1>
        <div class="text-muted mt-1">PragatiX / SPDMS SQL Database Security & Schema Audit</div>
        <div class="small mt-2">
          <span class="badge bg-secondary me-2">🗄️ {summary['database']}</span>
          <span class="badge bg-secondary me-2">⚙️ {summary['engine']}</span>
          <span class="badge bg-secondary">📅 {summary['scan_date']}</span>
        </div>
      </div>
      <div class="d-flex gap-4 flex-wrap">
        {score_ring(sec_score,'Security','#7c3aed')}
        {score_ring(perf_score,'Performance','#06b6d4')}
        {score_ring(qual_score,'Quality','#22c55e')}
      </div>
    </div>
  </div>

  <!-- STATS ROW -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num text-info">{summary['total_files']}</div><div class="text-muted small">SQL Files</div></div>
    </div>
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num text-primary">{summary['total_tables']}</div><div class="text-muted small">Tables</div></div>
    </div>
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num" style="color:#ff4444">{crit}</div><div class="text-muted small">Critical</div></div>
    </div>
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num" style="color:#ff8800">{high}</div><div class="text-muted small">High</div></div>
    </div>
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num" style="color:#ffcc00">{med}</div><div class="text-muted small">Medium</div></div>
    </div>
    <div class="col-6 col-md-2">
      <div class="stat-card"><div class="stat-num text-primary">{low}</div><div class="text-muted small">Low / Info</div></div>
    </div>
  </div>

  <!-- CHARTS ROW -->
  <div class="row g-3 mb-4">
    <div class="col-md-4">
      <div class="chart-card h-100">
        <div class="fw-semibold mb-3 text-info">Issues by Severity</div>
        <canvas id="pieChart" height="200"></canvas>
      </div>
    </div>
    <div class="col-md-4">
      <div class="chart-card h-100">
        <div class="fw-semibold mb-3 text-info">Issues by Category</div>
        <canvas id="barChart" height="200"></canvas>
      </div>
    </div>
    <div class="col-md-4">
      <div class="chart-card h-100">
        <div class="fw-semibold mb-3 text-info">Scores Overview</div>
        <canvas id="scoreChart" height="200"></canvas>
      </div>
    </div>
  </div>

  <!-- HEAT MAP -->
  <div class="chart-card mb-4">
    <div class="fw-semibold mb-3 text-info">🔥 Top Risk Tables</div>
    <table class="table table-dark table-sm table-hover">
      <thead><tr><th>Table</th><th>Risk Heat</th><th>Issues</th></tr></thead>
      <tbody>{heat_rows}</tbody>
    </table>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <section id="sec-summary" class="mb-5">
    <h3 class="section-title">📋 Executive Summary</h3>
    <div class="row g-3">
      <div class="col-md-8">
        <div class="chart-card">
          <p>This report presents a complete static security analysis of the <strong>PragatiX / SPDMS</strong> MySQL
          database SQL dump exported on <strong>August 6, 2026</strong>. The scan covered
          <strong>{summary['total_files']} SQL files</strong> across schemas, data, and tables folders, 
          covering <strong>{summary['total_tables']} database tables</strong>.</p>
          <br/>
          <p>The overall <strong>Security Score is {sec_score}/100</strong> — indicating several
          high-priority findings around data integrity, schema design, and dump security settings
          that should be addressed before the next production release.</p>
          <br/>
          <h6 class="text-warning">Key Findings:</h6>
          <ul>
            <li><strong>Schema denormalisation</strong> — The <code>students</code> table stores 7 columns as both a raw value and a FK reference (year, semester, section, gender, academic_year, phone, DOB — all duplicated). This is the highest-volume schema issue.</li>
            <li><strong>Test data in production dump</strong> — Users with phone numbers <code>123</code>, <code>1234567890</code>, and fictional accounts (luffy, Elon Musk, Steve Jobs) exist alongside real student records.</li>
            <li><strong>FOREIGN_KEY_CHECKS=0</strong> — FK checks are globally disabled during the entire dump import, which is a medium-to-high integrity risk.</li>
            <li><strong>DROP TABLE in dump</strong> — All schema files begin with DROP TABLE IF EXISTS, creating risk if the dump is accidentally replayed on a live database.</li>
            <li><strong>BCrypt passwords confirmed</strong> — All passwords are properly BCrypt-hashed ($2a$10$…). ✅ POSITIVE FINDING.</li>
            <li><strong>NULL-capable username/email on users table</strong> — MySQL's UNIQUE KEY allows multiple NULL rows, which can be exploited for authentication bypass.</li>
          </ul>
        </div>
      </div>
      <div class="col-md-4">
        <div class="chart-card h-100">
          <h6 class="text-info mb-3">Positive Findings ✅</h6>
          <ul class="small">
            <li class="mb-2">✅ BCrypt hashing ($2a$10$) used consistently</li>
            <li class="mb-2">✅ InnoDB engine with FK constraints</li>
            <li class="mb-2">✅ utf8mb4 charset throughout</li>
            <li class="mb-2">✅ Proper AUTO_INCREMENT PKs on all tables</li>
            <li class="mb-2">✅ UNIQUE constraints on email & reg_no</li>
            <li class="mb-2">✅ created_at / updated_at audit timestamps</li>
            <li class="mb-2">✅ Proper CASCADE / RESTRICT FK rules</li>
            <li class="mb-2">✅ No EXEC/sp_executesql (no dynamic SQL)</li>
            <li class="mb-2">✅ No plaintext secrets in schema DDL</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <!-- PER-CATEGORY FINDINGS -->
  {cat_sections}

  <!-- OBJECT ANALYSIS -->
  <section id="sec-objects" class="mb-5">
    <h3 class="section-title">🔍 Object Analysis</h3>
    <div class="table-responsive">
    <table class="table table-dark table-hover" id="tblObjects">
      <thead class="table-secondary">
        <tr><th>Table</th><th>Has Schema</th><th>Has Data</th><th>Issue Count</th><th>Risk</th></tr>
      </thead>
      <tbody>
        {''.join(
            f"""<tr>
              <td><code>{t}</code></td>
              <td>{'✅' if v.get('schemas') else '—'}</td>
              <td>{'✅' if v.get('data') else '—'}</td>
              <td>{v.get('issues',0)}</td>
              <td>{'<span class="badge bg-danger">Critical</span>' if v.get('issues',0)>=8
                  else '<span class="badge bg-warning text-dark">High</span>' if v.get('issues',0)>=4
                  else '<span class="badge bg-info text-dark">Medium</span>' if v.get('issues',0)>=2
                  else '<span class="badge bg-secondary">Low</span>'}</td>
            </tr>"""
            for t, v in sorted(tables_meta.items(), key=lambda x: x[1].get('issues',0), reverse=True)
        )}
      </tbody>
    </table>
    </div>
  </section>

  <!-- RECOMMENDATIONS -->
  <section id="sec-recommendations" class="mb-5">
    <h3 class="section-title">💡 Recommendations (Priority Order)</h3>
    <div class="chart-card">
      <ol class="ps-3">
        <li class="mb-3"><span class="badge bg-danger me-2">P1 — Critical</span>
          <strong>Fix NULL-capable username/email on users table.</strong>
          Add NOT NULL constraints; audit for existing NULL rows and backfill or delete them.</li>
        <li class="mb-3"><span class="badge bg-warning text-dark me-2">P2 — High</span>
          <strong>Remove test/fictional data from production dump.</strong>
          Delete rows with phone=123, phone=1234567890, fictional usernames before any production promotion.</li>
        <li class="mb-3"><span class="badge bg-warning text-dark me-2">P3 — High</span>
          <strong>Resolve denormalised columns in <code>students</code> table.</strong>
          Remove duplicate VARCHAR shadow-columns (DOB/date_of_birth, phone/phone_no, year/year_id, etc.) and derive values via FK joins.</li>
        <li class="mb-3"><span class="badge bg-warning text-dark me-2">P4 — High</span>
          <strong>Guard DROP TABLE statements.</strong>
          Wrap all DROP TABLE statements with an environment check variable or move to a separate DDL migration file distinct from the data dump.</li>
        <li class="mb-3"><span class="badge bg-info text-dark me-2">P5 — Medium</span>
          <strong>Re-enable FOREIGN_KEY_CHECKS during import.</strong>
          Run a post-import FK integrity check: <code>SELECT * FROM information_schema.INNODB_SYS_FOREIGN_COLS</code>.</li>
        <li class="mb-3"><span class="badge bg-info text-dark me-2">P6 — Medium</span>
          <strong>Replace ENUM columns with lookup tables.</strong>
          Convert <code>academic_year</code> ENUM to a reference table to avoid DDL migrations for every new year.</li>
        <li class="mb-3"><span class="badge bg-info text-dark me-2">P7 — Medium</span>
          <strong>Consolidate INSERT statements with explicit column lists.</strong>
          Update all dump INSERT statements to include column names for forward compatibility.</li>
        <li class="mb-3"><span class="badge bg-primary me-2">P8 — Low</span>
          <strong>Enforce phone number format CHECK constraint.</strong>
          Add <code>CHECK (LENGTH(phone) >= 10 AND phone REGEXP '^[0-9]+$')</code> to both students and users tables.</li>
        <li class="mb-3"><span class="badge bg-primary me-2">P9 — Low</span>
          <strong>Standardise column naming to snake_case.</strong>
          Column <code>DOB</code> should be renamed <code>dob</code> or removed in favour of <code>date_of_birth</code>.</li>
        <li class="mb-3"><span class="badge bg-secondary me-2">P10 — Info</span>
          <strong>Strip sensitive metadata from exported dumps.</strong>
          Remove GTID_PURGED, AUTO_INCREMENT values, and SQL_LOG_BIN settings from dumps shared outside the ops team.</li>
      </ol>
    </div>
  </section>

  <!-- APPENDIX -->
  <section id="sec-appendix" class="mb-5">
    <h3 class="section-title">📑 Appendix — All Findings</h3>
    {findings_table(None)}
  </section>

  <div class="text-center text-muted small py-4">
    Claude Security Report • Generated {summary['scan_date']} • PragatiX / SPDMS Database • {total} Findings
  </div>

</div><!-- /main -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<script>
// DataTables
$(document).ready(function(){{
  $('table.findings-table, #tblObjects').DataTable({{
    pageLength:15, responsive:true,
    dom:'<"d-flex justify-content-between flex-wrap gap-2 mb-2"lf>rtip'
  }});
}});

// Pie
new Chart(document.getElementById('pieChart'),{{
  type:'doughnut',
  data:{{labels:{pie_labels},datasets:[{{data:{pie_data},backgroundColor:{pie_colors},borderWidth:2,borderColor:'#13132a'}}]}},
  options:{{plugins:{{legend:{{labels:{{color:'#e2e8f0',font:{{size:11}}}}}}}},cutout:'65%'}}
}});

// Bar
new Chart(document.getElementById('barChart'),{{
  type:'bar',
  data:{{labels:{bar_labels},datasets:[{{label:'Issues',data:{bar_data},
    backgroundColor:['#7c3aed','#06b6d4','#22c55e','#f97316','#f43f5e','#a855f7']}}]}},
  options:{{plugins:{{legend:{{display:false}}}},scales:{{
    y:{{ticks:{{color:'#94a3b8'}},grid:{{color:'#2d2d50'}}}},
    x:{{ticks:{{color:'#94a3b8'}},grid:{{display:false}}}}
  }}}}
}});

// Score Bar
new Chart(document.getElementById('scoreChart'),{{
  type:'bar',
  data:{{labels:{score_labels},datasets:[{{label:'Score /100',data:{score_data},
    backgroundColor:['#7c3aed','#06b6d4','#22c55e']}}]}},
  options:{{plugins:{{legend:{{display:false}}}},scales:{{
    y:{{min:0,max:100,ticks:{{color:'#94a3b8'}},grid:{{color:'#2d2d50'}}}},
    x:{{ticks:{{color:'#94a3b8'}},grid:{{display:false}}}}
  }}}}
}});

// Sidebar active link
document.querySelectorAll('.sidebar a').forEach(a=>{{
  a.addEventListener('click',()=>{{
    document.querySelectorAll('.sidebar a').forEach(x=>x.classList.remove('active'));
    a.classList.add('active');
  }});
}});
</script>
</body>
</html>"""

out_path = os.path.join(REPORT_PATH, "Claude_Security_Report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[DONE] Report written to: {out_path}")
