#!/usr/bin/env bash
# ==============================================================================
# security-gate.sh — PragatiX Security Gate
# ==============================================================================
# Computes PASS/FAIL status from all security scan results.
# Respects GATE_MODE:
#   report-only  → Print result clearly, but always exit 0 (never block run)
#   block        → Exit non-zero when gate FAILS
#
# Environment variables expected (set by the workflow):
#   GATE_MODE            report-only | block
#   COVERAGE_THRESHOLD   integer (e.g. 40)
#   SONAR_ENABLED        true | false
#   REPORTS_DIR          path to security/reports/
#   GITLEAKS_REPORT      path to gitleaks-report.json
#   DEPCHECK_REPORT      path to dependency-check-report.json
#   SEMGREP_REPORT       path to semgrep.json
#   TRIVY_REPORT         path to trivy.json
#
# KNOWN CURRENT ISSUES (expected FAIL in report-only mode):
#   - Open IDOR vulnerability identified in code review
#   - Prior credential-exposure incident (now resolved but counted)
#   These are CORRECT findings — the gate should report accurately, not suppress.
# ==============================================================================
set -euo pipefail

GATE_MODE="${GATE_MODE:-report-only}"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-40}"
SONAR_ENABLED="${SONAR_ENABLED:-false}"
REPORTS_DIR="${REPORTS_DIR:-security/reports}"
MERGED_JSON="${REPORTS_DIR}/merged-findings.json"

GITLEAKS_REPORT="${GITLEAKS_REPORT:-security/generated/gitleaks/gitleaks-report.json}"
DEPCHECK_REPORT="${DEPCHECK_REPORT:-security/generated/dependency-check/dependency-check-report.json}"
SEMGREP_REPORT="${SEMGREP_REPORT:-security/generated/semgrep/semgrep.json}"
TRIVY_REPORT="${TRIVY_REPORT:-security/generated/trivy/trivy.json}"

# ─── Helpers ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
BLU='\033[0;34m'
CYN='\033[0;36m'
BLD='\033[1m'
RST='\033[0m'

pass_count=0
fail_count=0
warn_count=0
declare -a gate_lines=()

gate_check() {
    local name="$1"     # Display name
    local status="$2"   # PASS | FAIL | WARN | SKIP
    local detail="$3"   # Detail message
    gate_lines+=("$name|$status|$detail")
    case "$status" in
        PASS) ((pass_count++)) ;;
        FAIL) ((fail_count++)) ;;
        WARN) ((warn_count++)) ;;
    esac
}

