"""
Report Generator Module
Generates the interactive HTML security report with Bootstrap 5, Chart.js, and DataTables.
"""
import json
import os
import html as html_lib
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Any
from rule_engine import Finding, Severity, Category
from scoring import OverallScores, get_score_grade, get_score_color
from sql_parser import ParsedStatement, StatementType


class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, findings: List[Finding], statements: List[ParsedStatement],
                 scores: OverallScores, file_stats: Dict[str, Any]) -> Dict[str, str]:
        """Generate all report files."""
        self._prepare_data(findings, statements, scores, file_stats)
        
        paths = {}
        paths['html'] = self._generate_html()
        paths['css'] = self._generate_css()
        paths['js'] = self._generate_js()
        paths['charts_js'] = self._generate_charts_js()
        paths['findings_json'] = self._generate_findings_json()
        paths['summary_json'] = self._generate_summary_json()
        
        return paths
    
    def _prepare_data(self, findings: List[Finding], statements: List[ParsedStatement],
                      scores: OverallScores, file_stats: Dict[str, Any]) -> None:
        """Prepare all data needed for report generation."""
        self.findings = findings
        self.statements = statements
        self.scores = scores
        self.file_stats = file_stats
        
        self.total_files = file_stats.get('total_files', 0)
        self.total_queries = len(statements)
        
        self.object_counts = Counter()
        for stmt in statements:
            if stmt.object_type:
                self.object_counts[stmt.object_type] += 1
        
        self.severity_counts = Counter(f.severity.value for f in findings)
        self.category_counts = Counter(f.category.value for f in findings)
        
        self.files_with_issues = Counter(f.file_name for f in findings)
        
        self.table_scores = self._compute_table_scores()
        
        self.critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        self.high_findings = [f for f in findings if f.severity == Severity.HIGH]
        self.medium_findings = [f for f in findings if f.severity == Severity.MEDIUM]
        self.low_findings = [f for f in findings if f.severity == Severity.LOW]
        self.info_findings = [f for f in findings if f.severity == Severity.INFO]
        
        self.security_findings = [f for f in findings if f.category == Category.SECURITY]
        self.performance_findings = [f for f in findings if f.category == Category.PERFORMANCE]
        self.schema_findings = [f for f in findings if f.category == Category.SCHEMA]
        self.dq_findings = [f for f in findings if f.category == Category.DATA_QUALITY]
        self.bp_findings = [f for f in findings if f.category == Category.BEST_PRACTICES]
        self.maint_findings = [f for f in findings if f.category == Category.MAINTAINABILITY]
        
        self.tables = [s for s in statements if s.object_type == 'TABLE']
        self.views = [s for s in statements if s.object_type == 'VIEW']
        self.procedures = [s for s in statements if s.object_type in ('PROCEDURE', 'PROC')]
        self.functions = [s for s in statements if s.object_type == 'FUNCTION']
        self.triggers = [s for s in statements if s.object_type == 'TRIGGER']
    
    def _compute_table_scores(self) -> Dict[str, Dict[str, Any]]:
        """Compute risk scores per table for heatmap."""
        table_findings = defaultdict(list)
        for f in self.findings:
            if f.table:
                table_findings[f.table].append(f)
        
        result = {}
        for table, tfs in table_findings.items():
            risk_score = sum({
                Severity.CRITICAL: 25,
                Severity.HIGH: 15,
                Severity.MEDIUM: 8,
                Severity.LOW: 3,
                Severity.INFO: 1
            }.get(f.severity, 5) for f in tfs)
            result[table] = {
                'risk_score': min(risk_score, 100),
                'count': len(tfs),
                'criticals': sum(1 for f in tfs if f.severity == Severity.CRITICAL),
                'highs': sum(1 for f in tfs if f.severity == Severity.HIGH)
            }
        return dict(sorted(result.items(), key=lambda x: x[1]['risk_score'], reverse=True))
    
    def _html_escape(self, text: str) -> str:
        return html_lib.escape(str(text))
    
    def _sql_highlight(self, sql: str) -> str:
        """Highlight SQL keywords in the snippet."""
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CROSS',
                   'GROUP', 'BY', 'HAVING', 'ORDER', 'UNION', 'ALL', 'EXEC', 'EXECUTE', 'INSERT',
                   'INTO', 'UPDATE', 'DELETE', 'VALUES', 'SET', 'CREATE', 'TABLE', 'ALTER', 'DROP',
                   'INDEX', 'VIEW', 'PROCEDURE', 'PROC', 'FUNCTION', 'TRIGGER', 'AND', 'OR', 'NOT',
                   'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL', 'AS', 'ON', 'CASE', 'WHEN',
                   'THEN', 'ELSE', 'END', 'BEGIN', 'COMMIT', 'ROLLBACK', 'DECLARE', 'PRIMARY',
                   'KEY', 'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE', 'CHECK', 'DEFAULT',
                   'IDENTITY', 'CLUSTERED', 'NONCLUSTERED', 'WITH', 'TOP', 'DISTINCT', 'COUNT',
                   'SUM', 'AVG', 'MIN', 'MAX', 'OVER', 'PARTITION', 'GRANT', 'REVOKE', 'DENY']
        
        escaped = html_lib.escape(sql)
        
        def replace_keyword(match):
            return f'<span class="sql-kw">{match.group(0)}</span>'
        
        for kw in sorted(keywords, key=len, reverse=True):
            pattern = r'\b' + kw + r'\b'
            import re
            escaped = re.sub(pattern, replace_keyword, escaped, flags=re.IGNORECASE)
        
        escaped = re.sub(r'\b(\d+)\b', r'<span class="sql-num">\1</span>', escaped)
        escaped = re.sub(r"('(?:[^']|'')*')", r'<span class="sql-str">\1</span>', escaped)
        
        return escaped
    
    def _severity_badge(self, severity: str) -> str:
        colors = {
            'Critical': 'danger',
            'High': 'warning',
            'Medium': 'info',
            'Low': 'secondary',
            'Info': 'light'
        }
        return f'<span class="badge bg-{colors.get(severity, "secondary")}">{severity}</span>'
    
    def _score_circle(self, score: float, label: str) -> str:
        color = get_score_color(score)
        grade = get_score_grade(score)
        return f'''
        <div class="score-circle-wrap text-center">
            <div class="score-circle bg-{color}">
                <div class="score-value">{score:.1f}</div>
                <div class="score-grade">{grade}</div>
            </div>
            <div class="score-label mt-2">{label}</div>
        </div>'''
    
    def _findings_table(self, findings_list: List[Finding], section_id: str) -> str:
        if not findings_list:
            return '<div class="alert alert-success">No findings in this category. Excellent!</div>'
        
        rows = []
        for f in findings_list:
            obj_name = f.object_name or f.table or '-'
            rows.append(f'''
            <tr>
                <td>{self._severity_badge(f.severity.value)}</td>
                <td><span class="badge bg-primary">{f.category.value}</span></td>
                <td class="text-monospace">{self._html_escape(obj_name)}</td>
                <td>{self._html_escape(f.object_type or '-')}</td>
                <td class="text-monospace small">{self._html_escape(f.file_name)}</td>
                <td>{f.line_number}</td>
                <td>{self._html_escape(f.issue_title)}</td>
                <td class="expander-cell"><button class="btn btn-sm btn-outline-info expand-btn" data-target="row-{id(f)}">View</button></td>
            </tr>
            <tr class="finding-detail" id="row-{id(f)}" style="display:none">
                <td colspan="8">
                    <div class="finding-meta mb-2">
                        <strong>Rule:</strong> <code>{f.rule_id}</code> |
                        <strong>Impact:</strong> {self._html_escape(f.impact)} |
                        <strong>Risk:</strong> {self._html_escape(f.risk)}
                    </div>
                    <div class="mb-2"><strong>Description:</strong> {self._html_escape(f.description)}</div>
                    <div class="mb-2"><strong>Recommendation:</strong> {self._html_escape(f.recommendation)}</div>
                    <div class="mb-2"><strong>Reference:</strong> {self._html_escape(f.best_practice_ref)}</div>
                    <div class="sql-block"><pre><code>{self._sql_highlight(f.sql_snippet)}</code></pre></div>
                </td>
            </tr>
            ''')
        
        return f'''
        <table class="table table-dark table-hover findings-table" id="table-{section_id}">
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Category</th>
                    <th>Object</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Issue</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>{''.join(rows)}</tbody>
        </table>'''
    
    def _generate_html(self) -> str:
        """Generate the main HTML report."""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        severity_counts_json = json.dumps({k: v for k, v in self.severity_counts.items()})
        category_counts_json = json.dumps({k: v for k, v in self.category_counts.items()})
        object_counts_json = json.dumps({k: v for k, v in self.object_counts.items()})
        table_risk_json = json.dumps({k: v['risk_score'] for k, v in self.table_scores.items()})
        files_issues_json = json.dumps({k: v for k, v in self.files_with_issues.most_common(15)})
        
        summary_cards = self._build_summary_cards()
        object_analysis = self._build_object_analysis()
        recommendations = self._build_recommendations()
        
        html_content = f'''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Security Scanner Report - PragatiX Database</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.bootstrap5.min.css" rel="stylesheet">
    <link rel="stylesheet" href="report.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow">
    <div class="container-fluid">
        <a class="navbar-brand" href="#"><i class="bi bi-shield-check"></i> SQL Security Scanner</a>
        <span class="navbar-text text-muted">PragatiX Database Security Audit</span>
        <span class="badge bg-success ms-auto">Report Generated: {now}</span>
    </div>
</nav>

<div class="container-fluid">
    <div class="row">
        <!-- Sidebar -->
        <nav class="col-md-3 col-lg-2 d-md-block sidebar bg-dark">
            <div class="position-sticky pt-3">
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link" href="#dashboard"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="#summary"><i class="bi bi-clipboard-data"></i> Executive Summary</a></li>
                    <li class="nav-item"><a class="nav-link" href="#security"><i class="bi bi-shield-exclamation"></i> Security Findings</a></li>
                    <li class="nav-item"><a class="nav-link" href="#performance"><i class="bi bi-lightning"></i> Performance Findings</a></li>
                    <li class="nav-item"><a class="nav-link" href="#schema"><i class="bi bi-diagram-3"></i> Schema Findings</a></li>
                    <li class="nav-item"><a class="nav-link" href="#data-quality"><i class="bi bi-database-check"></i> Data Quality</a></li>
                    <li class="nav-item"><a class="nav-link" href="#best-practices"><i class="bi bi-check2-square"></i> Best Practices</a></li>
                    <li class="nav-item"><a class="nav-link" href="#maintainability"><i class="bi bi-tools"></i> Maintainability</a></li>
                    <li class="nav-item"><a class="nav-link" href="#objects"><i class="bi bi-boxes"></i> Object Analysis</a></li>
                    <li class="nav-item"><a class="nav-link" href="#recommendations"><i class="bi bi-lightbulb"></i> Recommendations</a></li>
                    <li class="nav-item"><a class="nav-link" href="#appendix"><i class="bi bi-list-check"></i> Appendix</a></li>
                </ul>
            </div>
        </nav>

        <!-- Main Content -->
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
            <!-- Dashboard -->
            <div id="dashboard" class="section py-4">
                <h1 class="display-6 mb-4">SQL Security Scanner Report</h1>
                
                <div class="row g-3 mb-4">
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-primary">
                            <div class="card-body">
                                <h6 class="card-title">SQL Files</h6>
                                <h2 class="card-text">{self.total_files}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-info">
                            <div class="card-body">
                                <h6 class="card-title">Tables</h6>
                                <h2 class="card-text">{self.object_counts.get('TABLE', 0)}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-success">
                            <div class="card-body">
                                <h6 class="card-title">Total Queries</h6>
                                <h2 class="card-text">{self.total_queries}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-warning">
                            <div class="card-body">
                                <h6 class="card-title">Total Findings</h6>
                                <h2 class="card-text">{len(self.findings)}</h2>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mb-4">
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-danger">
                            <div class="card-body">
                                <h6 class="card-title">Critical Issues</h6>
                                <h2 class="card-text">{self.severity_counts.get('Critical', 0)}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-orange">
                            <div class="card-body">
                                <h6 class="card-title">High Issues</h6>
                                <h2 class="card-text">{self.severity_counts.get('High', 0)}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-cyan">
                            <div class="card-body">
                                <h6 class="card-title">Medium Issues</h6>
                                <h2 class="card-text">{self.severity_counts.get('Medium', 0)}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3">
                        <div class="card stat-card bg-secondary">
                            <div class="card-body">
                                <h6 class="card-title">Low/Info</h6>
                                <h2 class="card-text">{self.severity_counts.get('Low', 0) + self.severity_counts.get('Info', 0)}</h2>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card score-card">
                            <div class="card-header bg-dark"><h5 class="mb-0">Overall Scores</h5></div>
                            <div class="card-body d-flex justify-content-around flex-wrap">
                                {self._score_circle(self.scores.security_score, "Security Score")}
                                {self._score_circle(self.scores.performance_score, "Performance Score")}
                                {self._score_circle(self.scores.quality_score, "Quality Score")}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="card chart-card">
                            <div class="card-header"><h6 class="mb-0">Issues by Severity</h6></div>
                            <div class="card-body"><canvas id="severityChart"></canvas></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card chart-card">
                            <div class="card-header"><h6 class="mb-0">Issues by Category</h6></div>
                            <div class="card-body"><canvas id="categoryChart"></canvas></div>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mt-1">
                    <div class="col-md-6">
                        <div class="card chart-card">
                            <div class="card-header"><h6 class="mb-0">Object Types</h6></div>
                            <div class="card-body"><canvas id="objectChart"></canvas></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card chart-card">
                            <div class="card-header"><h6 class="mb-0">Top Risk Tables (Heatmap)</h6></div>
                            <div class="card-body"><canvas id="heatmapChart"></canvas></div>
                        </div>
                    </div>
                </div>

                <div class="row g-3 mt-1">
                    <div class="col-12">
                        <div class="card chart-card">
                            <div class="card-header"><h6 class="mb-0">Files vs Issues</h6></div>
                            <div class="card-body"><canvas id="filesChart"></canvas></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Executive Summary -->
            <div id="summary" class="section py-4">
                <h2 class="mb-4">Executive Summary</h2>
                <div class="card">
                    <div class="card-body">
                        <p>This report presents the findings of a static security analysis of the <strong>PragatiX</strong> SQL Server database dump. A total of <strong>{self.total_files}</strong> SQL files were analyzed, containing <strong>{self.total_queries}</strong> parsed statements.</p>
                        
                        <h5>Key Statistics</h5>
                        <ul>
                            <li><strong>{self.object_counts.get('TABLE', 0)}</strong> tables analyzed</li>
                            <li><strong>{self.object_counts.get('VIEW', 0)}</strong> views</li>
                            <li><strong>{self.object_counts.get('PROCEDURE', 0) + self.object_counts.get('PROC', 0)}</strong> stored procedures</li>
                            <li><strong>{self.object_counts.get('FUNCTION', 0)}</strong> functions</li>
                            <li><strong>{self.object_counts.get('TRIGGER', 0)}</strong> triggers</li>
                        </ul>
                        
                        <h5>Findings Overview</h5>
                        <div class="table-responsive">
                            <table class="table table-dark table-sm">
                                <thead><tr><th>Severity</th><th>Count</th></tr></thead>
                                <tbody>
                                    <tr><td>{self._severity_badge('Critical')}</td><td>{self.severity_counts.get('Critical', 0)}</td></tr>
                                    <tr><td>{self._severity_badge('High')}</td><td>{self.severity_counts.get('High', 0)}</td></tr>
                                    <tr><td>{self._severity_badge('Medium')}</td><td>{self.severity_counts.get('Medium', 0)}</td></tr>
                                    <tr><td>{self._severity_badge('Low')}</td><td>{self.severity_counts.get('Low', 0)}</td></tr>
                                    <tr><td>{self._severity_badge('Info')}</td><td>{self.severity_counts.get('Info', 0)}</td></tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <h5>Score Grades</h5>
                        <div class="table-responsive">
                            <table class="table table-dark table-sm">
                                <thead><tr><th>Metric</th><th>Score</th><th>Grade</th></tr></thead>
                                <tbody>
                                    <tr><td>Security</td><td>{self.scores.security_score:.1f}/100</td><td>{get_score_grade(self.scores.security_score)}</td></tr>
                                    <tr><td>Performance</td><td>{self.scores.performance_score:.1f}/100</td><td>{get_score_grade(self.scores.performance_score)}</td></tr>
                                    <tr><td>Quality</td><td>{self.scores.quality_score:.1f}/100</td><td>{get_score_grade(self.scores.quality_score)}</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Security Findings -->
            <div id="security" class="section py-4">
                <h2 class="mb-1">Security Findings</h2>
                <p class="text-muted">{len(self.security_findings)} findings - {self.severity_counts.get('Critical', 0)} critical, {self.severity_counts.get('High', 0)} high</p>
                {self._findings_table(self.security_findings, 'security')}
            </div>

            <!-- Performance Findings -->
            <div id="performance" class="section py-4">
                <h2 class="mb-1">Performance Findings</h2>
                <p class="text-muted">{len(self.performance_findings)} findings</p>
                {self._findings_table(self.performance_findings, 'performance')}
            </div>

            <!-- Schema Findings -->
            <div id="schema" class="section py-4">
                <h2 class="mb-1">Schema Design Findings</h2>
                <p class="text-muted">{len(self.schema_findings)} findings</p>
                {self._findings_table(self.schema_findings, 'schema')}
            </div>

            <!-- Data Quality -->
            <div id="data-quality" class="section py-4">
                <h2 class="mb-1">Data Quality Findings</h2>
                <p class="text-muted">{len(self.dq_findings)} findings</p>
                {self._findings_table(self.dq_findings, 'dq')}
            </div>

            <!-- Best Practices -->
            <div id="best-practices" class="section py-4">
                <h2 class="mb-1">Best Practices Findings</h2>
                <p class="text-muted">{len(self.bp_findings)} findings</p>
                {self._findings_table(self.bp_findings, 'bp')}
            </div>

            <!-- Maintainability -->
            <div id="maintainability" class="section py-4">
                <h2 class="mb-1">Maintainability Findings</h2>
                <p class="text-muted">{len(self.maint_findings)} findings</p>
                {self._findings_table(self.maint_findings, 'maint')}
            </div>

            <!-- Object Analysis -->
            <div id="objects" class="section py-4">
                <h2 class="mb-4">Object Analysis</h2>
                {object_analysis}
            </div>

            <!-- Recommendations -->
            <div id="recommendations" class="section py-4">
                <h2 class="mb-4">Recommendations</h2>
                {recommendations}
            </div>

            <!-- Appendix -->
            <div id="appendix" class="section py-4">
                <h2 class="mb-4">Appendix - All Findings</h2>
                {self._findings_table(self.findings, 'appendix')}
            </div>

            <footer class="py-3 text-center text-muted">
                Generated by SQL Security Scanner at {now} | PragatiX Database Audit
            </footer>
        </main>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.bootstrap5.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
    window.REPORT_DATA = {{
        severity: {severity_counts_json},
        category: {category_counts_json},
        objects: {object_counts_json},
        tableRisk: {table_risk_json},
        filesIssues: {files_issues_json}
    }};
</script>
<script src="report.js"></script>
</body>
</html>'''
        
        filepath = os.path.join(self.output_dir, 'Security_Report.html')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filepath
    
    def _build_summary_cards(self) -> str:
        """Build summary statistic cards HTML."""
        cards = [
            ('SQL Files', self.total_files, 'primary'),
            ('Tables', self.object_counts.get('TABLE', 0), 'info'),
            ('Views', self.object_counts.get('VIEW', 0), 'success'),
            ('Procedures', self.object_counts.get('PROCEDURE', 0) + self.object_counts.get('PROC', 0), 'warning'),
            ('Functions', self.object_counts.get('FUNCTION', 0), 'secondary'),
            ('Triggers', self.object_counts.get('TRIGGER', 0), 'danger'),
            ('Queries', self.total_queries, 'light'),
            ('Findings', len(self.findings), 'danger'),
        ]
        html = []
        for label, value, color in cards:
            html.append(f'''
            <div class="col-6 col-md-3">
                <div class="card stat-card bg-{color}">
                    <div class="card-body">
                        <h6 class="card-title">{label}</h6>
                        <h2 class="card-text">{value}</h2>
                    </div>
                </div>
            </div>''')
        return ''.join(html)
    
    def _build_object_analysis(self) -> str:
        """Build object analysis section HTML."""
        sections = []
        
        object_groups = [
            ('Tables', self.tables),
            ('Views', self.views),
            ('Stored Procedures', self.procedures),
            ('Functions', self.functions),
            ('Triggers', self.triggers),
        ]
        
        for title, objs in object_groups:
            if not objs:
                continue
            cards = []
            for obj in objs[:200]:
                obj_key = f"{obj.object_type}:{obj.object_name}"
                score = 100
                obj_findings = [f for f in self.findings if f.object_name == obj.object_name]
                if obj_findings:
                    severity_weights = {'Critical': 25, 'High': 15, 'Medium': 8, 'Low': 3, 'Info': 1}
                    score = max(0, 100 - sum(severity_weights.get(f.severity.value, 5) for f in obj_findings))
                score_color = get_score_color(score)
                
                col_count = len(obj.columns)
                constraint_count = len(obj.constraints)
                index_count = len(obj.indexes)
                find_count = len(obj_findings)
                
                cards.append(f'''
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card object-card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 text-truncate">{self._html_escape(obj.object_name)}</h6>
                            <span class="badge bg-{score_color}">{score:.0f}</span>
                        </div>
                        <div class="card-body">
                            <div class="row text-center mb-2">
                                <div class="col-6"><small class="text-muted">Columns</small><br><strong>{col_count}</strong></div>
                                <div class="col-6"><small class="text-muted">Constraints</small><br><strong>{constraint_count}</strong></div>
                            </div>
                            <div class="row text-center mb-2">
                                <div class="col-6"><small class="text-muted">Indexes</small><br><strong>{index_count}</strong></div>
                                <div class="col-6"><small class="text-muted">Findings</small><br><strong>{find_count}</strong></div>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar bg-{score_color}" style="width: {score}%"></div>
                            </div>
                            <small class="text-muted d-block mt-1">{self._html_escape(obj.file_name)} (Line {obj.line_start})</small>
                            <button class="btn btn-sm btn-outline-info mt-2 w-100 object-detail-btn" data-obj="{id(obj)}">View Details</button>
                            <div class="object-detail" id="obj-detail-{id(obj)}" style="display:none">
                                <hr>
                                <h6 class="text-info">Columns</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm table-dark table-striped">
                                        <thead><tr><th>Column</th><th>Type</th><th>Nullable</th><th>Constraints</th></tr></thead>
                                        <tbody>
                                        {''.join(f'<tr><td>{self._html_escape(c["name"])}</td><td>{self._html_escape(c["type"])}</td><td>{"Yes" if c.get("nullable") else "No"}</td><td>{"<br>".join(self._html_escape(x) for x in c.get("constraints", [])) or "-"}</td></tr>' for c in obj.columns[:15])}
                                        </tbody>
                                    </table>
                                </div>
                                {f'<p class="text-muted small">+{len(obj.columns) - 15} more columns</p>' if len(obj.columns) > 15 else ''}
                                <h6 class="text-info">Constraints</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm table-dark table-striped">
                                        <thead><tr><th>Type</th><th>Details</th></tr></thead>
                                        <tbody>
                                        {''.join(f'<tr><td>{self._html_escape(c.get("type", ""))}</td><td>{self._html_escape(c.get("columns", c.get("expression", "-")))}</td></tr>' for c in obj.constraints[:10])}
                                        </tbody>
                                    </table>
                                </div>
                                <h6 class="text-info">Findings</h6>
                                <ul class="list-unstyled">
                                {''.join(f'<li><span class="badge bg-danger">{f.severity.value}</span> {self._html_escape(f.issue_title)}</li>' for f in obj_findings[:5])}
                                {'' if len(obj_findings) <= 5 else f'<li class="text-muted">+{len(obj_findings)-5} more...</li>'}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>''')
            
            sections.append(f'''
            <div class="mb-5">
                <h4 class="mb-3">{title} ({len(objs)})</h4>
                <div class="row">{''.join(cards)}</div>
            </div>''')
        
        return ''.join(sections)
    
    def _build_recommendations(self) -> str:
        """Build recommendations section HTML."""
        recs = []
        
        if self.severity_counts.get('Critical', 0) > 0:
            recs.append(('Critical Issues',
                f'There are <strong>{self.severity_counts.get("Critical", 0)} critical findings</strong> that require immediate attention. Review each critical finding in the Security section and remediate them before deployment.',
                'danger'))
        
        if self.severity_counts.get('High', 0) > 0:
            recs.append(('High Priority',
                f'<strong>{self.severity_counts.get("High", 0)} high-severity findings</strong> should be addressed within the next sprint cycle.',
                'warning'))
        
        sec_recs = self._build_category_recommendations(self.security_findings, 'Security',
            ['parameterized queries', 'secure secret storage', 'principle of least privilege'])
        if sec_recs:
            recs.append(('Security', sec_recs, 'danger'))
        
        perf_recs = self._build_category_recommendations(self.performance_findings, 'Performance',
            ['index optimization', 'set-based operations', 'proper transaction management'])
        if perf_recs:
            recs.append(('Performance', perf_recs, 'warning'))
        
        schema_recs = self._build_category_recommendations(self.schema_findings, 'Schema Design',
            ['primary key enforcement', 'foreign key constraints', 'appropriate data types'])
        if schema_recs:
            recs.append(('Schema Design', schema_recs, 'info'))
        
        dq_recs = self._build_category_recommendations(self.dq_findings, 'Data Quality',
            ['input validation', 'data deduplication', 'format standardization'])
        if dq_recs:
            recs.append(('Data Quality', dq_recs, 'secondary'))
        
        recs_html = []
        for i, (title, text, color) in enumerate(recs, 1):
            recs_html.append(f'''
            <div class="card recommendation-card mb-3 border-{color}">
                <div class="card-header bg-{color}">
                    <h5 class="mb-0"><span class="badge bg-dark me-2">{i}</span>{title}</h5>
                </div>
                <div class="card-body">{text}</div>
            </div>''')
        
        recs_html.append('''
        <div class="card recommendation-card mb-3 border-success">
            <div class="card-header bg-success">
                <h5 class="mb-0">Next Steps</h5>
            </div>
            <div class="card-body">
                <ol class="mb-0">
                    <li><strong>Remediate Critical and High findings</strong> first - these pose the greatest risk to the application</li>
                    <li><strong>Establish parameterized queries</strong> across all database access to prevent SQL injection</li>
                    <li><strong>Move all credentials and secrets</strong> out of source code and into secure configuration stores</li>
                    <li><strong>Add proper indexing strategy</strong> based on the performance findings</li>
                    <li><strong>Enforce schema standards</strong> with PRIMARY KEY, FOREIGN KEY, and CHECK constraints</li>
                    <li><strong>Re-run this scanner</strong> after remediation to verify improvements</li>
                </ol>
            </div>
        </div>''')
        
        return ''.join(recs_html)
    
    def _build_category_recommendations(self, findings_list: List[Finding], category: str, common_advice: List[str]) -> str:
        """Build recommendations for a category based on findings."""
        if not findings_list:
            return f'<p>No {category} findings detected. Excellent job!</p>'
        
        unique_issues = list(dict.fromkeys(f.issue_title for f in findings_list))
        items = [f'<li><strong>{self._html_escape(issue)}</strong> - review all occurrences</li>' for issue in unique_issues[:8]]
        
        return f'''
        <ul class="mb-2">{''.join(items)}</ul>
        <p><strong>Recommended actions:</strong></p>
        <ul>{''.join(f'<li>{advice}</li>' for advice in common_advice)}</ul>'''
    
    def _generate_css(self) -> str:
        """Generate the report CSS file."""
        css = '''/* SQL Security Scanner Report Styles - Dark Theme */
:root {
    --bs-body-bg: #0d1117;
    --bs-body-color: #c9d1d9;
    --sidebar-width: 220px;
    --card-bg: #161b22;
    --card-border: #30363d;
    --accent: #58a6ff;
    --danger: #f85149;
    --warning: #d29922;
    --success: #3fb950;
}

body {
    background-color: var(--bs-body-bg);
    color: var(--bs-body-color);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Sidebar */
.sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 100;
    padding-top: 60px;
    box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
    background-color: #161b22 !important;
    width: 220px;
    overflow-y: auto;
}

.sidebar .nav-link {
    color: #8b949e;
    padding: 0.6rem 1rem;
    border-radius: 6px;
    margin: 2px 8px;
    transition: all 0.2s;
}

.sidebar .nav-link:hover {
    color: var(--accent);
    background-color: #21262d;
}

.sidebar .nav-link.active {
    color: var(--accent);
    background-color: rgba(88, 166, 255, 0.1);
}

main {
    margin-left: 220px;
    padding-left: 2rem;
    padding-right: 2rem;
}

@media (max-width: 768px) {
    .sidebar { display: none; }
    main { margin-left: 0; }
}

/* Stat Cards */
.stat-card {
    border: none;
    border-radius: 10px;
    color: #fff;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.stat-card .card-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.85;
}

.stat-card .card-text {
    font-weight: 700;
    font-size: 2rem;
}

.bg-orange { background-color: #f0883e !important; }
.bg-cyan { background-color: #39c5cf !important; }

/* Score Circles */
.score-circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}

.score-value {
    font-size: 1.8rem;
    font-weight: 700;
}

.score-grade {
    font-size: 1.2rem;
    font-weight: 600;
    opacity: 0.9;
}

.score-label {
    font-weight: 600;
    color: #8b949e;
}

/* Cards */
.card {
    background-color: var(--card-bg);
    border-color: var(--card-border);
}

.chart-card, .object-card {
    border: 1px solid var(--card-border);
    border-radius: 10px;
}

.chart-card .card-header, .object-card .card-header {
    background-color: #21262d;
    border-bottom: 1px solid var(--card-border);
    border-radius: 10px 10px 0 0;
}

/* Tables */
.table-dark {
    --bs-table-bg: #161b22;
    --bs-table-border-color: #30363d;
}

.findings-table thead th {
    background-color: #21262d;
    color: var(--accent);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: sticky;
    top: 60px;
    z-index: 10;
}

.findings-table td {
    vertical-align: middle;
    font-size: 0.9rem;
}

.dataTables_wrapper .dataTables_filter input,
.dataTables_wrapper .dataTables_length select {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid var(--card-border);
    border-radius: 6px;
}

/* SQL Highlighting */
.sql-block {
    background-color: #0d1117;
    border: 1px solid var(--card-border);
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
}

.sql-block pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
}

.sql-kw { color: #ff7b72; font-weight: 600; }
.sql-str { color: #a5d6ff; }
.sql-num { color: #79c0ff; }
.sql-com { color: #8b949e; font-style: italic; }

/* Finding Detail */
.finding-detail {
    background-color: #0d1117 !important;
}

.finding-detail td {
    background-color: #0d1117;
    border-top: none !important;
}

.expander-cell {
    width: 60px;
}

/* Object Cards */
.object-card .card-body {
    font-size: 0.85rem;
}

.object-card .progress {
    background-color: #21262d;
}

.object-detail {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--card-border);
}

/* Recommendation Cards */
.recommendation-card {
    border-width: 2px;
}

.recommendation-card .card-header {
    color: #fff;
    border-bottom: none;
}

/* Sections */
.section {
    border-bottom: 1px solid var(--card-border);
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.section h2 {
    color: var(--accent);
    font-weight: 600;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0d1117;
}

::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #484f58;
}

/* Badge */
.badge.bg-light {
    color: #0d1117;
}
'''
        filepath = os.path.join(self.output_dir, 'report.css')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(css)
        return filepath
    
    def _generate_js(self) -> str:
        """Generate the report JS file."""
        js = '''// SQL Security Scanner Report JavaScript
(function() {
    'use strict';

    const DATA = window.REPORT_DATA || {};

    // Charts
    function initCharts() {
        const isDark = true;
        const textColor = '#c9d1d9';
        const gridColor = 'rgba(140, 149, 159, 0.1)';

        const commonOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: textColor, font: { size: 11 } }
                }
            },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } }
            }
        };

        // Severity Pie Chart
        const severityEl = document.getElementById('severityChart');
        if (severityEl && Object.keys(DATA.severity || {}).length) {
            const severityData = DATA.severity;
            const order = ['Critical', 'High', 'Medium', 'Low', 'Info'];
            const labels = order.filter(s => severityData[s]);
            const colors = {
                'Critical': '#f85149',
                'High': '#f0883e',
                'Medium': '#39c5cf',
                'Low': '#8b949e',
                'Info': '#58a6ff'
            };
            new Chart(severityEl, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: labels.map(l => severityData[l]),
                        backgroundColor: labels.map(l => colors[l] || '#58a6ff')
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: textColor, font: { size: 11 } }
                        }
                    }
                }
            });
        }

        // Category Bar Chart
        const categoryEl = document.getElementById('categoryChart');
        if (categoryEl && Object.keys(DATA.category || {}).length) {
            const categoryData = DATA.category;
            new Chart(categoryEl, {
                type: 'bar',
                data: {
                    labels: Object.keys(categoryData),
                    datasets: [{
                        label: 'Findings',
                        data: Object.values(categoryData),
                        backgroundColor: ['#f85149', '#d29922', '#58a6ff', '#3fb950', '#8b949e', '#bc8cff'].slice(0, Object.keys(categoryData).length)
                    }]
                },
                options: commonOptions
            });
        }

        // Object Types Donut Chart
        const objectEl = document.getElementById('objectChart');
        if (objectEl && Object.keys(DATA.objects || {}).length) {
            const objectData = DATA.objects;
            new Chart(objectEl, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(objectData),
                    datasets: [{
                        data: Object.values(objectData),
                        backgroundColor: ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff', '#39c5cf', '#8b949e']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: textColor, font: { size: 11 } }
                        }
                    }
                }
            });
        }

        // Heatmap Chart (Top Risk Tables)
        const heatmapEl = document.getElementById('heatmapChart');
        if (heatmapEl && Object.keys(DATA.tableRisk || {}).length) {
            const tableRisk = DATA.tableRisk;
            const tables = Object.keys(tableRisk).slice(0, 15);
            const scores = tables.map(t => tableRisk[t]);
            const colors = scores.map(s => {
                if (s >= 80) return 'rgba(248, 81, 73, 0.85)';
                if (s >= 50) return 'rgba(242, 136, 62, 0.85)';
                if (s >= 25) return 'rgba(210, 153, 34, 0.85)';
                return 'rgba(63, 185, 80, 0.85)';
            });
            new Chart(heatmapEl, {
                type: 'bar',
                data: {
                    labels: tables,
                    datasets: [{
                        label: 'Risk Score',
                        data: scores,
                        backgroundColor: colors
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            max: 100,
                            ticks: { color: textColor },
                            grid: { color: gridColor }
                        },
                        y: {
                            ticks: {
                                color: textColor,
                                font: { size: 10 }
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        // Files vs Issues Line Chart
        const filesEl = document.getElementById('filesChart');
        if (filesEl && Object.keys(DATA.filesIssues || {}).length) {
            const filesIssues = DATA.filesIssues;
            new Chart(filesEl, {
                type: 'line',
                data: {
                    labels: Object.keys(filesIssues),
                    datasets: [{
                        label: 'Issues',
                        data: Object.values(filesIssues),
                        borderColor: '#f85149',
                        backgroundColor: 'rgba(248, 81, 73, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: commonOptions
            });
        }
    }

    // DataTables initialization
    function initDataTables() {
        document.querySelectorAll('.findings-table').forEach(function(table) {
            if (typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
                $(table).DataTable({
                    pageLength: 10,
                    responsive: true,
                    dom: '<"row mb-3"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                         '<"row"<"col-sm-12"tr>>' +
                         '<"row mt-3"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>' +
                         'Bfrtip',
                    buttons: [
                        { extend: 'csv', text: 'Export CSV', className: 'btn btn-sm btn-outline-info me-1' },
                        { extend: 'excel', text: 'Export Excel', className: 'btn btn-sm btn-outline-success me-1' },
                        { extend: 'pdf', text: 'Export PDF', className: 'btn btn-sm btn-outline-danger me-1' },
                        { extend: 'print', text: 'Print', className: 'btn btn-sm btn-outline-secondary' }
                    ],
                    order: [[0, 'asc']],
                    columnDefs: [
                        { targets: [6, 7], orderable: false }
                    ]
                });
            }
        });
    }

    // Expand/collapse finding details
    function initExpanders() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.expand-btn');
            if (btn) {
                const target = document.getElementById(btn.dataset.target);
                if (target) {
                    const isVisible = target.style.display !== 'none';
                    target.style.display = isVisible ? 'none' : 'table-row';
                    btn.textContent = isVisible ? 'View' : 'Hide';
                    btn.classList.toggle('btn-outline-warning', !isVisible);
                }
            }
        });
    }

    // Object detail toggle
    function initObjectDetails() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.object-detail-btn');
            if (btn) {
                const target = document.getElementById('obj-detail-' + btn.dataset.obj);
                if (target) {
                    const isVisible = target.style.display !== 'none';
                    target.style.display = isVisible ? 'none' : 'block';
                    btn.textContent = isVisible ? 'View Details' : 'Hide Details';
                    btn.classList.toggle('btn-outline-warning', !isVisible);
                }
            }
        });
    }

    // Scrollspy for sidebar
    function initScrollspy() {
        const sections = document.querySelectorAll('.section');
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    navLinks.forEach(function(link) {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + entry.target.id) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, { rootMargin: '-20% 0px -70% 0px' });
        sections.forEach(function(section) {
            observer.observe(section);
        });
    }

    // Initialize on load
    document.addEventListener('DOMContentLoaded', function() {
        initCharts();
        initDataTables();
        initExpanders();
        initObjectDetails();
        initScrollspy();
    });
})();
'''
        filepath = os.path.join(self.output_dir, 'report.js')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(js)
        return filepath
    
    def _generate_charts_js(self) -> str:
        """Generate the charts JS file."""
        js = '''// SQL Security Scanner - Chart.js Configurations
// Helper for chart color schemes
const CHART_COLORS = {
    critical: '#f85149',
    high: '#f0883e',
    medium: '#39c5cf',
    low: '#8b949e',
    info: '#58a6ff',
    security: '#f85149',
    performance: '#d29922',
    schema: '#58a6ff',
    dataQuality: '#3fb950',
    bestPractices: '#8b949e',
    maintainability: '#bc8cff'
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#c9d1d9',
                font: { size: 11 }
            }
        }
    }
};

function makePieChart(canvasId, labels, data, colors) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' }
            }
        }
    });
}

function makeBarChart(canvasId, labels, data, label, color) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    new Chart(el, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label || 'Findings',
                data: data,
                backgroundColor: color || 'rgba(88, 166, 255, 0.8)'
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            scales: {
                x: {
                    ticks: { color: '#c9d1d9' },
                    grid: { color: 'rgba(140, 149, 159, 0.1)' }
                },
                y: {
                    ticks: { color: '#c9d1d9' },
                    grid: { color: 'rgba(140, 149, 159, 0.1)' },
                    beginAtZero: true
                }
            }
        }
    });
}
'''
        filepath = os.path.join(self.output_dir, 'charts.js')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(js)
        return filepath
    
    def _generate_findings_json(self) -> str:
        """Generate the findings JSON file."""
        findings_data = []
        for f in self.findings:
            findings_data.append({
                'severity': f.severity.value,
                'category': f.category.value,
                'rule_id': f.rule_id,
                'issue_title': f.issue_title,
                'description': f.description,
                'impact': f.impact,
                'risk': f.risk,
                'recommendation': f.recommendation,
                'best_practice_ref': f.best_practice_ref,
                'database': f.database,
                'schema': f.schema,
                'table': f.table,
                'object_name': f.object_name,
                'object_type': f.object_type,
                'file_name': f.file_name,
                'line_number': f.line_number,
                'sql_snippet': f.sql_snippet
            })
        
        filepath = os.path.join(self.output_dir, 'findings.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(findings_data, f, indent=2, ensure_ascii=False)
        return filepath
    
    def _generate_summary_json(self) -> str:
        """Generate the summary JSON file."""
        summary = {
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_path': self.file_stats.get('source_path'),
            'total_files': self.total_files,
            'total_statements': self.total_queries,
            'object_counts': dict(self.object_counts),
            'severity_counts': dict(self.severity_counts),
            'category_counts': dict(self.category_counts),
            'scores': {
                'security': round(self.scores.security_score, 2),
                'performance': round(self.scores.performance_score, 2),
                'quality': round(self.scores.quality_score, 2),
                'security_grade': get_score_grade(self.scores.security_score),
                'performance_grade': get_score_grade(self.scores.performance_score),
                'quality_grade': get_score_grade(self.scores.quality_score)
            },
            'top_risk_tables': [
                {'table': t, **v} for t, v in list(self.table_scores.items())[:10]
            ],
            'files_with_most_issues': [
                {'file': f, 'count': c} for f, c in self.files_with_issues.most_common(10)
            ]
        }
        
        filepath = os.path.join(self.output_dir, 'summary.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        return filepath