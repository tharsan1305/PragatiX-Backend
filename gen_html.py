import os

path = r'N:\pragatiX\PragatiX-Backend\PragatiX-Security.html'
if os.path.exists(path):
    os.remove(path)

CSS = r''':root{--critical:#c0392b;--critical-bg:#fadbd8;--high:#e67e22;--high-bg:#fdebd0;--medium:#f1c40f;--medium-bg:#fef9e7;--low:#2980b9;--low-bg:#d6eaf8;--bg:#f8f9fa;--card-bg:#fff;--text:#2c3e50;--muted:#7f8c8d}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.container{max-width:1200px;margin:0 auto;padding:20px}
h1{font-size:2em;margin-bottom:4px}
h2{font-size:1.5em;margin:32px 0 12px;border-bottom:2px solid #ddd;padding-bottom:6px}
h3{font-size:1.2em;margin:24px 0 8px}
h4{font-size:1em;margin:16px 0 6px}
.subtitle{color:var(--muted);font-size:0.95em;margin-bottom:24px}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}
.summary-card{background:var(--card-bg);border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08);text-align:center}
.summary-card .num{font-size:2.4em;font-weight:700}
.summary-card .label{font-size:0.85em;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.78em;font-weight:700;color:#fff}
.badge-critical{background:var(--critical)}.badge-high{background:var(--high)}.badge-medium{background:var(--medium);color:#333}.badge-low{background:var(--low)}.badge-clean{background:#27ae60}
table{width:100%;border-collapse:collapse;background:var(--card-bg);border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:16px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #eee;font-size:0.92em;vertical-align:top}
th{background:#f1f3f5;font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:none}
code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-size:0.9em;word-break:break-all}
pre{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto;font-size:0.88em;margin:8px 0}
pre code{background:none;padding:0}
.toc{background:var(--card-bg);border-radius:8px;padding:16px 24px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:24px}
.toc a{color:var(--low);text-decoration:none}
.toc a:hover{text-decoration:underline}
.toc li{margin:4px 0}
.file-section{margin-bottom:48px;padding:20px 24px;background:var(--card-bg);border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.file-section h2{margin-top:0;border-bottom:3px solid #ddd}
.finding-row td:first-child{white-space:nowrap;width:90px}
.finding-row td:nth-child(2){width:180px;font-family:monospace;font-size:0.88em}
.priority{background:var(--critical-bg);border-left:4px solid var(--critical);padding:12px 16px;margin:8px 0;border-radius:0 6px 6px 0}
.priority ol{padding-left:20px}
.priority li{margin:6px 0}
.health-score{font-size:3em;font-weight:700;color:var(--critical)}
.health-label{font-size:0.9em;color:var(--muted)}
.extras{background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:16px 20px;margin:24px 0}
.extras h3{margin-top:0;color:#856404}
@media print{body{font-size:11px}.container{max-width:100%}}'''

def badge(sev):
    return f'<span class="badge badge-{sev.lower()}">{sev}</span>'

def tr(sev, loc, issue, why, fix):
    return f'<tr class="finding-row"><td>{badge(sev)}</td><td><code>{loc}</code></td><td>{issue}</td><td>{why}</td><td><pre>{fix}</pre></td></tr>'

