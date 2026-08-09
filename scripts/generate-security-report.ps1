# ==============================================================================
# generate-security-report.ps1
# Windows PowerShell equivalent of generate-security-report.sh
# For LOCAL manual runs on Windows 11 — not used in GitHub Actions
# (GitHub Actions uses the .sh version on ubuntu-latest runners)
#
# Usage:
#   cd N:\pragatiX
#   .\scripts\generate-security-report.ps1
# ==============================================================================
param(
    [string]$ReportsDir      = "security\reports",
    [string]$ReportBase      = "security\generated",
    [string]$SonarEnabled    = "false",
    [string]$GateMode        = "report-only",
    [string]$CoverageThreshold = "40",
    [string]$GitSha          = "local",
    [string]$GitBranch       = "local",
    [string]$RunId           = "0",
    [string]$RunNumber       = "0",
    [string]$Repo            = "local/pragatix",
    [string]$TriggeredBy     = $env:USERNAME,
    [string]$WorkflowName    = "Local Security Scan"
)

$ErrorActionPreference = "Continue"

$MergedJson = Join-Path $ReportsDir "merged-findings.json"
$OutputHtml = Join-Path $ReportsDir "final-security-report.html"
$BuildDate  = Get-Date -Format "yyyy-MM-dd"
$BuildTime  = (Get-Date -Format "HH:mm:ss") + " (local)"

Write-Host "[generate-security-report.ps1] Starting..."
Write-Host "  Reports dir: $ReportsDir"
Write-Host "  Output:      $OutputHtml"

# ── Ensure output directory exists ────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

