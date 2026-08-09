#!/usr/bin/env python3
"""
merge-reports.py — PragatiX DevSecOps Report Merger
======================================================
Reads JSON/XML/SARIF outputs from every security tool in
security/generated/<tool>/ and merges them into a single
normalized JSON file (merged-findings.json) consumed by the HTML report.

Usage:
  python merge-reports.py \
    --reports-dir  security/generated \
    --output       security/reports/merged-findings.json \
    --sonar-enabled false

Tool output locations expected:
  gitleaks/gitleaks-report.json
  semgrep/semgrep.json
  semgrep/semgrep.sarif
  codeql/*.sarif
  dependency-check/dependency-check-report.json
  trivy/trivy.json
  sbom/sbom-cyclonedx.json
  sbom/sbom-spdx.json
  sonar/sonar-status.json
  junit/*.xml
  jacoco/jacoco.xml
  spotbugs/spotbugsXml.xml
  checkstyle/checkstyle-result.xml
  pmd/pmd.xml
"""

import argparse
import json
import os
import sys
import glob
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


# ─── Argument Parsing ─────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="Merge DevSecOps security reports into normalized JSON")
    parser.add_argument("--reports-dir",   required=True,  help="Root dir containing all tool subdirs")
    parser.add_argument("--output",        required=True,  help="Output path for merged-findings.json")
    parser.add_argument("--sonar-enabled", default="false", help="Whether SonarQube is enabled (true/false)")
    return parser.parse_args()


# ─── Severity Normalisation ────────────────────────────────────────────────────
SEVERITY_MAP = {
    # SARIF levels
    "error":   "CRITICAL",
    "warning": "HIGH",
    "note":    "MEDIUM",
    "none":    "INFO",
    # Common tool outputs
    "critical": "CRITICAL",
    "high":     "HIGH",
    "medium":   "MEDIUM",
    "moderate": "MEDIUM",
    "low":      "LOW",
    "info":     "INFO",
    "note":     "INFO",
    # OWASP CVSS levels
    "9":  "CRITICAL",
    "7":  "HIGH",
    "4":  "MEDIUM",
    "0":  "LOW",
    # SpotBugs ranks
    "scary":    "HIGH",
    "troubling": "MEDIUM",
    "concern":   "LOW",
}


def normalize_severity(raw: str) -> str:
    if not raw:
        return "INFO"
    return SEVERITY_MAP.get(str(raw).lower().strip(), "MEDIUM")


# ─── Finding Builder ──────────────────────────────────────────────────────────
def make_finding(tool: str, title: str, description: str,
                 severity: str, category: str,
                 file: str = "", line: int = 0,
                 cwe: str = "", owasp: str = "",
                 rule_id: str = "", fingerprint: str = "") -> dict:
    return {
        "tool":        tool,
        "rule_id":     rule_id or "",
        "title":       title,
        "description": description,
        "severity":    normalize_severity(severity),
        "category":    category,
        "file":        file,
        "line":        line,
        "cwe":         cwe,
        "owasp":       owasp,
        "fingerprint": fingerprint or f"{tool}:{rule_id}:{file}:{line}",
    }


# ─── SARIF Parser ─────────────────────────────────────────────────────────────
def parse_sarif(fpath: str, tool_name: str) -> list:
    findings = []
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        for run in data.get("runs", []):
            rules_meta = {}
            # Index rules by id for CWE/description lookup
            for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
                rules_meta[rule.get("id", "")] = rule

            for result in run.get("results", []):
                rule_id   = result.get("ruleId", "")
                level     = result.get("level", "warning")
                msg       = result.get("message", {}).get("text", "No description")
                rule_info = rules_meta.get(rule_id, {})

                # Try to extract CWE from rule metadata
                cwe = ""
                for tag in rule_info.get("properties", {}).get("tags", []):
                    if tag.upper().startswith("CWE"):
                        cwe = tag
                        break

                # File + line from first location
                file_path = ""
                line_num  = 0
                locs = result.get("locations", [])
                if locs:
                    pl = locs[0].get("physicalLocation", {})
                    file_path = pl.get("artifactLocation", {}).get("uri", "")
                    line_num  = pl.get("region", {}).get("startLine", 0)

                findings.append(make_finding(
                    tool=tool_name,
                    title=rule_info.get("shortDescription", {}).get("text", rule_id) or rule_id,
                    description=msg[:500],
                    severity=level,
                    category="Security",
                    file=file_path,
                    line=line_num,
                    cwe=cwe,
                    rule_id=rule_id,
                ))
    except Exception as e:
        print(f"  [WARN] [{tool_name}] SARIF parse error ({fpath}): {e}", file=sys.stderr)
    return findings


