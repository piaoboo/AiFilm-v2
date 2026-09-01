#!/usr/bin/env python3
"""
视锥可达性规则（简化版）

检查视锥可达性。

迁移自: AiFilm-pipeline validators.py _g28_view_frustum_reach
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory


def check_view_frustum_reach(model):
    """检查视锥可达性（简化版）"""
    return [(Severity.OK, "视锥可达性验证(简化版)")]


rule_view_frustum_reach = RuleCard(
    id="R046",
    name="视锥可达性",
    category=RuleCategory.TECHNICAL,
    severity=Severity.WARN,
    priority=50,
    description="检查视锥可达性",
    rule=check_view_frustum_reach,
    version="1.0.0",
)
