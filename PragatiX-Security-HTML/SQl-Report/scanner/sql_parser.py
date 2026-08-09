"""
SQL Parser Module
Uses sqlglot to parse T-SQL statements and extract structured information.
"""
import sqlglot
from sqlglot import exp
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re


class StatementType(Enum):
    CREATE_TABLE = "CREATE_TABLE"
    ALTER_TABLE = "ALTER_TABLE"
    DROP_TABLE = "DROP_TABLE"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SELECT = "SELECT"
    MERGE = "MERGE"
    CREATE_PROCEDURE = "CREATE_PROCEDURE"
    CREATE_FUNCTION = "CREATE_FUNCTION"
    CREATE_TRIGGER = "CREATE_TRIGGER"
    CREATE_VIEW = "CREATE_VIEW"
    CREATE_INDEX = "CREATE_INDEX"
    CONSTRAINT = "CONSTRAINT"
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    DENY = "DENY"
    EXEC = "EXEC"
    DECLARE = "DECLARE"
    SET = "SET"
    IF = "IF"
    WHILE = "WHILE"
    BEGIN = "BEGIN"
    COMMENT = "COMMENT"
    OTHER = "OTHER"


@dataclass
class ParsedStatement:
    type: StatementType
    raw_sql: str
    file_name: str
    line_start: int
    line_end: int
    database: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None
    object_name: Optional[str] = None
    object_type: Optional[str] = None
    columns: List[Dict] = field(default_factory=list)
    constraints: List[Dict] = field(default_factory=list)
    indexes: List[Dict] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    ast: Any = None