# ─── Gitleaks Parser ──────────────────────────────────────────────────────────
def parse_gitleaks(fpath: str) -> list:
    findings = []
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("findings", [])
        for item in items:
            findings.append(make_finding(
                tool="Gitleaks",
                title=f"Secret Detected: {item.get('RuleID', item.get('rule', 'unknown'))}",
                description=f"Secret found in {item.get('File', item.get('file', 'unknown'))} "
                            f"(commit: {item.get('Commit', item.get('commit', 'N/A'))[:8]})",
                severity="CRITICAL",
                category="Secrets",
                file=item.get("File", item.get("file", "")),
                line=item.get("StartLine", item.get("startLine", 0)),
                rule_id=item.get("RuleID", item.get("rule", "")),
            ))
    except Exception as e:
        print(f"  [WARN] [Gitleaks] parse error: {e}", file=sys.stderr)
    return findings


# ─── Semgrep JSON Parser ──────────────────────────────────────────────────────
def parse_semgrep_json(fpath: str) -> list:
    findings = []
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        for result in data.get("results", []):
            severity = result.get("extra", {}).get("severity", "WARNING")
            meta     = result.get("extra", {}).get("metadata", {})
            owasp    = ", ".join(meta.get("owasp", [])) if isinstance(meta.get("owasp"), list) else meta.get("owasp", "")
            cwe      = ", ".join(meta.get("cwe", [])) if isinstance(meta.get("cwe"), list) else meta.get("cwe", "")
            findings.append(make_finding(
                tool="Semgrep",
                title=result.get("check_id", "Unknown Rule"),
                description=result.get("extra", {}).get("message", "No description")[:500],
                severity=severity,
                category="Security",
                file=result.get("path", ""),
                line=result.get("start", {}).get("line", 0),
                cwe=cwe,
                owasp=owasp,
                rule_id=result.get("check_id", ""),
            ))
    except Exception as e:
        print(f"  [WARN] [Semgrep] JSON parse error: {e}", file=sys.stderr)
    return findings


# ─── OWASP Dependency-Check JSON Parser ───────────────────────────────────────
def parse_depcheck_json(fpath: str) -> list:
    findings = []
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        for dep in data.get("dependencies", []):
            for vuln in dep.get("vulnerabilities", []):
                cvss_score = str(vuln.get("cvssv3", {}).get("baseScore",
                             vuln.get("cvssv2", {}).get("score", 0)))
                findings.append(make_finding(
                    tool="OWASP-Dependency-Check",
                    title=vuln.get("name", "Unknown CVE"),
                    description=vuln.get("description", "")[:500],
                    severity=vuln.get("severity", "MEDIUM"),
                    category="Dependency",
                    file=dep.get("fileName", ""),
                    cwe=", ".join(vuln.get("cwes", [])),
                    rule_id=vuln.get("name", ""),
                ))
    except Exception as e:
        print(f"  [WARN] [OWASP-DepCheck] parse error: {e}", file=sys.stderr)
    return findings


# ─── Trivy JSON Parser ────────────────────────────────────────────────────────
def parse_trivy_json(fpath: str) -> list:
    findings = []
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                findings.append(make_finding(
                    tool="Trivy",
                    title=f"{vuln.get('VulnerabilityID', '')} — {vuln.get('PkgName', '')}",
                    description=vuln.get("Description", vuln.get("Title", ""))[:500],
                    severity=vuln.get("Severity", "UNKNOWN"),
                    category="Dependency",
                    file=result.get("Target", ""),
                    rule_id=vuln.get("VulnerabilityID", ""),
                    cwe=", ".join(vuln.get("CweIDs", [])),
                ))
            for secret in result.get("Secrets", []):
                findings.append(make_finding(
                    tool="Trivy",
                    title=f"Secret: {secret.get('RuleID', '')}",
                    description=secret.get("Title", "")[:500],
                    severity="CRITICAL",
                    category="Secrets",
                    file=result.get("Target", ""),
                    rule_id=secret.get("RuleID", ""),
                ))
            for mis in result.get("Misconfigurations", []):
                findings.append(make_finding(
                    tool="Trivy",
                    title=mis.get("Title", "Misconfiguration"),
                    description=mis.get("Description", "")[:500],
                    severity=mis.get("Severity", "MEDIUM"),
                    category="Misconfiguration",
                    file=result.get("Target", ""),
                    rule_id=mis.get("ID", ""),
                ))
    except Exception as e:
        print(f"  [WARN] [Trivy] parse error: {e}", file=sys.stderr)
    return findings


