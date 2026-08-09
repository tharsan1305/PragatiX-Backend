"""
SQL Security Scanner - Main CLI Entry Point

Usage:
    python scan.py [--source <path>] [--output <path>]

Scans a SQL Server dump directory for security, performance, schema,
data quality, best practices, and maintainability issues.
Generates an interactive HTML report.
"""
import os
import sys
import time
import argparse
import logging
from collections import Counter

from file_discovery import discover_sql_files, print_discovery_summary, count_lines
from sql_parser import SqlParser, parse_all_files
from rule_engine import RuleEngine, Severity
from scoring import calculate_scores
from report_generator import ReportGenerator

logging.getLogger('sqlglot').setLevel(logging.CRITICAL)


def parse_args():
    parser = argparse.ArgumentParser(
        description='SQL Security Scanner - Analyzes SQL Server dump projects')
    parser.add_argument('--source', '-s', type=str,
                        default=r'N:\pragatiX\Sql_Dump\PragatiX-SQL.dump',
                        help='Path to SQL dump directory')
    parser.add_argument('--output', '-o', type=str,
                        default=r'N:\pragatiX\Backend\PragatiX-Security-HTML\Report',
                        help='Output directory for the report')
    return parser.parse_args()


def main():
    start_time = time.time()
    args = parse_args()
    
    source_path = os.path.abspath(args.source)
    output_path = os.path.abspath(args.output)
    
    print("\n" + "="*70)
    print("  SQL SECURITY SCANNER")
    print("="*70)
    print(f"  Source: {source_path}")
    print(f"  Output: {output_path}")
    print("="*70)
    
    if not os.path.isdir(source_path):
        print(f"\n[ERROR] Source directory not found: {source_path}")
        sys.exit(1)
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # STEP 1: File discovery
    print("\n[STEP 1] Discovering SQL files...")
    sql_files = discover_sql_files(source_path)
    
    if not sql_files:
        print("[ERROR] No SQL files found in the source directory.")
        sys.exit(1)
    
    for f in sql_files:
        f.line_count = count_lines(f.path)
    
    print_discovery_summary(sql_files)
    
    # STEP 2: SQL Parsing
    print("[STEP 2] Parsing SQL statements...")
    parser = SqlParser(dialect='mysql')
    statements = parse_all_files(sql_files, parser)
    print(f"  Parsed {len(statements)} statements from {len(sql_files)} files")
    
    # Count statement types
    type_counts = Counter(s.type.value for s in statements)
    for t, c in type_counts.most_common():
        print(f"    {t}: {c}")
    
    # STEP 3: Analysis
    print("\n[STEP 3] Running analysis rules...")
    rule_engine = RuleEngine()
    findings = rule_engine.analyze(statements)
    
    severity_counts = Counter(f.severity.value for f in findings)
    category_counts = Counter(f.category.value for f in findings)
    
    print(f"  Total findings: {len(findings)}")
    for severity in ['Critical', 'High', 'Medium', 'Low', 'Info']:
        print(f"    {severity}: {severity_counts.get(severity, 0)}")
    print("  By category:")
    for cat, count in category_counts.most_common():
        print(f"    {cat}: {count}")
    
    # STEP 4: Scoring
    print("\n[STEP 4] Computing scores...")
    scores = calculate_scores(findings, statements)
    print(f"  Security Score:    {scores.security_score:.1f}/100")
    print(f"  Performance Score: {scores.performance_score:.1f}/100")
    print(f"  Quality Score:     {scores.quality_score:.1f}/100")
    
    # STEP 5: Report generation
    print("\n[STEP 5] Generating report...")
    file_stats = {
        'source_path': source_path,
        'total_files': len(sql_files),
        'total_size': sum(f.size for f in sql_files),
        'total_lines': sum(f.line_count for f in sql_files),
    }
    
    generator = ReportGenerator(output_path)
    generated = generator.generate(findings, statements, scores, file_stats)
    
    print(f"\n{'='*70}")
    print("  REPORT GENERATED SUCCESSFULLY")
    print(f"{'='*70}")
    for name, path in generated.items():
        print(f"  {name.upper()}: {path}")
    print(f"{'='*70}")
    
    elapsed = time.time() - start_time
    print(f"\n  Scan completed in {elapsed:.2f} seconds")
    print(f"  Files scanned: {len(sql_files)}")
    print(f"  Statements parsed: {len(statements)}")
    print(f"  Total findings: {len(findings)}")
    print(f"    Critical: {severity_counts.get('Critical', 0)}")
    print(f"    High:     {severity_counts.get('High', 0)}")
    print(f"    Medium:   {severity_counts.get('Medium', 0)}")
    print(f"    Low:      {severity_counts.get('Low', 0)}")
    print(f"    Info:     {severity_counts.get('Info', 0)}")
    print(f"\n  Report: {os.path.join(output_path, 'Security_Report.html')}")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()