class SqlParser:
    def __init__(self, dialect: str = "mysql"):
        self.dialect = dialect
        
    def parse_file(self, file_path: str, file_name: str) -> List[ParsedStatement]:
        """Parse a SQL file and return list of parsed statements."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        statements = self._split_statements(content)
        parsed = []
        
        for i, (stmt_text, line_start, line_end) in enumerate(statements):
            if not stmt_text.strip() or self._is_comment_only(stmt_text):
                continue
            
            parsed_stmt = self._parse_statement(stmt_text, file_name, line_start, line_end)
            if parsed_stmt:
                parsed.append(parsed_stmt)
        
        return parsed
    
    def _split_statements(self, content: str) -> List[tuple]:
        """Split SQL content into individual statements with line numbers."""
        lines = content.split('\n')
        statements = []
        current_stmt = []
        line_start = 1
        in_block_comment = False
        in_string = False
        string_char = None
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if not in_block_comment and not in_string:
                if line_stripped.startswith('--'):
                    continue
                if line_stripped.startswith('/*'):
                    in_block_comment = True
                    if '*/' in line_stripped[2:]:
                        in_block_comment = False
                    continue
            
            if in_block_comment:
                if '*/' in line:
                    in_block_comment = False
                continue
            
            for j, char in enumerate(line):
                if not in_string and char in ("'", '"', '`'):
                    in_string = True
                    string_char = char
                elif in_string and char == string_char:
                    if j + 1 < len(line) and line[j + 1] == string_char:
                        continue
                    in_string = False
                    string_char = None
                elif not in_string and char == ';':
                    current_stmt.append(line[:j+1])
                    stmt_text = '\n'.join(current_stmt)
                    statements.append((stmt_text, line_start, i))
                    current_stmt = []
                    line_start = i + 1
                    break
            else:
                current_stmt.append(line)
        
        if current_stmt:
            stmt_text = '\n'.join(current_stmt)
            statements.append((stmt_text, line_start, len(lines)))
        
        return statements
    
    def _is_comment_only(self, text: str) -> bool:
        """Check if statement is only comments."""
        lines = text.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('--') and not stripped.startswith('/*'):
                return False
        return True
    
    def _parse_statement(self, sql: str, file_name: str, line_start: int, line_end: int) -> Optional[ParsedStatement]:
        """Parse a single SQL statement using sqlglot."""
        try:
            parsed = sqlglot.parse(sql, dialect=self.dialect)
            if not parsed:
                return self._create_fallback_statement(sql, file_name, line_start, line_end)
            
            ast = parsed[0]
            stmt_type = self._classify_statement(ast)
            
            stmt = ParsedStatement(
                type=stmt_type,
                raw_sql=sql,
                file_name=file_name,
                line_start=line_start,
                line_end=line_end,
                ast=ast
            )
            
            # If this is a MySQL CREATE TABLE statement, always use the manual
            # parser for reliable column/PK/FK extraction (sqlglot mysql dialect
            # mis-parses MySQL dump table options like ENGINE=InnoDB).
            if self._is_mysql_create_table(sql):
                return self._parse_mysql_create_table(sql, file_name, line_start, line_end)
            
            self._extract_metadata(stmt, ast)
            
            return stmt
            
        except Exception as e:
            return self._create_fallback_statement(sql, file_name, line_start, line_end)
    
    def _is_mysql_create_table(self, sql: str) -> bool:
        """Check if the SQL is a CREATE TABLE statement."""
        return re.match(r'\s*CREATE\s+TABLE', sql, re.IGNORECASE) is not None

    def _parse_mysql_create_table(self, sql: str, file_name: str, line_start: int, line_end: int) -> ParsedStatement:
        """Manually parse a MySQL CREATE TABLE with table options."""
        stmt = ParsedStatement(
            type=StatementType.CREATE_TABLE,
            raw_sql=sql,
            file_name=file_name,
            line_start=line_start,
            line_end=line_end,
            object_type="TABLE"
        )
        
        # Extract table name
        table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(`[^`]+`|\w+)', sql, re.IGNORECASE)
        if table_match:
            stmt.object_name = table_match.group(1).strip('`')
        
        # Find the column definition block
        open_idx = sql.find('(')
        if open_idx == -1:
            return stmt
        
        depth = 0
        close_idx = -1
        for i, ch in enumerate(sql[open_idx:], open_idx):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    close_idx = i
                    break
        
        if close_idx == -1:
            return stmt
        
        body = sql[open_idx+1:close_idx]
        
        # Split top-level definitions (respecting nested parens and strings)
        defs = self._split_top_level(body)
        
        for d in defs:
            d = d.strip()
            if not d:
                continue
            d_upper = d.upper()
            
            if re.match(r'^PRIMARY\s+KEY', d_upper):
                cols = self._extract_key_columns(d)
                stmt.constraints.append({
                    'type': 'PRIMARY KEY',
                    'columns': cols,
                    'name': None
                })
            elif re.match(r'^FOREIGN\s+KEY', d_upper):
                cols = self._extract_key_columns(d)
                ref_match = re.search(r'REFERENCES\s+(`[^`]+`|\w+)\s*\(([^)]*)\)', d, re.IGNORECASE)
                ref_table = ref_match.group(1).strip('`') if ref_match else None
                ref_cols = [c.strip().strip('`') for c in ref_match.group(2).split(',')] if ref_match else []
                stmt.constraints.append({
                    'type': 'FOREIGN KEY',
                    'columns': cols,
                    'referenced_table': ref_table,
                    'referenced_columns': ref_cols,
                    'name': None
                })
            elif re.match(r'^UNIQUE', d_upper) or re.match(r'^KEY', d_upper):
                cols = self._extract_key_columns(d)
                name_match = re.search(r'^(?:UNIQUE\s+)?KEY\s+(`[^`]+`|\w+)', d, re.IGNORECASE)
                name = name_match.group(1).strip('`') if name_match else None
                stmt.indexes.append({
                    'columns': cols,
                    'name': name,
                    'unique': 'UNIQUE' in d_upper
                })
            elif re.match(r'^CHECK', d_upper):
                stmt.constraints.append({
                    'type': 'CHECK',
                    'expression': d,
                    'name': None
                })
            elif re.match(r'^CONSTRAINT', d_upper):
                name_match = re.search(r'CONSTRAINT\s+(`[^`]+`|\w+)', d, re.IGNORECASE)
                name = name_match.group(1).strip('`') if name_match else None
                if 'FOREIGN KEY' in d_upper:
                    cols = self._extract_key_columns(d)
                    ref_match = re.search(r'REFERENCES\s+(`[^`]+`|\w+)\s*\(([^)]*)\)', d, re.IGNORECASE)
                    stmt.constraints.append({
                        'type': 'FOREIGN KEY',
                        'columns': cols,
                        'referenced_table': ref_match.group(1).strip('`') if ref_match else None,
                        'referenced_columns': [c.strip().strip('`') for c in ref_match.group(2).split(',')] if ref_match else [],
                        'name': name
                    })
                else:
                    stmt.constraints.append({
                        'type': 'CONSTRAINT',
                        'expression': d,
                        'name': name
                    })
            else:
                # Column definition
                col_info = self._parse_column_def(d)
                if col_info:
                    stmt.columns.append(col_info)
        
        return stmt
    
    def _split_top_level(self, body: str) -> List[str]:
        """Split comma-separated definitions at top level, respecting parens and strings."""
        defs = []
        current = []
        depth = 0
        in_string = False
        string_char = None
        
        for ch in body:
            if not in_string and ch in ("'", '"', '`'):
                in_string = True
                string_char = ch
                current.append(ch)
            elif in_string:
                current.append(ch)
                if ch == string_char:
                    in_string = False
            elif ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                defs.append(''.join(current))
                current = []
            else:
                current.append(ch)
        
        if current:
            defs.append(''.join(current))
        return defs
    
    def _extract_key_columns(self, d: str) -> List[str]:
        """Extract column names from a KEY/FOREIGN KEY/PRIMARY KEY definition."""
        m = re.search(r'\(([^)]*)\)', d)
        if not m:
            return []
        parts = m.group(1).split(',')
        return [p.strip().strip('`').strip() for p in parts if p.strip()]
    
    def _parse_column_def(self, d: str) -> Optional[Dict]:
        """Parse a single column definition like `id` bigint NOT NULL AUTO_INCREMENT."""
        m = re.match(r'^\s*(`[^`]+`|\w+)\s+([A-Za-z_]+(?:\([^)]*\))?)', d)
        if not m:
            return None
        
        col_name = m.group(1).strip('`')
        col_type = m.group(2).strip()
        upper = d.upper()
        
        col_info = {
            'name': col_name,
            'type': col_type,
            'nullable': 'NOT NULL' not in upper,
            'default': None,
            'is_primary_key': False,
            'is_identity': False,
            'constraints': []
        }
        
        if 'NOT NULL' in upper:
            col_info['constraints'].append('NOT NULL')
        if 'NULL' in upper and 'NOT NULL' not in upper:
            col_info['constraints'].append('NULL')
        if 'AUTO_INCREMENT' in upper:
            col_info['is_identity'] = True
            col_info['constraints'].append('AUTO_INCREMENT')
        if 'PRIMARY KEY' in upper:
            col_info['is_primary_key'] = True
            col_info['constraints'].append('PRIMARY KEY')
        if 'UNIQUE' in upper:
            col_info['constraints'].append('UNIQUE')
        if 'DEFAULT' in upper:
            default_match = re.search(r'DEFAULT\s+(.+?)(?:\s+(?:ON\s+UPDATE|UNIQUE|PRIMARY|COMMENT|COLLATE|USING)|\)|\Z)', d, re.IGNORECASE)
            if default_match:
                col_info['default'] = default_match.group(1).strip().strip('`').strip("'").strip('"')
                col_info['constraints'].append(f"DEFAULT {col_info['default']}")
        
        return col_info
    
    def _classify_statement(self, ast: exp.Expression) -> StatementType:
        """Classify the statement type based on AST."""
        if isinstance(ast, exp.Create):
            if ast.kind == "DATABASE":
                return StatementType.OTHER
            if isinstance(ast.this, exp.Table):
                if ast.kind == "PROCEDURE":
                    return StatementType.CREATE_PROCEDURE
                elif ast.kind == "FUNCTION":
                    return StatementType.CREATE_FUNCTION
                elif ast.kind == "TRIGGER":
                    return StatementType.CREATE_TRIGGER
                elif ast.kind == "VIEW":
                    return StatementType.CREATE_VIEW
                elif ast.kind == "INDEX":
                    return StatementType.CREATE_INDEX
                return StatementType.CREATE_TABLE
        elif isinstance(ast, exp.Alter):
            return StatementType.ALTER_TABLE
        elif isinstance(ast, exp.Drop):
            return StatementType.DROP_TABLE
        elif isinstance(ast, exp.Insert):
            return StatementType.INSERT
        elif isinstance(ast, exp.Update):
            return StatementType.UPDATE
        elif isinstance(ast, exp.Delete):
            return StatementType.DELETE
        elif isinstance(ast, exp.Select):
            return StatementType.SELECT
        elif isinstance(ast, exp.Merge):
            return StatementType.MERGE
        elif isinstance(ast, exp.Grant):
            return StatementType.GRANT
        elif isinstance(ast, exp.Revoke):
            return StatementType.REVOKE
        elif isinstance(ast, exp.Command) and ast.this.upper() in ('EXEC', 'EXECUTE'):
            return StatementType.EXEC
        elif isinstance(ast, exp.Declare):
            return StatementType.DECLARE
        elif isinstance(ast, exp.Set):
            return StatementType.SET
        elif isinstance(ast, exp.If):
            return StatementType.IF
        elif isinstance(ast, exp.While):
            return StatementType.WHILE
        elif isinstance(ast, exp.Begin):
            return StatementType.BEGIN
        
        sql_upper = ast.sql().upper()
        if 'CONSTRAINT' in sql_upper:
            return StatementType.CONSTRAINT
        if 'DENY' in sql_upper:
            return StatementType.DENY
        
        return StatementType.OTHER
    
    def _extract_metadata(self, stmt: ParsedStatement, ast: exp.Expression) -> None:
        """Extract metadata from the AST."""
        if isinstance(ast, exp.Create) and ast.kind == "DATABASE":
            return
        if isinstance(ast, exp.Create) and isinstance(ast.this, exp.Table):
            table = ast.this
            stmt.object_name = table.name
            stmt.object_type = "TABLE"
            if table.db:
                stmt.database = table.db
            if table.catalog:
                stmt.schema = table.catalog
            elif table.args.get('schema'):
                stmt.schema = table.args['schema']
            
            self._extract_columns(stmt, ast)
            self._extract_constraints(stmt, ast)
        
        elif isinstance(ast, exp.Create) and ast.kind in ("PROCEDURE", "FUNCTION", "TRIGGER", "VIEW"):
            stmt.object_name = ast.this.name if hasattr(ast.this, 'name') else str(ast.this)
            stmt.object_type = ast.kind
            if hasattr(ast.this, 'db') and ast.this.db:
                stmt.database = ast.this.db
        
        elif isinstance(ast, (exp.Insert, exp.Update, exp.Delete, exp.Select)):
            tables = self._find_tables(ast)
            if tables:
                stmt.table = tables[0]
                if len(tables) > 1:
                    stmt.references = tables[1:]
        
        elif isinstance(ast, exp.Command):
            stmt.raw_sql = ast.sql()
    
    def _extract_columns(self, stmt: ParsedStatement, ast: exp.Create) -> None:
        """Extract column definitions from CREATE TABLE."""
        if not ast.expressions:
            return
        
        for expr in ast.expressions:
            if isinstance(expr, exp.ColumnDef):
                col_info = {
                    'name': expr.name,
                    'type': expr.kind.sql() if expr.kind else 'UNKNOWN',
                    'nullable': True,
                    'default': None,
                    'is_primary_key': False,
                    'is_identity': False,
                    'constraints': []
                }
                
                for constraint in expr.constraints:
                    ctype = constraint.kind.upper() if constraint.kind else ''
                    col_info['constraints'].append(ctype)
                    
                    if ctype in ('PRIMARY KEY', 'NOT NULL'):
                        col_info['nullable'] = (ctype != 'NOT NULL')
                    if ctype == 'PRIMARY KEY':
                        col_info['is_primary_key'] = True
                    if ctype == 'IDENTITY':
                        col_info['is_identity'] = True
                    if ctype == 'DEFAULT' and constraint.expressions:
                        col_info['default'] = constraint.expressions[0].sql()
                
                stmt.columns.append(col_info)
    
    def _extract_constraints(self, stmt: ParsedStatement, ast: exp.Create) -> None:
        """Extract table-level constraints."""
        if not ast.expressions:
            return
        
        for expr in ast.expressions:
            if isinstance(expr, exp.PrimaryKey):
                cols = [c.name for c in expr.expressions]
                stmt.constraints.append({
                    'type': 'PRIMARY KEY',
                    'columns': cols,
                    'name': expr.args.get('name')
                })
            elif isinstance(expr, exp.ForeignKey):
                cols = [c.name for c in expr.expressions]
                ref_table = expr.args.get('reference')
                ref_cols = []
                if ref_table and hasattr(ref_table, 'expressions'):
                    ref_cols = [c.name for c in ref_table.expressions]
                stmt.constraints.append({
                    'type': 'FOREIGN KEY',
                    'columns': cols,
                    'referenced_table': ref_table.this.name if ref_table and hasattr(ref_table, 'this') else None,
                    'referenced_columns': ref_cols,
                    'name': expr.args.get('name')
                })
            elif isinstance(expr, exp.Unique):
                cols = [c.name for c in expr.expressions]
                stmt.constraints.append({
                    'type': 'UNIQUE',
                    'columns': cols,
                    'name': expr.args.get('name')
                })
            elif isinstance(expr, exp.Check):
                stmt.constraints.append({
                    'type': 'CHECK',
                    'expression': expr.this.sql() if expr.this else None,
                    'name': expr.args.get('name')
                })
            elif isinstance(expr, exp.Index):
                cols = [c.name for c in expr.expressions]
                stmt.indexes.append({
                    'columns': cols,
                    'name': expr.args.get('name'),
                    'unique': expr.args.get('unique', False)
                })
    
    def _find_tables(self, ast: exp.Expression) -> List[str]:
        """Find all table references in a query."""
        tables = []
        for table in ast.find_all(exp.Table):
            if table.name:
                tables.append(table.name)
        return list(dict.fromkeys(tables))
    
    def _create_fallback_statement(self, sql: str, file_name: str, line_start: int, line_end: int) -> ParsedStatement:
        """Create a basic statement when parsing fails."""
        sql_upper = sql.upper().strip()
        stmt_type = StatementType.OTHER
        
        if sql_upper.startswith('CREATE TABLE'):
            stmt_type = StatementType.CREATE_TABLE
        elif sql_upper.startswith('ALTER TABLE'):
            stmt_type = StatementType.ALTER_TABLE
        elif sql_upper.startswith('DROP TABLE'):
            stmt_type = StatementType.DROP_TABLE
        elif sql_upper.startswith('INSERT'):
            stmt_type = StatementType.INSERT
        elif sql_upper.startswith('UPDATE'):
            stmt_type = StatementType.UPDATE
        elif sql_upper.startswith('DELETE'):
            stmt_type = StatementType.DELETE
        elif sql_upper.startswith('SELECT'):
            stmt_type = StatementType.SELECT
        elif sql_upper.startswith('MERGE'):
            stmt_type = StatementType.MERGE
        elif 'CREATE PROCEDURE' in sql_upper or 'CREATE PROC' in sql_upper:
            stmt_type = StatementType.CREATE_PROCEDURE
        elif 'CREATE FUNCTION' in sql_upper:
            stmt_type = StatementType.CREATE_FUNCTION
        elif 'CREATE TRIGGER' in sql_upper:
            stmt_type = StatementType.CREATE_TRIGGER
        elif 'CREATE VIEW' in sql_upper:
            stmt_type = StatementType.CREATE_VIEW
        elif 'CREATE INDEX' in sql_upper:
            stmt_type = StatementType.CREATE_INDEX
        elif 'GRANT' in sql_upper:
            stmt_type = StatementType.GRANT
        elif 'REVOKE' in sql_upper:
            stmt_type = StatementType.REVOKE
        elif 'DENY' in sql_upper:
            stmt_type = StatementType.DENY
        elif sql_upper.startswith('EXEC') or sql_upper.startswith('EXECUTE'):
            stmt_type = StatementType.EXEC
        
        return ParsedStatement(
            type=stmt_type,
            raw_sql=sql,
            file_name=file_name,
            line_start=line_start,
            line_end=line_end
        )


def parse_all_files(sql_files: List, parser: SqlParser) -> List[ParsedStatement]:
    """Parse all SQL files and return combined statements."""
    all_statements = []
    for sql_file in sql_files:
        try:
            statements = parser.parse_file(sql_file.path, sql_file.relative_path)
            all_statements.extend(statements)
            sql_file.line_count = count_lines(sql_file.path)
        except Exception as e:
            print(f"Error parsing {sql_file.relative_path}: {e}")
    return all_statements


def count_lines(file_path: str) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0