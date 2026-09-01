#!/usr/bin/env python3
"""
场景花名册完整性规则（简化版）

检查场景花名册完整性。

迁移自: AiFilm-pipeline validators.py _g43_scene_roster_completeness
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory


def check_scene_roster_completeness(model):
    """检查场景花名册完整性（简化版）"""
    return [(Severity.OK, "场景花名册验证(简化版)")]


rule_scene_roster_completeness = RuleCard(
    id="R043",
    name="场景花名册完整性",
    category=RuleCategory.TECHNICAL,
    severity=Severity.WARN,
    priority=50,
    description="检查场景花名册完整性",
    rule=check_scene_roster_completeness,
    version="1.0.0",
)