def section(title, purpose, tables, findings_html, checks):
    return f'''<div class="file-section">
<h2>{title}</h2>
<p><strong>Purpose:</strong> {purpose}</p>
<p><strong>Tables/objects:</strong> {tables}</p>
{findings_html}
<h4>Table Checks</h4>
<p>{checks}</p>
</div>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>PragatiX Migration Security Audit</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="container">
<h1>PragatiX &mdash; Migration Security &amp; Schema Audit</h1>
<p class="subtitle"><strong>Scope:</strong> <code>N:\\pragatiX\\PragatiX-Backend\\migration\\</code> &mdash; V1 through V19 (19 files)<br>
<strong>Platform declared:</strong> MySQL 8.0+ &nbsp;|&nbsp; <strong>Actual runtime:</strong> Hibernate <code>ddl-auto: update</code> (no Flyway configured)<br>
<strong>Audit date:</strong> 2026-08-05</p>

<h2>Summary</h2>
<div class="summary-grid">
<div class="summary-card"><div class="num">45</div><div class="label">Tables Scanned</div></div>
<div class="summary-card"><div class="num" style="color:var(--critical)">10</div><div class="label">CRITICAL</div></div>
<div class="summary-card"><div class="num" style="color:var(--high)">9</div><div class="label">HIGH</div></div>
<div class="summary-card"><div class="num" style="color:var(--medium)">22</div><div class="label">MEDIUM</div></div>
<div class="summary-card"><div class="num" style="color:var(--low)">17</div><div class="label">LOW</div></div>
<div class="summary-card"><div class="num">58</div><div class="label">Total Findings</div></div>
<div class="summary-card"><div class="health-score">12</div><div class="health-label">Health Score / 100<br><small>Formula: 100 &minus; (4&times;CRITICAL + 2&times;HIGH + 1&times;MEDIUM + 0.5&times;LOW), floored at 0</small></div></div>
</div>

<div class="extras">
<h3>Beyond the migrations &mdash; application config findings</h3>
<table>
<tr><th>Severity</th><th>File</th><th>Issue</th><th>Why it matters</th><th>Fix</th></tr>
<tr><td>{badge("CRITICAL")}</td><td><code>application.yml</code></td><td>MySQL root password <code>sharu</code> committed in source control</td><td>Full DB credentials exposed in every repo clone / CI log</td><td>Remove; inject via <code>$&#123;DB_PASSWORD&#125;</code> env var; rotate the password</td></tr>
<tr><td>{badge("CRITICAL")}</td><td><code>application.yml</code></td><td>Spring Security default user <code>admin</code>/<code>admin</code></td><td>Well-known default credential on every environment</td><td>Remove; provision real admin via secure bootstrap</td></tr>
<tr><td>{badge("CRITICAL")}</td><td><code>application.yml</code></td><td>Hardcoded JWT secret <code>spdms_super_secret_key&hellip;</code></td><td>Static, publicly-known signing key &rarr; anyone can forge JWTs and impersonate any user</td><td>Move to <code>JWT_SECRET</code> env var; rotate immediately</td></tr>
<tr><td>{badge("CRITICAL")}</td><td><code>application.properties</code></td><td>Twilio account SID + auth token committed in plaintext</td><td>SMS gateway compromise &rarr; spam abuse, billing damage</td><td>Revoke token in Twilio console; move to secrets manager</td></tr>
<tr><td>{badge("CRITICAL")}</td><td><code>application.yml</code></td><td><code>ddl-auto: update</code> and <strong>no Flyway/Liquibase dependency</strong> in <code>pom.xml</code></td><td>The <code>migration/</code> folder is never executed by the app; schema is whatever Hibernate last created</td><td>Add Flyway dependency, configure <code>spring.flyway.*</code>, set <code>ddl-auto: validate</code></td></tr>
<tr><td>{badge("HIGH")}</td><td>migrations &harr; entities</td><td>JPA entities require columns/tables the migrations never create (<code>activity_name</code>, <code>section_id</code>, <code>user_id</code>, <code>gender_id</code>, <code>year_id</code>, <code>semester_id</code>, <code>attendance_settings</code>, <code>activity_assignments</code>)</td><td>App and schema are out of sync; a migration-only build produces an unusable schema</td><td>Make the migration set authoritative and reconcile entities to it</td></tr>
</table>
</div>

<h2>Table of Contents</h2>
<div class="toc">
<ol>
<li><a href="#v1">V1__init.sql</a> &mdash; Initial schema (37 tables, UUID PKs, triggers)</li>
<li><a href="#v2">V2__production_upgrade.sql</a> &mdash; UUID&rarr;BIGINT conversion, new tables, admin seed</li>
<li><a href="#v3">V3</a> &mdash; Make student section nullable</li>
<li><a href="#v4">V4</a> &mdash; Make student user nullable</li>
<li><a href="#v5">V5</a> &mdash; Set student password NOT NULL</li>
<li><a href="#v6">V6</a> &mdash; Add activity stage fields</li>
<li><a href="#v7">V7</a> &mdash; Default activities XP category</li>
<li><a href="#v8">V8</a> &mdash; Add activity event fields</li>
<li><a href="#v9">V9</a> &mdash; Update activity rules fields</li>
<li><a href="#v10">V10</a> &mdash; Award rules refactor</li>
<li><a href="#v11">V11</a> &mdash; Add assignment mode</li>
<li><a href="#v12">V12</a> &mdash; Fix activities subgroup column</li>
<li><a href="#v13">V13</a> &mdash; Fix activity unique constraint</li>
<li><a href="#v14">V14</a> &mdash; Remove assigned academic year</li>
<li><a href="#v15">V15</a> &mdash; Drop legacy subgroup column</li>
<li><a href="#v16">V16</a> &mdash; Create activity stage mapping table</li>
<li><a href="#v17">V17</a> &mdash; Add stage ID and overrides</li>
<li><a href="#v18">V18</a> &mdash; Update attendance settings dates</li>
<li><a href="#v19">V19</a> &mdash; Drop attendance dates</li>
</ol>
</div>
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Part 1:', os.path.getsize(path), 'bytes')
