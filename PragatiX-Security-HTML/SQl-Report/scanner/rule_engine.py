"""
Analysis Rule Engine
Implements all security, performance, schema, data quality, best practices, and maintainability rules.
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from sql_parser import ParsedStatement, StatementType


class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class Category(Enum):
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    SCHEMA = "Schema Design"
    DATA_QUALITY = "Data Quality"
    BEST_PRACTICES = "Best Practices"
    MAINTAINABILITY = "Maintainability"


@dataclass
class Finding:
    severity: Severity
    category: Category
    database: Optional[str]
    schema: Optional[str]
    table: Optional[str]
    object_name: Optional[str]
    object_type: Optional[str]
    file_name: str
    line_number: int
    sql_snippet: str
    issue_title: str
    description: str
    impact: str
    risk: str
    recommendation: str
    best_practice_ref: str
    rule_id: str


class RuleEngine:
    def __init__(self):
        self.findings: List[Finding] = []
        self.secret_patterns = [
            (r'(?i)(password|pwd|secret|api[_-]?key|token|jwt|connectionstring|conn[_-]?str)\s*[=:]\s*["\']?[^"\'\s]{8,}', "Hardcoded secret"),
            (r'(?i)(DES|MD5|SHA1|SHA-1)\s*\(', "Weak cryptography"),
            (r'xp_cmdshell', "xp_cmdshell usage"),
            (r'OPENROWSET|OPENQUERY', "Linked server usage"),
            (r'(?i)TRUSTWORTHY\s+ON', "TRUSTWORTHY ON"),
            (r'(?i)EXECUTE\s+AS\s+(OWNER|CALLER|SELF)', "EXECUTE AS risk"),
            (r'(?i)GRANT\s+(ALL|CONTROL\s+SERVER|ALTER\s+ANY\s+LOGIN|ALTER\s+ANY\s+DATABASE)', "Excessive permissions"),
            (r'(?i)db_owner|sysadmin', "High privilege role"),
        ]
        
        self.sql_injection_patterns = [
            (r'(?i)EXEC\s*\(\s*@', "Dynamic SQL with EXEC"),
            (r'(?i)sp_executesql\s+@', "sp_executesql usage"),
            (r'@\w+\s*\+\s*@\w+', "String concatenation in SQL"),
            (r'@\w+\s*\+\s*[\'"]', "String concatenation with literal"),
        ]
    
    def analyze(self, statements: List[ParsedStatement]) -> List[Finding]:
        """Run all analysis rules on parsed statements."""
        self.findings = []
        
        for stmt in statements:
            self._analyze_statement(stmt)
        
        return self._deduplicate(self.findings)
    
    def _deduplicate(self, findings: List[Finding]) -> List[Finding]:
        """Remove duplicate findings for the same logical object.
        
        The same table/procedure appears in multiple dump files (tables/,
        schemas/, data/, and root-level aggregate files). Keep one finding
        per (rule, object) preferring the most canonical source file.
        """
        def folder_priority(f: Finding) -> int:
            path = (f.file_name or '').replace('\\', '/')
            if '/tables/' in path:
                return 0
            if '/schemas/' in path:
                return 1
            if '/data/' in path:
                return 2
            return 3
        
        ordered = sorted(findings, key=folder_priority)
        seen = set()
        deduped = []
        for f in ordered:
            obj_key = (f.object_name or f.table or '') if (f.object_name or f.table) else f.file_name
            key = (f.category.value, f.rule_id, obj_key, f.issue_title)
            if key not in seen:
                seen.add(key)
                deduped.append(f)
        
        # Restore original scan order (grouped by category relevance is handled at report time)
        deduped.sort(key=lambda f: (f.category.value, f.severity.value != 'Critical', f.severity.value != 'High',
                                    f.line_number))
        return deduped
    
    def _analyze_statement(self, stmt: ParsedStatement) -> None:
        """Analyze a single statement with all applicable rules."""
        sql = stmt.raw_sql
        sql_upper = sql.upper()
        
        self._run_security_rules(stmt, sql, sql_upper)
        self._run_performance_rules(stmt, sql, sql_upper)
        self._run_schema_rules(stmt, sql, sql_upper)
        self._run_data_quality_rules(stmt, sql, sql_upper)
        self._run_best_practices_rules(stmt, sql, sql_upper)
        self._run_maintainability_rules(stmt, sql, sql_upper)
    
    def _add_finding(self, stmt: ParsedStatement, severity: Severity, category: Category,
                     rule_id: str, title: str, description: str, impact: str,
                     risk: str, recommendation: str, best_practice_ref: str,
                     sql_snippet: str = None, line_offset: int = 0) -> None:
        """Add a finding to the results."""
        snippet = sql_snippet or stmt.raw_sql[:500]
        line_no = stmt.line_start + line_offset
        
        self.findings.append(Finding(
            severity=severity,
            category=category,
            database=stmt.database,
            schema=stmt.schema,
            table=stmt.table,
            object_name=stmt.object_name,
            object_type=stmt.object_type,
            file_name=stmt.file_name,
            line_number=line_no,
            sql_snippet=snippet,
            issue_title=title,
            description=description,
            impact=impact,
            risk=risk,
            recommendation=recommendation,
            best_practice_ref=best_practice_ref,
            rule_id=rule_id
        ))
    
    def _run_security_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run security-related rules."""
        for pattern, desc in self.secret_patterns:
            matches = list(re.finditer(pattern, sql, re.IGNORECASE))
            for match in matches:
                line_offset = sql[:match.start()].count('\n')
                self._add_finding(stmt, Severity.CRITICAL, Category.SECURITY,
                    "SEC-001", f"Hardcoded Secret Detected: {desc}",
                    f"Found potential hardcoded secret: {match.group()[:50]}",
                    "Secrets in source code can be exposed in version control, logs, or backups",
                    "Critical - Immediate credential compromise risk",
                    "Move secrets to secure configuration (Azure Key Vault, AWS Secrets Manager, env vars)",
                    "OWASP A07:2021 - Identification and Authentication Failures",
                    sql[max(0, match.start()-100):match.end()+100], line_offset)
        
        for pattern, desc in self.sql_injection_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                self._add_finding(stmt, Severity.HIGH, Category.SECURITY,
                    "SEC-002", f"SQL Injection Risk: {desc}",
                    f"Dynamic SQL construction detected: {desc}",
                    "User input concatenated into SQL can lead to injection attacks",
                    "High - Data breach, data manipulation, privilege escalation",
                    "Use parameterized queries, sp_executesql with parameters, or ORM",
                    "OWASP A03:2021 - Injection",
                    sql[:500])
        
        if 'EXEC(' in sql_upper or 'EXECUTE(' in sql_upper:
            self._add_finding(stmt, Severity.HIGH, Category.SECURITY,
                "SEC-003", "EXEC() with Dynamic SQL",
                "EXEC() executing dynamically constructed string",
                "Allows arbitrary code execution if input not validated",
                "High - Remote code execution possible",
                "Use sp_executesql with parameters, avoid EXEC(string)",
                "Microsoft SQL Server Best Practices - Dynamic SQL")
        
        if 'XP_CMDSHELL' in sql_upper:
            self._add_finding(stmt, Severity.CRITICAL, Category.SECURITY,
                "SEC-004", "xp_cmdshell Enabled/Used",
                "xp_cmdshell allows OS command execution from SQL",
                "Full server compromise if SQL injection exists",
                "Critical - OS-level access",
                "Disable xp_cmdshell (sp_configure), use CLR or external processes",
                "Microsoft Security Best Practices - xp_cmdshell")
        
        if 'OPENROWSET' in sql_upper or 'OPENQUERY' in sql_upper:
            self._add_finding(stmt, Severity.HIGH, Category.SECURITY,
                "SEC-005", "Linked Server / OPENROWSET Usage",
                "Cross-server queries can expose credentials and allow lateral movement",
                "Credential leakage, lateral movement",
                "High - Network exposure",
                "Avoid linked servers; use ETL/ELT processes, secure APIs",
                "Microsoft SQL Server Security - Linked Servers")
        
        if 'TRUSTWORTHY ON' in sql_upper:
            self._add_finding(stmt, Severity.HIGH, Category.SECURITY,
                "SEC-006", "TRUSTWORTHY ON",
                "Database TRUSTWORTHY allows EXECUTE AS to escape database context",
                "Privilege escalation across databases",
                "High - Cross-database access",
                "Set TRUSTWORTHY OFF, use module signing instead",
                "Microsoft SQL Server - TRUSTWORTHY Database Property")
        
        if 'EXECUTE AS' in sql_upper and ('OWNER' in sql_upper or 'CALLER' in sql_upper):
            self._add_finding(stmt, Severity.MEDIUM, Category.SECURITY,
                "SEC-007", "EXECUTE AS OWNER/CALLER",
                "Module executes with elevated permissions",
                "Unintended privilege escalation",
                "Medium - Permission misuse",
                "Use EXECUTE AS with specific low-privilege user, or module signing",
                "Microsoft SQL Server - EXECUTE AS Clause")
        
        if re.search(r'\bGRANT\s+(ALL|CONTROL\s+SERVER|ALTER\s+ANY\s+LOGIN|ALTER\s+ANY\s+DATABASE)\b', sql_upper):
            self._add_finding(stmt, Severity.CRITICAL, Category.SECURITY,
                "SEC-008", "Excessive GRANT Permissions",
                "Overly broad permissions granted",
                "Violation of least privilege, attack surface expansion",
                "Critical - Full server/database control",
                "Grant minimal required permissions only",
                "Principle of Least Privilege - SQL Server Permissions")
        
        if re.search(r'\b(db_owner|sysadmin|securityadmin)\b', sql_upper):
            self._add_finding(stmt, Severity.HIGH, Category.SECURITY,
                "SEC-009", "High-Privilege Role Assignment",
                "Assignment of powerful fixed server/database roles",
                "Excessive permissions for routine operations",
                "High - Full control over database/server",
                "Create custom roles with minimal required permissions",
                "SQL Server Role-Based Security Best Practices")
    
    def _run_performance_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run performance-related rules."""
        if stmt.type in (StatementType.SELECT, StatementType.INSERT, StatementType.UPDATE, StatementType.DELETE):
            if re.search(r'\bSELECT\s+\*\b', sql_upper):
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-001", "SELECT * Usage",
                    "Selecting all columns increases I/O, network, and memory usage",
                    "Unnecessary data transfer, plan cache bloat, breaking changes on schema changes",
                    "Medium - Wasted resources, slower queries",
                    "Explicitly list required columns only",
                    "SQL Server Performance - Avoid SELECT *")
            
            if stmt.type == StatementType.SELECT and 'WHERE' not in sql_upper:
                if 'JOIN' not in sql_upper or 'CROSS JOIN' in sql_upper:
                    self._add_finding(stmt, Severity.HIGH, Category.PERFORMANCE,
                        "PERF-002", "Missing WHERE Clause (Table Scan)",
                        "Query without filter scans entire table",
                        "Full table scan, high I/O, blocking",
                        "High - Performance degradation",
                        "Add appropriate WHERE clause with indexed columns",
                        "SQL Server Query Tuning - SARGable Predicates")
            
            if 'CROSS JOIN' in sql_upper or (('JOIN' in sql_upper and 'ON' not in sql_upper and 'WHERE' not in sql_upper)):
                self._add_finding(stmt, Severity.HIGH, Category.PERFORMANCE,
                    "PERF-003", "Cartesian Product / Missing Join Condition",
                    "Cross join or missing ON/WHERE clause produces cartesian product",
                    "Exponential row multiplication, server hang",
                    "High - Resource exhaustion",
                    "Add proper JOIN conditions with ON clause",
                    "SQL Server JOIN Best Practices")
            
            if re.search(r'\bWHERE\s+\w+\s*\(\s*\w+\s*\)', sql_upper) or re.search(r'\bWHERE\s+CONVERT\(', sql_upper) or re.search(r'\bWHERE\s+CAST\(', sql_upper):
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-004", "Function/Implicit Conversion in WHERE Clause",
                    "Functions on columns prevent index seeks",
                    "Index scan instead of seek, poor cardinality estimates",
                    "Medium - Suboptimal query plan",
                    "Rewrite to avoid functions on columns, use computed columns or indexed views",
                    "SQL Server SARGable Queries - Avoid Functions on Columns")
            
            if re.search(r"LIKE\s+['\"]%", sql_upper):
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-005", "Leading Wildcard in LIKE",
                    "LIKE '%text%' prevents index usage",
                    "Full scan of indexed column",
                    "Medium - Index scan instead of seek",
                    "Use full-text search, or move wildcard to end if possible",
                    "SQL Server Full-Text Search vs LIKE")
            
            if re.search(r'\bIN\s*\([^)]{100,}\)', sql_upper) or sql_upper.count('OR') > 10:
                self._add_finding(stmt, Severity.LOW, Category.PERFORMANCE,
                    "PERF-006", "Large IN List / Many OR Conditions",
                    "Large IN lists or many ORs cause plan compilation issues",
                    "High compilation time, plan cache pollution",
                    "Low - Compilation overhead",
                    "Use temp table/table-valued parameter with JOIN instead",
                    "SQL Server - Optimizing IN Clauses")
            
            if 'DISTINCT' in sql_upper and ('JOIN' in sql_upper or 'GROUP BY' in sql_upper):
                self._add_finding(stmt, Severity.LOW, Category.PERFORMANCE,
                    "PERF-007", "Potential DISTINCT Misuse",
                    "DISTINCT with JOINs may indicate missing proper JOIN conditions",
                    "Unnecessary sort/unique operation",
                    "Low - Extra processing",
                    "Verify JOIN logic, use proper keys instead of DISTINCT",
                    "SQL Server - DISTINCT vs Proper JOINs")
            
            if 'ORDER BY' in sql_upper and 'INDEX' not in sql_upper:
                self._add_finding(stmt, Severity.INFO, Category.PERFORMANCE,
                    "PERF-008", "ORDER BY Without Supporting Index",
                    "Sort operation may spill to tempdb",
                    "TempDB contention, memory grant issues",
                    "Info - Potential sort spill",
                    "Add index matching ORDER BY columns",
                    "SQL Server - Index Design for Sorting")
            
            if 'CURSOR' in sql_upper or 'WHILE' in sql_upper:
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-009", "Cursor / WHILE Loop Usage",
                    "Row-by-row processing (RBAR) is slow in SQL Server",
                    "Severe performance degradation vs set-based operations",
                    "Medium - RBAR pattern",
                    "Rewrite as set-based operations (CTE, window functions, MERGE)",
                    "SQL Server - Set-Based vs Row-Based Operations")
            
            if re.search(r'(?i)INSERT\s+INTO\s+\w+\s+(VALUES|SELECT).*?(?:,.*?){100,}', sql_upper) or \
               re.search(r'(?i)(UPDATE|DELETE)\s+\w+.*?WHERE.*?(?:OR|AND).*?(?:OR|AND).*?(?:OR|AND)', sql_upper):
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-010", "Large DML Without Batching",
                    "Large INSERT/UPDATE/DELETE without batching causes long transactions",
                    "Log growth, blocking, transaction log full",
                    "Medium - Log/blocking issues",
                    "Batch DML in chunks of 1000-5000 rows",
                    "SQL Server - Batching Large DML Operations")
            
            if 'NOLOCK' in sql_upper or 'READ UNCOMMITTED' in sql_upper:
                self._add_finding(stmt, Severity.MEDIUM, Category.PERFORMANCE,
                    "PERF-011", "NOLOCK / READ UNCOMMITTED Hint",
                    "Dirty reads, missing rows, duplicate reads possible",
                    "Data inconsistency, corruption risk",
                    "Medium - Data integrity risk",
                    "Use READ COMMITTED SNAPSHOT (RCSI) or proper isolation level",
                    "SQL Server - NOLOCK Risks and Alternatives")
            
            if re.search(r'BEGIN\s+TRAN', sql_upper) and 'COMMIT' not in sql_upper and 'ROLLBACK' not in sql_upper:
                self._add_finding(stmt, Severity.HIGH, Category.PERFORMANCE,
                    "PERF-012", "Uncommitted Transaction",
                    "Transaction started but not committed/rolled back",
                    "Lock holding, blocking, log growth",
                    "High - Blocking and log issues",
                    "Ensure all transactions have COMMIT/ROLLBACK, use TRY/CATCH",
                    "SQL Server - Transaction Management")
    
    def _run_schema_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run schema design rules."""
        if stmt.type == StatementType.CREATE_TABLE:
            col_pk = any(c.get('is_primary_key') for c in stmt.columns)
            constraint_pk = any(c.get('type') == 'PRIMARY KEY' for c in stmt.constraints)
            has_pk = col_pk or constraint_pk
            has_fk = any(c.get('type') == 'FOREIGN KEY' for c in stmt.constraints)
            has_clustered = any('CLUSTERED' in c.get('type', '') for c in stmt.constraints)
            
            if not has_pk:
                self._add_finding(stmt, Severity.HIGH, Category.SCHEMA,
                    "SCHEMA-001", "Table Missing Primary Key",
                    "Table created without PRIMARY KEY constraint",
                    "Heap table, no unique row identification, replication issues",
                    "High - Data integrity, performance",
                    "Add PRIMARY KEY (surrogate or natural key)",
                    "Every Table Should Have a Primary Key")
            
            is_mysql = 'ENGINE=' in sql_upper or 'AUTO_INCREMENT' in sql_upper
            if not is_mysql and not has_clustered and has_pk:
                self._add_finding(stmt, Severity.MEDIUM, Category.SCHEMA,
                    "SCHEMA-002", "Primary Key Not Clustered",
                    "PK exists but not defined as CLUSTERED",
                    "Heap with non-clustered PK, extra lookup overhead",
                    "Medium - Extra key lookup",
                    "Make PK CLUSTERED unless specific reason for non-clustered",
                    "SQL Server - Clustered Index Design Guide")
            
            if not has_fk and stmt.columns:
                self._add_finding(stmt, Severity.INFO, Category.SCHEMA,
                    "SCHEMA-003", "No Foreign Keys Defined",
                    "Table has no FOREIGN KEY constraints",
                    "Referential integrity not enforced at DB level",
                    "Info - Data integrity risk",
                    "Add FK constraints for referential integrity",
                    "Foreign Key Constraints")
            
            for col in stmt.columns:
                col_type = col.get('type', '').upper()
                if col.get('is_primary_key') and col.get('nullable'):
                    self._add_finding(stmt, Severity.HIGH, Category.SCHEMA,
                        "SCHEMA-004", f"Nullable Primary Key Column: {col['name']}",
                        "Primary key column allows NULL values",
                        "Violates entity integrity, duplicate NULLs possible",
                        "High - Data integrity violation",
                        "Make PK column NOT NULL",
                        "SQL Server - Primary Key Constraints")
                
                if 'FLOAT' in col_type or 'REAL' in col_type:
                    self._add_finding(stmt, Severity.MEDIUM, Category.SCHEMA,
                        "SCHEMA-005", f"FLOAT/REAL for Monetary Data: {col['name']}",
                        "Floating point types cause rounding errors for money",
                        "Financial calculation inaccuracies",
                        "Medium - Data accuracy",
                        "Use DECIMAL(p,s) or MONEY for monetary values",
                        "SQL Server - Decimal vs Float for Money")
                
                if any(t in col_type for t in ['VARCHAR(MAX)', 'NVARCHAR(MAX)', 'TEXT', 'NTEXT', 'IMAGE']):
                    self._add_finding(stmt, Severity.LOW, Category.SCHEMA,
                        "SCHEMA-006", f"Large Object Type: {col['name']} ({col['type']})",
                        "LOB types (MAX, TEXT, IMAGE) have storage/performance implications",
                        "Row overflow, no online index rebuild (legacy), backup size",
                        "Low - Storage/performance",
                        "Use VARCHAR(n) with appropriate length, FILESTREAM for large files",
                        "SQL Server - LOB Data Types")
                
                if col.get('default') is None and not col.get('is_identity') and not col.get('is_primary_key') and not col.get('nullable'):
                    self._add_finding(stmt, Severity.INFO, Category.SCHEMA,
                        "SCHEMA-007", f"NOT NULL Column Missing DEFAULT: {col['name']}",
                        "Column is NOT NULL but has no DEFAULT constraint",
                        "Application must always provide a value, risk of insert failures",
                        "Info - Data consistency",
                        "Add DEFAULT constraint for consistent defaults",
                        "SQL Server - DEFAULT Constraints")
            
            identity_cols = [c for c in stmt.columns if c.get('is_identity')]
            if len(identity_cols) > 1:
                self._add_finding(stmt, Severity.HIGH, Category.SCHEMA,
                    "SCHEMA-008", "Multiple IDENTITY Columns",
                    "Table has more than one IDENTITY column",
                    "Only one IDENTITY allowed per table in SQL Server",
                    "High - Invalid schema",
                    "Remove extra IDENTITY columns, use SEQUENCE if needed",
                    "SQL Server - IDENTITY Property")
            
            pk_cols = [c for c in stmt.columns if c.get('is_primary_key')]
            if len(pk_cols) > 1:
                self._add_finding(stmt, Severity.MEDIUM, Category.SCHEMA,
                    "SCHEMA-009", "Composite Primary Key",
                    "Primary key consists of multiple columns",
                    "Wider non-clustered indexes, more complex joins",
                    "Medium - Index width, join complexity",
                    "Consider surrogate key (INT/BIGINT IDENTITY) as PK",
                    "SQL Server - Surrogate vs Natural Keys")
            
            guid_pk = any('UNIQUEIDENTIFIER' in c.get('type', '').upper() and c.get('is_primary_key') for c in stmt.columns)
            if guid_pk:
                self._add_finding(stmt, Severity.MEDIUM, Category.SCHEMA,
                    "SCHEMA-010", "GUID as Clustered Primary Key",
                    "GUID PK causes fragmentation due to random inserts",
                    "Page splits, fragmentation, larger indexes",
                    "Medium - Fragmentation",
                    "Use NEWSEQUENTIALID() or INT/BIGINT IDENTITY for clustered PK",
                    "SQL Server - GUID vs INT for Primary Key")
    
    def _run_data_quality_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run data quality rules on INSERT/data statements."""
        if stmt.type == StatementType.INSERT:
            if 'VALUES' in sql_upper:
                values_match = re.search(r'VALUES\s*(.+)', sql, re.IGNORECASE | re.DOTALL)
                if values_match:
                    values_text = values_match.group(1)
                    row_count = values_text.count('),(') + 1
                    if row_count > 1000:
                        self._add_finding(stmt, Severity.INFO, Category.DATA_QUALITY,
                            "DQ-001", f"Large INSERT with {row_count} Rows",
                            "Large multi-row INSERT statement",
                            "Long compilation, plan cache, transaction log",
                            "Info - Performance",
                            "Consider BULK INSERT, BCP, or batched inserts",
                            "SQL Server - Bulk Insert Operations")
            
            if re.search(r"['\"]\s*['\"]", sql) or re.search(r'\(\s*,', sql):
                self._add_finding(stmt, Severity.MEDIUM, Category.DATA_QUALITY,
                    "DQ-002", "Empty String or Missing Values in INSERT",
                    "Empty strings ('') or missing values detected",
                    "Data quality issues, NOT NULL violations",
                    "Medium - Data integrity",
                    "Validate data before insert, use DEFAULT constraints",
                    "Data Quality - Input Validation")
            
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            emails = re.findall(email_pattern, sql)
            if len(emails) > len(set(emails)):
                self._add_finding(stmt, Severity.MEDIUM, Category.DATA_QUALITY,
                    "DQ-003", "Duplicate Email Addresses in Data",
                    "Same email appears multiple times in INSERT data",
                    "Duplicate user accounts, communication issues",
                    "Medium - Data duplication",
                    "Add UNIQUE constraint on email column, deduplicate source",
                    "Data Quality - Uniqueness Validation")
            
            phone_pattern = r'(?<![\d])[6-9]\d{9}(?![\d])'
            phones = re.findall(phone_pattern, sql)
            if len(phones) > 50:
                self._add_finding(stmt, Severity.LOW, Category.DATA_QUALITY,
                    "DQ-004", "Phone Numbers Present in Data",
                    f"Detected {len(phones)} Indian mobile numbers in INSERT data",
                    "Validate phone formats at application layer",
                    "Low - Data quality",
                    "Validate phone format at application/ETL layer",
                    "Indian Phone Number Validation")
            
            gst_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}'
            gsts = re.findall(gst_pattern, sql)
            if gsts:
                self._add_finding(stmt, Severity.INFO, Category.DATA_QUALITY,
                    "DQ-005", "GSTIN Values Found in Data",
                    f"Detected {len(gsts)} GSTIN values in INSERT data",
                    "Validate GSTIN at application layer if tax-related",
                    "Info - Compliance",
                    "Validate GSTIN format (2-digit state + PAN + entity + check)",
                    "Indian GSTIN Validation")
            
            pan_pattern = r'(?<![A-Z])[A-Z]{5}\d{4}[A-Z](?![A-Z])'
            pans = re.findall(pan_pattern, sql)
            if len(pans) > 20:
                self._add_finding(stmt, Severity.INFO, Category.DATA_QUALITY,
                    "DQ-006", "PAN Number Values Found in Data",
                    f"Detected {len(pans)} PAN values in INSERT data",
                    "Personal data handling compliance",
                    "Info - Compliance",
                    "Validate PAN format (5 letters + 4 digits + 1 letter)",
                    "Indian PAN Validation")
            
            aadhaar_pattern = r'(?<![\d])\d{4}\s?\d{4}\s?\d{4}(?![\d])'
            aadhaars = re.findall(aadhaar_pattern, sql)
            if aadhaars:
                self._add_finding(stmt, Severity.MEDIUM, Category.DATA_QUALITY,
                    "DQ-007", "Aadhaar-Like Numbers in Data",
                    f"Detected {len(aadhaars)} Aadhaar-like values",
                    "Sensitive personal data in database dump",
                    "Medium - Privacy/Compliance",
                    "Encrypt Aadhaar data at rest, restrict access",
                    "Indian Aadhaar Validation & Privacy")
            
            pincode_pattern = r'(?<![\d])[1-9]\d{5}(?![\d])'
            pincodes = re.findall(pincode_pattern, sql)
            if len(pincodes) > 100:
                self._add_finding(stmt, Severity.INFO, Category.DATA_QUALITY,
                    "DQ-008", "Indian Pincode Values Found in Data",
                    f"Detected {len(pincodes)} pincode values in INSERT data",
                    "Validate postal codes at application layer",
                    "Info - Data quality",
                    "Validate pincode (6 digits, first digit 1-9)",
                    "Indian Pincode Validation")
    
    def _run_best_practices_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run best practices and naming convention rules."""
        reserved_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'GROUP', 'BY', 'HAVING', 'INSERT', 'UPDATE', 'DELETE',
                            'CREATE', 'ALTER', 'DROP', 'TABLE', 'INDEX', 'VIEW', 'PROCEDURE', 'FUNCTION', 'TRIGGER',
                            'USER', 'ROLE', 'GRANT', 'REVOKE', 'DENY', 'KEY', 'PRIMARY', 'FOREIGN', 'REFERENCES',
                            'CHECK', 'DEFAULT', 'CONSTRAINT', 'UNIQUE', 'NOT', 'NULL', 'IDENTITY', 'CLUSTERED',
                            'NONCLUSTERED', 'PARTITION', 'SCHEMA', 'DATABASE', 'SERVER', 'LOGIN', 'PASSWORD']
        
        if stmt.object_name:
            obj_name = stmt.object_name
            if obj_name.upper() in reserved_keywords:
                self._add_finding(stmt, Severity.MEDIUM, Category.BEST_PRACTICES,
                    "BP-001", f"Reserved Keyword as Object Name: {obj_name}",
                    f"Object named after T-SQL reserved keyword: {obj_name}",
                    "Requires brackets/quotes everywhere, confusion, migration issues",
                    "Medium - Maintenance burden",
                    "Rename object to non-reserved name, or always use [brackets]",
                    "SQL Server - Reserved Keywords")
            
            has_snake = '_' in obj_name
            has_camel = any(c.isupper() for c in obj_name[1:]) and '_' not in obj_name
            has_pascal = obj_name[0].isupper() and '_' not in obj_name
            
            if has_snake and has_camel:
                self._add_finding(stmt, Severity.LOW, Category.BEST_PRACTICES,
                    "BP-002", f"Mixed Naming Convention: {obj_name}",
                    "Object name mixes snake_case and camelCase/PascalCase",
                    "Inconsistent naming, harder to predict/remember",
                    "Low - Inconsistency",
                    "Adopt single naming convention (snake_case recommended for SQL)",
                    "SQL Server Naming Conventions")
        
        if '--' in sql or '/*' in sql:
            comment_lines = [l for l in sql.split('\n') if l.strip().startswith('--') or '/*' in l]
            if len(comment_lines) > 10:
                self._add_finding(stmt, Severity.INFO, Category.BEST_PRACTICES,
                    "BP-003", "Excessive Commented Code",
                    f"Statement has {len(comment_lines)} comment lines",
                    "Dead code, confusion, larger files",
                    "Info - Code cleanliness",
                    "Remove commented-out code, use version control for history",
                    "Clean Code - Remove Dead Code")
        
        if re.search(r'(?i)SET\s+(ANSI_NULLS|QUOTED_IDENTIFIER|ANSI_PADDING|ANSI_WARNINGS|CONCAT_NULL_YIELDS_NULL)\s+OFF', sql_upper):
            self._add_finding(stmt, Severity.MEDIUM, Category.BEST_PRACTICES,
                "BP-004", "Deprecated SET Options OFF",
                "Legacy SET options disabled (ANSI_NULLS OFF, etc.)",
                "Deprecated behavior, compatibility issues, future removal",
                "Medium - Deprecation",
                "Keep all ANSI SET options ON (default in modern SQL Server)",
                "SQL Server - SET Options")
        
        if stmt.type == StatementType.CREATE_PROCEDURE and len(sql) > 5000:
            self._add_finding(stmt, Severity.MEDIUM, Category.BEST_PRACTICES,
                "BP-005", "Oversized Stored Procedure",
                f"Procedure exceeds 5000 characters ({len(sql)} chars)",
                "Hard to maintain, test, debug; compilation/recompilation issues",
                "Medium - Maintainability",
                "Break into smaller procedures, use modules",
                "SQL Server - Stored Procedure Best Practices")
    
    def _run_maintainability_rules(self, stmt: ParsedStatement, sql: str, sql_upper: str) -> None:
        """Run maintainability rules."""
        if stmt.type in (StatementType.CREATE_PROCEDURE, StatementType.CREATE_FUNCTION, StatementType.CREATE_TRIGGER):
            nest_level = 0
            max_nest = 0
            for char in sql:
                if char == '(':
                    nest_level += 1
                    max_nest = max(max_nest, nest_level)
                elif char == ')':
                    nest_level = max(0, nest_level - 1)
            
            if max_nest > 5:
                self._add_finding(stmt, Severity.MEDIUM, Category.MAINTAINABILITY,
                    "MAINT-001", f"Deep Nesting Level: {max_nest}",
                    f"Code has nesting depth of {max_nest} levels",
                    "Hard to read, understand, and maintain",
                    "Medium - Cognitive complexity",
                    "Refactor into smaller functions/procedures, use CTEs",
                    "Cyclomatic Complexity - SQL Server")
            
            case_count = sql_upper.count('CASE ')
            if case_count > 5:
                self._add_finding(stmt, Severity.LOW, Category.MAINTAINABILITY,
                    "MAINT-002", f"Complex CASE Expressions: {case_count}",
                    f"Procedure contains {case_count} CASE expressions",
                    "Complex conditional logic, hard to test",
                    "Low - Complexity",
                    "Simplify logic, use lookup tables, or computed columns",
                    "SQL Server - CASE Expression Best Practices")
            
            param_count = sql.count('@') - sql.count('@@')
            if param_count > 10:
                self._add_finding(stmt, Severity.LOW, Category.MAINTAINABILITY,
                    "MAINT-003", f"Too Many Parameters: {param_count}",
                    f"Procedure has ~{param_count} parameters",
                    "Hard to call, maintain, document; parameter sniffing issues",
                    "Low - Usability",
                    "Group related parameters into table-valued parameters or JSON",
                    "SQL Server - Table-Valued Parameters")
        
        if stmt.type == StatementType.SELECT:
            col_count = sql_upper.count(',') + 1 if 'SELECT' in sql_upper else 0
            if col_count > 30:
                self._add_finding(stmt, Severity.INFO, Category.MAINTAINABILITY,
                    "MAINT-004", f"Wide Result Set: ~{col_count} Columns",
                    f"Query returns approximately {col_count} columns",
                    "Network overhead, client memory, tighter coupling",
                    "Info - Coupling",
                    "Select only needed columns, use views for common subsets",
                    "SQL Server - Column Selection Best Practices")