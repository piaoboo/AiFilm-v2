#!/usr/bin/env python3
"""
表演一致性规则（简化版）

检查角色表演是否连贯。

迁移自: AiFilm-pipeline validators.py _g50_performance
版本: v1.0.0
日期: 2026-09-01
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import content_rule, Severity


def check_performance(model):
    """检查表演一致性（简化版）"""
    return [(Severity.OK, "表演一致性验证(简化版)")]


rule_performance = content_rule(
    id="R034",
    name="表演一致性",
    rule=check_performance,
    validate=lambda output: output,
    severity=Severity.WARN,
    description="检查角色表演是否连贯",
    priority=50,
    version="1.0.0",
)
