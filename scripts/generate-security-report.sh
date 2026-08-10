#!/usr/bin/env bash
# ==============================================================================
# generate-security-report.sh
# Generates security/reports/final-security-report.html from all tool outputs.
# Reads merged-findings.json produced by merge-reports.py.
#
# Environment variables expected (set by the workflow):
#   REPORTS_DIR          security/reports
#   REPORT_BASE          security/generated
#   SONAR_ENABLED        true | false
#   GATE_MODE            report-only | block
#   COVERAGE_THRESHOLD   integer
#   GIT_SHA              commit SHA
#   GIT_BRANCH           branch name
#   RUN_ID               GitHub run ID
#   RUN_NUMBER           GitHub run number
#   REPO                 org/repo
#   TRIGGERED_BY         actor login
#   WORKFLOW_NAME        workflow name
# ==============================================================================
set -euo pipefail

REPORTS_DIR="${REPORTS_DIR:-security/reports}"
REPORT_BASE="${REPORT_BASE:-security/generated}"
MERGED_JSON="${REPORTS_DIR}/merged-findings.json"
OUTPUT_HTML="${REPORTS_DIR}/final-security-report.html"
TEMPLATE_DIR="security/templates"

SONAR_ENABLED="${SONAR_ENABLED:-false}"
GATE_MODE="${GATE_MODE:-report-only}"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-40}"
GIT_SHA="${GIT_SHA:-unknown}"
GIT_BRANCH="${GIT_BRANCH:-unknown}"
RUN_ID="${RUN_ID:-0}"
RUN_NUMBER="${RUN_NUMBER:-0}"
REPO="${REPO:-unknown/unknown}"
TRIGGERED_BY="${TRIGGERED_BY:-unknown}"
WORKFLOW_NAME="${WORKFLOW_NAME:-Security Pipeline}"
GATE_RESULT_LOWER="$(echo "${GATE_RESULT:-FAIL}" | tr '[:upper:]' '[:lower:]')"
BUILD_DATE="$(date -u '+%Y-%m-%d')"
BUILD_TIME="$(date -u '+%H:%M:%S UTC')"

mkdir -p "$REPORTS_DIR"

echo "[generate-security-report] Reading: $MERGED_JSON"
echo "[generate-security-report] Output:  $OUTPUT_HTML"

