"""
File Discovery Module
Recursively finds all SQL files in the Sql_Dump directory.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict


@dataclass
class SqlFile:
    path: str
    relative_path: str
    folder: str
    size: int
    line_count: int = 0


def discover_sql_files(root_path: str) -> List[SqlFile]:
    """Discover all .sql files recursively in the given root path."""
    root = Path(root_path).resolve()
    sql_files = []
    
    for file_path in root.rglob("*.sql"):
        if file_path.is_file():
            rel_path = file_path.relative_to(root)
            folder = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
            
            stat = file_path.stat()
            sql_files.append(SqlFile(
                path=str(file_path),
                relative_path=str(rel_path),
                folder=folder,
                size=stat.st_size
            ))
    
    return sql_files


def count_lines(file_path: str) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def group_files_by_folder(files: List[SqlFile]) -> Dict[str, List[SqlFile]]:
    """Group files by their folder."""
    grouped = defaultdict(list)
    for f in files:
        grouped[f.folder].append(f)
    return dict(grouped)


def print_discovery_summary(files: List[SqlFile]) -> None:
    """Print a summary of discovered files."""
    grouped = group_files_by_folder(files)
    
    print(f"\n{'='*60}")
    print(f"FILE DISCOVERY SUMMARY")
    print(f"{'='*60}")
    print(f"Total SQL files found: {len(files)}")
    print(f"Total size: {sum(f.size for f in files) / 1024:.2f} KB")
    print(f"\nBy folder:")
    for folder, folder_files in sorted(grouped.items()):
        total_size = sum(f.size for f in folder_files) / 1024
        print(f"  {folder}: {len(folder_files)} files ({total_size:.2f} KB)")
    print(f"{'='*60}\n")