# ── Step 1: Run merge-reports.py ──────────────────────────────────────────────
Write-Host ""
Write-Host "[Step 1/3] Running merge-reports.py..."
$MergeScript = "scripts\merge-reports.py"
if (Test-Path $MergeScript) {
    python $MergeScript `
        --reports-dir $ReportBase `
        --output $MergedJson `
        --sonar-enabled $SonarEnabled
} else {
    Write-Warning "merge-reports.py not found at $MergeScript"
}

# ── Step 2: Extract metrics from merged JSON ───────────────────────────────────
Write-Host ""
Write-Host "[Step 2/3] Extracting metrics..."

function Get-Metric {
    param([string]$Expr, [string]$Default = "0")
    if (Test-Path $MergedJson) {
        try {
            $result = python -c "
import json, sys
try:
    data = json.load(open(r'$($MergedJson -replace '\\','\\\\')'))
    result = $Expr
    print(result if result is not None else '$Default')
except Exception as e:
    print('$Default')
" 2>$null
            return $result.Trim()
        } catch { return $Default }
    }
    return $Default
}

$Crit       = Get-Metric "data['summary']['severity_counts'].get('CRITICAL', 0)"
$High       = Get-Metric "data['summary']['severity_counts'].get('HIGH', 0)"
$Med        = Get-Metric "data['summary']['severity_counts'].get('MEDIUM', 0)"
$Low        = Get-Metric "data['summary']['severity_counts'].get('LOW', 0)"
$InfoCount  = Get-Metric "data['summary']['severity_counts'].get('INFO', 0)"
$Total      = Get-Metric "data['meta']['total_findings']"
$LinePct    = Get-Metric "data['coverage']['line_pct']"
$BranchPct  = Get-Metric "data['coverage']['branch_pct']"
$MethodPct  = Get-Metric "data['coverage']['method_pct']"
$Tests      = Get-Metric "data['tests']['tests']"
$Failures   = Get-Metric "data['tests']['failures']"
$Errors     = Get-Metric "data['tests']['errors']"
$Skipped    = Get-Metric "data['tests']['skipped']"
$SonarSt    = Get-Metric "data['sonar']['status']" "NOT_CONFIGURED"
$SbomCdx    = Get-Metric "data['sbom']['cyclonedx']['component_count']"
$SbomSpdx   = Get-Metric "data['sbom']['spdx']['component_count']"

$SecScore   = [Math]::Max(10, 100 - ([int]$Crit * 15 + [int]$High * 5 + [int]$Med * 2 + [int]$Low))
$GateResult = if ([int]$Crit -gt 0 -or [int]$Failures -gt 0 -or [int]$Errors -gt 0 -or [double]$LinePct -lt [double]$CoverageThreshold) { "FAIL" } else { "PASS" }

Write-Host "  Critical=$Crit High=$High Med=$Med Low=$Low Info=$InfoCount"
Write-Host "  Coverage: Line=$LinePct% Branch=$BranchPct% Method=$MethodPct%"
Write-Host "  Gate: $GateResult (Mode: $GateMode)"

# ── Step 3: Generate HTML (minimal local version) ─────────────────────────────
Write-Host ""
Write-Host "[Step 3/3] Generating HTML report..."

# Extract findings rows via Python (write to temp file to avoid PS multi-line -c issue)
$FindingsRows = ""
if (Test-Path $MergedJson) {
    $MergedJsonEsc = $MergedJson -replace '\\', '\\\\'
    $TmpPy = [System.IO.Path]::GetTempFileName() + ".py"
    Set-Content -Path $TmpPy -Encoding UTF8 -Value @"
import json, html, os, sys
merged = r'$MergedJsonEsc'
rows = ''
SEV_BADGE = {'CRITICAL':('badge-critical','[C]'),'HIGH':('badge-high','[H]'),'MEDIUM':('badge-medium','[M]'),'LOW':('badge-low','[L]'),'INFO':('badge-info','[I]')}
try:
    data = json.load(open(merged, encoding='utf-8'))
    for f in data.get('findings',[])[:200]:
        sev = f.get('severity','INFO')
        cls,icon = SEV_BADGE.get(sev,('badge-info','[I]'))
        fname = os.path.basename(f.get('file','')) or '-'
        line = f.get('line',0) or '-'
        cwe  = html.escape(f.get('cwe','') or '-')
        owasp = html.escape(f.get('owasp','') or '-')
        rows += f'<tr><td><span class="badge {cls}">{icon} {html.escape(sev)}</span></td><td>{html.escape(f.get("tool",""))}</td><td>{html.escape(f.get("title","")[:80])}</td><td>{html.escape(fname)}</td><td>{line}</td><td>{cwe}</td><td>{owasp}</td></tr>'
    if not rows:
        rows = '<tr><td colspan=7>No findings.</td></tr>'
except Exception as e:
    rows = f'<tr><td colspan=7>Error loading findings: {e}</td></tr>'
sys.stdout.buffer.write(rows.encode('utf-8'))
"@
    $FindingsRows = python $TmpPy 2>$null
    Remove-Item $TmpPy -ErrorAction SilentlyContinue
}

$GateBadge = if ($GateResult -eq "PASS") { "✅" } else { "❌" }
$GateClass = $GateResult.ToLower()

# Read dashboard CSS/JS
$DashCss = ""
$DashJs  = ""
$CssPath = "security\dashboard.css"
$JsPath  = "security\dashboard.js"
if (Test-Path $CssPath) { $DashCss = Get-Content $CssPath -Raw }
if (Test-Path $JsPath)  { $DashJs  = Get-Content $JsPath  -Raw }

$Html = @"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PragatiX Security Report (Local) — $BuildDate</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
$DashCss
</style>
</head>
<body>
<div class="layout">
<nav class="sidebar">
  <div class="sidebar-logo">
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none"><rect width="36" height="36" rx="8" fill="#7c3aed"/><path d="M8 18 L14 12 L22 20 L28 14" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="28" cy="14" r="3" fill="#06b6d4"/></svg>
    <span class="sidebar-brand-text">PragatiX<br/><small>Security</small></span>
  </div>
  <nav class="sidebar-nav">
    <a href="#exec" class="nav-link active"><i class="fa fa-chart-pie"></i> Summary</a>
    <a href="#security" class="nav-link"><i class="fa fa-shield-halved"></i> Findings</a>
    <a href="#recommendations" class="nav-link"><i class="fa fa-lightbulb"></i> Recommendations</a>
  </nav>
  <div class="sidebar-footer">
    <button class="btn-action" onclick="window.print()"><i class="fa fa-print"></i> Print</button>
  </div>
</nav>
<main class="main-content">
  <header class="page-header">
    <div class="header-left">
      <h1>Security Report <small>(Local Scan)</small></h1>
      <div class="header-meta">
        <span class="meta-chip"><i class="fa fa-calendar"></i> $BuildDate $BuildTime</span>
        <span class="meta-chip"><i class="fa fa-user"></i> $TriggeredBy</span>
        <span class="meta-chip"><i class="fa fa-code-branch"></i> $GitBranch</span>
      </div>
    </div>
    <div class="header-right">
      <div class="gate-badge gate-$GateClass">$GateBadge GATE: $GateResult <small>($GateMode)</small></div>
    </div>
  </header>

  <section id="exec" class="section">
    <h2 class="section-title"><i class="fa fa-chart-pie"></i> Executive Summary</h2>
    <div class="sev-cards">
      <div class="sev-card sev-critical"><div class="sev-num">$Crit</div><div class="sev-label">Critical</div></div>
      <div class="sev-card sev-high">    <div class="sev-num">$High</div><div class="sev-label">High</div></div>
      <div class="sev-card sev-medium">  <div class="sev-num">$Med</div><div class="sev-label">Medium</div></div>
      <div class="sev-card sev-low">     <div class="sev-num">$Low</div><div class="sev-label">Low</div></div>
      <div class="sev-card sev-info">    <div class="sev-num">$InfoCount</div><div class="sev-label">Info</div></div>
    </div>
    <div class="charts-row">
      <div class="chart-card"><h4>Severity Distribution</h4><canvas id="sevChart" height="220"></canvas></div>
      <div class="chart-card"><h4>Coverage</h4><canvas id="coverageChart" height="220"></canvas></div>
    </div>
  </section>

  <section id="security" class="section">
    <h2 class="section-title"><i class="fa fa-shield-halved"></i> Security Findings ($Total total)</h2>
    <div class="table-toolbar">
      <input type="text" id="findingsSearch" placeholder="🔍 Search…" class="search-input" onkeyup="filterTable()"/>
      <select id="sevFilter" class="sev-filter" onchange="filterTable()">
        <option value="">All Severities</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>
    </div>
    <div class="table-wrap">
    <table class="findings-table" id="findingsTable">
      <thead><tr><th>Severity</th><th>Tool</th><th>Finding</th><th>File</th><th>Line</th><th>CWE</th><th>OWASP</th></tr></thead>
      <tbody id="findingsBody">$FindingsRows</tbody>
    </table>
    </div>
  </section>

  <footer class="page-footer">PragatiX DevSecOps Dashboard (Local) — $BuildDate $BuildTime</footer>
</main>
</div>
<script>
$DashJs
new Chart(document.getElementById('sevChart'), {
  type: 'doughnut',
  data: { labels: ['Critical','High','Medium','Low','Info'], datasets: [{ data: [$Crit,$High,$Med,$Low,$InfoCount], backgroundColor: ['#ef4444','#f97316','#eab308','#3b82f6','#6b7280'], borderWidth: 2, borderColor: '#13132a' }] },
  options: { plugins: { legend: { labels: { color: '#e2e8f0' } } }, cutout: '60%' }
});
new Chart(document.getElementById('coverageChart'), {
  type: 'bar',
  data: { labels: ['Line','Branch','Method'], datasets: [{ label: 'Coverage %', data: [$LinePct,$BranchPct,$MethodPct], backgroundColor: ['#7c3aed','#06b6d4','#22c55e'] }] },
  options: { scales: { y: { min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: '#2d2d50' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } }, plugins: { legend: { display: false } } }
});
function filterTable() {
  const search = document.getElementById('findingsSearch').value.toLowerCase();
  const sev = document.getElementById('sevFilter').value.toLowerCase();
  document.querySelectorAll('#findingsBody tr').forEach(row => {
    const text = row.textContent.toLowerCase();
    const sevCell = row.cells[0] ? row.cells[0].textContent.toLowerCase() : '';
    row.style.display = (!search || text.includes(search)) && (!sev || sevCell.includes(sev)) ? '' : 'none';
  });
}
</script>
</body>
</html>
"@

Set-Content -Path $OutputHtml -Value $Html -Encoding UTF8
Write-Host "[generate-security-report.ps1] ✅ Report written to: $OutputHtml"
Write-Host ""
Write-Host "Opening in browser..."
Start-Process $OutputHtml