# ─── SpotBugs XML Parser ──────────────────────────────────────────────────────
def parse_spotbugs_xml(fpath: str) -> list:
    findings = []
    try:
        tree = ET.parse(fpath)
        root = tree.getroot()
        for bug in root.findall(".//BugInstance"):
            severity_rank = bug.get("rank", "15")
            try:
                rank = int(severity_rank)
                if rank <= 4:   sev = "HIGH"
                elif rank <= 9: sev = "MEDIUM"
                else:           sev = "LOW"
            except ValueError:
                sev = "MEDIUM"
            src = bug.find("SourceLine")
            file_path = src.get("sourcefile", "") if src is not None else ""
            line_num  = int(src.get("start", 0)) if src is not None else 0
            desc_el   = bug.find("LongMessage")
            desc = desc_el.text if desc_el is not None else bug.get("type", "")
            findings.append(make_finding(
                tool="SpotBugs",
                title=bug.get("type", "Bug"),
                description=(desc or "")[:500],
                severity=sev,
                category="Code Quality",
                file=file_path,
                line=line_num,
                rule_id=bug.get("type", ""),
            ))
    except Exception as e:
        print(f"  [WARN] [SpotBugs] XML parse error: {e}", file=sys.stderr)
    return findings


# ─── Checkstyle XML Parser ────────────────────────────────────────────────────
def parse_checkstyle_xml(fpath: str) -> list:
    findings = []
    try:
        tree = ET.parse(fpath)
        root = tree.getroot()
        for file_el in root.findall("file"):
            fname = file_el.get("name", "")
            for err in file_el.findall("error"):
                findings.append(make_finding(
                    tool="Checkstyle",
                    title=err.get("source", "").split(".")[-1],
                    description=err.get("message", "")[:500],
                    severity=err.get("severity", "warning"),
                    category="Code Style",
                    file=fname,
                    line=int(err.get("line", 0)),
                    rule_id=err.get("source", ""),
                ))
    except Exception as e:
        print(f"  [WARN] [Checkstyle] XML parse error: {e}", file=sys.stderr)
    return findings


# ─── PMD XML Parser ───────────────────────────────────────────────────────────
def parse_pmd_xml(fpath: str) -> list:
    findings = []
    try:
        tree = ET.parse(fpath)
        root = tree.getroot()
        ns = {"pmd": "http://pmd.sourceforge.net/report/2.0.0"}
        for file_el in root.findall(".//file") or root.findall(".//pmd:file", ns):
            fname = file_el.get("name", "")
            for viol in file_el.findall("violation") or file_el.findall("pmd:violation", ns):
                sev_num = int(viol.get("priority", "3"))
                if sev_num <= 1:   sev = "HIGH"
                elif sev_num <= 2: sev = "MEDIUM"
                else:              sev = "LOW"
                findings.append(make_finding(
                    tool="PMD",
                    title=viol.get("rule", "PMD Rule"),
                    description=(viol.text or "")[:500].strip(),
                    severity=sev,
                    category="Code Quality",
                    file=fname,
                    line=int(viol.get("beginline", 0)),
                    rule_id=viol.get("rule", ""),
                ))
    except Exception as e:
        print(f"  [WARN] [PMD] XML parse error: {e}", file=sys.stderr)
    return findings


# ─── JUnit XML Parser (for counts) ────────────────────────────────────────────
def parse_junit_xml(base_dir: str) -> dict:
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for fpath in glob.glob(os.path.join(base_dir, "*.xml")):
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
            for ts in root.iter("testsuite"):
                totals["tests"]    += int(ts.get("tests",    0))
                totals["failures"] += int(ts.get("failures", 0))
                totals["errors"]   += int(ts.get("errors",   0))
                totals["skipped"]  += int(ts.get("skipped",  0))
        except Exception:
            pass
    return totals