jq_safe() {
    # Run jq with a default if file missing or jq fails
    local query="$1"
    local file="$2"
    local default="${3:-0}"
    if command -v jq &>/dev/null && [ -f "$file" ]; then
        jq -r "$query" "$file" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

python_count() {
    # Use python3 for JSON parsing when jq is unavailable
    local query="$1"
    local file="$2"
    local default="${3:-0}"
    if [ -f "$file" ]; then
        python3 -c "$query" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚦  PragatiX Security Gate"
echo "  Mode:      ${GATE_MODE}"
echo "  Threshold: ${COVERAGE_THRESHOLD}% line coverage"
echo "  SonarQube: ${SONAR_ENABLED}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ─── 1. Secrets / Gitleaks ────────────────────────────────────────────────────
echo "🔑 [1/7] Checking: Secrets (Gitleaks)"
if [ -f "$GITLEAKS_REPORT" ]; then
    SECRET_COUNT=$(python3 -c "
import json, sys
try:
    data = json.load(open('$GITLEAKS_REPORT'))
    items = data if isinstance(data, list) else data.get('findings', [])
    print(len(items))
except:
    print(0)
" 2>/dev/null || echo 0)

    if [ "$SECRET_COUNT" -gt 0 ]; then
        gate_check "Secrets (Gitleaks)" "FAIL" "${SECRET_COUNT} secret(s) detected in repository"
        echo "  ❌ FAIL — ${SECRET_COUNT} secret(s) found"
    else
        gate_check "Secrets (Gitleaks)" "PASS" "No secrets found"
        echo "  ✅ PASS — No secrets detected"
    fi
else
    gate_check "Secrets (Gitleaks)" "WARN" "Report not found — scan may not have run"
    echo "  ⚠️  WARN — Gitleaks report not found"
fi

# ─── 2. Critical Vulnerabilities (Semgrep + Trivy + CodeQL) ──────────────────
echo "🛡️  [2/7] Checking: Critical Vulnerabilities"
CRIT_COUNT=0

if [ -f "$MERGED_JSON" ]; then
    CRIT_COUNT=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    findings = data.get('findings', [])
    count = sum(1 for f in findings if f.get('severity','').upper() == 'CRITICAL')
    print(count)
except:
    print(0)
" 2>/dev/null || echo 0)
fi

if [ "$CRIT_COUNT" -gt 0 ]; then
    gate_check "Critical Vulnerabilities" "FAIL" "${CRIT_COUNT} critical vulnerability/vulnerabilities found"
    echo "  ❌ FAIL — ${CRIT_COUNT} critical vulnerability/vulnerabilities"
    echo "      NOTE: Known open IDOR vulnerability contributes to this count."
    echo "      This is EXPECTED and CORRECT — do not suppress."
else
    gate_check "Critical Vulnerabilities" "PASS" "No critical vulnerabilities"
    echo "  ✅ PASS — No critical vulnerabilities"
fi

# ─── 3. JUnit Test Failures ────────────────────────────────────────────────────
echo "🧪 [3/7] Checking: JUnit Tests"
JUNIT_FAILURES=0
JUNIT_ERRORS=0
JUNIT_TESTS=0

if [ -f "$MERGED_JSON" ]; then
    JUNIT_FAILURES=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    print(data.get('tests', {}).get('failures', 0))
except: print(0)
" 2>/dev/null || echo 0)
    JUNIT_ERRORS=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    print(data.get('tests', {}).get('errors', 0))
except: print(0)
" 2>/dev/null || echo 0)
    JUNIT_TESTS=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    print(data.get('tests', {}).get('tests', 0))
except: print(0)
" 2>/dev/null || echo 0)
fi

TOTAL_JUNIT_ISSUES=$((JUNIT_FAILURES + JUNIT_ERRORS))
if [ "$TOTAL_JUNIT_ISSUES" -gt 0 ]; then
    gate_check "JUnit Tests" "FAIL" "${JUNIT_TESTS} tests, ${JUNIT_FAILURES} failures, ${JUNIT_ERRORS} errors"
    echo "  ❌ FAIL — ${JUNIT_FAILURES} test failure(s), ${JUNIT_ERRORS} error(s)"
elif [ "$JUNIT_TESTS" -eq 0 ]; then
    gate_check "JUnit Tests" "WARN" "No tests found or JUnit report missing"
    echo "  ⚠️  WARN — No test results found"
else
    gate_check "JUnit Tests" "PASS" "${JUNIT_TESTS} tests passed"
    echo "  ✅ PASS — ${JUNIT_TESTS} tests passed"
fi

# ─── 4. Code Coverage ────────────────────────────────────────────────────────
echo "📈 [4/7] Checking: Code Coverage (JaCoCo)"
COVERAGE_PCT=0
if [ -f "$MERGED_JSON" ]; then
    COVERAGE_PCT=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    print(data.get('coverage', {}).get('line_pct', 0))
except: print(0)
" 2>/dev/null || echo 0)
fi

if python3 -c "import sys; sys.exit(0 if float('${COVERAGE_PCT}') >= float('${COVERAGE_THRESHOLD}') else 1)" 2>/dev/null; then
    gate_check "Code Coverage" "PASS" "${COVERAGE_PCT}% >= ${COVERAGE_THRESHOLD}% threshold"
    echo "  ✅ PASS — ${COVERAGE_PCT}% coverage (threshold: ${COVERAGE_THRESHOLD}%)"
else
    gate_check "Code Coverage" "FAIL" "${COVERAGE_PCT}% < ${COVERAGE_THRESHOLD}% threshold"
    echo "  ❌ FAIL — ${COVERAGE_PCT}% coverage is below ${COVERAGE_THRESHOLD}% threshold"
    echo "      HOW TO FIX: Add unit tests. Raise COVERAGE_THRESHOLD gradually as"
    echo "      coverage improves. Target path: src/test/java/"
fi

# ─── 5. OWASP Dependency-Check Critical CVEs ─────────────────────────────────
echo "📦 [5/7] Checking: Dependency Vulnerabilities (OWASP)"
DC_CRITICAL=0
if [ -f "$MERGED_JSON" ]; then
    DC_CRITICAL=$(python3 -c "
import json
try:
    data = json.load(open('$MERGED_JSON'))
    findings = data.get('findings', [])
    count = sum(1 for f in findings
                if f.get('tool') == 'OWASP-Dependency-Check'
                and f.get('severity','').upper() == 'CRITICAL')
    print(count)
except: print(0)
" 2>/dev/null || echo 0)
fi

if [ "$DC_CRITICAL" -gt 0 ]; then
    gate_check "Dependency CVEs" "FAIL" "${DC_CRITICAL} critical dependency CVE(s)"
    echo "  ❌ FAIL — ${DC_CRITICAL} critical CVE(s) in dependencies"
else
    gate_check "Dependency CVEs" "PASS" "No critical dependency CVEs"
    echo "  ✅ PASS — No critical dependency CVEs"
fi

# ─── 6. SonarQube Quality Gate ───────────────────────────────────────────────
echo "📡 [6/7] Checking: SonarQube Quality Gate"
if [ "$SONAR_ENABLED" = "true" ]; then
    SONAR_GATE_STATUS="UNKNOWN"
    SONAR_STATUS_FILE="security/generated/sonar/sonar-status.json"
    if [ -f "$SONAR_STATUS_FILE" ]; then
        SONAR_GATE_STATUS=$(python3 -c "
import json
try:
    data = json.load(open('$SONAR_STATUS_FILE'))
    print(data.get('projectStatus', {}).get('status', data.get('status', 'UNKNOWN')))
except: print('UNKNOWN')
" 2>/dev/null || echo "UNKNOWN")
    fi
    if [ "$SONAR_GATE_STATUS" = "OK" ] || [ "$SONAR_GATE_STATUS" = "PASS" ]; then
        gate_check "SonarQube Gate" "PASS" "Quality gate: ${SONAR_GATE_STATUS}"
        echo "  ✅ PASS — SonarQube Quality Gate: ${SONAR_GATE_STATUS}"
    elif [ "$SONAR_GATE_STATUS" = "UNKNOWN" ]; then
        gate_check "SonarQube Gate" "WARN" "Could not determine gate status"
        echo "  ⚠️  WARN — SonarQube status unknown"
    else
        gate_check "SonarQube Gate" "FAIL" "Quality gate: ${SONAR_GATE_STATUS}"
        echo "  ❌ FAIL — SonarQube Quality Gate: ${SONAR_GATE_STATUS}"
    fi
else
    gate_check "SonarQube Gate" "SKIP" "SONAR_ENABLED=false — excluded from gate calculation"
    echo "  ⏭️  SKIP — SONAR_ENABLED=false (not counted in gate result)"
fi

# ─── 7. Credential Exposure History ──────────────────────────────────────────
echo "🔐 [7/7] Checking: Prior Credential Exposure"
# This check flags the known prior credential-exposure incident.
# It is intentionally a FAIL so the gate accurately reflects the risk posture.
# Remove this check only after a full credential rotation + audit has been completed
# and documented in your incident log.
gate_check "Credential Exposure" "FAIL" "Prior credential-exposure incident recorded — verify full rotation completed"
echo "  ❌ FAIL — Prior credential-exposure incident on record"
echo "      ACTION: Verify all credentials rotated, secrets purged from git history."
echo "      Reference: See incident log / security runbook."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊  SECURITY GATE RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "%-35s %-8s %s\n" "Check" "Status" "Detail"
echo "───────────────────────────────────────────────────────────────────"
for line in "${gate_lines[@]}"; do
    IFS='|' read -r name status detail <<< "$line"
    case "$status" in
        PASS) icon="✅" ;;
        FAIL) icon="❌" ;;
        WARN) icon="⚠️ " ;;
        SKIP) icon="⏭️ " ;;
        *)    icon="❓" ;;
    esac
    printf "%-35s %-8s %s\n" "$name" "$icon $status" "$detail"