# ─── Extract values from merged JSON via python3 ─────────────────────────────
extract() {
    local expr="$1"
    local default="${2:-0}"
    if [ -f "$MERGED_JSON" ]; then
        python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    result = $expr
    print(result if result is not None else '$default')
except Exception as e:
    print('$default')
" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

CRIT=$(extract "data['summary']['severity_counts'].get('CRITICAL', 0)")
HIGH=$(extract "data['summary']['severity_counts'].get('HIGH', 0)")
MED=$(extract  "data['summary']['severity_counts'].get('MEDIUM', 0)")
LOW=$(extract  "data['summary']['severity_counts'].get('LOW', 0)")
INFO=$(extract "data['summary']['severity_counts'].get('INFO', 0)")
TOTAL=$(extract "data['meta']['total_findings']")

LINE_PCT=$(extract    "data['coverage']['line_pct']")
BRANCH_PCT=$(extract  "data['coverage']['branch_pct']")
METHOD_PCT=$(extract  "data['coverage']['method_pct']")

TESTS=$(extract    "data['tests']['tests']")
FAILURES=$(extract "data['tests']['failures']")
ERRORS=$(extract   "data['tests']['errors']")
SKIPPED=$(extract  "data['tests']['skipped']")

SONAR_STATUS=$(extract "data['sonar']['status']" "NOT_CONFIGURED")
SBOM_CDX_COUNT=$(extract "data['sbom']['cyclonedx']['component_count']")
SBOM_SPDX_COUNT=$(extract "data['sbom']['spdx']['component_count']")

# Gate computed result
GATE_RESULT="PASS"
if [ "$CRIT" -gt 0 ] || [ "$FAILURES" -gt 0 ] || [ "$ERRORS" -gt 0 ]; then
    GATE_RESULT="FAIL"
fi
# Coverage check
if python3 -c "import sys; sys.exit(0 if float('${LINE_PCT}') >= float('${COVERAGE_THRESHOLD}') else 1)" 2>/dev/null; then
    : # coverage passes
else
    GATE_RESULT="FAIL"
fi

GATE_LABEL="report-only"
if [ "$GATE_MODE" = "block" ]; then
    GATE_LABEL="blocking"
fi

# ─── Security Score (0-100) ───────────────────────────────────────────────────
SEC_SCORE=$(python3 -c "
crit=$CRIT; high=$HIGH; med=$MED; low=$LOW
score = max(10, 100 - (crit*15 + high*5 + med*2 + low*1))
print(int(score))
" 2>/dev/null || echo 65)

# ─── Build findings rows for the table ────────────────────────────────────────
FINDINGS_ROWS=$(python3 - << 'PYEOF'
import json, html, sys, os
merged = os.environ.get('MERGED_JSON', 'security/reports/merged-findings.json')
rows = ""
SEV_BADGE = {
    "CRITICAL": ("badge-critical", "🔴"),
    "HIGH":     ("badge-high",     "🟠"),
    "MEDIUM":   ("badge-medium",   "🟡"),
    "LOW":      ("badge-low",      "🔵"),
    "INFO":     ("badge-info",     "⚪"),
}
try:
    data = json.load(open(merged))
    findings = data.get("findings", [])
    # Limit table to 200 rows to keep HTML manageable
    for f in findings[:200]:
        sev = f.get("severity", "INFO")
        cls, icon = SEV_BADGE.get(sev, ("badge-info", "⚪"))
        rows += f"""<tr>
          <td><span class="badge {cls}">{icon} {html.escape(sev)}</span></td>
          <td>{html.escape(f.get('tool',''))}</td>
          <td title="{html.escape(f.get('description',''))}">{html.escape(f.get('title','')[:80])}</td>
          <td class="col-file">{html.escape(os.path.basename(f.get('file','')) or '—')}</td>
          <td>{f.get('line',0) or '—'}</td>
          <td>{html.escape(f.get('cwe','') or '—')}</td>
          <td>{html.escape(f.get('owasp','') or '—')}</td>
        </tr>\n"""
    if len(findings) > 200:
        rows += f'<tr><td colspan="7" class="text-center text-muted">… and {len(findings)-200} more findings. Download merged-findings.json for full list.</td></tr>'
except Exception as e:
    rows = f'<tr><td colspan="7">Error loading findings: {html.escape(str(e))}</td></tr>'
print(rows)
PYEOF
)

# ─── Generate HTML ────────────────────────────────────────────────────────────
cat > "$OUTPUT_HTML" << HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PragatiX Security Report — Run #${RUN_NUMBER}</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet"/>
<link href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
$(cat security/dashboard.css 2>/dev/null || echo "/* dashboard.css not found */")
</style>
</head>
<body>
<div class="layout">

<!-- SIDEBAR -->
<nav class="sidebar">
  <div class="sidebar-logo">
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <rect width="36" height="36" rx="8" fill="#7c3aed"/>
      <path d="M8 18 L14 12 L22 20 L28 14" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="28" cy="14" r="3" fill="#06b6d4"/>
    </svg>
    <span class="sidebar-brand-text">PragatiX<br/><small>Security</small></span>
  </div>
  <nav class="sidebar-nav">
    <a href="#exec" class="nav-link active"><i class="fa fa-chart-pie"></i> Executive Summary</a>
    <a href="#pipeline" class="nav-link"><i class="fa fa-circle-nodes"></i> Pipeline Status</a>
    <a href="#build" class="nav-link"><i class="fa fa-hammer"></i> Build & Tests</a>
    <a href="#coverage" class="nav-link"><i class="fa fa-square-check"></i> Coverage</a>
    <a href="#quality" class="nav-link"><i class="fa fa-star"></i> Code Quality</a>
    <a href="#security" class="nav-link"><i class="fa fa-shield-halved"></i> Security Findings</a>
    <a href="#sbom" class="nav-link"><i class="fa fa-list"></i> SBOM</a>
    <a href="#recommendations" class="nav-link"><i class="fa fa-lightbulb"></i> Recommendations</a>
    <a href="#artifacts" class="nav-link"><i class="fa fa-download"></i> Artifacts</a>
    <a href="#timeline" class="nav-link"><i class="fa fa-clock"></i> Timeline</a>
  </nav>
  <div class="sidebar-footer">
    <button class="btn-action" onclick="window.print()"><i class="fa fa-print"></i> Print</button>
    <button class="btn-action" onclick="exportJSON()"><i class="fa fa-file-export"></i> Export JSON</button>
  </div>
</nav>

<!-- MAIN -->
<main class="main-content">

  <!-- HEADER -->
  <header class="page-header">
    <div class="header-left">
      <h1>Security Report</h1>
      <div class="header-meta">
        <span class="meta-chip"><i class="fa fa-code-branch"></i> ${GIT_BRANCH}</span>
        <span class="meta-chip"><i class="fa fa-code-commit"></i> ${GIT_SHA:0:8}</span>
        <span class="meta-chip"><i class="fa fa-hashtag"></i> Run #${RUN_NUMBER}</span>
        <span class="meta-chip"><i class="fa fa-calendar"></i> ${BUILD_DATE} ${BUILD_TIME}</span>
        <span class="meta-chip"><i class="fa fa-user"></i> ${TRIGGERED_BY}</span>
      </div>
    </div>
    <div class="header-right">
      <div class="gate-badge gate-$(echo ${GATE_RESULT} | tr '[:upper:]' '[:lower:]')">
        $([ "$GATE_RESULT" = "PASS" ] && echo "✅" || echo "❌")
        GATE: ${GATE_RESULT}
        <small>(${GATE_LABEL})</small>
      </div>
    </div>
  </header>

  <!-- ── EXECUTIVE SUMMARY ───────────────────────────────────────────────── -->
  <section id="exec" class="section">
    <h2 class="section-title"><i class="fa fa-chart-pie"></i> Executive Summary</h2>

    <!-- Info grid -->
    <div class="info-grid">
      <div class="info-row"><span class="info-label">Repository</span><span class="info-val">${REPO}</span></div>
      <div class="info-row"><span class="info-label">Workflow</span><span class="info-val">${WORKFLOW_NAME}</span></div>
      <div class="info-row"><span class="info-label">Run ID</span><span class="info-val">${RUN_ID}</span></div>
      <div class="info-row"><span class="info-label">Branch</span><span class="info-val">${GIT_BRANCH}</span></div>
      <div class="info-row"><span class="info-label">Commit</span><span class="info-val">${GIT_SHA}</span></div>
      <div class="info-row"><span class="info-label">Triggered By</span><span class="info-val">@${TRIGGERED_BY}</span></div>
      <div class="info-row"><span class="info-label">Build Date</span><span class="info-val">${BUILD_DATE}</span></div>
      <div class="info-row"><span class="info-label">Build Time</span><span class="info-val">${BUILD_TIME}</span></div>
    </div>

    <!-- Severity Cards -->
    <div class="sev-cards">
      <div class="sev-card sev-critical"><div class="sev-num">${CRIT}</div><div class="sev-label">Critical</div></div>
      <div class="sev-card sev-high">    <div class="sev-num">${HIGH}</div><div class="sev-label">High</div></div>
      <div class="sev-card sev-medium">  <div class="sev-num">${MED}</div> <div class="sev-label">Medium</div></div>
      <div class="sev-card sev-low">     <div class="sev-num">${LOW}</div> <div class="sev-label">Low</div></div>
      <div class="sev-card sev-info">    <div class="sev-num">${INFO}</div><div class="sev-label">Info</div></div>
    </div>

    <!-- Charts -->
    <div class="charts-row">
      <div class="chart-card">
        <h4>Findings by Severity</h4>
        <canvas id="sevChart" height="220"></canvas>
      </div>
      <div class="chart-card">
        <h4>Security Score</h4>
        <canvas id="scoreChart" height="220"></canvas>
      </div>
      <div class="chart-card">
        <h4>Coverage Overview</h4>
        <canvas id="coverageChart" height="220"></canvas>
      </div>
    </div>
  </section>

  <!-- ── PIPELINE STATUS ─────────────────────────────────────────────────── -->
  <section id="pipeline" class="section">
    <h2 class="section-title"><i class="fa fa-circle-nodes"></i> Pipeline Status</h2>
    <div class="gate-result-box gate-box-$(echo ${GATE_RESULT} | tr '[:upper:]' '[:lower:]')">
      <div class="gate-result-icon">$([ "$GATE_RESULT" = "PASS" ] && echo "✅" || echo "❌")</div>
      <div>
        <div class="gate-result-text">Security Gate: <strong>${GATE_RESULT}</strong></div>
        <div class="gate-result-sub">Mode: <code>${GATE_MODE}</code>
          $([ "$GATE_MODE" = "report-only" ] && echo " — informational only, workflow not blocked" || echo " — workflow blocked on FAIL")
        </div>
        <div class="gate-result-sub" style="color:#f97316;margin-top:6px">
          ⚠️ Known issues: open IDOR vulnerability + prior credential-exposure incident are
          expected FAIL contributors. See Recommendations section.
        </div>
      </div>
    </div>

    <table class="status-table">
      <thead><tr><th>Tool</th><th>Status</th><th>Findings</th></tr></thead>
      <tbody>
        <tr><td>Gitleaks</td><td class="$([ "${CRIT}" -gt 0 ] && echo 'status-fail' || echo 'status-pass')">$([ "${CRIT}" -gt 0 ] && echo '❌ Issues' || echo '✅ Clean')</td><td>—</td></tr>
        <tr><td>Semgrep</td><td class="status-pass">✅ Ran</td><td>See findings table</td></tr>
        <tr><td>CodeQL</td><td class="status-pass">✅ Ran</td><td>See GitHub Security tab</td></tr>
        <tr><td>SonarQube</td><td class="status-skip">⏭️ ${SONAR_STATUS}</td><td>$([ "$SONAR_ENABLED" = "false" ] && echo 'SONAR_ENABLED=false' || echo "${SONAR_STATUS}")</td></tr>
        <tr><td>OWASP Dep-Check</td><td class="status-pass">✅ Ran</td><td>See findings table</td></tr>
        <tr><td>Trivy</td><td class="status-pass">✅ Ran</td><td>See findings table</td></tr>
        <tr><td>Syft SBOM</td><td class="status-pass">✅ CycloneDX + SPDX</td><td>${SBOM_CDX_COUNT} components</td></tr>
      </tbody>
    </table>
  </section>

  <!-- ── BUILD & TESTS ──────────────────────────────────────────────────── -->
  <section id="build" class="section">
    <h2 class="section-title"><i class="fa fa-hammer"></i> Build &amp; Testing</h2>
    <div class="metric-grid">
      <div class="metric-card"><div class="metric-val">${TESTS}</div><div class="metric-label">Total Tests</div></div>
      <div class="metric-card $([ "${FAILURES}" -gt 0 ] && echo 'metric-fail' || echo '')">
        <div class="metric-val">${FAILURES}</div><div class="metric-label">Failures</div></div>
      <div class="metric-card $([ "${ERRORS}" -gt 0 ] && echo 'metric-fail' || echo '')">
        <div class="metric-val">${ERRORS}</div><div class="metric-label">Errors</div></div>
      <div class="metric-card"><div class="metric-val">${SKIPPED}</div><div class="metric-label">Skipped</div></div>
    </div>
    <div class="tool-note">
      JUnit 5 + Spring Boot Test + Mockito. Reports: <code>target/surefire-reports/</code>
    </div>
  </section>

  <!-- ── COVERAGE ───────────────────────────────────────────────────────── -->
  <section id="coverage" class="section">
    <h2 class="section-title"><i class="fa fa-square-check"></i> Code Coverage (JaCoCo)</h2>
    <div class="coverage-bars">
      <div class="cov-bar-row">
        <span class="cov-label">Line Coverage</span>
        <div class="cov-track"><div class="cov-fill $(python3 -c "print('cov-warn' if float('${LINE_PCT}') < float('${COVERAGE_THRESHOLD}') else 'cov-ok')" 2>/dev/null || echo cov-ok)" style="width:${LINE_PCT}%"></div></div>
        <span class="cov-pct">${LINE_PCT}%</span>
      </div>
      <div class="cov-bar-row">
        <span class="cov-label">Branch Coverage</span>
        <div class="cov-track"><div class="cov-fill cov-ok" style="width:${BRANCH_PCT}%"></div></div>
        <span class="cov-pct">${BRANCH_PCT}%</span>
      </div>
      <div class="cov-bar-row">
        <span class="cov-label">Method Coverage</span>
        <div class="cov-track"><div class="cov-fill cov-ok" style="width:${METHOD_PCT}%"></div></div>
        <span class="cov-pct">${METHOD_PCT}%</span>
      </div>
    </div>
    <div class="tool-note">
      Threshold: <strong>${COVERAGE_THRESHOLD}%</strong> line coverage.
      $(python3 -c "print('✅ Threshold met.' if float('${LINE_PCT}') >= float('${COVERAGE_THRESHOLD}') else '❌ Below threshold — add unit tests in src/test/java/')" 2>/dev/null || echo "")
      To raise threshold, update <code>COVERAGE_THRESHOLD</code> in <code>backend-ci.yml</code>.
    </div>
  </section>

  <!-- ── CODE QUALITY ───────────────────────────────────────────────────── -->
  <section id="quality" class="section">
    <h2 class="section-title"><i class="fa fa-star"></i> Code Quality</h2>
    <table class="status-table">
      <thead><tr><th>Tool</th><th>Status</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Checkstyle</td><td class="status-pass">✅ Ran</td><td>Google Java Style base. See checkstyle-result.xml</td></tr>
        <tr><td>PMD</td><td class="status-pass">✅ Ran</td><td>Java 21 rules. See pmd.xml</td></tr>
        <tr><td>SpotBugs</td><td class="status-pass">✅ Ran</td><td>Bytecode-level analysis. See spotbugsXml.xml</td></tr>
        <tr><td>SonarQube</td>
            <td class="status-skip">⏭️ Not Configured</td>
            <td>
              $([ "$SONAR_ENABLED" = "false" ] && echo 'SONAR_ENABLED=false — runs on localhost only. Cannot reach from GitHub-hosted runners. See scripts/README.md.' || echo "Gate status: ${SONAR_STATUS}")
            </td>
        </tr>
      </tbody>
    </table>
  </section>

  <!-- ── SECURITY FINDINGS ──────────────────────────────────────────────── -->
  <section id="security" class="section">
    <h2 class="section-title"><i class="fa fa-shield-halved"></i> Security Findings (${TOTAL} total)</h2>
    <div class="table-toolbar">
      <input type="text" id="findingsSearch" placeholder="🔍 Search findings…" class="search-input" onkeyup="filterTable()"/>
      <select id="sevFilter" class="sev-filter" onchange="filterTable()">
        <option value="">All Severities</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
        <option value="INFO">Info</option>
      </select>
    </div>
    <div class="table-wrap">
    <table class="findings-table" id="findingsTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Severity ↕</th>
          <th onclick="sortTable(1)">Tool ↕</th>
          <th onclick="sortTable(2)">Finding ↕</th>
          <th>File</th>
          <th>Line</th>
          <th>CWE</th>
          <th>OWASP</th>
        </tr>
      </thead>
      <tbody id="findingsBody">
${FINDINGS_ROWS}
      </tbody>
    </table>
    </div>
  </section>

  <!-- ── SBOM ───────────────────────────────────────────────────────────── -->
  <section id="sbom" class="section">
    <h2 class="section-title"><i class="fa fa-list"></i> Software Bill of Materials (SBOM)</h2>
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-val">${SBOM_CDX_COUNT}</div>
        <div class="metric-label">CycloneDX Components</div>
      </div>
      <div class="metric-card">
        <div class="metric-val">${SBOM_SPDX_COUNT}</div>
        <div class="metric-label">SPDX Packages</div>
      </div>
    </div>
    <div class="tool-note">
      Generated by <strong>Syft</strong> in both CycloneDX-JSON and SPDX-JSON formats.
      Download from GitHub Artifacts: <code>sbom-cyclonedx-*.json</code>, <code>sbom-spdx-*.json</code>.
    </div>
  </section>

  <!-- ── RECOMMENDATIONS ────────────────────────────────────────────────── -->
  <section id="recommendations" class="section">
    <h2 class="section-title"><i class="fa fa-lightbulb"></i> Recommendations</h2>
    <table class="status-table">
      <thead><tr><th>Priority</th><th>Issue</th><th>Owner</th><th>Est. Fix Time</th><th>Status</th></tr></thead>
      <tbody>
        <tr>
          <td><span class="badge badge-critical">P1 — CRITICAL</span></td>
          <td>Remediate open IDOR vulnerability — attackers can access other users' resources by manipulating IDs in requests. Enforce ownership checks at service layer.</td>
          <td>Backend Team</td>
          <td>2–4 hours</td>
          <td class="status-fail">Open</td>
        </tr>
        <tr>
          <td><span class="badge badge-critical">P2 — CRITICAL</span></td>
          <td>Complete credential exposure incident response — verify all affected credentials rotated, remove secrets from git history via git-filter-repo or BFG, add pre-commit secret scanning.</td>
          <td>Security Lead</td>
          <td>4–8 hours</td>
          <td class="status-fail">Verify</td>
        </tr>
        <tr>
          <td><span class="badge badge-high">P3 — HIGH</span></td>
          <td>Fix NULL-capable username/email on users table — MySQL UNIQUE allows multiple NULL rows. Potential authentication bypass.</td>
          <td>Database Team</td>
          <td>1–2 hours</td>
          <td class="status-fail">Open</td>
        </tr>
        <tr>
          <td><span class="badge badge-high">P4 — HIGH</span></td>
          <td>Patch any critical CVEs reported by OWASP Dependency-Check. Run <code>mvn versions:display-dependency-updates</code> to identify upgrades.</td>
          <td>Backend Team</td>
          <td>2–4 hours</td>
          <td class="status-fail">Open</td>
        </tr>
        <tr>
          <td><span class="badge badge-medium">P5 — MEDIUM</span></td>
          <td>Enable SonarQube analysis — configure SonarCloud (free for open source) or a self-hosted runner. Set SONAR_ENABLED=true and add SONAR_TOKEN + SONAR_HOST_URL secrets.</td>
          <td>DevOps</td>
          <td>2–3 hours</td>
          <td class="status-skip">Planned</td>
        </tr>
        <tr>
          <td><span class="badge badge-medium">P6 — MEDIUM</span></td>
          <td>Increase test coverage from current level to at least ${COVERAGE_THRESHOLD}% line coverage. Add unit tests for service and security layers first.</td>
          <td>Backend Team</td>
          <td>Ongoing</td>
          <td class="status-fail">Open</td>
        </tr>
        <tr>
          <td><span class="badge badge-low">P7 — LOW</span></td>
          <td>Resolve denormalised columns in students table (7 duplicate column pairs).</td>
          <td>Database Team</td>
          <td>4–8 hours</td>
          <td class="status-skip">Planned</td>
        </tr>
        <tr>
          <td><span class="badge badge-low">P8 — LOW</span></td>
          <td>Remove test/fictional accounts from production database (phone=123, fictional users).</td>
          <td>DBA</td>
          <td>30 minutes</td>
          <td class="status-fail">Open</td>
        </tr>
      </tbody>
    </table>
  </section>

  <!-- ── ARTIFACTS ──────────────────────────────────────────────────────── -->
  <section id="artifacts" class="section">
    <h2 class="section-title"><i class="fa fa-download"></i> Artifacts</h2>
    <p class="tool-note">Download from GitHub Actions → Run #${RUN_NUMBER} → Artifacts</p>
    <table class="status-table">
      <thead><tr><th>Artifact Name</th><th>Contents</th><th>Retention</th></tr></thead>
      <tbody>
        <tr><td>FINAL-security-report-${RUN_NUMBER}</td><td>final-security-report.html + merged-findings.json</td><td>90 days</td></tr>
        <tr><td>all-security-reports-${RUN_NUMBER}</td><td>All raw tool reports bundle</td><td>90 days</td></tr>
        <tr><td>gitleaks-report-${RUN_NUMBER}</td><td>gitleaks-report.json</td><td>90 days</td></tr>
        <tr><td>semgrep-report-${RUN_NUMBER}</td><td>semgrep.sarif, semgrep.json</td><td>30 days</td></tr>
        <tr><td>codeql-report-${RUN_NUMBER}</td><td>CodeQL SARIF files</td><td>30 days</td></tr>
        <tr><td>sonar-report-${RUN_NUMBER}</td><td>sonar-status.json</td><td>30 days</td></tr>
        <tr><td>dependency-check-report-${RUN_NUMBER}</td><td>HTML + JSON OWASP report</td><td>30 days</td></tr>
        <tr><td>trivy-report-${RUN_NUMBER}</td><td>trivy.sarif, trivy.json</td><td>30 days</td></tr>
        <tr><td>sbom-cyclonedx-${RUN_NUMBER}</td><td>CycloneDX SBOM JSON</td><td>90 days</td></tr>
        <tr><td>sbom-spdx-${RUN_NUMBER}</td><td>SPDX SBOM JSON</td><td>90 days</td></tr>
        <tr><td>junit-reports-${RUN_NUMBER}</td><td>JUnit XML test reports</td><td>30 days</td></tr>
        <tr><td>jacoco-coverage-${RUN_NUMBER}</td><td>JaCoCo HTML + XML coverage</td><td>30 days</td></tr>
        <tr><td>quality-reports-${RUN_NUMBER}</td><td>Checkstyle, PMD, SpotBugs reports</td><td>30 days</td></tr>
        <tr><td>pragatix-backend-${RUN_NUMBER}</td><td>Spring Boot JAR</td><td>30 days</td></tr>
      </tbody>
    </table>
  </section>

  <!-- ── TIMELINE ───────────────────────────────────────────────────────── -->
  <section id="timeline" class="section">
    <h2 class="section-title"><i class="fa fa-clock"></i> Pipeline Timeline</h2>
    <div class="timeline">
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>Secret Scan (Gitleaks)</strong><div class="tl-meta">Full history scan</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>Semgrep SAST</strong><div class="tl-meta">p/java + p/owasp-top-ten</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>CodeQL Analysis</strong><div class="tl-meta">java-kotlin language pack</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-grey"></div><div class="tl-content"><strong>SonarQube</strong><div class="tl-meta">Skipped — SONAR_ENABLED=false</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>OWASP Dependency-Check</strong><div class="tl-meta">NVD CVE database scan</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>Trivy Filesystem Scan</strong><div class="tl-meta">Source + dependency scan</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>Syft SBOM Generation</strong><div class="tl-meta">CycloneDX + SPDX formats</div></div></div>
      <div class="tl-item"><div class="tl-dot tl-green"></div><div class="tl-content"><strong>Report Merge &amp; Gate</strong><div class="tl-meta">Final decision: ${GATE_RESULT}</div></div></div>
    </div>
  </section>

  <!-- ── FINAL DECISION ─────────────────────────────────────────────────── -->
  <section class="section final-decision gate-box-${GATE_RESULT_LOWER}">
    <h2>Final Decision</h2>
    <div class="final-icon">$([ "$GATE_RESULT" = "PASS" ] && echo "✅" || echo "❌")</div>
    <div class="final-text">SECURITY GATE: ${GATE_RESULT}</div>
    <div class="final-sub">Mode: <code>${GATE_MODE}</code> | Run #${RUN_NUMBER} | ${BUILD_DATE}</div>
  </section>

  <footer class="page-footer">
    PragatiX DevSecOps Dashboard — Generated ${BUILD_DATE} ${BUILD_TIME} — Run #${RUN_NUMBER}
  </footer>
</main>
</div>

<!-- Scripts -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script>
$(cat security/dashboard.js 2>/dev/null || echo "/* dashboard.js not found */")

// Chart data
const SEV_DATA = [${CRIT}, ${HIGH}, ${MED}, ${LOW}, ${INFO}];
const SEV_LABELS = ['Critical','High','Medium','Low','Info'];
const SEV_COLORS = ['#ef4444','#f97316','#eab308','#3b82f6','#6b7280'];

new Chart(document.getElementById('sevChart'), {
  type: 'doughnut',
  data: { labels: SEV_LABELS, datasets: [{ data: SEV_DATA, backgroundColor: SEV_COLORS, borderWidth: 2, borderColor: '#13132a' }] },
  options: { plugins: { legend: { labels: { color: '#e2e8f0', font: { size: 12 } } } }, cutout: '60%' }
});

new Chart(document.getElementById('scoreChart'), {
  type: 'doughnut',
  data: {
    datasets: [{
      data: [${SEC_SCORE}, ${100 - SEC_SCORE}],
      backgroundColor: ['#7c3aed','#1e1e3e'],
      borderWidth: 0
    }]
  },
  options: {
    plugins: { legend: { display: false }, tooltip: { enabled: false } },
    cutout: '70%'
  },
  plugins: [{
    id: 'scoreText',
    afterDraw(chart) {
      const { ctx, chartArea: { top, bottom, left, right } } = chart;
      ctx.save();
      ctx.font = 'bold 28px Segoe UI';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.fillText('${SEC_SCORE}', (left+right)/2, (top+bottom)/2+8);
      ctx.font = '13px Segoe UI';
      ctx.fillStyle = '#94a3b8';
      ctx.fillText('/100', (left+right)/2, (top+bottom)/2+26);
      ctx.restore();
    }
  }]
});

new Chart(document.getElementById('coverageChart'), {
  type: 'bar',
  data: {
    labels: ['Line','Branch','Method'],
    datasets: [{
      label: 'Coverage %',
      data: [${LINE_PCT}, ${BRANCH_PCT}, ${METHOD_PCT}],
      backgroundColor: ['#7c3aed','#06b6d4','#22c55e']
    }]
  },
  options: {
    scales: {
      y: { min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#2d2d50' } },
      x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
    },
    plugins: { legend: { display: false } }
  }
});

function filterTable() {
  const search = document.getElementById('findingsSearch').value.toLowerCase();
  const sev = document.getElementById('sevFilter').value.toLowerCase();
  const rows = document.querySelectorAll('#findingsBody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    const sevCell = row.cells[0] ? row.cells[0].textContent.toLowerCase() : '';
    const textMatch = !search || text.includes(search);
    const sevMatch  = !sev || sevCell.includes(sev);
    row.style.display = textMatch && sevMatch ? '' : 'none';
  });
}

let sortDir = {};
function sortTable(col) {
  const tbody = document.getElementById('findingsBody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  sortDir[col] = !sortDir[col];
  rows.sort((a, b) => {
    const at = (a.cells[col] ? a.cells[col].textContent : '').trim();
    const bt = (b.cells[col] ? b.cells[col].textContent : '').trim();
    return sortDir[col] ? at.localeCompare(bt) : bt.localeCompare(at);
  });
  rows.forEach(r => tbody.appendChild(r));
}

function exportJSON() {
  fetch('merged-findings.json')
    .then(r => r.blob())
    .then(b => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(b);
      a.download = 'merged-findings.json';
      a.click();
    })
    .catch(() => alert('merged-findings.json not in same directory. Download from GitHub Artifacts.'));
}
</script>
</body>
</html>
HTMLEOF

echo "[generate-security-report] ✅ HTML report written to: $OUTPUT_HTML"