# ─── JaCoCo XML Parser (for coverage %) ───────────────────────────────────────
def parse_jacoco_xml(fpath: str) -> dict:
    result = {"line_covered": 0, "line_missed": 0, "branch_covered": 0,
              "branch_missed": 0, "method_covered": 0, "method_missed": 0}
    if not os.path.exists(fpath):
        return result
    try:
        tree = ET.parse(fpath)
        root = tree.getroot()
        for counter in root.findall("counter"):
            ctype   = counter.get("type", "").lower()
            covered = int(counter.get("covered", 0))
            missed  = int(counter.get("missed", 0))
            if ctype == "line":
                result["line_covered"] = covered
                result["line_missed"]  = missed
            elif ctype == "branch":
                result["branch_covered"] = covered
                result["branch_missed"]  = missed
            elif ctype == "method":
                result["method_covered"] = covered
                result["method_missed"]  = missed
    except Exception as e:
        print(f"  [WARN] [JaCoCo] XML parse error: {e}", file=sys.stderr)
    return result


# ─── SBOM Summary ────────────────────────────────────────────────────────────
def parse_sbom_summary(fpath: str, fmt: str) -> dict:
    result = {"format": fmt, "component_count": 0}
    if not os.path.exists(fpath):
        return result
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        if fmt == "cyclonedx":
            result["component_count"] = len(data.get("components", []))
            result["bom_version"]     = data.get("version", "")
            result["spec_version"]    = data.get("specVersion", "")
        elif fmt == "spdx":
            result["component_count"] = len(data.get("packages", []))
            result["spdx_version"]    = data.get("spdxVersion", "")
    except Exception as e:
        print(f"  [WARN] [SBOM-{fmt}] parse error: {e}", file=sys.stderr)
    return result


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    args     = parse_args()
    base     = args.reports_dir
    out_path = args.output
    sonar_enabled = args.sonar_enabled.lower() == "true"

    print(f"[merge-reports] Scanning: {base}")
    print(f"[merge-reports] Output:   {out_path}")

    all_findings: list = []

    # ── Gitleaks ──────────────────────────────────────────────────────────────
    gl_path = os.path.join(base, "gitleaks", "gitleaks-report.json")
    if os.path.exists(gl_path):
        ff = parse_gitleaks(gl_path)
        print(f"  Gitleaks:      {len(ff)} findings")
        all_findings.extend(ff)

    # ── Semgrep ───────────────────────────────────────────────────────────────
    sg_json = os.path.join(base, "semgrep", "semgrep.json")
    sg_sarif = os.path.join(base, "semgrep", "semgrep.sarif")
    if os.path.exists(sg_json):
        ff = parse_semgrep_json(sg_json)
        print(f"  Semgrep JSON:  {len(ff)} findings")
        all_findings.extend(ff)
    elif os.path.exists(sg_sarif):
        ff = parse_sarif(sg_sarif, "Semgrep")
        print(f"  Semgrep SARIF: {len(ff)} findings")
        all_findings.extend(ff)

    # ── CodeQL ────────────────────────────────────────────────────────────────
    codeql_dir = os.path.join(base, "codeql")
    codeql_findings = []
    for sarif_file in glob.glob(os.path.join(codeql_dir, "*.sarif")):
        codeql_findings.extend(parse_sarif(sarif_file, "CodeQL"))
    print(f"  CodeQL:        {len(codeql_findings)} findings")
    all_findings.extend(codeql_findings)

    # ── OWASP Dependency-Check ────────────────────────────────────────────────
    dc_json = os.path.join(base, "dependency-check", "dependency-check-report.json")
    if os.path.exists(dc_json):
        ff = parse_depcheck_json(dc_json)
        print(f"  DepCheck:      {len(ff)} findings")
        all_findings.extend(ff)

    # ── Trivy ─────────────────────────────────────────────────────────────────
    trivy_json = os.path.join(base, "trivy", "trivy.json")
    trivy_sarif = os.path.join(base, "trivy", "trivy.sarif")
    if os.path.exists(trivy_json):
        ff = parse_trivy_json(trivy_json)
        print(f"  Trivy JSON:    {len(ff)} findings")
        all_findings.extend(ff)
    elif os.path.exists(trivy_sarif):
        ff = parse_sarif(trivy_sarif, "Trivy")
        print(f"  Trivy SARIF:   {len(ff)} findings")
        all_findings.extend(ff)

    # ── SpotBugs ──────────────────────────────────────────────────────────────
    sb_xml = os.path.join(base, "spotbugs", "spotbugsXml.xml")
    if os.path.exists(sb_xml):
        ff = parse_spotbugs_xml(sb_xml)
        print(f"  SpotBugs:      {len(ff)} findings")
        all_findings.extend(ff)

    # ── Checkstyle ────────────────────────────────────────────────────────────
    cs_xml = os.path.join(base, "checkstyle", "checkstyle-result.xml")
    if os.path.exists(cs_xml):
        ff = parse_checkstyle_xml(cs_xml)
        print(f"  Checkstyle:    {len(ff)} findings")
        all_findings.extend(ff)

    # ── PMD ───────────────────────────────────────────────────────────────────
    pmd_xml = os.path.join(base, "pmd", "pmd.xml")
    if os.path.exists(pmd_xml):
        ff = parse_pmd_xml(pmd_xml)
        print(f"  PMD:           {len(ff)} findings")
        all_findings.extend(ff)

    # ── JUnit ─────────────────────────────────────────────────────────────────
    junit_dir = os.path.join(base, "junit")
    junit_counts = parse_junit_xml(junit_dir)
    print(f"  JUnit:         {junit_counts['tests']} tests | "
          f"{junit_counts['failures']} failures | {junit_counts['errors']} errors")

    # ── JaCoCo ────────────────────────────────────────────────────────────────
    jacoco_xml = os.path.join(base, "jacoco", "jacoco.xml")
    jacoco = parse_jacoco_xml(jacoco_xml)
    line_total = jacoco["line_covered"] + jacoco["line_missed"]
    line_pct   = round(jacoco["line_covered"] * 100 / max(1, line_total), 1)
    print(f"  JaCoCo:        {line_pct}% line coverage")

    # ── SonarQube ─────────────────────────────────────────────────────────────
    sonar_status_path = os.path.join(base, "sonar", "sonar-status.json")
    sonar_status = {"status": "NOT_CONFIGURED"}
    if sonar_enabled and os.path.exists(sonar_status_path):
        try:
            with open(sonar_status_path) as f:
                sonar_status = json.load(f)
        except Exception:
            pass
    elif not sonar_enabled:
        sonar_status = {"status": "SKIPPED", "reason": "SONAR_ENABLED=false"}

    # ── SBOM Summaries ────────────────────────────────────────────────────────
    sbom_cdx  = parse_sbom_summary(os.path.join(base, "sbom", "sbom-cyclonedx.json"), "cyclonedx")
    sbom_spdx = parse_sbom_summary(os.path.join(base, "sbom", "sbom-spdx.json"), "spdx")

    # ── Count Severities ──────────────────────────────────────────────────────
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in all_findings:
        counts[f.get("severity", "INFO")] = counts.get(f.get("severity", "INFO"), 0) + 1

    # ── Build Merged Output ───────────────────────────────────────────────────
    merged = {
        "meta": {
            "generated_at":    datetime.now(timezone.utc).isoformat(),
            "tool":            "PragatiX DevSecOps Report Merger v1.0",
            "total_findings":  len(all_findings),
            "sonar_enabled":   sonar_enabled,
        },
        "summary": {
            "severity_counts":  counts,
            "secrets_found":    counts.get("CRITICAL", 0) > 0 and
                                any(f["tool"] == "Gitleaks" for f in all_findings),
            "critical_vulns":   counts.get("CRITICAL", 0),
            "high_vulns":       counts.get("HIGH", 0),
            "medium_vulns":     counts.get("MEDIUM", 0),
            "low_vulns":        counts.get("LOW", 0),
        },
        "coverage": {
            **jacoco,
            "line_pct":     line_pct,
            "branch_pct":   round(jacoco["branch_covered"] * 100 / max(1, jacoco["branch_covered"] + jacoco["branch_missed"]), 1),
            "method_pct":   round(jacoco["method_covered"] * 100 / max(1, jacoco["method_covered"] + jacoco["method_missed"]), 1),
        },
        "tests":   junit_counts,
        "sonar":   sonar_status,
        "sbom": {
            "cyclonedx": sbom_cdx,
            "spdx":      sbom_spdx,
        },
        "findings": all_findings,
    }

    # ── Write Output ──────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)

    print(f"\n[merge-reports] DONE: Merged {len(all_findings)} findings -> {out_path}")
    print(f"[merge-reports] Severity: CRITICAL={counts['CRITICAL']} | HIGH={counts['HIGH']} | "
          f"MEDIUM={counts['MEDIUM']} | LOW={counts['LOW']} | INFO={counts['INFO']}")


if __name__ == "__main__":
    main()