done
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ─── Final Decision ───────────────────────────────────────────────────────────
if [ "$fail_count" -gt 0 ]; then
    GATE_RESULT="FAIL"
    GATE_COLOR="❌"
else
    GATE_RESULT="PASS"
    GATE_COLOR="✅"
fi

echo ""
echo "  $GATE_COLOR  SECURITY GATE: $GATE_RESULT"
echo "      ${pass_count} passed | ${fail_count} failed | ${warn_count} warnings"
echo "      Mode: $GATE_MODE"
echo ""

if [ "$GATE_MODE" = "report-only" ]; then
    echo "  ℹ️  GATE_MODE=report-only"
    echo "      The gate result above is INFORMATIONAL ONLY."
    echo "      The workflow will NOT be blocked regardless of PASS/FAIL."
    echo "      Switch to GATE_MODE=block in the workflow env to enforce."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ─── Write Markdown Summary for GitHub Actions UI ─────────────────────────────
SUMMARY_FILE="${REPORTS_DIR}/gate-summary.md"
mkdir -p "$REPORTS_DIR"

cat > "$SUMMARY_FILE" << SUMMARY_EOF
## 🚦 Security Gate: ${GATE_RESULT} ${GATE_COLOR}

> **Mode**: \`${GATE_MODE}\` — $([ "$GATE_MODE" = "report-only" ] && echo "result is informational only — workflow not blocked" || echo "result blocks the workflow on FAIL")

| Check | Status | Detail |
|---|---|---|
SUMMARY_EOF

for line in "${gate_lines[@]}"; do
    IFS='|' read -r name status detail <<< "$line"
    case "$status" in
        PASS) icon="✅" ;;
        FAIL) icon="❌" ;;
        WARN) icon="⚠️" ;;
        SKIP) icon="⏭️" ;;
        *)    icon="❓" ;;
    esac
    echo "| $name | $icon $status | $detail |" >> "$SUMMARY_FILE"
done

cat >> "$SUMMARY_FILE" << SUMMARY_EOF

---
**${pass_count} PASS** | **${fail_count} FAIL** | **${warn_count} WARN**

> ⚠️ Known issues currently causing FAIL: open IDOR vulnerability + prior credential-exposure incident.
> These are EXPECTED and CORRECT findings. See security runbook for remediation steps.
SUMMARY_EOF

echo "📄 Gate summary written to: $SUMMARY_FILE"

# ─── Exit Code (respects GATE_MODE) ─────────────────────────────────────────
if [ "$GATE_MODE" = "block" ] && [ "$GATE_RESULT" = "FAIL" ]; then
    echo "🚫 GATE_MODE=block + GATE_RESULT=FAIL — exiting with code 1"
    exit 1
fi

exit 0
