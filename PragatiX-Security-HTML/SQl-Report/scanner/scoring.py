"""
Scoring System
Computes overall and per-object security, performance, and quality scores.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import math
from rule_engine import Finding, Severity, Category


@dataclass
class ObjectScore:
    object_name: str
    object_type: str
    file_name: str
    security_score: float = 100.0
    performance_score: float = 100.0
    quality_score: float = 100.0
    findings_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class OverallScores:
    security_score: float = 100.0
    performance_score: float = 100.0
    quality_score: float = 100.0
    object_scores: List[ObjectScore] = field(default_factory=list)


SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 40,
    Severity.HIGH: 20,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
    Severity.INFO: 1
}

CATEGORY_WEIGHTS = {
    Category.SECURITY: {"security": 1.0, "performance": 0.1, "quality": 0.2},
    Category.PERFORMANCE: {"security": 0.1, "performance": 1.0, "quality": 0.3},
    Category.SCHEMA: {"security": 0.2, "performance": 0.3, "quality": 1.0},
    Category.DATA_QUALITY: {"security": 0.1, "performance": 0.1, "quality": 1.0},
    Category.BEST_PRACTICES: {"security": 0.1, "performance": 0.2, "quality": 0.5},
    Category.MAINTAINABILITY: {"security": 0.0, "performance": 0.2, "quality": 0.5},
}

# Score decay factor: higher = more forgiving, lower = harsher
SCORE_DECAY = 400.0


def _weighted_findings_score(findings: List[Finding], dimension: str) -> float:
    """Compute a weighted finding penalty for a given dimension."""
    total = 0.0
    for f in findings:
        severity_weight = SEVERITY_WEIGHTS.get(f.severity, 5)
        cat_weights = CATEGORY_WEIGHTS.get(f.category, {"security": 0.3, "performance": 0.3, "quality": 0.3})
        total += severity_weight * cat_weights.get(dimension, 0.3)
    return total


def _apply_decay(weighted: float) -> float:
    """Convert weighted penalty into a 0-100 score using exponential decay."""
    return 100.0 * math.exp(-weighted / SCORE_DECAY)


def calculate_scores(findings: List[Finding], statements) -> OverallScores:
    """Calculate overall and per-object scores from findings."""
    overall = OverallScores()
    object_scores_map: Dict[str, ObjectScore] = {}
    
    for stmt in statements:
        if stmt.object_name and stmt.object_type:
            key = f"{stmt.object_type}:{stmt.object_name}"
            if key not in object_scores_map:
                object_scores_map[key] = ObjectScore(
                    object_name=stmt.object_name,
                    object_type=stmt.object_type,
                    file_name=stmt.file_name
                )
    
    overall.security_score = _apply_decay(_weighted_findings_score(findings, "security"))
    overall.performance_score = _apply_decay(_weighted_findings_score(findings, "performance"))
    overall.quality_score = _apply_decay(_weighted_findings_score(findings, "quality"))
    
    for obj_key, obj_score in object_scores_map.items():
        obj_findings = [f for f in findings
                        if f.object_name == obj_score.object_name and f.object_type == obj_score.object_type]
        for f in obj_findings:
            obj_score.findings_count[f.severity.value] += 1
        obj_score.security_score = _apply_decay(_weighted_findings_score(obj_findings, "security"))
        obj_score.performance_score = _apply_decay(_weighted_findings_score(obj_findings, "performance"))
        obj_score.quality_score = _apply_decay(_weighted_findings_score(obj_findings, "quality"))
        overall.object_scores.append(obj_score)
    
    overall.object_scores.sort(key=lambda x: (x.security_score + x.performance_score + x.quality_score) / 3)
    
    return overall


def get_score_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def get_score_color(score: float) -> str:
    """Get Bootstrap color class for score."""
    if score >= 80:
        return "success"
    elif score >= 60:
        return "warning"
    else:
        return "danger"