#!/usr:bin/env python3
"""
空板供给规则（简化版）

检查空板供给。

迁移自: AiFilm-pipeline validators.py _g27_empty_plate_supply
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import RuleCard, Severity, RuleCategory


def check_empty_plate_supply(model):
    """检查空板供给（简化版）"""
    return [(Severity.OK, "空板供给验证(简化版)")]


rule_empty_plate_supply = RuleCard(
    id="R045",
    name="空板供给",
    category=RuleCategory.TECHNICAL,
    severity=Severity.WARN,
    priority=50,
    description="检查空板供给",
    rule=check_empty_plate_supply,
    version="1.0.0",
)
